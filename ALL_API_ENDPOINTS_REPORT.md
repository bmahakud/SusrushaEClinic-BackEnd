# Sushrusa Healthcare Platform

## Complete Backend API Endpoints List (Plain List)

This document lists all backend API endpoints as a plain list, grouped by module and section, for easy copy-paste into Google Docs.

---

# 1. Authentication Module (`/api/auth/`)

## Core Authentication
- [GET] /api/auth/health/ — Health check endpoint (Auth: No)
- [POST] /api/auth/send-otp/ — Send OTP to phone number (Auth: No)
- [POST] /api/auth/verify-otp/ — Verify OTP and get JWT tokens (Auth: No)
- [POST] /api/auth/refresh/ — Refresh access token (Auth: No)
- [POST] /api/auth/logout/ — Logout and invalidate tokens (Auth: Yes)

## Profile Management
- [GET] /api/auth/profile/ — Get current user profile (Auth: Yes)
- [PUT] /api/auth/profile/ — Update user profile (Auth: Yes)
- [POST] /api/auth/change-password/ — Change user password (Auth: Yes)

## Session Management
- [GET] /api/auth/sessions/ — Get user's active sessions (Auth: Yes)
- [DELETE] /api/auth/sessions/ — Terminate specific session (Auth: Yes) 

---

# 2. Patient Management Module (`/api/admin/patients/`)

## Patient Profiles
- [GET] /api/admin/patients/ — List all patients (Auth: Yes)
- [POST] /api/admin/patients/ — Create new patient (Auth: Yes)
- [GET] /api/admin/patients/{id}/ — Get patient details (Auth: Yes)
- [PUT] /api/admin/patients/{id}/ — Update patient (Auth: Yes)
- [PATCH] /api/admin/patients/{id}/ — Partial update patient (Auth: Yes)
- [DELETE] /api/admin/patients/{id}/ — Delete patient (Auth: Yes)

## Patient Search & Analytics
- [GET] /api/admin/patients/search/ — Search patients (Auth: Yes)
- [GET] /api/admin/patients/stats/ — Patient statistics (Auth: Yes)

## Patient Medical Records
- [GET] /api/admin/patients/{patient_id}/medical-records/ — List medical records (Auth: Yes)
- [POST] /api/admin/patients/{patient_id}/medical-records/ — Create medical record (Auth: Yes)
- [GET] /api/admin/patients/{patient_id}/medical-records/{id}/ — Get medical record (Auth: Yes)
- [PUT] /api/admin/patients/{patient_id}/medical-records/{id}/ — Update medical record (Auth: Yes)
- [PATCH] /api/admin/patients/{patient_id}/medical-records/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/admin/patients/{patient_id}/medical-records/{id}/ — Delete medical record (Auth: Yes)

## Patient Documents
- [GET] /api/admin/patients/{patient_id}/documents/ — List documents (Auth: Yes)
- [POST] /api/admin/patients/{patient_id}/documents/ — Upload document (Auth: Yes)
- [GET] /api/admin/patients/{patient_id}/documents/{id}/ — Get document (Auth: Yes)
- [PUT] /api/admin/patients/{patient_id}/documents/{id}/ — Update document (Auth: Yes)
- [PATCH] /api/admin/patients/{patient_id}/documents/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/admin/patients/{patient_id}/documents/{id}/ — Delete document (Auth: Yes)

## Patient Notes
- [GET] /api/admin/patients/{patient_id}/notes/ — List notes (Auth: Yes)
- [POST] /api/admin/patients/{patient_id}/notes/ — Create note (Auth: Yes)
- [GET] /api/admin/patients/{patient_id}/notes/{id}/ — Get note (Auth: Yes)
- [PUT] /api/admin/patients/{patient_id}/notes/{id}/ — Update note (Auth: Yes)
- [PATCH] /api/admin/patients/{patient_id}/notes/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/admin/patients/{patient_id}/notes/{id}/ — Delete note (Auth: Yes)

---

# 3. Doctor Management Module (`/api/admin/doctors/`)

