# Consultation Reschedule System Guide

## Overview

The consultation reschedule system allows admins and doctors to handle overdue consultations that haven't been completed. When a consultation time passes without completion, the system provides a workflow to reschedule the consultation with the same patient and doctor (or optionally with a different doctor).

## Key Features

1. **Automatic Overdue Detection**: System automatically identifies consultations that have passed their scheduled time
2. **Reschedule Request Workflow**: Doctors can request reschedules for overdue consultations
3. **Admin Approval System**: Admins can approve or reject reschedule requests
4. **Flexible Rescheduling**: Can reschedule with same doctor or different doctor
5. **Audit Trail**: Complete history of all reschedule requests and changes
6. **Doctor Visibility**: Doctors can see reschedule requests and overdue consultations

## System Flow

### 1. Consultation Time Expiration
- When consultation time passes, the consultation becomes "overdue"
- System marks consultation as eligible for reschedule
- Consultation status changes to track reschedule workflow

### 2. Reschedule Request
- **Doctors** can request reschedule for their overdue consultations
- **Admins** can request reschedule for any overdue consultation
- Request includes reason and marks consultation for admin review

### 3. Admin Approval
- **Admins** review reschedule requests
- Can approve or reject with comments
- Approved requests move to reschedule application phase

### 4. Reschedule Application
- **Admins** apply approved reschedules with new date/time
- System creates new consultation slot
- Maintains patient and consultation history
- Creates audit trail of the change

## API Endpoints

### For Doctors

#### 1. View Overdue Consultations
```
GET /api/consultations/doctor/overdue/
```
- Returns list of overdue consultations for the logged-in doctor
- Includes reschedule status and eligibility information
- Paginated results

#### 2. Request Reschedule
```
POST /api/consultations/doctor/{consultation_id}/request-reschedule/
```
**Request Body:**
```json
{
    "reason": "Patient was delayed due to traffic"
}
```
- Submits reschedule request for overdue consultation
- Only works for consultations that are eligible for reschedule

### For Admins

#### 1. View All Overdue Consultations
```
GET /api/consultations/overdue/
```
- Returns all overdue consultations across all doctors
- Includes reschedule status and request information
- Paginated results

#### 2. Request Reschedule (Admin)
```
POST /api/consultations/{consultation_id}/request-reschedule/
```
**Request Body:**
```json
{
    "reason": "Doctor was called for emergency"
}
```

#### 3. Approve/Reject Reschedule Request
```
POST /api/consultations/{consultation_id}/approve-reschedule/
```
**Request Body:**
```json
{
    "approve": true,
    "reason": "Approved - patient confirmed availability"
}
```
or
```json
{
    "approve": false,
    "reason": "Rejected - patient unavailable for new time"
}
```

#### 4. Apply Approved Reschedule
```
POST /api/consultations/{consultation_id}/apply-reschedule/
```
**Request Body:**
```json
{
    "new_date": "2024-01-15",
    "new_time": "14:30:00",
    "reason": "Rescheduled to accommodate patient schedule"
}
```

## Data Models

### Consultation Model Updates

The Consultation model now includes these new fields:

```python
# Reschedule Information
reschedule_requested = models.BooleanField(default=False)
reschedule_requested_at = models.DateTimeField(null=True, blank=True)
reschedule_requested_by = models.ForeignKey(User, null=True, blank=True)
reschedule_reason = models.TextField(blank=True)
reschedule_approved = models.BooleanField(default=False)
reschedule_approved_by = models.ForeignKey(User, null=True, blank=True)
reschedule_approved_at = models.DateTimeField(null=True, blank=True)
```

### New Status Values

- `overdue`: Consultation time has passed, eligible for reschedule
- `rescheduled`: Consultation has been successfully rescheduled

### New Properties

```python
@property
def is_overdue(self):
    """Check if consultation is overdue"""
    
@property
def is_eligible_for_reschedule(self):
    """Check if consultation is eligible for reschedule"""
    
@property
def hours_overdue(self):
    """Calculate how many hours the consultation is overdue"""
```

## Usage Examples

### Scenario 1: Doctor Requests Reschedule

1. **Doctor logs in and sees overdue consultations**
   ```
   GET /api/consultations/doctor/overdue/
   ```

2. **Doctor requests reschedule for specific consultation**
   ```
   POST /api/consultations/doctor/CON001/request-reschedule/
   {
       "reason": "Patient called to reschedule due to illness"
   }
   ```

3. **System marks consultation as reschedule requested**
   - Status changes to `overdue`
   - `reschedule_requested` set to `true`
   - Request timestamp and reason recorded

### Scenario 2: Admin Reviews and Approves

1. **Admin views all overdue consultations**
   ```
   GET /api/consultations/overdue/
   ```

