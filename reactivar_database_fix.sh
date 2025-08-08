#!/bin/bash
echo "🔄 Reactivando fix: Update database configuration to support Azure environment variables"
echo "📋 Deploy #83: Commit 0714833 (previamente cancelado)"
echo ""

# Verificar que estamos en bd1eb36
current_commit=$(git rev-parse --short HEAD)
if [ "$current_commit" != "bd1eb36" ]; then
    echo "❌ Error: No estás en el commit correcto"
    echo "   Actual: $current_commit"
    echo "   Esperado: bd1eb36"
    echo ""
    echo "Ejecuta: git reset --hard bd1eb36"
    exit 1
fi

echo "✅ Commit actual confirmado: bd1eb36"
echo ""

# 1. Actualizar config.py
echo "📝 Actualizando config.py..."
cat > config.py << 'EOL'
import os
import logging
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

logger = logging.getLogger(__name__)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-acidtech-2024-change-in-production'
    
    # Database Configuration - Support both formats
    @staticmethod
    def get_database_uri():
        # First check for full DATABASE_URL (for local dev or other platforms)
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            logger.info("Using DATABASE_URL environment variable")
            return database_url
        
        # Then check for Azure individual variables
        azure_server = os.environ.get('AZURE_SQL_SERVER')
        azure_database = os.environ.get('AZURE_SQL_DATABASE') 
        azure_username = os.environ.get('AZURE_SQL_USERNAME')
        azure_password = os.environ.get('AZURE_SQL_PASSWORD')
        
        logger.info(f"Azure variables - Server: {bool(azure_server)}, DB: {bool(azure_database)}, User: {bool(azure_username)}, Pass: {bool(azure_password)}")
        
        if all([azure_server, azure_database, azure_username, azure_password]):
            # Build connection string for Azure SQL Server
            connection_string = f"mssql+pyodbc://{azure_username}:{azure_password}@{azure_server}/{azure_database}?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
            logger.info(f"Using Azure SQL Server: {azure_server}/{azure_database}")
            return connection_string
        
        # Fallback to SQLite for local development
        logger.info("Falling back to SQLite for local development")
        return 'sqlite:///' + os.path.join(basedir, 'app.db')
    
    SQLALCHEMY_DATABASE_URI = get_database_uri.__func__()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # File Mode Configuration for QA Testing
    USE_FILE_MODE = os.environ.get('USE_FILE_MODE', 'false').lower() == 'true'
    EXCEL_DATA_PATH = os.path.join(basedir, 'static', 'uploads', 'qa_data.xlsx')
    TEMP_UPLOAD_PATH = os.environ.get('TEMP_UPLOAD_PATH', '/tmp' if os.name != 'nt' else os.path.join(basedir, 'temp'))
    
    # Azure Configuration
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_KEY_VAULT_URL = os.environ.get('AZURE_KEY_VAULT_URL')
    APPINSIGHTS_CONNECTION_STRING = os.environ.get('APPINSIGHTS_CONNECTION_STRING')
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
EOL

# 2. Actualizar requirements.txt
echo "📝 Actualizando requirements.txt..."
cat > requirements.txt << 'EOL'
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-Login==0.6.3
Flask-WTF==1.2.1
WTForms==3.1.0
Werkzeug==3.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
pandas==2.1.4
openpyxl==3.1.2
pyodbc==5.1.0
pymssql==2.3.1
EOL

echo "✅ Archivos actualizados"
echo ""

# 3. Crear el commit (recrear 0714833)
echo "📦 Creando commit 0714833..."
git add .
git commit -m "fix: Update database configuration to support Azure environment variables

- Add support for Azure SQL Server individual environment variables:
  * AZURE_SQL_SERVER
  * AZURE_SQL_DATABASE  
  * AZURE_SQL_USERNAME
  * AZURE_SQL_PASSWORD
- Add SQL Server dependencies (pyodbc, pymssql) to requirements.txt
- Build proper connection string with encryption and security settings
- Maintain backward compatibility with DATABASE_URL
- Add logging to diagnose database connection issues
- Fallback to SQLite for local development

This should resolve the 503 error caused by database connectivity issues.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

new_commit=$(git rev-parse --short HEAD)
echo "✅ Nuevo commit creado: $new_commit"
echo ""

echo "🎯 Variables que Azure debe tener configuradas:"
echo "   AZURE_SQL_SERVER=acidtech-prod-sqlserver.database.windows.net"
echo "   AZURE_SQL_DATABASE=acidtech-prod-db"
echo "   AZURE_SQL_USERNAME=acidtechadmin@acidtech-prod-sqlserver"
echo "   AZURE_SQL_PASSWORD=[tu contraseña real]"
echo ""

echo "🚀 PARA HACER PUSH MANUALMENTE CUANDO TERMINE EL DEPLOYMENT:"
echo "   git push origin main"
echo ""

echo "⏰ Después del push, Azure tardará 3-5 minutos en:"
echo "   1. Instalar dependencias SQL Server (pyodbc, pymssql)"
echo "   2. Reiniciar la aplicación"
echo "   3. Conectar a la base de datos SQL Server"
echo ""

echo "🔍 Para monitorear el deployment:"
echo "   az webapp log tail --name acidtech-prod-app --resource-group acidtech-prod-rg"
echo ""

echo "✅ Script completado. El fix está listo para push manual."