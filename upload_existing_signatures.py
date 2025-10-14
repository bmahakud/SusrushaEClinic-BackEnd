"""
Script to upload existing doctor signatures to DigitalOcean Spaces
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings
from doctors.models import DoctorProfile
import boto3

def upload_existing_signatures():
    """Upload all existing doctor signatures to DigitalOcean Spaces"""
    
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    # Get all doctor profiles with signatures
    profiles_with_signatures = DoctorProfile.objects.exclude(signature='').exclude(signature=None)
    
    print(f"\n📋 Found {profiles_with_signatures.count()} doctor profiles with signatures")
    
    upload_count = 0
    error_count = 0
    
    for profile in profiles_with_signatures:
        try:
            if profile.signature:
                # Try to get the path - handle both FileField and string paths
                try:
                    local_path = profile.signature.path
                except Exception:
                    # If path fails, construct it from MEDIA_ROOT and signature name
                    local_path = os.path.join(settings.MEDIA_ROOT, str(profile.signature))
                
                # Get the signature name for the remote key
                signature_name = str(profile.signature)
                
                if os.path.exists(local_path):
                    remote_key = f"{settings.AWS_LOCATION}/{signature_name}"
                    
                    try:
                        # Upload file
                        s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                        
                        # Make file public
                        s3_client.put_object_acl(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            Key=remote_key,
                            ACL='public-read'
                        )
                        
                        print(f"✅ Uploaded signature for Dr. {profile.user.name}: {remote_key}")
                        upload_count += 1
                        
                    except Exception as e:
                        print(f"❌ Error uploading signature for Dr. {profile.user.name}: {e}")
                        error_count += 1
                else:
                    print(f"⚠️  Local file not found for Dr. {profile.user.name}: {local_path}")
                    error_count += 1
                    
        except Exception as e:
            print(f"❌ Error processing signature for profile {profile.id}: {e}")
            error_count += 1
    
    print(f"\n📊 Upload Summary:")
    print(f"   ✅ Successfully uploaded: {upload_count}")
    print(f"   ❌ Errors: {error_count}")
    print(f"   📋 Total processed: {profiles_with_signatures.count()}")

if __name__ == '__main__':
    print("🚀 Starting doctor signature upload to DigitalOcean Spaces...")
    upload_existing_signatures()
    print("✨ Done!")

