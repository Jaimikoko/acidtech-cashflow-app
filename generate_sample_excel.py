#!/usr/bin/env python3
"""
Generate sample Excel file for QA testing
Creates a comprehensive Excel file with sample data for all modules
"""

import pandas as pd
import os
from datetime import datetime, date, timedelta

def generate_sample_excel():
    """Generate sample Excel file with realistic business data"""
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join('static', 'uploads')
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'qa_data.xlsx')
    
    # Sample Transactions (Accounts Receivable + Payable)
    transactions_data = [
        # Receivables (money coming in)
        {
            'id': 1, 'type': 'receivable', 'vendor_customer': 'Acme Corporation',
            'amount': 15000.00, 'due_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'description': 'Consulting Services Q4 2024', 'invoice_number': 'INV-2024-001', 'status': 'pending'
        },
        {
            'id': 2, 'type': 'receivable', 'vendor_customer': 'Tech Solutions Inc',
            'amount': 8500.00, 'due_date': (date.today() + timedelta(days=15)).strftime('%Y-%m-%d'),
            'description': 'Software Development Project', 'invoice_number': 'INV-2024-002', 'status': 'pending'
        },
        {
            'id': 3, 'type': 'receivable', 'vendor_customer': 'Global Systems Ltd',
            'amount': 12250.00, 'due_date': (date.today() + timedelta(days=45)).strftime('%Y-%m-%d'),
            'description': 'System Integration Services', 'invoice_number': 'INV-2024-003', 'status': 'pending'
        },
        {
            'id': 4, 'type': 'receivable', 'vendor_customer': 'DataFlow Corp',
            'amount': 6800.00, 'due_date': (date.today() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'description': 'Database Migration Project', 'invoice_number': 'INV-2024-004', 'status': 'pending'
        },
        {
            'id': 5, 'type': 'receivable', 'vendor_customer': 'CloudTech Partners',
            'amount': 3200.00, 'due_date': (date.today() + timedelta(days=60)).strftime('%Y-%m-%d'),
            'description': 'Cloud Infrastructure Setup', 'invoice_number': 'INV-2024-005', 'status': 'pending'
        },
        # Payables (money going out)
        {
            'id': 6, 'type': 'payable', 'vendor_customer': 'Office Supplies Co',
            'amount': 2400.00, 'due_date': (date.today() + timedelta(days=20)).strftime('%Y-%m-%d'),
            'description': 'Monthly Office Supplies', 'invoice_number': 'BILL-2024-001', 'status': 'pending'
        },
        {
            'id': 7, 'type': 'payable', 'vendor_customer': 'IT Equipment Ltd',
            'amount': 5600.00, 'due_date': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'description': 'Laptop and Hardware Purchase', 'invoice_number': 'BILL-2024-002', 'status': 'pending'
        },
        {
            'id': 8, 'type': 'payable', 'vendor_customer': 'Utility Services Inc',
            'amount': 850.00, 'due_date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'description': 'Monthly Utilities - December', 'invoice_number': 'BILL-2024-003', 'status': 'pending'
        },
        {
            'id': 9, 'type': 'payable', 'vendor_customer': 'Marketing Agency Pro',
            'amount': 3200.00, 'due_date': (date.today() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'description': 'Digital Marketing Campaign', 'invoice_number': 'BILL-2024-004', 'status': 'pending'
        },
        {
            'id': 10, 'type': 'payable', 'vendor_customer': 'Legal Services Corp',
            'amount': 1800.00, 'due_date': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'description': 'Legal Consultation Services', 'invoice_number': 'BILL-2024-005', 'status': 'pending'
        }
    ]
    
    # Sample Purchase Orders
    purchase_orders_data = [
        {
            'id': 1, 'po_number': 'PO-2024-001', 'vendor': 'Tech Hardware Solutions',
            'total_amount': 4500.00, 'status': 'approved',
            'order_date': (date.today() - timedelta(days=15)).strftime('%Y-%m-%d'),
            'expected_delivery': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'description': 'New Workstation Setup - 2 Laptops + Monitors'
        },
        {
            'id': 2, 'po_number': 'PO-2024-002', 'vendor': 'Office Furniture Plus',
            'total_amount': 2800.00, 'status': 'sent',
            'order_date': (date.today() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'expected_delivery': (date.today() + timedelta(days=25)).strftime('%Y-%m-%d'),
            'description': 'Office Furniture Upgrade - Chairs + Desks'
        },
        {
            'id': 3, 'po_number': 'PO-2024-003', 'vendor': 'Software Licensing Co',
            'total_amount': 3600.00, 'status': 'draft',
            'order_date': (date.today() - timedelta(days=5)).strftime('%Y-%m-%d'),
            'expected_delivery': (date.today() + timedelta(days=20)).strftime('%Y-%m-%d'),
            'description': 'Annual Software Licenses - Project Management + Design Suite'
        },
        {
            'id': 4, 'po_number': 'PO-2024-004', 'vendor': 'Network Solutions Inc',
            'total_amount': 1850.00, 'status': 'approved',
            'order_date': (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'expected_delivery': (date.today() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'description': 'Network Equipment Upgrade'
        },
        {
            'id': 5, 'po_number': 'PO-2024-005', 'vendor': 'Security Systems Pro',
            'total_amount': 2200.00, 'status': 'sent',
            'order_date': (date.today() - timedelta(days=12)).strftime('%Y-%m-%d'),
            'expected_delivery': (date.today() + timedelta(days=35)).strftime('%Y-%m-%d'),
            'description': 'Office Security System Installation'
        }
    ]
    
    # Sample Users
    users_data = [
        {'id': 1, 'username': 'demo_user', 'email': 'demo@acidtech.com', 'first_name': 'Demo', 'last_name': 'User'},
        {'id': 2, 'username': 'john_doe', 'email': 'john@acidtech.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'id': 3, 'username': 'jane_smith', 'email': 'jane@acidtech.com', 'first_name': 'Jane', 'last_name': 'Smith'}
    ]
    
    # Create DataFrames
    transactions_df = pd.DataFrame(transactions_data)
    purchase_orders_df = pd.DataFrame(purchase_orders_data)
    users_df = pd.DataFrame(users_data)
    
    # Create Excel writer object
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Write each sheet
        transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
        purchase_orders_df.to_excel(writer, sheet_name='PurchaseOrders', index=False)
        users_df.to_excel(writer, sheet_name='Users', index=False)
        
        # Format the sheets
        workbook = writer.book
        
        # Format Transactions sheet
        transactions_sheet = writer.sheets['Transactions']
        transactions_sheet.column_dimensions['A'].width = 10  # ID
        transactions_sheet.column_dimensions['B'].width = 15  # Type
        transactions_sheet.column_dimensions['C'].width = 25  # Vendor/Customer
        transactions_sheet.column_dimensions['D'].width = 15  # Amount
        transactions_sheet.column_dimensions['E'].width = 15  # Due Date
        transactions_sheet.column_dimensions['F'].width = 40  # Description
        transactions_sheet.column_dimensions['G'].width = 20  # Invoice Number
        transactions_sheet.column_dimensions['H'].width = 15  # Status
        
        # Format Purchase Orders sheet
        po_sheet = writer.sheets['PurchaseOrders']
        po_sheet.column_dimensions['A'].width = 10  # ID
        po_sheet.column_dimensions['B'].width = 20  # PO Number
        po_sheet.column_dimensions['C'].width = 25  # Vendor
        po_sheet.column_dimensions['D'].width = 15  # Total Amount
        po_sheet.column_dimensions['E'].width = 15  # Status
        po_sheet.column_dimensions['F'].width = 15  # Order Date
        po_sheet.column_dimensions['G'].width = 15  # Expected Delivery
        po_sheet.column_dimensions['H'].width = 45  # Description
        
        # Format Users sheet
        users_sheet = writer.sheets['Users']
        users_sheet.column_dimensions['A'].width = 10  # ID
        users_sheet.column_dimensions['B'].width = 20  # Username
        users_sheet.column_dimensions['C'].width = 30  # Email
        users_sheet.column_dimensions['D'].width = 20  # First Name
        users_sheet.column_dimensions['E'].width = 20  # Last Name
    
    # Calculate and print summary
    total_receivables = sum(t['amount'] for t in transactions_data if t['type'] == 'receivable')
    total_payables = sum(t['amount'] for t in transactions_data if t['type'] == 'payable')
    total_po_amount = sum(po['total_amount'] for po in purchase_orders_data)
    
    print(f"*** Sample Excel file generated: {output_path}")
    print(f"*** Data Summary:")
    print(f"   • Transactions: {len(transactions_data)} ({len([t for t in transactions_data if t['type'] == 'receivable'])} receivables, {len([t for t in transactions_data if t['type'] == 'payable'])} payables)")
    print(f"   • Total Receivables: ${total_receivables:,.2f}")
    print(f"   • Total Payables: ${total_payables:,.2f}")
    print(f"   • Net Cash Flow: ${total_receivables - total_payables:,.2f}")
    print(f"   • Purchase Orders: {len(purchase_orders_data)} (Total: ${total_po_amount:,.2f})")
    print(f"   • Users: {len(users_data)}")
    print(f"   • Sheets: Transactions, PurchaseOrders, Users")
    
    return output_path

if __name__ == "__main__":
    generate_sample_excel()