## Doctor Profiles
- [GET] /api/admin/doctors/ — List all doctors (Auth: Yes)
- [POST] /api/admin/doctors/ — Create new doctor (Auth: Yes)
- [GET] /api/admin/doctors/{id}/ — Get doctor details (Auth: Yes)
- [PUT] /api/admin/doctors/{id}/ — Update doctor (Auth: Yes)
- [PATCH] /api/admin/doctors/{id}/ — Partial update doctor (Auth: Yes)
- [DELETE] /api/admin/doctors/{id}/ — Delete doctor (Auth: Yes)

## Doctor Search & Analytics
- [GET] /api/admin/doctors/search/ — Search doctors (Auth: Yes)
- [GET] /api/admin/doctors/stats/ — Doctor statistics (Auth: Yes)

## Doctor Education
- [GET] /api/admin/doctors/{doctor_id}/education/ — List education records (Auth: Yes)
- [POST] /api/admin/doctors/{doctor_id}/education/ — Add education record (Auth: Yes)
- [GET] /api/admin/doctors/{doctor_id}/education/{id}/ — Get education record (Auth: Yes)
- [PUT] /api/admin/doctors/{doctor_id}/education/{id}/ — Update education (Auth: Yes)
- [PATCH] /api/admin/doctors/{doctor_id}/education/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/admin/doctors/{doctor_id}/education/{id}/ — Delete education (Auth: Yes)

## Doctor Experience
- [GET] /api/admin/doctors/{doctor_id}/experience/ — List experience records (Auth: Yes)
- [POST] /api/admin/doctors/{doctor_id}/experience/ — Add experience record (Auth: Yes)
- [GET] /api/admin/doctors/{doctor_id}/experience/{id}/ — Get experience record (Auth: Yes)
- [PUT] /api/admin/doctors/{doctor_id}/experience/{id}/ — Update experience (Auth: Yes)
- [PATCH] /api/admin/doctors/{doctor_id}/experience/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/admin/doctors/{doctor_id}/experience/{id}/ — Delete experience (Auth: Yes)

## Doctor Documents
- [GET] /api/admin/doctors/{doctor_id}/documents/ — List documents (Auth: Yes)
- [POST] /api/admin/doctors/{doctor_id}/documents/ — Upload document (Auth: Yes)
- [GET] /api/admin/doctors/{doctor_id}/documents/{id}/ — Get document (Auth: Yes)
- [PUT] /api/admin/doctors/{doctor_id}/documents/{id}/ — Update document (Auth: Yes)
- [PATCH] /api/admin/doctors/{doctor_id}/documents/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/admin/doctors/{doctor_id}/documents/{id}/ — Delete document (Auth: Yes)

## Doctor Availability
- [GET] /api/admin/doctors/{doctor_id}/availability/ — List availability (Auth: Yes)
- [POST] /api/admin/doctors/{doctor_id}/availability/ — Set availability (Auth: Yes)
- [GET] /api/admin/doctors/{doctor_id}/availability/{id}/ — Get availability (Auth: Yes)
- [PUT] /api/admin/doctors/{doctor_id}/availability/{id}/ — Update availability (Auth: Yes)
- [PATCH] /api/admin/doctors/{doctor_id}/availability/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/admin/doctors/{doctor_id}/availability/{id}/ — Delete availability (Auth: Yes)

## Doctor Schedule
- [GET] /api/admin/doctors/{doctor_id}/schedule/ — List schedule (Auth: Yes)
- [POST] /api/admin/doctors/{doctor_id}/schedule/ — Set schedule (Auth: Yes)
- [GET] /api/admin/doctors/{doctor_id}/schedule/{id}/ — Get schedule (Auth: Yes)
- [PUT] /api/admin/doctors/{doctor_id}/schedule/{id}/ — Update schedule (Auth: Yes)
- [PATCH] /api/admin/doctors/{doctor_id}/schedule/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/admin/doctors/{doctor_id}/schedule/{id}/ — Delete schedule (Auth: Yes)

## Doctor Reviews
- [GET] /api/admin/doctors/{doctor_id}/reviews/ — List reviews (Auth: Yes)
- [POST] /api/admin/doctors/{doctor_id}/reviews/ — Add review (Auth: Yes)
- [GET] /api/admin/doctors/{doctor_id}/reviews/{id}/ — Get review (Auth: Yes)
- [PUT] /api/admin/doctors/{doctor_id}/reviews/{id}/ — Update review (Auth: Yes)
- [PATCH] /api/admin/doctors/{doctor_id}/reviews/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/admin/doctors/{doctor_id}/reviews/{id}/ — Delete review (Auth: Yes)

