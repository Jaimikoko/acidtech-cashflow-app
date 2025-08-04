from flask import Blueprint

# Create accounts receivable blueprint
accounts_receivable_bp = Blueprint('accounts_receivable', __name__, template_folder='../../templates')

# Import routes
from . import routes