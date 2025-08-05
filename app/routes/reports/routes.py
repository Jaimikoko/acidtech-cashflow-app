from flask import render_template, request, jsonify
from flask_login import login_required
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from models.purchase_order import PurchaseOrder
from database import db
import json

from . import reports_bp

@reports_bp.route('/')
@login_required
def index():
    return render_template('reports/index.html')

@reports_bp.route('/cash-flow')
@login_required
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
@login_required
def cash_flow_chart():
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
        
        # Get receivables for the week
        week_receivables = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'receivable',
            Transaction.status == 'paid',
            Transaction.due_date >= current_date,
            Transaction.due_date <= week_end
        ).scalar() or 0
        
        # Get payables for the week
        week_payables = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'payable',
            Transaction.status == 'paid',
            Transaction.due_date >= current_date,
            Transaction.due_date <= week_end
        ).scalar() or 0
        
        receivables.append(float(week_receivables))
        payables.append(float(week_payables))
        net_flow.append(float(week_receivables - week_payables))
        
        current_date += timedelta(days=7)
    
    return jsonify({
        'dates': dates,
        'receivables': receivables,
        'payables': payables,
        'net_flow': net_flow
    })

@reports_bp.route('/aging')
@login_required
def aging():
    # Aging report for receivables and payables
    today = date.today()
    
    # Receivables aging
    receivables_30 = Transaction.query.filter(
        Transaction.type == 'receivable',
        Transaction.status == 'pending',
        Transaction.due_date >= today - timedelta(days=30),
        Transaction.due_date <= today
    ).all()
    
    receivables_60 = Transaction.query.filter(
        Transaction.type == 'receivable',
        Transaction.status == 'pending',
        Transaction.due_date >= today - timedelta(days=60),
        Transaction.due_date < today - timedelta(days=30)
    ).all()
    
    receivables_90 = Transaction.query.filter(
        Transaction.type == 'receivable',
        Transaction.status == 'pending',
        Transaction.due_date < today - timedelta(days=60)
    ).all()
    
    return render_template('reports/aging.html',
                         receivables_30=receivables_30,
                         receivables_60=receivables_60,
                         receivables_90=receivables_90)

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
    # Analyze spending by vendor
    vendor_spending = db.session.query(
        Transaction.vendor_customer,
        db.func.sum(Transaction.amount).label('total_amount'),
        db.func.count(Transaction.id).label('transaction_count')
    ).filter(
        Transaction.type == 'payable'
    ).group_by(Transaction.vendor_customer).order_by(
        db.func.sum(Transaction.amount).desc()
    ).all()
    
    return render_template('reports/vendor_analysis.html', vendor_spending=vendor_spending)