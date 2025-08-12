from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from models.bank_transaction import BankTransaction
from database import db
from sqlalchemy import func
import json

from . import cash_flow_bp

# Import classification service
from services.transaction_classifier import CashFlowClassifier

# Account mappings for the four main accounts
ACCOUNT_MAPPINGS = {
    'Revenue 4717': {'name': 'Revenue 4717', 'type': 'inflow', 'color': '#10b981'},
    'Bill Pay 5285': {'name': 'Bill Pay 5285', 'type': 'outflow', 'color': '#ef4444'},
    'Payroll 4079': {'name': 'Payroll 4079', 'type': 'outflow', 'color': '#f59e0b'},
    'Capital One': {'name': 'Capital One', 'type': 'mixed', 'color': '#3b82f6'}
}

@cash_flow_bp.route('/')
@login_required
def index():
    """Cash Flow main page with enhanced account analysis"""
    
    # Get filter parameters
    account_filter = request.args.get('account', 'all')
    year = int(request.args.get('year', 2025))
    month = request.args.get('month')
    month = int(month) if month else None
    
    # Get account summaries for all accounts from database
    account_summaries = {}
    for account_key in ACCOUNT_MAPPINGS.keys():
        account_summaries[account_key] = _get_account_summary_from_database(account_key, year)

    # Get overall cash flow data from database
    cash_flow_data = _get_comprehensive_cash_flow_data_from_database(account_filter, year, month)

    # Aging analysis currently not implemented for DB mode
    aging_analysis = None

    return render_template('cash_flow/index.html',
                         cash_flow_data=cash_flow_data,
                         account_mappings=ACCOUNT_MAPPINGS,
                         account_summaries=account_summaries,
                         aging_analysis=aging_analysis,
                         account_filter=account_filter,
                         year=year,
                         month=month)

@cash_flow_bp.route('/account/<path:account_name>')
@login_required
def account_detail(account_name):
    """Detailed view for a specific account with dynamic filters"""
    
    # URL decode account name to handle spaces like "Revenue 4717"
    account_name = account_name.replace('%20', ' ').replace('+', ' ')
    
    if account_name not in ACCOUNT_MAPPINGS:
        return redirect(url_for('cash_flow.index'))
    
    # Get filter parameters
    year = int(request.args.get('year', 2025))
    month = request.args.get('month')
    period = request.args.get('period')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    month = int(month) if month and month.isdigit() else None
    
    # Build filter parameters for data retrieval
    filter_params = {
        'account': account_name,
        'year': year,
        'month': month,
        'period': period,
        'start_date': start_date,
        'end_date': end_date
    }
    
    # Database mode - get real data from BankTransaction
    account_data = _get_account_summary_from_database(account_name, year)
    transactions = _get_transactions_from_database(account_name, filter_params)
    
    return render_template('cash_flow/account_detail.html',
                         account_data=account_data,
                         account_info=ACCOUNT_MAPPINGS[account_name],
                         transactions=transactions,
                         year=year,
                         month=month,
                         period=period,
                         filter_params=filter_params)

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
    
    chart_data = _generate_chart_data_from_database(account_filter, date_from, date_to, period)
    
    return jsonify(chart_data)

@cash_flow_bp.route('/api/summary')
def summary():
    """API endpoint for cash flow summary data"""
    
    account_filter = request.args.get('account', 'all')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    summary_data = _get_summary_from_database(account_filter, date_from, date_to)
    
    return jsonify(summary_data)

@cash_flow_bp.route('/api/monthly-chart')
def monthly_chart_data():
    """API endpoint for monthly cash flow chart with bars and lines"""
    
    account_filter = request.args.get('account', 'all')
    year = int(request.args.get('year', 2025))

    cash_flow_data = _get_comprehensive_cash_flow_data_from_database(account_filter, year)
    monthly_data = cash_flow_data.get('monthly_data', {i: {'inflows': 0, 'outflows': 0, 'net': 0} for i in range(1, 13)})
    
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

