#!/usr/bin/env python3
"""
Local development runner for SentimentStream
This script sets up the environment and runs the application locally
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def setup_environment():
    """Set up the local development environment"""
    print("🚀 Setting up local development environment...")
    
    # Create necessary directories
    directories = [
        'static/uploads',
        'static/uploads/posters',
        'static/uploads/logos',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Set default environment variables for local development
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    print("✅ Environment setup complete!")

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        ('flask', 'flask'),
        ('flask_sqlalchemy', 'flask-sqlalchemy'),
        ('flask_login', 'flask-login'),
        ('flask_wtf', 'flask-wtf'),
        ('PIL', 'pillow'),
        ('google.genai', 'google-genai'),
        ('stripe', 'stripe'),
        ('werkzeug', 'werkzeug'),
        ('jinja2', 'jinja2')
    ]
    
    missing_packages = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} - MISSING")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_configuration():
    """Check if the application is properly configured"""
    print("🔧 Checking configuration...")
    
    # Check if config file exists
    if not os.path.exists('config.py'):
        print("❌ config.py not found!")
        return False
    
    # Check if main app file exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found!")
        return False
    
    print("✅ Configuration files found!")
    return True

def run_application():
    """Run the Flask application"""
    print("🌐 Starting SentimentStream application...")
    
    try:
        from app import app
        
        print("✅ Application loaded successfully!")
        print("📍 Server will be available at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the application
        app.run(
            debug=True,
            host='0.0.0.0',
            port=8000,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("Make sure all dependencies are installed and the application files are correct.")
        return False
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False

def main():
    """Main function to run the local development server"""
    print("=" * 60)
    print("🎨 SentimentStream - Local Development Server")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        sys.exit(1)
    
    # Check configuration
    if not check_configuration():
        print("\n❌ Configuration check failed. Please fix the issues and try again.")
        sys.exit(1)
    
    print("\n🎉 All checks passed! Starting the application...")
    print("=" * 60)
    
    # Run the application
    run_application()

if __name__ == '__main__':
    main() 