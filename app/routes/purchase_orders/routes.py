# Temporary routes file - will be migrated from original routes/purchase_orders.py
from . import purchase_orders_bp

@purchase_orders_bp.route('/')
def index():
    return "<h1>Purchase Orders - Coming Soon (Modular)</h1><p>This blueprint is being migrated to the new modular structure.</p>"