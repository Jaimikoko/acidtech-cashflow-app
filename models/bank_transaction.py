from datetime import datetime
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
    
    # Reference Information
    reference = db.Column(db.String(100))  # Invoice number, check number, etc.
    bank_reference = db.Column(db.String(100))  # Bank's transaction ID
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
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