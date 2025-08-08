from datetime import datetime, date
from database import db

class PayrollEntry(db.Model):
    """
    Payroll entries - Employee payroll records derived from BankTransaction
    """
    __tablename__ = 'payroll_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Employee Information
    employee_name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(20))
    
    # Pay Period
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    pay_date = db.Column(db.Date, nullable=False)
    
    # Amounts
    gross_pay = db.Column(db.Numeric(15, 2), nullable=False)
    net_pay = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Deductions
    federal_tax = db.Column(db.Numeric(15, 2), default=0)
    state_tax = db.Column(db.Numeric(15, 2), default=0)
    social_security = db.Column(db.Numeric(15, 2), default=0)
    medicare = db.Column(db.Numeric(15, 2), default=0)
    other_deductions = db.Column(db.Numeric(15, 2), default=0)
    
    # Link to bank transaction
    bank_transaction_id = db.Column(db.Integer, db.ForeignKey('bank_transactions.id'))
    
    # Status
    status = db.Column(db.String(20), default='processed')  # 'draft', 'processed', 'cancelled'
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    bank_transaction = db.relationship('BankTransaction', backref='payroll_entry', lazy=True)
    creator = db.relationship('User', backref=db.backref('payroll_entries', lazy=True))
    
    def __repr__(self):
        return f'<PayrollEntry {self.employee_name}: ${self.net_pay}>'
    
    @property
    def total_deductions(self):
        """Calculate total deductions"""
        return (self.federal_tax + self.state_tax + self.social_security + 
                self.medicare + self.other_deductions)
    
    @classmethod
    def create_from_bank_transaction(cls, bank_transaction, employee_name=None):
        """Create a payroll entry from a bank transaction"""
        if not employee_name:
            # Try to extract employee name from description
            desc_parts = bank_transaction.description.split()
            employee_name = desc_parts[1] if len(desc_parts) > 1 else 'Unknown Employee'
        
        # Estimate pay period (assuming bi-weekly)
        pay_date = bank_transaction.transaction_date
        pay_period_end = pay_date
        pay_period_start = date(pay_date.year, pay_date.month, max(1, pay_date.day - 13))
        
        # Estimate deductions (rough approximation)
        gross_amount = abs(bank_transaction.amount)
        net_amount = gross_amount
        
        # Rough tax estimates (this would normally come from payroll system)
        federal_tax = gross_amount * 0.12  # Approximate federal tax
        state_tax = gross_amount * 0.04    # Approximate state tax
        social_security = gross_amount * 0.062  # Social Security
        medicare = gross_amount * 0.0145   # Medicare
        
        gross_pay = net_amount + federal_tax + state_tax + social_security + medicare
        
        return cls(
            employee_name=employee_name,
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            pay_date=pay_date,
            gross_pay=gross_pay,
            net_pay=net_amount,
            federal_tax=federal_tax,
            state_tax=state_tax,
            social_security=social_security,
            medicare=medicare,
            bank_transaction_id=bank_transaction.id,
            status='processed'
        )
    
    @classmethod
    def get_payroll_summary(cls, start_date=None, end_date=None):
        """Get payroll summary for a date range"""
        query = cls.query
        
        if start_date:
            query = query.filter(cls.pay_date >= start_date)
        if end_date:
            query = query.filter(cls.pay_date <= end_date)
        
        entries = query.all()
        
        total_gross = sum(entry.gross_pay for entry in entries)
        total_net = sum(entry.net_pay for entry in entries)
        total_taxes = sum(entry.federal_tax + entry.state_tax for entry in entries)
        
        return {
            'total_gross_pay': total_gross,
            'total_net_pay': total_net,
            'total_taxes': total_taxes,
            'employee_count': len(set(entry.employee_name for entry in entries)),
            'pay_period_count': len(entries)
        }