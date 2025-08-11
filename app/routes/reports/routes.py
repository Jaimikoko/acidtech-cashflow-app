from flask import render_template, request, jsonify, current_app
from flask_login import login_required
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from models.purchase_order import PurchaseOrder
from database import db
import json

from . import reports_bp

@reports_bp.route('/')
def index():
    """Reports index with File Mode support"""
    file_mode = current_app.config.get('USE_FILE_MODE', False)
    return render_template('reports/index.html', file_mode=file_mode)

@reports_bp.route('/cash-flow')
def cash_flow():
    # Get date range from query params
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
    
    return render_template('reports/cash_flow.html', 
                         start_date=start_date, 
                         end_date=end_date)

@reports_bp.route('/api/cash-flow-chart')
def cash_flow_chart():
    """Cash flow chart API with File Mode support"""
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    else:
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
    
    # Generate weekly data points
    dates = []
    receivables = []
    payables = []
    net_flow = []

    current_date = start_date
    while current_date <= end_date:
        week_end = current_date + timedelta(days=6)
        if week_end > end_date:
            week_end = end_date

        dates.append(current_date.strftime('%Y-%m-%d'))

        try:
            from models.views import VArOpen, VApOpen
            from sqlalchemy import func
            week_receivables = db.session.query(func.sum(VArOpen.amount)).filter(
                VArOpen.due_date >= current_date,
                VArOpen.due_date <= week_end
            ).scalar() or 0
            week_payables = db.session.query(func.sum(VApOpen.amount)).filter(
                VApOpen.due_date >= current_date,
                VApOpen.due_date <= week_end
            ).scalar() or 0
        except Exception:
            week_receivables = 0
            week_payables = 0

        receivables.append(float(week_receivables))
        payables.append(float(week_payables))
        net_flow.append(float(week_receivables - week_payables))

        current_date += timedelta(days=7)

    return jsonify({'dates': dates, 'receivables': receivables, 'payables': payables, 'net_flow': net_flow})

@reports_bp.route('/aging')
@login_required
def aging():
    report_type = request.args.get('type', 'receivable')
    today = date.today()
    try:
        Model = VArOpen if report_type == 'receivable' else VApOpen
    except Exception:
        Model = None

    aging_summary = {
        'current': 0, 'current_count': 0,
        'days_1_30': 0, 'days_1_30_count': 0,
        'days_31_60': 0, 'days_31_60_count': 0,
        'days_61_90': 0, 'days_61_90_count': 0,
        'days_90_plus': 0, 'days_90_plus_count': 0,
    }
    aging_transactions = []

    if Model is not None:
        try:
            records = Model.query.all()
            for t in records:
                days = (today - (t.due_date or today)).days
                amt = float(t.amount or 0)
                if days <= 0:
                    aging_summary['current'] += amt
                    aging_summary['current_count'] += 1
                elif days <= 30:
                    aging_summary['days_1_30'] += amt
                    aging_summary['days_1_30_count'] += 1
                elif days <= 60:
                    aging_summary['days_31_60'] += amt
                    aging_summary['days_31_60_count'] += 1
                elif days <= 90:
                    aging_summary['days_61_90'] += amt
                    aging_summary['days_61_90_count'] += 1
                else:
                    aging_summary['days_90_plus'] += amt
                    aging_summary['days_90_plus_count'] += 1
            aging_transactions = records
        except Exception:
            pass

    return render_template('reports/aging.html', aging_summary=aging_summary, aging_transactions=aging_transactions, today=today)

@reports_bp.route('/ai-insights')
@login_required
def ai_insights():
    try:
        # Get recent transactions for AI analysis
        recent_transactions = Transaction.query.order_by(
            Transaction.created_at.desc()
        ).limit(100).all()
        
        # Simple analytics (placeholder for AI)
        total_receivables = sum(t.amount for t in recent_transactions if t.type == 'receivable')
        total_payables = sum(t.amount for t in recent_transactions if t.type == 'payable')
        cash_flow_trend = total_receivables - total_payables
        
        insights = {
            'cash_flow_health': 'Positive' if cash_flow_trend > 0 else 'Needs Attention',
            'trend': cash_flow_trend,
            'recommendations': [
                'Monitor overdue receivables closely',
                'Consider payment terms optimization',
                'Review vendor payment schedules'
            ]
        }
        
        return render_template('reports/ai_insights.html', insights=insights)
    except Exception as e:
        return render_template('reports/ai_insights.html', 
                             error=f"AI insights temporarily unavailable: {str(e)}")

@reports_bp.route('/vendor-analysis')
@login_required
def vendor_analysis():
    try:
        from models.views import VApOpen
        from sqlalchemy import func
        vendor_spending = db.session.query(
            VApOpen.vendor_customer,
            func.sum(VApOpen.amount).label('total_amount'),
            func.count(VApOpen.id).label('transaction_count')
        ).group_by(VApOpen.vendor_customer).order_by(func.sum(VApOpen.amount).desc()).all()
    except Exception:
        vendor_spending = []

    return render_template('reports/vendor_analysis.html', vendor_spending=vendor_spending)