from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime, date, timedelta
from app.models.transaction import Transaction
from app.models.purchase_order import PurchaseOrder
from app.utils.ai_predictor import CashFlowPredictor
from app import db
import json

bp = Blueprint('reports', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('reports/index.html')

@bp.route('/cash-flow')
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

@bp.route('/api/cash-flow-chart')
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
        
        # Get receivables for this week
        week_receivables = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'receivable',
            Transaction.due_date >= current_date,
            Transaction.due_date <= week_end
        ).scalar() or 0
        
        # Get payables for this week
        week_payables = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'payable',
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

@bp.route('/aging')
@login_required
def aging():
    # Aging report for both receivables and payables
    today = date.today()
    
    # Receivables aging
    ar_current = Transaction.query.filter(
        Transaction.type == 'receivable',
        Transaction.status == 'pending',
        Transaction.due_date >= today
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    ar_30_days = Transaction.query.filter(
        Transaction.type == 'receivable',
        Transaction.status == 'pending',
        Transaction.due_date >= today - timedelta(days=30),
        Transaction.due_date < today
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    ar_60_days = Transaction.query.filter(
        Transaction.type == 'receivable',
        Transaction.status == 'pending',
        Transaction.due_date >= today - timedelta(days=60),
        Transaction.due_date < today - timedelta(days=30)
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    ar_90_days = Transaction.query.filter(
        Transaction.type == 'receivable',
        Transaction.status == 'pending',
        Transaction.due_date < today - timedelta(days=60)
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    # Payables aging
    ap_current = Transaction.query.filter(
        Transaction.type == 'payable',
        Transaction.status == 'pending',
        Transaction.due_date >= today
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    ap_30_days = Transaction.query.filter(
        Transaction.type == 'payable',
        Transaction.status == 'pending',
        Transaction.due_date >= today - timedelta(days=30),
        Transaction.due_date < today
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    ap_60_days = Transaction.query.filter(
        Transaction.type == 'payable',
        Transaction.status == 'pending',
        Transaction.due_date >= today - timedelta(days=60),
        Transaction.due_date < today - timedelta(days=30)
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    ap_90_days = Transaction.query.filter(
        Transaction.type == 'payable',
        Transaction.status == 'pending',
        Transaction.due_date < today - timedelta(days=60)
    ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
    
    return render_template('reports/aging.html',
                         ar_current=ar_current,
                         ar_30_days=ar_30_days,
                         ar_60_days=ar_60_days,
                         ar_90_days=ar_90_days,
                         ap_current=ap_current,
                         ap_30_days=ap_30_days,
                         ap_60_days=ap_60_days,
                         ap_90_days=ap_90_days)

@bp.route('/vendor-analysis')
@login_required
def vendor_analysis():
    # Top vendors by transaction volume
    vendor_data = db.session.query(
        Transaction.vendor_customer,
        db.func.sum(Transaction.amount).label('total_amount'),
        db.func.count(Transaction.id).label('transaction_count')
    ).filter(
        Transaction.type == 'payable'
    ).group_by(Transaction.vendor_customer).order_by(
        db.func.sum(Transaction.amount).desc()
    ).limit(10).all()
    
    # Customer analysis
    customer_data = db.session.query(
        Transaction.vendor_customer,
        db.func.sum(Transaction.amount).label('total_amount'),
        db.func.count(Transaction.id).label('transaction_count')
    ).filter(
        Transaction.type == 'receivable'
    ).group_by(Transaction.vendor_customer).order_by(
        db.func.sum(Transaction.amount).desc()
    ).limit(10).all()
    
    return render_template('reports/vendor_analysis.html',
                         vendor_data=vendor_data,
                         customer_data=customer_data)

@bp.route('/ai-insights')
@login_required
def ai_insights():
    predictor = CashFlowPredictor()
    predictions = predictor.get_cash_flow_prediction()
    risk_analysis = predictor.get_risk_analysis()
    insights = predictor.get_vendor_customer_insights()
    
    return render_template('reports/ai_insights.html',
                         predictions=predictions[:30],  # Show next 30 days
                         risk_analysis=risk_analysis,
                         insights=insights)

@bp.route('/api/ai-predictions')
@login_required  
def ai_predictions_api():
    predictor = CashFlowPredictor()
    predictions = predictor.get_cash_flow_prediction()
    
    return jsonify({
        'dates': [p['date'] for p in predictions],
        'inflow': [p['inflow'] for p in predictions],
        'outflow': [p['outflow'] for p in predictions], 
        'net_flow': [p['net_flow'] for p in predictions],
        'confidence': [p['confidence'] for p in predictions]
    })