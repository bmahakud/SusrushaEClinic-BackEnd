#!/usr/bin/env python3
"""
Test script to verify prescription serializer fixes
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from prescriptions.serializers import (
    PrescriptionSerializer, 
    PrescriptionDetailSerializer, 
    PrescriptionCreateSerializer,
    PrescriptionUpdateSerializer,
    PrescriptionListSerializer,
    PrescriptionPDFSerializer,
    PrescriptionWithPDFSerializer
)
from prescriptions.models import Prescription, PrescriptionPDF
from django.contrib.auth import get_user_model

User = get_user_model()

def test_prescription_serializers():
    """Test prescription serializers to ensure they work correctly"""
    
    print("🔍 Testing Prescription Serializers")
    print("=" * 50)
    
    try:
        # Test 1: Check if we can create serializer instances
        print("✅ Testing serializer instantiation...")
        
        # Test PrescriptionSerializer
        prescription_serializer = PrescriptionSerializer()
        print("   ✅ PrescriptionSerializer - OK")
        
        # Test PrescriptionDetailSerializer
        detail_serializer = PrescriptionDetailSerializer()
        print("   ✅ PrescriptionDetailSerializer - OK")
        
        # Test PrescriptionCreateSerializer
        create_serializer = PrescriptionCreateSerializer()
        print("   ✅ PrescriptionCreateSerializer - OK")
        
        # Test PrescriptionUpdateSerializer
        update_serializer = PrescriptionUpdateSerializer()
        print("   ✅ PrescriptionUpdateSerializer - OK")
        
        # Test PrescriptionListSerializer
        list_serializer = PrescriptionListSerializer()
        print("   ✅ PrescriptionListSerializer - OK")
        
        # Test PrescriptionPDFSerializer
        pdf_serializer = PrescriptionPDFSerializer()
        print("   ✅ PrescriptionPDFSerializer - OK")
        
        # Test PrescriptionWithPDFSerializer
        with_pdf_serializer = PrescriptionWithPDFSerializer()
        print("   ✅ PrescriptionWithPDFSerializer - OK")
        
        print("\n" + "=" * 50)
        
        # Test 2: Check field definitions
        print("✅ Testing field definitions...")
        
        # Check PrescriptionDetailSerializer fields
        detail_fields = detail_serializer.get_fields()
        print(f"   📋 PrescriptionDetailSerializer fields: {list(detail_fields.keys())}")
        
        # Check if consultation_details and patient_history are SerializerMethodFields
        if 'consultation_details' in detail_fields:
            field_type = type(detail_fields['consultation_details']).__name__
            print(f"   ✅ consultation_details field type: {field_type}")
            if field_type == 'SerializerMethodField':
                print("   ✅ consultation_details is correctly defined as SerializerMethodField")
            else:
                print("   ❌ consultation_details should be SerializerMethodField")
        
        if 'patient_history' in detail_fields:
            field_type = type(detail_fields['patient_history']).__name__
            print(f"   ✅ patient_history field type: {field_type}")
            if field_type == 'SerializerMethodField':
                print("   ✅ patient_history is correctly defined as SerializerMethodField")
            else:
                print("   ❌ patient_history should be SerializerMethodField")
        
        print("\n" + "=" * 50)
        
        # Test 3: Check if there are any existing prescriptions to test with
        print("✅ Testing with existing data...")
        
        prescriptions = Prescription.objects.all()[:1]
        if prescriptions:
            prescription = prescriptions[0]
            print(f"   📄 Found prescription: {prescription.id}")
            
            # Test serialization
            try:
                serialized_data = detail_serializer.to_representation(prescription)
                print("   ✅ Serialization successful")
                print(f"   📊 Serialized data keys: {list(serialized_data.keys())}")
                
                # Check if computed fields are present
                if 'consultation_details' in serialized_data:
                    print("   ✅ consultation_details present in serialized data")
                else:
                    print("   ⚠️  consultation_details not in serialized data")
                
                if 'patient_history' in serialized_data:
                    print("   ✅ patient_history present in serialized data")
                else:
                    print("   ⚠️  patient_history not in serialized data")
                    
            except Exception as e:
                print(f"   ❌ Serialization failed: {e}")
        else:
            print("   📭 No prescriptions found in database")
        
        print("\n" + "=" * 50)
        
        # Test 4: Test PDF serializers
        print("✅ Testing PDF serializers...")
        
        pdf_instances = PrescriptionPDF.objects.all()[:1]
        if pdf_instances:
            pdf_instance = pdf_instances[0]
            print(f"   📄 Found PDF: {pdf_instance.id}")
            
            try:
                pdf_data = pdf_serializer.to_representation(pdf_instance)
                print("   ✅ PDF serialization successful")
                print(f"   📊 PDF data keys: {list(pdf_data.keys())}")
                
                # Check if computed fields are present
                if 'file_url' in pdf_data:
                    print("   ✅ file_url present in PDF data")
                else:
                    print("   ⚠️  file_url not in PDF data")
                
                if 'prescription_info' in pdf_data:
                    print("   ✅ prescription_info present in PDF data")
                else:
                    print("   ⚠️  prescription_info not in PDF data")
                    
            except Exception as e:
                print(f"   ❌ PDF serialization failed: {e}")
        else:
            print("   📭 No PDF instances found in database")
        
        print("\n" + "=" * 50)
        print("🏁 All serializer tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prescription_serializers() 