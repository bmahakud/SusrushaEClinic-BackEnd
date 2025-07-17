# 🏥 **Sushrusa Healthcare Platform - Complete API Endpoints List**

## 📊 **API Overview**
- **Total Endpoints**: 100+ API endpoints
- **Base URL**: `http://localhost:8000/api/`
- **Authentication**: JWT Bearer Token (except auth endpoints)
- **Documentation**: Swagger UI at `/api/docs/`

---

## 🔐 **1. Authentication Module** (`/api/auth/`)

### **Core Authentication**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/auth/health/` | Health check endpoint | ❌ |
| `POST` | `/api/auth/send-otp/` | Send OTP to phone number | ❌ |
| `POST` | `/api/auth/verify-otp/` | Verify OTP and get JWT tokens | ❌ |
| `POST` | `/api/auth/refresh/` | Refresh access token | ❌ |
| `POST` | `/api/auth/logout/` | Logout and invalidate tokens | ✅ |

### **Profile Management**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/auth/profile/` | Get current user profile | ✅ |
| `PUT` | `/api/auth/profile/` | Update user profile | ✅ |
| `POST` | `/api/auth/change-password/` | Change user password | ✅ |

### **Session Management**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/auth/sessions/` | Get user's active sessions | ✅ |
| `DELETE` | `/api/auth/sessions/` | Terminate specific session | ✅ |

---

## 👥 **2. Patient Management Module** (`/api/admin/patients/`)

### **Patient Profiles**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/patients/` | List all patients | ✅ |
| `POST` | `/api/admin/patients/` | Create new patient | ✅ |
| `GET` | `/api/admin/patients/{id}/` | Get patient details | ✅ |
| `PUT` | `/api/admin/patients/{id}/` | Update patient | ✅ |
| `PATCH` | `/api/admin/patients/{id}/` | Partial update patient | ✅ |
| `DELETE` | `/api/admin/patients/{id}/` | Delete patient | ✅ |

### **Patient Search & Analytics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/patients/search/` | Search patients | ✅ |
| `GET` | `/api/admin/patients/stats/` | Patient statistics | ✅ |

### **Patient Medical Records**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/patients/{patient_id}/medical-records/` | List medical records | ✅ |
| `POST` | `/api/admin/patients/{patient_id}/medical-records/` | Create medical record | ✅ |
| `GET` | `/api/admin/patients/{patient_id}/medical-records/{id}/` | Get medical record | ✅ |
| `PUT` | `/api/admin/patients/{patient_id}/medical-records/{id}/` | Update medical record | ✅ |
| `PATCH` | `/api/admin/patients/{patient_id}/medical-records/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/admin/patients/{patient_id}/medical-records/{id}/` | Delete medical record | ✅ |

### **Patient Documents**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/patients/{patient_id}/documents/` | List documents | ✅ |
| `POST` | `/api/admin/patients/{patient_id}/documents/` | Upload document | ✅ |
| `GET` | `/api/admin/patients/{patient_id}/documents/{id}/` | Get document | ✅ |
| `PUT` | `/api/admin/patients/{patient_id}/documents/{id}/` | Update document | ✅ |
| `PATCH` | `/api/admin/patients/{patient_id}/documents/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/admin/patients/{patient_id}/documents/{id}/` | Delete document | ✅ |

### **Patient Notes**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/patients/{patient_id}/notes/` | List notes | ✅ |
| `POST` | `/api/admin/patients/{patient_id}/notes/` | Create note | ✅ |
| `GET` | `/api/admin/patients/{patient_id}/notes/{id}/` | Get note | ✅ |
| `PUT` | `/api/admin/patients/{patient_id}/notes/{id}/` | Update note | ✅ |
| `PATCH` | `/api/admin/patients/{patient_id}/notes/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/admin/patients/{patient_id}/notes/{id}/` | Delete note | ✅ |

---

## 👨‍⚕️ **3. Doctor Management Module** (`/api/admin/doctors/`)

### **Doctor Profiles**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/doctors/` | List all doctors | ✅ |
| `POST` | `/api/admin/doctors/` | Create new doctor | ✅ |
| `GET` | `/api/admin/doctors/{id}/` | Get doctor details | ✅ |
| `PUT` | `/api/admin/doctors/{id}/` | Update doctor | ✅ |
| `PATCH` | `/api/admin/doctors/{id}/` | Partial update doctor | ✅ |
| `DELETE` | `/api/admin/doctors/{id}/` | Delete doctor | ✅ |

