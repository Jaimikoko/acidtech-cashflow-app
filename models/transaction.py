from datetime import datetime
from database import db

class Transaction(db.Model):
    """
    AR/AP Transactions - Future cash flows (not yet realized)
    These are projections/commitments for future payments/receipts
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # 'payable', 'receivable'
    vendor_customer = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Enhanced date tracking
    issue_date = db.Column(db.Date)                  # When PO/Invoice was created (optional for backward compatibility)
    due_date = db.Column(db.Date, nullable=False)    # When payment is due
    projected_date = db.Column(db.Date)              # When we expect payment (can differ from due_date)
    
    # Payment terms
    net_terms = db.Column(db.String(20))  # "NET15", "NET30", "NET45", "DUE_ON_RECEIPT", etc.
    discount_terms = db.Column(db.String(50))  # "2/10 NET30" (2% discount if paid in 10 days)
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  # 'pending', 'paid', 'overdue', 'cancelled'
    
    # Enhanced classification
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # "SERVICES", "SUPPLIES", "RENT", etc.
    accounting_class = db.Column(db.String(100))  # For integration with bank transactions
    
    # Reference information
    invoice_number = db.Column(db.String(50))
    po_number = db.Column(db.String(50))      # Purchase Order reference
    job_number = db.Column(db.String(50))     # Job Performance reference
    contract_number = db.Column(db.String(50)) # Contract reference
    
    # File attachments
    receipt_path = db.Column(db.String(255))
    invoice_path = db.Column(db.String(255))
    contract_path = db.Column(db.String(255))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Payment tracking
    paid_date = db.Column(db.Date)  # When actually paid
    paid_amount = db.Column(db.Numeric(15, 2))  # Actual amount paid (may differ from original)
    bank_transaction_id = db.Column(db.Integer, db.ForeignKey('bank_transactions.id'))  # Link to bank transaction
    
    creator = db.relationship('User', backref=db.backref('transactions', lazy=True))
    
    def __repr__(self):
        return f'<Transaction {self.invoice_number}: {self.amount}>'
    
    @property
    def is_overdue(self):
        from datetime import date
        return self.due_date < date.today() and self.status == 'pending'