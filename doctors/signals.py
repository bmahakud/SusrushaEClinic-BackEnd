"""
Signals for automatic file upload to DigitalOcean Spaces
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import DoctorProfile, DoctorDocument, DoctorEducation
import threading
import boto3
import os

def upload_doctor_education_async(education_id):
    """
    Asynchronous function to upload doctor education certificate to DigitalOcean Spaces
    """
    try:
        from doctors.models import DoctorEducation
        
        # Get the education
        education = DoctorEducation.objects.get(id=education_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload certificate if it exists
        if education.certificate and hasattr(education.certificate, 'path'):
            local_path = education.certificate.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{education.certificate.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded doctor education certificate to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading doctor education certificate: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_doctor_education_async: {e}")

def upload_doctor_education_sync(education_id):
    """
    Synchronous function to upload doctor education certificate to DigitalOcean Spaces immediately
    """
    try:
        from doctors.models import DoctorEducation
        
        # Get the education
        education = DoctorEducation.objects.get(id=education_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload certificate if it exists
        if education.certificate and hasattr(education.certificate, 'path'):
            local_path = education.certificate.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{education.certificate.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded doctor education certificate to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading doctor education certificate: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_doctor_education_sync: {e}")

def upload_doctor_document_async(document_id):
    """
    Asynchronous function to upload doctor document to DigitalOcean Spaces
    """
    try:
        from doctors.models import DoctorDocument
        
        # Get the document
        document = DoctorDocument.objects.get(id=document_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload document if it exists
        if document.file and hasattr(document.file, 'path'):
            local_path = document.file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{document.file.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded doctor document to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading doctor document: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_doctor_document_async: {e}")

def upload_doctor_document_sync(document_id):
    """
    Synchronous function to upload doctor document to DigitalOcean Spaces immediately
    """
    try:
        from doctors.models import DoctorDocument
        
        # Get the document
        document = DoctorDocument.objects.get(id=document_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload document if it exists
        if document.file and hasattr(document.file, 'path'):
            local_path = document.file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{document.file.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded doctor document to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading doctor document: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_doctor_document_sync: {e}")

@receiver(post_save, sender=DoctorEducation)
def upload_doctor_education_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload doctor education certificate to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_doctor_education_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_doctor_education_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for doctor education {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_doctor_education_to_spaces signal: {e}")

@receiver(post_save, sender=DoctorDocument)
def upload_doctor_document_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload doctor document to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_doctor_document_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_doctor_document_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for doctor document {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_doctor_document_to_spaces signal: {e}") 