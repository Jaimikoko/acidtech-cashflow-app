#!/bin/bash

# Azure App Service startup script for Linux
echo "Starting AciTech Cash Flow Application..."

# Set working directory
cd /home/site/wwwroot

# Verify Python version and environment
echo "Python version check:"
python --version
python3 --version
which python
which python3
echo "Working directory: $(pwd)"
echo "Files in directory:"
ls -la

# Verify dependencies installation
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python init_db.py

# Test imports before starting
echo "Testing critical imports..."
python -c "import flask; print('Flask import OK')"
python -c "from wsgi import app; print('WSGI import OK')"

# Start the application with better error handling
echo "Starting application with Gunicorn..."
exec gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 4 --access-logfile=- --error-logfile=- wsgi:app