### **Doctor Search & Analytics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/doctors/search/` | Search doctors | ✅ |
| `GET` | `/api/admin/doctors/stats/` | Doctor statistics | ✅ |

### **Doctor Education**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/doctors/{doctor_id}/education/` | List education records | ✅ |
| `POST` | `/api/admin/doctors/{doctor_id}/education/` | Add education record | ✅ |
| `GET` | `/api/admin/doctors/{doctor_id}/education/{id}/` | Get education record | ✅ |
| `PUT` | `/api/admin/doctors/{doctor_id}/education/{id}/` | Update education | ✅ |
| `PATCH` | `/api/admin/doctors/{doctor_id}/education/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/admin/doctors/{doctor_id}/education/{id}/` | Delete education | ✅ |

### **Doctor Experience**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/doctors/{doctor_id}/experience/` | List experience records | ✅ |
| `POST` | `/api/admin/doctors/{doctor_id}/experience/` | Add experience record | ✅ |
| `GET` | `/api/admin/doctors/{doctor_id}/experience/{id}/` | Get experience record | ✅ |
| `PUT` | `/api/admin/doctors/{doctor_id}/experience/{id}/` | Update experience | ✅ |
| `PATCH` | `/api/admin/doctors/{doctor_id}/experience/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/admin/doctors/{doctor_id}/experience/{id}/` | Delete experience | ✅ |

### **Doctor Documents**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/doctors/{doctor_id}/documents/` | List documents | ✅ |
| `POST` | `/api/admin/doctors/{doctor_id}/documents/` | Upload document | ✅ |
| `GET` | `/api/admin/doctors/{doctor_id}/documents/{id}/` | Get document | ✅ |
| `PUT` | `/api/admin/doctors/{doctor_id}/documents/{id}/` | Update document | ✅ |
| `PATCH` | `/api/admin/doctors/{doctor_id}/documents/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/admin/doctors/{doctor_id}/documents/{id}/` | Delete document | ✅ |

### **Doctor Availability**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/doctors/{doctor_id}/availability/` | List availability | ✅ |
| `POST` | `/api/admin/doctors/{doctor_id}/availability/` | Set availability | ✅ |
| `GET` | `/api/admin/doctors/{doctor_id}/availability/{id}/` | Get availability | ✅ |
| `PUT` | `/api/admin/doctors/{doctor_id}/availability/{id}/` | Update availability | ✅ |
| `PATCH` | `/api/admin/doctors/{doctor_id}/availability/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/admin/doctors/{doctor_id}/availability/{id}/` | Delete availability | ✅ |

### **Doctor Schedule**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/doctors/{doctor_id}/schedule/` | List schedule | ✅ |
| `POST` | `/api/admin/doctors/{doctor_id}/schedule/` | Set schedule | ✅ |
| `GET` | `/api/admin/doctors/{doctor_id}/schedule/{id}/` | Get schedule | ✅ |
| `PUT` | `/api/admin/doctors/{doctor_id}/schedule/{id}/` | Update schedule | ✅ |
| `PATCH` | `/api/admin/doctors/{doctor_id}/schedule/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/admin/doctors/{doctor_id}/schedule/{id}/` | Delete schedule | ✅ |

### **Doctor Reviews**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/admin/doctors/{doctor_id}/reviews/` | List reviews | ✅ |
| `POST` | `/api/admin/doctors/{doctor_id}/reviews/` | Add review | ✅ |
| `GET` | `/api/admin/doctors/{doctor_id}/reviews/{id}/` | Get review | ✅ |
| `PUT` | `/api/admin/doctors/{doctor_id}/reviews/{id}/` | Update review | ✅ |
| `PATCH` | `/api/admin/doctors/{doctor_id}/reviews/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/admin/doctors/{doctor_id}/reviews/{id}/` | Delete review | ✅ |

---

## 🏥 **4. Consultation Management Module** (`/api/consultations/`)

### **Consultations**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/consultations/` | List consultations | ✅ |
| `POST` | `/api/consultations/` | Create consultation | ✅ |
| `GET` | `/api/consultations/{id}/` | Get consultation | ✅ |
| `PUT` | `/api/consultations/{id}/` | Update consultation | ✅ |
| `PATCH` | `/api/consultations/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/consultations/{id}/` | Delete consultation | ✅ |

