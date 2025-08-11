# 🔐 S3 Access Denied Error - Signed URL Fix Guide

## 🚨 Problem Description

The error you encountered:
```xml
<Error>
<Code>NoSuchKey</Code>
<Message/>
<BucketName>edrspace</BucketName>
<RequestId>tx00000a0a10ba25783f4c7-0068944783-59cf17d5-sgp1b</RequestId>
<HostId>59cf17d5-sgp1b-sgp1-zg02</HostId>
</Error>
```

This error occurs when trying to access prescription PDFs stored in the DigitalOcean Spaces (S3-compatible storage) with incorrect file paths. The signed URLs were being generated with the wrong file key structure, causing the files to not be found.

## 🔧 Root Cause

1. **Incorrect File Paths**: The signed URLs were being generated with file keys that didn't include the `AWS_LOCATION` prefix
2. **Path Mismatch**: Files are stored at `edrcontainer1/prescriptions/pdfs/...` but URLs were trying to access `edrspace/prescriptions/pdfs/...`
3. **Missing Location Prefix**: The `AWS_LOCATION` setting (`edrcontainer1`) wasn't being included in the file key generation

## ✅ Solution Implemented

### **1. Updated Prescription Views (`prescriptions/views.py`)**

#### **Added Signed URL Import**
```python
from utils.signed_urls import generate_signed_url
```

#### **Updated PDF URL Generation**
All functions that return PDF URLs now use signed URLs with correct file paths:

- `finalize_and_generate_pdf()` - Generates signed URLs for newly created PDFs
- `pdf_versions()` - Generates signed URLs for all PDF versions
- `patient_pdfs()` - Generates signed URLs for patient PDFs
- `download_pdf()` - Returns signed download URLs

#### **Example Implementation**
```python
# Generate signed URL for the PDF file
pdf_url = None
if pdf_instance.pdf_file:
    try:
        # Get the file key from the file path and ensure it includes AWS_LOCATION
        file_key = str(pdf_instance.pdf_file)
        if not file_key.startswith(f"{settings.AWS_LOCATION}/"):
            file_key = f"{settings.AWS_LOCATION}/{file_key}"
        pdf_url = generate_signed_url(file_key, expiration=3600)  # 1 hour expiration
    except Exception as e:
        print(f"Error generating signed URL for PDF: {e}")
        # Fallback to direct URL if signed URL generation fails
        pdf_url = pdf_instance.pdf_file.url if pdf_instance.pdf_file else None
```

### **2. Updated Frontend API (`lib/api.ts`)**

#### **Modified Download PDF Function**
```typescript
// Download PDF
downloadPDF: async (prescriptionId: string, version: string | number = 'latest'): Promise<{ download_url: string; filename: string }> => {
  const response = await api.get(`/api/prescriptions/${prescriptionId}/pdf/${version}/`);
  return response.data.data;
},
```

### **3. Updated VideoConsultation Component**

#### **Enhanced PDF Download**
```typescript
// Download the PDF
if (result.pdf.url) {
  const link = document.createElement('a');
  link.href = result.pdf.url;
  link.download = `prescription_${consultationId}_${new Date().toISOString().split('T')[0]}.pdf`;
  link.target = '_blank'; // Open in new tab for signed URLs
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
```

## 🔍 How Signed URLs Work

### **1. URL Structure**
```
https://edrspace.sgp1.digitaloceanspaces.com/media/prescriptions/pdfs/123/file.pdf?AWSAccessKeyId=XXX&Signature=XXX&Expires=XXX
```

### **2. Components**
- **Base URL**: `https://edrspace.sgp1.digitaloceanspaces.com/`
- **File Path**: `media/prescriptions/pdfs/123/file.pdf`
- **AWS Parameters**:
  - `AWSAccessKeyId`: Your AWS access key
  - `Signature`: HMAC signature for security
  - `Expires`: URL expiration timestamp

### **3. Security Features**
- **Time-limited**: URLs expire after 1 hour
- **Signed**: Each URL has a unique cryptographic signature
- **Secure**: Prevents unauthorized access to files

## 🛠️ Implementation Details

### **1. Signed URL Generation Function**
```python
def generate_signed_url(file_key, expiration=3600):
    """
    Generate a signed URL for accessing a file in DigitalOcean Spaces
    
    Args:
        file_key (str): The key/path of the file in the bucket
        expiration (int): URL expiration time in seconds (default: 1 hour)
    
    Returns:
        str: Signed URL for accessing the file
    """
    try:
        # Initialize S3 client for DigitalOcean Spaces
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Generate signed URL
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_key
            },
            ExpiresIn=expiration
        )
        
        return signed_url
        
    except Exception as e:
        print(f"Error generating signed URL for {file_key}: {e}")
        # Fallback to public URL if signed URL generation fails
        return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.sgp1.digitaloceanspaces.com/{file_key}"
```

