#!/usr/bin/env python3
"""
Startup script for Azure App Service - Improved Version
This provides diagnostics and can serve as a gunicorn wrapper if needed.
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [STARTUP] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install critical Python packages before starting the app."""
    logger.info("=== INSTALLING REQUIRED DEPENDENCIES ===")
    cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "Flask-WTF",
        "WTForms",
        "email-validator",
    ]
    try:
        subprocess.check_call(cmd)
        logger.info("✅ Dependency installation complete")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Dependency installation failed: {e}")
        sys.exit(1)

def diagnose_environment():
    """Diagnose the environment and log critical information."""
    logger.info("=== AZURE APP SERVICE STARTUP DIAGNOSTICS ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Files in working directory: {os.listdir('.')}")
    
    # Check critical environment variables
    critical_env_vars = ['DATABASE_URL', 'SECRET_KEY', 'FLASK_CONFIG', 'PORT']
    for var in critical_env_vars:
        value = os.environ.get(var, 'NOT SET')
        # Mask sensitive values
        if 'SECRET' in var or 'PASSWORD' in var:
            value = '***MASKED***' if value != 'NOT SET' else 'NOT SET'
        logger.info(f"Environment {var}: {value}")
    
    # Check Python path
    logger.info(f"Python path (first 5 entries): {sys.path[:5]}")
    
    return True

def test_imports():
    """Test critical imports and log results."""
    logger.info("=== TESTING CRITICAL IMPORTS ===")
    
    try:
        from flask import Flask
        logger.info("✅ Flask imported successfully")
    except ImportError as e:
        logger.error(f"❌ Flask import failed: {e}")
        return False

    try:
        from flask_sqlalchemy import SQLAlchemy
        logger.info("✅ Flask-SQLAlchemy imported successfully")
    except ImportError as e:
        logger.error(f"❌ Flask-SQLAlchemy import failed: {e}")
        return False

    try:
        from wsgi import app
        logger.info("✅ WSGI app imported successfully")
        logger.info(f"App type: {type(app)}")
        return app
    except ImportError as e:
        logger.error(f"❌ WSGI app import failed: {e}")
        return False

def test_database_connection(app):
    """Test database connection if possible."""
    logger.info("=== TESTING DATABASE CONNECTION ===")
    
    try:
        with app.app_context():
            from database import db
            db.engine.connect()
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        # This is not critical for startup, just log and continue
        return False

def run_gunicorn():
    """Run gunicorn with production-ready settings."""
    logger.info("=== STARTING GUNICORN SERVER ===")

    port = os.environ.get("PORT", "5001")

    cmd = [
        "gunicorn",
        "--bind", f"0.0.0.0:{port}",
        "--timeout", "600",
        "wsgi:app",
    ]

    logger.info(f"Gunicorn command: {' '.join(cmd)}")

    try:
        # Use exec to replace the current process
        os.execvp("gunicorn", cmd)
    except Exception as e:
        logger.error(f"Failed to start gunicorn: {e}")
        sys.exit(1)

def main():
    """Main startup function."""
    try:
        # Step 0: Ensure required packages are installed
        install_dependencies()

        # Step 1: Diagnose environment
        diagnose_environment()
        
        # Step 2: Test imports
        app = test_imports()
        if not app:
            logger.error("Critical import failure - cannot continue")
            sys.exit(1)
        
        # Step 3: Test database (non-critical)
        test_database_connection(app)
        
        # Step 4: Start gunicorn
        logger.info("All diagnostics completed - starting gunicorn server")
        run_gunicorn()
        
    except Exception as e:
        logger.error(f"Startup failed with exception: {e}")
        logger.exception("Full stacktrace:")
        sys.exit(1)

if __name__ == "__main__":
    main()

