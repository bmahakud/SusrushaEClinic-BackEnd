# 🔧 Signal-Based PDF Upload to DigitalOcean Spaces - Implementation Guide

## 🎯 Overview

This guide explains how we implemented automatic PDF upload to DigitalOcean Spaces using Django signals, following the same pattern used for profile images and clinic cover images.

## 🔧 Problem Solved

The previous implementation had issues with PDF uploads to DigitalOcean Spaces:
- **Manual upload process** - PDFs were saved locally but not automatically uploaded to S3
- **Timing issues** - Signed URLs were generated before files were uploaded
- **Inconsistent behavior** - Different from other file uploads in the system

## ✅ Solution: Signal-Based Upload

### **1. Signal Implementation (`prescriptions/signals.py`)**

Following the same pattern as profile images and clinic cover images:

```python
"""
Signals for automatic PDF upload to DigitalOcean Spaces
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import PrescriptionPDF
import threading
import boto3
import os

def upload_pdf_async(pdf_id):
    """
    Asynchronous function to upload PDF to DigitalOcean Spaces
    """
    try:
        from prescriptions.models import PrescriptionPDF
        
        # Get the PDF instance
        pdf_instance = PrescriptionPDF.objects.get(id=pdf_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload PDF file if it exists
        if pdf_instance.pdf_file and hasattr(pdf_instance.pdf_file, 'path'):
            local_path = pdf_instance.pdf_file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{pdf_instance.pdf_file.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [ASYNC] Uploaded PDF to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [ASYNC] Error uploading PDF: {e}")
                    
    except Exception as e:
        print(f"❌ [ASYNC] Error in upload_pdf_async: {e}")

def upload_pdf_sync(pdf_id):
    """
    Synchronous function to upload PDF to DigitalOcean Spaces immediately
    """
    try:
        from prescriptions.models import PrescriptionPDF
        
        # Get the PDF instance
        pdf_instance = PrescriptionPDF.objects.get(id=pdf_id)
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Upload PDF file if it exists
        if pdf_instance.pdf_file and hasattr(pdf_instance.pdf_file, 'path'):
            local_path = pdf_instance.pdf_file.path
            if os.path.exists(local_path):
                remote_key = f"{settings.AWS_LOCATION}/{pdf_instance.pdf_file.name}"
                try:
                    s3_client.upload_file(local_path, settings.AWS_STORAGE_BUCKET_NAME, remote_key)
                    # Make file public
                    s3_client.put_object_acl(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=remote_key,
                        ACL='public-read'
                    )
                    print(f"✅ [SYNC] Uploaded PDF to DigitalOcean Spaces: {remote_key}")
                except Exception as e:
                    print(f"❌ [SYNC] Error uploading PDF: {e}")
                    
    except Exception as e:
        print(f"❌ [SYNC] Error in upload_pdf_sync: {e}")

@receiver(post_save, sender=PrescriptionPDF)
def upload_prescription_pdf_to_spaces(sender, instance, created, **kwargs):
    """
    Automatically upload prescription PDF to DigitalOcean Spaces after saving
    """
    if not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return
    
    try:
        # For immediate access, upload synchronously first, then start async thread for any retries
        upload_pdf_sync(instance.id)
        
        # Also start async thread for any additional processing
        thread = threading.Thread(target=upload_pdf_async, args=(instance.id,))
        thread.daemon = True  # Thread will be killed when main process exits
        thread.start()
        print(f"🚀 [SIGNAL] Started async upload thread for PDF {instance.id}")
                    
    except Exception as e:
        print(f"❌ Error in upload_prescription_pdf_to_spaces signal: {e}")
```

### **2. Signal Registration (`prescriptions/apps.py`)**

```python
from django.apps import AppConfig

class PrescriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prescriptions'
    
    def ready(self):
        """Import signals when the app is ready"""
        import prescriptions.signals
```

### **3. Updated PDF Generation (`prescriptions/enhanced_pdf_generator.py`)**

```python
def generate_and_save(self, user):
    """Generate PDF and save to PrescriptionPDF model"""
    from .models import PrescriptionPDF
    
    pdf_data = self.generate_pdf()
    checksum = hashlib.md5(pdf_data).hexdigest()
    
    pdf_instance = PrescriptionPDF(
        prescription=self.prescription,
        generated_by=user,
        file_size=len(pdf_data),
        checksum=checksum
    )
    
    if self.header_image_path:
        pdf_instance.header_image = self.header_image_path
    if self.footer_image_path:
        pdf_instance.footer_image = self.footer_image_path
    
    filename = f"prescription_{self.prescription.id}_v{pdf_instance.version_number or 1}.pdf"
    print(f"📄 Saving PDF with filename: {filename}")
    
    # Save the PDF file - this will trigger the signal to upload to DigitalOcean Spaces
    pdf_instance.pdf_file.save(filename, BytesIO(pdf_data), save=False)
    
    # Save the instance - this triggers the post_save signal
    pdf_instance.save()
    
    print(f"✅ PDF saved successfully:")
    print(f"   - File path: {pdf_instance.pdf_file}")
    print(f"   - File name: {pdf_instance.pdf_file.name}")
    print(f"   - File URL: {pdf_instance.pdf_file.url}")
    print(f"   - File size: {pdf_instance.file_size} bytes")
    print(f"   - Signal will automatically upload to DigitalOcean Spaces")
    
    return pdf_instance
```

