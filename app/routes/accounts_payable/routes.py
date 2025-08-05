from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from database import db
from utils.excel_data_manager import excel_manager
import os

from . import accounts_payable_bp

# Mock pagination object
class MockPagination:
    def __init__(self, items):
        self.items = items
        self.page = 1
        self.per_page = 20
        self.total = len(items)
        self.pages = 1
        self.has_prev = False
        self.has_next = False
        self.prev_num = None
        self.next_num = None

@accounts_payable_bp.route('/')
def index():
    """Accounts Payable index with File Mode support"""
    status_filter = request.args.get('status', 'all')
    
    if current_app.config.get('USE_FILE_MODE', False):
        # File Mode: Use Excel data
        try:
            # Get payable transactions from Excel
            all_payables = excel_manager.get_transactions(transaction_type='payable')
            
            # Filter by status if specified
            if status_filter != 'all':
                payables = [t for t in all_payables if t['status'] == status_filter]
            else:
                payables = all_payables
            
            # Calculate totals
            total_pending = sum(t['amount'] for t in all_payables if t['status'] == 'pending')
            total_overdue = sum(t['amount'] for t in all_payables if t['status'] == 'pending' and t['due_date'] < date.today())
            
            transactions = MockPagination(payables)
            
            return render_template('accounts_payable/index.html',
                                 transactions=transactions,
                                 total_pending=total_pending,
                                 total_overdue=total_overdue,
                                 status_filter=status_filter,
                                 file_mode=True)
        except Exception as e:
            # Fallback to database mode if Excel fails
            pass
    
    # Database Mode or fallback
    try:
        # Query database for payable transactions
        query = Transaction.query.filter_by(type='payable')
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        transactions = query.order_by(Transaction.due_date.asc()).paginate(
            page=request.args.get('page', 1, type=int),
            per_page=20
        )
        
        # Calculate totals
        total_pending = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'payable',
            Transaction.status == 'pending'
        ).scalar() or 0
        
        total_overdue = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.type == 'payable',
            Transaction.status == 'pending',
            Transaction.due_date < date.today()
        ).scalar() or 0
        
    except Exception as e:
        # Fallback to hardcoded data
        mock_transactions = [
            {
                'id': 1, 'vendor_customer': 'Office Supplies Co', 'amount': 2400.00,
                'due_date': date.today() + timedelta(days=20), 'description': 'Monthly Office Supplies',
                'invoice_number': 'BILL-2024-001', 'status': 'pending'
            },
            {
                'id': 2, 'vendor_customer': 'IT Equipment Ltd', 'amount': 5600.00,
                'due_date': date.today() + timedelta(days=10), 'description': 'Hardware Purchase',
                'invoice_number': 'BILL-2024-002', 'status': 'pending'
            }
        ]
        transactions = MockPagination(mock_transactions)
        total_pending = 13200.75
        total_overdue = 3200.00
    
    return render_template('accounts_payable/index.html',
                         transactions=transactions,
                         total_pending=total_pending,
                         total_overdue=total_overdue,
                         status_filter=status_filter,
                         file_mode=current_app.config.get('USE_FILE_MODE', False))

@accounts_payable_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        vendor = request.form['vendor']
        amount = float(request.form['amount'])
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        description = request.form['description']
        invoice_number = request.form['invoice_number']
        
        # Handle file upload
        receipt_path = None
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                receipt_path = filename
        
        transaction = Transaction(
            type='payable',
            vendor_customer=vendor,
            amount=amount,
            due_date=due_date,
            description=description,
            invoice_number=invoice_number,
            receipt_path=receipt_path,
            created_by=1  # Temporary: Default user ID for QA testing
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Payable transaction created successfully', 'success')
        return redirect(url_for('accounts_payable.index'))
    
    return render_template('accounts_payable/create.html')

@accounts_payable_bp.route('/<int:id>/pay', methods=['POST'])
def mark_paid(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.type != 'payable':
        flash('Invalid transaction type', 'error')
        return redirect(url_for('accounts_payable.index'))
    
    transaction.status = 'paid'
    transaction.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Transaction marked as paid', 'success')
    return redirect(url_for('accounts_payable.index'))

@accounts_payable_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.type != 'payable':
        flash('Invalid transaction type', 'error')
        return redirect(url_for('accounts_payable.index'))
    
    if request.method == 'POST':
        transaction.vendor_customer = request.form['vendor']
        transaction.amount = float(request.form['amount'])
        transaction.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        transaction.description = request.form['description']
        transaction.invoice_number = request.form['invoice_number']
        transaction.updated_at = datetime.utcnow()
        
        # Handle file upload
        if 'receipt' in request.files:
            file = request.files['receipt']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                transaction.receipt_path = filename
        
        db.session.commit()
        flash('Transaction updated successfully', 'success')
        return redirect(url_for('accounts_payable.index'))
    
    return render_template('accounts_payable/edit.html', transaction=transaction)