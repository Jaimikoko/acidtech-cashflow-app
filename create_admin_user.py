#!/usr/bin/env python3
"""
Create Admin User for AcidTech Cash Flow Application
Creates an initial admin user for production deployment

Usage:
    python create_admin_user.py

Environment Variables (recommended for production):
    ADMIN_USERNAME - Admin username (default: admin)
    ADMIN_EMAIL - Admin email (default: admin@acidtech.com)
    ADMIN_PASSWORD - Admin password (default: AcidTech2024!)
    ADMIN_FIRST_NAME - First name (default: System)
    ADMIN_LAST_NAME - Last name (default: Administrator)
"""

import os
import sys
from datetime import datetime
from getpass import getpass

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def create_admin_user():
    try:
        from app import create_app
        from models.user import User
        from database import db
        
        # Create app context
        app = create_app('production')
        
        with app.app_context():
            # Check if any users exist
            user_count = User.query.count()
            
            if user_count > 0:
                print(f"✅ Database already has {user_count} users.")
                
                # Show existing users
                users = User.query.all()
                print("\n📋 Existing users:")
                for user in users:
                    print(f"   • {user.username} ({user.email}) - {user.role}")
                
                # Ask if we want to create another admin
                response = input("\n🤔 Do you want to create another admin user? (y/N): ")
                if response.lower() != 'y':
                    print("✋ Cancelled.")
                    return
            
            print("\n🔐 Creating new admin user...")
            
            # Get user details from environment or prompt
            username = os.environ.get('ADMIN_USERNAME')
            if not username:
                username = input("👤 Username [admin]: ").strip() or 'admin'
            
            email = os.environ.get('ADMIN_EMAIL')
            if not email:
                email = input("📧 Email [admin@acidtech.com]: ").strip() or 'admin@acidtech.com'
            
            first_name = os.environ.get('ADMIN_FIRST_NAME')
            if not first_name:
                first_name = input("👨 First Name [System]: ").strip() or 'System'
            
            last_name = os.environ.get('ADMIN_LAST_NAME')
            if not last_name:
                last_name = input("👨 Last Name [Administrator]: ").strip() or 'Administrator'
            
            # Check if username/email already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"❌ Username '{username}' already exists!")
                return
            
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                print(f"❌ Email '{email}' already exists!")
                return
            
            # Get password
            password = os.environ.get('ADMIN_PASSWORD')
            if not password:
                print("🔑 Password requirements:")
                print("   • Minimum 8 characters")
                print("   • Recommended: Include numbers and special characters")
                print()
                
                while True:
                    password = getpass("🔒 Password: ")
                    if len(password) < 8:
                        print("❌ Password must be at least 8 characters long!")
                        continue
                    
                    password_confirm = getpass("🔒 Confirm Password: ")
                    if password != password_confirm:
                        print("❌ Passwords don't match!")
                        continue
                    
                    break
            
            # Create admin user
            admin_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='admin',
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            admin_user.set_password(password)
            
            # Save to database
            db.session.add(admin_user)
            db.session.commit()
            
            print("\n🎉 Admin user created successfully!")
            print("=" * 50)
            print(f"👤 Username: {username}")
            print(f"📧 Email: {email}")
            print(f"👨 Name: {first_name} {last_name}")
            print(f"🔰 Role: admin")
            print("=" * 50)
            print(f"🌐 Login URL: http://your-domain/auth/login")
            print("\n✅ You can now login to the AcidTech Cash Flow system!")
            
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("💡 Make sure you've installed all dependencies with: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 AcidTech Cash Flow - Admin User Creation")
    print("=" * 50)
    create_admin_user()