def _generate_chart_data_from_database(account_filter, date_from, date_to, period):
    """Generate chart data from database"""

    # Parse dates
    start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
    end_date = datetime.strptime(date_to, '%Y-%m-%d').date()

    query = db.session.query(BankTransaction).filter(
        BankTransaction.transaction_date >= start_date,
        BankTransaction.transaction_date <= end_date
    )

    if account_filter != 'all' and account_filter in ACCOUNT_MAPPINGS:
        query = query.filter(BankTransaction.account_name == account_filter)

    transactions = query.all()

    # Group transactions by period
    groups = {}
    for t in transactions:
        if period == 'monthly':
            key = t.transaction_date.replace(day=1)
            label = key.strftime('%Y-%m')
        else:  # weekly
            key = t.transaction_date - timedelta(days=t.transaction_date.weekday())
            label = key.strftime('%Y-%m-%d')

        if label not in groups:
            groups[label] = {'inflows': 0, 'outflows': 0}

        amt = float(t.amount)
        if amt >= 0:
            groups[label]['inflows'] += amt
        else:
            groups[label]['outflows'] += abs(amt)

    labels = sorted(groups.keys())
    inflows = [groups[l]['inflows'] for l in labels]
    outflows = [groups[l]['outflows'] for l in labels]

    return {
        'labels': labels,
        'datasets': [
            {
                'label': 'Inflows',
                'data': inflows,
                'backgroundColor': 'rgba(16, 185, 129, 0.8)',
                'borderColor': 'rgb(16, 185, 129)',
                'borderWidth': 2
            },
            {
                'label': 'Outflows',
                'data': outflows,
                'backgroundColor': 'rgba(239, 68, 68, 0.8)',
                'borderColor': 'rgb(239, 68, 68)',
                'borderWidth': 2
            }
        ]
    }

def _get_summary_from_database(account_filter, date_from, date_to):
    """Get summary data from database"""

    query = db.session.query(BankTransaction)

    if account_filter != 'all' and account_filter in ACCOUNT_MAPPINGS:
        query = query.filter(BankTransaction.account_name == account_filter)

    if date_from:
        start = datetime.strptime(date_from, '%Y-%m-%d').date()
        query = query.filter(BankTransaction.transaction_date >= start)

    if date_to:
        end = datetime.strptime(date_to, '%Y-%m-%d').date()
        query = query.filter(BankTransaction.transaction_date <= end)

    transactions = query.all()

    total_inflows = sum(float(t.amount) for t in transactions if float(t.amount) > 0)
    total_outflows = sum(abs(float(t.amount)) for t in transactions if float(t.amount) < 0)
    net_flow = total_inflows - total_outflows

    account_summary = {}
    for account in ACCOUNT_MAPPINGS.keys():
        acc_trans = [t for t in transactions if t.account_name == account]
        inflows = sum(float(t.amount) for t in acc_trans if float(t.amount) > 0)
        outflows = sum(abs(float(t.amount)) for t in acc_trans if float(t.amount) < 0)
        account_summary[account] = {
            'inflows': inflows,
            'outflows': outflows,
            'net': inflows - outflows,
            'transaction_count': len(acc_trans)
        }

    return {
        'total_inflows': total_inflows,
        'total_outflows': total_outflows,
        'net_flow': net_flow,
        'projected_balance': net_flow,
        'account_summary': account_summary
    }

