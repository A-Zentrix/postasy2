#!/usr/bin/env python3
"""
Test script to verify master admin login functionality
"""

from app import app, db
from models import User
from routes import authenticate_master_admin, get_or_create_master_admin

def test_master_admin():
    """Test master admin authentication and creation"""
    print("🧪 Testing Master Admin Login...")
    
    with app.app_context():
        # Test authentication with email
        print("📧 Testing with email: admin@posterly.ai")
        result1 = authenticate_master_admin("admin@posterly.ai", "MasterKey#2025")
        print(f"✅ Email authentication: {result1}")
        
        # Test authentication with username
        print("👤 Testing with username: posterly_admin")
        result2 = authenticate_master_admin("posterly_admin", "MasterKey#2025")
        print(f"✅ Username authentication: {result2}")
        
        # Test wrong password
        print("❌ Testing with wrong password")
        result3 = authenticate_master_admin("admin@posterly.ai", "WrongPassword")
        print(f"❌ Wrong password test: {result3}")
        
        # Test wrong username
        print("❌ Testing with wrong username")
        result4 = authenticate_master_admin("wrong@email.com", "MasterKey#2025")
        print(f"❌ Wrong username test: {result4}")
        
        # Get or create master admin user
        print("\n👑 Getting/Creating master admin user...")
        master_user = get_or_create_master_admin()
        print(f"✅ Master admin user: {master_user.email}")
        print(f"✅ Username: {master_user.username}")
        print(f"✅ Is master admin: {master_user.is_master_admin}")
        print(f"✅ Is premium: {master_user.is_premium}")
        print(f"✅ User type: {master_user.user_type}")
        print(f"✅ Profile completed: {master_user.profile_completed}")
        
        # Test password verification
        print("\n🔐 Testing password verification...")
        if master_user.check_password("MasterKey#2025"):
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
        
        print("\n🎉 Master admin test completed!")

if __name__ == '__main__':
    test_master_admin() 