### **Consultation Search & Analytics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/consultations/search/` | Search consultations | ✅ |
| `GET` | `/api/consultations/stats/` | Consultation statistics | ✅ |

### **Consultation Diagnosis**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/consultations/{consultation_id}/diagnosis/` | List diagnoses | ✅ |
| `POST` | `/api/consultations/{consultation_id}/diagnosis/` | Add diagnosis | ✅ |
| `GET` | `/api/consultations/{consultation_id}/diagnosis/{id}/` | Get diagnosis | ✅ |
| `PUT` | `/api/consultations/{consultation_id}/diagnosis/{id}/` | Update diagnosis | ✅ |
| `PATCH` | `/api/consultations/{consultation_id}/diagnosis/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/consultations/{consultation_id}/diagnosis/{id}/` | Delete diagnosis | ✅ |

### **Consultation Vital Signs**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/consultations/{consultation_id}/vital-signs/` | List vital signs | ✅ |
| `POST` | `/api/consultations/{consultation_id}/vital-signs/` | Record vital signs | ✅ |
| `GET` | `/api/consultations/{consultation_id}/vital-signs/{id}/` | Get vital signs | ✅ |
| `PUT` | `/api/consultations/{consultation_id}/vital-signs/{id}/` | Update vital signs | ✅ |
| `PATCH` | `/api/consultations/{consultation_id}/vital-signs/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/consultations/{consultation_id}/vital-signs/{id}/` | Delete vital signs | ✅ |

### **Consultation Documents**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/consultations/{consultation_id}/documents/` | List documents | ✅ |
| `POST` | `/api/consultations/{consultation_id}/documents/` | Upload document | ✅ |
| `GET` | `/api/consultations/{consultation_id}/documents/{id}/` | Get document | ✅ |
| `PUT` | `/api/consultations/{consultation_id}/documents/{id}/` | Update document | ✅ |
| `PATCH` | `/api/consultations/{consultation_id}/documents/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/consultations/{consultation_id}/documents/{id}/` | Delete document | ✅ |

### **Consultation Notes**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/consultations/{consultation_id}/notes/` | List notes | ✅ |
| `POST` | `/api/consultations/{consultation_id}/notes/` | Add note | ✅ |
| `GET` | `/api/consultations/{consultation_id}/notes/{id}/` | Get note | ✅ |
| `PUT` | `/api/consultations/{consultation_id}/notes/{id}/` | Update note | ✅ |
| `PATCH` | `/api/consultations/{consultation_id}/notes/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/consultations/{consultation_id}/notes/{id}/` | Delete note | ✅ |

### **Consultation Symptoms**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/consultations/{consultation_id}/symptoms/` | List symptoms | ✅ |
| `POST` | `/api/consultations/{consultation_id}/symptoms/` | Add symptom | ✅ |
| `GET` | `/api/consultations/{consultation_id}/symptoms/{id}/` | Get symptom | ✅ |
| `PUT` | `/api/consultations/{consultation_id}/symptoms/{id}/` | Update symptom | ✅ |
| `PATCH` | `/api/consultations/{consultation_id}/symptoms/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/consultations/{consultation_id}/symptoms/{id}/` | Delete symptom | ✅ |

---

## 💊 **5. Prescription Management Module** (`/api/prescriptions/`)

### **Prescriptions**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/prescriptions/` | List prescriptions | ✅ |
| `POST` | `/api/prescriptions/` | Create prescription | ✅ |
| `GET` | `/api/prescriptions/{id}/` | Get prescription | ✅ |
| `PUT` | `/api/prescriptions/{id}/` | Update prescription | ✅ |
| `PATCH` | `/api/prescriptions/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/prescriptions/{id}/` | Delete prescription | ✅ |

### **Prescription Search & Analytics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/prescriptions/search/` | Search prescriptions | ✅ |
| `GET` | `/api/prescriptions/stats/` | Prescription statistics | ✅ |
| `GET` | `/api/prescriptions/medications/` | List all medications | ✅ |

