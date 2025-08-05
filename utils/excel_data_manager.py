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
            
            # Process all sheets with error handling
            processed_data = {
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
            
            self.data_cache = processed_data
            
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
    
    def get_cash_flow_transactions(self, account=None, year=None, month=None):
        """Get cash flow transactions from Excel with account information and filters"""
        data = self.load_excel_data()
        if not data:
            return self._get_default_cash_flow_transactions()
        
        # Get cash flow data from cache or load from Excel
        cash_flow_data = data.get('cash_flow', [])
        
        if not cash_flow_data:
            # Try to get CashFlow sheet directly
            excel_data = pd.read_excel(self.get_excel_path(), sheet_name='CashFlow') if os.path.exists(self.get_excel_path() or '') else pd.DataFrame()
            if not excel_data.empty:
                cash_flow_data = self._process_cash_flow_transactions(excel_data)
            else:
                # Fallback to converting transactions
                transactions = data.get('transactions', [])
                cash_flow_data = self._convert_transactions_to_cash_flow(transactions)
        
        # Apply filters
        filtered_data = cash_flow_data
        
        if account:
            filtered_data = [t for t in filtered_data if t.get('account') == account]
        
        if year:
            filtered_data = [t for t in filtered_data if self._get_year_from_date(t.get('date')) == year]
        
        if month:
            filtered_data = [t for t in filtered_data if self._get_month_from_date(t.get('date')) == month]
        
        return filtered_data
    
    def get_account_summary(self, account, year=2025):
        """Get comprehensive summary for a specific account"""
        transactions = self.get_cash_flow_transactions(account=account, year=year)
        
        if not transactions:
            return self._get_default_account_summary(account)
        
        # Calculate totals
        total_amount = sum(t['amount'] for t in transactions)
        transaction_count = len(transactions)
        
        # Monthly breakdown
        monthly_data = {}
        for month in range(1, 13):
            month_transactions = [t for t in transactions if self._get_month_from_date(t.get('date')) == month]
            monthly_data[month] = {
                'amount': sum(t['amount'] for t in month_transactions),
                'count': len(month_transactions),
                'transactions': month_transactions[:5]  # Top 5 for display
            }
        
        # Calculate month-over-month variations
        variations = {}
        for month in range(2, 13):
            current = monthly_data[month]['amount']
            previous = monthly_data[month-1]['amount']
            if previous > 0:
                variation = ((current - previous) / previous) * 100
            else:
                variation = 100 if current > 0 else 0
            variations[month] = variation
        
        # Top customers/vendors (if available)
        if account == 'Revenue 4717':
            customer_totals = {}
            for t in transactions:
                customer = t.get('customer', 'Unknown')
                if customer not in customer_totals:
                    customer_totals[customer] = 0
                customer_totals[customer] += t['amount']
            top_entities = sorted(customer_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        else:
            # For other accounts, group by description patterns
            entity_totals = {}
            for t in transactions:
                desc = t.get('description', '').split(' - ')[0]  # Take first part as entity
                if desc not in entity_totals:
                    entity_totals[desc] = 0
                entity_totals[desc] += t['amount']
            top_entities = sorted(entity_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Recent transactions
        recent_transactions = sorted(transactions, key=lambda x: x.get('date', ''), reverse=True)[:10]
        
        return {
            'account': account,
            'year': year,
            'total_amount': total_amount,
            'transaction_count': transaction_count,
            'monthly_data': monthly_data,
            'variations': variations,
            'top_entities': top_entities,
            'recent_transactions': recent_transactions,
            'average_monthly': total_amount / 12,
            'peak_month': max(monthly_data.items(), key=lambda x: x[1]['amount'])[0],
            'lowest_month': min(monthly_data.items(), key=lambda x: x[1]['amount'])[0]
        }
    
    def get_aging_analysis(self, account='Revenue 4717'):
        """Get aging analysis for receivables related to account"""
        # Get A/R transactions related to the account
        transactions = self.get_transactions(transaction_type='receivable')
        
        # Filter for specific account if needed (future enhancement)
        aging_buckets = {
            'current': [],      # 0-30 days
            '30_days': [],      # 31-60 days
            '60_days': [],      # 61-90 days
            '90_plus': []       # 90+ days
        }
        
        today = date.today()
        
        for transaction in transactions:
            if transaction['status'] != 'pending':
                continue
                
            due_date = transaction['due_date']
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            
            days_overdue = (today - due_date).days
            
            if days_overdue <= 30:
                aging_buckets['current'].append(transaction)
            elif days_overdue <= 60:
                aging_buckets['30_days'].append(transaction)
            elif days_overdue <= 90:
                aging_buckets['60_days'].append(transaction)
            else:
                aging_buckets['90_plus'].append(transaction)
        
        # Calculate totals for each bucket
        aging_summary = {}
        for bucket, transactions_list in aging_buckets.items():
            aging_summary[bucket] = {
                'count': len(transactions_list),
                'amount': sum(t['amount'] for t in transactions_list),
                'transactions': transactions_list
            }
        
        return aging_summary
    
    def _convert_transactions_to_cash_flow(self, transactions):
        """Convert A/R and A/P transactions to cash flow format"""
        cash_flow_transactions = []
        
        for t in transactions:
            cf_type = 'inflow' if t['type'] == 'receivable' else 'outflow'
            account = self._assign_account_to_transaction(t)
            
            cash_flow_transactions.append({
                'id': t['id'],
                'date': t['due_date'],
                'description': t['description'],
                'amount': t['amount'],
                'type': cf_type,
                'account': account,
                'status': t.get('status', 'pending'),
                'customer': t.get('vendor_customer', 'Unknown')
            })
        
        return cash_flow_transactions
    
    def _get_year_from_date(self, date_value):
        """Extract year from date value"""
        if isinstance(date_value, str):
            return int(date_value.split('-')[0])
        elif hasattr(date_value, 'year'):
            return date_value.year
        return 2025  # Default
    
    def _get_month_from_date(self, date_value):
        """Extract month from date value"""
        if isinstance(date_value, str):
            return int(date_value.split('-')[1])
        elif hasattr(date_value, 'month'):
            return date_value.month
        return 1  # Default
    
    def _get_default_account_summary(self, account):
        """Default account summary for fallback"""
        return {
            'account': account,
            'year': 2025,
            'total_amount': 0,
            'transaction_count': 0,
            'monthly_data': {i: {'amount': 0, 'count': 0, 'transactions': []} for i in range(1, 13)},
            'variations': {i: 0 for i in range(2, 13)},
            'top_entities': [],
            'recent_transactions': [],
            'average_monthly': 0,
            'peak_month': 1,
            'lowest_month': 1
        }
    
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