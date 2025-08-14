#!/usr/bin/env python3
"""
Test script to verify superadmin can create slots for any doctor
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
SUPERADMIN_CREDENTIALS = {
    "phone": "superadmin_phone",  # Replace with actual superadmin phone
    "otp": "123456"  # Replace with actual OTP
}

def test_superadmin_slot_creation():
    """Test that superadmin can create slots for any doctor"""
    
    print("🧪 Testing Superadmin Slot Creation...")
    
    # Step 1: Login as superadmin
    print("\n1. Logging in as superadmin...")
    login_response = requests.post(f"{BASE_URL}/auth/verify-otp/", json=SUPERADMIN_CREDENTIALS)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    login_data = login_response.json()
    access_token = login_data['data']['access']
    print("✅ Login successful")
    
    # Step 2: Get a doctor ID to create slots for
    print("\n2. Getting doctor list...")
    headers = {"Authorization": f"Bearer {access_token}"}
    doctors_response = requests.get(f"{BASE_URL}/admin/doctors/", headers=headers)
    
    if doctors_response.status_code != 200:
        print(f"❌ Failed to get doctors: {doctors_response.status_code}")
        return False
    
    doctors_data = doctors_response.json()
    if not doctors_data.get('data', {}).get('results'):
        print("❌ No doctors found")
        return False
    
    doctor_id = doctors_data['data']['results'][0]['id']
    print(f"✅ Found doctor: {doctor_id}")
    
    # Step 3: Create a slot for the doctor
    print("\n3. Creating slot for doctor...")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    slot_data = {
        "date": tomorrow,
        "start_time": "09:00:00",
        "end_time": "10:00:00",
        "is_available": True,
        "clinic": None  # Global availability
    }
    
    slot_response = requests.post(
        f"{BASE_URL}/doctors/{doctor_id}/slots/",
        json=slot_data,
        headers=headers
    )
    
    print(f"Status Code: {slot_response.status_code}")
    print(f"Response: {slot_response.text}")
    
    if slot_response.status_code == 201:
        print("✅ Slot creation successful!")
        return True
    else:
        print("❌ Slot creation failed!")
        return False

def test_superadmin_generate_slots():
    """Test that superadmin can generate slots for any doctor"""
    
    print("\n🧪 Testing Superadmin Slot Generation...")
    
    # Step 1: Login as superadmin
    print("\n1. Logging in as superadmin...")
    login_response = requests.post(f"{BASE_URL}/auth/verify-otp/", json=SUPERADMIN_CREDENTIALS)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    login_data = login_response.json()
    access_token = login_data['data']['access']
    print("✅ Login successful")
    
    # Step 2: Get a doctor ID and clinic ID
    print("\n2. Getting doctor and clinic data...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get doctors
    doctors_response = requests.get(f"{BASE_URL}/admin/doctors/", headers=headers)
    if doctors_response.status_code != 200:
        print(f"❌ Failed to get doctors: {doctors_response.status_code}")
        return False
    
    doctors_data = doctors_response.json()
    doctor_id = doctors_data['data']['results'][0]['id']
    
    # Get clinics
    clinics_response = requests.get(f"{BASE_URL}/eclinic/", headers=headers)
    if clinics_response.status_code != 200:
        print(f"❌ Failed to get clinics: {clinics_response.status_code}")
        return False
    
    clinics_data = clinics_response.json()
    clinic_id = clinics_data['data']['results'][0]['id']
    
    print(f"✅ Found doctor: {doctor_id}, clinic: {clinic_id}")
    
    # Step 3: Generate slots for the doctor
    print("\n3. Generating slots for doctor...")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    generate_data = {
        "clinic": clinic_id,
        "date": tomorrow,
        "start_time": "09:00:00",
        "end_time": "17:00:00"
    }
    
    generate_response = requests.post(
        f"{BASE_URL}/doctors/{doctor_id}/slots/generate_slots/",
        json=generate_data,
        headers=headers
    )
    
    print(f"Status Code: {generate_response.status_code}")
    print(f"Response: {generate_response.text}")
    
    if generate_response.status_code == 201:
        print("✅ Slot generation successful!")
        return True
    else:
        print("❌ Slot generation failed!")
        return False

if __name__ == "__main__":
    print("🚀 Starting Superadmin Slot Tests...")
    
    # Test 1: Direct slot creation
    test1_result = test_superadmin_slot_creation()
    
    # Test 2: Slot generation
    test2_result = test_superadmin_generate_slots()
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    print(f"Direct Slot Creation: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Slot Generation: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 All tests passed! Superadmin can now create slots for any doctor.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
