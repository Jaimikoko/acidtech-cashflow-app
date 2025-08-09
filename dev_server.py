#!/usr/bin/env python3
"""
Development Server for AcidTech Cash Flow Application
Single entry point for local development

Usage:
    python dev_server.py

Environment:
    - Uses development configuration
    - Enables debug mode
    - Runs on localhost:5001 by default (configurable via DEV_SERVER_PORT)
"""

import os
import sys
from pathlib import Path


# Port configuration (allows override via DEV_SERVER_PORT environment variable)
PORT = int(os.environ.get("DEV_SERVER_PORT", 5001))

# Ensure we're in the correct directory
if __name__ == "__main__":
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_CONFIG'] = 'development'
    
    try:
        from app import create_app
        
        # Create Flask application
        app = create_app('development')
        
        print("=" * 60)
        print("🚀 AcidTech Cash Flow - Development Server")
        print("=" * 60)
        print(f"📁 Working Directory: {current_dir}")
        print(f"🌍 Environment: Development")
        print(f"🔧 Debug Mode: Disabled")
        print(f"🌐 URL: http://localhost:{PORT}")
        print(f"📊 Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
        print("=" * 60)
        print("📝 Available routes:")
        
        # Show main routes
        main_routes = [
            "/ - Login/Main page",
            "/dashboard - Main dashboard",
            "/cash-flow - Cash flow analysis",
            "/accounts-receivable - AR management",
            "/accounts-payable - AP management", 
            "/purchase-orders - PO management",
            "/reports - Financial reports"
        ]
        
        for route in main_routes:
            print(f"   • {route}")
        
        print("=" * 60)
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Run development server
        app.run(
            host='0.0.0.0',  # Allow external connections
            port=PORT,  # Custom port to avoid conflicts
            debug=False,
            use_reloader=True,
            use_debugger=False
        )
        
    except ImportError as e:
        print(f"❌ Error importing Flask app: {e}")
        print("💡 Make sure you've installed all dependencies with: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
