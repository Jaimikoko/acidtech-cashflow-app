from flask import render_template, request, jsonify, current_app
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from database import db
from utils.excel_data_manager import excel_manager
import json

from . import cash_flow_bp

# Account mappings for the three main accounts
ACCOUNT_MAPPINGS = {
    'Revenue 4717': {'name': 'Revenue 4717', 'type': 'inflow', 'color': '#10b981'},
    'Bill Pay 4091': {'name': 'Bill Pay / Payroll 4091', 'type': 'outflow', 'color': '#ef4444'},
    'Capital One 4709': {'name': 'Capital One 4709', 'type': 'mixed', 'color': '#3b82f6'}
}

@cash_flow_bp.route('/')
def index():
    """Cash Flow main page with File Mode support"""
    
    # Get filter parameters
    account_filter = request.args.get('account', 'all')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Set default date range (last 90 days)
    if not date_from or not date_to:
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        date_from = start_date.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
    
    file_mode = current_app.config.get('USE_FILE_MODE', False)
    
    if file_mode:
        # File Mode: Use Excel data
        try:
            cash_flow_data = _get_cash_flow_from_excel(account_filter, date_from, date_to)
        except Exception as e:
            # Fallback to sample data
            cash_flow_data = _get_sample_cash_flow_data()
    else:
        # Database Mode: Use SQLAlchemy
        try:
            cash_flow_data = _get_cash_flow_from_database(account_filter, date_from, date_to)
        except Exception as e:
            # Fallback to sample data
            cash_flow_data = _get_sample_cash_flow_data()
    
    return render_template('cash_flow/index.html',
                         cash_flow_data=cash_flow_data,
                         account_mappings=ACCOUNT_MAPPINGS,
                         account_filter=account_filter,
                         date_from=date_from,
                         date_to=date_to,
                         file_mode=file_mode)

@cash_flow_bp.route('/api/chart-data')
def chart_data():
    """API endpoint for cash flow chart data"""
    
    account_filter = request.args.get('account', 'all')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    period = request.args.get('period', 'weekly')  # weekly or monthly
    
    # Set default date range
    if not date_from or not date_to:
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        date_from = start_date.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
    
    file_mode = current_app.config.get('USE_FILE_MODE', False)
    
    if file_mode:
        chart_data = _generate_chart_data_from_excel(account_filter, date_from, date_to, period)
    else:
        chart_data = _generate_chart_data_from_database(account_filter, date_from, date_to, period)
    
    return jsonify(chart_data)

@cash_flow_bp.route('/api/summary')
def summary():
    """API endpoint for cash flow summary data"""
    
    account_filter = request.args.get('account', 'all')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    file_mode = current_app.config.get('USE_FILE_MODE', False)
    
    if file_mode:
        summary_data = _get_summary_from_excel(account_filter, date_from, date_to)
    else:
        summary_data = _get_summary_from_database(account_filter, date_from, date_to)
    
    return jsonify(summary_data)

def _get_cash_flow_from_excel(account_filter, date_from, date_to):
    """Get cash flow data from Excel files"""
    
    transactions = excel_manager.get_cash_flow_transactions()
    
    # Convert date strings to date objects for filtering
    start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
    end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Filter transactions
    filtered_transactions = []
    for transaction in transactions:
        trans_date = transaction.get('date')
        if isinstance(trans_date, str):
            trans_date = datetime.strptime(trans_date, '%Y-%m-%d').date()
        
        # Date filter
        if not (start_date <= trans_date <= end_date):
            continue
            
        # Account filter
        if account_filter != 'all' and transaction.get('account') != account_filter:
            continue
            
        filtered_transactions.append(transaction)
    
    # Calculate totals
    total_inflows = sum(t['amount'] for t in filtered_transactions if t['type'] == 'inflow')
    total_outflows = sum(t['amount'] for t in filtered_transactions if t['type'] == 'outflow')
    net_flow = total_inflows - total_outflows
    
    # Group by account
    account_summary = {}
    for account_key in ACCOUNT_MAPPINGS.keys():
        account_transactions = [t for t in filtered_transactions if t.get('account') == account_key]
        account_inflows = sum(t['amount'] for t in account_transactions if t['type'] == 'inflow')
        account_outflows = sum(t['amount'] for t in account_transactions if t['type'] == 'outflow')
        
        account_summary[account_key] = {
            'inflows': account_inflows,
            'outflows': account_outflows,
            'net': account_inflows - account_outflows,
            'transaction_count': len(account_transactions)
        }
    
    return {
        'transactions': filtered_transactions[:20],  # Limit for display
        'total_inflows': total_inflows,
        'total_outflows': total_outflows,
        'net_flow': net_flow,
        'account_summary': account_summary,
        'transaction_count': len(filtered_transactions)
    }

def _get_cash_flow_from_database(account_filter, date_from, date_to):
    """Get cash flow data from database - placeholder for future implementation"""
    
    # For now, return sample data when database mode is used
    # TODO: Implement database queries when cash flow tables are created
    return _get_sample_cash_flow_data()

