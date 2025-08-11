# AWS Configuration Fix - AttributeError Resolution

## 🚨 **Issue Description**

The Django application was throwing an `AttributeError: 'Settings' object has no attribute 'AWS_LOCATION'` when trying to access the `/api/doctors/superadmin/` endpoint.

**Error Details:**
```
AttributeError at /api/doctors/superadmin/
'Settings' object has no attribute 'AWS_LOCATION'
Request Method: GET
Request URL: http://127.0.0.1:8000/api/doctors/superadmin/
```

## 🔍 **Root Cause Analysis**

### **1. Conditional AWS Settings**
- AWS settings were defined conditionally in `settings.py` based on `ALWAYS_UPLOAD_FILES_TO_AWS`
- When `ALWAYS_UPLOAD_FILES_TO_AWS = False`, AWS settings were not defined
- However, code was trying to access these settings at import time

### **2. Import-Time Access**
- Storage classes in `myproject/storage.py` were accessing `settings.AWS_LOCATION` at module import
- Signal files were also accessing AWS settings at import time
- This caused the error even when AWS was not configured

### **3. Multiple Affected Files**
- `myproject/storage.py` - Storage classes
- `authentication/signals.py` - File upload signals
- `authentication/utils.py` - AWS SNS functions
- Various other signal files

## 🛠️ **Solution Applied**

### **1. Created Safe AWS Settings Utility**
Created `myproject/aws_utils.py`:
```python
def get_aws_settings():
    """Safely get AWS settings, returning None for missing settings"""
    aws_config = {}
    
    # Check if AWS settings are available
    if not hasattr(settings, 'ALWAYS_UPLOAD_FILES_TO_AWS') or not settings.ALWAYS_UPLOAD_FILES_TO_AWS:
        return None
    
    # Get AWS settings safely
    aws_config['access_key_id'] = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    aws_config['secret_access_key'] = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
    aws_config['storage_bucket_name'] = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
    aws_config['s3_endpoint_url'] = getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
    aws_config['s3_region_name'] = getattr(settings, 'AWS_S3_REGION_NAME', None)
    aws_config['location'] = getattr(settings, 'AWS_LOCATION', None)
    
    return aws_config
```

### **2. Updated Storage Classes**
Modified `myproject/storage.py` to access settings lazily:
```python
def __init__(self, *args, **kwargs):
    # Access settings lazily to avoid AttributeError
    if hasattr(settings, 'AWS_LOCATION'):
        self.location = settings.AWS_LOCATION
    else:
        self.location = 'media'
    
    super().__init__(*args, **kwargs)
    
    # Force S3 storage configuration if AWS settings are available
    if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.endpoint_url = settings.AWS_S3_ENDPOINT_URL
        self.region_name = settings.AWS_S3_REGION_NAME
```

### **3. Updated Signal Files**
Modified signal files to use safe AWS settings:
```python
def upload_profile_picture_async(user_id):
    from myproject.aws_utils import get_aws_settings
    
    # Check if AWS is configured
    aws_config = get_aws_settings()
    if not aws_config:
        print("⚠️ AWS not configured, skipping upload")
        return
    
    # Use aws_config instead of direct settings access
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_config['access_key_id'],
        aws_secret_access_key=aws_config['secret_access_key'],
        endpoint_url=aws_config['s3_endpoint_url'],
        region_name=aws_config['s3_region_name']
    )
```

### **4. Fixed Analytics Views**
- Fixed indentation errors in `analytics/views.py`
- Added missing import for `PatientProfile`
- Ensured proper filtering for patients with profiles

## ✅ **Verification**

### **1. Syntax Check**
```bash
python -m py_compile analytics/views.py
# ✅ No syntax errors
```

### **2. Django Check**
```bash
python manage.py check
# ✅ No critical errors (only static file warnings)
```

### **3. Server Test**
```bash
python manage.py runserver 0.0.0.0:8000
# ✅ Server starts successfully
curl http://127.0.0.1:8000/api/doctors/superadmin/
# ✅ Returns authentication error (expected) instead of AWS error
```

## 📋 **Files Modified**

1. **`myproject/aws_utils.py`** - New utility for safe AWS settings access
2. **`myproject/storage.py`** - Updated storage classes for lazy loading
3. **`authentication/signals.py`** - Updated to use safe AWS settings
4. **`authentication/utils.py`** - Updated AWS SNS function
5. **`analytics/views.py`** - Fixed indentation and imports

## 🎯 **Benefits**

1. **Graceful Degradation** - App works with or without AWS configuration
2. **No Import Errors** - Settings accessed only when needed
3. **Better Error Handling** - Clear messages when AWS is not configured
4. **Maintainable Code** - Centralized AWS settings management
5. **Flexible Configuration** - Easy to switch between local and cloud storage

## 🔧 **Usage**

The fix allows the application to:
- Work in development without AWS configuration
- Work in production with AWS/DigitalOcean Spaces
- Gracefully handle missing AWS settings
- Provide clear feedback when AWS is not configured

**Status: ✅ RESOLVED**
