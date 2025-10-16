import os
from datetime import timedelta

class Config:
    """Configuration class for local development"""
    
    # Flask Configuration
    SECRET_KEY = "your-secret-key-change-this-in-production"
    DEBUG = True
    
    # Database Configuration
    DATABASE_URL = "sqlite:///postasy.db"
    
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
    GEMINI_API_KEY = "AIzaSyARLgg6blfmauGUDPSwo_mHMrpLHLP22uE"
    
    # Razorpay Configuration
    RAZORPAY_KEY_ID = "rzp_live_RR1Xu8K6RsDvdF"
    RAZORPAY_KEY_SECRET = "ij24LrPwGcHLBSEKS12EHRYe"
    RAZORPAY_WEBHOOK_SECRET = "your-webhook-secret-here"
    
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
    
    # Subscription Plans (INR Pricing)
    SUBSCRIPTION_PLANS = {
        'free': {
            'name': 'Free Plan',
            'price': 0,
            'currency': 'INR',
            'features': ['10 Templates/month', 'Watermarked downloads', 'No AI features', 'No Scheduling'],
            'razorpay_plan_id': None
        },
        'starter': {
            'name': 'Starter',
            'price': 99,
            'currency': 'INR',
            'features': ['50 Templates/month', 'Remove watermark', 'Scheduler (5 posts/week)', 'Pre-made trending templates'],
            'razorpay_plan_id': 'plan_RT1vLSXcKS8mLI'  # Razorpay Starter plan ID
        },
        'pro': {
            'name': 'Pro Plan',
            'price': 399,
            'currency': 'INR',
            'features': ['Unlimited Templates', 'AI Brand Assistant', 'AI Captions + Hashtags', 'Scheduler (Unlimited)', 'Instagram Performance Dashboard'],
            'razorpay_plan_id': 'plan_RT1vhhl2rcwvBA'  # Razorpay Pro plan ID
        },
        'agency': {
            'name': 'Agency',
            'price': 999,
            'currency': 'INR',
            'features': ['Everything in Pro', '5 Client Accounts', 'Approval Workflow', 'White-label reports', 'API Access'],
            'razorpay_plan_id': 'plan_RT1vv3mBjeH0NH'  # Razorpay Agency plan ID
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
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', Config.RAZORPAY_KEY_ID)
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', Config.RAZORPAY_KEY_SECRET)
    RAZORPAY_WEBHOOK_SECRET = os.environ.get('RAZORPAY_WEBHOOK_SECRET', Config.RAZORPAY_WEBHOOK_SECRET)

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