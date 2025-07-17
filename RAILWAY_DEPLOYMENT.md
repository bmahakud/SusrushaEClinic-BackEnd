# Railway Deployment Guide for Sushrusa Healthcare Platform

This guide will help you deploy the Django backend to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Railway CLI** (optional): Install for local development

## Step 1: Prepare Your Repository

The following files have been created for Railway deployment:

- `railway.json` - Railway configuration
- `nixpacks.toml` - Build configuration
- `Procfile` - Process definition
- `runtime.txt` - Python version specification

## Step 2: Deploy to Railway

### Option A: Deploy via Railway Dashboard

1. **Connect Repository**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Environment Variables**:
   Add the following environment variables in Railway dashboard:

   ```bash
   # Django Settings
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ALLOWED_HOSTS=your-railway-domain.railway.app,localhost,127.0.0.1
   
   # Database (Railway will provide this)
   DATABASE_URL=postgresql://...
   
   # Redis (if using)
   REDIS_URL=redis://...
   
   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=noreply@sushrusa.com
   
   # SMS Configuration (Twilio)
   SMS_BACKEND=twilio
   TWILIO_ACCOUNT_SID=your-twilio-sid
   TWILIO_AUTH_TOKEN=your-twilio-token
   TWILIO_PHONE_NUMBER=your-twilio-number
   
   # Payment Gateways
   STRIPE_PUBLISHABLE_KEY=your-stripe-key
   STRIPE_SECRET_KEY=your-stripe-secret
   RAZORPAY_KEY_ID=your-razorpay-key
   RAZORPAY_KEY_SECRET=your-razorpay-secret
   ```

3. **Add PostgreSQL Database**:
   - In Railway dashboard, click "New"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically set the `DATABASE_URL` environment variable

4. **Deploy**:
   - Railway will automatically detect the Django project
   - It will run migrations and start the application
   - Your app will be available at `https://your-app-name.railway.app`

### Option B: Deploy via Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Project**:
   ```bash
   railway init
   ```

4. **Set Environment Variables**:
   ```bash
   railway variables set SECRET_KEY=your-secret-key-here
   railway variables set DEBUG=False
   # Add other variables as needed
   ```

5. **Deploy**:
   ```bash
   railway up
   ```

## Step 3: Post-Deployment Setup

1. **Create Superuser**:
   ```bash
   railway run python manage.py createsuperuser
   ```

2. **Create SuperAdmin** (if needed):
   ```bash
   railway run python manage.py create_superadmin --phone +919876543210 --password superadmin123
   ```

3. **Collect Static Files**:
   ```bash
   railway run python manage.py collectstatic --noinput
   ```

## Step 4: Update Frontend Configuration

Update your frontend API base URL to point to your Railway deployment:

```typescript
// In your frontend API configuration
const API_BASE_URL = 'https://your-app-name.railway.app/api';
```

## Step 5: Verify Deployment

1. **Health Check**: Visit `https://your-app-name.railway.app/api/health/`
2. **Admin Panel**: Visit `https://your-app-name.railway.app/admin/`
3. **API Documentation**: Visit `https://your-app-name.railway.app/api/docs/`

## Environment Variables Reference

### Required Variables
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string (provided by Railway)
- `DEBUG`: Set to `False` for production

### Optional Variables
- `REDIS_URL`: For caching and Celery
- `EMAIL_*`: For email functionality
- `TWILIO_*`: For SMS functionality
- `STRIPE_*`: For Stripe payments
- `RAZORPAY_*`: For Razorpay payments

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version in `runtime.txt` is compatible

2. **Database Connection Issues**:
   - Verify `DATABASE_URL` is set correctly
   - Check that PostgreSQL service is running

3. **Static Files Not Loading**:
   - Ensure `collectstatic` command runs during deployment
   - Check WhiteNoise configuration

4. **CORS Issues**:
   - Update `ALLOWED_HOSTS` with your Railway domain
   - Configure CORS settings for your frontend domain

### Logs and Debugging

- View logs in Railway dashboard
- Use `railway logs` command for CLI access
- Check Django logs in the application

## Monitoring and Maintenance

1. **Set up monitoring** in Railway dashboard
2. **Configure alerts** for downtime
3. **Regular backups** of your database
4. **Update dependencies** regularly

## Cost Optimization

- Railway offers a free tier with limitations
- Monitor usage in Railway dashboard
- Consider upgrading for production workloads

## Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **HTTPS**: Railway provides SSL certificates automatically
3. **Database Security**: Use strong passwords and restrict access
4. **Django Security**: Keep Django and dependencies updated

## Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Django Documentation: [docs.djangoproject.com](https://docs.djangoproject.com)
- Railway Community: [discord.gg/railway](https://discord.gg/railway) 