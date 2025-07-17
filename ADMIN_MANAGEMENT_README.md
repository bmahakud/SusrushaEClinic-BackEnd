# 🏥 Admin Management System - Sushrusa Healthcare Platform

## 📋 Overview

The Admin Management System provides comprehensive functionality for SuperAdmin users to manage admin accounts within the Sushrusa Healthcare Platform. This system includes CRUD operations, search and filtering, statistics, and performance analytics.

## 🎯 Features

### ✅ Core Functionality
- **Create Admin Accounts**: SuperAdmin can create new admin accounts with auto-generated passwords
- **List Admin Accounts**: View all admin accounts with pagination, search, and filtering
- **Update Admin Accounts**: Modify admin account details and information
- **Delete Admin Accounts**: Soft delete (deactivate) admin accounts
- **Admin Statistics**: Comprehensive analytics and performance metrics
- **Search & Filters**: Advanced search by name, phone, email with status and sorting options

### 📊 Statistics Dashboard
- **Total Admins**: Count with month-over-month growth
- **Active Admins**: Active admin count with growth metrics
- **New This Month**: New admin accounts created this month
- **Average Performance**: Performance score based on consultations and revenue managed
- **Top Performers**: List of top 5 performing admins
- **Performance Analytics**: Detailed metrics for each admin

## 🔐 Authentication & Authorization

### Required Permissions
- **SuperAdmin Role**: Only users with `superadmin` role can access these endpoints
- **JWT Authentication**: All endpoints require valid JWT access token
- **Role-Based Access**: Strict permission checking for all operations

### Authentication Flow
1. SuperAdmin sends OTP to their phone number
2. Verify OTP to get JWT access and refresh tokens
3. Use access token in Authorization header for all admin management requests

## 📡 API Endpoints

### Base URL
```
http://localhost:8000/api
```

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/send-otp/` | Send OTP to SuperAdmin phone |
| `POST` | `/auth/verify-otp/` | Verify OTP and get JWT tokens |

### Admin Management Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/auth/superadmin/admins/stats/` | Get admin statistics and analytics |
| `GET` | `/auth/superadmin/admins/` | List all admin accounts with search/filters |
| `POST` | `/auth/superadmin/admins/` | Create new admin account |
| `GET` | `/auth/superadmin/admins/{admin_id}/` | Get specific admin details |
| `PUT` | `/auth/superadmin/admins/{admin_id}/` | Update admin account |
| `DELETE` | `/auth/superadmin/admins/{admin_id}/` | Deactivate admin account |

## 📝 API Usage Examples

### 1. Get Admin Statistics
```bash
curl -X GET "http://localhost:8000/api/auth/superadmin/admins/stats/" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_admins": {
      "value": 48,
      "change": "+5 from last month"
    },
    "active_admins": {
      "value": 42,
      "change": "+3 from last month"
    },
    "new_this_month": {
      "value": 8,
      "change": "+60% from last month"
    },
    "avg_performance": {
      "value": "92%",
      "change": "+0% from last month"
    },
    "admin_performance": [...],
    "top_performers": [...]
  },
  "message": "Admin statistics retrieved successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. List Admin Accounts
```bash
curl -X GET "http://localhost:8000/api/auth/superadmin/admins/?search=john&status=active&sort_by=name&sort_order=asc&page=1&page_size=10" \
  -H "Authorization: Bearer <access_token>"
```

### 3. Create New Admin Account
```bash
curl -X POST "http://localhost:8000/api/auth/superadmin/admins/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543212",
    "name": "Jane Admin",
    "email": "jane.admin@example.com",
    "password": "securepass123",
    "is_active": true
  }'
```

### 4. Update Admin Account
```bash
curl -X PUT "http://localhost:8000/api/auth/superadmin/admins/ADM001/" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated Admin",
    "email": "john.updated@example.com",
    "city": "Mumbai",
    "state": "Maharashtra"
  }'
```

### 5. Deactivate Admin Account
```bash
curl -X DELETE "http://localhost:8000/api/auth/superadmin/admins/ADM002/" \
  -H "Authorization: Bearer <access_token>"
```

## 🔍 Query Parameters

### List Admin Accounts Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `search` | string | Search by name, phone, or email | "" |
| `status` | string | Filter by status: active, inactive, all | "all" |
| `sort_by` | string | Sort by: name, date_joined, last_login | "date_joined" |
| `sort_order` | string | Sort order: asc, desc | "desc" |
| `page` | integer | Page number for pagination | 1 |
| `page_size` | integer | Items per page | 20 |

### Example Queries
```bash
# Search for admins with "john" in name, phone, or email
GET /auth/superadmin/admins/?search=john

