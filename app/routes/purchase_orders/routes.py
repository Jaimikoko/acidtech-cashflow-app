from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from models.purchase_order import PurchaseOrder, PurchaseOrderItem
from database import db
import json

from . import purchase_orders_bp

@purchase_orders_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    
    query = PurchaseOrder.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    purchase_orders = query.order_by(PurchaseOrder.order_date.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    # Calculate totals
    total_draft = PurchaseOrder.query.filter_by(status='draft').count()
    total_sent = PurchaseOrder.query.filter_by(status='sent').count()
    total_approved = PurchaseOrder.query.filter_by(status='approved').count()
    
    return render_template('purchase_orders/index.html',
                         purchase_orders=purchase_orders,
                         total_draft=total_draft,
                         total_sent=total_sent,
                         total_approved=total_approved,
                         status_filter=status_filter)

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