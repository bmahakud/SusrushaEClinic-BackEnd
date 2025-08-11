#!/usr/bin/env python
"""
Test script to verify file upload and signed URL generation is working
"""

import os
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings
from prescriptions.models import PrescriptionPDF, Prescription
from consultations.models import Consultation
from utils.signed_urls import generate_signed_url
import boto3

def test_upload_and_signed_url():
    """Test file upload and signed URL generation"""
    print("🔍 Testing File Upload and Signed URL Generation")
    
    # Check settings
    print(f"📋 Settings Check:")
    print(f"   ALWAYS_UPLOAD_FILES_TO_AWS: {settings.ALWAYS_UPLOAD_FILES_TO_AWS}")
    print(f"   AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"   AWS_LOCATION: {settings.AWS_LOCATION}")
    print(f"   AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
    
    # Test S3 connection
    print(f"\n🔗 Testing S3 Connection...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # List objects in bucket
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix=settings.AWS_LOCATION,
            MaxKeys=5
        )
        
        if 'Contents' in response:
            print(f"   ✅ S3 connection successful")
            print(f"   📁 Found {len(response['Contents'])} objects in bucket")
            for obj in response['Contents'][:3]:
                print(f"      - {obj['Key']}")
        else:
            print(f"   ⚠️  S3 connection successful but bucket is empty")
            
    except Exception as e:
        print(f"   ❌ S3 connection failed: {e}")
        return
    
    # Test signed URL generation
    print(f"\n🔗 Testing Signed URL Generation...")
    try:
        # Test with a sample file path
        test_file_key = f"{settings.AWS_LOCATION}/test_file.txt"
        signed_url = generate_signed_url(test_file_key, expiration=3600)
        print(f"   ✅ Signed URL generated successfully")
        print(f"   🔗 URL: {signed_url[:100]}...")
        
        # Check if URL contains required parameters
        required_params = ['AWSAccessKeyId', 'Signature', 'Expires']
        missing_params = [param for param in required_params if param not in signed_url]
        if not missing_params:
            print(f"   ✅ Signed URL contains all required parameters")
        else:
            print(f"   ❌ Missing parameters: {missing_params}")
            
    except Exception as e:
        print(f"   ❌ Error generating signed URL: {e}")
    
    # Test with existing prescription PDFs
    print(f"\n📄 Testing with Existing Prescription PDFs...")
    try:
        pdfs = PrescriptionPDF.objects.all()[:3]
        print(f"   Found {pdfs.count()} prescription PDFs")
        
        for pdf in pdfs:
            if pdf.pdf_file:
                print(f"   📄 PDF {pdf.id}: {pdf.pdf_file.name}")
                
                # Generate signed URL
                try:
                    signed_url = generate_signed_url(str(pdf.pdf_file))
                    print(f"      ✅ Signed URL: {signed_url[:80]}...")
                except Exception as e:
                    print(f"      ❌ Error generating signed URL: {e}")
            else:
                print(f"   📄 PDF {pdf.id}: No file attached")
                
    except Exception as e:
        print(f"   ❌ Error testing prescription PDFs: {e}")

if __name__ == "__main__":
    test_upload_and_signed_url()
