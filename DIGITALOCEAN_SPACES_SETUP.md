# DigitalOcean Spaces Setup Guide

This guide will help you set up DigitalOcean Spaces for file storage in your Django application.

## 🚀 **Step 1: Create DigitalOcean Spaces**

1. **Login to DigitalOcean Dashboard**
   - Go to https://cloud.digitalocean.com/
   - Sign in to your account

2. **Create a Space**
   - Click on "Spaces" in the left sidebar
   - Click "Create a Space"
   - Choose a name (e.g., `sushrusa-media`)
   - Select a region (e.g., `NYC3`)
   - Choose "Public" for file listing
   - Click "Create a Space"

3. **Get API Keys**
   - Go to "API" in the left sidebar
   - Click "Generate New Token"
   - Give it a name (e.g., `sushrusa-spaces`)
   - Select "Write" scope
   - Copy the generated token

## 🔧 **Step 2: Configure Environment Variables**

Add these environment variables to your `.env` file or server configuration:

```bash
# DigitalOcean Spaces Configuration
USE_DIGITALOCEAN_SPACES=True
DO_SPACES_KEY=your_access_key_here
DO_SPACES_SECRET=your_secret_key_here
DO_SPACES_BUCKET=your_bucket_name_here
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
```

**Example:**
```bash
USE_DIGITALOCEAN_SPACES=True
DO_SPACES_KEY=DO00ABC123DEF456
DO_SPACES_SECRET=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
DO_SPACES_BUCKET=sushrusa-media
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
```

## 🧪 **Step 3: Test the Setup**

Run these commands to test your configuration:

```bash
# Test the connection
python manage.py setup_digitalocean_spaces --test-connection

# List all buckets
python manage.py setup_digitalocean_spaces --list-buckets

# Create bucket if it doesn't exist
python manage.py setup_digitalocean_spaces --create-bucket
```

## 📁 **Step 4: File Organization**

Your files will be organized in DigitalOcean Spaces as follows:

```
your-bucket/
├── media/
│   ├── profile_pictures/
│   │   ├── doctor1.jpg
│   │   └── doctor2.png
│   ├── clinic_logos/
│   │   ├── clinic1.png
│   │   └── clinic2.jpg
│   └── clinic_covers/
│       ├── cover1.jpg
│       └── cover2.png
└── static/
    ├── admin/
    ├── css/
    └── js/
```

## 🔄 **Step 5: Migrate Existing Files (Optional)**

If you have existing files in your local `media/` directory, you can migrate them:

```bash
# Collect static files and upload to Spaces
python manage.py collectstatic --noinput

# For media files, you can use the AWS CLI or a custom script
```

## 🌐 **Step 6: Update Frontend URLs**

The frontend will automatically use the new URLs. Files will be served from:
```
https://your-bucket.nyc3.digitaloceanspaces.com/media/profile_pictures/doctor1.jpg
```

## 🔒 **Step 7: Security Considerations**

1. **Bucket Policy**: The setup automatically configures public read access
2. **CORS**: Configure CORS if needed for direct uploads
3. **CDN**: Consider using DigitalOcean CDN for better performance

## 🚨 **Troubleshooting**

### Common Issues:

1. **"NoSuchBucket" Error**
   ```bash
   python manage.py setup_digitalocean_spaces --create-bucket
   ```

2. **"Access Denied" Error**
   - Check your API keys
   - Ensure the bucket name is correct
   - Verify the region matches your Space

3. **"Invalid Endpoint" Error**
   - Make sure the endpoint URL is correct
   - Format: `https://region.digitaloceanspaces.com`

### Debug Commands:

```bash
# Check current configuration
python manage.py setup_digitalocean_spaces

# Test with specific credentials
export DO_SPACES_KEY=your_key
export DO_SPACES_SECRET=your_secret
python manage.py setup_digitalocean_spaces --test-connection
```

## 💰 **Cost Optimization**

1. **Lifecycle Rules**: Set up automatic deletion of old files
2. **Compression**: Enable compression for images
3. **CDN**: Use DigitalOcean CDN for frequently accessed files

## 📊 **Monitoring**

Monitor your Spaces usage in the DigitalOcean dashboard:
- Storage used
- Bandwidth consumed
- Number of requests

## 🔄 **Switching Between Local and DigitalOcean Storage**

To switch back to local storage for development:

```bash
# Set environment variable to False
export USE_DIGITALOCEAN_SPACES=False

# Or comment out in .env file
# USE_DIGITALOCEAN_SPACES=False
```

## ✅ **Verification**

After setup, test by:

1. **Creating a doctor with profile image**
2. **Creating an e-clinic with logo and cover image**
3. **Checking the URLs in the API response**
4. **Verifying images load in the frontend**

The URLs should look like:
```
https://your-bucket.nyc3.digitaloceanspaces.com/media/profile_pictures/filename.jpg
```

## 🎉 **Success!**

Your Django application is now configured to use DigitalOcean Spaces for file storage. All uploaded files will be stored in the cloud and served via CDN for optimal performance. 