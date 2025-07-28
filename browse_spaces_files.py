#!/usr/bin/env python3
"""
Script to browse and list files in DigitalOcean Spaces
"""

import boto3
from pathlib import Path
import json

# DigitalOcean Spaces configuration
AWS_ACCESS_KEY_ID = 'UCW66UXZOVY3QVYQLSEK'
AWS_SECRET_ACCESS_KEY = 'TJi4SulSCtEU5RlHWsKkOpFoL0Qo/qVf5JB6Dcg8rWk'
AWS_STORAGE_BUCKET_NAME = 'edrspace'
AWS_S3_ENDPOINT_URL = 'https://sgp1.digitaloceanspaces.com'
AWS_LOCATION = 'edrcontainer1'

def list_files_in_spaces(prefix='', max_keys=100):
    """List files in DigitalOcean Spaces with given prefix"""
    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=AWS_S3_ENDPOINT_URL,
            region_name='sgp1'
        )
        
        # List objects
        response = s3_client.list_objects_v2(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Prefix=prefix,
            MaxKeys=max_keys
        )
        
        if 'Contents' in response:
            files = []
            for obj in response['Contents']:
                file_info = {
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': f"https://{AWS_STORAGE_BUCKET_NAME}.sgp1.digitaloceanspaces.com/{obj['Key']}"
                }
                files.append(file_info)
            return files
        else:
            return []
            
    except Exception as e:
        print(f"❌ Error listing files: {e}")
        return []

def display_files(files, category):
    """Display files in a formatted way"""
    if not files:
        print(f"📁 No files found in {category}")
        return
    
    print(f"\n📁 {category} Files ({len(files)} files):")
    print("=" * 80)
    
    for i, file_info in enumerate(files, 1):
        size_mb = file_info['size'] / (1024 * 1024)
        print(f"{i:2d}. {file_info['key']}")
        print(f"    📏 Size: {size_mb:.2f} MB")
        print(f"    📅 Modified: {file_info['last_modified']}")
        print(f"    🔗 URL: {file_info['url']}")
        print()

def main():
    """Main function to browse files"""
    print("🔍 DigitalOcean Spaces File Browser")
    print("=" * 50)
    
    # List images (media files)
    print("\n🔍 Searching for uploaded images...")
    image_files = list_files_in_spaces(f"{AWS_LOCATION}/images/")
    display_files(image_files, "Images (Media Files)")
    
    # List static files
    print("\n🔍 Searching for static files...")
    static_files = list_files_in_spaces(f"{AWS_LOCATION}/static/")
    display_files(static_files, "Static Files")
    
    # Summary
    total_files = len(image_files) + len(static_files)
    print(f"\n📊 Summary: {total_files} total files found")
    
    if image_files:
        print(f"   📸 Images: {len(image_files)} files")
    if static_files:
        print(f"   📄 Static: {len(static_files)} files")
    
    print(f"\n🌐 Base URLs:")
    print(f"   📸 Images: https://{AWS_STORAGE_BUCKET_NAME}.sgp1.digitaloceanspaces.com/{AWS_LOCATION}/images/")
    print(f"   📄 Static: https://{AWS_STORAGE_BUCKET_NAME}.sgp1.digitaloceanspaces.com/{AWS_LOCATION}/static/")

if __name__ == "__main__":
    main() 