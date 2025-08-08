#!/usr/bin/env python3
"""
Dashboard API routes for cash flow with classified transaction data
Provides real-time KPIs and summaries based on classified transactions

Author: AcidTech Development Team
Date: 2025-08-08
"""

from flask import jsonify, request, render_template
from datetime import datetime, date, timedelta
from services.cash_flow_calculator import CashFlowCalculator
from models.bank_transaction import BankTransaction

from . import cash_flow_bp

# Initialize calculator instance
calculator = CashFlowCalculator()

@cash_flow_bp.route('/api/dashboard/summary')
def api_dashboard_summary():
    """
    Get comprehensive dashboard summary with real classified data
    
    GET /cash-flow/api/dashboard/summary?start_date=2025-01-01&end_date=2025-12-31
    
    Returns:
    {
        "success": true,
        "data": {
            "kpis": {...},
            "account_summaries": {...},
            "classification_status": {...}
        }
    }
    """
    
    try:
        # Get date parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid start_date format. Use YYYY-MM-DD'
                }), 400
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid end_date format. Use YYYY-MM-DD'
                }), 400
        
        # Get dashboard summary
        summary = calculator.get_dashboard_summary(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get dashboard summary: {str(e)}'
        }), 500

@cash_flow_bp.route('/api/dashboard/account/<account_name>')
def api_account_summary(account_name):
    """
    Get detailed summary for a specific account
    
    GET /cash-flow/api/dashboard/account/Revenue%204717?start_date=2025-01-01
    
    Returns:
    {
        "success": true,
        "data": {
            "account_name": "Revenue 4717",
            "totals": {...},
            "monthly_data": {...}
        }
    }
    """
    
    try:
        # URL decode account name
        account_name = account_name.replace('%20', ' ')
        
        # Get date parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Get account summary
        summary = calculator.get_account_summary(account_name, start_date, end_date)
        
        if 'error' in summary:
            return jsonify({
                'success': False,
                'error': summary['error']
            }), 404
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get account summary: {str(e)}'
        }), 500

@cash_flow_bp.route('/api/dashboard/transfers')
def api_transfer_reconciliation():
    """
    Get transfer reconciliation status
    
    GET /cash-flow/api/dashboard/transfers
    
    Returns:
    {
        "success": true,
        "data": {
            "reconciliation_ratio": 98.5,
            "status": "RECONCILED",
            "total_outgoing_transfers": 150000,
            "total_incoming_transfers": 148000
        }
    }
    """
    
    try:
        reconciliation = calculator.get_transfer_reconciliation()
        
        return jsonify({
            'success': True,
            'data': reconciliation
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get transfer reconciliation: {str(e)}'
        }), 500

@cash_flow_bp.route('/api/dashboard/credit-card')
def api_credit_card_summary():
    """
    Get Capital One credit card summary
    
    GET /cash-flow/api/dashboard/credit-card
    
    Returns:
    {
        "success": true,
        "data": {
            "total_purchases": 25000,
            "total_payments": 20000,
            "current_cycle": {...},
            "receipts": {...}
        }
    }
    """
    
    try:
        cc_summary = calculator.get_credit_card_summary()
        
        return jsonify({
            'success': True,
            'data': cc_summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get credit card summary: {str(e)}'
        }), 500

@cash_flow_bp.route('/api/dashboard/tax-summary')
def api_tax_summary():
    """
    Get tax deductible expenses summary
    
    GET /cash-flow/api/dashboard/tax-summary?start_date=2025-01-01
    
    Returns:
    {
        "success": true,
        "data": {
            "total_deductible": 45000,
            "category_breakdown": {...},
            "receipt_compliance": {...}
        }
    }
    """
    
    try:
        # Get date parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        tax_summary = calculator.get_tax_summary(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': tax_summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get tax summary: {str(e)}'
        }), 500

@cash_flow_bp.route('/api/dashboard/kpis')
def api_quick_kpis():
    """
    Get quick KPIs for dashboard widgets
    
    GET /cash-flow/api/dashboard/kpis
    
    Returns:
    {
        "success": true,
        "data": {
            "revenue_total": 2131700,
            "total_expenses": 200000,
            "net_cash_flow": 1931700,
            "profit_margin": 90.6,
            "classification_percentage": 100.0
        }
    }
    """
    
    try:
        # Get current year summary
        summary = calculator.get_dashboard_summary()
        
        # Extract just the key KPIs for widgets
        kpis = {
            'revenue_total': summary['kpis']['revenue_total'],
            'total_expenses': summary['kpis']['total_expenses'],
            'net_cash_flow': summary['kpis']['net_cash_flow'],
            'profit_margin': summary['kpis']['profit_margin'],
            'classification_percentage': summary['classification_status']['classification_percentage']
        }
        
        return jsonify({
            'success': True,
            'data': kpis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get KPIs: {str(e)}'
        }), 500

# Web routes for dashboard pages
@cash_flow_bp.route('/enhanced-dashboard')
def enhanced_dashboard():
    """
    Enhanced dashboard with real-time classified data
    
    Shows:
    - Real KPIs from classified transactions
    - Account summaries with breakdowns
    - Transfer reconciliation status
    - Credit card cycle information
    - Classification progress
    """
    
    try:
        # Get initial data for page load
        summary = calculator.get_dashboard_summary()
        
        # Get quick stats for template
        kpis = summary['kpis']
        classification_status = summary['classification_status']
        
        return render_template('cash_flow/enhanced_dashboard.html',
                             kpis=kpis,
                             classification_status=classification_status,
                             account_summaries=summary['account_summaries'],
                             transfer_reconciliation=summary['transfer_reconciliation'],
                             credit_card_summary=summary['credit_card_summary'],
                             last_updated=summary['last_updated'])
        
    except Exception as e:
        return render_template('cash_flow/enhanced_dashboard.html',
                             error=f'Failed to load dashboard: {str(e)}',
                             kpis={},
                             classification_status={})

@cash_flow_bp.route('/real-time-dashboard')  
def real_time_dashboard():
    """
    Real-time dashboard with auto-refresh functionality
    Uses AJAX for dynamic updates
    """
    
    return render_template('cash_flow/real_time_dashboard.html')