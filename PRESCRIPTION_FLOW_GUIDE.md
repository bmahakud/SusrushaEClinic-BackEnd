# 🏥 Sushrusa eClinic - Prescription System Flow Guide

## 📋 Overview

The prescription system in Sushrusa eClinic is a comprehensive solution that allows doctors to create, manage, and generate professional PDF prescriptions. The system automatically generates beautifully formatted PDFs when prescriptions are created or finalized.

## 🔄 Complete Prescription Flow

### 1. **Prescription Creation Flow**

```
Patient Consultation → Doctor Creates Prescription → Auto PDF Generation → Patient Receives PDF
```

#### Step-by-Step Process:

1. **Consultation Setup**
   - Patient books consultation with doctor
   - Consultation is scheduled and confirmed
   - Doctor prepares for consultation

2. **Prescription Creation**
   - Doctor creates prescription during/after consultation
   - System automatically generates PDF (draft version)
   - Prescription is saved as draft initially

3. **Prescription Finalization**
   - Doctor reviews and finalizes prescription
   - System generates final PDF with professional formatting
   - PDF is stored with versioning

4. **Patient Access**
   - Patient can view/download prescription PDF
   - PDF includes all medical details, medications, and instructions

### 2. **Prescription Data Structure**

#### Core Prescription Information:
- **Patient Details**: Name, ID, Age, Gender, Contact
- **Doctor Details**: Name, ID, Specialization, Registration Number
- **Consultation Info**: Date, Time, Type, Chief Complaint
- **Vital Signs**: Pulse, BP, Temperature, Weight, Height, etc.
- **Diagnosis**: Primary, Secondary, Clinical Classification
- **Medications**: Name, Dosage, Frequency, Duration, Instructions
- **Instructions**: General, Diet, Lifestyle, Follow-up

#### Medication Format:
- **Dosage**: Morning-Afternoon-Night format (e.g., 1-0-1)
- **Frequency**: Once Daily, Twice Daily, Thrice Daily, etc.
- **Duration**: Days, Weeks, Months, or Continuous
- **Timing**: Before/After meals, Bedtime, etc.

### 3. **PDF Generation Features**