def _get_account_summary_from_database(account_name, year):
    """Get account summary from database using BankTransaction model"""
    
    # Query for the specific account and year
    query = db.session.query(BankTransaction).filter(
        BankTransaction.account_name == account_name,
        func.extract('year', BankTransaction.transaction_date) == year
    )
    
    transactions = query.all()

    if not transactions:
        return {
            'account': account_name,
            'year': year,
            'total_amount': 0,
            'transaction_count': 0,
            'monthly_data': {m: {'amount': 0, 'count': 0, 'transactions': []} for m in range(1, 13)},
            'average_monthly': 0,
            'top_entities': [],
            'recent_transactions': [],
            'peak_month': None,
            'lowest_month': None
        }
    
    # Calculate totals
    total_amount = sum(float(t.amount) for t in transactions)
    transaction_count = len(transactions)
    
    # Filter only positive amounts for revenue accounts
    if account_name == 'Revenue 4717':
        revenue_transactions = [t for t in transactions if float(t.amount) > 0]
        total_amount = sum(float(t.amount) for t in revenue_transactions)
        transaction_count = len(revenue_transactions)
    
    # Monthly breakdown
    monthly_data = {}
    for month in range(1, 13):
        month_transactions = [t for t in transactions if t.transaction_date.month == month]
        if account_name == 'Revenue 4717':
            month_transactions = [t for t in month_transactions if float(t.amount) > 0]
        
        monthly_amount = sum(float(t.amount) for t in month_transactions)
        monthly_data[month] = {
            'amount': monthly_amount,
            'count': len(month_transactions),
            'transactions': month_transactions[:5]  # Show first 5
        }
    
    # Calculate average monthly
    months_with_data = [m for m in monthly_data.values() if m['amount'] > 0]
    average_monthly = total_amount / max(1, len(months_with_data))
    
    # Top entities (group by merchant/description keywords)
    entity_totals = {}
    for t in transactions:
        if float(t.amount) > 0:  # Only positive amounts for revenue
            desc = t.description[:30].strip()
            if desc in entity_totals:
                entity_totals[desc] += float(t.amount)
            else:
                entity_totals[desc] = float(t.amount)
    
    # Get top 5 entities
    top_entities = sorted(entity_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Recent transactions (last 10)
    recent_transactions = []
    sorted_transactions = sorted(transactions, key=lambda t: t.transaction_date, reverse=True)[:10]
    
    for t in sorted_transactions:
        if account_name == 'Revenue 4717' and float(t.amount) <= 0:
            continue  # Skip negative amounts for revenue display
            
        recent_transactions.append({
            'date': t.transaction_date,
            'description': t.description,
            'amount': float(t.amount),
            'type': 'inflow' if float(t.amount) > 0 else 'outflow',
            'customer': t.description.split(' ')[0] if t.description else 'Unknown'
        })
    
    return {
        'account': account_name,
        'year': year,
        'total_amount': total_amount,
        'transaction_count': transaction_count,
        'monthly_data': monthly_data,
        'average_monthly': average_monthly,
        'top_entities': top_entities,
        'recent_transactions': recent_transactions[:10],
        'peak_month': max(monthly_data.keys(), key=lambda k: monthly_data[k]['amount']),
        'lowest_month': min(monthly_data.keys(), key=lambda k: monthly_data[k]['amount'])
    }

def _get_comprehensive_cash_flow_data_from_database(account_filter, year, month=None):
    """Get comprehensive cash flow data from database"""

    query = db.session.query(BankTransaction).filter(
        func.extract('year', BankTransaction.transaction_date) == year
    )

    if account_filter != 'all' and account_filter in ACCOUNT_MAPPINGS:
        query = query.filter(BankTransaction.account_name == account_filter)

    if month:
        query = query.filter(func.extract('month', BankTransaction.transaction_date) == month)

    transactions = query.all()

    monthly_data = {m: {'inflows': 0, 'outflows': 0, 'net': 0, 'transactions': 0} for m in range(1, 13)}
    account_summary = {a: {'inflows': 0, 'outflows': 0, 'net': 0, 'transaction_count': 0} for a in ACCOUNT_MAPPINGS.keys()}

    for t in transactions:
        amt = float(t.amount)
        m = t.transaction_date.month

        if amt >= 0:
            monthly_data[m]['inflows'] += amt
            account_summary[t.account_name]['inflows'] += amt
        else:
            monthly_data[m]['outflows'] += abs(amt)
            account_summary[t.account_name]['outflows'] += abs(amt)

        monthly_data[m]['transactions'] += 1

    for m in monthly_data:
        monthly_data[m]['net'] = monthly_data[m]['inflows'] - monthly_data[m]['outflows']

    for account in account_summary:
        summary = account_summary[account]
        summary['net'] = summary['inflows'] - summary['outflows']
        summary['transaction_count'] = sum(1 for t in transactions if t.account_name == account)

    total_inflow = sum(data['inflows'] for data in monthly_data.values())
    total_outflow = sum(data['outflows'] for data in monthly_data.values())
    net_cash_flow = total_inflow - total_outflow

    recent_transactions = sorted(transactions, key=lambda t: t.transaction_date, reverse=True)[:10]
    recent_list = []
    for t in recent_transactions:
        recent_list.append({
            'id': t.id,
            'date': t.transaction_date,
            'description': t.description,
            'amount': float(t.amount),
            'type': 'inflow' if float(t.amount) > 0 else 'outflow',
            'account': t.account_name,
            'customer': t.description.split(' ')[0] if t.description else 'Unknown'
        })

    return {
        'transactions': recent_list,
        'total_inflows': total_inflow,
        'total_outflows': total_outflow,
        'net_flow': net_cash_flow,
        'monthly_data': monthly_data,
        'account_summary': account_summary,
        'transaction_count': len(transactions),
        'year': year,
        'month': month
    }

def _get_transactions_from_database(account_name, filter_params):
    """Get filtered transactions from database"""
    
    query = db.session.query(BankTransaction).filter(
        BankTransaction.account_name == account_name
    )
    
    # Apply filters
    if filter_params.get('year'):
        query = query.filter(func.extract('year', BankTransaction.transaction_date) == filter_params['year'])
    
    if filter_params.get('month'):
        query = query.filter(func.extract('month', BankTransaction.transaction_date) == filter_params['month'])
    
    if filter_params.get('start_date'):
        try:
            start_date = datetime.strptime(filter_params['start_date'], '%Y-%m-%d').date()
            query = query.filter(BankTransaction.transaction_date >= start_date)
        except:
            pass
    
    if filter_params.get('end_date'):
        try:
            end_date = datetime.strptime(filter_params['end_date'], '%Y-%m-%d').date()
            query = query.filter(BankTransaction.transaction_date <= end_date)
        except:
            pass
    
    # Order by date descending
    query = query.order_by(BankTransaction.transaction_date.desc())
    
    transactions = query.all()
    
    # Convert to format expected by template
    result = []
    for t in transactions:
        # For Revenue 4717, only show positive amounts
        if account_name == 'Revenue 4717' and float(t.amount) <= 0:
            continue
            
        result.append({
            'id': t.id,
            'date': t.transaction_date,
            'description': t.description,
            'amount': float(t.amount),
            'type': 'inflow' if float(t.amount) > 0 else 'outflow',
            'status': 'completed',
            'customer': t.description.split(' ')[0] if t.description else 'Unknown',
            'account': t.account_name
        })
    
    return result

# ===================================================================
# TRANSACTION CLASSIFICATION ENDPOINTS
# ===================================================================

@cash_flow_bp.route('/api/classification/classify-all', methods=['POST'])
def classify_all_transactions():
    """
    API endpoint to classify all transactions using intelligent rules
    
    POST /cash-flow/api/classification/classify-all
    
    Request JSON:
    {
        "limit": 100,                    # Optional: max transactions to process
        "force_reclassify": false,       # Optional: reclassify already classified
        "account_filter": "Revenue 4717" # Optional: specific account only
    }
    
    Response:
    {
        "success": true,
        "stats": {
            "total_processed": 594,
            "successful_classifications": 590,
            "success_rate": 99.3,
            "by_category": {...},
            "processing_time": 12.5
        }
    }
    """
    
    try:
        # Get request parameters
        data = request.get_json() or {}
        limit = data.get('limit')
        force_reclassify = data.get('force_reclassify', False)
        account_filter = data.get('account_filter')
        
        # Validate limit
        if limit is not None:
            try:
                limit = int(limit)
                if limit <= 0 or limit > 10000:
                    return jsonify({
                        'success': False,
                        'error': 'Limit must be between 1 and 10000'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Invalid limit value'
                }), 400
        
        # Initialize classifier
        classifier = CashFlowClassifier()
        
        # If account filter is specified, temporarily modify the query logic
        if account_filter:
            # This would require extending the classifier to support account filtering
            # For now, we'll process all and filter in the response
            pass
        
        # Execute classification
        stats = classifier.classify_all_transactions(
            limit=limit,
            force_reclassify=force_reclassify
        )
        
        # Add some additional useful information
        total_transactions = BankTransaction.query.count()
        classified_transactions = BankTransaction.query.filter(
            BankTransaction.is_classified == True
        ).count()
        
        stats['database_totals'] = {
            'total_transactions_in_db': total_transactions,
            'total_classified': classified_transactions,
            'total_unclassified': total_transactions - classified_transactions,
            'overall_classification_percentage': (classified_transactions / total_transactions * 100) if total_transactions > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {stats["total_processed"]} transactions',
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Classification failed: {str(e)}'
        }), 500

