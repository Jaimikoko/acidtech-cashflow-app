#!/usr/bin/env python3
"""
AcidTech Cash Flow Calculator Service

Calculates real-time KPIs and summaries based on classified transactions
Provides accurate financial metrics for dashboard and reporting

Author: AcidTech Development Team  
Date: 2025-08-08
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_, or_
from calendar import monthrange

from database import db
from models.bank_transaction import BankTransaction

class CashFlowCalculator:
    """
    Advanced calculator for cash flow metrics using classified transaction data
    """
    
    def __init__(self):
        """Initialize calculator with account configurations"""
        
        # Account type mappings
        self.account_types = {
            'Revenue 4717': {
                'type': 'revenue',
                'positive_flow': 'REVENUE',
                'negative_flow': 'INTERNAL_TRANSFER',
                'gl_base': '4000',
                'color': '#10b981'
            },
            'Bill Pay 5285': {
                'type': 'expense',
                'positive_flow': 'INTERNAL_TRANSFER',
                'negative_flow': 'OPERATING_EXPENSE',
                'gl_base': '6000', 
                'color': '#ef4444'
            },
            'Payroll 4079': {
                'type': 'payroll',
                'positive_flow': 'INTERNAL_TRANSFER',
                'negative_flow': 'PAYROLL_EXPENSE',
                'gl_base': '6200',
                'color': '#f59e0b'
            },
            'Capital One': {
                'type': 'credit_card',
                'positive_flow': 'CREDIT_CARD_PAYMENT',
                'negative_flow': 'OPERATING_EXPENSE',
                'gl_base': '6000',
                'color': '#3b82f6'
            }
        }

    def get_dashboard_summary(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
        """
        Get comprehensive dashboard summary with real classified data
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict with complete dashboard metrics
        """
        
        # Default to current year if no dates provided
        if not start_date:
            start_date = date(date.today().year, 1, 1)
        if not end_date:
            end_date = date.today()
        
        # Base query with date filters
        base_query = BankTransaction.query.filter(
            BankTransaction.transaction_date >= start_date,
            BankTransaction.transaction_date <= end_date,
            BankTransaction.is_classified == True
        )
        
        # Calculate primary KPIs
        revenue_total = base_query.filter(
            BankTransaction.business_category == 'REVENUE'
        ).with_entities(func.sum(BankTransaction.amount)).scalar()
        revenue_total = Decimal(str(revenue_total)) if revenue_total else Decimal('0')
        
        operating_expenses = base_query.filter(
            BankTransaction.business_category == 'OPERATING_EXPENSE'
        ).with_entities(func.sum(func.abs(BankTransaction.amount))).scalar()
        operating_expenses = Decimal(str(operating_expenses)) if operating_expenses else Decimal('0')
        
        payroll_expenses = base_query.filter(
            BankTransaction.business_category == 'PAYROLL_EXPENSE'
        ).with_entities(func.sum(func.abs(BankTransaction.amount))).scalar()
        payroll_expenses = Decimal(str(payroll_expenses)) if payroll_expenses else Decimal('0')
        
        tax_payments = base_query.filter(
            BankTransaction.business_category == 'TAX_PAYMENT'
        ).with_entities(func.sum(func.abs(BankTransaction.amount))).scalar()
        tax_payments = Decimal(str(tax_payments)) if tax_payments else Decimal('0')
        
        bank_fees = base_query.filter(
            BankTransaction.business_category == 'BANK_FEE'
        ).with_entities(func.sum(func.abs(BankTransaction.amount))).scalar()
        bank_fees = Decimal(str(bank_fees)) if bank_fees else Decimal('0')
        
        # Calculate net cash flow
        total_expenses = operating_expenses + payroll_expenses + tax_payments + bank_fees
        net_cash_flow = revenue_total - total_expenses
        
        # Get account breakdowns
        account_summaries = {}
        for account_name in self.account_types.keys():
            account_summaries[account_name] = self.get_account_summary(
                account_name, start_date, end_date
            )
        
        # Calculate ratios and percentages
        expense_ratio = float(total_expenses / revenue_total * 100) if revenue_total > 0 else 0
        profit_margin = float(net_cash_flow / revenue_total * 100) if revenue_total > 0 else 0
        
        # Get transfer reconciliation status
        transfer_reconciliation = self.get_transfer_reconciliation()
        
        # Get classification status
        classification_status = BankTransaction.get_classification_summary()
        
        # Get credit card summary
        credit_card_summary = self.get_credit_card_summary()
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': (end_date - start_date).days + 1
            },
            'kpis': {
                'revenue_total': float(revenue_total),
                'operating_expenses': float(operating_expenses), 
                'payroll_expenses': float(payroll_expenses),
                'tax_payments': float(tax_payments),
                'bank_fees': float(bank_fees),
                'total_expenses': float(total_expenses),
                'net_cash_flow': float(net_cash_flow),
                'expense_ratio': round(expense_ratio, 1),
                'profit_margin': round(profit_margin, 1)
            },
            'account_summaries': account_summaries,
            'transfer_reconciliation': transfer_reconciliation,
            'classification_status': classification_status,
            'credit_card_summary': credit_card_summary,
            'last_updated': datetime.utcnow().isoformat()
        }

    def get_account_summary(self, account_name: str, start_date: Optional[date] = None, 
                          end_date: Optional[date] = None) -> Dict:
        """
        Get detailed summary for a specific account
        
        Args:
            account_name: Name of the account
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dict with account-specific metrics
        """
        
        if account_name not in self.account_types:
            return {'error': f'Unknown account: {account_name}'}
        
        # Default to current year
        if not start_date:
            start_date = date(date.today().year, 1, 1)
        if not end_date:
            end_date = date.today()
        
        # Query for this account
        account_query = BankTransaction.query.filter(
            BankTransaction.account_name == account_name,
            BankTransaction.transaction_date >= start_date,
            BankTransaction.transaction_date <= end_date,
            BankTransaction.is_classified == True
        )
        
        total_transactions = account_query.count()
        
        # Get totals by flow direction
        positive_total = account_query.filter(
            BankTransaction.amount > 0
        ).with_entities(func.sum(BankTransaction.amount)).scalar()
        positive_total = Decimal(str(positive_total)) if positive_total else Decimal('0')
        
        negative_total = account_query.filter(
            BankTransaction.amount < 0
        ).with_entities(func.sum(func.abs(BankTransaction.amount))).scalar()
        negative_total = Decimal(str(negative_total)) if negative_total else Decimal('0')
        
        net_total = positive_total - negative_total
        
        # Get breakdown by business category
        category_breakdown = {}
        categories = account_query.with_entities(
            BankTransaction.business_category
        ).distinct().all()
        
        for (category,) in categories:
            if category:
                category_total = account_query.filter(
                    BankTransaction.business_category == category
                ).with_entities(func.sum(BankTransaction.amount)).scalar()
                category_total = Decimal(str(category_total)) if category_total else Decimal('0')
                
                category_count = account_query.filter(
                    BankTransaction.business_category == category
                ).count()
                
                category_breakdown[category] = {
                    'total': float(category_total),
                    'count': category_count,
                    'average': float(category_total / category_count) if category_count > 0 else 0
                }
        
        # Monthly breakdown
        monthly_data = self._get_monthly_breakdown(account_name, start_date, end_date)
        
        # Recent transactions
        recent_transactions = account_query.order_by(
            BankTransaction.transaction_date.desc()
        ).limit(10).all()
        
        recent_list = []
        for t in recent_transactions:
            recent_list.append({
                'id': t.id,
                'date': t.transaction_date.isoformat(),
                'description': t.description[:60] + '...' if len(t.description) > 60 else t.description,
                'amount': float(t.amount),
                'category': t.business_category,
                'confidence': float(t.classification_confidence) if t.classification_confidence else 0,
                'merchant': t.merchant_name
            })
        
        return {
            'account_name': account_name,
            'account_type': self.account_types[account_name]['type'],
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'totals': {
                'positive_total': float(positive_total),
                'negative_total': float(negative_total),
                'net_total': float(net_total),
                'transaction_count': total_transactions
            },
            'category_breakdown': category_breakdown,
            'monthly_data': monthly_data,
            'recent_transactions': recent_list,
            'account_config': self.account_types[account_name]
        }

    def get_transfer_reconciliation(self) -> Dict:
        """
        Get transfer reconciliation status between accounts
        
        Returns:
            Dict with reconciliation metrics
        """
        
        # Get all internal transfers
        transfers_out = BankTransaction.query.filter(
            BankTransaction.business_category == 'INTERNAL_TRANSFER',
            BankTransaction.amount < 0,
            BankTransaction.is_classified == True
        ).all()
        
        transfers_in = BankTransaction.query.filter(
            BankTransaction.business_category == 'INTERNAL_TRANSFER',
            BankTransaction.amount > 0,
            BankTransaction.is_classified == True
        ).all()
        
        # Calculate totals
        total_outgoing = sum(abs(float(t.amount)) for t in transfers_out)
        total_incoming = sum(float(t.amount) for t in transfers_in)
        
        # Calculate reconciliation ratio
        reconciliation_ratio = (min(total_outgoing, total_incoming) / max(total_outgoing, total_incoming) * 100) if max(total_outgoing, total_incoming) > 0 else 100
        
        # Identify unmatched transfers
        unmatched_outgoing = len([t for t in transfers_out if not t.transfer_reference])
        unmatched_incoming = len([t for t in transfers_in if not t.transfer_reference])
        
        return {
            'total_outgoing_transfers': total_outgoing,
            'total_incoming_transfers': total_incoming,
            'difference': abs(total_outgoing - total_incoming),
            'reconciliation_ratio': round(reconciliation_ratio, 1),
            'transfers_out_count': len(transfers_out),
            'transfers_in_count': len(transfers_in),
            'unmatched_outgoing': unmatched_outgoing,
            'unmatched_incoming': unmatched_incoming,
            'status': 'RECONCILED' if reconciliation_ratio > 95 else 'NEEDS_REVIEW'
        }

    def get_credit_card_summary(self) -> Dict:
        """
        Get Capital One credit card summary with cycle information
        
        Returns:
            Dict with credit card metrics
        """
        
        # Get all Capital One transactions
        cc_transactions = BankTransaction.query.filter(
            BankTransaction.is_credit_card_transaction == True,
            BankTransaction.is_classified == True
        ).all()
        
        if not cc_transactions:
            return {
                'total_transactions': 0,
                'message': 'No credit card transactions found'
            }
        
        # Separate purchases and payments
        purchases = [t for t in cc_transactions if t.amount < 0]
        payments = [t for t in cc_transactions if t.amount > 0]
        
        total_purchases = sum(abs(float(t.amount)) for t in purchases)
        total_payments = sum(float(t.amount) for t in payments)
        
        # Current cycle information (based on day 11 cutoff)
        today = date.today()
        current_cycle_cut = date(today.year, today.month, 11)
        if today.day < 11:
            # Still in previous month's cycle
            if today.month == 1:
                current_cycle_cut = date(today.year - 1, 12, 11)
            else:
                current_cycle_cut = date(today.year, today.month - 1, 11)
        
        # Get transactions in current cycle
        current_cycle_transactions = [
            t for t in cc_transactions 
            if t.transaction_date >= current_cycle_cut
        ]
        
        current_cycle_purchases = sum(
            abs(float(t.amount)) for t in current_cycle_transactions if t.amount < 0
        )
        
        # Count transactions needing receipts
        receipts_required = len([
            t for t in purchases 
            if t.receipt_status == 'REQUIRED'
        ])
        
        receipts_received = len([
            t for t in purchases 
            if t.receipt_status == 'RECEIVED'
        ])
        
        return {
            'total_transactions': len(cc_transactions),
            'total_purchases': total_purchases,
            'total_payments': total_payments,
            'net_balance_change': total_payments - total_purchases,
            'purchase_count': len(purchases),
            'payment_count': len(payments),
            'current_cycle': {
                'cycle_cut_date': current_cycle_cut.isoformat(),
                'purchases_this_cycle': current_cycle_purchases,
                'transactions_this_cycle': len(current_cycle_transactions)
            },
            'receipts': {
                'required': receipts_required,
                'received': receipts_received,
                'pending': receipts_required - receipts_received,
                'completion_rate': round(receipts_received / receipts_required * 100, 1) if receipts_required > 0 else 100
            }
        }

    def _get_monthly_breakdown(self, account_name: str, start_date: date, end_date: date) -> Dict:
        """Get monthly breakdown for an account"""
        
        monthly_data = {}
        
        # Get all months in the date range
        current_date = start_date.replace(day=1)
        end_month = end_date.replace(day=1)
        
        while current_date <= end_month:
            # Get last day of current month
            last_day = monthrange(current_date.year, current_date.month)[1]
            month_end = current_date.replace(day=last_day)
            
            # Query for this month
            month_query = BankTransaction.query.filter(
                BankTransaction.account_name == account_name,
                BankTransaction.transaction_date >= current_date,
                BankTransaction.transaction_date <= month_end,
                BankTransaction.is_classified == True
            )
            
            positive_total = month_query.filter(
                BankTransaction.amount > 0
            ).with_entities(func.sum(BankTransaction.amount)).scalar()
            positive_total = Decimal(str(positive_total)) if positive_total else Decimal('0')
            
            negative_total = month_query.filter(
                BankTransaction.amount < 0
            ).with_entities(func.sum(func.abs(BankTransaction.amount))).scalar()
            negative_total = Decimal(str(negative_total)) if negative_total else Decimal('0')
            
            transaction_count = month_query.count()
            
            month_key = current_date.strftime('%Y-%m')
            monthly_data[month_key] = {
                'month': current_date.strftime('%B %Y'),
                'positive_total': float(positive_total),
                'negative_total': float(negative_total),
                'net_total': float(positive_total - negative_total),
                'transaction_count': transaction_count
            }
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        return monthly_data

    def get_tax_summary(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
        """
        Get tax-related summary for tax reporting
        
        Returns:
            Dict with tax deductible expenses and categories
        """
        
        if not start_date:
            start_date = date(date.today().year, 1, 1)
        if not end_date:
            end_date = date.today()
        
        # Get all tax deductible transactions
        tax_deductible = BankTransaction.query.filter(
            BankTransaction.is_tax_deductible == True,
            BankTransaction.transaction_date >= start_date,
            BankTransaction.transaction_date <= end_date,
            BankTransaction.is_classified == True
        ).all()
        
        # Calculate totals by tax category
        category_totals = {}
        for transaction in tax_deductible:
            category = transaction.tax_category or 'UNCATEGORIZED'
            if category not in category_totals:
                category_totals[category] = {
                    'total': 0,
                    'count': 0,
                    'receipts_required': 0,
                    'receipts_received': 0
                }
            
            category_totals[category]['total'] += abs(float(transaction.amount))
            category_totals[category]['count'] += 1
            
            if transaction.receipt_status == 'REQUIRED':
                category_totals[category]['receipts_required'] += 1
            elif transaction.receipt_status == 'RECEIVED':
                category_totals[category]['receipts_received'] += 1
        
        total_deductible = sum(abs(float(t.amount)) for t in tax_deductible)
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_deductible': total_deductible,
            'transaction_count': len(tax_deductible),
            'category_breakdown': category_totals,
            'receipt_compliance': {
                'total_requiring_receipts': len([t for t in tax_deductible if t.receipt_status == 'REQUIRED']),
                'receipts_received': len([t for t in tax_deductible if t.receipt_status == 'RECEIVED']),
                'receipts_pending': len([t for t in tax_deductible if t.receipt_status == 'REQUIRED'])
            }
        }