#### Professional Design Elements:
- **Header**: Clinic logo, name, contact information
- **Footer**: Emergency contacts, validity info, digital signature
- **Color Scheme**: Professional blue (#2E86AB) and purple (#A23B72)
- **Layout**: Clean, organized tables and sections
- **Typography**: Professional fonts and sizing

#### PDF Content Sections:
1. **Header**: Clinic branding and prescription label
2. **Patient & Doctor Information**: Complete details in organized tables
3. **Vital Signs**: All recorded vital signs
4. **Diagnosis**: Primary and secondary diagnoses
5. **Medications**: Detailed medication table with dosages
6. **Instructions**: General, diet, and lifestyle advice
7. **Follow-up Plan**: Next visit and follow-up notes
8. **Footer**: Emergency contacts and validity information

### 4. **API Endpoints**

#### Prescription Management:
```
POST   /api/prescriptions/                    # Create prescription
GET    /api/prescriptions/                    # List prescriptions
GET    /api/prescriptions/{id}/               # Get prescription details
PUT    /api/prescriptions/{id}/               # Update prescription
DELETE /api/prescriptions/{id}/               # Delete prescription
```

#### Prescription Actions:
```
POST   /api/prescriptions/{id}/finalize/                    # Finalize prescription
POST   /api/prescriptions/{id}/save-draft/                  # Save as draft
POST   /api/prescriptions/{id}/auto-save/                   # Auto-save draft
POST   /api/prescriptions/{id}/finalize-and-generate-pdf/   # Finalize + generate PDF
```

#### PDF Management:
```
GET    /api/prescriptions/{id}/pdf-versions/                # List PDF versions
GET    /api/prescriptions/{id}/pdf/{version}/               # Download specific PDF
GET    /api/prescriptions/{id}/pdf/latest/                  # Download latest PDF
```

#### Consultation & Patient Specific:
```
GET    /api/prescriptions/consultation/{consultation_id}/   # Get by consultation
GET    /api/prescriptions/patient/{patient_id}/             # Get by patient
GET    /api/prescriptions/patient/{patient_id}/pdfs/        # Get patient PDFs
```

#### Special Endpoints:
```
GET    /api/prescriptions/drafts/                           # Get draft prescriptions
GET    /api/prescriptions/finalized/                        # Get finalized prescriptions
```

### 5. **Automatic PDF Generation**

#### When PDFs are Generated:
1. **On Prescription Creation**: Draft PDF is automatically generated
2. **On Prescription Finalization**: Final PDF is generated with professional formatting
3. **On Manual Request**: PDF can be regenerated anytime

#### PDF Versioning:
- Each prescription can have multiple PDF versions
- Version numbers are automatically incremented
- Current version is marked for easy access
- All versions are preserved for audit trail

#### PDF Storage:
- PDFs are stored in the `PrescriptionPDF` model
- Files are saved with unique names
- Checksums are calculated for integrity
- File sizes are recorded

### 6. **User Roles & Permissions**

#### Doctor:
- ✅ Create prescriptions for their patients
- ✅ Edit their own prescriptions
- ✅ Finalize prescriptions
- ✅ Generate PDFs
- ✅ View all their prescriptions

#### Patient:
- ✅ View their own prescriptions
- ✅ Download their prescription PDFs
- ❌ Cannot edit prescriptions

#### Admin:
- ✅ View all prescriptions in their clinic
- ✅ Access all PDFs
- ✅ Manage prescription settings

#### SuperAdmin:
- ✅ Full access to all prescriptions
- ✅ System-wide management

### 7. **Prescription Status Flow**

```
DRAFT → FINALIZED → PDF GENERATED → PATIENT ACCESSIBLE
```

#### Status Transitions:
1. **Draft**: Initial state when prescription is created
2. **Finalized**: When doctor finalizes the prescription
3. **PDF Generated**: Professional PDF is created
4. **Patient Accessible**: Patient can view/download

### 8. **Error Handling & Validation**

#### Validation Rules:
- Patient and doctor must be specified
- At least one medication is required for finalized prescriptions
- Vital signs are optional but recommended
- Diagnosis should be provided for finalized prescriptions

#### Error Responses:
- **400**: Validation errors with detailed messages
- **403**: Permission denied
- **404**: Prescription not found
- **500**: PDF generation errors

### 9. **Integration Points**

#### With Consultation System:
- Prescriptions are linked to consultations
- Consultation details are included in PDFs
- Patient history is accessible

#### With User Management:
- Doctor and patient information is pulled from user profiles
- Role-based permissions are enforced
- User authentication is required

#### With File Storage:
- PDFs are stored in media directory
- Optional integration with cloud storage (DigitalOcean Spaces)
- File upload for custom headers/footers

### 10. **Best Practices**

#### For Doctors:
- Always include complete patient information
- Provide detailed medication instructions
- Add relevant vital signs
- Include follow-up instructions
- Review before finalizing

#### For System Administrators:
- Monitor PDF generation logs
- Ensure sufficient storage space
- Regular backup of prescription data
- Monitor system performance

#### For Developers:
- Use proper error handling
- Implement async PDF generation for better performance
- Follow the established API patterns
- Maintain backward compatibility

## 🚀 Getting Started

### 1. **Create a Prescription**
```bash
POST /api/prescriptions/
{
  "consultation": "consultation_id",
  "patient": "patient_id",
  "primary_diagnosis": "Hypertension",
  "medications": [
    {
      "medicine_name": "Amlodipine",
      "composition": "5mg tablet",
      "morning_dose": 1,
      "afternoon_dose": 0,
      "evening_dose": 0,
      "frequency": "once_daily",
      "duration_days": 30
    }
  ],
  "general_instructions": "Take medication regularly",
  "next_visit": "After 30 days"
}
```

### 2. **Finalize and Generate PDF**
```bash
POST /api/prescriptions/{id}/finalize-and-generate-pdf/
```

### 3. **Download PDF**
```bash
GET /api/prescriptions/{id}/pdf/latest/
```

## 📊 Monitoring & Logs

The system provides comprehensive logging for:
- Prescription creation and updates
- PDF generation success/failure
- User access patterns
- Error tracking and debugging

## 🔧 Configuration

### Environment Variables:
- `ALWAYS_UPLOAD_FILES_TO_AWS`: Enable cloud storage upload
- `AWS_ACCESS_KEY_ID`: Cloud storage credentials
- `AWS_SECRET_ACCESS_KEY`: Cloud storage credentials
- `AWS_STORAGE_BUCKET_NAME`: Cloud storage bucket

### Media Files:
- Header images: `media/prescription_headers/`
- Footer images: `media/prescription_footers/`
- Generated PDFs: `media/prescriptions/pdfs/`

## 📞 Support

For technical support or questions about the prescription system:
- Email: tech-support@sushrusa.com
- Documentation: `/api/docs/`
- API Schema: `/api/schema/`

---

**© 2024 Sushrusa eClinic. All rights reserved.** 