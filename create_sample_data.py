#!/usr/bin/env python3
"""
Script para crear datos de prueba en la base de datos
Para usar en Azure y testing local
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add the application directory to the Python path
app_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, app_dir)

from app import create_app
from database import db
from models.transaction import Transaction
from models.purchase_order import PurchaseOrder, PurchaseOrderItem
from models.user import User

def create_sample_data():
    """Create sample data for testing"""
    
    print("*** Creando datos de prueba...")
    
    # Create application context
    app = create_app()
    
    with app.app_context():
        try:
            # Drop and recreate all tables to match current models
            print("*** Recreando tablas para que coincidan con modelos...")
            db.drop_all()
            db.create_all()
            
            # Create a test user if none exists
            if not User.query.first():
                print("*** Creando usuario de prueba...")
                test_user = User(
                    username='demo_user',
                    email='demo@acidtech.com',
                    first_name='Demo',
                    last_name='User'
                )
                test_user.set_password('demo123')
                db.session.add(test_user)
                db.session.commit()
                print("*** Usuario demo creado")
            
            user = User.query.first()
            
            # Clear existing transactions for clean slate
            Transaction.query.delete()
            PurchaseOrderItem.query.delete()
            PurchaseOrder.query.delete()
            
            print("*** Creando transacciones de ejemplo...")
            
            # Sample Receivables (money coming in)
            receivables_data = [
                {
                    'vendor_customer': 'Acme Corporation',
                    'amount': 15000.00,
                    'due_date': date.today() + timedelta(days=30),
                    'description': 'Consulting Services - Q4 2024',
                    'invoice_number': 'INV-2024-001',
                    'status': 'pending'
                },
                {
                    'vendor_customer': 'Tech Solutions Inc',
                    'amount': 8500.00,
                    'due_date': date.today() + timedelta(days=15),
                    'description': 'Software Development Project',
                    'invoice_number': 'INV-2024-002',
                    'status': 'pending'
                },
                {
                    'vendor_customer': 'Global Systems Ltd',
                    'amount': 12250.00,
                    'due_date': date.today() + timedelta(days=45),
                    'description': 'System Integration Services',
                    'invoice_number': 'INV-2024-003',
                    'status': 'pending'
                },
                {
                    'vendor_customer': 'DataFlow Corp',
                    'amount': 6800.00,
                    'due_date': date.today() - timedelta(days=5),  # Overdue
                    'description': 'Database Migration Project',
                    'invoice_number': 'INV-2024-004',
                    'status': 'pending'
                },
                {
                    'vendor_customer': 'CloudTech Partners',
                    'amount': 3200.00,
                    'due_date': date.today() + timedelta(days=60),
                    'description': 'Cloud Infrastructure Setup',
                    'invoice_number': 'INV-2024-005',
                    'status': 'pending'
                }
            ]
            
            for data in receivables_data:
                transaction = Transaction(
                    type='receivable',
                    vendor_customer=data['vendor_customer'],
                    amount=data['amount'],
                    due_date=data['due_date'],
                    description=data['description'],
                    invoice_number=data['invoice_number'],
                    status=data['status'],
                    created_by=user.id,
                    created_at=datetime.utcnow() - timedelta(days=30)
                )
                db.session.add(transaction)
            
            # Sample Payables (money going out)
            payables_data = [
                {
                    'vendor_customer': 'Office Supplies Co',
                    'amount': 2400.00,
                    'due_date': date.today() + timedelta(days=20),
                    'description': 'Monthly Office Supplies',
                    'invoice_number': 'BILL-2024-001',
                    'status': 'pending'
                },
                {
                    'vendor_customer': 'IT Equipment Ltd',
                    'amount': 5600.00,
                    'due_date': date.today() + timedelta(days=10),
                    'description': 'Laptop and Hardware Purchase',
                    'invoice_number': 'BILL-2024-002',
                    'status': 'pending'
                },
                {
                    'vendor_customer': 'Utility Services Inc',
                    'amount': 850.00,
                    'due_date': date.today() + timedelta(days=7),
                    'description': 'Monthly Utilities - December',
                    'invoice_number': 'BILL-2024-003',
                    'status': 'pending'
                },
                {
                    'vendor_customer': 'Marketing Agency Pro',
                    'amount': 3200.00,
                    'due_date': date.today() - timedelta(days=2),  # Overdue
                    'description': 'Digital Marketing Campaign',
                    'invoice_number': 'BILL-2024-004',
                    'status': 'pending'
                },
                {
                    'vendor_customer': 'Legal Services Corp',
                    'amount': 1800.00,
                    'due_date': date.today() + timedelta(days=30),
                    'description': 'Legal Consultation Services',
                    'invoice_number': 'BILL-2024-005',
                    'status': 'pending'
                }
            ]
            
            for data in payables_data:
                transaction = Transaction(
                    type='payable',
                    vendor_customer=data['vendor_customer'],
                    amount=data['amount'],
                    due_date=data['due_date'],
                    description=data['description'],
                    invoice_number=data['invoice_number'],
                    status=data['status'],
                    created_by=user.id,
                    created_at=datetime.utcnow() - timedelta(days=20)
                )
                db.session.add(transaction)
            
            print("*** Creando ordenes de compra de ejemplo...")
            
            # Sample Purchase Orders
            po_data = [
                {
                    'po_number': 'PO-2024-001',
                    'vendor': 'Tech Hardware Solutions',
                    'description': 'New Workstation Setup',
                    'status': 'approved',
                    'total_amount': 4500.00,
                    'items': [
                        {'description': 'High-Performance Laptop', 'quantity': 2, 'unit_price': 1800.00},
                        {'description': 'External Monitor', 'quantity': 2, 'unit_price': 450.00}
                    ]
                },
                {
                    'po_number': 'PO-2024-002',
                    'vendor': 'Office Furniture Plus',
                    'description': 'Office Furniture Upgrade',
                    'status': 'sent',
                    'total_amount': 2800.00,
                    'items': [
                        {'description': 'Ergonomic Office Chair', 'quantity': 4, 'unit_price': 350.00},
                        {'description': 'Standing Desk', 'quantity': 2, 'unit_price': 600.00}
                    ]
                },
                {
                    'po_number': 'PO-2024-003',
                    'vendor': 'Software Licensing Co',
                    'description': 'Annual Software Licenses',
                    'status': 'draft',
                    'total_amount': 3600.00,
                    'items': [
                        {'description': 'Project Management Software', 'quantity': 1, 'unit_price': 1200.00},
                        {'description': 'Design Software Suite', 'quantity': 1, 'unit_price': 2400.00}
                    ]
                }
            ]
            
            for po_info in po_data:
                po = PurchaseOrder(
                    po_number=po_info['po_number'],
                    vendor=po_info['vendor'],
                    description=po_info['description'],
                    status=po_info['status'],
                    total_amount=po_info['total_amount'],
                    order_date=date.today() - timedelta(days=15),
                    expected_delivery=date.today() + timedelta(days=30),
                    created_by=user.id,
                    created_at=datetime.utcnow() - timedelta(days=15)
                )
                db.session.add(po)
                db.session.flush()  # Get the PO ID
                
                # Add items to the PO
                for item_info in po_info['items']:
                    item = PurchaseOrderItem(
                        po_id=po.id,
                        item_description=item_info['description'],
                        quantity=item_info['quantity'],
                        unit_price=item_info['unit_price'],
                        total_price=item_info['quantity'] * item_info['unit_price']
                    )
                    db.session.add(item)
            
            # Commit all changes
            db.session.commit()
            
            # Print summary
            total_receivables = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='receivable', status='pending').scalar() or 0
            total_payables = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='payable', status='pending').scalar() or 0
            total_transactions = Transaction.query.count()
            total_pos = PurchaseOrder.query.count()
            
            print("\n*** Datos de prueba creados exitosamente!")
            print(f"*** Resumen:")
            print(f"   • Transacciones totales: {total_transactions}")
            print(f"   • Cuentas por cobrar: ${total_receivables:,.2f}")
            print(f"   • Cuentas por pagar: ${total_payables:,.2f}")
            print(f"   • Flujo neto: ${total_receivables - total_payables:,.2f}")
            print(f"   • Órdenes de compra: {total_pos}")
            print(f"   • Usuario demo: demo_user / demo123")
            
        except Exception as e:
            print(f"*** Error creando datos de prueba: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    create_sample_data()