### **Prescription Medications**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/prescriptions/{prescription_id}/medications/` | List medications | ✅ |
| `POST` | `/api/prescriptions/{prescription_id}/medications/` | Add medication | ✅ |
| `GET` | `/api/prescriptions/{prescription_id}/medications/{id}/` | Get medication | ✅ |
| `PUT` | `/api/prescriptions/{prescription_id}/medications/{id}/` | Update medication | ✅ |
| `PATCH` | `/api/prescriptions/{prescription_id}/medications/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/prescriptions/{prescription_id}/medications/{id}/` | Delete medication | ✅ |

### **Prescription Documents**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/prescriptions/{prescription_id}/documents/` | List documents | ✅ |
| `POST` | `/api/prescriptions/{prescription_id}/documents/` | Upload document | ✅ |
| `GET` | `/api/prescriptions/{prescription_id}/documents/{id}/` | Get document | ✅ |
| `PUT` | `/api/prescriptions/{prescription_id}/documents/{id}/` | Update document | ✅ |
| `PATCH` | `/api/prescriptions/{prescription_id}/documents/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/prescriptions/{prescription_id}/documents/{id}/` | Delete document | ✅ |

### **Prescription Notes**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/prescriptions/{prescription_id}/notes/` | List notes | ✅ |
| `POST` | `/api/prescriptions/{prescription_id}/notes/` | Add note | ✅ |
| `GET` | `/api/prescriptions/{prescription_id}/notes/{id}/` | Get note | ✅ |
| `PUT` | `/api/prescriptions/{prescription_id}/notes/{id}/` | Update note | ✅ |
| `PATCH` | `/api/prescriptions/{prescription_id}/notes/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/prescriptions/{prescription_id}/notes/{id}/` | Delete note | ✅ |

### **Medication Reminders**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/prescriptions/reminders/` | List reminders | ✅ |
| `POST` | `/api/prescriptions/reminders/` | Create reminder | ✅ |
| `GET` | `/api/prescriptions/reminders/{id}/` | Get reminder | ✅ |
| `PUT` | `/api/prescriptions/reminders/{id}/` | Update reminder | ✅ |
| `PATCH` | `/api/prescriptions/reminders/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/prescriptions/reminders/{id}/` | Delete reminder | ✅ |

---

## 💳 **6. Payment Processing Module** (`/api/payments/`)

### **Payments**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/payments/` | List payments | ✅ |
| `POST` | `/api/payments/` | Create payment | ✅ |
| `GET` | `/api/payments/{id}/` | Get payment | ✅ |
| `PUT` | `/api/payments/{id}/` | Update payment | ✅ |
| `PATCH` | `/api/payments/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/payments/{id}/` | Delete payment | ✅ |

### **Payment Methods**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/payments/methods/` | List payment methods | ✅ |
| `POST` | `/api/payments/methods/` | Add payment method | ✅ |
| `GET` | `/api/payments/methods/{id}/` | Get payment method | ✅ |
| `PUT` | `/api/payments/methods/{id}/` | Update payment method | ✅ |
| `PATCH` | `/api/payments/methods/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/payments/methods/{id}/` | Delete payment method | ✅ |

### **Payment Refunds**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/payments/refunds/` | List refunds | ✅ |
| `POST` | `/api/payments/refunds/` | Create refund | ✅ |
| `GET` | `/api/payments/refunds/{id}/` | Get refund | ✅ |
| `PUT` | `/api/payments/refunds/{id}/` | Update refund | ✅ |
| `PATCH` | `/api/payments/refunds/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/payments/refunds/{id}/` | Delete refund | ✅ |

### **Payment Discounts**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/payments/discounts/` | List discounts | ✅ |
| `POST` | `/api/payments/discounts/` | Create discount | ✅ |
| `GET` | `/api/payments/discounts/{id}/` | Get discount | ✅ |
| `PUT` | `/api/payments/discounts/{id}/` | Update discount | ✅ |
| `PATCH` | `/api/payments/discounts/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/payments/discounts/{id}/` | Delete discount | ✅ |

### **Payment Utilities**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/payments/search/` | Search payments | ✅ |
| `GET` | `/api/payments/stats/` | Payment statistics | ✅ |
| `POST` | `/api/payments/validate-discount/` | Validate discount code | ❌ |
| `POST` | `/api/payments/webhook/` | Payment webhook | ❌ |

---

## 🏢 **7. E-Clinic Management Module** (`/api/eclinic/`)