# Get only active admins sorted by name ascending
GET /auth/superadmin/admins/?status=active&sort_by=name&sort_order=asc

# Get second page with 10 items per page
GET /auth/superadmin/admins/?page=2&page_size=10
```

## 📊 Statistics Metrics

### Performance Calculation
Admin performance is calculated based on:
- **Consultations Managed**: Number of consultations created by the admin
- **Revenue Managed**: Total revenue from consultations managed by the admin
- **Performance Score**: Formula: `min(100, (consultations * 10) + (revenue / 1000))`

### Growth Metrics
- **Month-over-Month Growth**: Percentage change from previous month
- **Active Admin Growth**: Change in active admin count
- **New Admin Growth**: Change in new admin creation rate

## 🛡️ Security Features

### Data Protection
- **Soft Delete**: Admin accounts are deactivated rather than permanently deleted
- **Password Security**: Auto-generated secure passwords for new accounts
- **Input Validation**: Comprehensive validation for all input fields
- **SQL Injection Protection**: Parameterized queries prevent SQL injection

### Access Control
- **Role-Based Permissions**: Only SuperAdmin can access admin management
- **JWT Token Validation**: Secure token-based authentication
- **Self-Deletion Prevention**: Admins cannot delete their own accounts

## 🚀 Getting Started

### Prerequisites
- Django backend running on `http://localhost:8000`
- SuperAdmin account with valid phone number
- JWT authentication configured

### Quick Start
1. **Start the Django server:**
   ```bash
   cd sushrusa_backend
   python manage.py runserver
   ```

2. **Test the API:**
   ```bash
   python test_admin_management.py
   ```

3. **Access Swagger Documentation:**
   ```
   http://localhost:8000/api/docs/
   ```

### Testing
Run the provided test script to verify all endpoints:
```bash
cd sushrusa_backend
python test_admin_management.py
```

## 📋 Error Codes

| Error Code | Description | HTTP Status |
|------------|-------------|-------------|
| `PERMISSION_DENIED` | Only SuperAdmin can access this endpoint | 403 |
| `ADMIN_NOT_FOUND` | Admin account not found | 404 |
| `USER_EXISTS` | User with this phone number already exists | 400 |
| `MISSING_FIELD` | Required field is missing | 400 |
| `VALIDATION_ERROR` | Invalid data provided | 400 |
| `SELF_DELETION` | Cannot delete your own account | 400 |

## 🔧 Configuration

### Environment Variables
No additional environment variables required. The system uses existing Django settings.

### Database
The system uses the existing User model with role-based filtering for admin accounts.

### File Structure
```
sushrusa_backend/
├── authentication/
│   ├── views.py          # Admin management views
│   ├── urls.py           # URL patterns
│   └── models.py         # User model
├── admin_management_flow.json    # API flow documentation
├── test_admin_management.py      # Test script
└── ADMIN_MANAGEMENT_README.md    # This file
```

## 📈 Performance Considerations

### Optimization Features
- **Pagination**: Large result sets are paginated for better performance
- **Database Indexing**: Proper indexing on frequently queried fields
- **Selective Queries**: Only fetch required fields to reduce data transfer
- **Caching**: Consider implementing Redis caching for statistics

### Scalability
- **Horizontal Scaling**: Stateless API design supports horizontal scaling
- **Database Optimization**: Efficient queries with proper indexing
- **Load Balancing**: API can be load balanced across multiple instances

## 🤝 Contributing

### Development Guidelines
1. Follow Django REST framework best practices
2. Add comprehensive error handling
3. Include proper validation for all inputs
4. Write tests for new functionality
5. Update documentation for any changes

### Code Style
- Follow PEP 8 Python style guide
- Use descriptive variable and function names
- Add docstrings for all functions and classes
- Include type hints where appropriate

## 📞 Support

For questions or issues with the Admin Management System:
1. Check the API documentation at `/api/docs/`
2. Review the test script for usage examples
3. Check the error codes section for troubleshooting
4. Verify authentication and permissions

## 📄 License

This Admin Management System is part of the Sushrusa Healthcare Platform and follows the same licensing terms.

---

**Last Updated**: January 2024  
**Version**: 1.0.0  
**Author**: Sushrusa Development Team 