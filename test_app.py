#!/usr/bin/env python3
"""
Test script for SentimentStream application
This script tests the core functionality and identifies issues
"""

import os
import sys
from datetime import datetime
from app import app, db
from models import User, Poster, Subscription
from forms import RegistrationForm, LoginForm

def test_database():
    """Test database connectivity and models"""
    print("🔍 Testing database...")
    
    try:
        with app.app_context():
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("✅ Database connection successful")
            
            # Test User model
            test_user = User()
            test_user.username = f"test_user_{int(datetime.utcnow().timestamp())}"
            test_user.email = f"test_{int(datetime.utcnow().timestamp())}@example.com"
            test_user.set_password("testpassword")
            test_user.profile_completed = False
            test_user.is_premium = False
            test_user.is_master_admin = False
            
            db.session.add(test_user)
            db.session.commit()
            print("✅ User model test successful")
            
            # Test password verification
            if test_user.check_password("testpassword"):
                print("✅ Password hashing test successful")
            else:
                print("❌ Password hashing test failed")
            
            # Clean up test user
            db.session.delete(test_user)
            db.session.commit()
            print("✅ Database cleanup successful")
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

def test_forms():
    """Test form validation"""
    print("🔍 Testing forms...")
    
    try:
        with app.app_context():
            # Test registration form
            form_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'testpass123',
                'password2': 'testpass123'
            }
            
            form = RegistrationForm(data=form_data)
            if form.validate():
                print("✅ Registration form validation successful")
            else:
                print("❌ Registration form validation failed")
                for field, errors in form.errors.items():
                    print(f"  {field}: {errors}")
            
            # Test login form
            login_data = {
                'username': 'testuser',
                'password': 'testpass123'
            }
            
            login_form = LoginForm(data=login_data)
            if login_form.validate():
                print("✅ Login form validation successful")
            else:
                print("❌ Login form validation failed")
                
    except Exception as e:
        print(f"❌ Form test failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test application configuration"""
    print("🔍 Testing configuration...")
    
    try:
        # Test config loading
        if hasattr(app, 'config'):
            print("✅ Application configuration loaded")
            
            # Test required config keys
            required_keys = ['SECRET_KEY', 'DATABASE_URL', 'UPLOAD_FOLDER']
            for key in required_keys:
                if key in app.config:
                    print(f"✅ Config key '{key}' found")
                else:
                    print(f"❌ Config key '{key}' missing")
            
            # Test API keys (optional)
            api_keys = ['GEMINI_API_KEY', 'STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY']
            for key in api_keys:
                if key in app.config:
                    value = app.config[key]
                    if value and value != f"your-{key.lower().replace('_', '-')}-here":
                        print(f"✅ API key '{key}' configured")
                    else:
                        print(f"⚠️  API key '{key}' not configured (optional)")
                else:
                    print(f"⚠️  API key '{key}' not found (optional)")
                    
        else:
            print("❌ Application configuration not found")
            return False
            
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

def test_directories():
    """Test required directories exist"""
    print("🔍 Testing directories...")
    
    required_dirs = [
        'static/uploads',
        'static/uploads/posters',
        'static/uploads/logos',
        'templates'
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory '{directory}' exists")
        else:
            print(f"❌ Directory '{directory}' missing")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Created directory '{directory}'")
            except Exception as e:
                print(f"❌ Failed to create directory '{directory}': {e}")
                return False
    
    return True

def test_templates():
    """Test template files exist"""
    print("🔍 Testing templates...")
    
    required_templates = [
        'base.html',
        'register.html',
        'login.html',
        'dashboard.html',
        'generate_poster.html',
        'poster_gallery.html'
    ]
    
    for template in required_templates:
        template_path = os.path.join('templates', template)
        if os.path.exists(template_path):
            print(f"✅ Template '{template}' exists")
        else:
            print(f"❌ Template '{template}' missing")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 SentimentStream Application Test Suite")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Directories", test_directories),
        ("Templates", test_templates),
        ("Database", test_database),
        ("Forms", test_forms)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to run.")
        print("\n🚀 To start the application:")
        print("   python run_local.py")
        print("\n🌐 Access the application at: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please fix the issues before running the application.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 