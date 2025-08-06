from flask import render_template, request, jsonify, current_app, redirect, url_for, flash
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from database import db
from utils.excel_data_manager import excel_manager
import json

from . import cash_flow_bp

# Account mappings for the four main accounts
ACCOUNT_MAPPINGS = {
    'Revenue 4717': {'name': 'Revenue 4717', 'type': 'inflow', 'color': '#10b981'},
    'Bill Pay 5285': {'name': 'Bill Pay 5285', 'type': 'outflow', 'color': '#ef4444'},
    'Payroll 4079': {'name': 'Payroll 4079', 'type': 'outflow', 'color': '#f59e0b'},
    'Capital One': {'name': 'Capital One', 'type': 'mixed', 'color': '#3b82f6'}
}

@cash_flow_bp.route('/')
def index():
    """Cash Flow main page with enhanced account analysis"""
    
    # Get filter parameters
    account_filter = request.args.get('account', 'all')
    year = int(request.args.get('year', 2025))
    month = request.args.get('month')
    month = int(month) if month else None
    
    file_mode = current_app.config.get('USE_FILE_MODE', False)
    
    # Get account summaries for all accounts
    account_summaries = {}
    for account_key in ACCOUNT_MAPPINGS.keys():
        if file_mode:
            try:
                account_summaries[account_key] = excel_manager.get_account_summary(account_key, year)
            except Exception as e:
                account_summaries[account_key] = _get_default_account_summary(account_key)
        else:
            # Database mode - placeholder for now
            account_summaries[account_key] = _get_default_account_summary(account_key)
    
    # Get overall cash flow data
    if file_mode:
        try:
            cash_flow_data = _get_comprehensive_cash_flow_data(account_filter, year, month)
        except Exception as e:
            cash_flow_data = _get_sample_cash_flow_data()
    else:
        cash_flow_data = _get_sample_cash_flow_data()
    
    # Get aging analysis for Revenue 4717
    aging_analysis = None
    if file_mode:
        try:
            aging_analysis = excel_manager.get_aging_analysis('Revenue 4717')
        except Exception as e:
            aging_analysis = _get_default_aging_analysis()
    
    return render_template('cash_flow/index.html',
                         cash_flow_data=cash_flow_data,
                         account_mappings=ACCOUNT_MAPPINGS,
                         account_summaries=account_summaries,
                         aging_analysis=aging_analysis,
                         account_filter=account_filter,
                         year=year,
                         month=month,
                         file_mode=file_mode)

@cash_flow_bp.route('/account/<account_name>')
def account_detail(account_name):
    """Detailed view for a specific account"""
    
    if account_name not in ACCOUNT_MAPPINGS:
        return redirect(url_for('cash_flow.index'))
    
    year = int(request.args.get('year', 2025))
    file_mode = current_app.config.get('USE_FILE_MODE', False)
    
    if file_mode:
        try:
            account_data = excel_manager.get_account_summary(account_name, year)
            transactions = excel_manager.get_cash_flow_transactions(account=account_name, year=year)
        except Exception as e:
            account_data = _get_default_account_summary(account_name)
            transactions = []
    else:
        # Database mode - placeholder
        account_data = _get_default_account_summary(account_name)
        transactions = []
    
    return render_template('cash_flow/account_detail.html',
                         account_data=account_data,
                         account_info=ACCOUNT_MAPPINGS[account_name],
                         transactions=transactions,
                         year=year,
                         file_mode=file_mode)

@cash_flow_bp.route('/export/<account_name>')
def export_account_data(account_name):
    """Export account data to Excel"""
    
    if account_name not in ACCOUNT_MAPPINGS:
        return redirect(url_for('cash_flow.index'))
    
    year = int(request.args.get('year', 2025))
    file_mode = current_app.config.get('USE_FILE_MODE', False)
    
    if file_mode:
        try:
            transactions = excel_manager.get_cash_flow_transactions(account=account_name, year=year)
        except Exception as e:
            transactions = []
    else:
        transactions = []  # Database mode placeholder
    
    # Create DataFrame and Excel file
    if transactions:
        import pandas as pd
        import os
        from flask import send_file
        import tempfile
        
        df = pd.DataFrame(transactions)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        df.to_excel(temp_file.name, index=False, sheet_name=f'{account_name}_{year}')
        temp_file.close()
        
        filename = f"{account_name.replace(' ', '_')}_{year}_export.xlsx"
        
        return send_file(temp_file.name, as_attachment=True, download_name=filename)
    
    flash('No data available for export', 'warning')
    return redirect(url_for('cash_flow.account_detail', account_name=account_name))

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

