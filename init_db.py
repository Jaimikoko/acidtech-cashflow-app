#!/usr/bin/env python3
import os
from datetime import datetime, date, timedelta
from app import create_app
from database import db
from models.user import User
from models.transaction import Transaction
from models.purchase_order import PurchaseOrder, PurchaseOrderItem

def init_database():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("Database already initialized with data.")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@acidtech.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create demo user
        demo_user = User(
            username='demo',
            email='demo@acidtech.com',
            first_name='Demo',
            last_name='User',
            role='user'
        )
        demo_user.set_password('demo123')
        db.session.add(demo_user)
        
        db.session.commit()
        
        # Create sample accounts payable transactions
        payables = [
            {
                'vendor_customer': 'ABC Office Supplies',
                'amount': 1250.00,
                'due_date': date.today() + timedelta(days=15),
                'description': 'Office supplies for Q1',
                'invoice_number': 'INV-001',
                'status': 'pending'
            },
            {
                'vendor_customer': 'Tech Solutions Inc',
                'amount': 5500.00,
                'due_date': date.today() + timedelta(days=30),
                'description': 'Software licensing annual fee',
                'invoice_number': 'INV-002',
                'status': 'pending'
            },
            {
                'vendor_customer': 'City Electric Company',
                'amount': 450.75,
                'due_date': date.today() - timedelta(days=5),
                'description': 'Monthly electricity bill',
                'invoice_number': 'INV-003',
                'status': 'pending'
            },
            {
                'vendor_customer': 'Professional Services LLC',
                'amount': 3200.00,
                'due_date': date.today() + timedelta(days=45),
                'description': 'Consulting services',
                'invoice_number': 'INV-004',
                'status': 'pending'
            },
            {
                'vendor_customer': 'Office Rent Corp',
                'amount': 2800.00,
                'due_date': date.today() - timedelta(days=10),
                'description': 'Monthly office rent',
                'invoice_number': 'INV-005',
                'status': 'paid'
            }
        ]
        
        for payable_data in payables:
            transaction = Transaction(
                type='payable',
                vendor_customer=payable_data['vendor_customer'],
                amount=payable_data['amount'],
                issue_date=date.today() - timedelta(days=10),  # Set issue_date for new fields
                due_date=payable_data['due_date'],
                description=payable_data['description'],
                invoice_number=payable_data['invoice_number'],
                status=payable_data['status'],
                created_by=admin.id
            )
            db.session.add(transaction)
        
        # Create sample accounts receivable transactions
        receivables = [
            {
                'vendor_customer': 'Acme Corporation',
                'amount': 8500.00,
                'due_date': date.today() + timedelta(days=20),
                'description': 'Software development services',
                'invoice_number': 'AR-001',
                'status': 'pending'
            },
            {
                'vendor_customer': 'Global Industries',
                'amount': 12000.00,
                'due_date': date.today() + timedelta(days=35),
                'description': 'Annual maintenance contract',
                'invoice_number': 'AR-002',
                'status': 'pending'
            },
            {
                'vendor_customer': 'StartUp Inc',
                'amount': 3750.00,
                'due_date': date.today() - timedelta(days=2),
                'description': 'Web design project',
                'invoice_number': 'AR-003',
                'status': 'pending'
            },
            {
                'vendor_customer': 'Enterprise Solutions',
                'amount': 15500.00,
                'due_date': date.today() + timedelta(days=60),
                'description': 'Custom software solution',
                'invoice_number': 'AR-004',
                'status': 'pending'
            },
            {
                'vendor_customer': 'Local Business',
                'amount': 2200.00,
                'due_date': date.today() - timedelta(days=15),
                'description': 'IT support services',
                'invoice_number': 'AR-005',
                'status': 'paid'
            }
        ]
        
        for receivable_data in receivables:
            transaction = Transaction(
                type='receivable',
                vendor_customer=receivable_data['vendor_customer'],
                amount=receivable_data['amount'],
                issue_date=date.today() - timedelta(days=5),   # Set issue_date for new fields
                due_date=receivable_data['due_date'],
                description=receivable_data['description'],
                invoice_number=receivable_data['invoice_number'],
                status=receivable_data['status'],
                created_by=admin.id
            )
            db.session.add(transaction)
        
        # Create sample purchase orders
        po1 = PurchaseOrder(
            po_number='PO-2024-001',
            vendor='Tech Hardware Suppliers',
            total_amount=4500.00,
            status='approved',
            order_date=date.today() - timedelta(days=5),
            expected_delivery=date.today() + timedelta(days=10),
            description='Computer equipment for new employees',
            terms='Net 30 days',
            created_by=admin.id
        )
        db.session.add(po1)
        db.session.flush()
        
        # Add line items for PO1
        po1_items = [
            {'description': 'Laptop - Dell XPS 13', 'quantity': 2, 'unit_price': 1500.00, 'total_price': 3000.00},
            {'description': 'External Monitor - 27" 4K', 'quantity': 2, 'unit_price': 350.00, 'total_price': 700.00},
            {'description': 'Wireless Mouse', 'quantity': 2, 'unit_price': 75.00, 'total_price': 150.00},
            {'description': 'Keyboard - Mechanical', 'quantity': 2, 'unit_price': 125.00, 'total_price': 250.00},
            {'description': 'USB Hub', 'quantity': 2, 'unit_price': 50.00, 'total_price': 100.00},
            {'description': 'Laptop Stand', 'quantity': 2, 'unit_price': 150.00, 'total_price': 300.00}
        ]
        
        for item_data in po1_items:
            item = PurchaseOrderItem(
                po_id=po1.id,
                item_description=item_data['description'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(item)
        
        po2 = PurchaseOrder(
            po_number='PO-2024-002',
            vendor='Office Furniture Plus',
            total_amount=2800.00,
            status='sent',
            order_date=date.today() - timedelta(days=2),
            expected_delivery=date.today() + timedelta(days=14),
            description='Office furniture for expansion',
            terms='Net 45 days',
            created_by=admin.id
        )
        db.session.add(po2)
        db.session.flush()
        
        # Add line items for PO2
        po2_items = [
            {'description': 'Office Desk - Adjustable Height', 'quantity': 3, 'unit_price': 650.00, 'total_price': 1950.00},
            {'description': 'Ergonomic Office Chair', 'quantity': 3, 'unit_price': 250.00, 'total_price': 750.00},
            {'description': 'Filing Cabinet - 4 Drawer', 'quantity': 1, 'unit_price': 300.00, 'total_price': 300.00}
        ]
        
        for item_data in po2_items:
            item = PurchaseOrderItem(
                po_id=po2.id,
                item_description=item_data['description'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(item)
        
        po3 = PurchaseOrder(
            po_number='PO-2024-003',
            vendor='Marketing Materials Co',
            total_amount=1200.00,
            status='draft',
            order_date=date.today(),
            expected_delivery=date.today() + timedelta(days=7),
            description='Marketing materials for trade show',
            terms='Net 15 days',
            created_by=admin.id
        )
        db.session.add(po3)
        db.session.flush()
        
        # Add line items for PO3
        po3_items = [
            {'description': 'Trade Show Banner - Large', 'quantity': 2, 'unit_price': 200.00, 'total_price': 400.00},
            {'description': 'Business Cards - Premium', 'quantity': 5000, 'unit_price': 0.08, 'total_price': 400.00},
            {'description': 'Brochures - Tri-fold', 'quantity': 1000, 'unit_price': 0.40, 'total_price': 400.00}
        ]
        
        for item_data in po3_items:
            item = PurchaseOrderItem(
                po_id=po3.id,
                item_description=item_data['description'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                total_price=item_data['total_price']
            )
            db.session.add(item)
        
        db.session.commit()
        
        print("Database initialized successfully!")
        print("Admin user created: username='admin', password='admin123'")
        print("Demo user created: username='demo', password='demo123'")
        print("Sample data added:")
        print("- 5 Accounts Payable transactions")
        print("- 5 Accounts Receivable transactions") 
        print("- 3 Purchase Orders with line items")

if __name__ == '__main__':
    init_database()