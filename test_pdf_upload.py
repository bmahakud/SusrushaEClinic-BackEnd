#!/usr/bin/env python3
"""
Test script to verify PDF generation and upload process
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
import boto3
import time

User = get_user_model()

def test_pdf_generation_and_upload():
    """Test PDF generation and upload process"""
    
    print("🔍 Testing PDF Generation and Upload Process")
    print("=" * 60)
    
    try:
        # Test 1: Check if we have a prescription to work with
        prescriptions = Prescription.objects.filter(is_finalized=True)[:1]
        
        if not prescriptions:
            print("📭 No finalized prescriptions found. Creating a test prescription...")
            
            # Create a test prescription
            users = User.objects.all()[:2]
            if len(users) >= 2:
                doctor = users[0]
                patient = users[1]
                
                prescription = Prescription.objects.create(
                    doctor=doctor,
                    patient=patient,
                    primary_diagnosis="Test diagnosis",
                    general_instructions="Test instructions",
                    is_draft=False,
                    is_finalized=True
                )
                print(f"✅ Created test prescription: {prescription.id}")
            else:
                print("❌ Need at least 2 users to create test prescription")
                return
        else:
            prescription = prescriptions[0]
            print(f"📄 Using existing prescription: {prescription.id}")
        
        print("\n" + "=" * 60)
        
        # Test 2: Generate PDF
        print("📄 Generating PDF...")
        
        try:
            pdf_instance = generate_prescription_pdf(
                prescription=prescription,
                user=prescription.doctor
            )
            
            print(f"✅ PDF generated successfully:")
            print(f"   - PDF ID: {pdf_instance.id}")
            print(f"   - Version: {pdf_instance.version_number}")
            print(f"   - File: {pdf_instance.pdf_file}")
            print(f"   - File Name: {pdf_instance.pdf_file.name}")
            print(f"   - File URL: {pdf_instance.pdf_file.url}")
            print(f"   - File Size: {pdf_instance.file_size} bytes")
            
        except Exception as e:
            print(f"❌ Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("\n" + "=" * 60)
        
        # Test 3: Verify file exists in S3
        print("🔍 Verifying file in S3...")
        
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Get the file key
            file_key = str(pdf_instance.pdf_file)
            if not file_key.startswith(f"{settings.AWS_LOCATION}/"):
                file_key = f"{settings.AWS_LOCATION}/{file_key}"
            
            print(f"   📁 Looking for file: {file_key}")
            
            # Wait a moment for S3 to process
            print("   ⏳ Waiting for S3 to process upload...")
            time.sleep(2)
            
            # Check if file exists
            try:
                response = s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
                print(f"   ✅ File found in S3!")
                print(f"   📊 File size in S3: {response['ContentLength']} bytes")
                print(f"   📅 Last modified: {response['LastModified']}")
                
            except Exception as s3_error:
                print(f"   ❌ File not found in S3: {s3_error}")
                
                # List files in the directory to see what's there
                print("   🔍 Listing files in the directory...")
                try:
                    prefix = f"{settings.AWS_LOCATION}/prescriptions/pdfs/"
                    response = s3_client.list_objects_v2(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Prefix=prefix,
                        MaxKeys=10
                    )
                    
                    if 'Contents' in response:
                        print(f"   📁 Found {len(response['Contents'])} files:")
                        for obj in response['Contents']:
                            print(f"      - {obj['Key']}")
                    else:
                        print("   📭 No files found in directory")
                        
                except Exception as list_error:
                    print(f"   ❌ Error listing files: {list_error}")
                
        except Exception as e:
            print(f"❌ Error accessing S3: {e}")
        
        print("\n" + "=" * 60)
        
        # Test 4: Generate signed URL
        print("🔗 Generating signed URL...")
        
        try:
            file_key = str(pdf_instance.pdf_file)
            if not file_key.startswith(f"{settings.AWS_LOCATION}/"):
                file_key = f"{settings.AWS_LOCATION}/{file_key}"
            
            signed_url = generate_signed_url(file_key, expiration=3600)
            print(f"   ✅ Signed URL generated:")
            print(f"   🔗 {signed_url[:100]}...")
            
            # Test if the URL works
            import requests
            try:
                response = requests.head(signed_url, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ Signed URL is accessible (Status: {response.status_code})")
                else:
                    print(f"   ⚠️  Signed URL returned status: {response.status_code}")
            except Exception as url_error:
                print(f"   ❌ Error accessing signed URL: {url_error}")
                
        except Exception as e:
            print(f"❌ Error generating signed URL: {e}")
        
        print("\n" + "=" * 60)
        print("🏁 Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation_and_upload() 