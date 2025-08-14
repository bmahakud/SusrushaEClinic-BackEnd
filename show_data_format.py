#!/usr/bin/env python3
"""
Script to show the existing data format and structure
"""
import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from consultations.models import Consultation
from prescriptions.models import Prescription, PrescriptionMedication, PrescriptionVitalSigns

User = get_user_model()

def show_data_format():
    """Show the format of existing data"""
    print("📊 Existing Data Format")
    print("=" * 60)
    
    # Show recent consultations
    consultations = Consultation.objects.order_by('-id')[:3]
    print(f"\n📅 Recent Consultations ({consultations.count()}):")
    for i, consultation in enumerate(consultations, 1):
        print(f"\n{i}. Consultation ID: {consultation.id}")
        print(f"   Patient: {consultation.patient.name} ({consultation.patient.id})")
        print(f"   Doctor: {consultation.doctor.name} ({consultation.doctor.id})")
        print(f"   Date: {consultation.scheduled_date}")
        print(f"   Time: {consultation.scheduled_time}")
        print(f"   Chief Complaint: {consultation.chief_complaint}")
        print(f"   Status: {consultation.status}")
        print(f"   Type: {consultation.consultation_type}")
        print(f"   Fee: ₹{consultation.consultation_fee}")
        print(f"   Duration: {consultation.duration} minutes")
        print(f"   Created: {consultation.created_at}")
    
    # Show recent prescriptions
    prescriptions = Prescription.objects.order_by('-id')[:3]
    print(f"\n💊 Recent Prescriptions ({prescriptions.count()}):")
    for i, prescription in enumerate(prescriptions, 1):
        print(f"\n{i}. Prescription ID: {prescription.id}")
        print(f"   Patient: {prescription.patient.name} ({prescription.patient.id})")
        print(f"   Doctor: {prescription.doctor.name} ({prescription.doctor.id})")
        print(f"   Consultation: {prescription.consultation.id if prescription.consultation else 'None'}")
        print(f"   Primary Diagnosis: {prescription.primary_diagnosis}")
        print(f"   Patient Previous History: {prescription.patient_previous_history}")
        print(f"   Clinical Classification: {prescription.clinical_classification}")
        print(f"   Status: {'Finalized' if prescription.is_finalized else 'Draft'}")
        print(f"   Issued Date: {prescription.issued_date}")
        print(f"   General Instructions: {prescription.general_instructions[:100]}...")
        print(f"   Created: {prescription.created_at}")
        
        # Show medications
        medications = PrescriptionMedication.objects.filter(prescription=prescription)
        print(f"   Medications ({medications.count()}):")
        for med in medications:
            print(f"     - {med.medicine_name} ({med.dosage_form})")
            print(f"       Composition: {med.composition}")
            print(f"       Dosage: {med.morning_dose}/{med.afternoon_dose}/{med.evening_dose}")
            print(f"       Frequency: {med.frequency}")
            print(f"       Timing: {med.timing}")
            print(f"       Duration: {med.duration_days} days")
            print(f"       Instructions: {med.special_instructions}")
        
        # Show vital signs
        try:
            vital_signs = PrescriptionVitalSigns.objects.get(prescription=prescription)
            print(f"   Vital Signs:")
            print(f"     - Blood Pressure: {vital_signs.blood_pressure_systolic}/{vital_signs.blood_pressure_diastolic}")
            print(f"     - Pulse: {vital_signs.pulse}")
            print(f"     - Temperature: {vital_signs.temperature}")
            print(f"     - Weight: {vital_signs.weight} kg")
            print(f"     - Height: {vital_signs.height} cm")
            print(f"     - Oxygen Saturation: {vital_signs.oxygen_saturation}%")
            print(f"     - Respiratory Rate: {vital_signs.respiratory_rate}")
        except PrescriptionVitalSigns.DoesNotExist:
            print(f"   Vital Signs: Not recorded")

