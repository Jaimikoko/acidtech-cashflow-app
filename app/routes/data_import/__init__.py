from flask import Blueprint

# Create data import blueprint
data_import_bp = Blueprint('data_import', __name__, template_folder='../../templates')

# Import routes
from . import routes