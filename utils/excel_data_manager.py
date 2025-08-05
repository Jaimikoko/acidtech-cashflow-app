"""
Excel Data Manager for File Mode QA Testing
Reads and manages data from Excel files instead of database
"""

import pandas as pd
import os
from datetime import datetime, date, timedelta
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class ExcelDataManager:
    """Manages data loading from Excel files for QA File Mode"""
    
    def __init__(self):
        self.data_cache = {}
        self.last_load_time = None
        self.cache_duration = 300  # 5 minutes
    
    def is_file_mode_enabled(self):
        """Check if File Mode is enabled"""
        return current_app.config.get('USE_FILE_MODE', False)
    
    def get_excel_path(self):
        """Get the path to the Excel data file"""
        return current_app.config.get('EXCEL_DATA_PATH')
    
    def should_reload_data(self):
        """Check if data should be reloaded from Excel"""
        if not self.last_load_time:
            return True
        return (datetime.now() - self.last_load_time).seconds > self.cache_duration
    
    def load_excel_data(self, force_reload=False):
        """Load data from Excel file with caching"""
        if not self.is_file_mode_enabled():
            return None
            
        if not force_reload and not self.should_reload_data():
            return self.data_cache
            
        excel_path = self.get_excel_path()
        
        if not os.path.exists(excel_path):
            logger.warning(f"Excel file not found: {excel_path}. Using default sample data.")
            return self._get_default_sample_data()
        
        try:
            logger.info(f"Loading Excel data from: {excel_path}")
            
            # Read all sheets
            excel_data = pd.read_excel(excel_path, sheet_name=None)
            
            self.data_cache = {
                'transactions': self._process_transactions(excel_data.get('Transactions', pd.DataFrame())),
                'purchase_orders': self._process_purchase_orders(excel_data.get('PurchaseOrders', pd.DataFrame())),
                'users': self._process_users(excel_data.get('Users', pd.DataFrame())),
                'cash_flow': self._process_cash_flow_transactions(excel_data.get('CashFlow', pd.DataFrame())),
                'metadata': {
                    'loaded_at': datetime.now(),
                    'file_path': excel_path,
                    'sheets': list(excel_data.keys())
                }
            }
            
            self.last_load_time = datetime.now()
            logger.info(f"Excel data loaded successfully. Sheets: {list(excel_data.keys())}")
            
            return self.data_cache
            
        except Exception as e:
            logger.error(f"Error loading Excel data: {e}")
            return self._get_default_sample_data()
    
    def _process_transactions(self, df):
        """Process transactions DataFrame"""
        if df.empty:
            return self._get_default_transactions()
        
        transactions = []
        for _, row in df.iterrows():
            try:
                # Parse date with fallback
                due_date = row.get('due_date', date.today() + timedelta(days=30))
                if isinstance(due_date, str):
                    due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
                elif pd.isna(due_date):
                    due_date = date.today() + timedelta(days=30)
                
                transaction = {
                    'id': int(row.get('id', 0)),
                    'type': str(row.get('type', 'receivable')),
                    'vendor_customer': str(row.get('vendor_customer', 'Unknown')),
                    'amount': float(row.get('amount', 0)),
                    'due_date': due_date,
                    'description': str(row.get('description', '')),
                    'invoice_number': str(row.get('invoice_number', '')),
                    'status': str(row.get('status', 'pending'))
                }
                transactions.append(transaction)
            except Exception as e:
                logger.warning(f"Error processing transaction row: {e}")
                continue
        
        return transactions
    
    def _process_purchase_orders(self, df):
        """Process purchase orders DataFrame"""
        if df.empty:
            return self._get_default_purchase_orders()
        
        pos = []
        for _, row in df.iterrows():
            try:
                order_date = row.get('order_date', date.today())
                if isinstance(order_date, str):
                    order_date = datetime.strptime(order_date, '%Y-%m-%d').date()
                elif pd.isna(order_date):
                    order_date = date.today()
                
                po = {
                    'id': int(row.get('id', 0)),
                    'po_number': str(row.get('po_number', '')),
                    'vendor': str(row.get('vendor', 'Unknown Vendor')),
                    'total_amount': float(row.get('total_amount', 0)),
                    'status': str(row.get('status', 'draft')),
                    'order_date': order_date,
                    'expected_delivery': order_date + timedelta(days=30),
                    'description': str(row.get('description', ''))
                }
                pos.append(po)
            except Exception as e:
                logger.warning(f"Error processing PO row: {e}")
                continue
        
        return pos
    
    def _process_users(self, df):
        """Process users DataFrame"""
        if df.empty:
            return [{'id': 1, 'username': 'demo_user', 'email': 'demo@acidtech.com'}]
        
        users = []
        for _, row in df.iterrows():
            user = {
                'id': int(row.get('id', 1)),
                'username': str(row.get('username', 'demo_user')),
                'email': str(row.get('email', 'demo@acidtech.com'))
            }
            users.append(user)
        
        return users
    
    def _get_default_sample_data(self):
        """Get default sample data when Excel file is not available"""
        return {
            'transactions': self._get_default_transactions(),
            'purchase_orders': self._get_default_purchase_orders(),
            'users': [{'id': 1, 'username': 'demo_user', 'email': 'demo@acidtech.com'}],
            'metadata': {
                'loaded_at': datetime.now(),
                'file_path': 'default_sample_data',
                'sheets': ['default']
            }
        }
    
    def _get_default_transactions(self):
        """Default transaction data"""
        return [
            {
                'id': 1, 'type': 'receivable', 'vendor_customer': 'Acme Corporation',
                'amount': 15000.00, 'due_date': date.today() + timedelta(days=30),
                'description': 'Consulting Services Q4', 'invoice_number': 'INV-2024-001', 'status': 'pending'
            },
            {
                'id': 2, 'type': 'payable', 'vendor_customer': 'Office Supplies Co',
                'amount': 2400.00, 'due_date': date.today() + timedelta(days=20),
                'description': 'Monthly Office Supplies', 'invoice_number': 'BILL-2024-001', 'status': 'pending'
            },
            {
                'id': 3, 'type': 'receivable', 'vendor_customer': 'Tech Solutions Inc',
                'amount': 8500.00, 'due_date': date.today() + timedelta(days=15),
                'description': 'Software Development Project', 'invoice_number': 'INV-2024-002', 'status': 'pending'
            },
            {
                'id': 4, 'type': 'payable', 'vendor_customer': 'IT Equipment Ltd',
                'amount': 5600.00, 'due_date': date.today() + timedelta(days=10),
                'description': 'Hardware Purchase', 'invoice_number': 'BILL-2024-002', 'status': 'pending'
            },
            {
                'id': 5, 'type': 'receivable', 'vendor_customer': 'Global Systems Ltd',
                'amount': 12250.00, 'due_date': date.today() + timedelta(days=45),
                'description': 'System Integration Services', 'invoice_number': 'INV-2024-003', 'status': 'pending'
            }
        ]
    
    def _get_default_purchase_orders(self):
        """Default purchase order data"""
        return [
            {
                'id': 1, 'po_number': 'PO-2024-001', 'vendor': 'Tech Hardware Solutions',
                'total_amount': 4500.00, 'status': 'approved', 'order_date': date.today() - timedelta(days=15),
                'expected_delivery': date.today() + timedelta(days=30), 'description': 'New Workstation Setup'
            },
            {
                'id': 2, 'po_number': 'PO-2024-002', 'vendor': 'Office Furniture Plus',
                'total_amount': 2800.00, 'status': 'sent', 'order_date': date.today() - timedelta(days=10),
                'expected_delivery': date.today() + timedelta(days=25), 'description': 'Office Furniture Upgrade'
            },
            {
                'id': 3, 'po_number': 'PO-2024-003', 'vendor': 'Software Licensing Co',
                'total_amount': 3600.00, 'status': 'draft', 'order_date': date.today() - timedelta(days=5),
                'expected_delivery': date.today() + timedelta(days=20), 'description': 'Annual Software Licenses'
            }
        ]
    
    # Data retrieval methods
    def get_transactions(self, transaction_type=None, status=None):
        """Get transactions with optional filtering"""
        data = self.load_excel_data()
        if not data:
            return []
        
        transactions = data.get('transactions', [])
        
        if transaction_type:
            transactions = [t for t in transactions if t['type'] == transaction_type]
        
        if status:
            transactions = [t for t in transactions if t['status'] == status]
        
        return transactions
    
    def get_purchase_orders(self, status=None):
        """Get purchase orders with optional status filtering"""
        data = self.load_excel_data()
        if not data:
            return []
        
        pos = data.get('purchase_orders', [])
        
        if status:
            pos = [po for po in pos if po['status'] == status]
        
        return pos
    
    def calculate_totals(self):
        """Calculate financial totals from Excel data"""
        transactions = self.get_transactions()
        
        total_receivables = sum(t['amount'] for t in transactions if t['type'] == 'receivable' and t['status'] == 'pending')
        total_payables = sum(t['amount'] for t in transactions if t['type'] == 'payable' and t['status'] == 'pending')
        
        overdue_receivables = len([t for t in transactions if t['type'] == 'receivable' and t['status'] == 'pending' and t['due_date'] < date.today()])
        overdue_payables = len([t for t in transactions if t['type'] == 'payable' and t['status'] == 'pending' and t['due_date'] < date.today()])
        
        return {
            'total_receivables': total_receivables,
            'total_payables': total_payables,
            'cash_available': total_receivables - total_payables,
            'overdue_receivables': overdue_receivables,
            'overdue_payables': overdue_payables
        }
    
    def get_cash_flow_transactions(self):
        """Get cash flow transactions from Excel with account information"""
        data = self.load_excel_data()
        if not data:
            return self._get_default_cash_flow_transactions()
        
        # Try to get CashFlow sheet first, then fall back to Transactions
        cash_flow_data = data.get('CashFlow', data.get('Transactions', []))
        
        if isinstance(cash_flow_data, list) and cash_flow_data:
            return cash_flow_data
        
        # If no cash flow data, convert transactions to cash flow format
        transactions = data.get('transactions', [])
        cash_flow_transactions = []
        
        for t in transactions:
            # Map transaction type to cash flow type
            cf_type = 'inflow' if t['type'] == 'receivable' else 'outflow'
            
            # Assign account based on transaction type and amount
            account = self._assign_account_to_transaction(t)
            
            cash_flow_transactions.append({
                'id': t['id'],
                'date': t['due_date'],
                'description': t['description'],
                'amount': t['amount'],
                'type': cf_type,
                'account': account,
                'status': t.get('status', 'pending')
            })
        
        return cash_flow_transactions
    
    def _assign_account_to_transaction(self, transaction):
        """Assign account based on transaction characteristics"""
        # Simple logic to assign accounts - can be made more sophisticated
        if transaction['type'] == 'receivable':
            return 'Revenue 4717'
        elif transaction['type'] == 'payable':
            # Assign based on amount or description
            if transaction['amount'] > 5000:
                return 'Bill Pay 4091'  # Large payments go to Bill Pay
            else:
                return 'Capital One 4709'  # Smaller payments go to Capital One
        
        return 'Capital One 4709'  # Default
    
    def _process_cash_flow_transactions(self, df):
        """Process cash flow transactions DataFrame"""
        if df.empty:
            return self._get_default_cash_flow_transactions()
        
        transactions = []
        for _, row in df.iterrows():
            try:
                # Parse date
                trans_date = row.get('date', date.today())
                if isinstance(trans_date, str):
                    trans_date = datetime.strptime(trans_date, '%Y-%m-%d').date()
                elif pd.isna(trans_date):
                    trans_date = date.today()
                
                transaction = {
                    'id': int(row.get('id', 0)),
                    'date': trans_date,
                    'description': str(row.get('description', '')),
                    'amount': float(row.get('amount', 0)),
                    'type': str(row.get('type', 'outflow')).lower(),
                    'account': str(row.get('account', 'Capital One 4709')),
                    'status': str(row.get('status', 'completed'))
                }
                transactions.append(transaction)
            except Exception as e:
                logger.warning(f"Error processing cash flow row: {e}")
                continue
        
        return transactions
    
    def _get_default_cash_flow_transactions(self):
        """Default cash flow transaction data"""
        return [
            {
                'id': 1, 'date': date.today() - timedelta(days=7),
                'description': 'Client Payment - Acme Corporation',
                'amount': 15000.00, 'type': 'inflow', 'account': 'Revenue 4717', 'status': 'completed'
            },
            {
                'id': 2, 'date': date.today() - timedelta(days=5),
                'description': 'Monthly Payroll',
                'amount': 8500.00, 'type': 'outflow', 'account': 'Bill Pay 4091', 'status': 'completed'
            },
            {
                'id': 3, 'date': date.today() - timedelta(days=3),
                'description': 'Office Supplies Purchase',
                'amount': 1200.00, 'type': 'outflow', 'account': 'Capital One 4709', 'status': 'completed'
            },
            {
                'id': 4, 'date': date.today() - timedelta(days=2),
                'description': 'Tech Solutions Invoice Payment',
                'amount': 12000.00, 'type': 'inflow', 'account': 'Revenue 4717', 'status': 'completed'
            },
            {
                'id': 5, 'date': date.today() - timedelta(days=1),
                'description': 'Utilities Payment',
                'amount': 850.00, 'type': 'outflow', 'account': 'Capital One 4709', 'status': 'completed'
            },
            {
                'id': 6, 'date': date.today(),
                'description': 'Equipment Purchase',
                'amount': 3500.00, 'type': 'outflow', 'account': 'Bill Pay 4091', 'status': 'pending'
            }
        ]

# Global instance
excel_manager = ExcelDataManager()