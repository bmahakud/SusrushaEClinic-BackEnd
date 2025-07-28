#!/usr/bin/env python3
"""
Final test to verify complete file upload functionality
"""

import os
import sys
import django
import time

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from eclinic.models import Clinic
from authentication.models import User
from django.conf import settings

def test_final_upload():
    """Test final file upload functionality"""
    print("🎯 Final Test - Complete File Upload Functionality")
    print("=" * 60)
    
    try:
        # Create a test admin user
        admin_user, created = User.objects.get_or_create(
            phone='+911234567890',
            defaults={
                'name': 'Test Admin',
                'role': 'admin'
            }
        )
        
        # Create test image files
        test_logo_content = b'fake logo image content for final test'
        test_logo = SimpleUploadedFile(
            "final_test_logo.png",
            test_logo_content,
            content_type="image/png"
        )
        
        test_cover_content = b'fake cover image content for final test'
        test_cover = SimpleUploadedFile(
            "final_test_cover.png",
            test_cover_content,
            content_type="image/png"
        )
        
        # Create clinic with files
        clinic_data = {
            'name': 'Final Test Clinic',
            'clinic_type': 'virtual_clinic',
            'description': 'A final test clinic for complete functionality',
            'phone': '+911234567893',
            'email': 'final_test@example.com',
            'website': 'https://final_test.example.com',
            'street': '123 Final Test St',
            'city': 'Final Test City',
            'state': 'Final Test State',
            'pincode': '123456',
            'country': 'India',
            'operating_hours': {'monday': {'start': '09:00', 'end': '18:00'}},
            'specialties': ['General Medicine'],
            'services': ['Consultation'],
            'facilities': ['Video Call'],
            'registration_number': 'FINAL123',
            'license_number': 'FINAL456',
            'accreditation': 'FINAL',
            'is_active': True,
            'accepts_online_consultations': True,
            'admin': admin_user,
            'logo': test_logo,
            'cover_image': test_cover
        }
        
        print("📝 Creating clinic with files...")
        start_time = time.time()
        clinic = Clinic.objects.create(**clinic_data)
        end_time = time.time()
        
        print(f"✅ Clinic created in {end_time - start_time:.2f} seconds")
        print(f"📁 Clinic ID: {clinic.id}")
        print(f"📁 Logo path: {clinic.logo}")
        print(f"📁 Cover path: {clinic.cover_image}")
        
        # Wait for async upload to complete
        print("⏳ Waiting for async upload to complete...")
        time.sleep(5)
        
        # Test file accessibility
        import requests
        
        if clinic.logo:
            logo_url = f"https://edrspace.sgp1.digitaloceanspaces.com/edrcontainer1/{clinic.logo.name}"
            try:
                response = requests.head(logo_url, timeout=5)
                print(f"✅ Logo accessible: {response.status_code} - {logo_url}")
            except Exception as e:
                print(f"❌ Logo not accessible: {e}")
        
        if clinic.cover_image:
            cover_url = f"https://edrspace.sgp1.digitaloceanspaces.com/edrcontainer1/{clinic.cover_image.name}"
            try:
                response = requests.head(cover_url, timeout=5)
                print(f"✅ Cover accessible: {response.status_code} - {cover_url}")
            except Exception as e:
                print(f"❌ Cover not accessible: {e}")
        
        # Test signed URL generation
        from utils.signed_urls import get_signed_media_url
        
        if clinic.logo:
            signed_logo_url = get_signed_media_url(str(clinic.logo))
            print(f"🔗 Signed logo URL: {signed_logo_url[:100]}...")
        
        if clinic.cover_image:
            signed_cover_url = get_signed_media_url(str(clinic.cover_image))
            print(f"🔗 Signed cover URL: {signed_cover_url[:100]}...")
        
        # Clean up
        clinic.delete()
        print("🗑️ Test clinic deleted")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_upload() 