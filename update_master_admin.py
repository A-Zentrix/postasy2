#!/usr/bin/env python3
"""
Script to update existing master admin user with user_type
"""

from app import app, db
from models import User

def update_master_admin():
    """Update master admin user with user_type"""
    print("🔄 Updating Master Admin User...")
    
    with app.app_context():
        # Find master admin user
        master_user = User.query.filter_by(email="admin@posterly.ai").first()
        
        if master_user:
            print("✅ Master admin user found!")
            print(f"📧 Email: {master_user.email}")
            print(f"👤 Username: {master_user.username}")
            print(f"👑 Is master admin: {master_user.is_master_admin}")
            print(f"⭐ Is premium: {master_user.is_premium}")
            print(f"🏢 Current user type: {master_user.user_type}")
            
            # Update user_type if not set
            if not master_user.user_type:
                master_user.user_type = "organization"
                db.session.commit()
                print("✅ Updated user_type to 'organization'")
            else:
                print("✅ User type already set")
            
            # Verify the update
            db.session.refresh(master_user)
            print(f"🏢 Updated user type: {master_user.user_type}")
            
        else:
            print("❌ Master admin user not found!")

if __name__ == '__main__':
    update_master_admin() 