def _generate_chart_data_from_excel(account_filter, date_from, date_to, period):
    """Generate chart data from Excel transactions"""
    
    transactions = excel_manager.get_cash_flow_transactions()
    
    start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
    end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Determine period increment
    if period == 'monthly':
        delta = timedelta(days=30)
    else:  # weekly
        delta = timedelta(days=7)
    
    chart_data = {
        'labels': [],
        'datasets': [
            {
                'label': 'Inflows',
                'data': [],
                'backgroundColor': 'rgba(16, 185, 129, 0.8)',
                'borderColor': 'rgb(16, 185, 129)',
                'borderWidth': 2
            },
            {
                'label': 'Outflows', 
                'data': [],
                'backgroundColor': 'rgba(239, 68, 68, 0.8)',
                'borderColor': 'rgb(239, 68, 68)',
                'borderWidth': 2
            }
        ]
    }
    
    current_date = start_date
    while current_date <= end_date:
        period_end = current_date + delta
        if period_end > end_date:
            period_end = end_date
        
        # Format label
        if period == 'monthly':
            label = current_date.strftime('%b %Y')
        else:
            label = current_date.strftime('%m/%d')
        
        chart_data['labels'].append(label)
        
        # Calculate inflows and outflows for this period
        period_inflows = 0
        period_outflows = 0
        
        for transaction in transactions:
            trans_date = transaction.get('date')
            if isinstance(trans_date, str):
                trans_date = datetime.strptime(trans_date, '%Y-%m-%d').date()
            
            if current_date <= trans_date < period_end:
                # Account filter
                if account_filter != 'all' and transaction.get('account') != account_filter:
                    continue
                
                if transaction['type'] == 'inflow':
                    period_inflows += transaction['amount']
                else:
                    period_outflows += transaction['amount']
        
        chart_data['datasets'][0]['data'].append(period_inflows)
        chart_data['datasets'][1]['data'].append(period_outflows)
        
        current_date = period_end
    
    return chart_data

def _generate_chart_data_from_database(account_filter, date_from, date_to, period):
    """Generate chart data from database - placeholder"""
    
    # TODO: Implement database chart data generation
    return {
        'labels': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'datasets': [
            {
                'label': 'Inflows',
                'data': [15000, 12000, 18000, 16000],
                'backgroundColor': 'rgba(16, 185, 129, 0.8)',
                'borderColor': 'rgb(16, 185, 129)',
                'borderWidth': 2
            },
            {
                'label': 'Outflows',
                'data': [8000, 9000, 7500, 8500],
                'backgroundColor': 'rgba(239, 68, 68, 0.8)',
                'borderColor': 'rgb(239, 68, 68)',
                'borderWidth': 2
            }
        ]
    }

def _get_summary_from_excel(account_filter, date_from, date_to):
    """Get summary data from Excel"""
    
    cash_flow_data = _get_cash_flow_from_excel(account_filter, date_from, date_to)
    
    return {
        'total_inflows': cash_flow_data['total_inflows'],
        'total_outflows': cash_flow_data['total_outflows'],
        'net_flow': cash_flow_data['net_flow'],
        'projected_balance': cash_flow_data['net_flow'] + 50000,  # Assuming starting balance
        'account_summary': cash_flow_data['account_summary']
    }

def _get_summary_from_database(account_filter, date_from, date_to):
    """Get summary data from database - placeholder"""
    
    # TODO: Implement database summary
    return {
        'total_inflows': 61000,
        'total_outflows': 33000,
        'net_flow': 28000,
        'projected_balance': 78000,
        'account_summary': {
            'Revenue 4717': {'inflows': 45000, 'outflows': 0, 'net': 45000, 'transaction_count': 8},
            'Bill Pay 4091': {'inflows': 0, 'outflows': 25000, 'net': -25000, 'transaction_count': 12},
            'Capital One 4709': {'inflows': 16000, 'outflows': 8000, 'net': 8000, 'transaction_count': 6}
        }
    }

def _get_sample_cash_flow_data():
    """Sample data for fallback"""
    
    return {
        'transactions': [
            {
                'id': 1, 'date': date.today() - timedelta(days=5), 'description': 'Client Payment - Acme Corp',
                'amount': 15000, 'type': 'inflow', 'account': 'Revenue 4717'
            },
            {
                'id': 2, 'date': date.today() - timedelta(days=3), 'description': 'Payroll Payment',
                'amount': 8000, 'type': 'outflow', 'account': 'Bill Pay 4091'
            },
            {
                'id': 3, 'date': date.today() - timedelta(days=1), 'description': 'Office Supplies',
                'amount': 1200, 'type': 'outflow', 'account': 'Capital One 4709'
            }
        ],
        'total_inflows': 61000,
        'total_outflows': 33000,
        'net_flow': 28000,
        'account_summary': {
            'Revenue 4717': {'inflows': 45000, 'outflows': 0, 'net': 45000, 'transaction_count': 8},
            'Bill Pay 4091': {'inflows': 0, 'outflows': 25000, 'net': -25000, 'transaction_count': 12},
            'Capital One 4709': {'inflows': 16000, 'outflows': 8000, 'net': 8000, 'transaction_count': 6}
        },
        'transaction_count': 26
    }