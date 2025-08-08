#!/usr/bin/env python3
"""
AcidTech Cash Flow - Transaction Classifier Service

Provides intelligent classification of bank transactions based on:
- Account type (Revenue 4717, Bill Pay 5285, Payroll 4079, Capital One)
- Transaction patterns and descriptions
- Amount flow analysis
- Internal transfer detection
- Credit card cycle logic (Capital One - cuts day 11)

Author: AcidTech Development Team
Date: 2025-08-08
"""

import re
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func

from database import db
from models.bank_transaction import BankTransaction

class CashFlowClassifier:
    """
    Intelligent transaction classifier for AcidTech cash flow management
    """
    
    def __init__(self):
        """Initialize classifier with account mappings and patterns"""
        
        # Account configurations
        self.account_configs = {
            'Revenue 4717': {
                'primary_type': 'revenue',
                'expected_flow': 'inbound',
                'transfer_targets': ['5285', '4079'],
                'gl_base': '4000'
            },
            'Bill Pay 5285': {
                'primary_type': 'expense',
                'expected_flow': 'outbound', 
                'transfer_source': '4717',
                'gl_base': '6000'
            },
            'Payroll 4079': {
                'primary_type': 'expense',
                'expected_flow': 'outbound',
                'transfer_source': '4717', 
                'gl_base': '6200'
            },
            'Capital One': {
                'primary_type': 'credit_card',
                'expected_flow': 'mixed',
                'cycle_day': 11,
                'gl_base': '6000'
            }
        }
        
        # Transfer detection patterns (based on actual data analysis)
        self.transfer_patterns = {
            'to_bill_pay': [
                r'Transfer.*CH x4717.*CH x5285',
                r'Transfer.*4717.*5285',
                r'Bill Pay',
                r'TMID:.*5285'
            ],
            'to_payroll': [
                r'Transfer.*CH x4717.*CH x4709', 
                r'Transfer.*4717.*4709',
                r'Payroll',
                r'Salary',
                r'Hourly'
            ],
            'from_revenue': [
                r'Transfer.*CH x4717',
                r'Transfer to DDA'
            ],
            'internal_transfer': [
                r'Transfer.*TMID:',
                r'CH x\d{4}.*CH x\d{4}'
            ]
        }
        
        # Vendor/merchant extraction patterns
        self.vendor_patterns = [
            r'ACH.*?([A-Z][A-Z\s&\.]{10,40}?)[\s]{2,}',  # ACH payments
            r'Memo Credit\s*:\s*([A-Z][A-Z\s&\.]{10,40}?)[\s]{2,}',  # Memo credits
            r'Debit Card\s*([A-Z][A-Z\s&\.]{10,40})[\s]*\d',  # Debit card
            r'^([A-Z][A-Z\s&\.]{10,40})[\s]*\*',  # Starting patterns
        ]
        
        # Tax deductible categories
        self.tax_deductible_categories = [
            'business_expense', 'office_supplies', 'travel', 'meals',
            'equipment', 'professional_services', 'utilities', 'rent'
        ]

    def classify_transaction(self, transaction: BankTransaction) -> Dict:
        """
        Classify a single transaction based on account and patterns
        
        Args:
            transaction: BankTransaction instance
            
        Returns:
            Dict with classification results
        """
        
        result = {
            'transaction_id': transaction.id,
            'account_name': transaction.account_name,
            'amount': float(transaction.amount),
            'original_category': transaction.category,
            'classification_updates': {},
            'confidence_score': 0.0,
            'classification_method': 'RULE_BASED',
            'notes': []
        }
        
        # Route to specific account classifier
        if 'Revenue 4717' in transaction.account_name:
            self._classify_revenue_transaction(transaction, result)
        elif 'Bill Pay' in transaction.account_name or '5285' in transaction.account_name:
            self._classify_bill_pay_transaction(transaction, result)
        elif 'Payroll' in transaction.account_name or '4079' in transaction.account_name:
            self._classify_payroll_transaction(transaction, result)
        elif 'Capital One' in transaction.account_name:
            self._classify_capital_one_transaction(transaction, result)
        else:
            # Unknown account type
            result['classification_updates']['needs_review'] = True
            result['confidence_score'] = 0.1
            result['notes'].append(f"Unknown account type: {transaction.account_name}")
        
        # Apply common enhancements
        self._enhance_classification(transaction, result)
        
        return result

    def _classify_revenue_transaction(self, transaction: BankTransaction, result: Dict):
        """Classify Revenue 4717 transactions"""
        
        desc = transaction.description.upper()
        amount = float(transaction.amount)
        
        if amount > 0:
            # Positive amounts in Revenue = actual revenue
            result['classification_updates'].update({
                'business_category': 'REVENUE',
                'transaction_subtype': 'DEPOSIT',
                'gl_account_code': '4000',
                'is_tax_deductible': False,
                'is_classified': True
            })
            result['confidence_score'] = 0.95
            result['notes'].append("Revenue account income - high confidence")
            
            # Extract customer/entity name
            vendor_name = self._extract_vendor_name(transaction.description)
            if vendor_name:
                result['classification_updates']['merchant_name'] = vendor_name
                result['notes'].append(f"Customer identified: {vendor_name}")
        
        else:
            # Negative amounts in Revenue = transfers or fees
            
            # Check for transfer to Bill Pay (5285)
            if self._matches_patterns(desc, self.transfer_patterns['to_bill_pay']):
                result['classification_updates'].update({
                    'business_category': 'INTERNAL_TRANSFER',
                    'transaction_subtype': 'TRANSFER_OUT',
                    'is_internal_transfer': True,
                    'source_account': 'Revenue 4717',
                    'target_account': 'Bill Pay 5285',
                    'gl_account_code': '1100',  # Cash transfer
                    'is_classified': True
                })
                result['confidence_score'] = 0.92
                result['notes'].append("Internal transfer to Bill Pay account")
            
            # Check for transfer to Payroll (4079)
            elif self._matches_patterns(desc, self.transfer_patterns['to_payroll']):
                result['classification_updates'].update({
                    'business_category': 'INTERNAL_TRANSFER',
                    'transaction_subtype': 'TRANSFER_OUT',
                    'is_internal_transfer': True,
                    'source_account': 'Revenue 4717',
                    'target_account': 'Payroll 4079',
                    'gl_account_code': '1100',  # Cash transfer
                    'is_classified': True
                })
                result['confidence_score'] = 0.90
                result['notes'].append("Internal transfer to Payroll account")
            
            # Check for tax payments
            elif 'TAX' in desc or 'IRS' in desc:
                result['classification_updates'].update({
                    'business_category': 'TAX_PAYMENT',
                    'transaction_subtype': 'TAX',
                    'gl_account_code': '6300',
                    'tax_category': 'TAX_PAYMENT',
                    'is_tax_deductible': True,
                    'is_classified': True
                })
                result['confidence_score'] = 0.88
                result['notes'].append("Tax payment identified")
            
            else:
                # Other negative amounts - fees or unknown
                result['classification_updates'].update({
                    'business_category': 'BANK_FEE',
                    'transaction_subtype': 'FEE',
                    'gl_account_code': '6100',
                    'is_classified': True,
                    'needs_review': True  # Flag for manual review
                })
                result['confidence_score'] = 0.70
                result['notes'].append("Possible bank fee - needs review")

    def _classify_bill_pay_transaction(self, transaction: BankTransaction, result: Dict):
        """Classify Bill Pay 5285 transactions"""
        
        desc = transaction.description.upper()
        amount = float(transaction.amount)
        
        if amount > 0:
            # Positive amounts in Bill Pay = transfers in from Revenue
            result['classification_updates'].update({
                'business_category': 'INTERNAL_TRANSFER',
                'transaction_subtype': 'TRANSFER_IN',
                'is_internal_transfer': True,
                'source_account': 'Revenue 4717',
                'target_account': 'Bill Pay 5285',
                'gl_account_code': '1100',
                'is_classified': True
            })
            result['confidence_score'] = 0.90
            result['notes'].append("Transfer in from Revenue account")
        
        else:
            # Negative amounts in Bill Pay = vendor payments
            result['classification_updates'].update({
                'business_category': 'OPERATING_EXPENSE',
                'transaction_subtype': 'VENDOR_PAYMENT',
                'gl_account_code': '6000',
                'is_tax_deductible': True,
                'requires_receipt': True,
                'receipt_status': 'REQUIRED',
                'is_classified': True
            })
            result['confidence_score'] = 0.85
            result['notes'].append("Vendor payment - receipt required")
            
            # Extract vendor name
            vendor_name = self._extract_vendor_name(transaction.description)
            if vendor_name:
                result['classification_updates']['merchant_name'] = vendor_name
                result['notes'].append(f"Vendor identified: {vendor_name}")

    def _classify_payroll_transaction(self, transaction: BankTransaction, result: Dict):
        """Classify Payroll 4079 transactions"""
        
        desc = transaction.description.upper()
        amount = float(transaction.amount)
        
        if amount > 0:
            # Positive amounts in Payroll = transfers in from Revenue
            result['classification_updates'].update({
                'business_category': 'INTERNAL_TRANSFER',
                'transaction_subtype': 'TRANSFER_IN',
                'is_internal_transfer': True,
                'source_account': 'Revenue 4717',
                'target_account': 'Payroll 4079',
                'gl_account_code': '1100',
                'is_classified': True
            })
            result['confidence_score'] = 0.90
            result['notes'].append("Transfer in from Revenue account")
        
        else:
            # Negative amounts in Payroll = payroll expenses
            result['classification_updates'].update({
                'business_category': 'PAYROLL_EXPENSE',
                'transaction_subtype': 'PAYROLL',
                'gl_account_code': '6200',
                'tax_category': 'PAYROLL',
                'is_tax_deductible': True,
                'is_classified': True
            })
            result['confidence_score'] = 0.88
            result['notes'].append("Payroll expense")

    def _classify_capital_one_transaction(self, transaction: BankTransaction, result: Dict):
        """Classify Capital One credit card transactions"""
        
        desc = transaction.description.upper()
        amount = float(transaction.amount)
        
        # Mark as credit card transaction and calculate cycle
        result['classification_updates']['is_credit_card_transaction'] = True
        
        # Calculate Capital One cycle (cuts on 11th)
        cycle_info = self._calculate_credit_card_cycle(transaction.transaction_date)
        result['classification_updates'].update({
            'credit_card_cycle_date': cycle_info['cycle_cut_date'],
            'credit_card_due_date': cycle_info['due_date']
        })
        
        if amount > 0:
            # Positive amounts in Capital One = payments TO the card
            result['classification_updates'].update({
                'business_category': 'CREDIT_CARD_PAYMENT',
                'transaction_subtype': 'PAYMENT',
                'is_credit_card_payment': True,
                'gl_account_code': '2100',  # Credit card liability
                'is_classified': True
            })
            result['confidence_score'] = 0.92
            result['notes'].append("Credit card payment received")
        
        else:
            # Negative amounts in Capital One = business expenses
            result['classification_updates'].update({
                'business_category': 'OPERATING_EXPENSE',
                'transaction_subtype': 'PURCHASE',
                'gl_account_code': '6000',
                'is_tax_deductible': True,  # Most business expenses are
                'requires_receipt': True,
                'receipt_status': 'REQUIRED',
                'is_classified': True
            })
            result['confidence_score'] = 0.80
            result['notes'].append("Business expense on credit card - receipt required")
            
            # Extract merchant name
            vendor_name = self._extract_vendor_name(transaction.description)
            if vendor_name:
                result['classification_updates']['merchant_name'] = vendor_name

    def _enhance_classification(self, transaction: BankTransaction, result: Dict):
        """Apply common enhancements to all classifications"""
        
        # Add classification metadata
        result['classification_updates'].update({
            'classification_method': 'RULE_BASED',
            'classification_confidence': result['confidence_score'],
            'updated_at': datetime.utcnow()
        })
        
        # Extract transfer reference if present
        transfer_ref = self._extract_transfer_reference(transaction.description)
        if transfer_ref:
            result['classification_updates']['transfer_reference'] = transfer_ref

    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any of the given regex patterns"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _extract_vendor_name(self, description: str) -> Optional[str]:
        """Extract vendor/merchant name from transaction description"""
        
        for pattern in self.vendor_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                vendor = match.group(1).strip()
                # Clean up the vendor name
                vendor = re.sub(r'\s+', ' ', vendor)  # Multiple spaces to single
                vendor = vendor.strip(' .')  # Remove trailing spaces/periods
                
                if len(vendor) >= 3 and not vendor.isdigit():
                    return vendor
        
        return None

    def _extract_transfer_reference(self, description: str) -> Optional[str]:
        """Extract transfer reference ID from description"""
        
        # Look for TMID pattern
        match = re.search(r'TMID:([a-f0-9-]{8,})', description, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None

    def _calculate_credit_card_cycle(self, transaction_date: date) -> Dict:
        """Calculate Capital One credit card cycle dates (cuts on 11th)"""
        
        # Determine cycle cut date for this transaction
        if transaction_date.day >= 11:
            # This month's cycle
            cycle_cut = date(transaction_date.year, transaction_date.month, 11)
            # Next cycle cut
            if transaction_date.month == 12:
                next_cycle = date(transaction_date.year + 1, 1, 11)
            else:
                next_cycle = date(transaction_date.year, transaction_date.month + 1, 11)
        else:
            # Previous month's cycle
            if transaction_date.month == 1:
                cycle_cut = date(transaction_date.year - 1, 12, 11)
            else:
                cycle_cut = date(transaction_date.year, transaction_date.month - 1, 11)
            next_cycle = date(transaction_date.year, transaction_date.month, 11)
        
        # Due date is typically ~25 days after cycle cut
        due_date = cycle_cut + timedelta(days=25)
        
        return {
            'cycle_cut_date': cycle_cut,
            'due_date': due_date,
            'next_cycle_cut': next_cycle,
            'days_until_due': (due_date - transaction_date).days if due_date > transaction_date else 0
        }

    def classify_all_transactions(self, limit: Optional[int] = None, force_reclassify: bool = False) -> Dict:
        """
        Classify all transactions in the database
        
        Args:
            limit: Maximum number of transactions to process
            force_reclassify: If True, reclassify already classified transactions
            
        Returns:
            Dict with classification statistics
        """
        
        print("🔄 Starting transaction classification process...")
        
        # Build query
        query = BankTransaction.query
        
        if not force_reclassify:
            query = query.filter(BankTransaction.is_classified == False)
        
        if limit:
            query = query.limit(limit)
        
        transactions = query.all()
        
        if not transactions:
            return {
                'total_processed': 0,
                'message': 'No transactions found to classify'
            }
        
        print(f"📊 Found {len(transactions)} transactions to classify")
        
        # Classification statistics
        stats = {
            'total_processed': 0,
            'successful_classifications': 0,
            'failed_classifications': 0,
            'by_category': {},
            'by_account': {},
            'by_confidence': {'high': 0, 'medium': 0, 'low': 0},
            'errors': [],
            'processing_time': None
        }
        
        start_time = datetime.now()
        
        try:
            for i, transaction in enumerate(transactions, 1):
                try:
                    # Progress indicator
                    if i % 50 == 0:
                        print(f"  Processed {i}/{len(transactions)} transactions...")
                    
                    # Classify transaction
                    result = self.classify_transaction(transaction)
                    
                    # Apply updates to transaction
                    if result['classification_updates']:
                        for field, value in result['classification_updates'].items():
                            if hasattr(transaction, field):
                                setattr(transaction, field, value)
                    
                    # Update statistics
                    stats['total_processed'] += 1
                    
                    if result.get('classification_updates', {}).get('is_classified'):
                        stats['successful_classifications'] += 1
                        
                        # By category
                        category = result['classification_updates'].get('business_category', 'UNKNOWN')
                        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
                        
                        # By account
                        account = transaction.account_name
                        stats['by_account'][account] = stats['by_account'].get(account, 0) + 1
                        
                        # By confidence
                        confidence = result['confidence_score']
                        if confidence >= 0.85:
                            stats['by_confidence']['high'] += 1
                        elif confidence >= 0.70:
                            stats['by_confidence']['medium'] += 1
                        else:
                            stats['by_confidence']['low'] += 1
                    
                except Exception as e:
                    stats['failed_classifications'] += 1
                    stats['errors'].append(f"Transaction {transaction.id}: {str(e)}")
                    print(f"❌ Error classifying transaction {transaction.id}: {e}")
            
            # Commit all changes
            db.session.commit()
            print("✅ Database changes committed successfully")
            
        except Exception as e:
            db.session.rollback()
            stats['errors'].append(f"Database error: {str(e)}")
            print(f"❌ Database error: {e}")
        
        end_time = datetime.now()
        stats['processing_time'] = (end_time - start_time).total_seconds()
        
        # Calculate success rate
        if stats['total_processed'] > 0:
            stats['success_rate'] = (stats['successful_classifications'] / stats['total_processed']) * 100
        else:
            stats['success_rate'] = 0
        
        print(f"🎯 Classification completed in {stats['processing_time']:.2f} seconds")
        print(f"📈 Success rate: {stats['success_rate']:.1f}%")
        
        return stats