# Sushrusa Healthcare Platform - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Sushrusa Healthcare Platform Django REST API backend in various environments, from local development to production deployment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Security Configuration](#security-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB
- OS: Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+ / Windows 10+

**Recommended for Production:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 100GB+ SSD
- OS: Ubuntu 22.04 LTS

### Software Dependencies

- Python 3.11+
- PostgreSQL 12+ (production) / SQLite (development)
- Redis 6+
- Nginx (production)
- Docker & Docker Compose (optional)
- Git

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd sushrusa_backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/macOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your local configuration
```

### 5. Database Setup

**For SQLite (Development):**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

**For PostgreSQL:**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE sushrusa_db;
CREATE USER sushrusa_user WITH PASSWORD 'sushrusa_password';
GRANT ALL PRIVILEGES ON DATABASE sushrusa_db TO sushrusa_user;
\q

# Update .env with PostgreSQL settings
DATABASE_URL=postgresql://sushrusa_user:sushrusa_password@localhost:5432/sushrusa_db

# Run migrations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Redis Setup

```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

### 8. Start Celery (Optional)

```bash
# In a new terminal
celery -A sushrusa_platform worker --loglevel=info

# In another terminal for beat scheduler
celery -A sushrusa_platform beat --loglevel=info
```

## Docker Deployment

### 1. Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Individual Docker Commands

```bash
# Build image
docker build -t sushrusa-backend .

# Run PostgreSQL
docker run -d \
  --name sushrusa-postgres \
  -e POSTGRES_DB=sushrusa_db \
  -e POSTGRES_USER=sushrusa_user \
  -e POSTGRES_PASSWORD=sushrusa_password \
  -p 5432:5432 \
  postgres:15

# Run Redis
docker run -d \
  --name sushrusa-redis \
  -p 6379:6379 \
  redis:7-alpine

# Run Django application
docker run -d \
  --name sushrusa-web \
  --link sushrusa-postgres:db \
  --link sushrusa-redis:redis \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://sushrusa_user:sushrusa_password@db:5432/sushrusa_db \
  -e REDIS_URL=redis://redis:6379/0 \
  sushrusa-backend
```

### 3. Docker Health Checks

```bash
# Check container health
docker ps
docker-compose ps

# View container logs
docker logs sushrusa-web
docker-compose logs web

# Execute commands in container
docker exec -it sushrusa-web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Production Deployment

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql postgresql-contrib redis-server nginx git curl

# Create application user
sudo adduser sushrusa
sudo usermod -aG sudo sushrusa
```

### 2. Application Setup

```bash
# Switch to application user
sudo su - sushrusa

# Clone repository
git clone <repository-url> /home/sushrusa/sushrusa_backend
cd /home/sushrusa/sushrusa_backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### 3. Database Configuration

```bash
# Configure PostgreSQL
sudo -u postgres psql
CREATE DATABASE sushrusa_production;
CREATE USER sushrusa_prod WITH PASSWORD 'secure_production_password';
GRANT ALL PRIVILEGES ON DATABASE sushrusa_production TO sushrusa_prod;
\q

# Update production environment
cp .env.example .env.production
# Edit .env.production with production settings
```

### 4. Static Files and Media

```bash
# Create directories
mkdir -p /home/sushrusa/sushrusa_backend/static
mkdir -p /home/sushrusa/sushrusa_backend/media

# Collect static files
python manage.py collectstatic --noinput

# Set permissions
sudo chown -R sushrusa:sushrusa /home/sushrusa/sushrusa_backend
```

### 5. Gunicorn Configuration

Create `/home/sushrusa/sushrusa_backend/gunicorn.conf.py`:

```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
user = "sushrusa"
group = "sushrusa"
tmp_upload_dir = None
errorlog = "/home/sushrusa/sushrusa_backend/logs/gunicorn_error.log"
accesslog = "/home/sushrusa/sushrusa_backend/logs/gunicorn_access.log"
loglevel = "info"
```

### 6. Systemd Service Configuration

Create `/etc/systemd/system/sushrusa.service`:

```ini
[Unit]
Description=Sushrusa Healthcare Platform
After=network.target

