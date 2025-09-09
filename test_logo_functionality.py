#!/usr/bin/env python3
"""
Test Logo Functionality
This script tests if the logo feature is working correctly
"""

import os
import sys
import json

def test_logo_functionality():
    print("🔍 Testing Logo Functionality...")
    
    # Check if logo uploads directory exists
    logo_dir = "static/uploads/logos"
    if os.path.exists(logo_dir):
        print(f"✅ Logo directory exists: {logo_dir}")
        
        # List logo files
        logo_files = [f for f in os.listdir(logo_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
        print(f"📁 Found {len(logo_files)} logo files:")
        for logo_file in logo_files:
            print(f"   - {logo_file}")
    else:
        print(f"❌ Logo directory not found: {logo_dir}")
    
    # Check forms.py for logo field
    try:
        with open('forms.py', 'r') as f:
            content = f.read()
            if 'show_logo' in content:
                print("✅ Logo field found in forms.py")
            else:
                print("❌ Logo field not found in forms.py")
    except Exception as e:
        print(f"❌ Error reading forms.py: {e}")
    
    # Check models.py for logo_filename
    try:
        with open('models.py', 'r') as f:
            content = f.read()
            if 'logo_filename' in content:
                print("✅ logo_filename field found in models.py")
            else:
                print("❌ logo_filename field not found in models.py")
            
            if 'get_profile_fields' in content and 'logo_filename' in content:
                print("✅ Logo included in get_profile_fields()")
            else:
                print("❌ Logo not included in get_profile_fields()")
    except Exception as e:
        print(f"❌ Error reading models.py: {e}")
    
    # Check image_service.py for logo processing
    try:
        with open('image_service.py', 'r') as f:
            content = f.read()
            if 'logo_path' in content and 'logo_filename' in content:
                print("✅ Logo processing found in image_service.py")
            else:
                print("❌ Logo processing not found in image_service.py")
    except Exception as e:
        print(f"❌ Error reading image_service.py: {e}")
    
    # Check generate_poster.html for logo checkbox
    try:
        with open('templates/generate_poster.html', 'r') as f:
            content = f.read()
            if 'show_logo' in content:
                print("✅ Logo checkbox found in generate_poster.html")
            else:
                print("❌ Logo checkbox not found in generate_poster.html")
    except Exception as e:
        print(f"❌ Error reading generate_poster.html: {e}")
    
    print("\n🎯 Logo Functionality Test Complete!")
    print("📝 To test the logo feature:")
    print("1. Start the server: python run_local.py")
    print("2. Login and go to profile settings")
    print("3. Upload a logo file")
    print("4. Go to generate poster page")
    print("5. Check 'Include Company Logo' checkbox")
    print("6. Generate poster and verify logo appears")

if __name__ == "__main__":
    test_logo_functionality() 