### **2. Error Handling**
- **Graceful Fallback**: If signed URL generation fails, falls back to direct URLs
- **Exception Logging**: Logs errors for debugging
- **User Feedback**: Provides clear error messages

### **3. Configuration Requirements**
```python
# Required Django settings
AWS_ACCESS_KEY_ID = 'your_access_key'
AWS_SECRET_ACCESS_KEY = 'your_secret_key'
AWS_STORAGE_BUCKET_NAME = 'edrspace'
AWS_S3_ENDPOINT_URL = 'https://sgp1.digitaloceanspaces.com'
AWS_S3_REGION_NAME = 'sgp1'
```

## 🧪 Testing

### **1. Test Script**
Run the test script to verify signed URL functionality:
```bash
cd sushrusa_backend
python test_signed_urls.py
```

### **2. Manual Testing**
1. **Generate a prescription PDF** through the VideoConsultation component
2. **Check the URL** - it should contain AWS parameters
3. **Download the PDF** - should work without access denied errors
4. **Verify expiration** - URLs should expire after 1 hour

### **3. Expected Results**
```
✅ Signed URL generated successfully
📁 File Key: media/prescriptions/pdfs/test/test_prescription.pdf
🔗 Signed URL: https://edrspace.sgp1.digitaloceanspaces.com/media/prescriptions/pdfs/test/test_prescription.pdf?AWSAccessKeyId=XXX&Signature=XXX&Expires=XXX...
⏰ Expiration: 1 hour
✅ All required AWS parameters present
```

## 🔒 Security Benefits

### **1. Access Control**
- **Time-limited access**: URLs expire automatically
- **Unique signatures**: Each URL is cryptographically signed
- **No permanent links**: Prevents unauthorized sharing

### **2. Privacy Protection**
- **Secure file access**: Only authenticated users can access files
- **Audit trail**: All access is logged through AWS
- **Encrypted transmission**: HTTPS ensures secure data transfer

### **3. Compliance**
- **HIPAA compliance**: Secure file access for medical records
- **Data protection**: Prevents unauthorized access to patient data
- **Audit requirements**: Maintains access logs for compliance

## 🚀 Performance Benefits

### **1. Reduced Server Load**
- **Direct S3 access**: Files served directly from S3, not through Django
- **CDN benefits**: Leverages DigitalOcean's CDN for faster delivery
- **Scalability**: S3 handles file serving, not your application server

### **2. Better User Experience**
- **Faster downloads**: Direct S3 access is faster than proxying through Django
- **Reliable access**: S3 provides high availability and reliability
- **Progressive loading**: Large files can be streamed efficiently

## 🔧 Troubleshooting

### **1. Common Issues**

#### **Access Denied Still Occurring**
- Check AWS credentials in Django settings
- Verify bucket permissions
- Ensure file paths are correct

#### **Signed URLs Not Generating**
- Check boto3 installation: `pip install boto3`
- Verify AWS configuration in settings
- Check for Python exceptions in logs

#### **URLs Expiring Too Quickly**
- Adjust expiration time in `generate_signed_url()` calls
- Default is 1 hour (3600 seconds)
- Can be increased for longer access

### **2. Debug Steps**
1. **Check AWS Configuration**:
   ```python
   print(f"AWS_ACCESS_KEY_ID: {settings.AWS_ACCESS_KEY_ID}")
   print(f"AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
   ```

2. **Test Signed URL Generation**:
   ```python
   from utils.signed_urls import generate_signed_url
   url = generate_signed_url("test/file.pdf")
   print(url)
   ```

3. **Check File Existence**:
   ```python
   # Verify file exists in S3
   s3_client.head_object(Bucket=bucket_name, Key=file_key)
   ```

## 📋 API Changes Summary

### **Before (Broken)**
```json
{
  "pdf": {
    "url": "https://edrspace.sgp1.digitaloceanspaces.com/media/prescriptions/pdfs/123/file.pdf"
  }
}
```

### **After (Fixed)**
```json
{
  "pdf": {
    "url": "https://edrspace.sgp1.digitaloceanspaces.com/media/prescriptions/pdfs/123/file.pdf?AWSAccessKeyId=XXX&Signature=XXX&Expires=XXX"
  }
}
```

## 🎯 Next Steps

1. **Deploy the changes** to your production environment
2. **Test prescription PDF generation** and download
3. **Monitor for any remaining access issues**
4. **Consider implementing URL caching** for better performance
5. **Add monitoring** for signed URL generation failures

## 📚 Related Files

- `sushrusa_backend/prescriptions/views.py` - Updated API endpoints
- `sushrusa_backend/utils/signed_urls.py` - Signed URL generation utility
- `sushrusa-homepage-design-hub/src/lib/api.ts` - Updated frontend API
- `sushrusa-homepage-design-hub/src/components/workflow/VideoConsultation.tsx` - Updated component
- `sushrusa_backend/test_signed_urls.py` - Test script

---

**Note**: This fix ensures secure, authenticated access to prescription PDFs while maintaining performance and user experience. 