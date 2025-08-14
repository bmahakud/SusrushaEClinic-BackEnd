#!/usr/bin/env python3
"""
Test script to demonstrate the complete prescription flow
from creation to PDF generation with professional formatting.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from prescriptions.models import Prescription, PrescriptionMedication, PrescriptionVitalSigns
from prescriptions.enhanced_pdf_generator import generate_prescription_pdf

User = get_user_model()

def test_prescription_flow():
    """Test the complete prescription flow"""
    
    print("🏥 Testing Complete Prescription Flow")
    print("=" * 50)
    
    # Get a doctor and patient
    doctor = User.objects.filter(role='doctor').first()
    patient = User.objects.filter(role='patient').first()
    
    if not doctor or not patient:
        print("❌ No doctor or patient found in the system")
        return
    
    print(f"👨‍⚕️ Doctor: {doctor.name} (ID: {doctor.id})")
    print(f"👤 Patient: {patient.name} (ID: {patient.id})")
    print()
    
    # Step 1: Create a comprehensive prescription
    print("📝 Step 1: Creating Prescription")
    print("-" * 30)
    
    prescription = Prescription.objects.create(
        doctor=doctor,
        patient=patient,
        primary_diagnosis='Hypertension Stage 2 with Diabetes Type 2',
        patient_previous_history='Mild obesity and hyperlipidemia',
        clinical_classification='NYHA Class I',
        general_instructions='Take all medications regularly as prescribed. Monitor blood pressure twice daily. Check blood sugar levels before meals and at bedtime.',
        fluid_intake='2-3 liters of water daily',
        diet_instructions='Low sodium diet (<2g/day). Diabetic diet with controlled carbohydrates. Avoid processed foods and sugary drinks.',
        lifestyle_advice='Regular aerobic exercise 30-45 minutes daily. Quit smoking completely. Practice stress management techniques. Maintain healthy weight.',
        next_visit='After 3 weeks',
        follow_up_notes='Monitor for any side effects. Report immediately if experiencing dizziness, chest pain, or severe headache. Schedule lab tests for kidney function and lipid profile.',
        is_draft=False,
        is_finalized=True
    )
    
    print(f"✅ Created prescription ID: {prescription.id}")
    print(f"   - Diagnosis: {prescription.primary_diagnosis}")
    print(f"   - Status: {'Finalized' if prescription.is_finalized else 'Draft'}")
    print()
    
    # Step 2: Add medications
    print("💊 Step 2: Adding Medications")
    print("-" * 30)
    
    medications_data = [
        {
            'medicine_name': 'Amlodipine',
            'composition': '5mg tablet',
            'morning_dose': 1,
            'afternoon_dose': 0,
            'evening_dose': 0,
            'frequency': 'once_daily',
            'timing': 'after_breakfast',
            'duration_days': 30,
            'special_instructions': 'Take after breakfast. May cause mild ankle swelling initially.',
            'order': 1
        },
        {
            'medicine_name': 'Metformin',
            'composition': '500mg tablet',
            'morning_dose': 1,
            'afternoon_dose': 0,
            'evening_dose': 1,
            'frequency': 'twice_daily',
            'timing': 'with_food',
            'duration_days': 30,
            'special_instructions': 'Take with food to avoid stomach upset. Start with lower dose.',
            'order': 2
        },
        {
            'medicine_name': 'Atorvastatin',
            'composition': '10mg tablet',
            'morning_dose': 0,
            'afternoon_dose': 0,
            'evening_dose': 1,
            'frequency': 'once_daily',
            'timing': 'bedtime',
            'duration_days': 30,
            'special_instructions': 'Take at bedtime. Avoid grapefruit juice.',
            'order': 3
        },
        {
            'medicine_name': 'Aspirin',
            'composition': '75mg tablet',
            'morning_dose': 1,
            'afternoon_dose': 0,
            'evening_dose': 0,
            'frequency': 'once_daily',
            'timing': 'after_breakfast',
            'duration_days': 30,
            'special_instructions': 'Take after breakfast. Stop if bleeding occurs.',
            'order': 4
        }
    ]
    
    for med_data in medications_data:
        medication = PrescriptionMedication.objects.create(
            prescription=prescription,
            **med_data
        )
        print(f"✅ Added: {medication.medicine_name} - {medication.get_frequency_display()}")
    
    print(f"   Total medications: {prescription.medications.count()}")
    print()
    
    # Step 3: Add vital signs
    print("📊 Step 3: Adding Vital Signs")
    print("-" * 30)
    
    vital_signs = PrescriptionVitalSigns.objects.create(
        prescription=prescription,
        pulse=82,
        blood_pressure_systolic=145,
        blood_pressure_diastolic=95,
        temperature=36.8,
        weight=78.5,
        height=172.0,
        respiratory_rate=16,
        oxygen_saturation=98,
        blood_sugar_fasting=135,
        blood_sugar_postprandial=185,
        hba1c=7.2,
        notes='Patient shows signs of uncontrolled hypertension and diabetes. Weight has increased by 2kg in last 3 months.'
    )
    
    print(f"✅ Added vital signs:")
    print(f"   - BP: {vital_signs.blood_pressure_systolic}/{vital_signs.blood_pressure_diastolic} mmHg")
    print(f"   - Pulse: {vital_signs.pulse} bpm")
    print(f"   - Weight: {vital_signs.weight} kg")
    print(f"   - Blood Sugar (Fasting): {vital_signs.blood_sugar_fasting} mg/dL")
    print(f"   - HbA1c: {vital_signs.hba1c}%")
    print()
    
    # Step 4: Generate professional PDF
    print("📄 Step 4: Generating Professional PDF")
    print("-" * 30)
    
    try:
        pdf_instance = generate_prescription_pdf(prescription, doctor)
        print(f"✅ PDF Generated Successfully!")
        print(f"   - File: {pdf_instance.pdf_file.name}")
        print(f"   - Version: {pdf_instance.version_number}")
        print(f"   - Size: {pdf_instance.file_size} bytes")
        print(f"   - Generated by: {pdf_instance.generated_by.name}")
        print(f"   - Generated at: {pdf_instance.generated_at}")
        
        # Check if file exists
        if pdf_instance.pdf_file:
            file_path = pdf_instance.pdf_file.path
            if os.path.exists(file_path):
                print(f"   - File exists on disk: Yes")
                print(f"   - File path: {file_path}")
            else:
                print(f"   - File exists on disk: No")
        else:
            print(f"   - File exists on disk: No file field")
            
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Step 5: Display prescription summary
    print("📋 Step 5: Prescription Summary")
    print("-" * 30)
    
    print(f"Prescription ID: {prescription.id}")
    print(f"Patient: {prescription.patient.name}")
    print(f"Doctor: {prescription.doctor.name}")
    print(f"Date: {prescription.issued_date}")
    print(f"Time: {prescription.issued_time}")
    print(f"Status: {'Finalized' if prescription.is_finalized else 'Draft'}")
    print(f"Primary Diagnosis: {prescription.primary_diagnosis}")
    print(f"Medications: {prescription.medications.count()}")
    print(f"Vital Signs: {'Yes' if hasattr(prescription, 'vital_signs') and prescription.vital_signs else 'No'}")
    print(f"PDF Versions: {prescription.pdf_versions.count()}")
    
    print()
    print("🎉 Prescription Flow Test Completed Successfully!")
    print()
    print("📚 Available API Endpoints:")
    print("  - GET /api/prescriptions/{id}/ - View prescription details")
    print("  - GET /api/prescriptions/{id}/pdf-versions/ - List PDF versions")
    print("  - GET /api/prescriptions/{id}/pdf/latest/ - Download latest PDF")
    print("  - POST /api/prescriptions/{id}/finalize-and-generate-pdf/ - Regenerate PDF")
    print()
    print("🔗 Test URLs:")
    print(f"  - Prescription Details: http://127.0.0.1:8000/api/prescriptions/{prescription.id}/")
    print(f"  - PDF Versions: http://127.0.0.1:8000/api/prescriptions/{prescription.id}/pdf-versions/")
    print(f"  - Download PDF: http://127.0.0.1:8000/api/prescriptions/{prescription.id}/pdf/latest/")

if __name__ == "__main__":
    test_prescription_flow()