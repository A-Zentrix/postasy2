#!/usr/bin/env python3
"""
Quick setup script for SentimentStream local development
This script helps you configure and run the application locally
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print the application banner"""
    print("=" * 60)
    print("🎨 SentimentStream - Local Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        # Check if requirements.txt exists
        if not os.path.exists('requirements.txt'):
            print("❌ requirements.txt not found!")
            return False
        
        # Install dependencies
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'static/uploads',
        'static/uploads/posters',
        'static/uploads/logos',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    return True

def configure_api_keys():
    """Help user configure API keys"""
    print("\n🔑 API Key Configuration")
    print("You can configure API keys now or later by editing config.py")
    
    # Check if config.py exists
    if not os.path.exists('config.py'):
        print("❌ config.py not found!")
        return False
    
    print("\nOptional API Keys (press Enter to skip):")
    
    # Gemini API Key
    gemini_key = input("Google Gemini API Key (for AI image generation): ").strip()
    if gemini_key:
        update_config_file('GEMINI_API_KEY', gemini_key)
        print("✅ Gemini API key configured!")
    
    # Stripe Keys
    stripe_secret = input("Stripe Secret Key (for payments): ").strip()
    if stripe_secret:
        update_config_file('STRIPE_SECRET_KEY', stripe_secret)
        print("✅ Stripe secret key configured!")
    
    stripe_publishable = input("Stripe Publishable Key (for payments): ").strip()
    if stripe_publishable:
        update_config_file('STRIPE_PUBLISHABLE_KEY', stripe_publishable)
        print("✅ Stripe publishable key configured!")
    
    return True

def update_config_file(key_name, value):
    """Update a specific key in config.py"""
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Replace the placeholder value
        old_line = f'{key_name} = "your-{key_name.lower().replace("_", "-")}-here"'
        new_line = f'{key_name} = "{value}"'
        
        if old_line in content:
            content = content.replace(old_line, new_line)
            
            with open('config.py', 'w') as f:
                f.write(content)
            
            return True
        else:
            print(f"⚠️  Could not find {key_name} in config.py - please update manually")
            return False
            
    except Exception as e:
        print(f"❌ Error updating config.py: {e}")
        return False

def test_application():
    """Test if the application can be imported"""
    print("🧪 Testing application...")
    
    try:
        # Test basic imports
        import flask
        import flask_sqlalchemy
        import flask_login
        
        # Test application import
        from app import app
        print("✅ Application imports successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed!")
        return False
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False

def run_application():
    """Run the application"""
    print("\n🚀 Starting SentimentStream...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the application
        subprocess.run([sys.executable, 'run_local.py'])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies!")
        print("Please install them manually: pip install -r requirements.txt")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("\n❌ Failed to create directories!")
        sys.exit(1)
    
    # Configure API keys
    configure_api_keys()
    
    # Test application
    if not test_application():
        print("\n❌ Application test failed!")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python run_local.py")
    print("2. Open: http://localhost:5000")
    print("3. Configure API keys in config.py for full features")
    
    # Ask if user wants to run the application now
    run_now = input("\nWould you like to start the application now? (y/n): ").strip().lower()
    if run_now in ['y', 'yes']:
        run_application()

if __name__ == '__main__':
    main() 