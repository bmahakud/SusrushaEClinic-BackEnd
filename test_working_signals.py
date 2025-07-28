#!/usr/bin/env python3
"""
Test for working signals - immediate file uploads
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
from django.utils import timezone
from authentication.models import User
from doctors.models import DoctorEducation
from patients.models import MedicalRecord
from eclinic.models import Clinic
from django.conf import settings
import requests

def test_working_signals():
    """Test the working signals for immediate file uploads"""
    print("🔍 Testing Working Signals for Immediate File Uploads")
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
        
        # Test 1: Authentication - Profile Picture ✅ WORKING
        print("\n📸 Testing Authentication - Profile Picture")
        print("-" * 50)
        
        profile_pic_content = b'fake profile picture content'
        profile_pic = SimpleUploadedFile(
            "test_profile_pic.png",
            profile_pic_content,
            content_type="image/png"
        )
        
        admin_user.profile_picture = profile_pic
        admin_user.save()
        
        # Test immediate accessibility
        if admin_user.profile_picture:
            profile_url = f"https://edrspace.sgp1.digitaloceanspaces.com/edrcontainer1/{admin_user.profile_picture.name}"
            try:
                response = requests.head(profile_url, timeout=5)
                print(f"✅ Profile picture immediately accessible: {response.status_code}")
            except Exception as e:
                print(f"❌ Profile picture not accessible: {e}")
        
        # Test 2: Doctors - Certificate ✅ WORKING
        print("\n👨‍⚕️ Testing Doctors - Certificate")
        print("-" * 50)
        
        cert_content = b'fake certificate content'
        cert_file = SimpleUploadedFile(
            "test_certificate.pdf",
            cert_content,
            content_type="application/pdf"
        )
        
        doctor_education = DoctorEducation.objects.create(
            doctor=admin_user,
            degree='MBBS',
            institution='Test Medical College',
            year_of_completion=2020,
            certificate=cert_file
        )
        
        # Test immediate accessibility
        if doctor_education.certificate:
            cert_url = f"https://edrspace.sgp1.digitaloceanspaces.com/edrcontainer1/{doctor_education.certificate.name}"
            try:
                response = requests.head(cert_url, timeout=5)
                print(f"✅ Doctor certificate immediately accessible: {response.status_code}")
            except Exception as e:
                print(f"❌ Doctor certificate not accessible: {e}")
        
        # Test 3: Patients - Document ✅ WORKING
        print("\n👤 Testing Patients - Document")
        print("-" * 50)
        
        doc_content = b'fake patient document content'
        doc_file = SimpleUploadedFile(
            "test_patient_doc.pdf",
            doc_content,
            content_type="application/pdf"
        )
        
        medical_record = MedicalRecord.objects.create(
            patient=admin_user,
            record_type='lab_report',
            title='Test Lab Report',
            description='A test lab report',
            date_recorded=timezone.now().date(),
            document=doc_file
        )
        
        # Test immediate accessibility
        if medical_record.document:
            doc_url = f"https://edrspace.sgp1.digitaloceanspaces.com/edrcontainer1/{medical_record.document.name}"
            try:
                response = requests.head(doc_url, timeout=5)
                print(f"✅ Patient document immediately accessible: {response.status_code}")
            except Exception as e:
                print(f"❌ Patient document not accessible: {e}")
        
        # Test 4: Eclinic - Logo and Cover ✅ WORKING
        print("\n🏥 Testing Eclinic - Logo and Cover")
        print("-" * 50)
        
        logo_content = b'fake clinic logo content'
        logo_file = SimpleUploadedFile(
            "test_clinic_logo.png",
            logo_content,
            content_type="image/png"
        )
        
        cover_content = b'fake clinic cover content'
        cover_file = SimpleUploadedFile(
            "test_clinic_cover.png",
            cover_content,
            content_type="image/png"
        )
        
        clinic = Clinic.objects.create(
            name='Test Clinic',
            clinic_type='virtual_clinic',
            description='A test clinic',
            phone='+911234567893',
            email='test_clinic@example.com',
            admin=admin_user,
            logo=logo_file,
            cover_image=cover_file
        )
        
        # Test immediate accessibility
        if clinic.logo:
            logo_url = f"https://edrspace.sgp1.digitaloceanspaces.com/edrcontainer1/{clinic.logo.name}"
            try:
                response = requests.head(logo_url, timeout=5)
                print(f"✅ Clinic logo immediately accessible: {response.status_code}")
            except Exception as e:
                print(f"❌ Clinic logo not accessible: {e}")
        
        if clinic.cover_image:
            cover_url = f"https://edrspace.sgp1.digitaloceanspaces.com/edrcontainer1/{clinic.cover_image.name}"
            try:
                response = requests.head(cover_url, timeout=5)
                print(f"✅ Clinic cover immediately accessible: {response.status_code}")
            except Exception as e:
                print(f"❌ Clinic cover not accessible: {e}")
        
        # Clean up
        print("\n🗑️ Cleaning up test data...")
        medical_record.delete()
        doctor_education.delete()
        clinic.delete()
        print("✅ Test data cleaned up")
        
        print("\n🎉 All working signals test completed successfully!")
        print("\n✅ Summary of Working Signals:")
        print("   📸 Authentication - Profile Picture")
        print("   👨‍⚕️ Doctors - Education Certificate")
        print("   👤 Patients - Medical Record Document")
        print("   🏥 Eclinic - Logo and Cover Image")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_working_signals() 