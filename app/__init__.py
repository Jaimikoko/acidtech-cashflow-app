#!/usr/bin/env python3
"""
Flask application factory for AciTech Cash Flow Management System
Modular structure with organized blueprints
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify
from flask_migrate import Migrate, upgrade
from flask_login import LoginManager
from sqlalchemy import text

# Configure basic logging for production compatibility
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name=None):
    """
    Flask application factory
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    logger.info(f"Creating Flask app with config: {config_name}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Set correct template and static folders (they're in the parent directory)
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    config['production'].init_app(app)
    
    logger.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    
    # Initialize extensions
    from database import db
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Configure user_loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        try:
            from models.user import User
            return User.query.get(int(user_id))
        except Exception as e:
            logger.error(f"Error loading user {user_id}: {e}")
            return None
    
    # Register blueprints with error handling
    try:
        # Main blueprint
        from app.routes.main import main_bp
        app.register_blueprint(main_bp)
        logger.info("Main blueprint registered")
        
        # Auth blueprint
        from app.routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        logger.info("Auth blueprint registered")
        
        # Accounts Payable blueprint
        from app.routes.accounts_payable import accounts_payable_bp
        app.register_blueprint(accounts_payable_bp, url_prefix='/accounts-payable')
        logger.info("Accounts payable blueprint registered")
        
        # Accounts Receivable blueprint
        from app.routes.accounts_receivable import accounts_receivable_bp
        app.register_blueprint(accounts_receivable_bp, url_prefix='/accounts-receivable')
        logger.info("Accounts receivable blueprint registered")
        
        # Purchase Orders blueprint
        from app.routes.purchase_orders import purchase_orders_bp
        app.register_blueprint(purchase_orders_bp, url_prefix='/purchase-orders')
        logger.info("Purchase orders blueprint registered")
        
        # Reports blueprint
        from app.routes.reports import reports_bp
        app.register_blueprint(reports_bp, url_prefix='/reports')
        logger.info("Reports blueprint registered")
        
        # Data Import blueprint
        from app.routes.data_import import data_import_bp
        app.register_blueprint(data_import_bp, url_prefix='/data-import')
        logger.info("Data Import blueprint registered")
        
        # Cash Flow blueprint
        from app.routes.cash_flow import cash_flow_bp
        app.register_blueprint(cash_flow_bp, url_prefix='/cash-flow')
        logger.info("Cash Flow blueprint registered")
        
    except Exception as e:
        logger.error(f"Failed to register blueprints: {e}")
        # Don't raise here, let the app try to start with available blueprints
        logger.warning("Some blueprints may not be available")
    
    # Create upload folder if it doesn't exist
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        logger.info(f"Upload folder ready: {app.config['UPLOAD_FOLDER']}")
    except Exception as e:
        logger.warning(f"Could not create upload folder: {e}")
    
    # Initialize database tables
    with app.app_context():
        try:
            if app.config.get('ENV') == 'production':
                upgrade()
                logger.info("Database migrations applied")
            else:
                db.create_all()
                logger.info("Database tables created/verified")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            # Don't raise here, let the app start anyway
    
    # Health check endpoint for Azure App Service
    @app.route('/health')
    def health():
        try:
            # Test database connection
            from database import db
            with db.engine.connect() as conn:
                conn.execute(text('SELECT 1'))
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 503
    
    # Error handlers
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"Page not found: {error}")
        return jsonify({'error': 'Page not found'}), 404
    
    # Custom Jinja2 filters for number formatting
    @app.template_filter('currency')
    def currency_format(value):
        """Format numbers as currency with accounting style"""
        try:
            if value is None:
                return "$0.00"
            
            # Convert to float if needed
            if isinstance(value, str):
                value = float(value.replace(',', '').replace('$', ''))
            
            value = float(value)
            
            # Format with commas and 2 decimal places
            if value >= 0:
                return "${:,.2f}".format(value)
            else:
                # Negative numbers in parentheses (accounting style)
                return "(${:,.2f})".format(abs(value))
                
        except (ValueError, TypeError):
            return "$0.00"
    
    @app.template_filter('accounting')
    def accounting_format(value):
        """Format numbers in accounting style (negatives in parentheses)"""
        try:
            if value is None:
                return "0.00"
            
            if isinstance(value, str):
                value = float(value.replace(',', '').replace('$', ''))
            
            value = float(value)
            
            if value >= 0:
                return "{:,.2f}".format(value)
            else:
                return "({:,.2f})".format(abs(value))
                
        except (ValueError, TypeError):
            return "0.00"
    
    return app

# Import models to ensure they're registered with SQLAlchemy
try:
    from models.user import User
    from models.transaction import Transaction
    from models.purchase_order import PurchaseOrder
    from models.bank_transaction import BankTransaction
    from models.payroll import PayrollEntry
    logger.info("Models imported successfully")
except ImportError as e:
    logger.warning(f"Could not import some models: {e}")