from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app import db
import json

bp = Blueprint('purchase_orders', __name__)

@bp.route('/')
@login_required
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

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        po_number = request.form['po_number']
        vendor = request.form['vendor']
        order_date = datetime.strptime(request.form['order_date'], '%Y-%m-%d').date()
        expected_delivery = None
        if request.form['expected_delivery']:
            expected_delivery = datetime.strptime(request.form['expected_delivery'], '%Y-%m-%d').date()
        description = request.form['description']
        terms = request.form['terms']
        
        # Check if PO number already exists
        existing_po = PurchaseOrder.query.filter_by(po_number=po_number).first()
        if existing_po:
            flash('Purchase Order number already exists', 'error')
            return render_template('purchase_orders/create.html')
        
        # Parse line items from JSON
        line_items_json = request.form.get('line_items', '[]')
        line_items_data = json.loads(line_items_json)
        
        total_amount = sum(float(item['total_price']) for item in line_items_data)
        
        purchase_order = PurchaseOrder(
            po_number=po_number,
            vendor=vendor,
            total_amount=total_amount,
            order_date=order_date,
            expected_delivery=expected_delivery,
            description=description,
            terms=terms,
            created_by=current_user.id
        )
        
        db.session.add(purchase_order)
        db.session.flush()  # Get the ID
        
        # Add line items
        for item_data in line_items_data:
            line_item = PurchaseOrderItem(
                po_id=purchase_order.id,
                item_description=item_data['description'],
                quantity=int(item_data['quantity']),
                unit_price=float(item_data['unit_price']),
                total_price=float(item_data['total_price'])
            )
            db.session.add(line_item)
        
        db.session.commit()
        
        flash('Purchase Order created successfully', 'success')
        return redirect(url_for('purchase_orders.index'))
    
    return render_template('purchase_orders/create.html')

@bp.route('/<int:id>')
@login_required
def view(id):
    purchase_order = PurchaseOrder.query.get_or_404(id)
    return render_template('purchase_orders/view.html', purchase_order=purchase_order)

@bp.route('/<int:id>/update-status', methods=['POST'])
@login_required
def update_status(id):
    purchase_order = PurchaseOrder.query.get_or_404(id)
    new_status = request.form['status']
    
    if new_status in ['draft', 'sent', 'approved', 'fulfilled']:
        purchase_order.status = new_status
        purchase_order.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Purchase Order status updated to {new_status}', 'success')
    else:
        flash('Invalid status', 'error')
    
    return redirect(url_for('purchase_orders.view', id=id))

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    purchase_order = PurchaseOrder.query.get_or_404(id)
    
    if request.method == 'POST':
        purchase_order.vendor = request.form['vendor']
        purchase_order.order_date = datetime.strptime(request.form['order_date'], '%Y-%m-%d').date()
        if request.form['expected_delivery']:
            purchase_order.expected_delivery = datetime.strptime(request.form['expected_delivery'], '%Y-%m-%d').date()
        purchase_order.description = request.form['description']
        purchase_order.terms = request.form['terms']
        
        # Update line items
        line_items_json = request.form.get('line_items', '[]')
        line_items_data = json.loads(line_items_json)
        
        # Delete existing line items
        PurchaseOrderItem.query.filter_by(po_id=purchase_order.id).delete()
        
        # Add updated line items
        total_amount = 0
        for item_data in line_items_data:
            line_item = PurchaseOrderItem(
                po_id=purchase_order.id,
                item_description=item_data['description'],
                quantity=int(item_data['quantity']),
                unit_price=float(item_data['unit_price']),
                total_price=float(item_data['total_price'])
            )
            db.session.add(line_item)
            total_amount += float(item_data['total_price'])
        
        purchase_order.total_amount = total_amount
        purchase_order.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Purchase Order updated successfully', 'success')
        return redirect(url_for('purchase_orders.view', id=id))
    
    return render_template('purchase_orders/edit.html', purchase_order=purchase_order)