#!/usr/bin/env python3
"""
Debug startup script to diagnose Azure deployment issues
"""
import os
import sys
from datetime import datetime

def debug_startup():
    print(f"=== STARTUP DEBUG {datetime.now()} ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    print("\n=== FILES IN CURRENT DIRECTORY ===")
    try:
        for item in sorted(os.listdir('.')):
            print(f"  {item}")
    except Exception as e:
        print(f"Error listing directory: {e}")
    
    print("\n=== TESTING IMPORTS ===")
    try:
        import flask
        print(f"✓ Flask import successful: {flask.__version__}")
    except Exception as e:
        print(f"✗ Flask import failed: {e}")
    
    try:
        from wsgi import app
        print(f"✓ WSGI import successful")
        return app
    except Exception as e:
        print(f"✗ WSGI import failed: {e}")
        return None

if __name__ == "__main__":
    app = debug_startup()
    if app:
        print("✓ Ready to start Flask app")
        app.run(host='0.0.0.0', port=8000, debug=True)
    else:
        print("✗ Cannot start Flask app")
        sys.exit(1)