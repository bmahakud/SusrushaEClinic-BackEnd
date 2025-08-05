# WhatsApp Notification Setup for Sushrusa EClinic

## Overview

This document explains how the WhatsApp notification system works in the Sushrusa EClinic application. The system automatically sends WhatsApp notifications to both doctors and patients when consultations are created.

## Features

- **Automatic Notifications**: WhatsApp messages are sent automatically when consultations are created
- **Doctor Notifications**: Doctors receive appointment details including date, time, patient name, and meeting link
- **Patient Notifications**: Patients receive appointment confirmation with doctor details and meeting link
- **Template-based**: Uses MSG91 WhatsApp Business API with predefined templates

## WhatsApp Template

### Template Name: `diracai3`

### Template Content:
```
Hello {{1}},

Your appointment has been scheduled successfully on Sushrusa EClinic!

📅 **Appointment Details:**
• Date: {{2}}
• Time: {{3}}
• Patient: {{4}}
• Consultation Type: {{5}}

🔗 **Meeting Link:** {{6}}

Please ensure you're available at the scheduled time. The patient will join via the provided link.

If you need to reschedule, please contact the clinic administrator.

Best regards,
Team DiracAI
Sushrusa EClinic
```

### Template Parameters:
1. **{{1}}**: Recipient name (Doctor/Patient name)
2. **{{2}}**: Appointment date (e.g., "05 August, 2025")
3. **{{3}}**: Appointment time (e.g., "03:50 PM")
4. **{{4}}**: Patient name (for doctor) / Doctor name (for patient)
5. **{{5}}**: Consultation type (e.g., "video", "audio", "chat")
6. **{{6}}**: Meeting link or "Meeting link will be shared soon"

## Configuration

### MSG91 Settings
- **Auth Key**: `416664AgVFnjJ8nhio65d6fc7bP1`
- **Integrated Number**: `917008182954`
- **Template Name**: `diracai3`
- **Namespace**: `1159b496_e313_4115_ace7_0210e4de2eea`
- **API URL**: `https://api.msg91.com/api/v5/whatsapp/whatsapp-outbound-message/bulk/`

### Phone Number Format
- All phone numbers are automatically prefixed with `91` (India country code)
- Example: `+919000000004` becomes `919000000004`

## Implementation Details

### Files Modified/Created:

1. **`consultations/services.py`**: WhatsApp notification service
2. **`consultations/serializers.py`**: Integration with consultation creation
3. **`consultations/views.py`**: Test endpoint for notifications
4. **`consultations/urls.py`**: URL routing for test endpoint
5. **`requirements.txt`**: Added requests library

### Service Class: `WhatsAppNotificationService`

#### Methods:
- `send_doctor_appointment_notification(consultation)`: Sends notification to doctor
- `send_patient_appointment_confirmation(consultation)`: Sends notification to patient

#### Integration Points:
- **ConsultationCreateSerializer**: Sends notifications when consultations are created via slot booking
- **ConsultationCreateDynamicSerializer**: Sends notifications when consultations are created dynamically

## Testing

### Test Endpoint
```
POST /api/consultations/test-whatsapp/
Content-Type: application/json
Authorization: Bearer <token>

{
    "consultation_id": "CON001"
}
```

### Response:
```json
{
    "success": true,
    "doctor_notification_sent": true,
    "patient_notification_sent": true,
    "consultation_id": "CON001",
    "doctor_name": "Dr. John Doe",
    "patient_name": "Jane Smith"
}
```

## Error Handling

### Common Issues:

1. **No Subscription Error**: 
   ```
   "There is no subscription assigned to this number: 917008182954"
   ```
   - **Solution**: Activate MSG91 subscription for the integrated number

2. **Invalid Phone Number**:
   ```
   "No phone number found for doctor/patient"
   ```
   - **Solution**: Ensure doctor/patient has a valid phone number in the database

3. **Template Not Approved**:
   ```
   "Template not found or not approved"
   ```
   - **Solution**: Ensure the template `diracai3` is approved in MSG91 dashboard

### Fallback Behavior:
- If WhatsApp notification fails, consultation creation still succeeds
- Errors are logged but don't prevent consultation creation
- Meeting link defaults to "Meeting link will be shared soon" if not available

## API Payload Structure

### Request Payload:
```json
{
    "integrated_number": "917008182954",
    "content_type": "template",
    "payload": {
        "messaging_product": "whatsapp",
        "type": "template",
        "template": {
            "name": "diracai3",
            "language": {
                "code": "en",
                "policy": "deterministic"
            },
            "namespace": "1159b496_e313_4115_ace7_0210e4de2eea",
            "to_and_components": [
                {
                    "to": ["919000000004"],
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": "Dr. John Doe"},
                                {"type": "text", "text": "05 August, 2025"},
                                {"type": "text", "text": "03:50 PM"},
                                {"type": "text", "text": "Jane Smith"},
                                {"type": "text", "text": "video"},
                                {"type": "text", "text": "https://meet.google.com/abc-defg-hij"}
                            ]
                        }
                    ]
                }
            ]
        }
    }
}
```

## Setup Instructions

1. **MSG91 Account Setup**:
   - Create MSG91 account
   - Add WhatsApp Business API
   - Get auth key and integrated number
   - Create and approve template `diracai3`

2. **Template Approval**:
   - Submit template for approval
   - Wait for WhatsApp approval (usually 24-48 hours)
   - Ensure template parameters match the implementation

3. **Phone Number Verification**:
   - Verify the integrated number in MSG91
   - Ensure it's approved for WhatsApp Business API

4. **Testing**:
   - Use the test endpoint to verify functionality
   - Check logs for any errors
   - Verify notifications are received

## Monitoring and Logs

### Log Messages:
- `📱 Sending WhatsApp notification to doctor/patient: [Name] ([Phone])`
- `✅ WhatsApp notification sent successfully to doctor/patient: [Name]`
- `❌ Failed to send WhatsApp notification to doctor/patient: [Name]`
- `❌ Error sending WhatsApp notification: [Error details]`

### Debug Information:
- Full API payload is logged for debugging
- API response status and content are logged
- Phone number formatting is logged

## Security Considerations

1. **Auth Key**: Store in environment variables in production
2. **Phone Numbers**: Validate and sanitize phone numbers
3. **Rate Limiting**: MSG91 has rate limits, monitor usage
4. **Error Handling**: Don't expose sensitive information in error messages

## Future Enhancements

1. **Multiple Templates**: Support different templates for different scenarios
2. **Scheduled Notifications**: Send reminders before appointments
3. **Status Updates**: Notify about consultation status changes
4. **Custom Messages**: Allow custom message content
5. **Analytics**: Track notification delivery and read receipts 