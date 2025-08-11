#!/usr/bin/env python3
"""
Test script to verify file path construction for prescription PDFs
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
from utils.signed_urls import generate_signed_url
from prescriptions.models import PrescriptionPDF

def test_file_path_construction():
    """Test file path construction for prescription PDFs"""
    
    print("🔍 Testing File Path Construction for Prescription PDFs")
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
        pdf_instances = PrescriptionPDF.objects.all()[:3]  # Get first 3 PDFs
        
        if pdf_instances:
            print(f"📊 Found {pdf_instances.count()} prescription PDFs")
            
            for i, pdf in enumerate(pdf_instances, 1):
                print(f"\n📄 PDF {i}:")
                print(f"   ID: {pdf.id}")
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
    
    # Test 3: Test with sample file paths
    print("🧪 Testing Sample File Paths:")
    sample_paths = [
        "prescriptions/pdfs/CON068/5725f4bfb1f04b89b71eb70c5642461e.pdf",
        "media/prescriptions/pdfs/CON068/5725f4bfb1f04b89b71eb70c5642461e.pdf",
        f"{settings.AWS_LOCATION}/prescriptions/pdfs/CON068/5725f4bfb1f04b89b71eb70c5642461e.pdf",
    ]
    
    for i, sample_path in enumerate(sample_paths, 1):
        print(f"\n   📁 Sample Path {i}: {sample_path}")
        try:
            signed_url = generate_signed_url(sample_path, expiration=3600)
            print(f"   ✅ Signed URL: {signed_url[:100]}...")
            
            # Check if URL contains the correct bucket and location
            if settings.AWS_STORAGE_BUCKET_NAME in signed_url and settings.AWS_LOCATION in signed_url:
                print(f"   ✅ URL contains correct bucket and location")
            else:
                print(f"   ⚠️  URL may not contain correct bucket/location")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_file_path_construction() 