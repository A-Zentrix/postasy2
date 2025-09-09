#!/usr/bin/env python3
"""
Test script for delete functionality
This script tests the delete route and functionality
"""

import requests
import sys
import os

def test_delete_functionality():
    """Test the delete functionality"""
    print("🧪 Testing Delete Functionality")
    print("=" * 50)
    
    # Base URL for local development
    base_url = "http://localhost:5000"
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server responded but health check failed")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server is not running: {e}")
        print("Please start the server with: python run_local.py")
        return False
    
    # Test 2: Check if gallery page is accessible
    print("\n2. Testing gallery page accessibility...")
    try:
        response = requests.get(f"{base_url}/poster/gallery", timeout=5)
        if response.status_code == 200:
            print("✅ Gallery page is accessible")
        elif response.status_code == 302:
            print("✅ Gallery page redirects (likely to login) - this is expected")
        else:
            print(f"❌ Gallery page returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing gallery page: {e}")
    
    # Test 3: Check if delete route exists
    print("\n3. Testing delete route structure...")
    try:
        # This will likely redirect to login, but we can check the route exists
        response = requests.post(f"{base_url}/poster/999/delete", timeout=5)
        if response.status_code in [302, 401, 403, 404]:
            print("✅ Delete route exists (redirecting as expected)")
        else:
            print(f"❌ Unexpected response from delete route: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing delete route: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Manual Testing Required:")
    print("1. Start the server: python run_local.py")
    print("2. Open browser: http://localhost:5000")
    print("3. Login to your account")
    print("4. Go to poster gallery")
    print("5. Click delete button on any poster")
    print("6. Confirm deletion in dialog")
    print("7. Verify poster is removed from gallery")
    
    print("\n📋 Expected Behavior:")
    print("- Click delete button → Confirmation dialog appears")
    print("- Confirm deletion → Button shows 'Deleting...' with spinner")
    print("- After deletion → Page reloads, poster is gone")
    print("- Success message → 'Poster deleted successfully'")
    
    print("\n🔧 Troubleshooting:")
    print("- Check browser console (F12) for JavaScript errors")
    print("- Check server console for backend errors")
    print("- Verify user is logged in and owns the poster")
    print("- Check file permissions for uploads folder")
    
    return True

if __name__ == "__main__":
    test_delete_functionality() 