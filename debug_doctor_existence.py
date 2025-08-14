#!/usr/bin/env python3
"""
Debug script to check doctor existence and ID format
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"

def check_doctor_existence():
    """Check if doctor DOC032 exists and what the correct format should be"""
    
    print("🔍 Debugging Doctor Existence...")
    
    # Step 1: Get all doctors to see what IDs exist
    print("\n1. Getting all doctors from the system...")
    
    try:
        # Try different endpoints to find the correct one
        endpoints = [
            "/api/doctors/",
            "/api/doctors/superadmin/",
            "/api/admin/doctors/"
        ]
        
        doctors = []
        working_endpoint = None
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('data', {}).get('results'):
                        doctors = data['data']['results']
                        working_endpoint = endpoint
                        print(f"✅ Found working endpoint: {endpoint}")
                        break
                    elif data.get('results'):
                        doctors = data['results']
                        working_endpoint = endpoint
                        print(f"✅ Found working endpoint: {endpoint}")
                        break
                    elif isinstance(data, list):
                        doctors = data
                        working_endpoint = endpoint
                        print(f"✅ Found working endpoint: {endpoint}")
                        break
            except Exception as e:
                print(f"❌ Endpoint {endpoint} failed: {str(e)}")
                continue
        
        if not doctors:
            print("❌ Could not find any working endpoint to get doctors")
            return False
        
        print(f"✅ Found {len(doctors)} doctors in the system:")
        
        for i, doctor in enumerate(doctors[:10]):  # Show first 10 doctors
            print(f"   {i+1}. {doctor.get('user_name', 'Unknown')}")
            print(f"      Profile ID: {doctor.get('id')}")
            print(f"      User ID: {doctor.get('user')}")
            print(f"      Phone: {doctor.get('user_phone', 'N/A')}")
            print()
        
        # Check if DOC032 exists
        doc032_exists = any(doctor.get('user') == 'DOC032' for doctor in doctors)
        
        if doc032_exists:
            print("✅ Doctor DOC032 exists in the system!")
            return True
        else:
            print("❌ Doctor DOC032 does NOT exist in the system.")
            print("\n📝 Available doctor IDs:")
            for doctor in doctors:
                print(f"   - {doctor.get('user')} ({doctor.get('user_name', 'Unknown')})")
            return False
            
    except Exception as e:
        print(f"❌ Error checking doctor existence: {str(e)}")
        return False

def test_doctor_endpoint(doctor_id):
    """Test if a specific doctor endpoint works"""
    
    print(f"\n2. Testing doctor endpoint for {doctor_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/doctors/{doctor_id}/")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Doctor endpoint works!")
            print(f"Doctor Name: {data.get('data', {}).get('user_name', 'Unknown')}")
            print(f"Doctor ID: {data.get('data', {}).get('user', 'Unknown')}")
            return True
        elif response.status_code == 404:
            print("❌ Doctor not found (404)")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing doctor endpoint: {str(e)}")
        return False

def test_slot_endpoint(doctor_id):
    """Test if the slot endpoint works for a specific doctor"""
    
    print(f"\n3. Testing slot endpoint for {doctor_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/doctors/{doctor_id}/slots/")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Slot endpoint works!")
            return True
        elif response.status_code == 404:
            print("❌ Doctor not found (404)")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing slot endpoint: {str(e)}")
        return False

def main():
    """Run all debug checks"""
    print("🚀 Starting Doctor Existence Debug...")
    
    # Check if DOC032 exists
    doc032_exists = check_doctor_existence()
    
    if doc032_exists:
        # Test the specific doctor endpoints
        test_doctor_endpoint('DOC032')
        test_slot_endpoint('DOC032')
    else:
        # Test with a different doctor ID if available
        print("\n🔍 Testing with a different doctor ID...")
        
        # Get the first available doctor
        try:
            response = requests.get(f"{BASE_URL}/admin/doctors/")
            if response.status_code == 200:
                data = response.json()
                doctors = data.get('data', {}).get('results', [])
                
                if doctors:
                    first_doctor_id = doctors[0].get('user')
                    print(f"Testing with first available doctor: {first_doctor_id}")
                    
                    test_doctor_endpoint(first_doctor_id)
                    test_slot_endpoint(first_doctor_id)
                else:
                    print("❌ No doctors found in the system")
        except Exception as e:
            print(f"❌ Error getting alternative doctor: {str(e)}")
    
    print("\n" + "="*50)
    print("📊 Debug Summary:")
    print(f"DOC032 Exists: {'✅ YES' if doc032_exists else '❌ NO'}")
    
    if not doc032_exists:
        print("\n💡 Recommendations:")
        print("1. Check if the doctor was deleted from the system")
        print("2. Use a different doctor ID that exists")
        print("3. Create a new doctor if needed")
        print("4. Check the database for the correct doctor IDs")

if __name__ == "__main__":
    main()
