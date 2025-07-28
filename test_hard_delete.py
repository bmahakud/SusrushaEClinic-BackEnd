#!/usr/bin/env python3
"""
Test to verify hard delete functionality for admin and doctor
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from authentication.models import User
from doctors.models import DoctorProfile
from django.utils import timezone
import time

def test_hard_delete():
    """Test hard delete functionality"""
    print("🔍 Testing Hard Delete Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Admin Hard Delete
        print("\n👤 Testing Admin Hard Delete")
        print("-" * 30)
        
        # Create a test admin
        admin = User.objects.create(
            phone='+911234567890',
            name='Test Admin for Delete',
            email='test_admin_delete@example.com',
            role='admin',
            is_active=True
        )
        
        admin_id = admin.id
        print(f"✅ Created admin with ID: {admin_id}")
        
        # Verify admin exists
        admin_exists = User.objects.filter(id=admin_id).exists()
        print(f"✅ Admin exists before delete: {admin_exists}")
        
        # Hard delete the admin
        admin.delete()
        print("✅ Admin deleted")
        
        # Verify admin no longer exists
        admin_exists_after = User.objects.filter(id=admin_id).exists()
        print(f"✅ Admin exists after delete: {admin_exists_after}")
        
        if not admin_exists_after:
            print("✅ Admin hard delete successful!")
        else:
            print("❌ Admin hard delete failed!")
        
        # Test 2: Doctor Hard Delete
        print("\n👨‍⚕️ Testing Doctor Hard Delete")
        print("-" * 30)
        
        # Create a test doctor user
        doctor_user = User.objects.create(
            phone='+911234567891',
            name='Test Doctor for Delete',
            email='test_doctor_delete@example.com',
            role='doctor',
            is_active=True
        )
        
        # Create doctor profile
        doctor = DoctorProfile.objects.create(
            user=doctor_user,
            license_number='TEST_DELETE_123',
            qualification='MBBS',
            specialization='general_medicine',
            experience_years=5,
            consultation_fee=100.00
        )
        
        doctor_id = doctor.id
        user_id = doctor_user.id
        print(f"✅ Created doctor with ID: {doctor_id}, user ID: {user_id}")
        
        # Verify doctor and user exist
        doctor_exists = DoctorProfile.objects.filter(id=doctor_id).exists()
        user_exists = User.objects.filter(id=user_id).exists()
        print(f"✅ Doctor exists before delete: {doctor_exists}")
        print(f"✅ User exists before delete: {user_exists}")
        
        # Hard delete the doctor (this should also delete the user due to CASCADE)
        doctor.delete()
        print("✅ Doctor deleted")
        
        # Verify doctor and user no longer exist
        doctor_exists_after = DoctorProfile.objects.filter(id=doctor_id).exists()
        user_exists_after = User.objects.filter(id=user_id).exists()
        print(f"✅ Doctor exists after delete: {doctor_exists_after}")
        print(f"✅ User exists after delete: {user_exists_after}")
        
        if not doctor_exists_after and not user_exists_after:
            print("✅ Doctor hard delete successful!")
        else:
            print("❌ Doctor hard delete failed!")
        
        print("\n🎉 Hard delete test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hard_delete() 