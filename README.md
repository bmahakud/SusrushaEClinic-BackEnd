# Sushrusa Healthcare Platform - Django REST API Backend

## Overview

Sushrusa is a comprehensive healthcare platform that connects patients with healthcare providers through a robust digital ecosystem. This Django REST API backend serves as the core infrastructure powering the platform's web and mobile applications, providing secure, scalable, and feature-rich endpoints for healthcare management.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality

**Authentication & User Management**
- Phone/OTP based authentication with JWT tokens
- Role-based access control (Patient, Doctor, Admin, SuperAdmin)
- Secure session management
- Profile management with comprehensive user data

**Patient Management**
- Complete patient profile management
- Medical records and history tracking
- Document upload and management
- Patient notes and annotations
- Advanced search and filtering capabilities

**Doctor Management**
- Doctor profile and credential management
- Education and experience tracking
- Availability and schedule management
- Performance analytics and reviews
- Document verification system

**Consultation Management**
- Appointment booking and scheduling
- Real-time consultation management
- Diagnosis and treatment tracking
- Vital signs recording
- Consultation notes and documentation

**Prescription Management**
- Digital prescription creation and management
- Medication tracking and reminders
- Prescription history and analytics
- Pharmacy integration support
- Medication interaction checking

**Payment Processing**
- Multi-gateway payment integration (Stripe, Razorpay, PayU)
- Secure payment method management
- Refund and dispute handling
- Discount and coupon management
- Comprehensive payment analytics

**E-Clinic Management**
- Clinic registration and verification
- Service and inventory management
- Appointment scheduling
- Review and rating system
- Geographic search capabilities

**Analytics & Reporting**
- Real-time dashboard metrics
- User growth and engagement analytics
- Revenue and financial reporting
- Geographic distribution analysis
- Custom report generation
- Data export capabilities

### Technical Features

- **RESTful API Design**: Clean, intuitive endpoints following REST conventions
- **Comprehensive Documentation**: Auto-generated API documentation with drf-spectacular
- **Role-Based Permissions**: Granular access control for different user types
- **Data Validation**: Robust input validation and error handling
- **File Management**: Secure file upload and storage for documents and images
- **Search & Filtering**: Advanced search capabilities with multiple filter options
- **Pagination**: Efficient handling of large datasets
- **Caching**: Redis-based caching for improved performance
- **Background Tasks**: Celery integration for asynchronous processing
- **Security**: CORS configuration, JWT authentication, and secure headers

## Architecture

### Technology Stack

- **Framework**: Django 5.2.4 with Django REST Framework 3.14+
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: JWT tokens with phone/OTP verification
- **Caching**: Redis
- **Task Queue**: Celery with Redis broker
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **File Storage**: Django file handling with cloud storage support
- **Payment Gateways**: Stripe, Razorpay, PayU integration

### Project Structure

```
sushrusa_backend/
├── sushrusa_platform/          # Main project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL configuration
│   └── wsgi.py                 # WSGI configuration
├── authentication/             # User authentication and management
├── patients/                   # Patient management
├── doctors/                    # Doctor management
├── consultations/              # Consultation management
├── prescriptions/              # Prescription management
├── payments/                   # Payment processing
├── eclinic/                    # E-clinic management
├── analytics/                  # Analytics and reporting
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
└── README.md                   # This file
```

### Database Design

The platform uses a comprehensive relational database schema with the following key entities:

- **Users**: Core user management with role-based access
- **Patients**: Patient profiles and medical information
- **Doctors**: Doctor profiles, credentials, and availability
- **Consultations**: Appointment and consultation management
- **Prescriptions**: Medication and prescription tracking
- **Payments**: Financial transactions and billing
- **Clinics**: Healthcare facility management
- **Analytics**: Platform metrics and reporting data

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 12+ (for production)
- Redis 6+ (for caching and task queue)
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd sushrusa_backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

### Docker Setup

1. **Build and run with Docker Compose**
```bash
docker-compose up --build
```

2. **Run migrations**
```bash
docker-compose exec web python manage.py migrate
```

3. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/sushrusa_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Payment Gateway Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...

# SMS Configuration (for OTP)
SMS_API_KEY=your-sms-api-key
SMS_SENDER_ID=SUSHRUSA

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# File Storage
MEDIA_ROOT=/path/to/media/files
STATIC_ROOT=/path/to/static/files

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Django Settings

Key configuration options in `settings.py`:

- **CORS Configuration**: Allows cross-origin requests for frontend integration
- **JWT Settings**: Token lifetime and security configuration
- **Database**: PostgreSQL for production, SQLite for development
- **File Upload**: Secure file handling with size limits
- **Pagination**: Default page sizes and limits
- **Logging**: Comprehensive logging configuration

## API Documentation

### Interactive Documentation

The API includes auto-generated interactive documentation:

