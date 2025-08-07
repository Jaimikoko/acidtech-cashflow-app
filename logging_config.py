#!/usr/bin/env python3
"""
Comprehensive logging configuration for AciTech Cash Flow Management System
Supports both development and production environments with proper handlers
"""

import os
import logging
import logging.handlers
from datetime import datetime


def setup_logging(app=None, config_name='development'):
    """
    Setup comprehensive logging configuration
    
    Args:
        app: Flask application instance (optional)
        config_name: Configuration environment ('development', 'production')
    """
    
    # Base logging configuration
    log_level = logging.DEBUG if config_name == 'development' else logging.INFO
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Define log file paths
    app_log_file = os.path.join(logs_dir, 'acidtech_app.log')
    error_log_file = os.path.join(logs_dir, 'acidtech_errors.log')
    
    # Clear existing handlers to avoid duplication
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler for all environments
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    
    # File handler for application logs
    file_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    
    # Error file handler for errors and critical issues
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    
    # Flask application logger
    app_logger = logging.getLogger('acidtech')
    app_logger.setLevel(log_level)
    
    # Database logger
    db_logger = logging.getLogger('sqlalchemy.engine')
    db_logger.setLevel(logging.WARNING if config_name == 'production' else logging.INFO)
    
    # Werkzeug logger (Flask development server)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING if config_name == 'production' else logging.INFO)
    
    # Configure Flask app logger if provided
    if app:
        app.logger.handlers.clear()
        app.logger.addHandler(console_handler)
        app.logger.addHandler(file_handler)
        app.logger.addHandler(error_handler)
        app.logger.setLevel(log_level)
        app.logger.propagate = False
    
    # Log the logging configuration
    logger = logging.getLogger('acidtech.logging')
    logger.info(f"Logging configured for environment: {config_name}")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    logger.info(f"Application logs: {app_log_file}")
    logger.info(f"Error logs: {error_log_file}")
    logger.info(f"Console logging: Enabled")
    
    return app_logger


def get_logger(name):
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f'acidtech.{name}')


class DatabaseLogHandler(logging.Handler):
    """
    Custom handler to log critical errors to database
    (Optional - can be implemented later if needed)
    """
    
    def __init__(self):
        super().__init__()
        self.setLevel(logging.ERROR)
    
    def emit(self, record):
        # This could be implemented to store critical errors in database
        # For now, we'll just pass
        pass


# Utility functions for structured logging

def log_request_info(request, logger):
    """Log incoming request information"""
    logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")
    if request.form:
        # Don't log sensitive data like passwords
        safe_form = {k: v for k, v in request.form.items() if 'password' not in k.lower()}
        logger.debug(f"Form data: {safe_form}")


def log_user_action(user_id, action, details=None, logger=None):
    """Log user actions for audit trail"""
    if not logger:
        logger = get_logger('user_actions')
    
    message = f"User {user_id} performed action: {action}"
    if details:
        message += f" - Details: {details}"
    
    logger.info(message)


def log_error_with_context(error, context=None, logger=None):
    """Log errors with additional context"""
    if not logger:
        logger = get_logger('errors')
    
    error_msg = f"Error occurred: {str(error)}"
    if context:
        error_msg += f" - Context: {context}"
    
    logger.error(error_msg, exc_info=True)


def log_performance_metric(operation, duration, details=None, logger=None):
    """Log performance metrics"""
    if not logger:
        logger = get_logger('performance')
    
    message = f"Operation '{operation}' took {duration:.3f}s"
    if details:
        message += f" - {details}"
    
    logger.info(message)


# Environment-specific configurations
LOGGING_CONFIG = {
    'development': {
        'level': logging.DEBUG,
        'console_level': logging.DEBUG,
        'file_level': logging.DEBUG,
        'sql_logging': True
    },
    'production': {
        'level': logging.INFO,
        'console_level': logging.INFO,
        'file_level': logging.INFO,
        'sql_logging': False
    }
}