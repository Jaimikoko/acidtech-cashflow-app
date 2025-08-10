import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Determine if running in production
IS_PRODUCTION = os.getenv('FLASK_CONFIG') == 'production' or bool(os.getenv('WEBSITE_SITE_NAME'))

# Resolve database URI
_database_uri = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
if IS_PRODUCTION and not _database_uri:
    raise ValueError('DATABASE_URL is required in production')


class Config:
    """Base configuration loaded from environment variables."""
    SECRET_KEY = os.getenv('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = _database_uri or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Database connection monitoring
    SHOW_DB_WARNING = os.getenv('SHOW_DB_WARNING', 'false').lower() == 'true'

    # File Mode Configuration for QA Testing
    USE_FILE_MODE = os.getenv('USE_FILE_MODE', 'false').lower() == 'true'
    EXCEL_DATA_PATH = os.path.join(basedir, 'static', 'uploads', 'qa_data.xlsx')
    TEMP_UPLOAD_PATH = os.getenv('TEMP_UPLOAD_PATH', '/tmp' if os.name != 'nt' else os.path.join(basedir, 'temp'))

    # Azure Configuration
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_KEY_VAULT_URL = os.getenv('AZURE_KEY_VAULT_URL')
    APPINSIGHTS_CONNECTION_STRING = os.getenv('APPINSIGHTS_CONNECTION_STRING')

    # Default cookie and security settings
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = 3600

    @classmethod
    def init_app(cls, app):
        """Initialize common configuration values."""
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = 'testing-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(Config):
    DEBUG = False

    # Security enhancements for production
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # Prevent XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour session timeout
    REMEMBER_COOKIE_SECURE = True

    # Force strong secrets and database configuration in production
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key:
            raise ValueError("Must set SECRET_KEY environment variable in production!")
        return key

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if not _database_uri:
            raise ValueError("Must set DATABASE_URL environment variable in production!")
        return _database_uri


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