def _get_comprehensive_cash_flow_data(account_filter, year, month=None):
    """Get comprehensive cash flow data from Excel with enhanced analysis"""
    
    # Get all transactions for the year
    all_transactions = excel_manager.get_cash_flow_transactions(year=year)
    
    # Apply account filter
    if account_filter != 'all':
        filtered_transactions = [t for t in all_transactions if t.get('account') == account_filter]
    else:
        filtered_transactions = all_transactions
    
    # Apply month filter if specified
    if month:
        filtered_transactions = [t for t in filtered_transactions 
                               if excel_manager._get_month_from_date(t.get('date')) == month]
    
    # Calculate totals
    total_inflows = sum(t['amount'] for t in filtered_transactions if t['type'] == 'inflow')
    total_outflows = sum(t['amount'] for t in filtered_transactions if t['type'] == 'outflow')
    net_flow = total_inflows - total_outflows
    
    # Monthly breakdown for charts
    monthly_data = {}
    for m in range(1, 13):
        month_transactions = [t for t in all_transactions 
                            if excel_manager._get_month_from_date(t.get('date')) == m]
        month_inflows = sum(t['amount'] for t in month_transactions if t['type'] == 'inflow')
        month_outflows = sum(t['amount'] for t in month_transactions if t['type'] == 'outflow')
        
        if account_filter != 'all':
            month_transactions = [t for t in month_transactions if t.get('account') == account_filter]
            month_inflows = sum(t['amount'] for t in month_transactions if t['type'] == 'inflow')
            month_outflows = sum(t['amount'] for t in month_transactions if t['type'] == 'outflow')
        
        monthly_data[m] = {
            'inflows': month_inflows,
            'outflows': month_outflows,
            'net': month_inflows - month_outflows,
            'transactions': len(month_transactions)
        }
    
    # Group by account for summary
    account_summary = {}
    for account_key in ACCOUNT_MAPPINGS.keys():
        account_transactions = [t for t in all_transactions if t.get('account') == account_key]
        account_inflows = sum(t['amount'] for t in account_transactions if t['type'] == 'inflow')
        account_outflows = sum(t['amount'] for t in account_transactions if t['type'] == 'outflow')
        
        account_summary[account_key] = {
            'inflows': account_inflows,
            'outflows': account_outflows,
            'net': account_inflows - account_outflows,
            'transaction_count': len(account_transactions)
        }
    
    # Recent transactions for display
    recent_transactions = sorted(filtered_transactions, 
                               key=lambda x: x.get('date', ''), reverse=True)[:15]
    
    return {
        'transactions': recent_transactions,
        'total_inflows': total_inflows,
        'total_outflows': total_outflows,
        'net_flow': net_flow,
        'monthly_data': monthly_data,
        'account_summary': account_summary,
        'transaction_count': len(filtered_transactions),
        'year': year,
        'month': month
    }

def _get_cash_flow_from_database(account_filter, date_from, date_to):
    """Get cash flow data from database - placeholder for future implementation"""
    
    # For now, return sample data when database mode is used
    # TODO: Implement database queries when cash flow tables are created
    return _get_sample_cash_flow_data()

@cash_flow_bp.route('/api/monthly-chart')
def monthly_chart_data():
    """API endpoint for monthly cash flow chart with bars and lines"""
    
    account_filter = request.args.get('account', 'all')
    year = int(request.args.get('year', 2025))
    
    file_mode = current_app.config.get('USE_FILE_MODE', False)
    
    if file_mode:
        try:
            cash_flow_data = _get_comprehensive_cash_flow_data(account_filter, year)
            monthly_data = cash_flow_data['monthly_data']
        except Exception as e:
            monthly_data = {i: {'inflows': 0, 'outflows': 0, 'net': 0} for i in range(1, 13)}
    else:
        # Database mode placeholder
        monthly_data = {i: {'inflows': 15000, 'outflows': 8000, 'net': 7000} for i in range(1, 13)}
    
    # Prepare chart data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    inflows_data = [monthly_data[i]['inflows'] for i in range(1, 13)]
    outflows_data = [monthly_data[i]['outflows'] for i in range(1, 13)]
    net_data = [monthly_data[i]['net'] for i in range(1, 13)]
    
    # Calculate cumulative balance (assuming starting balance)
    starting_balance = 50000  # Configurable starting balance
    cumulative_balance = [starting_balance]
    
    for net_amount in net_data:
        cumulative_balance.append(cumulative_balance[-1] + net_amount)
    
    chart_data = {
        'labels': months,
        'datasets': [
            {
                'label': 'Inflows',
                'type': 'bar',
                'data': inflows_data,
                'backgroundColor': 'rgba(16, 185, 129, 0.8)',
                'borderColor': 'rgb(16, 185, 129)',
                'borderWidth': 2,
                'yAxisID': 'y'
            },
            {
                'label': 'Outflows',
                'type': 'bar', 
                'data': outflows_data,
                'backgroundColor': 'rgba(239, 68, 68, 0.8)',
                'borderColor': 'rgb(239, 68, 68)',
                'borderWidth': 2,
                'yAxisID': 'y'
            },
            {
                'label': 'Cumulative Balance',
                'type': 'line',
                'data': cumulative_balance[1:],  # Skip initial balance for alignment
                'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                'borderColor': 'rgb(59, 130, 246)',
                'borderWidth': 3,
                'fill': False,
                'tension': 0.4,
                'yAxisID': 'y1'
            }
        ]
    }
    
    return jsonify(chart_data)

