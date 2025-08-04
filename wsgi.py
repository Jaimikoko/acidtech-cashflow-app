#!/usr/bin/env python3
"""
WSGI entry point for Azure App Service and other WSGI servers.
This file is the entry point for production deployments.
"""

import os
import sys
import logging

# Configure logging for Azure App Service
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Add the application directory to the Python path
    app_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(0, app_dir)
    
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Application directory: {app_dir}")
    logger.info(f"Python path: {sys.path[:3]}")
    
    # Try fallback first due to startup issues
    logger.warning("Using fallback to original app structure for stability...")
    from app import application
    app = application
    logger.info("Fallback successful - using original app structure")
    
except Exception as fallback_error:
    logger.error(f"Original app structure failed: {fallback_error}")
    
    # Try new modular structure as backup
    try:
        logger.info("Attempting new modular structure as backup...")
        from app import create_app
        
        # Create the Flask app using the factory pattern
        application = create_app(os.getenv('FLASK_CONFIG') or 'default')
        
        # Azure App Service expects a variable named 'app'
        app = application
        logger.info("Flask application loaded successfully with modular architecture")
        logger.info(f"App routes: {[rule.rule for rule in app.url_map.iter_rules()][:10]}")
        
    except Exception as e:
        logger.error(f"Both structures failed: {e}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Files in directory: {os.listdir('.')}")
        raise

if __name__ == "__main__":
    # Azure uses PORT environment variable, defaulting to 8000 for local dev
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    logger.info(f"Starting Flask app on {host}:{port}")
    app.run(host=host, port=port, debug=False)