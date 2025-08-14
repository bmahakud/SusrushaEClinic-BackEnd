#!/usr/bin/env python
"""
Test script to verify DigitalOcean Spaces upload is working
"""

import os
import django
import tempfile

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import boto3

def test_storage_upload():
    """Test if files are being uploaded to DigitalOcean Spaces"""
    print("🔍 Testing DigitalOcean Spaces Upload")
    
    # Check settings
    print(f"📋 Storage Settings:")
    print(f"   ALWAYS_UPLOAD_FILES_TO_AWS: {settings.ALWAYS_UPLOAD_FILES_TO_AWS}")
    print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"   AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
    print(f"   AWS_LOCATION: {getattr(settings, 'AWS_LOCATION', 'edrcontainer1')}")
    
    # Test 1: Check if storage is configured correctly
    print(f"\n🔧 Testing Storage Configuration...")
    try:
        storage = default_storage
        print(f"   ✅ Default storage: {type(storage).__name__}")
        print(f"   📁 Storage location: {getattr(storage, 'location', 'Not set')}")
        print(f"   🪣 Bucket name: {getattr(storage, 'bucket_name', 'Not set')}")
    except Exception as e:
        print(f"   ❌ Error with storage: {e}")
        return
    
    # Test 2: Upload a test file
    print(f"\n📤 Testing File Upload...")
    try:
        # Create a test file
        test_content = "This is a test file for DigitalOcean Spaces upload"
        test_filename = f"test_upload_{os.getpid()}.txt"
        
        # Upload using default storage
        file_path = default_storage.save(test_filename, ContentFile(test_content.encode()))
        print(f"   ✅ File uploaded successfully")
        print(f"   📄 File path: {file_path}")
        
        # Check if file exists in storage
        if default_storage.exists(file_path):
            print(f"   ✅ File exists in storage")
            
            # Read the file back
            with default_storage.open(file_path, 'r') as f:
                content = f.read()
                print(f"   ✅ File content matches: {content == test_content}")
        else:
            print(f"   ❌ File does not exist in storage")
            
    except Exception as e:
        print(f"   ❌ Error uploading file: {e}")
        return
    
    # Test 3: Check S3 directly
    print(f"\n🔍 Checking S3 Directly...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # List objects in the bucket
        response = s3_client.list_objects_v2(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Prefix=getattr(settings, 'AWS_LOCATION', 'edrcontainer1'),
            MaxKeys=10
        )
        
        if 'Contents' in response:
            print(f"   ✅ Found {len(response['Contents'])} objects in bucket")
            for obj in response['Contents'][:5]:
                print(f"      - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print(f"   ⚠️  No objects found in bucket")
            
        # Check if our test file is there
        aws_location = getattr(settings, 'AWS_LOCATION', 'edrcontainer1')
        test_key = f"{aws_location}/{test_filename}"
        try:
            s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=test_key)
            print(f"   ✅ Test file found in S3: {test_key}")
        except:
            print(f"   ❌ Test file not found in S3: {test_key}")
            
    except Exception as e:
        print(f"   ❌ Error checking S3: {e}")
    
    # Clean up test file
    try:
        default_storage.delete(test_filename)
        print(f"\n🧹 Cleaned up test file")
    except:
        pass

if __name__ == "__main__":
    test_storage_upload()