---

# 4. Consultation Management Module (`/api/consultations/`)

## Consultations
- [GET] /api/consultations/ — List consultations (Auth: Yes)
- [POST] /api/consultations/ — Create consultation (Auth: Yes)
- [GET] /api/consultations/{id}/ — Get consultation (Auth: Yes)
- [PUT] /api/consultations/{id}/ — Update consultation (Auth: Yes)
- [PATCH] /api/consultations/{id}/ — Partial update consultation (Auth: Yes)
- [DELETE] /api/consultations/{id}/ — Delete consultation (Auth: Yes)

## Consultation Search & Analytics
- [GET] /api/consultations/search/ — Search consultations (Auth: Yes)
- [GET] /api/consultations/stats/ — Consultation statistics (Auth: Yes)

## Consultation Diagnosis
- [GET] /api/consultations/{consultation_id}/diagnosis/ — List diagnoses (Auth: Yes)
- [POST] /api/consultations/{consultation_id}/diagnosis/ — Add diagnosis (Auth: Yes)
- [GET] /api/consultations/{consultation_id}/diagnosis/{id}/ — Get diagnosis (Auth: Yes)
- [PUT] /api/consultations/{consultation_id}/diagnosis/{id}/ — Update diagnosis (Auth: Yes)
- [PATCH] /api/consultations/{consultation_id}/diagnosis/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/consultations/{consultation_id}/diagnosis/{id}/ — Delete diagnosis (Auth: Yes)

## Consultation Vital Signs
- [GET] /api/consultations/{consultation_id}/vital-signs/ — List vital signs (Auth: Yes)
- [POST] /api/consultations/{consultation_id}/vital-signs/ — Record vital signs (Auth: Yes)
- [GET] /api/consultations/{consultation_id}/vital-signs/{id}/ — Get vital signs (Auth: Yes)
- [PUT] /api/consultations/{consultation_id}/vital-signs/{id}/ — Update vital signs (Auth: Yes)
- [PATCH] /api/consultations/{consultation_id}/vital-signs/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/consultations/{consultation_id}/vital-signs/{id}/ — Delete vital signs (Auth: Yes)

## Consultation Documents
- [GET] /api/consultations/{consultation_id}/documents/ — List documents (Auth: Yes)
- [POST] /api/consultations/{consultation_id}/documents/ — Upload document (Auth: Yes)
- [GET] /api/consultations/{consultation_id}/documents/{id}/ — Get document (Auth: Yes)
- [PUT] /api/consultations/{consultation_id}/documents/{id}/ — Update document (Auth: Yes)
- [PATCH] /api/consultations/{consultation_id}/documents/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/consultations/{consultation_id}/documents/{id}/ — Delete document (Auth: Yes)

## Consultation Notes
- [GET] /api/consultations/{consultation_id}/notes/ — List notes (Auth: Yes)
- [POST] /api/consultations/{consultation_id}/notes/ — Add note (Auth: Yes)
- [GET] /api/consultations/{consultation_id}/notes/{id}/ — Get note (Auth: Yes)
- [PUT] /api/consultations/{consultation_id}/notes/{id}/ — Update note (Auth: Yes)
- [PATCH] /api/consultations/{consultation_id}/notes/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/consultations/{consultation_id}/notes/{id}/ — Delete note (Auth: Yes)

## Consultation Symptoms
- [GET] /api/consultations/{consultation_id}/symptoms/ — List symptoms (Auth: Yes)
- [POST] /api/consultations/{consultation_id}/symptoms/ — Add symptom (Auth: Yes)
- [GET] /api/consultations/{consultation_id}/symptoms/{id}/ — Get symptom (Auth: Yes)
- [PUT] /api/consultations/{consultation_id}/symptoms/{id}/ — Update symptom (Auth: Yes)
- [PATCH] /api/consultations/{consultation_id}/symptoms/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/consultations/{consultation_id}/symptoms/{id}/ — Delete symptom (Auth: Yes)

---

# 5. Prescription Management Module (`/api/prescriptions/`)