2. **Admin approves reschedule request**
   ```
   POST /api/consultations/CON001/approve-reschedule/
   {
       "approve": true,
       "reason": "Approved - valid reason provided"
   }
   ```

3. **System marks reschedule as approved**
   - `reschedule_approved` set to `true`
   - Approval timestamp and admin recorded

### Scenario 3: Admin Applies Reschedule

1. **Admin applies the approved reschedule**
   ```
   POST /api/consultations/CON001/apply-reschedule/
   {
       "new_date": "2024-01-20",
       "new_time": "15:00:00",
       "reason": "Rescheduled to next available slot"
   }
   ```

2. **System creates new consultation**
   - New date and time applied
   - Status reset to `scheduled`
   - Reschedule history recorded
   - ConsultationReschedule record created

## Frontend Integration

### Doctor Dashboard

- **Overdue Consultations Tab**: Show consultations that need attention
- **Reschedule Request Button**: Allow doctors to request reschedules
- **Status Indicators**: Clear visual status for reschedule workflow

### Admin Dashboard

- **Overdue Consultations Management**: View and manage all overdue consultations
- **Reschedule Approval Interface**: Review and approve/reject requests
- **Reschedule Application Form**: Set new date/time for approved requests

### Status Display

```javascript
const getRescheduleStatus = (consultation) => {
    if (consultation.reschedule_approved) {
        return 'approved';
    } else if (consultation.reschedule_requested) {
        return 'pending_approval';
    } else if (consultation.is_eligible_for_reschedule) {
        return 'eligible';
    } else {
        return 'not_eligible';
    }
};
```

## Business Rules

### Reschedule Eligibility

- Consultations must not be completed or cancelled
- Must be overdue (past scheduled time)
- Cannot reschedule consultations that are already in progress

### Permission Matrix

| Action | Doctor | Admin | Superadmin |
|--------|--------|-------|------------|
| View own overdue | ✅ | ✅ | ✅ |
| View all overdue | ❌ | ✅ | ✅ |
| Request reschedule | ✅ | ✅ | ✅ |
| Approve reschedule | ❌ | ✅ | ✅ |
| Apply reschedule | ❌ | ✅ | ✅ |

### Time Constraints

- New consultation time must be in the future
- System prevents scheduling conflicts
- Grace period of 1 hour before consultation becomes eligible for reschedule

## Error Handling

### Common Error Scenarios

1. **Consultation Not Eligible**
   ```
   Error: This consultation is not eligible for reschedule
   ```

2. **Permission Denied**
   ```
   Error: You do not have permission to approve reschedule
   ```

3. **Invalid Date/Time**
   ```
   Error: New consultation time must be in the future
   ```

4. **Reschedule Not Approved**
   ```
   Error: Reschedule must be approved before applying
   ```

## Testing

### Test Endpoints

Use these endpoints to test the reschedule functionality:

1. **Create test consultation** with past time
2. **Request reschedule** as doctor
3. **Approve reschedule** as admin
4. **Apply reschedule** with new time
5. **Verify consultation** has new schedule

### Test Data

```python
# Create overdue consultation for testing
from django.utils import timezone
from datetime import timedelta

past_time = timezone.now() - timedelta(hours=2)
consultation = Consultation.objects.create(
    scheduled_date=past_time.date(),
    scheduled_time=past_time.time(),
    # ... other required fields
)
```

## Monitoring and Analytics

### Key Metrics

- Number of overdue consultations
- Reschedule request approval rate
- Average time to reschedule approval
- Most common reschedule reasons

### Dashboard Views

- **Overdue Summary**: Count by status and doctor
- **Reschedule Trends**: Daily/weekly reschedule requests
- **Approval Performance**: Admin response times

## Future Enhancements

1. **Automated Notifications**: Alert patients and doctors of reschedule changes
2. **Bulk Reschedule**: Handle multiple consultations simultaneously
3. **Reschedule Templates**: Predefined reschedule reasons and time slots
4. **Integration with Calendar**: Sync with external calendar systems
5. **Reschedule Analytics**: Advanced reporting and insights

## Support and Troubleshooting

### Common Issues

1. **Migration Errors**: Ensure all migrations are applied
2. **Permission Issues**: Check user roles and clinic assignments
3. **Date Format Issues**: Use ISO format (YYYY-MM-DD) for dates
4. **Time Zone Issues**: All times are handled in UTC

### Debug Information

Enable debug logging to troubleshoot issues:

```python
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Consultation {consultation.id} reschedule status: {consultation.reschedule_status}")
```

## Conclusion

The consultation reschedule system provides a robust workflow for handling overdue consultations while maintaining data integrity and audit trails. The system is designed to be user-friendly for doctors while giving admins full control over the reschedule process.

For additional support or feature requests, please contact the development team.

