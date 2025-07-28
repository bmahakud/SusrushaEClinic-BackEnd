#!/usr/bin/env python3
"""
Test script to verify AWS/DigitalOcean Spaces configuration
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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import boto3

def test_aws_configuration():
    """Test AWS configuration"""
    print("🔍 Testing AWS/DigitalOcean Spaces Configuration")
    print("=" * 60)
    
    # Check settings
    print(f"📁 ALWAYS_UPLOAD_FILES_TO_AWS: {settings.ALWAYS_UPLOAD_FILES_TO_AWS}")
    print(f"📁 AWS_ACCESS_KEY_ID: {settings.AWS_ACCESS_KEY_ID}")
    print(f"📁 AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"📁 AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}")
    print(f"📁 AWS_LOCATION: {settings.AWS_LOCATION}")
    print(f"📁 DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    print(f"📁 STATICFILES_STORAGE: {settings.STATICFILES_STORAGE}")
    print()
    
    # Test S3 client connection
    print("🧪 Testing S3 Client Connection...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # List buckets to test connection
        response = s3_client.list_buckets()
        print(f"✅ S3 Client connected successfully")
        print(f"📁 Available buckets: {[bucket['Name'] for bucket in response['Buckets']]}")
        
        # Test bucket access
        try:
            response = s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
            print(f"✅ Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' is accessible")
        except Exception as e:
            print(f"❌ Error accessing bucket: {e}")
            
    except Exception as e:
        print(f"❌ Error connecting to S3: {e}")
    
    print()
    
    # Test Django storage
    print("🧪 Testing Django Storage...")
    print(f"📁 Default storage class: {default_storage.__class__.__name__}")
    print(f"📁 Storage backend: {default_storage.__class__.__module__}")
    
    # Test file upload
    try:
        test_content = b"This is a test file for AWS configuration"
        test_filename = "test_aws_config.txt"
        
        # Upload file
        file_path = default_storage.save(test_filename, ContentFile(test_content))
        print(f"✅ File uploaded successfully: {file_path}")
        
        # Check if file exists
        if default_storage.exists(file_path):
            print(f"✅ File exists in storage")
        else:
            print(f"❌ File does not exist in storage")
        
        # Get file URL
        file_url = default_storage.url(file_path)
        print(f"📁 File URL: {file_url}")
        
        # Clean up
        default_storage.delete(file_path)
        print(f"🗑️ Test file deleted")
        
    except Exception as e:
        print(f"❌ Error testing file upload: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_aws_configuration() 