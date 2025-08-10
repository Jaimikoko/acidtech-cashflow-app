import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Detect production (GitHub/Azure set WEBSITE_SITE_NAME) o FLASK_CONFIG=production
IS_PRODUCTION = (os.getenv('FLASK_CONFIG') == 'production') or bool(os.getenv('WEBSITE_SITE_NAME'))

# Resolver DATABASE_URL (preferida) o SQLALCHEMY_DATABASE_URI (alias)
_database_uri = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
if IS_PRODUCTION and not _database_uri:
    raise ValueError('DATABASE_URL is required in production')


class Config:
    """Base configuration."""
    # En dev/test tiene fallback estable; en prod se sobreescribe (obligatorio)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # En dev/test usa env o SQLite local; en prod se sobreescribe (obligatorio)
    SQLALCHEMY_DATABASE_URI = _database_uri or ('sqlite:///' + os.path.join(basedir, 'app.db'))

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Monitoreo / flags
    SHOW_DB_WARNING = os.getenv('SHOW_DB_WARNING', 'false').lower() == 'true'

    # Modo archivo para QA
    USE_FILE_MODE = os.getenv('USE_FILE_MODE', 'false').lower() == 'true'
    EXCEL_DATA_PATH = os.path.join(basedir, 'static', 'uploads', 'qa_data.xlsx')
    TEMP_UPLOAD_PATH = os.getenv('TEMP_UPLOAD_PATH', '/tmp' if os.name != 'nt' else os.path.join(basedir, 'temp'))

    # Azure
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_KEY_VAULT_URL = os.getenv('AZURE_KEY_VAULT_URL')
    APPINSIGHTS_CONNECTION_STRING = os.getenv('APPINSIGHTS_CONNECTION_STRING')

    # Cookies/seguridad por defecto (dev/test)
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = 3600

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = _database_uri or ('sqlite:///' + os.path.join(basedir, 'app.db'))
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

    # En producción, ambos son obligatorios
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

    # Endurecer cookies
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}