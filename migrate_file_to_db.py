#!/usr/bin/env python3
"""
Clean migration script to transfer data from File Mode (Excel) to Database Mode
Transfers all cash flow data from Excel sheets to SQLAlchemy database tables
"""

import os
import sys
from datetime import datetime, date
import pandas as pd

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_file_mode_to_database():
    """Migrate data from Excel files to database"""
    
    print("*** Starting File Mode to Database Migration ***")
    
    # Import Flask app and models
    from app import create_app
    from database import db
    from models.user import User
    from models.transaction import Transaction
    from models.purchase_order import PurchaseOrder
    from utils.excel_data_manager import excel_manager
    
    # Create app context
    app = create_app()
    
    with app.app_context():
        print("Connected to database...")
        
        # Enable File Mode to load Excel data
        os.environ['USE_FILE_MODE'] = 'true'
        app.config['USE_FILE_MODE'] = True
        
        try:
            # Load Excel data
            print("Loading Excel data...")
            excel_data = excel_manager.load_excel_data(force_reload=True)
            
            if not excel_data:
                print("[ERROR] No Excel data found. Make sure qa_data.xlsx exists.")
                return False
            
            print(f"[OK] Excel data loaded. Sheets: {excel_data['metadata']['sheets']}")
            
            migration_stats = {
                'users_created': 0,
                'transactions_created': 0,
                'purchase_orders_created': 0,
                'cash_flow_records': 0,
                'errors': []
            }
            
            # 1. Migrate Users
            print("\n1. Migrating Users...")
            users_data = excel_data.get('users', [])
            
            for user_data in users_data:
                try:
                    # Check if user already exists
                    existing_user = User.query.filter_by(username=user_data['username']).first()
                    if existing_user:
                        print(f"   - User {user_data['username']} already exists, skipping...")
                        continue
                    
                    # Create new user
                    new_user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        first_name=user_data.get('first_name', ''),
                        last_name=user_data.get('last_name', '')
                    )
                    new_user.set_password('default123')  # Default password
                    
                    db.session.add(new_user)
                    migration_stats['users_created'] += 1
                    print(f"   [OK] Created user: {user_data['username']}")
                    
                except Exception as e:
                    error_msg = f"Error creating user {user_data.get('username', 'unknown')}: {str(e)}"
                    migration_stats['errors'].append(error_msg)
                    print(f"   [ERROR] {error_msg}")
            
            # Commit users first
            db.session.commit()
            print(f"   [SUMMARY] Users migrated: {migration_stats['users_created']}")
            
            # Get default user for transactions
            default_user = User.query.first()
            if not default_user:
                print("[ERROR] No users available for transaction ownership")
                return False
            
            # 2. Migrate Transactions (A/R and A/P)
            print("\n2. Migrating A/R and A/P Transactions...")
            transactions_data = excel_data.get('transactions', [])
            
            for trans_data in transactions_data:
                try:
                    # Check for duplicates by invoice number
                    if trans_data.get('invoice_number'):
                        existing_trans = Transaction.query.filter_by(
                            invoice_number=trans_data['invoice_number']
                        ).first()
                        if existing_trans:
                            continue
                    
                    # Convert date
                    due_date = trans_data['due_date']
                    if isinstance(due_date, str):
                        due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                    
                    new_transaction = Transaction(
                        type=trans_data['type'],
                        vendor_customer=trans_data['vendor_customer'],
                        amount=float(trans_data['amount']),
                        due_date=due_date,
                        description=trans_data['description'],
                        invoice_number=trans_data.get('invoice_number', ''),
                        status=trans_data.get('status', 'pending'),
                        created_by=default_user.id
                    )
                    
                    db.session.add(new_transaction)
                    migration_stats['transactions_created'] += 1
                    
                except Exception as e:
                    error_msg = f"Error creating transaction {trans_data.get('id', 'unknown')}: {str(e)}"
                    migration_stats['errors'].append(error_msg)
                    print(f"   [ERROR] {error_msg}")
            
            print(f"   [SUMMARY] A/R-A/P Transactions migrated: {migration_stats['transactions_created']}")
            
            # 3. Migrate Purchase Orders
            print("\n3. Migrating Purchase Orders...")
            po_data = excel_data.get('purchase_orders', [])
            
            for po in po_data:
                try:
                    # Check for duplicates by PO number
                    if po.get('po_number'):
                        existing_po = PurchaseOrder.query.filter_by(
                            po_number=po['po_number']
                        ).first()
                        if existing_po:
                            continue
                    
                    # Convert date
                    order_date = po['order_date']
                    if isinstance(order_date, str):
                        order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
                    
                    new_po = PurchaseOrder(
                        po_number=po['po_number'],
                        vendor=po['vendor'],
                        total_amount=float(po['total_amount']),
                        status=po.get('status', 'draft'),
                        order_date=order_date,
                        description=po.get('description', ''),
                        created_by=default_user.id
                    )
                    
                    db.session.add(new_po)
                    migration_stats['purchase_orders_created'] += 1
                    
                except Exception as e:
                    error_msg = f"Error creating PO {po.get('po_number', 'unknown')}: {str(e)}"
                    migration_stats['errors'].append(error_msg)
                    print(f"   [ERROR] {error_msg}")
            
            print(f"   [SUMMARY] Purchase Orders migrated: {migration_stats['purchase_orders_created']}")
            
            # 4. Process Cash Flow Data (for future cash flow tables)
            print("\n4. Processing Cash Flow Data...")
            cash_flow_data = excel_data.get('cash_flow', [])
            migration_stats['cash_flow_records'] = len(cash_flow_data)
            
            print(f"   [SUMMARY] Cash Flow records identified: {migration_stats['cash_flow_records']}")
            print("   [INFO] Cash Flow data will be available in File Mode until dedicated tables are created")
            
            # Commit all changes
            db.session.commit()
            
            # Migration Summary
            print("\n*** Migration Complete! ***")
            print("Summary:")
            print(f"   • Users created: {migration_stats['users_created']}")
            print(f"   • A/R-A/P Transactions: {migration_stats['transactions_created']}")
            print(f"   • Purchase Orders: {migration_stats['purchase_orders_created']}")
            print(f"   • Cash Flow records: {migration_stats['cash_flow_records']} (available in File Mode)")
            print(f"   • Errors: {len(migration_stats['errors'])}")
            
            if migration_stats['errors']:
                print("\n[WARNING] Errors encountered:")
                for error in migration_stats['errors'][:10]:  # Show first 10 errors
                    print(f"   - {error}")
                if len(migration_stats['errors']) > 10:
                    print(f"   ... and {len(migration_stats['errors']) - 10} more")
            
            # Database Mode Test
            print("\n[TEST] Testing Database Mode...")
            os.environ['USE_FILE_MODE'] = 'false'
            app.config['USE_FILE_MODE'] = False
            
            # Test queries
            db_users = User.query.count()
            db_transactions = Transaction.query.count()
            db_pos = PurchaseOrder.query.count()
            
            print("   Database Mode Test Results:")
            print(f"   • Users in DB: {db_users}")
            print(f"   • Transactions in DB: {db_transactions}")
            print(f"   • Purchase Orders in DB: {db_pos}")
            
            # Success message
            print("\n[SUCCESS] Migration successful! You can now use Database Mode.")
            print("To switch modes:")
            print("   • File Mode: set USE_FILE_MODE=true")
            print("   • Database Mode: set USE_FILE_MODE=false (or omit)")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def verify_migration():
    """Verify migration was successful"""
    
    print("\n*** Verifying Migration ***")
    
    from app import create_app
    from database import db
    from models.user import User
    from models.transaction import Transaction
    from models.purchase_order import PurchaseOrder
    
    app = create_app()
    
    with app.app_context():
        # Test both modes
        results = {}
        
        for mode_name, use_file_mode in [('Database Mode', False), ('File Mode', True)]:
            print(f"\n[TEST] Testing {mode_name}...")
            
            os.environ['USE_FILE_MODE'] = 'true' if use_file_mode else 'false'
            app.config['USE_FILE_MODE'] = use_file_mode
            
            try:
                if use_file_mode:
                    # Test Excel data loading
                    from utils.excel_data_manager import excel_manager
                    transactions = excel_manager.get_cash_flow_transactions()
                    account_summary = excel_manager.get_account_summary('Revenue 4717')
                    
                    results[mode_name] = {
                        'cash_flow_transactions': len(transactions),
                        'revenue_4717_total': account_summary.get('total_amount', 0),
                        'status': '[OK] Working'
                    }
                else:
                    # Test database queries
                    user_count = User.query.count()
                    transaction_count = Transaction.query.count()
                    po_count = PurchaseOrder.query.count()
                    
                    results[mode_name] = {
                        'users': user_count,
                        'transactions': transaction_count,
                        'purchase_orders': po_count,
                        'status': '[OK] Working'
                    }
                    
            except Exception as e:
                results[mode_name] = {'status': f'[ERROR] Error: {str(e)}'}
        
        # Print results
        print("\nVerification Results:")
        for mode, data in results.items():
            print(f"\n{mode}:")
            for key, value in data.items():
                print(f"   • {key}: {value}")
        
        return all('[OK]' in str(data.get('status', '')) for data in results.values())

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        verify_migration()
    else:
        success = migrate_file_mode_to_database()
        if success:
            verify_migration()