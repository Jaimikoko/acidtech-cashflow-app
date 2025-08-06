from flask import request, jsonify, render_template
from datetime import datetime, date
import csv
import io
import uuid
import pandas as pd
import re
from database import db
from models.bank_transaction import BankTransaction

from . import data_import_bp

@data_import_bp.route('/')
def index():
    """Data Import main page - Admin only"""
    try:
        return render_template('data_import/index.html')
    except Exception as e:
        # Fallback - redirect to simple error page
        return f"<h1>Data Import Error</h1><p>{str(e)}</p>"

@data_import_bp.route('/upload', methods=['POST'])
def upload_csv():
    """Process CSV upload and import bank transactions"""
    try:
        # Get form data
        account_name = request.form.get('account_name')
        account_type = request.form.get('account_type')
        csv_file = request.files.get('csv_file')
        
        if not csv_file or not account_name:
            return jsonify({'success': False, 'error': 'Missing required data'})
        
        # Generate batch ID for tracking
        batch_id = str(uuid.uuid4())[:8]
        
        # Read and process CSV
        csv_content = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        records_imported = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
            try:
                # Parse date
                transaction_date = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                
                # Parse amount
                amount = float(row['Amount'])
                
                # Create bank transaction
                bank_transaction = BankTransaction(
                    account_name=account_name,
                    account_type=account_type,
                    transaction_date=transaction_date,
                    description=row['Description'],
                    amount=amount,
                    transaction_type=row['Type'],
                    category=row.get('Category', ''),
                    accounting_class=row.get('Accounting_Class', ''),
                    reference=row.get('Reference', ''),
                    import_batch_id=batch_id,
                    created_by=1  # TODO: Get from current user when auth is implemented
                )
                
                db.session.add(bank_transaction)
                records_imported += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        # Commit all records
        db.session.commit()
        
        return jsonify({
            'success': True,
            'records_imported': records_imported,
            'batch_id': batch_id,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

def upload_and_replace_transactions(file_path, year=2025, account_name="Revenue 4717"):
    """
    Cargar archivo de datos financieros y configurar flujo definitivo de importación
    
    Args:
        file_path (str): Ruta al archivo CSV/XLSX
        year (int): Año para filtrar y reemplazar datos
        account_name (str): Nombre de la cuenta (Revenue 4717, Bill Pay 5285, etc.)
    
    Returns:
        dict: Estadísticas de la operación
    """
    try:
        print(f"INICIANDO CARGA DE DATOS: {account_name} - Año {year}")
        
        # 1. Leer y validar archivo
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)
        
        print(f"Archivo leido: {len(df)} registros encontrados")
        
        # 2. Limpiar datos existentes del año/cuenta
        deleted_count = BankTransaction.query.filter(
            BankTransaction.account_name == account_name,
            db.extract('year', BankTransaction.transaction_date) == year
        ).delete()
        
        print(f"Registros eliminados: {deleted_count} transacciones de {account_name} - {year}")
        
        # 3. Procesar y limpiar datos del archivo
        processed_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Parsear fecha (formato M/D/YYYY)
                date_str = str(row['DATE']).strip()
                transaction_date = pd.to_datetime(date_str, format='%m/%d/%Y').date()
                
                # Limpiar y parsear monto
                amount_str = str(row[' AMOUNT ']).strip()
                # Remover paréntesis (números negativos) y comas
                amount_str = re.sub(r'[(),"]', '', amount_str)
                if '(' in str(row[' AMOUNT ']):
                    amount = -float(amount_str)
                else:
                    amount = float(amount_str)
                
                # Limpiar descripción
                description = str(row['DESCRIPTION']).strip()
                
                # Determinar tipo de transacción
                transaction_type = "CREDIT" if amount > 0 else "DEBIT"
                
                # Mapear merchant a reference
                merchant = str(row['MERCHANT']).strip() if pd.notna(row['MERCHANT']) else ""
                
                # Mapear tipo y account (nota: las columnas tienen espacios)
                type_field = str(row[' TYPE ']).strip() if pd.notna(row.get(' TYPE ')) else ""
                accounting_class = str(row['ACCOUNT']).strip() if pd.notna(row['ACCOUNT']) else ""
                
                # Crear transacción bancaria
                bank_transaction = BankTransaction(
                    account_name=account_name,
                    account_type="CHECKING",  # Default para Revenue 4717
                    transaction_date=transaction_date,
                    description=description,
                    amount=amount,
                    transaction_type=transaction_type,
                    category=type_field,
                    accounting_class=accounting_class,
                    reference=merchant,
                    import_batch_id=f"REPLACE_{year}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    created_by=1  # Default admin user
                )
                
                db.session.add(bank_transaction)
                processed_count += 1
                
            except Exception as e:
                errors.append(f"Fila {index + 2}: {str(e)}")
                continue
        
        # 4. Confirmar transacciones
        db.session.commit()
        
        # 5. Estadísticas finales
        stats = {
            'success': True,
            'account_name': account_name,
            'year': year,
            'file_processed': file_path,
            'records_deleted': deleted_count,
            'records_inserted': processed_count,
            'errors': errors,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"CARGA COMPLETADA:")
        print(f"   - Registros eliminados: {deleted_count}")
        print(f"   - Registros insertados: {processed_count}")
        print(f"   - Errores: {len(errors)}")
        print(f"   - Fecha/hora: {stats['timestamp']}")
        
        return stats
        
    except Exception as e:
        db.session.rollback()
        error_stats = {
            'success': False,
            'error': str(e),
            'account_name': account_name,
            'year': year,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        print(f"ERROR EN CARGA: {str(e)}")
        return error_stats

@data_import_bp.route('/replace-data', methods=['POST'])
def replace_data():
    """
    Endpoint para reemplazar datos usando upload_and_replace_transactions
    """
    try:
        # Obtener parámetros
        account_name = request.form.get('account_name', 'Revenue 4717')
        year = int(request.form.get('year', 2025))
        csv_file = request.files.get('csv_file')
        
        if not csv_file:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        # Guardar archivo temporalmente
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            csv_file.save(temp_file.name)
            
            # Ejecutar carga
            result = upload_and_replace_transactions(temp_file.name, year, account_name)
            
            # Limpiar archivo temporal
            os.unlink(temp_file.name)
            
            return jsonify(result)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})