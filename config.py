import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Database connection monitoring
    SHOW_DB_WARNING = os.environ.get('SHOW_DB_WARNING', 'false').lower() == 'true'

    # File Mode Configuration for QA Testing
    USE_FILE_MODE = os.environ.get('USE_FILE_MODE', 'false').lower() == 'true'
    EXCEL_DATA_PATH = os.path.join(basedir, 'static', 'uploads', 'qa_data.xlsx')
    TEMP_UPLOAD_PATH = os.environ.get('TEMP_UPLOAD_PATH', '/tmp' if os.name != 'nt' else os.path.join(basedir, 'temp'))

    # Azure Configuration
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_KEY_VAULT_URL = os.environ.get('AZURE_KEY_VAULT_URL')
    APPINSIGHTS_CONNECTION_STRING = os.environ.get('APPINSIGHTS_CONNECTION_STRING')

    @classmethod
    def init_app(cls, app):
        """Initialize common configuration values."""
        pass
    
class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False

    SECRET_KEY = os.environ.get("SECRET_KEY")
    if SECRET_KEY is None:
        raise ValueError("SECRET_KEY is required")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if SQLALCHEMY_DATABASE_URI is None:
        raise ValueError("DATABASE_URL is required")

    # Security enhancements for production
    SESSION_COOKIE_SECURE = True  # HTTPS only
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session timeout

    @classmethod
    def init_app(cls, app):
        """Initialize configuration for production."""
        super().init_app(app)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
