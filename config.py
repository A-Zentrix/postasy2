import os
from datetime import timedelta

class Config:
    """Configuration class for local development"""
    
    # Flask Configuration
    SECRET_KEY = "your-secret-key-change-this-in-production"
    DEBUG = True
    
    # Database Configuration
    DATABASE_URL = "sqlite:///posterly.db"
    
    # Upload Configuration
    UPLOAD_FOLDER = "static/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Branding
    LOGO_URL = os.environ.get(
        "POSTASY_LOGO_URL",
        "https://i.ibb.co/1tKz4L94/Whats-App-Image-2025-08-09-at-17-54-24-61eeb336.jpg"
    )
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # API Keys (Replace with your actual keys for production)
    GEMINI_API_KEY = "AIzaSyB--ZUNOgfFX6CVPgfO9efb4ph_pn66X2I"
    STRIPE_SECRET_KEY = "sk_test_your-stripe-secret-key-here"
    STRIPE_PUBLISHABLE_KEY = "pk_test_your-stripe-publishable-key-here"
    STRIPE_WEBHOOK_SECRET = "whsec_your-webhook-secret-here"
    
    # OAuth Configuration (Optional - for social login)
    GOOGLE_CLIENT_ID = "your-google-client-id-here"
    GOOGLE_CLIENT_SECRET = "your-google-client-secret-here"
    
    # Email Configuration (Optional)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "your-email@gmail.com"
    MAIL_PASSWORD = "your-app-password"
    
    # Security Configuration
    WTF_CSRF_ENABLED = False  # Disable for local development
    
    # File Upload Settings
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    # Poster Generation Settings
    DEFAULT_POSTER_WIDTH = 1024
    DEFAULT_POSTER_HEIGHT = 1024
    WATERMARK_TEXT = "Postasy - Upgrade for Watermark-Free"
    
    # Subscription Plans (Local Development)
    SUBSCRIPTION_PLANS = {
        'free': {
            'name': 'Free Plan',
            'price': 0,
            'features': ['5 posters per month', 'Watermarked downloads', 'Basic templates'],
            'stripe_price_id': None
        },
        'pro': {
            'name': 'Pro Plan',
            'price': 9.99,
            'features': ['Unlimited posters', 'Watermark-free downloads', 'Premium templates', 'High-res exports'],
            'stripe_price_id': 'price_test_pro_plan'  # Test price ID
        },
        'premium': {
            'name': 'Premium Plan', 
            'price': 19.99,
            'features': ['Everything in Pro', 'Priority support', 'Advanced AI features', 'Custom branding'],
            'stripe_price_id': 'price_test_premium_plan'  # Test price ID
        }
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Override with environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY', Config.SECRET_KEY)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', Config.GEMINI_API_KEY)
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', Config.STRIPE_SECRET_KEY)
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', Config.STRIPE_PUBLISHABLE_KEY)
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', Config.STRIPE_WEBHOOK_SECRET)

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    DATABASE_URL = "sqlite:///test.db"
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 