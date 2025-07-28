#!/usr/bin/env python3
"""
Test to verify signal is working and uploading files to DigitalOcean Spaces
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

def test_signal_working():
    """Test if signal is working and uploading files"""
    print("🔍 Testing Signal Functionality")
    print("=" * 50)
    
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
        test_logo_content = b'fake logo image content for signal test'
        test_logo = SimpleUploadedFile(
            "signal_test_logo.png",
            test_logo_content,
            content_type="image/png"
        )
        
        test_cover_content = b'fake cover image content for signal test'
        test_cover = SimpleUploadedFile(
            "signal_test_cover.png",
            test_cover_content,
            content_type="image/png"
        )
        
        # Create clinic with files
        clinic_data = {
            'name': 'Signal Test Clinic',
            'clinic_type': 'virtual_clinic',
            'description': 'A test clinic for signal functionality',
            'phone': '+911234567894',
            'email': 'signal_test@example.com',
            'website': 'https://signal_test.example.com',
            'street': '123 Signal Test St',
            'city': 'Signal Test City',
            'state': 'Signal Test State',
            'pincode': '123456',
            'country': 'India',
            'operating_hours': {'monday': {'start': '09:00', 'end': '18:00'}},
            'specialties': ['General Medicine'],
            'services': ['Consultation'],
            'facilities': ['Video Call'],
            'registration_number': 'SIGNAL123',
            'license_number': 'SIGNAL456',
            'accreditation': 'SIGNAL',
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
        time.sleep(10)  # Wait longer for upload to complete
        
        # Check if files exist on DigitalOcean Spaces
        import boto3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        if clinic.logo:
            remote_key = f"{settings.AWS_LOCATION}/{clinic.logo.name}"
            try:
                response = s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=remote_key)
                print(f"✅ Logo exists on DigitalOcean Spaces: {remote_key}")
            except Exception as e:
                print(f"❌ Logo not found on DigitalOcean Spaces: {e}")
        
        if clinic.cover_image:
            remote_key = f"{settings.AWS_LOCATION}/{clinic.cover_image.name}"
            try:
                response = s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=remote_key)
                print(f"✅ Cover image exists on DigitalOcean Spaces: {remote_key}")
            except Exception as e:
                print(f"❌ Cover image not found on DigitalOcean Spaces: {e}")
        
        # Test file accessibility via HTTP
        import requests
        
        if clinic.logo:
            logo_url = f"https://edrspace.sgp1.digitaloceanspaces.com/edrcontainer1/{clinic.logo.name}"
            try:
                response = requests.head(logo_url, timeout=5)
                print(f"✅ Logo accessible via HTTP: {response.status_code}")
            except Exception as e:
                print(f"❌ Logo not accessible via HTTP: {e}")
        
        if clinic.cover_image:
            cover_url = f"https://edrspace.sgp1.digitaloceanspaces.com/edrcontainer1/{clinic.cover_image.name}"
            try:
                response = requests.head(cover_url, timeout=5)
                print(f"✅ Cover accessible via HTTP: {response.status_code}")
            except Exception as e:
                print(f"❌ Cover not accessible via HTTP: {e}")
        
        # Clean up
        clinic.delete()
        print("🗑️ Test clinic deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_signal_working() 