@cash_flow_bp.route('/api/classification/status', methods=['GET'])
def get_classification_status():
    """
    Get current classification status across all accounts
    
    GET /cash-flow/api/classification/status
    
    Response:
    {
        "success": true,
        "status": {
            "total_transactions": 594,
            "classified": 450,
            "unclassified": 144,
            "by_account": {...},
            "by_category": {...}
        }
    }
    """
    
    try:
        # Get classification summary using our model method
        summary = BankTransaction.get_classification_summary()
        
        # Get breakdown by account
        account_breakdown = {}
        for account in ACCOUNT_MAPPINGS.keys():
            total = BankTransaction.query.filter_by(account_name=account).count()
            classified = BankTransaction.query.filter(
                BankTransaction.account_name == account,
                BankTransaction.is_classified == True
            ).count()
            
            account_breakdown[account] = {
                'total': total,
                'classified': classified,
                'unclassified': total - classified,
                'percentage': (classified / total * 100) if total > 0 else 0
            }
        
        # Get recent unclassified transactions for preview
        unclassified_preview = []
        unclassified_transactions = BankTransaction.get_unclassified_transactions(limit=5)
        
        for t in unclassified_transactions:
            unclassified_preview.append({
                'id': t.id,
                'account': t.account_name,
                'description': t.description[:60] + '...' if len(t.description) > 60 else t.description,
                'amount': float(t.amount),
                'date': t.transaction_date.isoformat(),
                'status': t.classification_status
            })
        
        return jsonify({
            'success': True,
            'status': {
                **summary,
                'account_breakdown': account_breakdown,
                'unclassified_preview': unclassified_preview
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get classification status: {str(e)}'
        }), 500

@cash_flow_bp.route('/api/classification/classify-single/<int:transaction_id>', methods=['POST'])
def classify_single_transaction(transaction_id):
    """
    Classify a single transaction by ID
    
    POST /cash-flow/api/classification/classify-single/123
    
    Response:
    {
        "success": true,
        "transaction": {
            "id": 123,
            "classification": {...},
            "confidence": 0.95
        }
    }
    """
    
    try:
        # Get transaction
        transaction = BankTransaction.query.get_or_404(transaction_id)
        
        # Initialize classifier and classify
        classifier = CashFlowClassifier()
        result = classifier.classify_transaction(transaction)
        
        # Apply updates to transaction
        if result['classification_updates']:
            for field, value in result['classification_updates'].items():
                if hasattr(transaction, field):
                    setattr(transaction, field, value)
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction': {
                'id': transaction.id,
                'account': transaction.account_name,
                'description': transaction.description,
                'amount': float(transaction.amount),
                'classification_result': result,
                'new_status': transaction.classification_status
            }
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Failed to classify transaction: {str(e)}'
        }), 500

