#!/usr/bin/env python3
"""
Migration script to classify existing users as individual or organization
based on their email domains
"""

import os
import sys
from app import app, db
from models import User

def migrate_user_types():
    """Classify all existing users based on their email domains"""
    print("🔄 Starting user type migration...")
    
    with app.app_context():
        # Get all users
        users = User.query.all()
        print(f"📊 Found {len(users)} users to classify")
        
        updated_count = 0
        individual_count = 0
        organization_count = 0
        
        for user in users:
            # Skip if user_type is already set
            if hasattr(user, 'user_type') and user.user_type:
                continue
            
            # Classify user based on email domain
            old_type = getattr(user, 'user_type', None)
            new_type = user.classify_user_type()
            
            # Set the user type
            user.user_type = new_type
            
            if new_type == 'individual':
                individual_count += 1
            else:
                organization_count += 1
            
            updated_count += 1
            print(f"✅ {user.email} -> {new_type}")
        
        # Commit changes
        db.session.commit()
        
        print(f"\n🎉 Migration completed!")
        print(f"📈 Updated {updated_count} users")
        print(f"👤 Individual users: {individual_count}")
        print(f"🏢 Organization users: {organization_count}")

if __name__ == '__main__':
    migrate_user_types() 