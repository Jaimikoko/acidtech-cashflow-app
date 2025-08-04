#!/usr/bin/env python3
"""
WSGI entry point for Azure App Service and other WSGI servers.
This file is the entry point for production deployments.
"""

import os
import sys

# Add the application directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import application

# Azure App Service expects a variable named 'app'
app = application

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))