[Service]
User=sushrusa
Group=sushrusa
WorkingDirectory=/home/sushrusa/sushrusa_backend
Environment=PATH=/home/sushrusa/sushrusa_backend/venv/bin
EnvironmentFile=/home/sushrusa/sushrusa_backend/.env.production
ExecStart=/home/sushrusa/sushrusa_backend/venv/bin/gunicorn --config gunicorn.conf.py sushrusa_platform.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/sushrusa-celery.service`:

```ini
[Unit]
Description=Sushrusa Celery Worker
After=network.target

[Service]
User=sushrusa
Group=sushrusa
WorkingDirectory=/home/sushrusa/sushrusa_backend
Environment=PATH=/home/sushrusa/sushrusa_backend/venv/bin
EnvironmentFile=/home/sushrusa/sushrusa_backend/.env.production
ExecStart=/home/sushrusa/sushrusa_backend/venv/bin/celery -A sushrusa_platform worker --loglevel=info
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 7. Nginx Configuration

Create `/etc/nginx/sites-available/sushrusa`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Client upload limit
    client_max_body_size 10M;
    
    # Static files
    location /static/ {
        alias /home/sushrusa/sushrusa_backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files
    location /media/ {
        alias /home/sushrusa/sushrusa_backend/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # API endpoints
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Health check endpoint
    location /health/ {
        access_log off;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 8. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 9. Start Services

```bash
# Enable and start services
sudo systemctl enable sushrusa
sudo systemctl enable sushrusa-celery
sudo systemctl enable nginx

sudo systemctl start sushrusa
sudo systemctl start sushrusa-celery
sudo systemctl start nginx

# Check service status
sudo systemctl status sushrusa
sudo systemctl status sushrusa-celery
sudo systemctl status nginx
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance Setup

```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Configure security groups:
# - HTTP (80)
# - HTTPS (443)
# - SSH (22)
# - Custom TCP (8000) for development

# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip
```

#### 2. RDS Database Setup

```bash
# Create RDS PostgreSQL instance
# Update .env.production with RDS endpoint
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/sushrusa_db
```

#### 3. ElastiCache Redis Setup

```bash
# Create ElastiCache Redis cluster
# Update .env.production with Redis endpoint
REDIS_URL=redis://your-elasticache-endpoint:6379/0
```

#### 4. S3 Storage Setup

```bash
# Create S3 bucket for media files
# Configure IAM user with S3 permissions
# Update .env.production
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=sushrusa-media
```

### Google Cloud Platform Deployment

#### 1. Compute Engine Setup

```bash
# Create VM instance
gcloud compute instances create sushrusa-backend \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --zone=us-central1-a
```

#### 2. Cloud SQL Setup

```bash
# Create Cloud SQL PostgreSQL instance
gcloud sql instances create sushrusa-db \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1
```

#### 3. Cloud Storage Setup

```bash
# Create Cloud Storage bucket
gsutil mb gs://sushrusa-media
```

### DigitalOcean Deployment

#### 1. Droplet Setup

```bash
# Create droplet via DigitalOcean control panel
# Choose Ubuntu 22.04 LTS
# Configure firewall rules
```

#### 2. Managed Database

```bash
# Create managed PostgreSQL database
# Update connection string in .env.production
```

## Environment Configuration

### Development Environment

```bash
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
```

### Staging Environment

```bash
DEBUG=False
ALLOWED_HOSTS=staging.sushrusa.com
DATABASE_URL=postgresql://user:pass@staging-db:5432/sushrusa_staging
REDIS_URL=redis://staging-redis:6379/0
```

### Production Environment

```bash
DEBUG=False
ALLOWED_HOSTS=api.sushrusa.com,sushrusa.com
DATABASE_URL=postgresql://user:pass@prod-db:5432/sushrusa_production
REDIS_URL=redis://prod-redis:6379/0
SECURE_SSL_REDIRECT=True
```

## Security Configuration

### 1. Firewall Setup

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8000  # Block direct access to Django
```

### 2. Database Security

```bash
# PostgreSQL security
sudo -u postgres psql
ALTER USER sushrusa_prod WITH PASSWORD 'very_secure_password';
\q

# Update pg_hba.conf for restricted access
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

### 3. Redis Security

```bash
# Configure Redis authentication
sudo nano /etc/redis/redis.conf
# Add: requirepass your_redis_password
sudo systemctl restart redis-server
```

### 4. Application Security

```bash
# Set secure file permissions
chmod 600 .env.production
chmod -R 755 /home/sushrusa/sushrusa_backend
chmod -R 644 /home/sushrusa/sushrusa_backend/static
```

## Monitoring and Logging

### 1. Log Configuration

Create `/home/sushrusa/sushrusa_backend/logs/` directory:

```bash
mkdir -p /home/sushrusa/sushrusa_backend/logs
```

### 2. Log Rotation

Create `/etc/logrotate.d/sushrusa`:

```
/home/sushrusa/sushrusa_backend/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 sushrusa sushrusa
    postrotate
        systemctl reload sushrusa
    endscript
}
```

### 3. Monitoring Setup

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Set up system monitoring
# Consider using: Prometheus, Grafana, New Relic, or DataDog
```

## Backup and Recovery

### 1. Database Backup

Create backup script `/home/sushrusa/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/sushrusa/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="sushrusa_production"
DB_USER="sushrusa_prod"

mkdir -p $BACKUP_DIR

pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/sushrusa_db_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "sushrusa_db_*.sql.gz" -mtime +30 -delete
```

### 2. Media Files Backup

```bash
#!/bin/bash
BACKUP_DIR="/home/sushrusa/backups"
DATE=$(date +%Y%m%d_%H%M%S)
MEDIA_DIR="/home/sushrusa/sushrusa_backend/media"

tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C $MEDIA_DIR .

# Keep only last 7 days of media backups
find $BACKUP_DIR -name "media_*.tar.gz" -mtime +7 -delete
```

### 3. Automated Backups

Add to crontab (`crontab -e`):

```bash
# Daily database backup at 2 AM
0 2 * * * /home/sushrusa/backup_db.sh

# Weekly media backup on Sundays at 3 AM
0 3 * * 0 /home/sushrusa/backup_media.sh
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -U sushrusa_prod -h localhost -d sushrusa_production

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

#### 2. Redis Connection Issues

```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping

# Check Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

#### 3. Application Errors

```bash
# Check application logs
tail -f /home/sushrusa/sushrusa_backend/logs/sushrusa.log

# Check Gunicorn logs
tail -f /home/sushrusa/sushrusa_backend/logs/gunicorn_error.log

# Check system service status
sudo systemctl status sushrusa
```

#### 4. Nginx Issues

```bash
# Check Nginx status
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

#### 5. SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Test SSL configuration
openssl s_client -connect your-domain.com:443
```

### Performance Optimization

#### 1. Database Optimization

```sql
-- Create indexes for frequently queried fields
CREATE INDEX idx_user_phone ON authentication_user(phone);
CREATE INDEX idx_consultation_date ON consultations_consultation(consultation_date);
CREATE INDEX idx_payment_status ON payments_payment(status);
```

#### 2. Redis Optimization

```bash
# Configure Redis memory settings
sudo nano /etc/redis/redis.conf
# Set: maxmemory 1gb
# Set: maxmemory-policy allkeys-lru
```

#### 3. Application Optimization

```python
# Use database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'CONN_MAX_AGE': 600,
        }
    }
}
```

### Scaling Considerations

#### 1. Horizontal Scaling

- Use load balancer (AWS ALB, Nginx, HAProxy)
- Deploy multiple application instances
- Implement session affinity or stateless sessions

#### 2. Database Scaling

- Read replicas for read-heavy workloads
- Database sharding for large datasets
- Connection pooling (PgBouncer)

#### 3. Caching Strategy

- Redis cluster for high availability
- CDN for static files (CloudFlare, AWS CloudFront)
- Application-level caching

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Monitor system resources
- Check application logs
- Verify backup completion

#### Weekly
- Update system packages
- Review security logs
- Performance monitoring

#### Monthly
- Security updates
- Database maintenance
- Capacity planning review

### Update Procedure

```bash
# 1. Backup current version
git tag v1.0.0-backup

# 2. Pull latest changes
git pull origin main

# 3. Update dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart services
sudo systemctl restart sushrusa
sudo systemctl restart sushrusa-celery
```

---

This deployment guide provides comprehensive instructions for deploying the Sushrusa Healthcare Platform in various environments. For additional support, refer to the main README.md file or contact the development team.

