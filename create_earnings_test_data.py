#!/usr/bin/env python
"""
Script to create test payment data for doctor earnings functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta, time
from decimal import Decimal
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.utils import timezone
from authentication.models import User
from consultations.models import Consultation
from payments.models import Payment

def create_test_payments():
    """Create test payment data for doctors"""
    
    # Get a doctor user
    try:
        doctor = User.objects.filter(role='doctor').first()
        if not doctor:
            print("No doctor found. Please create a doctor user first.")
            return
        
        # Get an existing patient user
        patient = User.objects.filter(role='patient').first()
        if not patient:
            print("No patient found. Please create a patient user first.")
            return
        
        print(f"Using doctor: {doctor.name}")
        print(f"Using patient: {patient.name}")
        
        # Create test consultations and payments for the last 6 months
        base_date = timezone.now().date()
        payment_methods = ['card', 'upi', 'net_banking', 'wallet']
        consultation_types = ['video', 'in-person']
        
        total_created = 0
        
        for month_offset in range(6):
            # Calculate month start and end
            month_start = base_date.replace(day=1) - timedelta(days=30 * month_offset)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Create 5-15 consultations per month
            num_consultations = random.randint(5, 15)
            
            for i in range(num_consultations):
                # Random date within the month
                days_offset = random.randint(0, (month_end - month_start).days)
                consultation_date = month_start + timedelta(days=days_offset)
                
                # Create consultation
                consultation = Consultation.objects.create(
                    patient=patient,
                    doctor=doctor,
                    consultation_type=random.choice(consultation_types),
                    scheduled_date=consultation_date,
                    scheduled_time=time(random.randint(9, 17), random.randint(0, 59)),
                    duration=30,
                    status='completed',
                    payment_status='completed',
                    consultation_fee=Decimal(random.randint(500, 2000)),
                    is_paid=True,
                    chief_complaint=f"Test consultation {i+1}",
                    created_at=timezone.now() - timedelta(days=30 * month_offset + days_offset),
                    updated_at=timezone.now() - timedelta(days=30 * month_offset + days_offset)
                )
                
                # Create payment
                payment_amount = consultation.consultation_fee
                payment = Payment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    consultation=consultation,
                    amount=payment_amount,
                    currency='INR',
                    payment_method=random.choice(payment_methods),
                    payment_type='consultation',
                    status='completed',
                    description=f"Payment for consultation {consultation.id}",
                    processed_at=consultation.created_at + timedelta(minutes=random.randint(1, 60)),
                    completed_at=consultation.created_at + timedelta(minutes=random.randint(1, 60)),
                    gateway_name='test_gateway',
                    gateway_transaction_id=f"GTW{str(consultation.id).zfill(6)}",
                    gateway_response={
                        'status': 'success',
                        'message': 'Transaction successful',
                        'code': '200'
                    }
                )
                
                total_created += 1
        
        print(f"Successfully created {total_created} test payments")
        print("Test data includes:")
        print("- 6 months of payment history")
        print("- 5-15 consultations per month")
        print("- Various payment methods (card, UPI, net banking, wallet)")
        print("- Different consultation types (video, in-person)")
        print("- Random consultation fees between ₹500-₹2000")
        print("- All payments marked as completed")
        
    except Exception as e:
        print(f"Error creating test data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_test_payments()
