#!/usr/bin/env python3
"""
Script to create consultations and prescriptions for the specific doctor
"""
import os
import sys
import django
from datetime import datetime, timedelta

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

def create_data_for_doctor():
    """Create consultations and prescriptions for the specific doctor"""
    print("🏥 Creating data for doctor 6666666661...")
    print("=" * 60)
    
    # Get the doctor
    try:
        doctor = User.objects.get(phone='+916666666661')
        print(f"✅ Found doctor: {doctor.name} ({doctor.id})")
    except User.DoesNotExist:
        print("❌ Doctor not found. Please run create_example_data.py first.")
        return
    
    # Get or create a patient
    try:
        patient = User.objects.get(phone='+916666666662')
        print(f"✅ Found patient: {patient.name} ({patient.id})")
    except User.DoesNotExist:
        print("❌ Patient not found. Please run create_example_data.py first.")
        return
    
    # Get the next consultation number
    consultations = Consultation.objects.filter(id__startswith='CON').order_by('id')
    if consultations.exists():
        last_consultation = consultations.last()
        try:
            last_number = int(last_consultation.id[3:])
        except (ValueError, IndexError):
            last_number = 0
    else:
        last_number = 0
    
    consultations = []
    
    # Create consultation 1: Recent completed consultation
    consultation1_id = f"CON{last_number + 1:03d}"
    consultation1 = Consultation.objects.create(
        id=consultation1_id,
        patient=patient,
        doctor=doctor,
        scheduled_date=timezone.now().date() - timedelta(days=2),
        consultation_type='video_call',
        scheduled_time='10:00:00',
        duration=30,
        status='completed',
        payment_status='paid',
        consultation_fee=1500,
        is_paid=True,
        chief_complaint='Chest pain and shortness of breath',
        symptoms='Chest pain for 3 days, shortness of breath, fatigue',
        doctor_notes='Patient reports chest pain radiating to left arm. ECG shows ST elevation.',
        actual_start_time=timezone.now() - timedelta(days=2, hours=2),
        actual_end_time=timezone.now() - timedelta(days=2, hours=1, minutes=30),
        is_follow_up=False
    )
    print(f"✅ Created consultation 1: {consultation1.chief_complaint}")
    
    consultations.append(consultation1)
    
    # Create consultation 2: Follow-up consultation
    consultation2_id = f"CON{last_number + 2:03d}"
    consultation2 = Consultation.objects.create(
        id=consultation2_id,
        patient=patient,
        doctor=doctor,
        scheduled_date=timezone.now().date() - timedelta(days=1),
        consultation_type='video_call',
        scheduled_time='14:00:00',
        duration=20,
        status='completed',
        payment_status='paid',
        consultation_fee=1200,
        is_paid=True,
        chief_complaint='Follow-up for chest pain management',
        symptoms='Chest pain improved, still some discomfort',
        doctor_notes='Patient reports improvement in symptoms. Blood pressure controlled.',
        actual_start_time=timezone.now() - timedelta(days=1, hours=2),
        actual_end_time=timezone.now() - timedelta(days=1, hours=1, minutes=40),
        is_follow_up=True,
        parent_consultation=consultation1
    )
    print(f"✅ Created consultation 2: {consultation2.chief_complaint}")
    
    consultations.append(consultation2)
    
    # Create consultation 3: Upcoming consultation
    consultation3_id = f"CON{last_number + 3:03d}"
    consultation3 = Consultation.objects.create(
        id=consultation3_id,
        patient=patient,
        doctor=doctor,
        scheduled_date=timezone.now().date() + timedelta(days=7),
        consultation_type='video_call',
        scheduled_time='11:00:00',
        duration=30,
        status='scheduled',
        payment_status='pending',
        consultation_fee=1500,
        is_paid=False,
        chief_complaint='Routine check-up and medication review',
        symptoms='No new symptoms, routine follow-up',
        is_follow_up=True,
        parent_consultation=consultation1
    )
    print(f"✅ Created consultation 3: {consultation3.chief_complaint}")
    
    consultations.append(consultation3)
    
    # Create prescriptions
    prescriptions = []
    
    # Prescription 1: For first consultation (finalized)
    prescription1 = Prescription.objects.create(
        consultation=consultation1,
        patient=patient,
        doctor=doctor,
        issued_date=consultation1.scheduled_date,
        issued_time=consultation1.scheduled_time,
        primary_diagnosis='Acute Coronary Syndrome',
        patient_previous_history='Hypertension, Diabetes Type 2',
        clinical_classification='Cardiovascular',
        general_instructions='Take medications as prescribed. Monitor blood pressure daily. Avoid strenuous activities for 2 weeks.',
        fluid_intake='Drink 8-10 glasses of water daily',
        diet_instructions='Low sodium diet. Avoid fried foods. Include fruits and vegetables.',
        lifestyle_advice='Quit smoking. Regular walking for 30 minutes daily. Stress management techniques.',
        next_visit='2 weeks',
        follow_up_notes='Schedule follow-up in 2 weeks. Monitor blood pressure and blood sugar.',
        is_draft=False,
        is_finalized=True
    )
    print(f"✅ Created prescription 1: {prescription1.primary_diagnosis}")
    
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
    prescription2 = Prescription.objects.create(
        consultation=consultation2,
        patient=patient,
        doctor=doctor,
        issued_date=consultation2.scheduled_date,
        issued_time=consultation2.scheduled_time,
        primary_diagnosis='Stable Angina',
        patient_previous_history='Hypertension, Diabetes Type 2',
        clinical_classification='Cardiovascular',
        general_instructions='Continue current medications. Monitor symptoms.',
        fluid_intake='Maintain adequate hydration',
        diet_instructions='Continue low sodium diet',
        lifestyle_advice='Continue regular exercise as tolerated',
        next_visit='1 week',
        follow_up_notes='Patient showing improvement. Continue current treatment.',
        is_draft=True,
        is_finalized=False
    )
    print(f"✅ Created prescription 2 (draft): {prescription2.primary_diagnosis}")
    
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
    
    print("\n" + "=" * 60)
    print("✅ Data created successfully for doctor!")
    print("\n📋 Summary:")
    print(f"   👨‍⚕️ Doctor: {doctor.name} (ID: {doctor.id})")
    print(f"   👤 Patient: {patient.name} (ID: {patient.id})")
    print(f"   📅 Consultations: {len(consultations)}")
    print(f"   💊 Prescriptions: {len(prescriptions)}")
    
    print("\n🔍 Now you can view the data:")
    print("   1. Frontend: http://localhost:8080/prescriptions")
    print("   2. Login with phone: +916666666661")
    print("   3. Navigate to prescription management")
    print("   4. You should now see consultations and prescriptions!")

if __name__ == "__main__":
    create_data_for_doctor() 