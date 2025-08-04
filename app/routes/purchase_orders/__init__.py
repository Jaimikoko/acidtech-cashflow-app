from flask import Blueprint

# Create purchase orders blueprint
purchase_orders_bp = Blueprint('purchase_orders', __name__, template_folder='../../templates')

# Import routes
from . import routes