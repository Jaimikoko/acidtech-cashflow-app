from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, date
from app.models.transaction import Transaction
from app import db
import os

bp = Blueprint('accounts_payable', __name__)

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = Transaction.query.filter_by(type='payable')
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    transactions = query.order_by(Transaction.due_date.asc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Calculate totals
    total_pending = db.session.query(db.func.sum(Transaction.amount)).filter_by(
        type='payable', status='pending').scalar() or 0
    total_overdue = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.type == 'payable',
        Transaction.status == 'pending',
        Transaction.due_date < date.today()
    ).scalar() or 0
    
    return render_template('accounts_payable/index.html',
                         transactions=transactions,
                         total_pending=total_pending,
                         total_overdue=total_overdue,
                         status_filter=status_filter)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
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
            created_by=current_user.id
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Payable transaction created successfully', 'success')
        return redirect(url_for('accounts_payable.index'))
    
    return render_template('accounts_payable/create.html')

@bp.route('/<int:id>/pay', methods=['POST'])
@login_required
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

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
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