def show_api_format():
    """Show the API response format"""
    print(f"\n🌐 API Response Format")
    print("=" * 60)
    
    # Get a sample prescription
    prescription = Prescription.objects.first()
    if prescription:
        print("Sample Prescription API Response:")
        print(json.dumps({
            "success": True,
            "data": {
                "results": [{
                    "id": prescription.id,
                    "patient": {
                        "id": prescription.patient.id,
                        "name": prescription.patient.name,
                        "phone": prescription.patient.phone
                    },
                    "doctor": {
                        "id": prescription.doctor.id,
                        "name": prescription.doctor.name
                    },
                    "consultation": {
                        "id": prescription.consultation.id if prescription.consultation else None,
                        "scheduled_date": prescription.consultation.scheduled_date.isoformat() if prescription.consultation else None,
                        "scheduled_time": prescription.consultation.scheduled_time.isoformat() if prescription.consultation else None
                    },
                    "primary_diagnosis": prescription.primary_diagnosis,
                    "patient_previous_history": prescription.patient_previous_history,
                    "issued_date": prescription.issued_date.isoformat(),
                    "issued_time": prescription.issued_time.isoformat(),
                    "is_draft": prescription.is_draft,
                    "is_finalized": prescription.is_finalized,
                    "medications": [
                        {
                            "id": med.id,
                            "medicine_name": med.medicine_name,
                            "dosage_display": f"{med.morning_dose}/{med.afternoon_dose}/{med.evening_dose}",
                            "frequency": med.frequency,
                            "duration_days": med.duration_days
                        }
                        for med in PrescriptionMedication.objects.filter(prescription=prescription)
                    ],
                    "vital_signs": {
                        "blood_pressure_systolic": getattr(PrescriptionVitalSigns.objects.filter(prescription=prescription).first(), 'blood_pressure_systolic', None),
                        "blood_pressure_diastolic": getattr(PrescriptionVitalSigns.objects.filter(prescription=prescription).first(), 'blood_pressure_diastolic', None),
                        "pulse": getattr(PrescriptionVitalSigns.objects.filter(prescription=prescription).first(), 'pulse', None),
                        "temperature": getattr(PrescriptionVitalSigns.objects.filter(prescription=prescription).first(), 'temperature', None),
                        "weight": getattr(PrescriptionVitalSigns.objects.filter(prescription=prescription).first(), 'weight', None)
                    },
                    "general_instructions": prescription.general_instructions,
                    "created_at": prescription.created_at.isoformat(),
                    "updated_at": prescription.updated_at.isoformat()
                }],
                "count": 1,
                "next": None,
                "previous": None
            },
            "message": "Prescriptions retrieved successfully",
            "timestamp": "2025-01-06T12:00:00Z"
        }, indent=2))

def show_viewing_instructions():
    """Show how to view the data"""
    print(f"\n📖 How to View the Data")
    print("=" * 60)
    
    print("1. 🖥️  Django Admin Interface:")
    print("   URL: http://127.0.0.1:8000/admin/")
    print("   Login with your admin credentials")
    print("   Navigate to: Consultations > Consultations")
    print("   Navigate to: Prescriptions > Prescriptions")
    
    print("\n2. 🌐 API Endpoints (if server is running):")
    print("   All prescriptions: http://127.0.0.1:8000/api/prescriptions/")
    print("   Draft prescriptions: http://127.0.0.1:8000/api/prescriptions/drafts/")
    print("   Finalized prescriptions: http://127.0.0.1:8000/api/prescriptions/finalized/")
    
    print("\n3. 🎨 Frontend Interface:")
    print("   URL: http://localhost:8080/prescriptions")
    print("   Login as any doctor and navigate to prescription management")
    
    print("\n4. 📊 Database Direct Query:")
    print("   Use Django shell: python manage.py shell")
    print("   Or use your database client to view tables:")
    print("   - consultations")
    print("   - prescriptions")
    print("   - prescription_medications")
    print("   - prescription_vital_signs")

def main():
    """Main function"""
    print("📊 Data Format Viewer")
    print("=" * 60)
    
    # Show data format
    show_data_format()
    
    # Show API format
    show_api_format()
    
    # Show viewing instructions
    show_viewing_instructions()
    
    print(f"\n✅ Data format viewing complete!")
    print(f"📋 Summary:")
    print(f"   - Total Consultations: {Consultation.objects.count()}")
    print(f"   - Total Prescriptions: {Prescription.objects.count()}")
    print(f"   - Total Users: {User.objects.count()}")

if __name__ == "__main__":
    main() 