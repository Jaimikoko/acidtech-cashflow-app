#!/usr/bin/env python3
import os
import logging
from datetime import datetime
from flask import Flask, jsonify
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    logger.info(f"Creating Flask app with config: {config_name}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    logger.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register blueprints with error handling
    try:
        from routes.main import bp as main_bp
        app.register_blueprint(main_bp)
        logger.info("Main blueprint registered")
        
        from routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
        logger.info("Auth blueprint registered")
        
        from routes.accounts_payable import bp as ap_bp
        app.register_blueprint(ap_bp, url_prefix='/ap')
        logger.info("Accounts payable blueprint registered")
        
        from routes.accounts_receivable import bp as ar_bp
        app.register_blueprint(ar_bp, url_prefix='/ar')
        logger.info("Accounts receivable blueprint registered")
        
        from routes.purchase_orders import bp as po_bp
        app.register_blueprint(po_bp, url_prefix='/po')
        logger.info("Purchase orders blueprint registered")
        
        from routes.reports import bp as reports_bp
        app.register_blueprint(reports_bp, url_prefix='/reports')
        logger.info("Reports blueprint registered")
        
    except Exception as e:
        logger.error(f"Failed to register blueprints: {e}")
        raise
    
    # Create upload folder if it doesn't exist
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        logger.info(f"Upload folder ready: {app.config['UPLOAD_FOLDER']}")
    except Exception as e:
        logger.warning(f"Could not create upload folder: {e}")
    
    # Initialize database tables
    with app.app_context():
        try:
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
            db.engine.connect()
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
    
    return app

# Import models to ensure they're registered with SQLAlchemy
from models.user import User
from models.transaction import Transaction
from models.purchase_order import PurchaseOrder

# Create application instance
application = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Shell context processor
@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Transaction': Transaction, 'PurchaseOrder': PurchaseOrder}

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=False)