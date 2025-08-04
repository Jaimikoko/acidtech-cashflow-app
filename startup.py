#!/usr/bin/env python3
"""
Startup script for Azure App Service.
This helps diagnose startup issues and ensures proper application initialization.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting application initialization...")
        
        # Check environment
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Python path: {sys.path}")
        
        # Check if all required modules can be imported
        logger.info("Checking imports...")
        from flask import Flask
        logger.info("Flask imported successfully")
        
        from flask_sqlalchemy import SQLAlchemy
        logger.info("Flask-SQLAlchemy imported successfully")
        
        # Import application
        logger.info("Importing application...")
        from wsgi import app
        logger.info("Application imported successfully")
        
        # Test database connection
        with app.app_context():
            from database import db
            try:
                db.engine.connect()
                logger.info("Database connection successful")
            except Exception as e:
                logger.error(f"Database connection failed: {e}")
        
        logger.info("Application startup completed successfully")
        return app
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise

if __name__ == "__main__":
    app = main()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)