#!/usr/bin/env python3
"""
Script to upload existing clinic files to DigitalOcean Spaces
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from eclinic.models import Clinic
from django.conf import settings
from django.db import models
import boto3

def upload_existing_files():
    """Upload existing clinic files to DigitalOcean Spaces"""
    print("📤 Uploading Existing Clinic Files to DigitalOcean Spaces")
    print("=" * 60)
    
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Get all clinics with files
        clinics = Clinic.objects.filter(
            models.Q(logo__isnull=False, logo__gt='') | 
            models.Q(cover_image__isnull=False, cover_image__gt='')
        )
        
        print(f"📁 Found {clinics.count()} clinics with files")
        
        uploaded_count = 0
        
        for clinic in clinics:
            print(f"\n🏥 Processing clinic: {clinic.name} (ID: {clinic.id})")
            
            # Upload logo if it exists
            if clinic.logo and hasattr(clinic.logo, 'path'):
                local_path = clinic.logo.path
                if os.path.exists(local_path):
                    remote_key = f"{settings.AWS_LOCATION}/{clinic.logo.name}"
                    try:
                        # Check if file already exists on DigitalOcean Spaces
                        try:
                            s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=remote_key)
                            print(f"   ✅ Logo already exists on DigitalOcean Spaces: {remote_key}")
                        except:
                            # Upload file
                            s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                            # Make file public
                            s3_client.put_object_acl(
                                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                Key=remote_key,
                                ACL='public-read'
                            )
                            print(f"   ✅ Uploaded logo to DigitalOcean Spaces: {remote_key}")
                            uploaded_count += 1
                    except Exception as e:
                        print(f"   ❌ Error uploading logo: {e}")
                else:
                    print(f"   ⚠️ Logo file not found locally: {local_path}")
            
            # Upload cover image if it exists
            if clinic.cover_image and hasattr(clinic.cover_image, 'path'):
                local_path = clinic.cover_image.path
                if os.path.exists(local_path):
                    remote_key = f"{settings.AWS_LOCATION}/{clinic.cover_image.name}"
                    try:
                        # Check if file already exists on DigitalOcean Spaces
                        try:
                            s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=remote_key)
                            print(f"   ✅ Cover image already exists on DigitalOcean Spaces: {remote_key}")
                        except:
                            # Upload file
                            s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                            # Make file public
                            s3_client.put_object_acl(
                                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                Key=remote_key,
                                ACL='public-read'
                            )
                            print(f"   ✅ Uploaded cover image to DigitalOcean Spaces: {remote_key}")
                            uploaded_count += 1
                    except Exception as e:
                        print(f"   ❌ Error uploading cover image: {e}")
                else:
                    print(f"   ⚠️ Cover image file not found locally: {local_path}")
        
        print(f"\n🎉 Upload complete! Uploaded {uploaded_count} new files to DigitalOcean Spaces")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    upload_existing_files() 