@cash_flow_bp.route('/classification-dashboard')
@login_required
def classification_dashboard():
    """
    Web UI for transaction classification management
    
    Shows:
    - Classification statistics
    - Unclassified transactions
    - Bulk classification tools
    - Review queue
    """
    
    # Get classification status
    summary = BankTransaction.get_classification_summary()
    
    # Get unclassified transactions for the table
    unclassified_transactions = BankTransaction.get_unclassified_transactions(limit=50)
    
    # Format for template
    unclassified_list = []
    for t in unclassified_transactions:
        unclassified_list.append({
            'id': t.id,
            'account': t.account_name,
            'date': t.transaction_date,
            'description': t.description,
            'amount': t.amount,
            'status': t.classification_status,
            'needs_review': t.needs_review
        })
    
    # Get account breakdown
    account_stats = {}
    for account in ACCOUNT_MAPPINGS.keys():
        total = BankTransaction.query.filter_by(account_name=account).count()
        classified = BankTransaction.query.filter(
            BankTransaction.account_name == account,
            BankTransaction.is_classified == True
        ).count()
        
        account_stats[account] = {
            'total': total,
            'classified': classified,
            'unclassified': total - classified,
            'percentage': round((classified / total * 100), 1) if total > 0 else 0
        }
    
    return render_template('cash_flow/classification_dashboard.html',
                         summary=summary,
                         unclassified_transactions=unclassified_list,
                         account_stats=account_stats,
                         account_mappings=ACCOUNT_MAPPINGS)