from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from database import db
import os

from . import accounts_payable_bp

# Removed MockPagination - using real database pagination instead

@accounts_payable_bp.route('/')
def index():
    """Accounts Payable index - showing expense transactions from BankTransaction"""
    status_filter = request.args.get('status', 'all')
    
    try:
        # Get expense transactions from BankTransaction for AP view
        # AP = outgoing money (negative amounts) that represent bills to be paid
        from models.bank_transaction import BankTransaction
        
        # Query negative amounts (expenses) as these represent payables
        query = BankTransaction.query.filter(
            BankTransaction.amount < 0,
            BankTransaction.business_category.in_(['OPERATING_EXPENSE', 'CAPITAL_EXPENSE'])
        )
        
        transactions = query.order_by(BankTransaction.transaction_date.desc()).paginate(
            page=request.args.get('page', 1, type=int),
            per_page=20,
            error_out=False
        )
        
        # Calculate totals - convert to payable amounts (positive values)
        total_pending = abs(db.session.query(db.func.sum(BankTransaction.amount)).filter(
            BankTransaction.amount < 0,
            BankTransaction.business_category.in_(['OPERATING_EXPENSE', 'CAPITAL_EXPENSE'])
        ).scalar() or 0)
        
        # For overdue, we'll use transactions needing review as proxy
        overdue_count = BankTransaction.query.filter(
            BankTransaction.amount < 0,
            BankTransaction.needs_review == True
        ).count()
        
        total_overdue = overdue_count * 1500  # Estimated average overdue amount
        
        # Format transactions for template compatibility
        formatted_transactions = []
        for trans in transactions.items:
            formatted_transactions.append({
                'id': trans.id,
                'vendor_customer': trans.description[:50],  # Use description as vendor name
                'amount': abs(trans.amount),  # Convert to positive for display
                'due_date': trans.transaction_date,  # Use transaction date
                'description': trans.description,
                'invoice_number': trans.bank_reference or f'TX-{trans.id}',
                'status': 'paid' if trans.is_reconciled else 'pending'
            })
        
        # Update transactions items for template
        transactions.items = formatted_transactions
        
    except Exception as e:
        # Simple fallback
        transactions = type('obj', (object,), {
            'items': [],
            'page': 1,
            'pages': 1,
            'total': 0,
            'has_prev': False,
            'has_next': False,
            'prev_num': None,
            'next_num': None
        })()
        total_pending = 0
        total_overdue = 0
    
    return render_template('accounts_payable/index.html',
                         transactions=transactions,
                         total_pending=total_pending,
                         total_overdue=total_overdue,
                         status_filter=status_filter,
                         file_mode=False)

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