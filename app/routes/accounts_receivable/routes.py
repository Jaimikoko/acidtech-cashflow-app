from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from database import db
import os

from . import accounts_receivable_bp

@accounts_receivable_bp.route('/')
def index():
    """Accounts Receivable index using VArOpen view"""
    status_filter = request.args.get('status', 'all')

    try:
        from models.views import VArOpen
        from sqlalchemy import func
        query = VArOpen.query
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)

        transactions = query.order_by(VArOpen.due_date.asc()).paginate(
            page=request.args.get('page', 1, type=int),
            per_page=20,
            error_out=False
        )

        total_pending = db.session.query(func.sum(VArOpen.amount)).scalar() or 0
        total_overdue = db.session.query(func.sum(VArOpen.amount)).filter(
            VArOpen.due_date < date.today()
        ).scalar() or 0

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
        total_pending = 0
        total_overdue = 0

    return render_template('accounts_receivable/index.html',
                         transactions=transactions,
                         total_pending=total_pending,
                         total_overdue=total_overdue,
                         status_filter=status_filter)

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