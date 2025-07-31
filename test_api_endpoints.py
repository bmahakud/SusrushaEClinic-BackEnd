#!/usr/bin/env python
"""
Test script to check API endpoints
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from authentication.models import User
from consultations.models import Consultation

def test_api_endpoints():
    """Test the API endpoints"""
    client = Client()
    
    # Get a test user (doctor)
    try:
        doctor = User.objects.get(id='DOC001')
        print(f"✅ Found doctor: {doctor.name} ({doctor.phone})")
    except User.DoesNotExist:
        print("❌ Doctor DOC001 not found")
        return
    
    # Get a test consultation
    try:
        consultation = Consultation.objects.get(id='CON001')
        print(f"✅ Found consultation: {consultation.id} for patient {consultation.patient_id}")
    except Consultation.DoesNotExist:
        print("❌ Consultation CON001 not found")
        return
    
    # Test prescription by consultation endpoint
    print("\n🔍 Testing prescription by consultation endpoint...")
    try:
        # This should work with the URL pattern
        url = f'/api/prescriptions/consultation/{consultation.id}/'
        print(f"URL: {url}")
        
        # Test if the URL pattern exists
        from prescriptions.urls import urlpatterns
        print("Available prescription URL patterns:")
        for pattern in urlpatterns:
            print(f"  - {pattern.pattern}")
            
    except Exception as e:
        print(f"❌ Error testing prescription endpoint: {e}")
    
    # Test patient endpoint
    print("\n🔍 Testing patient endpoint...")
    try:
        url = f'/api/patients/{consultation.patient_id}/'
        print(f"URL: {url}")
        
        # Test if the URL pattern exists
        from patients.urls import urlpatterns
        print("Available patient URL patterns:")
        for pattern in urlpatterns:
            print(f"  - {pattern.pattern}")
            
    except Exception as e:
        print(f"❌ Error testing patient endpoint: {e}")

if __name__ == '__main__':
    test_api_endpoints() 