# Temporary routes file - will be migrated from original routes/accounts_payable.py
from . import accounts_payable_bp

@accounts_payable_bp.route('/')
def index():
    return "<h1>Accounts Payable - Coming Soon (Modular)</h1><p>This blueprint is being migrated to the new modular structure.</p>"