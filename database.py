from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_app(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    
    # Import all models to ensure they're registered
    from models import (
        User, 
        BankTransaction, 
        Transaction, 
        PurchaseOrder, 
        PurchaseOrderItem,
        PayrollEntry,
        VCashflowDaily,
        VApOpen,
        VArOpen,
        VPoSummary
    )
    
    return db
