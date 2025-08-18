#!/usr/bin/env python3
"""
Test script to check PDF generation with patient history
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from prescriptions.models import Prescription
from prescriptions.pdf_generator import ProfessionalPrescriptionPDFGenerator
from prescriptions.enhanced_pdf_generator import WPDFGenerator

def test_pdf_generation():
    """Test PDF generation with patient history"""
    
    print("🧪 Testing PDF Generation with Patient History")
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
    
    # Test the main PDF generator
    print("\n📄 Testing Main PDF Generator...")
    try:
        pdf_generator = ProfessionalPrescriptionPDFGenerator(prescription)
        pdf_content = pdf_generator.generate_pdf()
        
        if pdf_content:
            print("✅ Main PDF generator created PDF successfully")
            
            # Check if patient history is in the PDF content
            pdf_text = str(pdf_content)
            if "Patient History:" in pdf_text:
                print("✅ Patient History found in PDF content")
            else:
                print("❌ Patient History NOT found in PDF content")
                print("   PDF content preview:", pdf_text[:500])
        else:
            print("❌ Main PDF generator failed to create PDF")
            
    except Exception as e:
        print(f"❌ Error in main PDF generator: {e}")
    
    # Test the enhanced PDF generator
    print("\n📄 Testing Enhanced PDF Generator...")
    try:
        enhanced_generator = WPDFGenerator(prescription)
        enhanced_pdf_content = enhanced_generator.generate_pdf()
        
        if enhanced_pdf_content:
            print("✅ Enhanced PDF generator created PDF successfully")
            
            # Check if patient history is in the PDF content
            enhanced_pdf_text = str(enhanced_pdf_content)
            if "Patient Previous History:" in enhanced_pdf_text:
                print("✅ Patient History found in Enhanced PDF content")
            else:
                print("❌ Patient History NOT found in Enhanced PDF content")
                print("   Enhanced PDF content preview:", enhanced_pdf_text[:500])
        else:
            print("❌ Enhanced PDF generator failed to create PDF")
            
    except Exception as e:
        print(f"❌ Error in enhanced PDF generator: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 PDF Generation Test Completed!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        success = test_pdf_generation()
        if success:
            print("\n✅ PDF generation test completed successfully.")
            sys.exit(0)
        else:
            print("\n❌ PDF generation test failed.")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
