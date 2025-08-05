#!/usr/bin/env python3
"""
Generar transacciones del año 2025 para las 4 cuentas principales
Revenue 4717, Bill Pay 4091, Capital One 4709, Checking 4052
"""

import pandas as pd
import os
from datetime import datetime, date, timedelta
import random
import numpy as np

def generate_all_accounts_2025():
    """Generar transacciones para las 4 cuentas del año 2025"""
    
    print("*** Generando Transacciones 2025 para las 4 Cuentas ***")
    
    # Configuración de cuentas
    accounts_config = {
        'Revenue 4717': {
            'type': 'inflow',
            'monthly_range': (150000, 200000),
            'transaction_count_range': (25, 35),
            'customers': [
                'Acme Corporation', 'Tech Solutions Inc', 'Global Systems Ltd',
                'DataFlow Corp', 'CloudTech Partners', 'Digital Innovations',
                'Enterprise Solutions', 'Smart Systems Co', 'Innovation Labs', 'Future Tech Inc'
            ]
        },
        'Bill Pay 4091': {
            'type': 'outflow', 
            'monthly_range': (20000, 30000),
            'transaction_count_range': (15, 25),
            'vendors': [
                'Payroll Services', 'Office Rent', 'Utilities Corp', 'Insurance Group',
                'IT Services', 'Marketing Agency', 'Legal Services', 'Accounting Firm',
                'Equipment Leasing', 'Maintenance Co'
            ]
        },
        'Capital One 4709': {
            'type': 'mixed',
            'monthly_range': (5000, 15000),
            'transaction_count_range': (10, 20),
            'entities': [
                'Office Supplies', 'Travel Expenses', 'Equipment Purchase', 'Software License',
                'Conference Fees', 'Professional Development', 'Client Entertainment', 'Fuel & Gas',
                'Maintenance & Repairs', 'Miscellaneous'
            ]
        },
        'Checking 4052': {
            'type': 'mixed',
            'monthly_range': (10000, 25000),
            'transaction_count_range': (12, 22),
            'entities': [
                'Bank Transfer In', 'Bank Transfer Out', 'Wire Transfer', 'ACH Payment',
                'Check Deposit', 'ATM Withdrawal', 'Online Transfer', 'Direct Deposit',
                'Electronic Payment', 'Cashier Check'
            ]
        }
    }
    
    all_transactions = []
    transaction_id = 1
    
    # Generar por cada cuenta
    for account_name, config in accounts_config.items():
        print(f"\n-> Generando datos para {account_name}...")
        
        account_transactions = []
        monthly_totals = []
        
        # Generar por cada mes
        for month in range(1, 13):
            # Determinar rango de montos y transacciones para el mes
            monthly_min, monthly_max = config['monthly_range']
            monthly_target = random.uniform(monthly_min, monthly_max)
            
            # Ajustes estacionales
            seasonal_multiplier = get_seasonal_multiplier(month, account_name)
            monthly_target *= seasonal_multiplier
            
            trans_count_min, trans_count_max = config['transaction_count_range']
            transaction_count = random.randint(trans_count_min, trans_count_max)
            
            # Generar transacciones del mes
            month_transactions = generate_monthly_transactions(
                account_name, config, month, monthly_target, transaction_count, transaction_id
            )
            
            account_transactions.extend(month_transactions)
            transaction_id += len(month_transactions)
            
            month_total = sum(t['amount'] for t in month_transactions)
            monthly_totals.append(month_total)
        
        all_transactions.extend(account_transactions)
        
        # Resumen por cuenta
        total_amount = sum(monthly_totals)
        avg_monthly = total_amount / 12
        print(f"   [OK] {len(account_transactions)} transacciones")
        print(f"   [OK] Total: ${total_amount:,.2f}")
        print(f"   [OK] Promedio mensual: ${avg_monthly:,.2f}")
    
    # Guardar en Excel
    df = pd.DataFrame(all_transactions)
    
    # Crear archivo de salida
    output_dir = os.path.join('static', 'uploads')
    os.makedirs(output_dir, exist_ok=True)
    
    # Actualizar qa_data.xlsx agregando los nuevos datos
    excel_file = os.path.join(output_dir, 'qa_data.xlsx')
    
    try:
        # Leer archivo existente
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='CashFlow', index=False)
        print(f"\n[OK] Datos guardados en: {excel_file}")
    except FileNotFoundError:
        # Crear nuevo archivo si no existe
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CashFlow', index=False)
        print(f"\n[OK] Nuevo archivo creado: {excel_file}")
    
    # Estadísticas finales
    print(f"\n*** Resumen Final ***")
    print(f"Total de transacciones generadas: {len(all_transactions)}")
    
    for account_name in accounts_config.keys():
        account_trans = [t for t in all_transactions if t['account'] == account_name]
        account_total = sum(t['amount'] for t in account_trans if t['type'] == 'inflow') - sum(t['amount'] for t in account_trans if t['type'] == 'outflow')
        print(f"{account_name}: {len(account_trans)} trans, Balance neto: ${account_total:,.2f}")
    
    return True

