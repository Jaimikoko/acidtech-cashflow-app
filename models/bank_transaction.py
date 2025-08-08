from datetime import datetime, date
from database import db

class BankTransaction(db.Model):
    """
    Bank transactions - Posted/Realized transactions from bank statements
    These are completed transactions that already happened (not projections)
    """
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Bank Account Information
    account_name = db.Column(db.String(100), nullable=False)  # "Income 4717", "Bill Pay 4091", etc.
    account_type = db.Column(db.String(50), nullable=False)   # "CHECKING", "CREDIT_CARD", "SAVINGS"
    
    # Transaction Details
    transaction_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)  # Positive for income, negative for expenses
    
    # Transaction Type
    transaction_type = db.Column(db.String(20), nullable=False)  # "CREDIT", "DEBIT"
    
    # Classification
    category = db.Column(db.String(100))  # "INCOME", "RENT", "PAYROLL", "FUEL", etc.
    accounting_class = db.Column(db.String(100))  # "Revenue", "Gas & Fuel", "Payroll & Benefits", etc.
    
    # === NEW FIELDS FOR ENHANCED CLASSIFICATION ===
    
    # Enhanced Transaction Classification
    transaction_subtype = db.Column(db.String(50))  # "DEPOSIT", "PAYMENT", "FEE", "INTEREST", "TRANSFER"
    business_category = db.Column(db.String(100))   # "REVENUE", "OPERATING_EXPENSE", "CAPITAL_EXPENSE", "TAX"
    gl_account_code = db.Column(db.String(20))      # "4000", "6000", etc. - Chart of Accounts reference
    
    # Internal Transfer Fields
    is_internal_transfer = db.Column(db.Boolean, default=False)
    source_account = db.Column(db.String(100))      # Source account for transfers
    target_account = db.Column(db.String(100))      # Target account for transfers
    transfer_reference = db.Column(db.String(100))  # Unique ID to link transfer pair
    
    # Credit Card Specific Fields
    is_credit_card_transaction = db.Column(db.Boolean, default=False)
    credit_card_cycle_date = db.Column(db.Date)     # Cycle cut date (11th of each month for Capital One)
    credit_card_due_date = db.Column(db.Date)       # Payment due date
    is_credit_card_payment = db.Column(db.Boolean, default=False)  # Payment TO the credit card
    
    # Enhanced Merchant/Vendor Information
    merchant_name = db.Column(db.String(200))       # Clean merchant name
    merchant_category = db.Column(db.String(100))   # "RESTAURANT", "GAS_STATION", "OFFICE_SUPPLIES", etc.
    vendor_tax_id = db.Column(db.String(20))        # For 1099 tracking
    
    # Tax and Compliance
    is_tax_deductible = db.Column(db.Boolean, default=False)
    tax_category = db.Column(db.String(50))         # "MEALS", "TRAVEL", "OFFICE", "VEHICLE"
    requires_receipt = db.Column(db.Boolean, default=False)
    receipt_status = db.Column(db.String(20), default='NOT_REQUIRED')  # "REQUIRED", "RECEIVED", "MISSING"
    
    # Classification Control
    is_classified = db.Column(db.Boolean, default=False)
    classification_confidence = db.Column(db.Numeric(3, 2))  # 0.00 to 1.00 confidence score
    classification_method = db.Column(db.String(20))         # "MANUAL", "RULE_BASED", "ML", "IMPORTED"
    needs_review = db.Column(db.Boolean, default=False)
    review_notes = db.Column(db.Text)
    
    # Enhanced Reconciliation
    is_reconciled = db.Column(db.Boolean, default=False)
    reconciliation_date = db.Column(db.Date)
    reconciliation_batch_id = db.Column(db.String(50))
    
    # Reference Information
    reference = db.Column(db.String(100))  # Invoice number, check number, etc.
    bank_reference = db.Column(db.String(100))  # Bank's transaction ID
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Import tracking
    import_batch_id = db.Column(db.String(50))  # Track which import batch this came from
    
    def __repr__(self):
        return f'<BankTransaction {self.account_name}: {self.description} - ${self.amount}>'
    
    @property
    def is_income(self):
        """Check if this is an income transaction"""
        return self.amount > 0
    
    @property
    def is_expense(self):
        """Check if this is an expense transaction"""
        return self.amount < 0
    
    # === NEW CLASSIFICATION METHODS ===
    
    @property
    def is_capital_one(self):
        """Check if this is a Capital One credit card transaction"""
        return 'Capital One' in self.account_name or self.is_credit_card_transaction
    
    @property
    def needs_classification(self):
        """Check if transaction needs manual classification"""
        return not self.is_classified or self.needs_review
    
    @property
    def classification_status(self):
        """Get human-readable classification status"""
        if not self.is_classified:
            return "UNCLASSIFIED"
        elif self.needs_review:
            return "NEEDS_REVIEW"
        elif self.classification_confidence and self.classification_confidence < 0.8:
            return "LOW_CONFIDENCE"
        else:
            return "CLASSIFIED"
    
    def get_credit_card_cycle_info(self):
        """Get credit card cycle information for Capital One (cuts on 11th)"""
        if not self.is_capital_one:
            return None
            
        from datetime import date, timedelta
        
        # Capital One cuts on 11th of each month
        current_date = self.transaction_date
        
        # Determine cycle cut date for this transaction
        if current_date.day >= 11:
            # This month's cycle
            cycle_cut = date(current_date.year, current_date.month, 11)
            # Next cycle cut
            if current_date.month == 12:
                next_cycle = date(current_date.year + 1, 1, 11)
            else:
                next_cycle = date(current_date.year, current_date.month + 1, 11)
        else:
            # Previous month's cycle
            if current_date.month == 1:
                cycle_cut = date(current_date.year - 1, 12, 11)
            else:
                cycle_cut = date(current_date.year, current_date.month - 1, 11)
            next_cycle = date(current_date.year, current_date.month, 11)
        
        # Due date is typically ~25 days after cycle cut
        due_date = cycle_cut + timedelta(days=25)
        
        return {
            'cycle_cut_date': cycle_cut,
            'due_date': due_date,
            'next_cycle_cut': next_cycle,
            'days_until_due': (due_date - current_date).days if due_date > current_date else 0
        }
    
    def auto_classify_by_rules(self):
        """Auto-classify transaction based on business rules"""
        
        # Rule-based classification logic
        classification_updates = {
            'classification_method': 'RULE_BASED',
            'classification_confidence': 0.9
        }
        
        # Account-based rules
        if 'Revenue 4717' in self.account_name:
            if self.is_income:
                classification_updates.update({
                    'business_category': 'REVENUE',
                    'transaction_subtype': 'DEPOSIT',
                    'gl_account_code': '4000',
                    'is_tax_deductible': False
                })
            else:
                # Negative amount in revenue account might be a fee or return
                classification_updates.update({
                    'business_category': 'OPERATING_EXPENSE',
                    'transaction_subtype': 'FEE',
                    'gl_account_code': '6100'
                })
        
        elif 'Bill Pay' in self.account_name:
            classification_updates.update({
                'business_category': 'OPERATING_EXPENSE',
                'transaction_subtype': 'PAYMENT',
                'gl_account_code': '6000',
                'is_tax_deductible': True  # Most business expenses are deductible
            })
        
        elif 'Payroll' in self.account_name:
            classification_updates.update({
                'business_category': 'OPERATING_EXPENSE',
                'transaction_subtype': 'PAYROLL',
                'gl_account_code': '6200',
                'tax_category': 'PAYROLL',
                'is_tax_deductible': True
            })
        
        elif 'Capital One' in self.account_name:
            self.is_credit_card_transaction = True
            cycle_info = self.get_credit_card_cycle_info()
            if cycle_info:
                self.credit_card_cycle_date = cycle_info['cycle_cut_date']
                self.credit_card_due_date = cycle_info['due_date']
            
            if self.is_income:
                # Credit card payment or refund
                classification_updates.update({
                    'business_category': 'CREDIT_CARD_PAYMENT',
                    'transaction_subtype': 'PAYMENT',
                    'is_credit_card_payment': True
                })
            else:
                # Credit card purchase
                classification_updates.update({
                    'business_category': 'OPERATING_EXPENSE',
                    'transaction_subtype': 'PURCHASE',
                    'gl_account_code': '6000',
                    'requires_receipt': True,
                    'receipt_status': 'REQUIRED'
                })
        
        # Update fields
        for field, value in classification_updates.items():
            setattr(self, field, value)
        
        self.is_classified = True
        return classification_updates
    
    @classmethod
    def get_by_account(cls, account_name, start_date=None, end_date=None):
        """Get transactions for a specific bank account"""
        query = cls.query.filter_by(account_name=account_name)
        
        if start_date:
            query = query.filter(cls.transaction_date >= start_date)
        if end_date:
            query = query.filter(cls.transaction_date <= end_date)
            
        return query.order_by(cls.transaction_date.desc()).all()
    
    @classmethod
    def get_cash_flow_summary(cls, start_date=None, end_date=None):
        """Get cash flow summary across all accounts"""
        query = cls.query
        
        if start_date:
            query = query.filter(cls.transaction_date >= start_date)
        if end_date:
            query = query.filter(cls.transaction_date <= end_date)
        
        transactions = query.all()
        
        total_income = sum(t.amount for t in transactions if t.is_income)
        total_expenses = sum(abs(t.amount) for t in transactions if t.is_expense)
        net_cash_flow = total_income - total_expenses
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_cash_flow': net_cash_flow,
            'transaction_count': len(transactions)
        }
    
    @classmethod
    def get_unclassified_transactions(cls, limit=None):
        """Get transactions that need classification"""
        query = cls.query.filter(
            (cls.is_classified == False) | (cls.needs_review == True)
        ).order_by(cls.transaction_date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_by_business_category(cls, category, start_date=None, end_date=None):
        """Get transactions by business category"""
        query = cls.query.filter_by(business_category=category)
        
        if start_date:
            query = query.filter(cls.transaction_date >= start_date)
        if end_date:
            query = query.filter(cls.transaction_date <= end_date)
        
        return query.order_by(cls.transaction_date.desc()).all()
    
    @classmethod
    def get_tax_deductible_expenses(cls, start_date=None, end_date=None):
        """Get tax-deductible expense transactions"""
        query = cls.query.filter(
            cls.is_tax_deductible == True,
            cls.amount < 0  # Expenses are negative
        )
        
        if start_date:
            query = query.filter(cls.transaction_date >= start_date)
        if end_date:
            query = query.filter(cls.transaction_date <= end_date)
        
        return query.order_by(cls.transaction_date.desc()).all()
    
    @classmethod
    def get_credit_card_summary(cls, start_date=None, end_date=None):
        """Get Capital One credit card transaction summary"""
        query = cls.query.filter(cls.is_credit_card_transaction == True)
        
        if start_date:
            query = query.filter(cls.transaction_date >= start_date)
        if end_date:
            query = query.filter(cls.transaction_date <= end_date)
        
        transactions = query.all()
        
        purchases = [t for t in transactions if t.amount < 0]  # Negative = purchases
        payments = [t for t in transactions if t.amount > 0]   # Positive = payments
        
        total_purchases = sum(abs(t.amount) for t in purchases)
        total_payments = sum(t.amount for t in payments)
        
        return {
            'total_purchases': total_purchases,
            'total_payments': total_payments,
            'net_balance_change': total_payments - total_purchases,
            'purchase_count': len(purchases),
            'payment_count': len(payments),
            'transactions_needing_receipts': len([t for t in purchases if t.receipt_status == 'REQUIRED'])
        }
    
    @classmethod 
    def get_classification_summary(cls):
        """Get overview of classification status"""
        from sqlalchemy import func
        
        total_count = cls.query.count()
        classified_count = cls.query.filter(cls.is_classified == True).count()
        needs_review_count = cls.query.filter(cls.needs_review == True).count()
        
        # Count by classification method
        method_counts = db.session.query(
            cls.classification_method,
            func.count(cls.id)
        ).filter(cls.is_classified == True).group_by(cls.classification_method).all()
        
        # Count by business category
        category_counts = db.session.query(
            cls.business_category,
            func.count(cls.id)
        ).filter(cls.business_category != None).group_by(cls.business_category).all()
        
        return {
            'total_transactions': total_count,
            'classified_transactions': classified_count,
            'unclassified_transactions': total_count - classified_count,
            'needs_review': needs_review_count,
            'classification_percentage': (classified_count / total_count * 100) if total_count > 0 else 0,
            'method_breakdown': dict(method_counts),
            'category_breakdown': dict(category_counts)
        }