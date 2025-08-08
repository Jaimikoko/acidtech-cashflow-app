#!/usr/bin/env python3
"""
Production Readiness Check for AcidTech Cash Flow Application
Validates that the application is properly configured for production deployment

Usage:
    python production_check.py
"""

import os
import sys
from urllib.parse import urlparse

def check_environment_variables():
    """Check required environment variables"""
    print("🔍 Checking Environment Variables...")
    
    required_vars = {
        'SECRET_KEY': 'Flask secret key for sessions',
        'DATABASE_URL': 'Database connection string',
        'FLASK_CONFIG': 'Should be "production"'
    }
    
    optional_vars = {
        'AZURE_STORAGE_CONNECTION_STRING': 'Azure Storage for file uploads',
        'APPINSIGHTS_CONNECTION_STRING': 'Application Insights telemetry',
        'AZURE_KEY_VAULT_URL': 'Azure Key Vault for secrets'
    }
    
    issues = []
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if not value:
            issues.append(f"❌ Missing required variable: {var} ({description})")
        elif var == 'SECRET_KEY':
            if value == 'dev-secret-key-acidtech-2024-change-in-production':
                issues.append(f"⚠️  {var} is using default development value - change in production!")
            elif len(value) < 32:
                issues.append(f"⚠️  {var} should be at least 32 characters long")
            else:
                print(f"✅ {var}: Set securely")
        elif var == 'FLASK_CONFIG':
            if value != 'production':
                issues.append(f"⚠️  {var} should be 'production', currently: '{value}'")
            else:
                print(f"✅ {var}: {value}")
        elif var == 'DATABASE_URL':
            # Validate database URL format
            try:
                parsed = urlparse(value)
                if parsed.scheme in ['postgresql', 'postgres', 'mssql+pyodbc']:
                    print(f"✅ {var}: Valid {parsed.scheme} connection")
                elif parsed.scheme == 'sqlite':
                    issues.append(f"⚠️  {var} uses SQLite - consider PostgreSQL for production")
                else:
                    print(f"✅ {var}: Set ({parsed.scheme})")
            except Exception as e:
                issues.append(f"❌ {var} format invalid: {e}")
        else:
            print(f"✅ {var}: Set")
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: Set")
        else:
            print(f"ℹ️  {var}: Not set ({description})")
    
    return issues

def check_app_configuration():
    """Check Flask app configuration"""
    print("\n🔍 Checking Flask Configuration...")
    
    issues = []
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from app import create_app
        
        # Try to create production app
        app = create_app('production')
        
        with app.app_context():
            # Check debug mode
            if app.debug:
                issues.append("❌ Debug mode is enabled in production!")
            else:
                print("✅ Debug mode: Disabled")
            
            # Check secret key
            if len(app.config['SECRET_KEY']) >= 32:
                print("✅ Secret key: Strong")
            else:
                issues.append("⚠️  Secret key should be longer")
            
            # Check session security
            if app.config.get('SESSION_COOKIE_SECURE'):
                print("✅ Session cookies: HTTPS only")
            else:
                issues.append("⚠️  SESSION_COOKIE_SECURE should be True in production")
            
            print("✅ Flask configuration: Valid")
            
    except Exception as e:
        issues.append(f"❌ Failed to create Flask app: {e}")
    
    return issues

def check_database_connection():
    """Test database connection"""
    print("\n🔍 Checking Database Connection...")
    
    issues = []
    
    try:
        from app import create_app
        from database import db
        from models.user import User
        
        app = create_app('production')
        
        with app.app_context():
            # Test basic connection
            db.engine.connect()
            print("✅ Database connection: Successful")
            
            # Check if tables exist
            user_count = User.query.count()
            print(f"✅ User table: {user_count} users found")
            
            if user_count == 0:
                issues.append("⚠️  No users in database - run create_admin_user.py")
            
    except Exception as e:
        issues.append(f"❌ Database connection failed: {e}")
    
    return issues

def check_security_headers():
    """Check security best practices"""
    print("\n🔍 Checking Security Configuration...")
    
    issues = []
    
    # These would typically be configured at the reverse proxy level (nginx, Azure App Service)
    recommendations = [
        "Configure HTTPS redirect at reverse proxy level",
        "Set security headers: HSTS, CSP, X-Frame-Options",
        "Configure rate limiting",
        "Set up monitoring and alerting",
        "Regular security updates for dependencies"
    ]
    
    for rec in recommendations:
        print(f"ℹ️  Recommendation: {rec}")
    
    return issues

def main():
    print("🚀 AcidTech Cash Flow - Production Readiness Check")
    print("=" * 60)
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_environment_variables())
    all_issues.extend(check_app_configuration())
    all_issues.extend(check_database_connection())
    all_issues.extend(check_security_headers())
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    if not all_issues:
        print("🎉 All checks passed! Application is ready for production.")
        print("\n✅ READY FOR DEPLOYMENT")
    else:
        print("⚠️  Issues found that should be addressed:")
        for issue in all_issues:
            print(f"   {issue}")
        
        critical_issues = [i for i in all_issues if i.startswith("❌")]
        if critical_issues:
            print(f"\n❌ CRITICAL ISSUES: {len(critical_issues)} - Fix before deployment")
            sys.exit(1)
        else:
            print(f"\n⚠️  WARNINGS: {len(all_issues)} - Recommended to fix")
    
    print("\n📚 Next Steps:")
    print("1. Set all required environment variables")
    print("2. Run: python create_admin_user.py")
    print("3. Test login functionality")
    print("4. Deploy using wsgi.py")
    print("5. Configure HTTPS and security headers")

if __name__ == "__main__":
    main()