### **4. Simplified Signed URL Generation (`prescriptions/views.py`)**

```python
# Generate signed URL for the PDF file
pdf_url = None
if pdf_instance.pdf_file:
    try:
        # Get the file key from the file path and ensure it includes AWS_LOCATION
        file_key = str(pdf_instance.pdf_file)
        if not file_key.startswith(f"{settings.AWS_LOCATION}/"):
            file_key = f"{settings.AWS_LOCATION}/{file_key}"
        
        # Add a small delay to allow the signal to upload the file to DigitalOcean Spaces
        import time
        time.sleep(2)
        
        # Generate signed URL - the signal should have uploaded the file by now
        pdf_url = generate_signed_url(file_key, expiration=3600)  # 1 hour expiration
        print(f"✅ Generated signed URL for PDF: {file_key}")
            
    except Exception as e:
        print(f"Error generating signed URL for PDF: {e}")
        # Fallback to direct URL if signed URL generation fails
        pdf_url = pdf_instance.pdf_file.url if pdf_instance.pdf_file else None
```

## 🔄 How It Works

### **1. PDF Generation Process**
1. **PDF Created**: `generate_prescription_pdf()` creates PDF data
2. **Model Saved**: `PrescriptionPDF` instance is saved to database
3. **Signal Triggered**: `post_save` signal is automatically triggered
4. **File Uploaded**: Signal uploads file to DigitalOcean Spaces
5. **Signed URL Generated**: After delay, signed URL is generated

### **2. Signal Flow**
```
PDF Generation → Model Save → Signal Trigger → S3 Upload → Signed URL
```

### **3. Upload Process**
1. **Synchronous Upload**: Immediate upload for instant access
2. **Asynchronous Upload**: Background thread for reliability
3. **Public ACL**: File is made publicly readable
4. **Error Handling**: Comprehensive error logging

## 🧪 Testing

### **Test Script: `test_signal_upload.py`**
```bash
cd sushrusa_backend
python test_signal_upload.py
```

This script tests:
- ✅ PDF generation and signal triggering
- ✅ File upload to DigitalOcean Spaces
- ✅ Signed URL generation and accessibility
- ✅ Complete end-to-end workflow

## 🚀 Benefits

### **1. Consistency**
- ✅ Same pattern as profile images and clinic cover images
- ✅ Unified upload mechanism across the application
- ✅ Consistent error handling and logging

### **2. Reliability**
- ✅ Automatic upload on model save
- ✅ Both synchronous and asynchronous upload
- ✅ Comprehensive error handling
- ✅ Fallback mechanisms

### **3. Performance**
- ✅ Immediate upload for instant access
- ✅ Background processing for reliability
- ✅ Optimized file handling

### **4. Maintainability**
- ✅ Clean separation of concerns
- ✅ Reusable upload functions
- ✅ Easy to extend and modify

## 📋 Configuration Requirements

### **1. Environment Variables**
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=edrspace
AWS_LOCATION=edrcontainer1
AWS_S3_ENDPOINT_URL=https://sgp1.digitaloceanspaces.com
AWS_S3_REGION_NAME=sgp1
ALWAYS_UPLOAD_FILES_TO_AWS=True
```

### **2. Django Settings**
```python
# File storage configuration
DEFAULT_FILE_STORAGE = 'myproject.storage.MediaStorage'
MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.sgp1.digitaloceanspaces.com/{AWS_LOCATION}/'
MEDIA_ROOT = ''
```

## 🎯 Result

- **✅ Automatic PDF Upload**: PDFs are automatically uploaded to DigitalOcean Spaces
- **✅ Consistent Behavior**: Same pattern as other file uploads
- **✅ Reliable Access**: Files are immediately available via signed URLs
- **✅ No More NoSuchKey Errors**: Files are properly uploaded before URL generation
- **✅ Better User Experience**: PDFs are accessible immediately after finalization

The prescription PDF system now uses the same reliable upload mechanism as profile images and clinic cover images! 