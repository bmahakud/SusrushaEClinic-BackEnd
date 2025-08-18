#!/usr/bin/env python3
"""
Debug script to check PDF content generation
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from prescriptions.models import Prescription

def debug_pdf_content():
    """Debug PDF content generation"""
    
    print("🔍 Debugging PDF Content Generation")
    print("=" * 60)
    
    # Get a prescription with patient history
    prescription = Prescription.objects.filter(
        patient_previous_history__isnull=False
    ).exclude(patient_previous_history='').first()
    
    if not prescription:
        print("❌ No prescription found with patient history")
        return False
    
    print(f"✅ Found prescription ID: {prescription.id}")
    print(f"   Patient: {prescription.patient.name}")
    print(f"   Doctor: {prescription.doctor.name}")
    print(f"   Primary Diagnosis: {prescription.primary_diagnosis}")
    print(f"   Patient History: {prescription.patient_previous_history}")
    print(f"   Clinical Classification: {prescription.clinical_classification}")
    
    # Check the condition that determines if diagnosis section is shown
    print("\n🔍 Checking Diagnosis Section Conditions:")
    print(f"   Has Primary Diagnosis: {bool(prescription.primary_diagnosis)}")
    print(f"   Has Patient History: {bool(prescription.patient_previous_history)}")
    print(f"   Has Clinical Classification: {bool(prescription.clinical_classification)}")
    
    # Check if the condition is met
    condition_met = prescription.primary_diagnosis or prescription.patient_previous_history
    print(f"   Diagnosis Section Will Show: {condition_met}")
    
    if condition_met:
        print("\n📝 What will be in the diagnosis text:")
        diagnosis_text = ""
        if prescription.primary_diagnosis:
            diagnosis_text += f"<b>Primary:</b> {prescription.primary_diagnosis}"
        if prescription.patient_previous_history:
            if diagnosis_text:
                diagnosis_text += "<br/>"
            diagnosis_text += f"<b>Patient History:</b> {prescription.patient_previous_history}"
        if prescription.clinical_classification:
            if diagnosis_text:
                diagnosis_text += "<br/>"
            diagnosis_text += f"<b>Clinical Classification:</b> {prescription.clinical_classification}"
        
        print(f"   Generated Diagnosis Text: {diagnosis_text}")
    else:
        print("   ❌ Diagnosis section will NOT be shown")
    
    print("\n" + "=" * 60)
    print("🎉 Debug completed!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        success = debug_pdf_content()
        if success:
            print("\n✅ Debug completed successfully.")
            sys.exit(0)
        else:
            print("\n❌ Debug failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Debug failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