def get_seasonal_multiplier(month, account_name):
    """Obtener multiplicador estacional por cuenta y mes"""
    
    if account_name == 'Revenue 4717':
        # Revenue: Q4 más fuerte, Q1 más lento
        multipliers = {
            1: 0.85, 2: 0.90, 3: 0.95,  # Q1 - inicio lento
            4: 1.05, 5: 1.10, 6: 1.15,  # Q2 - crecimiento
            7: 1.10, 8: 1.05, 9: 1.20,  # Q3 - proyectos verano
            10: 1.15, 11: 1.25, 12: 1.30  # Q4 - cierre fiscal
        }
    elif account_name == 'Bill Pay 4091':
        # Gastos más estables, ligero incremento en diciembre
        multipliers = {
            1: 1.05, 2: 0.95, 3: 1.00,  # Q1 - bonos enero
            4: 1.00, 5: 1.00, 6: 1.05,  # Q2 - estable
            7: 1.00, 8: 0.95, 9: 1.00,  # Q3 - vacaciones agosto
            10: 1.05, 11: 1.10, 12: 1.15  # Q4 - bonos navideños
        }
    else:
        # Otras cuentas: variación moderada
        multipliers = {
            1: 0.95, 2: 0.90, 3: 1.00,
            4: 1.05, 5: 1.00, 6: 1.10,
            7: 1.05, 8: 0.95, 9: 1.05,
            10: 1.10, 11: 1.05, 12: 1.20
        }
    
    return multipliers.get(month, 1.0)

def generate_monthly_transactions(account_name, config, month, monthly_target, transaction_count, start_id):
    """Generar transacciones para un mes específico"""
    
    transactions = []
    
    # Determinar tipos de transacción
    if config['type'] == 'inflow':
        transaction_types = ['inflow']
    elif config['type'] == 'outflow':
        transaction_types = ['outflow']
    else:  # mixed
        transaction_types = ['inflow', 'outflow']
    
    # Distribuir montos entre transacciones
    remaining_amount = monthly_target
    
    for i in range(transaction_count):
        # Tipo de transacción
        if len(transaction_types) == 1:
            trans_type = transaction_types[0]
        else:
            # Para cuentas mixtas, 60% inflow, 40% outflow
            trans_type = random.choices(['inflow', 'outflow'], weights=[0.6, 0.4])[0]
        
        # Monto de la transacción
        if i == transaction_count - 1:  # Última transacción usa el restante
            amount = max(remaining_amount, 100)
        else:
            max_amount = remaining_amount * 0.4  # Máximo 40% del restante
            min_amount = max(100, remaining_amount * 0.05)  # Mínimo 5% del restante
            amount = random.uniform(min_amount, max_amount)
            remaining_amount -= amount
        
        # Fecha aleatoria en el mes
        day = random.randint(1, 28)  # Usar 28 para evitar problemas con febrero
        trans_date = date(2025, month, day)
        
        # Descripción y entidad
        description, entity = generate_transaction_description(account_name, config, trans_type)
        
        # Estado
        status = random.choices(
            ['completed', 'pending', 'scheduled'],
            weights=[0.8, 0.15, 0.05]
        )[0]
        
        transaction = {
            'id': start_id + i,
            'date': trans_date,
            'description': description,
            'amount': round(abs(amount), 2),
            'type': trans_type,
            'account': account_name,
            'status': status,
            'entity': entity
        }
        
        transactions.append(transaction)
    
    return transactions

def generate_transaction_description(account_name, config, trans_type):
    """Generar descripción y entidad para la transacción"""
    
    if account_name == 'Revenue 4717':
        entity = random.choice(config['customers'])
        services = [
            'Software Development Services',
            'System Integration Project', 
            'Consulting Services',
            'Cloud Migration Services',
            'Data Analytics Implementation'
        ]
        service = random.choice(services)
        description = f"{service} - {entity}"
        
    elif account_name == 'Bill Pay 4091':
        entity = random.choice(config['vendors'])
        if 'Payroll' in entity:
            description = f"Payroll Payment - {random.choice(['Biweekly', 'Monthly', 'Bonus'])}"
        else:
            description = f"Payment to {entity} - {random.choice(['Monthly', 'Invoice', 'Contract'])}"
            
    else:  # Capital One 4709 o Checking 4052
        entity = random.choice(config['entities'])
        if trans_type == 'inflow':
            description = f"Deposit - {entity}"
        else:
            description = f"Payment - {entity}"
    
    return description, entity

if __name__ == '__main__':
    try:
        success = generate_all_accounts_2025()
        if success:
            print("\n[SUCCESS] Generacion completada exitosamente!")
            print("\nPara usar los datos:")
            print("1. Asegurate de tener USE_FILE_MODE=true")
            print("2. Reinicia la aplicacion Flask")
            print("3. Ve a /cash-flow para ver las 4 cuentas")
        else:
            print("\n[ERROR] Error en la generacion")
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()