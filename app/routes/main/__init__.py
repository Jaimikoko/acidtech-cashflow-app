from flask import Blueprint

# Create main blueprint
main_bp = Blueprint('main', __name__, template_folder='../../templates')

# Import routes
from . import routes