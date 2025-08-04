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
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    logger.info("Importing Flask application...")
    from app import application
    
    # Azure App Service expects a variable named 'app'
    app = application
    logger.info("Flask application loaded successfully")
    
except Exception as e:
    logger.error(f"Failed to load Flask application: {e}")
    raise

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), debug=False)