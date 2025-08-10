import os
import secrets
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Determine if running in production
IS_PRODUCTION = os.getenv('FLASK_CONFIG') == 'production' or bool(os.getenv('WEBSITE_SITE_NAME'))

# Resolve secret key with a stable development fallback
_secret_key = os.getenv('SECRET_KEY')
if IS_PRODUCTION:
    if not _secret_key:
        raise ValueError('SECRET_KEY is required in production')
else:
    _secret_key = _secret_key or secrets.token_urlsafe(32)

# Resolve database URI
_database_uri = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
if IS_PRODUCTION and not _database_uri:
    raise ValueError('DATABASE_URL is required in production')


class Config:
    SECRET_KEY = _secret_key
    SQLALCHEMY_DATABASE_URI = _database_uri
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
    SQLALCHEMY_DATABASE_URI = _database_uri
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
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    WTF_CSRF_ENABLED = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}

