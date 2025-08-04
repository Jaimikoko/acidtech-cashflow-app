# Temporary routes file - will be migrated from original routes/reports.py
from . import reports_bp

@reports_bp.route('/')
def index():
    return "<h1>Reports - Coming Soon (Modular)</h1><p>This blueprint is being migrated to the new modular structure.</p>"