"""
Signals for automatic file upload to DigitalOcean Spaces
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Prescription
import threading
import boto3
import os

def upload_prescription_files_async(prescription_id):
    """
    Asynchronous function to upload prescription files to DigitalOcean Spaces
    """
    try:
        from prescriptions.models import Prescription
        
        # Get the prescription
        prescription = Prescription.objects.get(id=prescription_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload header if it exists
        if prescription.header and hasattr(prescription.header, 'path'):
            local_path = prescription.header.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{prescription.header.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded prescription header to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading prescription header: {e}")
        
        # Upload footer if it exists
        if prescription.footer and hasattr(prescription.footer, 'path'):
            local_path = prescription.footer.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{prescription.footer.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded prescription footer to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading prescription footer: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_prescription_files_async: {e}")

def upload_prescription_files_sync(prescription_id):
    """
    Synchronous function to upload prescription files to DigitalOcean Spaces immediately
    """
    try:
        from prescriptions.models import Prescription
        
        # Get the prescription
        prescription = Prescription.objects.get(id=prescription_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload header if it exists
        if prescription.header and hasattr(prescription.header, 'path'):
            local_path = prescription.header.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{prescription.header.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded prescription header to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading prescription header: {e}")
        
        # Upload footer if it exists
        if prescription.footer and hasattr(prescription.footer, 'path'):
            local_path = prescription.footer.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{prescription.footer.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded prescription footer to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading prescription footer: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_prescription_files_sync: {e}")

@receiver(post_save, sender=Prescription)
def upload_prescription_files_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload prescription files to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_prescription_files_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_prescription_files_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for prescription {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_prescription_files_to_spaces signal: {e}") 