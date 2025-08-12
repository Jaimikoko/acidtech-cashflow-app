from flask import render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func
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

        # If no POs exist, use VPoSummary view
        if purchase_orders.total == 0:
            from models.views import VPoSummary
            view_query = VPoSummary.query
            if status_filter != 'all':
                view_query = view_query.filter_by(status=status_filter)
            purchase_orders = view_query.order_by(VPoSummary.order_date.desc()).paginate(
                page=request.args.get('page', 1, type=int),
                per_page=20,
                error_out=False
            )
            total_draft = 0
            total_sent = 0
            total_approved = purchase_orders.total

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

    total_value = db.session.query(func.sum(PurchaseOrder.total_amount)).scalar() or 0
    total_count = PurchaseOrder.query.count()
    completed = PurchaseOrder.query.filter(PurchaseOrder.status == 'approved').count()
    completion_rate = (completed / total_count * 100) if total_count else 0
    pending_orders = PurchaseOrder.query.filter(PurchaseOrder.status == 'sent').count()

    po = {
        'total_value': total_value,
        'completion_rate': completion_rate,
        'pending_orders': pending_orders
    }

    return render_template(
        'purchase_orders/index.html',
        purchase_orders=purchase_orders,
        total_draft=total_draft,
        total_sent=total_sent,
        total_approved=total_approved,
        status_filter=status_filter,
        po=po
    )

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