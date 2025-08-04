from flask import Blueprint

# Create reports blueprint
reports_bp = Blueprint('reports', __name__, template_folder='../../templates')

# Import routes
from . import routes