def _generate_chart_data_from_excel(account_filter, date_from, date_to, period):
    """Legacy chart data generation - kept for compatibility"""
    
    # Redirect to new monthly chart for better visualization
    return _generate_monthly_chart_data(account_filter, 2025)

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
    """Enhanced sample data for fallback"""
    
    return {
        'transactions': [
            {
                'id': 1, 'date': date.today() - timedelta(days=5), 'description': 'Client Payment - Acme Corp',
                'amount': 15000, 'type': 'inflow', 'account': 'Revenue 4717', 'customer': 'Acme Corporation'
            },
            {
                'id': 2, 'date': date.today() - timedelta(days=3), 'description': 'Payroll Payment',
                'amount': 8000, 'type': 'outflow', 'account': 'Bill Pay 4091', 'customer': 'Payroll'
            },
            {
                'id': 3, 'date': date.today() - timedelta(days=1), 'description': 'Office Supplies',
                'amount': 1200, 'type': 'outflow', 'account': 'Capital One 4709', 'customer': 'Office Depot'
            }
        ],
        'total_inflows': 2131700,  # Match generated data
        'total_outflows': 31900,
        'net_flow': 2099800,
        'monthly_data': {i: {'inflows': 177641, 'outflows': 2658, 'net': 174983} for i in range(1, 13)},
        'account_summary': {
            'Revenue 4717': {'inflows': 2131700, 'outflows': 0, 'net': 2131700, 'transaction_count': 373},
            'Bill Pay 4091': {'inflows': 0, 'outflows': 25800, 'net': -25800, 'transaction_count': 8},
            'Capital One 4709': {'inflows': 2500, 'outflows': 6100, 'net': -3600, 'transaction_count': 6}
        },
        'transaction_count': 387,
        'year': 2025
    }

def _get_default_account_summary(account):
    """Default account summary for fallback"""
    base_data = {
        'Revenue 4717': {'total_amount': 2131700, 'count': 373, 'monthly_avg': 177641},
        'Bill Pay 4091': {'total_amount': 25800, 'count': 8, 'monthly_avg': 2150},
        'Capital One 4709': {'total_amount': 6100, 'count': 6, 'monthly_avg': 508}
    }
    
    data = base_data.get(account, {'total_amount': 0, 'count': 0, 'monthly_avg': 0})
    
    return {
        'account': account,
        'year': 2025,
        'total_amount': data['total_amount'],
        'transaction_count': data['count'],
        'monthly_data': {i: {'amount': data['monthly_avg'], 'count': data['count']//12, 'transactions': []} for i in range(1, 13)},
        'variations': {i: 5.2 for i in range(2, 13)},  # Sample 5.2% growth
        'top_entities': [('Sample Entity', data['total_amount'] * 0.3)],
        'recent_transactions': [],
        'average_monthly': data['monthly_avg'],
        'peak_month': 12,
        'lowest_month': 1
    }

def _get_default_aging_analysis():
    """Default aging analysis for fallback"""
    return {
        'current': {'count': 5, 'amount': 45000, 'transactions': []},
        '30_days': {'count': 2, 'amount': 18000, 'transactions': []},
        '60_days': {'count': 1, 'amount': 8500, 'transactions': []},
        '90_plus': {'count': 0, 'amount': 0, 'transactions': []}
    }