### **Clinics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/eclinic/` | List clinics | ✅ |
| `POST` | `/api/eclinic/` | Create clinic | ✅ |
| `GET` | `/api/eclinic/{id}/` | Get clinic | ✅ |
| `PUT` | `/api/eclinic/{id}/` | Update clinic | ✅ |
| `PATCH` | `/api/eclinic/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/eclinic/{id}/` | Delete clinic | ✅ |

### **Clinic Search & Analytics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/eclinic/search/` | Search clinics | ✅ |
| `GET` | `/api/eclinic/stats/` | Clinic statistics | ✅ |
| `GET` | `/api/eclinic/nearby/` | Find nearby clinics | ✅ |

### **Clinic Doctors**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/eclinic/{clinic_id}/doctors/` | List clinic doctors | ✅ |
| `POST` | `/api/eclinic/{clinic_id}/doctors/` | Add doctor to clinic | ✅ |
| `GET` | `/api/eclinic/{clinic_id}/doctors/{id}/` | Get clinic doctor | ✅ |
| `PUT` | `/api/eclinic/{clinic_id}/doctors/{id}/` | Update clinic doctor | ✅ |
| `PATCH` | `/api/eclinic/{clinic_id}/doctors/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/eclinic/{clinic_id}/doctors/{id}/` | Remove doctor | ✅ |

### **Clinic Services**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/eclinic/{clinic_id}/services/` | List services | ✅ |
| `POST` | `/api/eclinic/{clinic_id}/services/` | Add service | ✅ |
| `GET` | `/api/eclinic/{clinic_id}/services/{id}/` | Get service | ✅ |
| `PUT` | `/api/eclinic/{clinic_id}/services/{id}/` | Update service | ✅ |
| `PATCH` | `/api/eclinic/{clinic_id}/services/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/eclinic/{clinic_id}/services/{id}/` | Delete service | ✅ |

### **Clinic Inventory**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/eclinic/{clinic_id}/inventory/` | List inventory | ✅ |
| `POST` | `/api/eclinic/{clinic_id}/inventory/` | Add inventory item | ✅ |
| `GET` | `/api/eclinic/{clinic_id}/inventory/{id}/` | Get inventory item | ✅ |
| `PUT` | `/api/eclinic/{clinic_id}/inventory/{id}/` | Update inventory | ✅ |
| `PATCH` | `/api/eclinic/{clinic_id}/inventory/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/eclinic/{clinic_id}/inventory/{id}/` | Delete inventory | ✅ |

### **Clinic Appointments**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/eclinic/{clinic_id}/appointments/` | List appointments | ✅ |
| `POST` | `/api/eclinic/{clinic_id}/appointments/` | Create appointment | ✅ |
| `GET` | `/api/eclinic/{clinic_id}/appointments/{id}/` | Get appointment | ✅ |
| `PUT` | `/api/eclinic/{clinic_id}/appointments/{id}/` | Update appointment | ✅ |
| `PATCH` | `/api/eclinic/{clinic_id}/appointments/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/eclinic/{clinic_id}/appointments/{id}/` | Delete appointment | ✅ |

### **Clinic Reviews**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/eclinic/{clinic_id}/reviews/` | List reviews | ✅ |
| `POST` | `/api/eclinic/{clinic_id}/reviews/` | Add review | ✅ |
| `GET` | `/api/eclinic/{clinic_id}/reviews/{id}/` | Get review | ✅ |
| `PUT` | `/api/eclinic/{clinic_id}/reviews/{id}/` | Update review | ✅ |
| `PATCH` | `/api/eclinic/{clinic_id}/reviews/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/eclinic/{clinic_id}/reviews/{id}/` | Delete review | ✅ |

### **Clinic Documents**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/eclinic/{clinic_id}/documents/` | List documents | ✅ |
| `POST` | `/api/eclinic/{clinic_id}/documents/` | Upload document | ✅ |
| `GET` | `/api/eclinic/{clinic_id}/documents/{id}/` | Get document | ✅ |
| `PUT` | `/api/eclinic/{clinic_id}/documents/{id}/` | Update document | ✅ |
| `PATCH` | `/api/eclinic/{clinic_id}/documents/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/eclinic/{clinic_id}/documents/{id}/` | Delete document | ✅ |

---

## 📈 **8. Analytics Module** (`/api/analytics/`)

