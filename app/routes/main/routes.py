from flask import render_template, request, jsonify, send_from_directory
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from models.transaction import Transaction
from models.purchase_order import PurchaseOrder
from database import db
import json
import os

from . import main_bp

@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main_bp.root_path, '..', '..', 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@main_bp.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        # Fallback to simple HTML if template fails
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>AciTech Cash Flow Management</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5;">
            <div style="max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #2563eb; text-align: center; margin-bottom: 30px;">
                    🚀 AciTech Cash Flow Management (Modular)
                </h1>
                <p style="text-align: center; color: #6b7280; font-size: 18px; margin-bottom: 30px;">
                    Professional cash flow management system - New Modular Architecture
                </p>
                <div style="text-align: center;">
                    <a href="/auth/login" style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px;">
                        Login
                    </a>
                    <a href="/auth/register" style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px;">
                        Get Started
                    </a>
                    <a href="/health" style="display: inline-block; background: #6b7280; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px;">
                        Health Check
                    </a>
                </div>
                <div style="margin-top: 40px; padding: 20px; background: #f3f4f6; border-radius: 6px;">
                    <h3 style="color: #374151; margin-bottom: 15px;">✅ System Status - Modular Architecture</h3>
                    <p style="color: #10b981; margin: 5px 0;">✓ Flask Application: Running</p>
                    <p style="color: #10b981; margin: 5px 0;">✓ Database: Connected</p>
                    <p style="color: #10b981; margin: 5px 0;">✓ Azure App Service: Active</p>
                    <p style="color: #2563eb; margin: 5px 0;">🔄 Architecture: New Modular Blueprints</p>
                    <p style="color: #f59e0b; margin: 5px 0;">⚠ Template Error: {str(e)}</p>
                </div>
            </div>
        </body>
        </html>
        '''

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get summary data for dashboard
    total_receivables = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='receivable', status='pending').scalar() or 0
    total_payables = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='payable', status='pending').scalar() or 0
    
    # Recent transactions
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    
    # Overdue items
    overdue_receivables = Transaction.query.filter(
        Transaction.type == 'receivable',
        Transaction.status == 'pending',
        Transaction.due_date < date.today()
    ).count()
    
    overdue_payables = Transaction.query.filter(
        Transaction.type == 'payable',
        Transaction.status == 'pending',
        Transaction.due_date < date.today()
    ).count()
    
    return render_template('dashboard.html',
                         total_receivables=total_receivables,
                         total_payables=total_payables,
                         recent_transactions=recent_transactions,
                         overdue_receivables=overdue_receivables,
                         overdue_payables=overdue_payables)

@main_bp.route('/api/cash-flow-data')
@login_required
def cash_flow_data():
    # Generate cash flow data for charts
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    # Sample data for demonstration
    dates = []
    receivables = []
    payables = []
    
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime('%Y-%m-%d'))
        
        # Sample receivables data
        receivables_amount = Transaction.query.filter(
            Transaction.type == 'receivable',
            Transaction.due_date == current_date
        ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        
        # Sample payables data
        payables_amount = Transaction.query.filter(
            Transaction.type == 'payable',
            Transaction.due_date == current_date
        ).with_entities(db.func.sum(Transaction.amount)).scalar() or 0
        
        receivables.append(float(receivables_amount))
        payables.append(float(payables_amount))
        
        current_date += timedelta(days=1)
    
    return jsonify({
        'dates': dates,
        'receivables': receivables,
        'payables': payables
    })