#!/usr/bin/env python3
"""
Test script for Admin Management API endpoints
Run this script to test the admin management functionality
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
SUPERADMIN_PHONE = "+919876543210"
TEST_ADMIN_PHONE = "+919876543212"

def print_response(response, title):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_admin_management():
    """Test admin management endpoints"""
    
    # Step 1: Send OTP to SuperAdmin
    print("Testing Admin Management API...")
    
    # Send OTP
    otp_response = requests.post(f"{BASE_URL}/auth/send-otp/", json={
        "phone": SUPERADMIN_PHONE
    })
    print_response(otp_response, "Send OTP Response")
    
    if otp_response.status_code != 200:
        print("Failed to send OTP. Exiting...")
        return
    
    # Verify OTP (using test OTP 999999)
    verify_response = requests.post(f"{BASE_URL}/auth/verify-otp/", json={
        "phone": SUPERADMIN_PHONE,
        "otp": "999999"
    })
    print_response(verify_response, "Verify OTP Response")
    
    if verify_response.status_code != 200:
        print("Failed to verify OTP. Exiting...")
        return
    
    # Extract access token
    access_token = verify_response.json()['data']['access']
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Get Admin Statistics
    stats_response = requests.get(f"{BASE_URL}/auth/superadmin/admins/stats/", headers=headers)
    print_response(stats_response, "Admin Statistics Response")
    
    # Step 3: List Admin Accounts
    list_response = requests.get(f"{BASE_URL}/auth/superadmin/admins/", headers=headers)
    print_response(list_response, "List Admin Accounts Response")
    
    # Step 4: Create New Admin Account
    create_data = {
        "phone": TEST_ADMIN_PHONE,
        "name": "Test Admin",
        "email": "test.admin@example.com",
        "password": "testpass123",
        "is_active": True
    }
    
    create_response = requests.post(f"{BASE_URL}/auth/superadmin/admins/", 
                                  json=create_data, headers=headers)
    print_response(create_response, "Create Admin Account Response")
    
    if create_response.status_code == 201:
        admin_id = create_response.json()['data']['user_id']
        
        # Step 5: Get Admin Details
        detail_response = requests.get(f"{BASE_URL}/auth/superadmin/admins/{admin_id}/", headers=headers)
        print_response(detail_response, "Get Admin Details Response")
        
        # Step 6: Update Admin Account
        update_data = {
            "name": "Updated Test Admin",
            "email": "updated.test@example.com",
            "city": "Mumbai",
            "state": "Maharashtra"
        }
        
        update_response = requests.put(f"{BASE_URL}/auth/superadmin/admins/{admin_id}/", 
                                     json=update_data, headers=headers)
        print_response(update_response, "Update Admin Account Response")
        
        # Step 7: Test Search and Filters
        search_response = requests.get(
            f"{BASE_URL}/auth/superadmin/admins/?search=test&status=active&sort_by=name&sort_order=asc", 
            headers=headers
        )
        print_response(search_response, "Search Admin Accounts Response")
        
        # Step 8: Deactivate Admin Account (Optional - uncomment to test)
        # delete_response = requests.delete(f"{BASE_URL}/auth/superadmin/admins/{admin_id}/", headers=headers)
        # print_response(delete_response, "Deactivate Admin Account Response")
    
    print("\n" + "="*50)
    print("Admin Management API Test Completed!")
    print("="*50)

if __name__ == "__main__":
    test_admin_management() 