from flask import Blueprint

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../../templates')

# Import routes
from . import routes