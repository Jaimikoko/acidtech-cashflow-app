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
    
    # Sample Cash Flow Data with Account Information
    cash_flow_data = [
        # Revenue 4717 - Inflows
        {
            'id': 1, 'date': (date.today() - timedelta(days=14)).strftime('%Y-%m-%d'),
            'description': 'Client Payment - Acme Corporation', 'amount': 15000.00,
            'type': 'inflow', 'account': 'Revenue 4717', 'status': 'completed'
        },
        {
            'id': 2, 'date': (date.today() - timedelta(days=10)).strftime('%Y-%m-%d'),
            'description': 'Tech Solutions Invoice Payment', 'amount': 12000.00,
            'type': 'inflow', 'account': 'Revenue 4717', 'status': 'completed'
        },
        {
            'id': 3, 'date': (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'description': 'Global Systems Contract Payment', 'amount': 18500.00,
            'type': 'inflow', 'account': 'Revenue 4717', 'status': 'completed'
        },
        {
            'id': 4, 'date': (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'description': 'Expected Payment - DataFlow Corp', 'amount': 8200.00,
            'type': 'inflow', 'account': 'Revenue 4717', 'status': 'pending'
        },
        
        # Bill Pay 4091 - Major Outflows (Payroll, Large Vendors)
        {
            'id': 5, 'date': (date.today() - timedelta(days=12)).strftime('%Y-%m-%d'),
            'description': 'Monthly Payroll - December', 'amount': 8500.00,
            'type': 'outflow', 'account': 'Bill Pay 4091', 'status': 'completed'
        },
        {
            'id': 6, 'date': (date.today() - timedelta(days=8)).strftime('%Y-%m-%d'),
            'description': 'IT Equipment Purchase', 'amount': 5600.00,
            'type': 'outflow', 'account': 'Bill Pay 4091', 'status': 'completed'
        },
        {
            'id': 7, 'date': (date.today() - timedelta(days=4)).strftime('%Y-%m-%d'),
            'description': 'Marketing Agency Payment', 'amount': 3200.00,
            'type': 'outflow', 'account': 'Bill Pay 4091', 'status': 'completed'
        },
        {
            'id': 8, 'date': (date.today() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'description': 'Scheduled Payroll - January', 'amount': 8500.00,
            'type': 'outflow', 'account': 'Bill Pay 4091', 'status': 'pending'
        },
        
        # Capital One 4709 - Mixed (Credit Card, Small Expenses)
        {
            'id': 9, 'date': (date.today() - timedelta(days=9)).strftime('%Y-%m-%d'),
            'description': 'Office Supplies Purchase', 'amount': 1200.00,
            'type': 'outflow', 'account': 'Capital One 4709', 'status': 'completed'
        },
        {
            'id': 10, 'date': (date.today() - timedelta(days=6)).strftime('%Y-%m-%d'),
            'description': 'Utilities Payment', 'amount': 850.00,
            'type': 'outflow', 'account': 'Capital One 4709', 'status': 'completed'
        },
        {
            'id': 11, 'date': (date.today() - timedelta(days=3)).strftime('%Y-%m-%d'),
            'description': 'Business Travel Expenses', 'amount': 1800.00,
            'type': 'outflow', 'account': 'Capital One 4709', 'status': 'completed'
        },
        {
            'id': 12, 'date': (date.today() - timedelta(days=2)).strftime('%Y-%m-%d'),
            'description': 'Credit Card Payment Received', 'amount': 2500.00,
            'type': 'inflow', 'account': 'Capital One 4709', 'status': 'completed'
        },
        {
            'id': 13, 'date': (date.today() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'description': 'Legal Services Payment', 'amount': 1800.00,
            'type': 'outflow', 'account': 'Capital One 4709', 'status': 'pending'
        },
        {
            'id': 14, 'date': (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'description': 'Monthly Internet/Phone', 'amount': 450.00,
            'type': 'outflow', 'account': 'Capital One 4709', 'status': 'pending'
        }
    ]
    
    # Create DataFrames
    transactions_df = pd.DataFrame(transactions_data)
    purchase_orders_df = pd.DataFrame(purchase_orders_data)
    users_df = pd.DataFrame(users_data)
    cash_flow_df = pd.DataFrame(cash_flow_data)
    
    # Create Excel writer object
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Write each sheet
        transactions_df.to_excel(writer, sheet_name='Transactions', index=False)
        purchase_orders_df.to_excel(writer, sheet_name='PurchaseOrders', index=False)
        users_df.to_excel(writer, sheet_name='Users', index=False)
        cash_flow_df.to_excel(writer, sheet_name='CashFlow', index=False)
        
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
        
        # Format Cash Flow sheet
        cash_flow_sheet = writer.sheets['CashFlow']
        cash_flow_sheet.column_dimensions['A'].width = 10  # ID
        cash_flow_sheet.column_dimensions['B'].width = 15  # Date
        cash_flow_sheet.column_dimensions['C'].width = 40  # Description
        cash_flow_sheet.column_dimensions['D'].width = 15  # Amount
        cash_flow_sheet.column_dimensions['E'].width = 12  # Type
        cash_flow_sheet.column_dimensions['F'].width = 20  # Account
        cash_flow_sheet.column_dimensions['G'].width = 15  # Status
    
    # Calculate and print summary
    total_receivables = sum(t['amount'] for t in transactions_data if t['type'] == 'receivable')
    total_payables = sum(t['amount'] for t in transactions_data if t['type'] == 'payable')
    total_po_amount = sum(po['total_amount'] for po in purchase_orders_data)
    
    # Cash flow summary
    total_inflows = sum(cf['amount'] for cf in cash_flow_data if cf['type'] == 'inflow')
    total_outflows = sum(cf['amount'] for cf in cash_flow_data if cf['type'] == 'outflow')
    
    # Account breakdown
    revenue_total = sum(cf['amount'] for cf in cash_flow_data if cf['account'] == 'Revenue 4717' and cf['type'] == 'inflow')
    billpay_total = sum(cf['amount'] for cf in cash_flow_data if cf['account'] == 'Bill Pay 4091' and cf['type'] == 'outflow')
    capital_inflows = sum(cf['amount'] for cf in cash_flow_data if cf['account'] == 'Capital One 4709' and cf['type'] == 'inflow')
    capital_outflows = sum(cf['amount'] for cf in cash_flow_data if cf['account'] == 'Capital One 4709' and cf['type'] == 'outflow')
    
    print(f"*** Sample Excel file generated: {output_path}")
    print(f"*** Data Summary:")
    print(f"   • Transactions: {len(transactions_data)} ({len([t for t in transactions_data if t['type'] == 'receivable'])} receivables, {len([t for t in transactions_data if t['type'] == 'payable'])} payables)")
    print(f"   • Total Receivables: ${total_receivables:,.2f}")
    print(f"   • Total Payables: ${total_payables:,.2f}")
    print(f"   • Net A/R-A/P Flow: ${total_receivables - total_payables:,.2f}")
    print(f"   • Purchase Orders: {len(purchase_orders_data)} (Total: ${total_po_amount:,.2f})")
    print(f"   • Cash Flow Transactions: {len(cash_flow_data)}")
    print(f"   • Total Cash Inflows: ${total_inflows:,.2f}")
    print(f"   • Total Cash Outflows: ${total_outflows:,.2f}")
    print(f"   • Net Cash Flow: ${total_inflows - total_outflows:,.2f}")
    print(f"   • Account Breakdown:")
    print(f"     - Revenue 4717: ${revenue_total:,.2f} inflows")
    print(f"     - Bill Pay 4091: ${billpay_total:,.2f} outflows")
    print(f"     - Capital One 4709: ${capital_inflows:,.2f} inflows, ${capital_outflows:,.2f} outflows")
    print(f"   • Users: {len(users_data)}")
    print(f"   • Sheets: Transactions, PurchaseOrders, Users, CashFlow")
    
    return output_path

if __name__ == "__main__":
    generate_sample_excel()