#!/usr/bin/env python3
"""
Script to create example consultations and prescriptions for testing
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from patients.models import PatientProfile
from doctors.models import DoctorProfile
from consultations.models import Consultation
from prescriptions.models import Prescription, PrescriptionMedication, PrescriptionVitalSigns

User = get_user_model()

def create_example_users():
    """Create example users for testing"""
    print("Creating example users...")
    
    # Try to get existing users first, or create new ones
    try:
        doctor_user = User.objects.get(phone='6666666661')
        print(f"📋 Using existing doctor: {doctor_user.name}")
    except User.DoesNotExist:
        doctor_user = User.objects.create(
            phone='6666666661',
            name='Dr. Sarah Johnson',
            email='sarah.johnson@example.com',
            role='doctor'
        )
        print(f"✅ Created doctor: {doctor_user.name}")
    
    try:
        patient_user = User.objects.get(phone='6666666662')
        print(f"📋 Using existing patient: {patient_user.name}")
    except User.DoesNotExist:
        patient_user = User.objects.create(
            phone='6666666662',
            name='John Smith',
            email='john.smith@example.com',
            role='patient'
        )
        print(f"✅ Created patient: {patient_user.name}")
    
    return doctor_user, patient_user

def create_example_profiles(doctor_user, patient_user):
    """Create doctor and patient profiles"""
    print("Creating profiles...")
    
    # Create doctor profile
    doctor_profile, created = DoctorProfile.objects.get_or_create(
        user=doctor_user,
        defaults={
            'license_number': 'DOC777777',
            'qualification': 'MBBS, MD - Internal Medicine',
            'specialization': 'Internal Medicine',
            'sub_specialization': 'Cardiology',
            'consultation_fee': 1500,
            'online_consultation_fee': 1200,
            'languages_spoken': ['English', 'Hindi'],
            'bio': 'Experienced cardiologist with 15+ years of practice',
            'experience_years': 15,
            'is_verified': True,
            'is_active': True,
            'is_accepting_patients': True,
            'rating': 4.8,
            'total_reviews': 127
        }
    )
    
    if created:
        print(f"✅ Created doctor profile for: {doctor_user.name}")
    else:
        print(f"📋 Using existing doctor profile for: {doctor_user.name}")
    
    # Create patient profile
    patient_profile, created = PatientProfile.objects.get_or_create(
        user=patient_user,
        defaults={
            'blood_group': 'O+',
            'allergies': 'Penicillin, Dust',
            'chronic_conditions': ['Hypertension', 'Diabetes Type 2'],
            'current_medications': ['Metformin 500mg', 'Amlodipine 5mg'],
            'insurance_provider': 'HealthFirst Insurance',
            'insurance_policy_number': 'HF123456789',
            'insurance_expiry': '2025-12-31',
            'preferred_language': 'English',
            'notification_preferences': {
                'sms': True,
                'email': True,
                'push': False
            },
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Created patient profile for: {patient_user.name}")
    else:
        print(f"📋 Using existing patient profile for: {patient_user.name}")
    
    return doctor_profile, patient_profile

def create_example_consultations(doctor_profile, patient_profile):
    """Create example consultations"""
    print("Creating example consultations...")
    
    consultations = []
    
    # Get the next consultation number
    last_consultation = Consultation.objects.order_by('id').last()
    if last_consultation:
        try:
            # Try to extract number from existing ID
            if last_consultation.id.startswith('CON'):
                last_number = int(last_consultation.id[3:])
            else:
                last_number = 0
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0
    
    # Consultation 1: Recent consultation
    consultation1_id = f"CON{last_number + 1:03d}"
    consultation1, created = Consultation.objects.get_or_create(
        id=consultation1_id,
        defaults={
            'patient': patient_profile.user,
            'doctor': doctor_profile.user,
            'scheduled_date': timezone.now().date() - timedelta(days=2),
            'consultation_type': 'video',
            'scheduled_time': '10:00:00',
            'duration': 30,
            'status': 'completed',
            'payment_status': 'paid',
            'consultation_fee': 1500,
            'is_paid': True,
            'chief_complaint': 'Chest pain and shortness of breath',
            'symptoms': 'Chest pain for 3 days, shortness of breath, fatigue',
            'doctor_notes': 'Patient reports chest pain radiating to left arm. ECG shows ST elevation.',
            'actual_start_time': timezone.now() - timedelta(days=2, hours=2),
            'actual_end_time': timezone.now() - timedelta(days=2, hours=1, minutes=30),
            'is_follow_up': False
        }
    )
    
    if created:
        print(f"✅ Created consultation 1: {consultation1.chief_complaint}")
    else:
        print(f"📋 Using existing consultation 1: {consultation1.chief_complaint}")
    
    consultations.append(consultation1)
    
    # Consultation 2: Follow-up consultation
    consultation2_id = f"CON{last_number + 2:03d}"
    consultation2, created = Consultation.objects.get_or_create(
        id=consultation2_id,
        defaults={
            'patient': patient_profile.user,
            'doctor': doctor_profile.user,
            'scheduled_date': timezone.now().date() - timedelta(days=1),
            'consultation_type': 'video',
            'scheduled_time': '14:00:00',
            'duration': 20,
            'status': 'completed',
            'payment_status': 'paid',
            'consultation_fee': 1200,
            'is_paid': True,
            'chief_complaint': 'Follow-up for chest pain management',
            'symptoms': 'Chest pain improved, still some discomfort',
            'doctor_notes': 'Patient reports improvement in symptoms. Blood pressure controlled.',
            'actual_start_time': timezone.now() - timedelta(days=1, hours=2),
            'actual_end_time': timezone.now() - timedelta(days=1, hours=1, minutes=40),
            'is_follow_up': True,
            'parent_consultation': consultation1
        }
    )
    
    if created:
        print(f"✅ Created consultation 2: {consultation2.chief_complaint}")
    else:
        print(f"📋 Using existing consultation 2: {consultation2.chief_complaint}")
    
    consultations.append(consultation2)
    
    # Consultation 3: Upcoming consultation
    consultation3_id = f"CON{last_number + 3:03d}"
    consultation3, created = Consultation.objects.get_or_create(
        id=consultation3_id,
        defaults={
            'patient': patient_profile.user,
            'doctor': doctor_profile.user,
            'scheduled_date': timezone.now().date() + timedelta(days=7),
            'consultation_type': 'video',
            'scheduled_time': '11:00:00',
            'duration': 30,
            'status': 'scheduled',
            'payment_status': 'pending',
            'consultation_fee': 1500,
            'is_paid': False,
            'chief_complaint': 'Routine check-up and medication review',
            'symptoms': 'No new symptoms, routine follow-up',
            'is_follow_up': True,
            'parent_consultation': consultation1
        }
    )
    
    if created:
        print(f"✅ Created consultation 3: {consultation3.chief_complaint}")
    else:
        print(f"📋 Using existing consultation 3: {consultation3.chief_complaint}")
    
    consultations.append(consultation3)
    
    return consultations

def create_example_prescriptions(consultations):
    """Create example prescriptions"""
    print("Creating example prescriptions...")
    
    prescriptions = []
    
    # Prescription 1: For first consultation (finalized)
    prescription1, created = Prescription.objects.get_or_create(
        consultation=consultations[0],
        defaults={
            'patient': consultations[0].patient,
            'doctor': consultations[0].doctor,
            'issued_date': consultations[0].scheduled_date,
            'issued_time': consultations[0].scheduled_time,
            'primary_diagnosis': 'Acute Coronary Syndrome',
            'secondary_diagnosis': 'Hypertension, Diabetes Type 2',
            'clinical_classification': 'Cardiovascular',
            'general_instructions': 'Take medications as prescribed. Monitor blood pressure daily. Avoid strenuous activities for 2 weeks.',
            'fluid_intake': 'Drink 8-10 glasses of water daily',
            'diet_instructions': 'Low sodium diet. Avoid fried foods. Include fruits and vegetables.',
            'lifestyle_advice': 'Quit smoking. Regular walking for 30 minutes daily. Stress management techniques.',
            'next_visit': '2 weeks',
            'follow_up_notes': 'Schedule follow-up in 2 weeks. Monitor blood pressure and blood sugar.',
            'is_draft': False,
            'is_finalized': True
        }
    )
    
    if created:
        print(f"✅ Created prescription 1: {prescription1.primary_diagnosis}")
    else:
        print(f"📋 Using existing prescription 1: {prescription1.primary_diagnosis}")
    
    # Add vital signs
    vital_signs1, created = PrescriptionVitalSigns.objects.get_or_create(
        prescription=prescription1,
        defaults={
            'pulse': 85,
            'blood_pressure_systolic': 140,
            'blood_pressure_diastolic': 90,
            'temperature': 98.6,
            'weight': 75,
            'height': 170,
            'oxygen_saturation': 95,
            'respiratory_rate': 18
        }
    )
    
    # Add medications
    medications1 = [
        {
            'medicine_name': 'Aspirin',
            'composition': 'Acetylsalicylic Acid 75mg',
            'dosage_form': 'Tablet',
            'morning_dose': 1,
            'afternoon_dose': 0,
            'evening_dose': 0,
            'frequency': 'once_daily',
            'timing': 'after_breakfast',
            'duration_days': 30,
            'is_continuous': True,
            'special_instructions': 'Take with food to avoid stomach upset',
            'notes': 'Blood thinner - avoid alcohol',
            'order': 1
        },
        {
            'medicine_name': 'Atorvastatin',
            'composition': 'Atorvastatin Calcium 20mg',
            'dosage_form': 'Tablet',
            'morning_dose': 0,
            'afternoon_dose': 0,
            'evening_dose': 1,
            'frequency': 'once_daily',
            'timing': 'bedtime',
            'duration_days': 30,
            'is_continuous': True,
            'special_instructions': 'Take at bedtime for better absorption',
            'notes': 'Cholesterol lowering medication',
            'order': 2
        },
        {
            'medicine_name': 'Metoprolol',
            'composition': 'Metoprolol Tartrate 25mg',
            'dosage_form': 'Tablet',
            'morning_dose': 1,
            'afternoon_dose': 0,
            'evening_dose': 1,
            'frequency': 'twice_daily',
            'timing': 'before_breakfast',
            'duration_days': 30,
            'is_continuous': True,
            'special_instructions': 'Take before meals',
            'notes': 'Beta blocker for blood pressure and heart rate control',
            'order': 3
        }
    ]
    
    for med_data in medications1:
        PrescriptionMedication.objects.get_or_create(
            prescription=prescription1,
            medicine_name=med_data['medicine_name'],
            defaults=med_data
        )
    
    prescriptions.append(prescription1)
    
    # Prescription 2: For second consultation (draft)
    prescription2, created = Prescription.objects.get_or_create(
        consultation=consultations[1],
        defaults={
            'patient': consultations[1].patient,
            'doctor': consultations[1].doctor,
            'issued_date': consultations[1].scheduled_date,
            'issued_time': consultations[1].scheduled_time,
            'primary_diagnosis': 'Stable Angina',
            'secondary_diagnosis': 'Hypertension, Diabetes Type 2',
            'clinical_classification': 'Cardiovascular',
            'general_instructions': 'Continue current medications. Monitor symptoms.',
            'fluid_intake': 'Maintain adequate hydration',
            'diet_instructions': 'Continue low sodium diet',
            'lifestyle_advice': 'Continue regular exercise as tolerated',
            'next_visit': '1 week',
            'follow_up_notes': 'Patient showing improvement. Continue current treatment.',
            'is_draft': True,
            'is_finalized': False
        }
    )
    
    if created:
        print(f"✅ Created prescription 2 (draft): {prescription2.primary_diagnosis}")
    else:
        print(f"📋 Using existing prescription 2: {prescription2.primary_diagnosis}")
    
    # Add vital signs for draft prescription
    vital_signs2, created = PrescriptionVitalSigns.objects.get_or_create(
        prescription=prescription2,
        defaults={
            'pulse': 78,
            'blood_pressure_systolic': 135,
            'blood_pressure_diastolic': 85,
            'temperature': 98.4,
            'weight': 74,
            'height': 170,
            'oxygen_saturation': 96,
            'respiratory_rate': 16
        }
    )
    
    prescriptions.append(prescription2)
    
    return prescriptions

def main():
    """Main function to create all example data"""
    print("🏥 Creating example consultations and prescriptions...")
    print("=" * 60)
    
    try:
        # Create users
        doctor_user, patient_user = create_example_users()
        
        # Create profiles
        doctor_profile, patient_profile = create_example_profiles(doctor_user, patient_user)
        
        # Create consultations
        consultations = create_example_consultations(doctor_profile, patient_profile)
        
        # Create prescriptions
        prescriptions = create_example_prescriptions(consultations)
        
        print("\n" + "=" * 60)
        print("✅ Example data created successfully!")
        print("\n📋 Summary:")
        print(f"   👨‍⚕️ Doctor: {doctor_user.name} (ID: {doctor_user.id})")
        print(f"   👤 Patient: {patient_user.name} (ID: {patient_user.id})")
        print(f"   📅 Consultations: {len(consultations)}")
        print(f"   💊 Prescriptions: {len(prescriptions)}")
        
        print("\n🔍 Where to view the data:")
        print("   1. Django Admin: http://127.0.0.1:8000/admin/")
        print("   2. API Endpoints:")
        print(f"      - All prescriptions: http://127.0.0.1:8000/api/prescriptions/")
        print(f"      - Doctor's prescriptions: http://127.0.0.1:8000/api/prescriptions/?doctor={doctor_user.id}")
        print(f"      - Patient's prescriptions: http://127.0.0.1:8000/api/prescriptions/?patient={patient_user.id}")
        print("   3. Frontend: http://localhost:8080/prescriptions")
        
        print("\n👨‍⚕️ Doctor Login Details:")
        print(f"   Phone: {doctor_user.phone}")
        print(f"   Name: {doctor_user.name}")
        
        print("\n👤 Patient Login Details:")
        print(f"   Phone: {patient_user.phone}")
        print(f"   Name: {patient_user.name}")
        
    except Exception as e:
        print(f"❌ Error creating example data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 