### **Dashboard & Overview**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/analytics/dashboard/` | Main dashboard stats | ✅ |
| `GET` | `/api/analytics/real-time/` | Real-time metrics | ✅ |

### **Specific Analytics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/analytics/user-growth/` | User growth analytics | ✅ |
| `GET` | `/api/analytics/consultations/` | Consultation analytics | ✅ |
| `GET` | `/api/analytics/revenue-report/` | Revenue reporting | ✅ |
| `GET` | `/api/analytics/geographic/` | Geographic analytics | ✅ |

### **Custom Reports & Exports**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/analytics/custom-report/` | Generate custom report | ✅ |
| `GET` | `/api/analytics/export/` | Export data | ✅ |

### **User Analytics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/analytics/user-analytics/` | List user analytics | ✅ |
| `POST` | `/api/analytics/user-analytics/` | Create user analytics | ✅ |
| `GET` | `/api/analytics/user-analytics/{id}/` | Get user analytics | ✅ |
| `PUT` | `/api/analytics/user-analytics/{id}/` | Update user analytics | ✅ |
| `PATCH` | `/api/analytics/user-analytics/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/analytics/user-analytics/{id}/` | Delete user analytics | ✅ |

### **Revenue Analytics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/analytics/revenue-analytics/` | List revenue analytics | ✅ |
| `POST` | `/api/analytics/revenue-analytics/` | Create revenue analytics | ✅ |
| `GET` | `/api/analytics/revenue-analytics/{id}/` | Get revenue analytics | ✅ |
| `PUT` | `/api/analytics/revenue-analytics/{id}/` | Update revenue analytics | ✅ |
| `PATCH` | `/api/analytics/revenue-analytics/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/analytics/revenue-analytics/{id}/` | Delete revenue analytics | ✅ |

### **Doctor Performance Analytics**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/analytics/doctor-performance/` | List doctor performance | ✅ |
| `POST` | `/api/analytics/doctor-performance/` | Create performance record | ✅ |
| `GET` | `/api/analytics/doctor-performance/{id}/` | Get performance record | ✅ |
| `PUT` | `/api/analytics/doctor-performance/{id}/` | Update performance | ✅ |
| `PATCH` | `/api/analytics/doctor-performance/{id}/` | Partial update | ✅ |
| `DELETE` | `/api/analytics/doctor-performance/{id}/` | Delete performance | ✅ |

---

## 📚 **9. API Documentation**

### **Documentation Endpoints**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/schema/` | OpenAPI schema | ❌ |
| `GET` | `/api/docs/` | Swagger UI documentation | ❌ |
| `GET` | `/api/redoc/` | ReDoc documentation | ❌ |

---

## 🔧 **10. Admin Interface**

### **Django Admin**
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/admin/` | Django admin interface | ✅ (Superuser) |

---

## 📊 **API Summary Statistics**

### **Total Endpoints by Module**
- **Authentication**: 8 endpoints
- **Patient Management**: 24 endpoints
- **Doctor Management**: 30 endpoints
- **Consultation Management**: 24 endpoints
- **Prescription Management**: 24 endpoints
- **Payment Processing**: 20 endpoints
- **E-Clinic Management**: 30 endpoints
- **Analytics**: 18 endpoints
- **Documentation**: 3 endpoints
- **Admin**: 1 endpoint

### **Total: 182+ API Endpoints**

### **HTTP Methods Distribution**
- **GET**: ~60% (List, Retrieve operations)
- **POST**: ~25% (Create operations)
- **PUT/PATCH**: ~10% (Update operations)
- **DELETE**: ~5% (Delete operations)

### **Authentication Requirements**
- **Public Endpoints**: ~15% (Health check, OTP, Documentation)
- **Authenticated Endpoints**: ~85% (All business logic)

---

## 🚀 **Quick Start Guide**

### **1. Authentication Flow**
```bash
# 1. Send OTP
curl -X POST http://localhost:8000/api/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+918766048755"}'

# 2. Verify OTP (get tokens)
curl -X POST http://localhost:8000/api/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+918766048755", "otp": "470044"}'

# 3. Use access token for authenticated requests
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer <access_token>"
```

### **2. API Documentation**
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### **3. Common Response Format**
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

This comprehensive API list covers all the endpoints created in the Sushrusa Healthcare Platform, providing a complete reference for developers and system integrators. 