## Prescriptions
- [GET] /api/prescriptions/ — List prescriptions (Auth: Yes)
- [POST] /api/prescriptions/ — Create prescription (Auth: Yes)
- [GET] /api/prescriptions/{id}/ — Get prescription (Auth: Yes)
- [PUT] /api/prescriptions/{id}/ — Update prescription (Auth: Yes)
- [PATCH] /api/prescriptions/{id}/ — Partial update prescription (Auth: Yes)
- [DELETE] /api/prescriptions/{id}/ — Delete prescription (Auth: Yes)

## Prescription Search & Analytics
- [GET] /api/prescriptions/search/ — Search prescriptions (Auth: Yes)
- [GET] /api/prescriptions/stats/ — Prescription statistics (Auth: Yes)
- [GET] /api/prescriptions/medications/ — List all medications (Auth: Yes)

## Prescription Medications
- [GET] /api/prescriptions/{prescription_id}/medications/ — List medications (Auth: Yes)
- [POST] /api/prescriptions/{prescription_id}/medications/ — Add medication (Auth: Yes)
- [GET] /api/prescriptions/{prescription_id}/medications/{id}/ — Get medication (Auth: Yes)
- [PUT] /api/prescriptions/{prescription_id}/medications/{id}/ — Update medication (Auth: Yes)
- [PATCH] /api/prescriptions/{prescription_id}/medications/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/prescriptions/{prescription_id}/medications/{id}/ — Delete medication (Auth: Yes)

## Prescription Documents
- [GET] /api/prescriptions/{prescription_id}/documents/ — List documents (Auth: Yes)
- [POST] /api/prescriptions/{prescription_id}/documents/ — Upload document (Auth: Yes)
- [GET] /api/prescriptions/{prescription_id}/documents/{id}/ — Get document (Auth: Yes)
- [PUT] /api/prescriptions/{prescription_id}/documents/{id}/ — Update document (Auth: Yes)
- [PATCH] /api/prescriptions/{prescription_id}/documents/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/prescriptions/{prescription_id}/documents/{id}/ — Delete document (Auth: Yes)

## Prescription Notes
- [GET] /api/prescriptions/{prescription_id}/notes/ — List notes (Auth: Yes)
- [POST] /api/prescriptions/{prescription_id}/notes/ — Add note (Auth: Yes)
- [GET] /api/prescriptions/{prescription_id}/notes/{id}/ — Get note (Auth: Yes)
- [PUT] /api/prescriptions/{prescription_id}/notes/{id}/ — Update note (Auth: Yes)
- [PATCH] /api/prescriptions/{prescription_id}/notes/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/prescriptions/{prescription_id}/notes/{id}/ — Delete note (Auth: Yes)

## Medication Reminders
- [GET] /api/prescriptions/reminders/ — List reminders (Auth: Yes)
- [POST] /api/prescriptions/reminders/ — Create reminder (Auth: Yes)
- [GET] /api/prescriptions/reminders/{id}/ — Get reminder (Auth: Yes)
- [PUT] /api/prescriptions/reminders/{id}/ — Update reminder (Auth: Yes)
- [PATCH] /api/prescriptions/reminders/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/prescriptions/reminders/{id}/ — Delete reminder (Auth: Yes)

---

# 6. Payment Processing Module (`/api/payments/`)

## Payments
- [GET] /api/payments/ — List payments (Auth: Yes)
- [POST] /api/payments/ — Create payment (Auth: Yes)
- [GET] /api/payments/{id}/ — Get payment (Auth: Yes)
- [PUT] /api/payments/{id}/ — Update payment (Auth: Yes)
- [PATCH] /api/payments/{id}/ — Partial update payment (Auth: Yes)
- [DELETE] /api/payments/{id}/ — Delete payment (Auth: Yes)

## Payment Methods
- [GET] /api/payments/methods/ — List payment methods (Auth: Yes)
- [POST] /api/payments/methods/ — Add payment method (Auth: Yes)
- [GET] /api/payments/methods/{id}/ — Get payment method (Auth: Yes)
- [PUT] /api/payments/methods/{id}/ — Update payment method (Auth: Yes)
- [PATCH] /api/payments/methods/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/payments/methods/{id}/ — Delete payment method (Auth: Yes)

## Payment Refunds
- [GET] /api/payments/refunds/ — List refunds (Auth: Yes)
- [POST] /api/payments/refunds/ — Create refund (Auth: Yes)
- [GET] /api/payments/refunds/{id}/ — Get refund (Auth: Yes)
- [PUT] /api/payments/refunds/{id}/ — Update refund (Auth: Yes)
- [PATCH] /api/payments/refunds/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/payments/refunds/{id}/ — Delete refund (Auth: Yes)

