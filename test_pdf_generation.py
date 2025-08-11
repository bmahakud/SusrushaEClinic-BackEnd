#!/usr/bin/env python3
"""
Test script to debug PDF generation and file path issues
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings
from prescriptions.models import Prescription, PrescriptionPDF
from prescriptions.enhanced_pdf_generator import generate_prescription_pdf
from utils.signed_urls import generate_signed_url
from django.contrib.auth import get_user_model

User = get_user_model()

def test_pdf_generation_and_paths():
    """Test PDF generation and file path handling"""
    
    print("🔍 Testing PDF Generation and File Paths")
    print("=" * 60)
    
    # Test 1: Check AWS configuration
    print("🔧 AWS Configuration:")
    print(f"   AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"   AWS_LOCATION: {settings.AWS_LOCATION}")
    print(f"   AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
    print(f"   AWS_S3_REGION_NAME: {settings.AWS_S3_REGION_NAME}")
    
    print("\n" + "=" * 60)
    
    # Test 2: Check existing prescription PDFs
    try:
        pdf_instances = PrescriptionPDF.objects.all()[:3]
        
        if pdf_instances:
            print(f"📊 Found {pdf_instances.count()} prescription PDFs")
            
            for i, pdf in enumerate(pdf_instances, 1):
                print(f"\n📄 PDF {i}:")
                print(f"   ID: {pdf.id}")
                print(f"   Prescription ID: {pdf.prescription.id}")
                print(f"   Version: {pdf.version_number}")
                print(f"   File: {pdf.pdf_file}")
                print(f"   File Name: {pdf.pdf_file.name if pdf.pdf_file else 'None'}")
                print(f"   File URL: {pdf.pdf_file.url if pdf.pdf_file else 'None'}")
                
                if pdf.pdf_file:
                    # Test different file key formats
                    file_key_variants = [
                        str(pdf.pdf_file),  # Original format
                        pdf.pdf_file.name,  # Just the name
                        f"{settings.AWS_LOCATION}/{pdf.pdf_file.name}",  # With AWS_LOCATION
                    ]
                    
                    for j, file_key in enumerate(file_key_variants, 1):
                        print(f"\n   🔗 Variant {j}: {file_key}")
                        try:
                            signed_url = generate_signed_url(file_key, expiration=3600)
                            print(f"   ✅ Signed URL: {signed_url[:100]}...")
                            
                            # Check if URL contains the correct bucket and location
                            if settings.AWS_STORAGE_BUCKET_NAME in signed_url and settings.AWS_LOCATION in signed_url:
                                print(f"   ✅ URL contains correct bucket and location")
                            else:
                                print(f"   ⚠️  URL may not contain correct bucket/location")
                                
                        except Exception as e:
                            print(f"   ❌ Error: {e}")
                else:
                    print(f"   ⚠️  No file attached")
        else:
            print("📭 No prescription PDFs found in database")
            
    except Exception as e:
        print(f"❌ Error accessing prescription PDFs: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 3: Test upload path function
    print("🧪 Testing Upload Path Function:")
    
    try:
        from prescriptions.models import prescription_pdf_upload_path
        
        # Create a mock instance to test the upload path
        class MockInstance:
            def __init__(self):
                self.prescription = MockPrescription()
        
        class MockPrescription:
            def __init__(self):
                self.consultation = MockConsultation()
        
        class MockConsultation:
            def __init__(self):
                self.id = "CON068"
        
        mock_instance = MockInstance()
        test_filename = "test_prescription.pdf"
        
        upload_path = prescription_pdf_upload_path(mock_instance, test_filename)
        print(f"   📁 Upload Path: {upload_path}")
        
        # Test signed URL generation for this path
        try:
            signed_url = generate_signed_url(upload_path, expiration=3600)
            print(f"   ✅ Signed URL for upload path: {signed_url[:100]}...")
            
            # Check if URL contains the correct bucket and location
            if settings.AWS_STORAGE_BUCKET_NAME in signed_url and settings.AWS_LOCATION in signed_url:
                print(f"   ✅ URL contains correct bucket and location")
            else:
                print(f"   ⚠️  URL may not contain correct bucket/location")
                
        except Exception as e:
            print(f"   ❌ Error generating signed URL: {e}")
            
    except Exception as e:
        print(f"❌ Error testing upload path: {e}")
    
    print("\n" + "=" * 60)
    
    # Test 4: Check if we can find any actual files in the bucket
    print("🔍 Checking for actual files in bucket:")
    
    try:
        import boto3
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # List objects in the bucket with the AWS_LOCATION prefix
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix=f"{settings.AWS_LOCATION}/prescriptions/pdfs/",
            MaxKeys=10
        )
        
        if 'Contents' in response:
            print(f"   📁 Found {len(response['Contents'])} files in bucket:")
            for obj in response['Contents']:
                print(f"      - {obj['Key']}")
                
                # Test signed URL for this file
                try:
                    signed_url = generate_signed_url(obj['Key'], expiration=3600)
                    print(f"         ✅ Signed URL: {signed_url[:80]}...")
                except Exception as e:
                    print(f"         ❌ Error: {e}")
        else:
            print("   📭 No files found in bucket")
            
    except Exception as e:
        print(f"❌ Error accessing bucket: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_pdf_generation_and_paths() 