#!/usr/bin/env python3
"""
Fix Doctor ID Prefix Issue
==========================

This script fixes the issue where doctors have "ADM" prefix instead of "DOC" prefix.
It updates the user IDs to use the correct "DOC" prefix for doctors.

Usage:
    python fix_doctor_ids.py

Requirements:
    - Django environment must be properly configured
    - Database connection must be working
    - User must have appropriate permissions
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from doctors.models import DoctorProfile

User = get_user_model()

def main():
    """Main function to fix doctor IDs"""
    print("=" * 60)
    print("SUSHURSA HEALTHCARE - DOCTOR ID PREFIX FIX")
    print("=" * 60)
    
    # Find doctors with ADM prefix
    print("\n1. Finding doctors with ADM prefix...")
    adm_doctors = User.objects.filter(id__startswith='ADM', role='doctor')
    print(f"   Found {adm_doctors.count()} doctors with ADM prefix")
    
    if adm_doctors.count() == 0:
        print("   No doctors with ADM prefix found. Exiting...")
        return
    
    # Show current ADM doctors
    print("\n2. Current ADM doctors:")
    for doctor in adm_doctors:
        print(f"   - {doctor.id}: {doctor.name} ({doctor.phone})")
    
    # Get the last DOC number
    print("\n3. Finding next available DOC number...")
    last_doc_user = User.objects.filter(id__startswith='DOC').order_by('id').last()
    if last_doc_user:
        last_doc_number = int(last_doc_user.id[3:])
        next_doc_number = last_doc_number + 1
        print(f"   Last DOC number: {last_doc_number}")
        print(f"   Next DOC number: {next_doc_number}")
    else:
        next_doc_number = 1
        print(f"   No existing DOC users found. Starting from: {next_doc_number}")
    
    # Confirm the fix
    print(f"\n4. Proposed changes:")
    print(f"   Will update {adm_doctors.count()} doctors:")
    for i, doctor in enumerate(adm_doctors):
        new_id = f"DOC{next_doc_number + i:03d}"
        print(f"   - {doctor.id} → {new_id}: {doctor.name}")
    
    response = input("\n   Do you want to proceed with the fix? (y/N): ")
    if response.lower() != 'y':
        print("   Operation cancelled by user.")
        return
    
    # Perform the fix
    print("\n5. Updating doctor IDs...")
    updated_count = 0
    errors = []
    
    for i, doctor in enumerate(adm_doctors):
        try:
            old_id = doctor.id
            new_id = f"DOC{next_doc_number + i:03d}"
            
            # Check if new ID already exists
            if User.objects.filter(id=new_id).exists():
                errors.append(f"Cannot update {old_id} to {new_id}: ID already exists")
                continue
            
            # Update the user ID
            doctor.id = new_id
            doctor.save()
            
            # Update doctor profile if exists
            try:
                doctor_profile = DoctorProfile.objects.get(user=doctor)
                # The doctor profile should automatically reference the new user ID
                print(f"   ✓ Updated {old_id} → {new_id}: {doctor.name}")
                updated_count += 1
            except DoctorProfile.DoesNotExist:
                print(f"   ✓ Updated {old_id} → {new_id}: {doctor.name} (no profile found)")
                updated_count += 1
                
        except Exception as e:
            errors.append(f"Error updating {doctor.id}: {str(e)}")
            print(f"   ✗ Failed to update {doctor.id}: {str(e)}")
    
    # Show results
    print(f"\n6. Results:")
    print(f"   ✓ Successfully updated: {updated_count} doctors")
    if errors:
        print(f"   ✗ Errors: {len(errors)}")
        for error in errors:
            print(f"     - {error}")
    
    # Verify the fix
    print(f"\n7. Verification:")
    remaining_adm_doctors = User.objects.filter(id__startswith='ADM', role='doctor').count()
    doc_doctors = User.objects.filter(id__startswith='DOC', role='doctor').count()
    
    print(f"   Doctors with ADM prefix: {remaining_adm_doctors}")
    print(f"   Doctors with DOC prefix: {doc_doctors}")
    
    if remaining_adm_doctors == 0:
        print("\n" + "=" * 60)
        print("DOCTOR ID PREFIX FIX COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\n✓ All {updated_count} doctors now have DOC prefix")
        print("✓ API endpoints should now work correctly")
    else:
        print(f"\n⚠ Warning: {remaining_adm_doctors} doctors still have ADM prefix")
        print("  Please check the errors above and try again")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
