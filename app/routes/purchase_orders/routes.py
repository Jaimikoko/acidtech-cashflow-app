from flask import render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models.purchase_order import PurchaseOrder, PurchaseOrderItem
from database import db
import json

from . import purchase_orders_bp

# Using real database pagination instead of mock objects

@purchase_orders_bp.route('/')
def index():
    """Purchase Orders index - showing large expenses as potential POs"""
    status_filter = request.args.get('status', 'all')
    
    try:
        # First try to get real POs from database
        query = PurchaseOrder.query
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        purchase_orders = query.order_by(PurchaseOrder.order_date.desc()).paginate(
            page=request.args.get('page', 1, type=int),
            per_page=20,
            error_out=False
        )
        
        # Calculate status counts
        total_draft = PurchaseOrder.query.filter_by(status='draft').count()
        total_sent = PurchaseOrder.query.filter_by(status='sent').count()
        total_approved = PurchaseOrder.query.filter_by(status='approved').count()
        
        # If no POs exist, show large expenses from BankTransaction as potential POs
        if purchase_orders.total == 0:
            from models.bank_transaction import BankTransaction
            
            # Get large expenses (>$5000) that could become POs
            large_expenses = BankTransaction.query.filter(
                BankTransaction.amount < -5000,  # Large negative amounts
                BankTransaction.business_category.in_(['OPERATING_EXPENSE', 'CAPITAL_EXPENSE'])
            ).order_by(BankTransaction.transaction_date.desc()).paginate(
                page=request.args.get('page', 1, type=int),
                per_page=20,
                error_out=False
            )
            
            # Convert to PO format for display
            formatted_pos = []
            for trans in large_expenses.items:
                vendor_name = trans.description.split(' ')[0] if trans.description else f'Vendor-{trans.id}'
                formatted_pos.append({
                    'id': f'BT-{trans.id}',  # Prefix with BT to show it's from BankTransaction
                    'po_number': f'PO-AUTO-{trans.id}',
                    'vendor': vendor_name,
                    'total_amount': abs(trans.amount),
                    'status': 'approved',  # Already paid
                    'order_date': trans.transaction_date,
                    'expected_delivery': trans.transaction_date,
                    'description': trans.description[:100]
                })
            
            # Update pagination items
            large_expenses.items = formatted_pos
            purchase_orders = large_expenses
            
            # Update counts for large expenses
            total_approved = len(formatted_pos)
            total_sent = 0
            total_draft = 0
        
    except Exception as e:
        # Simple fallback
        purchase_orders = type('obj', (object,), {
            'items': [],
            'page': 1,
            'pages': 1,
            'total': 0,
            'has_prev': False,
            'has_next': False,
            'prev_num': None,
            'next_num': None
        })()
        total_draft = 0
        total_sent = 0
        total_approved = 0
    
    return render_template('purchase_orders/index.html',
                         purchase_orders=purchase_orders,
                         total_draft=total_draft,
                         total_sent=total_sent,
                         total_approved=total_approved,
                         status_filter=status_filter,
                         file_mode=False)

@purchase_orders_bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        po_number = request.form['po_number']
        vendor = request.form['vendor']
        order_date = datetime.strptime(request.form['order_date'], '%Y-%m-%d').date()
        expected_delivery = None
        if request.form.get('expected_delivery'):
            expected_delivery = datetime.strptime(request.form['expected_delivery'], '%Y-%m-%d').date()
        description = request.form['description']
        terms = request.form.get('terms', '')
        
        # Check if PO number already exists
        existing_po = PurchaseOrder.query.filter_by(po_number=po_number).first()
        if existing_po:
            flash('PO number already exists', 'error')
            return render_template('purchase_orders/create.html')
        
        purchase_order = PurchaseOrder(
            po_number=po_number,
            vendor=vendor,
            order_date=order_date,
            expected_delivery=expected_delivery,
            description=description,
            terms=terms,
            created_by=current_user.id
        )
        
        db.session.add(purchase_order)
        db.session.commit()
        
        flash('Purchase order created successfully', 'success')
        return redirect(url_for('purchase_orders.view', id=purchase_order.id))
    
    return render_template('purchase_orders/create.html')

@purchase_orders_bp.route('/<int:id>')
@login_required
def view(id):
    purchase_order = PurchaseOrder.query.get_or_404(id)
    return render_template('purchase_orders/view.html', purchase_order=purchase_order)

@purchase_orders_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    purchase_order = PurchaseOrder.query.get_or_404(id)
    
    if request.method == 'POST':
        purchase_order.vendor = request.form['vendor']
        purchase_order.order_date = datetime.strptime(request.form['order_date'], '%Y-%m-%d').date()
        if request.form.get('expected_delivery'):
            purchase_order.expected_delivery = datetime.strptime(request.form['expected_delivery'], '%Y-%m-%d').date()
        purchase_order.description = request.form['description']
        purchase_order.terms = request.form.get('terms', '')
        purchase_order.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Purchase order updated successfully', 'success')
        return redirect(url_for('purchase_orders.view', id=purchase_order.id))
    
    return render_template('purchase_orders/edit.html', purchase_order=purchase_order)