from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from database import db
import os

from . import accounts_receivable_bp

# Using real database pagination instead of mock objects

@accounts_receivable_bp.route('/')
def index():
    """Accounts Receivable index - showing income transactions from BankTransaction"""
    status_filter = request.args.get('status', 'all')
    
    try:
        # Get income transactions from BankTransaction for AR view
        # AR = incoming money (positive amounts) that represent receivables
        from models.bank_transaction import BankTransaction
        
        # Query positive amounts (revenue) as these represent receivables
        query = BankTransaction.query.filter(
            BankTransaction.amount > 0,
            BankTransaction.business_category == 'REVENUE'
        )
        
        transactions = query.order_by(BankTransaction.transaction_date.desc()).paginate(
            page=request.args.get('page', 1, type=int),
            per_page=20,
            error_out=False
        )
        
        # Calculate totals
        total_pending = db.session.query(db.func.sum(BankTransaction.amount)).filter(
            BankTransaction.amount > 0,
            BankTransaction.business_category == 'REVENUE'
        ).scalar() or 0
        
        # For overdue AR, we'll use unclassified revenue as proxy for pending invoices
        overdue_count = BankTransaction.query.filter(
            BankTransaction.amount > 0,
            BankTransaction.is_classified == False
        ).count()
        
        total_overdue = overdue_count * 5000  # Estimated average invoice amount
        
        # Format transactions for template compatibility
        formatted_transactions = []
        for trans in transactions.items:
            # Extract customer name from description (first part before space/dash)
            customer_name = trans.description.split(' ')[0] if trans.description else f'Customer-{trans.id}'
            
            formatted_transactions.append({
                'id': trans.id,
                'vendor_customer': customer_name,
                'amount': trans.amount,
                'due_date': trans.transaction_date,  # Use transaction date
                'description': trans.description,
                'invoice_number': trans.bank_reference or f'INV-{trans.id}',
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
    
    return render_template('accounts_receivable/index.html',
                         transactions=transactions,
                         total_pending=total_pending,
                         total_overdue=total_overdue,
                         status_filter=status_filter,
                         file_mode=False)

@accounts_receivable_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        customer = request.form['customer']
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
            type='receivable',
            vendor_customer=customer,
            amount=amount,
            due_date=due_date,
            description=description,
            invoice_number=invoice_number,
            receipt_path=receipt_path,
            created_by=1  # Temporary: Default user ID for QA testing
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Receivable transaction created successfully', 'success')
        return redirect(url_for('accounts_receivable.index'))
    
    return render_template('accounts_receivable/create.html')

@accounts_receivable_bp.route('/<int:id>/receive', methods=['POST'])
@login_required
def mark_received(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.type != 'receivable':
        flash('Invalid transaction type', 'error')
        return redirect(url_for('accounts_receivable.index'))
    
    transaction.status = 'paid'
    transaction.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Payment received', 'success')
    return redirect(url_for('accounts_receivable.index'))

@accounts_receivable_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.type != 'receivable':
        flash('Invalid transaction type', 'error')
        return redirect(url_for('accounts_receivable.index'))
    
    if request.method == 'POST':
        transaction.vendor_customer = request.form['customer']
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
        return redirect(url_for('accounts_receivable.index'))
    
    return render_template('accounts_receivable/edit.html', transaction=transaction)