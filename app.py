import os
import logging
from datetime import datetime

from flask import Flask, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

# Import configuration
from config import config

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import db from models to avoid circular imports
from models import db
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Set environment variables from config for services that need them
    os.environ['GEMINI_API_KEY'] = app.config.get('GEMINI_API_KEY', '')
    os.environ['STRIPE_SECRET_KEY'] = app.config.get('STRIPE_SECRET_KEY', '')
    os.environ['STRIPE_PUBLISHABLE_KEY'] = app.config.get('STRIPE_PUBLISHABLE_KEY', '')
    os.environ['STRIPE_WEBHOOK_SECRET'] = app.config.get('STRIPE_WEBHOOK_SECRET', '')
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get("DATABASE_URL", "sqlite:///posterly.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Upload configuration
    app.config["UPLOAD_FOLDER"] = app.config.get("UPLOAD_FOLDER", "static/uploads")
    app.config["MAX_CONTENT_LENGTH"] = app.config.get("MAX_CONTENT_LENGTH", 16 * 1024 * 1024)

    # Expose branding to templates
    @app.context_processor
    def inject_branding():
        return {
            'brand_logo_url': app.config.get('LOGO_URL')
        }
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # CSRF protection (disabled for local development)
    if app.config.get('WTF_CSRF_ENABLED', False):
        csrf.init_app(app)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'  # type: ignore
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Create upload directories
    upload_dirs = [
        app.config.get("UPLOAD_FOLDER", "static/uploads"),
        os.path.join(app.config.get("UPLOAD_FOLDER", "static/uploads"), "posters"),
        os.path.join(app.config.get("UPLOAD_FOLDER", "static/uploads"), "logos")
    ]
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Create tables and register blueprints
    with app.app_context():
        import models
        db.create_all()
        
        # Register blueprints
        from routes import main_bp, auth_bp, poster_bp, profile_bp, subscription_bp, payment_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(poster_bp, url_prefix='/poster')
        app.register_blueprint(profile_bp, url_prefix='/profile')
        app.register_blueprint(subscription_bp, url_prefix='/subscription')
        app.register_blueprint(payment_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
