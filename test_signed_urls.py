#!/usr/bin/env python3
"""
Test script to verify signed URL functionality for prescription PDFs
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from utils.signed_urls import generate_signed_url
from prescriptions.models import PrescriptionPDF
from django.conf import settings

def test_signed_url_generation():
    """Test signed URL generation for prescription PDFs"""
    
    print("🔍 Testing Signed URL Generation for Prescription PDFs")
    print("=" * 60)
    
    # Test 1: Check if we can generate a signed URL for a sample file
    try:
        sample_file_key = "media/prescriptions/pdfs/test/test_prescription.pdf"
        signed_url = generate_signed_url(sample_file_key, expiration=3600)
        
        print(f"✅ Signed URL generated successfully")
        print(f"📁 File Key: {sample_file_key}")
        print(f"🔗 Signed URL: {signed_url[:100]}...")
        print(f"⏰ Expiration: 1 hour")
        
        # Check if URL contains required AWS parameters
        required_params = ['AWSAccessKeyId', 'Signature', 'Expires']
        missing_params = [param for param in required_params if param not in signed_url]
        
        if missing_params:
            print(f"❌ Missing required parameters: {missing_params}")
        else:
            print(f"✅ All required AWS parameters present")
            
    except Exception as e:
        print(f"❌ Error generating signed URL: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Check existing prescription PDFs
    try:
        pdf_instances = PrescriptionPDF.objects.all()[:5]  # Get first 5 PDFs
        
        if pdf_instances:
            print(f"📊 Found {pdf_instances.count()} prescription PDFs")
            
            for i, pdf in enumerate(pdf_instances, 1):
                print(f"\n📄 PDF {i}:")
                print(f"   ID: {pdf.id}")
                print(f"   File: {pdf.pdf_file}")
                print(f"   Size: {pdf.file_size} bytes")
                
                if pdf.pdf_file:
                    try:
                        file_key = str(pdf.pdf_file)
                        signed_url = generate_signed_url(file_key, expiration=3600)
                        print(f"   ✅ Signed URL: {signed_url[:80]}...")
                    except Exception as e:
                        print(f"   ❌ Error generating signed URL: {e}")
                else:
                    print(f"   ⚠️  No file attached")
        else:
            print("📭 No prescription PDFs found in database")
            
    except Exception as e:
        print(f"❌ Error accessing prescription PDFs: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Check AWS/S3 configuration
    print("🔧 AWS/S3 Configuration Check:")
    print(f"   AWS_ACCESS_KEY_ID: {'✅ Set' if settings.AWS_ACCESS_KEY_ID else '❌ Not set'}")
    print(f"   AWS_SECRET_ACCESS_KEY: {'✅ Set' if settings.AWS_SECRET_ACCESS_KEY else '❌ Not set'}")
    print(f"   AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"   AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
    print(f"   AWS_S3_REGION_NAME: {settings.AWS_S3_REGION_NAME}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_signed_url_generation() 