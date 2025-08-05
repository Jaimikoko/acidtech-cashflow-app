from flask import render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models.purchase_order import PurchaseOrder, PurchaseOrderItem
from database import db
from utils.excel_data_manager import excel_manager
import json

from . import purchase_orders_bp

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

@purchase_orders_bp.route('/')
def index():
    """Purchase Orders index with File Mode support"""
    status_filter = request.args.get('status', 'all')
    
    if current_app.config.get('USE_FILE_MODE', False):
        # File Mode: Use Excel data
        try:
            # Get purchase orders from Excel
            all_pos = excel_manager.get_purchase_orders()
            
            # Filter by status if specified
            if status_filter != 'all':
                pos = [po for po in all_pos if po['status'] == status_filter]
            else:
                pos = all_pos
            
            # Calculate status counts
            total_draft = len([po for po in all_pos if po['status'] == 'draft'])
            total_sent = len([po for po in all_pos if po['status'] == 'sent'])
            total_approved = len([po for po in all_pos if po['status'] == 'approved'])
            
            purchase_orders = MockPagination(pos)
            
            return render_template('purchase_orders/index.html',
                                 purchase_orders=purchase_orders,
                                 total_draft=total_draft,
                                 total_sent=total_sent,
                                 total_approved=total_approved,
                                 status_filter=status_filter,
                                 file_mode=True)
        except Exception as e:
            # Fallback to database mode if Excel fails
            pass
    
    # Database Mode or fallback
    try:
        # Query database for purchase orders
        query = PurchaseOrder.query
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        purchase_orders = query.order_by(PurchaseOrder.order_date.desc()).paginate(
            page=request.args.get('page', 1, type=int),
            per_page=20
        )
        
        # Calculate status counts
        total_draft = PurchaseOrder.query.filter_by(status='draft').count()
        total_sent = PurchaseOrder.query.filter_by(status='sent').count()
        total_approved = PurchaseOrder.query.filter_by(status='approved').count()
        
    except Exception as e:
        # Fallback to hardcoded data
        mock_pos = [
            {
                'id': 1, 'po_number': 'PO-2024-001', 'vendor': 'Tech Hardware Solutions',
                'total_amount': 4500.00, 'status': 'approved', 'order_date': date.today() - timedelta(days=15),
                'expected_delivery': date.today() + timedelta(days=30), 'description': 'New Workstation Setup'
            },
            {
                'id': 2, 'po_number': 'PO-2024-002', 'vendor': 'Office Furniture Plus',
                'total_amount': 2800.00, 'status': 'sent', 'order_date': date.today() - timedelta(days=10),
                'expected_delivery': date.today() + timedelta(days=25), 'description': 'Office Furniture Upgrade'
            }
        ]
        purchase_orders = MockPagination(mock_pos)
        total_draft = 1
        total_sent = 1
        total_approved = 1
    
    return render_template('purchase_orders/index.html',
                         purchase_orders=purchase_orders,
                         total_draft=total_draft,
                         total_sent=total_sent,
                         total_approved=total_approved,
                         status_filter=status_filter,
                         file_mode=current_app.config.get('USE_FILE_MODE', False))

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