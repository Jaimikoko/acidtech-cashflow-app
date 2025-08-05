from flask import request, jsonify, render_template
from datetime import datetime, date
import csv
import io
import uuid
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