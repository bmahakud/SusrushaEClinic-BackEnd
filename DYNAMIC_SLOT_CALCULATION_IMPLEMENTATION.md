# Dynamic Slot Calculation Implementation

## Overview

This document explains the implementation of dynamic slot calculation for the admin consultation creation functionality. Instead of pre-generating slots, the system now calculates available consultation slots on-the-fly based on doctor availability and clinic consultation duration.

## Problem Statement

Previously, the system required:
1. Doctors to manually create availability slots
2. Admins to select from pre-created slots
3. Manual slot management which was cumbersome

## Solution: Dynamic Slot Calculation

### Core Concept
- **No Pre-Generated Slots**: Slots are calculated dynamically when needed
- **Real-Time Calculation**: Based on doctor's availability periods and clinic's consultation duration
- **Automatic Division**: Available time periods are automatically divided into consultation slots
- **Conflict Detection**: System checks for overlapping consultations

## Implementation Details

### 1. Backend API Endpoint

**New Endpoint**: `GET /api/consultations/calculate_available_slots/`

**Parameters**:
- `doctor_id`: Doctor's user ID
- `clinic_id`: Clinic ID
- `date`: Date in YYYY-MM-DD format

**Response**:
```json
{
  "success": true,
  "data": {
    "slots": [
      {
        "start_time": "09:00",
        "end_time": "09:15",
        "duration_minutes": 15,
        "clinic_name": "Heart Care Clinic",
        "doctor_name": "Dr. Sarah Johnson",
        "is_available": true
      }
    ],
    "clinic_duration": 15,
    "date": "2024-12-25",
    "doctor_name": "Dr. Sarah Johnson",
    "clinic_name": "Heart Care Clinic"
  },
  "message": "Calculated 8 available slots for 2024-12-25"
}
```

### 2. Calculation Logic

```python
# 1. Get doctor's availability for the date
available_slots = DoctorSlot.objects.filter(
    doctor=doctor,
    date=date_obj,
    is_available=True,
    is_booked=False
).order_by('start_time')

# 2. Get clinic consultation duration
consultation_duration = clinic.consultation_duration  # in minutes

# 3. For each availability period, divide into consultation slots
for slot in available_slots:
    slot_start = datetime.combine(date_obj, slot.start_time)
    slot_end = datetime.combine(date_obj, slot.end_time)
    current_time = slot_start
    
    while current_time < slot_end:
        slot_end_time = current_time + timedelta(minutes=consultation_duration)
        
        if slot_end_time > slot_end:
            break
            
        # Check for overlapping consultations
        overlapping_consultation = Consultation.objects.filter(
            doctor=doctor,
            scheduled_date=date_obj,
            status__in=['scheduled', 'in_progress']
        ).filter(
            scheduled_time__lt=slot_end_time.time(),
            scheduled_time__gte=current_time.time()
        ).first()
        
        if not overlapping_consultation:
            # Add this slot to available slots
            calculated_slots.append({
                'start_time': current_time.time().strftime('%H:%M'),
                'end_time': slot_end_time.time().strftime('%H:%M'),
                'duration_minutes': consultation_duration,
                'clinic_name': clinic.name,
                'doctor_name': doctor.name,
                'is_available': True
            })
        
        current_time = slot_end_time
```

### 3. Frontend Integration

**New API Function**:
```typescript
export const calculateAvailableSlots = async (params: {
  doctor_id: string | number;
  clinic_id: string | number;
  date: string; // YYYY-MM-DD
}): Promise<{
  slots: Array<{
    start_time: string;
    end_time: string;
    duration_minutes: number;
    clinic_name: string;
    doctor_name: string;
    is_available: boolean;
  }>;
  clinic_duration: number;
  date: string;
  doctor_name: string;
  clinic_name: string;
}> => {
  const queryParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    queryParams.append(key, value.toString());
  });
  
  const response = await api.get(`/api/consultations/calculate_available_slots/?${queryParams.toString()}`);
  return response.data.data;
};
```

**Updated Consultation Creation Flow**:
1. Admin selects patient
2. Admin selects doctor
3. Admin selects clinic
4. Admin selects date
5. **System automatically calculates available slots**
6. Admin selects from calculated slots
7. Admin fills consultation details
8. Consultation is created

## Benefits

### 1. **Seamless User Experience**
- No manual slot creation required
- Real-time slot availability
- Automatic conflict detection

### 2. **Flexibility**
- Different clinics can have different consultation durations
- Slots adapt automatically to clinic settings
- Easy to modify consultation duration per clinic

### 3. **Efficiency**
- No wasted slots
- Optimal time utilization
- Reduced administrative overhead

### 4. **Accuracy**
- Real-time availability
- No double-booking
- Automatic conflict resolution

## Example Scenarios

### Scenario 1: 15-minute Clinic
- Doctor available: 9:00 AM - 11:00 AM
- Clinic duration: 15 minutes
- **Result**: 8 consultation slots (9:00, 9:15, 9:30, 9:45, 10:00, 10:15, 10:30, 10:45)

### Scenario 2: 30-minute Clinic
- Doctor available: 9:00 AM - 11:00 AM
- Clinic duration: 30 minutes
- **Result**: 4 consultation slots (9:00, 9:30, 10:00, 10:30)

### Scenario 3: Mixed Availability
- Doctor available: 9:00-10:00 AM, 2:00-4:00 PM
- Clinic duration: 20 minutes
- **Result**: 6 consultation slots (9:00, 9:20, 9:40, 2:00, 2:20, 2:40, 3:00, 3:20, 3:40)

## Error Handling

### 1. **Missing Parameters**
```json
{
  "success": false,
  "error": {
    "code": "MISSING_PARAMETERS",
    "message": "doctor_id, clinic_id, and date are required"
  }
}
```

### 2. **Invalid Date**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_DATE",
    "message": "Invalid date format. Use YYYY-MM-DD"
  }
}
```

### 3. **Doctor Not Found**
```json
{
  "success": false,
  "error": {
    "code": "DOCTOR_NOT_FOUND",
    "message": "Doctor not found"
  }
}
```

### 4. **Clinic Not Found**
```json
{
  "success": false,
  "error": {
    "code": "CLINIC_NOT_FOUND",
    "message": "Clinic not found"
  }
}
```

## Future Enhancements

### 1. **Advanced Slot Calculation**
- Consider doctor's preferred consultation duration
- Factor in break times
- Account for travel time between consultations

### 2. **Smart Scheduling**
- AI-powered slot optimization
- Patient preference matching
- Urgency-based slot allocation

### 3. **Real-time Updates**
- WebSocket integration for live slot updates
- Push notifications for slot changes
- Collaborative scheduling

### 4. **Analytics**
- Slot utilization metrics
- Peak time analysis
- Doctor availability patterns

## Testing

### Unit Tests
- Test slot calculation logic
- Test conflict detection
- Test edge cases (no availability, full day, etc.)

### Integration Tests
- Test API endpoint
- Test frontend integration
- Test consultation creation flow

### Manual Testing
- Test with different clinic durations
- Test with overlapping consultations
- Test with various availability patterns

## Conclusion

The dynamic slot calculation system provides a much more efficient and user-friendly approach to consultation scheduling. It eliminates the need for manual slot management while ensuring optimal time utilization and preventing conflicts. The system is flexible, scalable, and provides a seamless experience for both administrators and doctors. 