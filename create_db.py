#!/usr/bin/env python3
"""
Script to create the database with the new user_type column
"""

from app import app, db
from models import User, Poster, Subscription

def create_database():
    """Create the database tables"""
    print("🗄️ Creating database tables...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Check if master admin exists
        master_user = User.query.filter_by(email="admin@posterly.ai").first()
        if not master_user:
            print("👑 Creating master admin user...")
            master_user = User()
            master_user.username = "posterly_admin"
            master_user.email = "admin@posterly.ai"
            master_user.full_name = "Master Administrator"
            master_user.business_name = "Posterly Internal"
            master_user.is_premium = True
            master_user.is_master_admin = True
            master_user.profile_completed = True
            master_user.user_type = "organization"  # Master admin is organization type
            master_user.set_password("MasterKey#2025")
            db.session.add(master_user)
            db.session.commit()
            print("✅ Master admin user created!")
        else:
            print("✅ Master admin user already exists!")
        
        # Check table structure
        print("\n📊 Database structure:")
        print(f"Users table: {User.__table__.columns.keys()}")
        print(f"Posters table: {Poster.__table__.columns.keys()}")
        print(f"Subscriptions table: {Subscription.__table__.columns.keys()}")

if __name__ == '__main__':
    create_database() 