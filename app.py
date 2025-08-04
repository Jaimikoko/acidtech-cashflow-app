#!/usr/bin/env python3
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Register blueprints
    from routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from routes.accounts_payable import bp as ap_bp
    app.register_blueprint(ap_bp, url_prefix='/ap')
    
    from routes.accounts_receivable import bp as ar_bp
    app.register_blueprint(ar_bp, url_prefix='/ar')
    
    from routes.purchase_orders import bp as po_bp
    app.register_blueprint(po_bp, url_prefix='/po')
    
    from routes.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

# Create application instance first to avoid circular imports
application = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Import models after app creation to ensure they're registered with SQLAlchemy
with application.app_context():
    from models.user import User
    from models.transaction import Transaction
    from models.purchase_order import PurchaseOrder

# Shell context processor
@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Transaction': Transaction, 'PurchaseOrder': PurchaseOrder}

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))