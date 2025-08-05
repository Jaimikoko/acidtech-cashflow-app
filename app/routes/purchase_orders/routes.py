from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
from models.purchase_order import PurchaseOrder, PurchaseOrderItem
from database import db
import json

from . import purchase_orders_bp

@purchase_orders_bp.route('/')
def index():
    # QA MODE: Using hardcoded data for design testing (DB disconnected)
    
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
    
    # Mock purchase orders for display
    mock_pos = [
        {
            'id': 1,
            'po_number': 'PO-2024-001',
            'vendor': 'Tech Hardware Solutions',
            'total_amount': 4500.00,
            'status': 'approved',
            'order_date': date.today() - timedelta(days=15),
            'expected_delivery': date.today() + timedelta(days=30),
            'description': 'New Workstation Setup'
        },
        {
            'id': 2,
            'po_number': 'PO-2024-002',
            'vendor': 'Office Furniture Plus',
            'total_amount': 2800.00,
            'status': 'sent',
            'order_date': date.today() - timedelta(days=10),
            'expected_delivery': date.today() + timedelta(days=25),
            'description': 'Office Furniture Upgrade'
        },
        {
            'id': 3,
            'po_number': 'PO-2024-003',
            'vendor': 'Software Licensing Co',
            'total_amount': 3600.00,
            'status': 'draft',
            'order_date': date.today() - timedelta(days=5),
            'expected_delivery': date.today() + timedelta(days=20),
            'description': 'Annual Software Licenses'
        }
    ]
    
    purchase_orders = MockPagination(mock_pos)
    total_draft = 1
    total_sent = 1
    total_approved = 1
    status_filter = request.args.get('status', 'all')
    
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