## Payment Discounts
- [GET] /api/payments/discounts/ — List discounts (Auth: Yes)
- [POST] /api/payments/discounts/ — Create discount (Auth: Yes)
- [GET] /api/payments/discounts/{id}/ — Get discount (Auth: Yes)
- [PUT] /api/payments/discounts/{id}/ — Update discount (Auth: Yes)
- [PATCH] /api/payments/discounts/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/payments/discounts/{id}/ — Delete discount (Auth: Yes)

## Payment Utilities
- [GET] /api/payments/search/ — Search payments (Auth: Yes)
- [GET] /api/payments/stats/ — Payment statistics (Auth: Yes)
- [POST] /api/payments/validate-discount/ — Validate discount code (Auth: No)
- [POST] /api/payments/webhook/ — Payment webhook (Auth: No)

---

# 7. E-Clinic Management Module (`/api/eclinic/`)

## Clinics
- [GET] /api/eclinic/ — List clinics (Auth: Yes)
- [POST] /api/eclinic/ — Create clinic (Auth: Yes)
- [GET] /api/eclinic/{id}/ — Get clinic (Auth: Yes)
- [PUT] /api/eclinic/{id}/ — Update clinic (Auth: Yes)
- [PATCH] /api/eclinic/{id}/ — Partial update clinic (Auth: Yes)
- [DELETE] /api/eclinic/{id}/ — Delete clinic (Auth: Yes)

## Clinic Search & Analytics
- [GET] /api/eclinic/search/ — Search clinics (Auth: Yes)
- [GET] /api/eclinic/stats/ — Clinic statistics (Auth: Yes)
- [GET] /api/eclinic/nearby/ — Find nearby clinics (Auth: Yes)

## Clinic Doctors
- [GET] /api/eclinic/{clinic_id}/doctors/ — List clinic doctors (Auth: Yes)
- [POST] /api/eclinic/{clinic_id}/doctors/ — Add doctor to clinic (Auth: Yes)
- [GET] /api/eclinic/{clinic_id}/doctors/{id}/ — Get clinic doctor (Auth: Yes)
- [PUT] /api/eclinic/{clinic_id}/doctors/{id}/ — Update clinic doctor (Auth: Yes)
- [PATCH] /api/eclinic/{clinic_id}/doctors/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/eclinic/{clinic_id}/doctors/{id}/ — Remove doctor (Auth: Yes)

## Clinic Services
- [GET] /api/eclinic/{clinic_id}/services/ — List services (Auth: Yes)
- [POST] /api/eclinic/{clinic_id}/services/ — Add service (Auth: Yes)
- [GET] /api/eclinic/{clinic_id}/services/{id}/ — Get service (Auth: Yes)
- [PUT] /api/eclinic/{clinic_id}/services/{id}/ — Update service (Auth: Yes)
- [PATCH] /api/eclinic/{clinic_id}/services/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/eclinic/{clinic_id}/services/{id}/ — Delete service (Auth: Yes)

## Clinic Inventory
- [GET] /api/eclinic/{clinic_id}/inventory/ — List inventory (Auth: Yes)
- [POST] /api/eclinic/{clinic_id}/inventory/ — Add inventory item (Auth: Yes)
- [GET] /api/eclinic/{clinic_id}/inventory/{id}/ — Get inventory item (Auth: Yes)
- [PUT] /api/eclinic/{clinic_id}/inventory/{id}/ — Update inventory (Auth: Yes)
- [PATCH] /api/eclinic/{clinic_id}/inventory/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/eclinic/{clinic_id}/inventory/{id}/ — Delete inventory (Auth: Yes)

## Clinic Appointments
- [GET] /api/eclinic/{clinic_id}/appointments/ — List appointments (Auth: Yes)
- [POST] /api/eclinic/{clinic_id}/appointments/ — Create appointment (Auth: Yes)
- [GET] /api/eclinic/{clinic_id}/appointments/{id}/ — Get appointment (Auth: Yes)
- [PUT] /api/eclinic/{clinic_id}/appointments/{id}/ — Update appointment (Auth: Yes)
- [PATCH] /api/eclinic/{clinic_id}/appointments/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/eclinic/{clinic_id}/appointments/{id}/ — Delete appointment (Auth: Yes)

