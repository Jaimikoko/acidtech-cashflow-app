from flask import (
    render_template,
    render_template_string,
    request,
    jsonify,
    send_from_directory,
    flash,
    redirect,
    url_for,
)
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func
from models.transaction import Transaction
from models.bank_transaction import BankTransaction
from models.purchase_order import PurchaseOrder
from database import db
import json
import os
import time
import logging

from . import main_bp
from app.forms import LoginForm

# Get logger for this module
logger = logging.getLogger(__name__)


def get_financial_summary_kpis():
    """Calculate financial summary KPIs from bank transactions."""
    try:
        current_year = date.today().year

        revenue = db.session.query(func.sum(BankTransaction.amount)).filter(
            BankTransaction.amount > 0,
            func.extract('year', BankTransaction.transaction_date) == current_year,
        ).scalar() or 0

        expenses = db.session.query(func.sum(func.abs(BankTransaction.amount))).filter(
            BankTransaction.amount < 0,
            func.extract('year', BankTransaction.transaction_date) == current_year,
        ).scalar() or 0

        net_cash_flow = revenue - expenses

        transactions_processed = db.session.query(func.count(BankTransaction.id)).scalar() or 0

        avg_transaction_value = (
            db.session.query(func.avg(func.abs(BankTransaction.amount))).scalar() or 0
        )

        # Revenue growth vs same period last year
        today = date.today()
        start_current_year = date(current_year, 1, 1)
        days_elapsed = (today - start_current_year).days + 1
        start_prev_year = date(current_year - 1, 1, 1)
        end_prev_period = start_prev_year + timedelta(days=days_elapsed - 1)

        revenue_prev = db.session.query(func.sum(BankTransaction.amount)).filter(
            BankTransaction.amount > 0,
            BankTransaction.transaction_date >= start_prev_year,
            BankTransaction.transaction_date <= end_prev_period,
        ).scalar() or 0

        revenue_growth = (
            ((revenue - revenue_prev) / revenue_prev) * 100 if revenue_prev else 0
        )

        profit_margin = (net_cash_flow / revenue * 100) if revenue else 0

        return {
            "total_revenue_ytd": revenue,
            "total_expenses_ytd": expenses,
            "net_cash_flow": net_cash_flow,
            "transactions_processed": transactions_processed,
            "avg_transaction_value": avg_transaction_value,
            "revenue_growth": revenue_growth,
            "profit_margin": profit_margin,
            "processing_rate": 100 if transactions_processed else 0,
            "ytd_months": today.month,
        }
    except Exception as e:
        logger.error(f"Error calculating financial KPIs: {e}")
        return {
            "total_revenue_ytd": 0,
            "total_expenses_ytd": 0,
            "net_cash_flow": 0,
            "transactions_processed": 0,
            "avg_transaction_value": 0,
            "revenue_growth": 0,
            "profit_margin": 0,
        }

