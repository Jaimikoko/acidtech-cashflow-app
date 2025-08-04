from flask import Blueprint

# Create accounts payable blueprint
accounts_payable_bp = Blueprint('accounts_payable', __name__, template_folder='../../templates')

# Import routes
from . import routes