- **Swagger UI**: Available at `/api/docs/`
- **ReDoc**: Available at `/api/redoc/`
- **OpenAPI Schema**: Available at `/api/schema/`

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/send-otp/` | Send OTP to phone number |
| POST | `/api/auth/verify-otp/` | Verify OTP and get tokens |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Logout and invalidate tokens |
| GET/PUT | `/api/auth/profile/` | Get/update user profile |

### Core API Modules

**Patient Management** (`/api/patients/`)
- Patient profile CRUD operations
- Medical records management
- Document upload and retrieval
- Patient search and filtering

**Doctor Management** (`/api/doctors/`)
- Doctor profile management
- Education and experience tracking
- Availability scheduling
- Performance analytics

**Consultation Management** (`/api/consultations/`)
- Appointment booking and management
- Consultation workflow (start, complete, cancel)
- Diagnosis and vital signs recording
- Consultation history and analytics

**Prescription Management** (`/api/prescriptions/`)
- Digital prescription creation
- Medication management
- Prescription history
- Medication reminders

**Payment Processing** (`/api/payments/`)
- Payment method management
- Transaction processing
- Refund handling
- Payment analytics

**E-Clinic Management** (`/api/eclinic/`)
- Clinic registration and management
- Service and inventory tracking
- Appointment scheduling
- Review and rating system

**Analytics** (`/api/analytics/`)
- Dashboard statistics
- User growth analytics
- Revenue reporting
- Geographic analysis
- Custom report generation

### Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Error responses include detailed error information:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid data provided",
    "details": {
      "field_name": ["Error message"]
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Authentication

### Phone/OTP Authentication Flow

1. **Send OTP**: User provides phone number
2. **Verify OTP**: User enters received OTP code
3. **Token Generation**: System generates JWT access and refresh tokens
4. **API Access**: Use access token in Authorization header
5. **Token Refresh**: Use refresh token to get new access token

### JWT Token Usage

Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Role-Based Access Control

The platform supports four user roles:

- **Patient**: Access to own medical data and consultations
- **Doctor**: Access to assigned consultations and patient data
- **Admin**: Administrative access to platform management
- **SuperAdmin**: Full system access and configuration

## Database Schema

### Key Models

**User Model**
- Custom user model with phone-based authentication
- Role-based access control
- Profile information and preferences

**Patient Profile**
- Medical history and conditions
- Insurance information
- Emergency contacts
- Document storage

**Doctor Profile**
- Professional credentials and qualifications
- Specializations and experience
- Availability and scheduling
- Performance metrics

**Consultation Model**
- Appointment scheduling and management
- Consultation workflow tracking
- Diagnosis and treatment records
- Payment integration

**Prescription Model**
- Digital prescription management
- Medication tracking
- Dosage and instruction details
- Pharmacy integration

### Relationships

The database schema includes comprehensive relationships:

- One-to-Many: User to Consultations, Doctor to Patients
- Many-to-Many: Doctors to Clinics, Patients to Medical Conditions
- Foreign Keys: Consultation to Patient/Doctor, Prescription to Consultation

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test authentication
python manage.py test patients

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Structure

Tests are organized by application:

- **Unit Tests**: Model and utility function testing
- **API Tests**: Endpoint functionality and response validation
- **Integration Tests**: Cross-module functionality testing
- **Authentication Tests**: Security and permission testing

### Test Data

Use Django fixtures for consistent test data:

```bash
python manage.py loaddata test_fixtures.json
```

## Deployment

### Production Deployment

#### Using Docker

1. **Build production image**
```bash
docker build -t sushrusa-backend .
```

2. **Run with environment variables**
```bash
docker run -d \
  --name sushrusa-backend \
  -p 8000:8000 \
  --env-file .env.production \
  sushrusa-backend
```

#### Using Traditional Hosting

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure environment**
```bash
export DJANGO_SETTINGS_MODULE=sushrusa_platform.settings.production
```

3. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Start with Gunicorn**
```bash
gunicorn sushrusa_platform.wsgi:application --bind 0.0.0.0:8000
```

### Environment-Specific Settings

Create separate settings files for different environments:

- `settings/development.py`
- `settings/staging.py`
- `settings/production.py`

### Security Considerations

**Production Security Checklist:**

- [ ] Set `DEBUG = False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use HTTPS in production
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable database connection pooling
- [ ] Configure proper logging
- [ ] Set up monitoring and alerting
- [ ] Regular security updates

### Performance Optimization

**Database Optimization:**
- Use database indexes for frequently queried fields
- Implement query optimization with select_related and prefetch_related
- Configure connection pooling

**Caching Strategy:**
- Redis caching for frequently accessed data
- API response caching for static content
- Database query result caching

**File Storage:**
- Use cloud storage (AWS S3, Google Cloud Storage) for production
- Implement CDN for static file delivery
- Optimize image sizes and formats

## API Rate Limiting

The platform implements rate limiting to ensure fair usage:

- **Authentication endpoints**: 5 requests per minute
- **General API endpoints**: 100 requests per minute
- **File upload endpoints**: 10 requests per minute
- **Analytics endpoints**: 50 requests per minute

Rate limits can be configured in `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

## Monitoring and Logging

### Logging Configuration

The platform includes comprehensive logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'sushrusa.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'sushrusa': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Health Check Endpoints

Monitor system health with dedicated endpoints:

- `/health/`: Basic health check
- `/health/database/`: Database connectivity check
- `/health/redis/`: Redis connectivity check
- `/health/detailed/`: Comprehensive system status

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make changes and test**
```bash
python manage.py test
```

4. **Commit changes**
```bash
git commit -m "Add your feature description"
```

5. **Push to branch**
```bash
git push origin feature/your-feature-name
```

6. **Create Pull Request**

### Code Standards

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Write comprehensive tests for new features
- Update documentation for API changes

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- **Documentation**: Check the API documentation at `/api/docs/`
- **Issues**: Report bugs and feature requests on GitHub
- **Email**: Contact the development team at dev@sushrusa.com

## Changelog

### Version 1.0.0 (2024-01-15)

**Initial Release**
- Complete authentication system with phone/OTP
- Patient and doctor management modules
- Consultation and prescription management
- Payment processing integration
- E-clinic management system
- Analytics and reporting dashboard
- Comprehensive API documentation
- Production-ready deployment configuration

---

**Built with ❤️ by the Sushrusa Development Team**