@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main_bp.root_path, '..', '..', 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.route('/')
def index():
    """Main landing page - redirect based on auth status"""
    from flask_login import current_user
    
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    # If not authenticated, show login page
    return render_template('auth/login_main.html', form=form)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Bootstrap 5 Grid Dashboard with sidebar navigation"""
    return render_template('dashboard/main.html')

@main_bp.route('/financial-summary')
@login_required
def financial_summary():
    """Financial Summary page - executive overview"""
    kpis = get_financial_summary_kpis()
    return render_template('dashboard/financial_summary.html', kpis=kpis)

@main_bp.route('/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html')

@main_bp.route('/inventory')
@login_required
def inventory():
    """Inventory page"""
    inventory_data = {
        'total_items': 0,
        'low_stock': 0,
        'total_value': 0,
        'out_of_stock': 0,
        'items': [],
        'categories': [],
        'alerts': []
    }
    return render_template('inventory.html', inventory=inventory_data)

@main_bp.route('/dashboard/api/summary')
@login_required
def dashboard_summary():
    """API endpoint for dashboard summary data using VCashflowDaily view"""
    try:
        from sqlalchemy import func
        from models.views import VCashflowDaily
        from datetime import datetime, timedelta

        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow().date() - timedelta(days=days)

        totals = db.session.query(
            func.sum(VCashflowDaily.inflows).label('inflows'),
            func.sum(VCashflowDaily.outflows).label('outflows'),
            func.sum(VCashflowDaily.transaction_count).label('txns')
        ).filter(VCashflowDaily.txn_date >= start_date).first()

        inflows = float(totals.inflows or 0)
        outflows = float(totals.outflows or 0)
        txns = int(totals.txns or 0)
        net_flow = inflows - outflows

        return jsonify({
            'success': True,
            'total_inflows': inflows,
            'total_outflows': outflows,
            'net_flow': net_flow,
            'transaction_count': txns,
            'last_updated': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in dashboard_summary: {e}")
        return jsonify({
            'success': False,
            'total_inflows': 0,
            'total_outflows': 0,
            'net_flow': 0,
            'transaction_count': 0,
            'error': str(e)
        }), 500

@main_bp.route('/dashboard/legacy')
@login_required
def dashboard_legacy():
    """Legacy dashboard using database data"""

    # Database queries
    try:
        # Calculate totals from database
        total_receivables = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'receivable',
            Transaction.status == 'pending'
        ).scalar() or 0
        
        total_payables = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'payable',
            Transaction.status == 'pending'
        ).scalar() or 0
        
        # Get recent transactions
        recent_transactions_query = Transaction.query.order_by(
            Transaction.created_at.desc()
        ).limit(5).all()
        
        recent_transactions = [{
            'id': t.id,
            'vendor_customer': t.vendor_customer,
            'amount': t.amount,
            'type': t.type,
            'due_date': t.due_date,
            'invoice_number': t.invoice_number,
            'description': t.description
        } for t in recent_transactions_query]
        
        # Calculate overdue items
        overdue_receivables = Transaction.query.filter(
            Transaction.type == 'receivable',
            Transaction.status == 'pending',
            Transaction.due_date < date.today()
        ).count()
        
        overdue_payables = Transaction.query.filter(
            Transaction.type == 'payable',
            Transaction.status == 'pending', 
            Transaction.due_date < date.today()
        ).count()
        
    except Exception as e:
        # Fallback to hardcoded data if database fails
        total_receivables = 45750.00
        total_payables = 13200.75
        overdue_receivables = 2
        overdue_payables = 1
        recent_transactions = [
            {
                'id': 1, 'vendor_customer': 'Acme Corporation', 'amount': 15000.00,
                'type': 'receivable', 'due_date': date.today() + timedelta(days=30),
                'invoice_number': 'INV-2024-001', 'description': 'Consulting Services Q4'
            },
            {
                'id': 2, 'vendor_customer': 'Office Supplies Co', 'amount': 2400.00,
                'type': 'payable', 'due_date': date.today() + timedelta(days=15),
                'invoice_number': 'BILL-2024-001', 'description': 'Monthly Office Supplies'
            }
        ]
    
    cash_available = total_receivables - total_payables
    
    return render_template('dashboard.html',
                         total_receivables=total_receivables,
                         total_payables=total_payables,
                         cash_available=cash_available,
                         recent_transactions=recent_transactions,
                         overdue_receivables=overdue_receivables,
                         overdue_payables=overdue_payables)

@main_bp.route('/api/cash-flow-data')
def cash_flow_data():
    # Generate cash flow data for charts
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    # Sample data for demonstration
    dates = []
    receivables = []
    payables = []
    
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        
        # Sample receivables data
        receivables_amount = Transaction.query.filter(
            Transaction.type == 'receivable',
            Transaction.due_date == current_date
        ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        
        # Sample payables data
        payables_amount = Transaction.query.filter(
            Transaction.type == 'payable',
            Transaction.due_date == current_date
        ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        
        receivables.append(float(receivables_amount))
        payables.append(float(payables_amount))
        
        current_date += timedelta(days=1)
    
    return jsonify({
        'dates': dates,
        'receivables': receivables,
        'payables': payables
    })

@main_bp.route('/test-layout')
def test_layout():
    """Test route with full masterlayout and simulated data"""
    try:
        from flask import request
        
        # Datos de prueba completos para el dashboard
        total_receivables = 45750.00
        total_payables = 13200.75
        cash_available = 32549.25
        recent_transactions = [
            {
                "id": 1,
                "description": "Payment from Acme Corp",
                "amount": 1500.00,
                "type": "receivable",
                "vendor_customer": "Acme Corporation",
                "created_at": datetime.now() - timedelta(days=1)
            },
            {
                "id": 2,
                "description": "Office Supplies Payment", 
                "amount": 800.50,
                "type": "payable",
                "vendor_customer": "Office Depot",
                "created_at": datetime.now() - timedelta(days=2)
            },
            {
                "id": 3,
                "description": "Consulting Invoice",
                "amount": 2500.00,
                "type": "receivable",
                "vendor_customer": "Tech Solutions Inc",
                "created_at": datetime.now() - timedelta(days=3)
            }
        ]
        overdue_receivables = 2
        overdue_payables = 1
        
        return render_template('test_dashboard.html',
                             total_receivables=total_receivables,
                             total_payables=total_payables,
                             cash_available=cash_available,
                             recent_transactions=recent_transactions,
                             overdue_receivables=overdue_receivables,
                             overdue_payables=overdue_payables)
        
    except Exception as e:
        # Final fallback si algo falla
        return f"<h1>Error 500: {str(e)}</h1><p>Timestamp: {datetime.now()}</p>"

@main_bp.route('/init-sample-data')
def init_sample_data():
    """Initialize database with sample data - for Azure deployment"""
    try:
        from models.user import User
        
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        # Create test user
        test_user = User(
            username='demo_user',
            email='demo@acidtech.com',
            first_name='Demo',
            last_name='User'
        )
        test_user.set_password('demo123')
        db.session.add(test_user)
        db.session.commit()
        
        user = User.query.first()
        
        # Sample receivables
        receivables_data = [
            {'vendor_customer': 'Acme Corporation', 'amount': 15000.00, 'due_date': date.today() + timedelta(days=30), 'description': 'Consulting Services', 'invoice_number': 'INV-001', 'status': 'pending'},
            {'vendor_customer': 'Tech Solutions Inc', 'amount': 8500.00, 'due_date': date.today() + timedelta(days=15), 'description': 'Software Development', 'invoice_number': 'INV-002', 'status': 'pending'},
            {'vendor_customer': 'Global Systems Ltd', 'amount': 12250.00, 'due_date': date.today() + timedelta(days=45), 'description': 'System Integration', 'invoice_number': 'INV-003', 'status': 'pending'},
        ]
        
        for data in receivables_data:
            transaction = Transaction(
                type='receivable',
                vendor_customer=data['vendor_customer'],
                amount=data['amount'],
                due_date=data['due_date'],
                description=data['description'],
                invoice_number=data['invoice_number'],
                status=data['status'],
                created_by=user.id
            )
            db.session.add(transaction)
        
        # Sample payables
        payables_data = [
            {'vendor_customer': 'Office Supplies Co', 'amount': 2400.00, 'due_date': date.today() + timedelta(days=20), 'description': 'Office Supplies', 'invoice_number': 'BILL-001', 'status': 'pending'},
            {'vendor_customer': 'IT Equipment Ltd', 'amount': 5600.00, 'due_date': date.today() + timedelta(days=10), 'description': 'Hardware Purchase', 'invoice_number': 'BILL-002', 'status': 'pending'},
        ]
        
        for data in payables_data:
            transaction = Transaction(
                type='payable',
                vendor_customer=data['vendor_customer'],
                amount=data['amount'],
                due_date=data['due_date'],
                description=data['description'],
                invoice_number=data['invoice_number'],
                status=data['status'],
                created_by=user.id
            )
            db.session.add(transaction)
        
        db.session.commit()
        
        # Calculate totals
        total_receivables = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='receivable', status='pending').scalar() or 0
        total_payables = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='payable', status='pending').scalar() or 0
        total_transactions = Transaction.query.count()
        
        return f"""
        <h1>✅ Sample Data Initialized Successfully!</h1>
        <p><strong>Database populated with:</strong></p>
        <ul>
            <li>Total transactions: {total_transactions}</li>
            <li>Accounts receivable: ${total_receivables:,.2f}</li>
            <li>Accounts payable: ${total_payables:,.2f}</li>
            <li>Net cash flow: ${total_receivables - total_payables:,.2f}</li>
            <li>Demo user: demo_user / demo123</li>
        </ul>
        <p><a href="/dashboard">Go to Dashboard</a> | <a href="/">Home</a></p>
        """
        
    except Exception as e:
        db.session.rollback()
        return f"<h1>❌ Error initializing data:</h1><p>{str(e)}</p>"

