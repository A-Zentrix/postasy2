#!/usr/bin/env python3
"""
Script to check master admin user in database
"""

from app import app, db
from models import User

def check_master_admin():
    """Check master admin user in database"""
    print("🔍 Checking Master Admin User...")
    
    with app.app_context():
        # Check if master admin exists
        master_user = User.query.filter_by(email="admin@posterly.ai").first()
        
        if master_user:
            print("✅ Master admin user found!")
            print(f"📧 Email: {master_user.email}")
            print(f"👤 Username: {master_user.username}")
            print(f"👑 Is master admin: {master_user.is_master_admin}")
            print(f"⭐ Is premium: {master_user.is_premium}")
            print(f"🏢 User type: {master_user.user_type}")
            print(f"✅ Profile completed: {master_user.profile_completed}")
            
            # Test password
            if master_user.check_password("MasterKey#2025"):
                print("🔐 Password verification: ✅ Working")
            else:
                print("🔐 Password verification: ❌ Failed")
        else:
            print("❌ Master admin user not found!")
            print("Creating master admin user...")
            
            # Create master admin
            master_user = User()
            master_user.username = "posterly_admin"
            master_user.email = "admin@posterly.ai"
            master_user.full_name = "Master Administrator"
            master_user.business_name = "Posterly Internal"
            master_user.is_premium = True
            master_user.is_master_admin = True
            master_user.profile_completed = True
            master_user.user_type = "organization"
            master_user.set_password("MasterKey#2025")
            
            db.session.add(master_user)
            db.session.commit()
            print("✅ Master admin user created!")

if __name__ == '__main__':
    check_master_admin() 