# Temporary routes file - will be migrated from original routes/accounts_receivable.py
from . import accounts_receivable_bp

@accounts_receivable_bp.route('/')
def index():
    return "<h1>Accounts Receivable - Coming Soon (Modular)</h1><p>This blueprint is being migrated to the new modular structure.</p>"