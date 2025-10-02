from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile information
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    business_name = db.Column(db.String(100))
    logo_filename = db.Column(db.String(100))
    website = db.Column(db.String(200))
    facebook = db.Column(db.String(200))
    instagram = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    
    # Account status
    is_premium = db.Column(db.Boolean, default=False)
    profile_completed = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(100))
    
    # MASTER ADMIN FLAG - For internal testing and admin access
    # This user bypasses all usage limits and has unlimited access
    is_master_admin = db.Column(db.Boolean, default=False)
    
    # User classification based on email domain
    user_type = db.Column(db.String(20), default='individual')  # 'individual' or 'organization'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posters = db.relationship('Poster', backref='user', lazy=True, cascade='all, delete-orphan')
    subscription = db.relationship('Subscription', backref='user', uselist=False, lazy=True)
    
    def get_subscription_plan(self):
        """Get current subscription plan"""
        if self.subscription and self.subscription.status == 'active':
            return self.subscription.plan_id
        return 'free'
    
    def has_premium_access(self):
        """Check if user has premium access"""
        plan = self.get_subscription_plan()
        return plan in ['pro', 'premium'] or self.is_master_admin
    
    def set_password(self, password):
        """Set password with proper hashing"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def has_unlimited_access(self):
        """Check if user has unlimited access (premium or master admin)"""
        return self.is_premium or self.is_master_admin
    
    def is_admin_user(self):
        """Check if this is the master admin user"""
        return self.is_master_admin
    
    def get_profile_fields(self):
        """Return dictionary of profile fields for poster overlay"""
        return {
            'full_name': self.full_name,
            'phone': self.phone,
            'address': self.address,
            'business_name': self.business_name,
            'website': self.website,
            'facebook': self.facebook,
            'instagram': self.instagram,
            'twitter': self.twitter,
            'linkedin': self.linkedin,
            'logo_filename': self.logo_filename
        }
    
    def classify_user_type(self):
        """Classify user as individual or organization based on email domain"""
        if not self.email:
            return 'individual'
        
        domain = self.email.split('@')[-1].lower()
        
        # Personal email domains (individual users)
        personal_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com',
            'aol.com', 'icloud.com', 'me.com', 'mac.com', 'protonmail.com',
            'tutanota.com', 'mail.com', 'yandex.com', 'zoho.com', 'fastmail.com'
        }
        
        if domain in personal_domains:
            return 'individual'
        else:
            return 'organization'
    
    def get_daily_poster_limit(self):
        """Get daily poster creation limit based on user type"""
        if self.has_unlimited_access():
            return float('inf')  # Unlimited for premium users
        
        if self.user_type == 'organization':
            return 3  # 3 posters per day for organizations
        else:
            return 1  # 1 poster per day for individuals
    
    def get_daily_poster_count(self):
        """Get number of posters created today"""
        from datetime import datetime, date
        today = date.today()
        
        return Poster.query.filter(
            Poster.user_id == self.id,
            db.func.date(Poster.created_at) == today
        ).count()
    
    def can_create_poster_today(self):
        """Check if user can create a poster today"""
        if self.has_unlimited_access():
            return True
        
        daily_count = self.get_daily_poster_count()
        daily_limit = self.get_daily_poster_limit()
        
        return daily_count < daily_limit
    
    def get_remaining_daily_posts(self):
        """Get remaining posts for today"""
        if self.has_unlimited_access():
            return float('inf')
        
        daily_count = self.get_daily_poster_count()
        daily_limit = self.get_daily_poster_limit()
        
        return max(0, daily_limit - daily_count)

class Poster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    
    # Profile fields displayed on this poster (JSON string)
    displayed_fields = db.Column(db.Text)  # JSON string of field names
    
    # Metadata
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    has_watermark = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_displayed_fields_list(self):
        """Convert JSON string to list"""
        import json
        if self.displayed_fields:
            try:
                return json.loads(self.displayed_fields)
            except:
                return []
        return []
    
    def set_displayed_fields(self, fields_list):
        """Convert list to JSON string"""
        import json
        self.displayed_fields = json.dumps(fields_list)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_customer_id = db.Column(db.String(100))
    stripe_subscription_id = db.Column(db.String(100), unique=True)
    plan_id = db.Column(db.String(20), default='free')  # free, pro, premium
    status = db.Column(db.String(20), default='active')  # active, canceled, past_due, etc.
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
