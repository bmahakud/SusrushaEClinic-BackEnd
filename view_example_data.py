#!/usr/bin/env python3
"""
Script to view and test the example consultations and prescriptions
"""
import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from patients.models import PatientProfile
from doctors.models import DoctorProfile
from consultations.models import Consultation
from prescriptions.models import Prescription, PrescriptionMedication, PrescriptionVitalSigns

User = get_user_model()

def view_example_data():
    """View the created example data"""
    print("🔍 Viewing Example Data")
    print("=" * 60)
    
    # Get the example users
    try:
        doctor = User.objects.get(phone='+916666666661')
        patient = User.objects.get(phone='+916666666662')
        
        print(f"👨‍⚕️ Doctor: {doctor.name} (ID: {doctor.id})")
        print(f"   Phone: {doctor.phone}")
        print(f"   Email: {doctor.email}")
        print(f"   Role: {doctor.role}")
        
        print(f"\n👤 Patient: {patient.name} (ID: {patient.id})")
        print(f"   Phone: {patient.phone}")
        print(f"   Email: {patient.email}")
        print(f"   Role: {patient.role}")
        
        # Get doctor profile
        try:
            doctor_profile = DoctorProfile.objects.get(user=doctor)
            print(f"\n📋 Doctor Profile:")
            print(f"   License: {doctor_profile.license_number}")
            print(f"   Specialization: {doctor_profile.specialization}")
            print(f"   Qualification: {doctor_profile.qualification}")
            print(f"   Experience: {doctor_profile.experience_years} years")
            print(f"   Consultation Fee: ₹{doctor_profile.consultation_fee}")
        except DoctorProfile.DoesNotExist:
            print("❌ Doctor profile not found")
        
        # Get patient profile
        try:
            patient_profile = PatientProfile.objects.get(user=patient)
            print(f"\n📋 Patient Profile:")
            print(f"   Blood Group: {patient_profile.blood_group}")
            print(f"   Allergies: {patient_profile.allergies}")
            print(f"   Chronic Conditions: {patient_profile.chronic_conditions}")
            print(f"   Current Medications: {patient_profile.current_medications}")
        except PatientProfile.DoesNotExist:
            print("❌ Patient profile not found")
        
        # Get consultations
        consultations = Consultation.objects.filter(
            patient=patient,
            doctor=doctor
        ).order_by('-scheduled_date')
        
        print(f"\n📅 Consultations ({consultations.count()}):")
        for i, consultation in enumerate(consultations, 1):
            print(f"   {i}. {consultation.id} - {consultation.chief_complaint}")
            print(f"      Date: {consultation.scheduled_date}")
            print(f"      Time: {consultation.scheduled_time}")
            print(f"      Status: {consultation.status}")
            print(f"      Fee: ₹{consultation.consultation_fee}")
            print(f"      Type: {consultation.consultation_type}")
        
        # Get prescriptions
        prescriptions = Prescription.objects.filter(
            patient=patient,
            doctor=doctor
        ).order_by('-issued_date')
        
        print(f"\n💊 Prescriptions ({prescriptions.count()}):")
        for i, prescription in enumerate(prescriptions, 1):
            print(f"   {i}. {prescription.id} - {prescription.primary_diagnosis}")
            print(f"      Date: {prescription.issued_date}")
            print(f"      Status: {'Finalized' if prescription.is_finalized else 'Draft'}")
            print(f"      Consultation: {prescription.consultation.id}")
            
            # Get medications
            medications = PrescriptionMedication.objects.filter(prescription=prescription)
            print(f"      Medications: {medications.count()}")
            for med in medications:
                print(f"        - {med.medicine_name} ({med.dosage_form})")
            
            # Get vital signs
            try:
                vital_signs = PrescriptionVitalSigns.objects.get(prescription=prescription)
                print(f"      Vital Signs: BP {vital_signs.blood_pressure_systolic}/{vital_signs.blood_pressure_diastolic}, Pulse: {vital_signs.pulse}")
            except PrescriptionVitalSigns.DoesNotExist:
                print(f"      Vital Signs: Not recorded")
        
        return doctor, patient
        
    except User.DoesNotExist as e:
        print(f"❌ User not found: {e}")
        return None, None

def test_api_endpoints(doctor, patient):
    """Test the API endpoints"""
    print(f"\n🌐 Testing API Endpoints")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test endpoints
    endpoints = [
        f"/api/prescriptions/",
        f"/api/prescriptions/?doctor={doctor.id}",
        f"/api/prescriptions/?patient={patient.id}",
        f"/api/prescriptions/drafts/",
        f"/api/prescriptions/finalized/",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"✅ {endpoint}")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'results' in data['data']:
                    count = len(data['data']['results'])
                    print(f"   Results: {count} prescriptions")
                elif 'results' in data:
                    count = len(data['results'])
                    print(f"   Results: {count} prescriptions")
                else:
                    print(f"   Response: {type(data)}")
            else:
                print(f"   Error: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ {endpoint}")
            print(f"   Error: {e}")
        print()

def show_viewing_instructions():
    """Show instructions for viewing the data"""
    print(f"\n📖 How to View the Data")
    print("=" * 60)
    
    print("1. 🖥️  Django Admin Interface:")
    print("   URL: http://127.0.0.1:8000/admin/")
    print("   Login with your admin credentials")
    print("   Navigate to: Consultations > Consultations")
    print("   Navigate to: Prescriptions > Prescriptions")
    
    print("\n2. 🌐 API Endpoints (if server is running):")
    print("   All prescriptions: http://127.0.0.1:8000/api/prescriptions/")
    print("   Doctor's prescriptions: http://127.0.0.1:8000/api/prescriptions/?doctor=DOC031")
    print("   Patient's prescriptions: http://127.0.0.1:8000/api/prescriptions/?patient=PAT035")
    print("   Draft prescriptions: http://127.0.0.1:8000/api/prescriptions/drafts/")
    print("   Finalized prescriptions: http://127.0.0.1:8000/api/prescriptions/finalized/")
    
    print("\n3. 🎨 Frontend Interface:")
    print("   URL: http://localhost:8080/prescriptions")
    print("   Login as doctor with phone: +916666666661")
    print("   Navigate to prescription management")
    
    print("\n4. 📊 Database Direct Query:")
    print("   Use Django shell: python manage.py shell")
    print("   Or use your database client to view tables:")
    print("   - consultations")
    print("   - prescriptions")
    print("   - prescription_medications")
    print("   - prescription_vital_signs")

def main():
    """Main function"""
    print("🔍 Example Data Viewer")
    print("=" * 60)
    
    # View the data
    doctor, patient = view_example_data()
    
    if doctor and patient:
        # Test API endpoints
        test_api_endpoints(doctor, patient)
        
        # Show viewing instructions
        show_viewing_instructions()
        
        print(f"\n✅ Data viewing complete!")
        print(f"📋 Summary:")
        print(f"   - Doctor: {doctor.name} ({doctor.id})")
        print(f"   - Patient: {patient.name} ({patient.id})")
        print(f"   - Consultations: {Consultation.objects.filter(patient=patient, doctor=doctor).count()}")
        print(f"   - Prescriptions: {Prescription.objects.filter(patient=patient, doctor=doctor).count()}")
    else:
        print("❌ Could not find example data. Please run create_example_data.py first.")

if __name__ == "__main__":
    main() 