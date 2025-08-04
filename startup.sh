#!/bin/bash

# Azure App Service startup script for Linux
echo "Starting AciTech Cash Flow Application..."

# Verify Python version
echo "Python version check:"
python --version
python3 --version
which python
which python3

# Install dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting application with Gunicorn..."
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 4 wsgi:app