## Clinic Reviews
- [GET] /api/eclinic/{clinic_id}/reviews/ — List reviews (Auth: Yes)
- [POST] /api/eclinic/{clinic_id}/reviews/ — Add review (Auth: Yes)
- [GET] /api/eclinic/{clinic_id}/reviews/{id}/ — Get review (Auth: Yes)
- [PUT] /api/eclinic/{clinic_id}/reviews/{id}/ — Update review (Auth: Yes)
- [PATCH] /api/eclinic/{clinic_id}/reviews/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/eclinic/{clinic_id}/reviews/{id}/ — Delete review (Auth: Yes)

## Clinic Documents
- [GET] /api/eclinic/{clinic_id}/documents/ — List documents (Auth: Yes)
- [POST] /api/eclinic/{clinic_id}/documents/ — Upload document (Auth: Yes)
- [GET] /api/eclinic/{clinic_id}/documents/{id}/ — Get document (Auth: Yes)
- [PUT] /api/eclinic/{clinic_id}/documents/{id}/ — Update document (Auth: Yes)
- [PATCH] /api/eclinic/{clinic_id}/documents/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/eclinic/{clinic_id}/documents/{id}/ — Delete document (Auth: Yes)

---

# 8. Analytics Module (`/api/analytics/`)

## Dashboard & Overview
- [GET] /api/analytics/dashboard/ — Main dashboard stats (Auth: Yes)
- [GET] /api/analytics/real-time/ — Real-time metrics (Auth: Yes)

## Specific Analytics
- [GET] /api/analytics/user-growth/ — User growth analytics (Auth: Yes)
- [GET] /api/analytics/consultations/ — Consultation analytics (Auth: Yes)
- [GET] /api/analytics/revenue-report/ — Revenue reporting (Auth: Yes)
- [GET] /api/analytics/geographic/ — Geographic analytics (Auth: Yes)

## Custom Reports & Exports
- [GET] /api/analytics/custom-report/ — Generate custom report (Auth: Yes)
- [GET] /api/analytics/export/ — Export data (Auth: Yes)

## User Analytics
- [GET] /api/analytics/user-analytics/ — List user analytics (Auth: Yes)
- [POST] /api/analytics/user-analytics/ — Create user analytics (Auth: Yes)
- [GET] /api/analytics/user-analytics/{id}/ — Get user analytics (Auth: Yes)
- [PUT] /api/analytics/user-analytics/{id}/ — Update user analytics (Auth: Yes)
- [PATCH] /api/analytics/user-analytics/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/analytics/user-analytics/{id}/ — Delete user analytics (Auth: Yes)

## Revenue Analytics
- [GET] /api/analytics/revenue-analytics/ — List revenue analytics (Auth: Yes)
- [POST] /api/analytics/revenue-analytics/ — Create revenue analytics (Auth: Yes)
- [GET] /api/analytics/revenue-analytics/{id}/ — Get revenue analytics (Auth: Yes)
- [PUT] /api/analytics/revenue-analytics/{id}/ — Update revenue analytics (Auth: Yes)
- [PATCH] /api/analytics/revenue-analytics/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/analytics/revenue-analytics/{id}/ — Delete revenue analytics (Auth: Yes)

## Doctor Performance Analytics
- [GET] /api/analytics/doctor-performance/ — List doctor performance (Auth: Yes)
- [POST] /api/analytics/doctor-performance/ — Create performance record (Auth: Yes)
- [GET] /api/analytics/doctor-performance/{id}/ — Get performance record (Auth: Yes)
- [PUT] /api/analytics/doctor-performance/{id}/ — Update performance (Auth: Yes)
- [PATCH] /api/analytics/doctor-performance/{id}/ — Partial update (Auth: Yes)
- [DELETE] /api/analytics/doctor-performance/{id}/ — Delete performance (Auth: Yes)

---

# 9. API Documentation

- [GET] /api/schema/ — OpenAPI schema (Auth: No)
- [GET] /api/docs/ — Swagger UI documentation (Auth: No)
- [GET] /api/redoc/ — ReDoc documentation (Auth: No)

---

# 10. Admin Interface

- [GET] /admin/ — Django admin interface (Auth: Yes, Superuser)

--- 