from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
from sqlalchemy import func
from models.transaction import Transaction
from database import db
import os

from . import accounts_payable_bp

@accounts_payable_bp.route('/')
def index():
    """Accounts Payable index using VApOpen view"""
    status_filter = request.args.get('status', 'all')

    try:
        from models.views import VApOpen
        query = VApOpen.query
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)

        transactions = query.order_by(VApOpen.due_date.asc()).paginate(
            page=request.args.get('page', 1, type=int),
            per_page=20,
            error_out=False
        )
    except Exception:
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

    current_year = date.today().year
    total_outstanding = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == 'payable',
        Transaction.status == 'pending'
    ).scalar() or 0

    total_ytd = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.type == 'payable',
        func.extract('year', Transaction.due_date) == current_year
    ).scalar() or 0

    paid_count = db.session.query(func.count(Transaction.id)).filter(
        Transaction.type == 'payable',
        Transaction.status == 'paid',
        func.extract('year', Transaction.due_date) == current_year
    ).scalar() or 0

    total_count = db.session.query(func.count(Transaction.id)).filter(
        Transaction.type == 'payable',
        func.extract('year', Transaction.due_date) == current_year
    ).scalar() or 0

    payment_accuracy = (paid_count / total_count * 100) if total_count else 0

    pending_bills = db.session.query(func.count(Transaction.id)).filter(
        Transaction.type == 'payable',
        Transaction.status == 'pending'
    ).scalar() or 0

    ap = {
        'total_outstanding': total_outstanding,
        'total_ytd': total_ytd,
        'payment_accuracy': payment_accuracy,
        'pending_bills': pending_bills
    }

    return render_template(
        'accounts_payable/index.html',
        transactions=transactions,
        ap=ap,
        status_filter=status_filter
    )

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