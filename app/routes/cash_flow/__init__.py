from flask import Blueprint

cash_flow_bp = Blueprint('cash_flow', __name__)

from . import routes
from . import dashboard_routes