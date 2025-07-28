    #!/usr/bin/env python3
"""
Script to upload frontend build files to DigitalOcean Spaces
"""

import os
import boto3
from pathlib import Path
import mimetypes

# DigitalOcean Spaces configuration
AWS_ACCESS_KEY_ID = 'UCW66UXZOVY3QVYQLSEK'
AWS_SECRET_ACCESS_KEY = 'TJi4SulSCtEU5RlHWsKkOpFoL0Qo/qVf5JB6Dcg8rWk'
AWS_STORAGE_BUCKET_NAME = 'edrspace'
AWS_S3_ENDPOINT_URL = 'https://sgp1.digitaloceanspaces.com'
AWS_LOCATION = 'edrcontainer1'

def upload_file_to_spaces(file_path, s3_key, s3_client, bucket_name):
    """Upload a single file to DigitalOcean Spaces"""
    try:
        # Determine content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Upload file
        with open(file_path, 'rb') as file:
            s3_client.upload_fileobj(
                file,
                bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read',
                    'CacheControl': 'max-age=86400'
                }
            )
        print(f"✅ Uploaded: {s3_key}")
        return True
    except Exception as e:
        print(f"❌ Failed to upload {s3_key}: {e}")
        return False

def upload_directory_to_spaces(local_dir, s3_prefix, s3_client, bucket_name):
    """Upload all files from a directory to DigitalOcean Spaces"""
    local_path = Path(local_dir)
    
    if not local_path.exists():
        print(f"❌ Directory does not exist: {local_dir}")
        return False
    
    success_count = 0
    total_count = 0
    
    for file_path in local_path.rglob('*'):
        if file_path.is_file():
            # Calculate S3 key
            relative_path = file_path.relative_to(local_path)
            s3_key = f"{s3_prefix}/{relative_path}"
            
            total_count += 1
            if upload_file_to_spaces(str(file_path), s3_key, s3_client, bucket_name):
                success_count += 1
    
    print(f"\n📊 Upload Summary: {success_count}/{total_count} files uploaded successfully")
    return success_count == total_count

def main():
    """Main function to upload frontend build files"""
    print("🚀 Starting frontend build upload to DigitalOcean Spaces...")
    
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        endpoint_url=AWS_S3_ENDPOINT_URL,
        region_name='sgp1'
    )
    
    # Frontend build directory
    frontend_build_dir = Path("/home/tushar/Videos/sushrusa-homepage-design-hub/dist")
    
    if not frontend_build_dir.exists():
        print(f"❌ Frontend build directory not found: {frontend_build_dir}")
        print("Please run 'npm run build' in the frontend directory first.")
        return
    
    # Upload static files
    print(f"\n📁 Uploading static files from: {frontend_build_dir}")
    success = upload_directory_to_spaces(
        frontend_build_dir,
        f"{AWS_LOCATION}/static",
        s3_client,
        AWS_STORAGE_BUCKET_NAME
    )
    
    if success:
        print(f"\n🎉 Frontend build uploaded successfully!")
        print(f"🌐 Static files available at: https://{AWS_STORAGE_BUCKET_NAME}.sgp1.digitaloceanspaces.com/{AWS_LOCATION}/static/")
    else:
        print(f"\n⚠️  Some files failed to upload. Please check the errors above.")

if __name__ == "__main__":
    main() 