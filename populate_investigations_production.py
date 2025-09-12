#!/usr/bin/env python3
"""
Production Investigation Tests Population Script
===============================================

This script populates the production database with investigation tests.
Run this script on the production server to ensure all investigation tests are available.

Usage:
    python populate_investigations_production.py

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

from django.core.management import call_command
from prescriptions.models import InvestigationTest, InvestigationCategory

def main():
    """Main function to populate investigation tests"""
    print("=" * 60)
    print("SUSHURSA HEALTHCARE - INVESTIGATION TESTS POPULATION")
    print("=" * 60)
    
    # Check current status
    print("\n1. Checking current database status...")
    total_tests = InvestigationTest.objects.count()
    active_tests = InvestigationTest.objects.filter(is_active=True).count()
    total_categories = InvestigationCategory.objects.count()
    active_categories = InvestigationCategory.objects.filter(is_active=True).count()
    
    print(f"   - Total tests: {total_tests}")
    print(f"   - Active tests: {active_tests}")
    print(f"   - Total categories: {total_categories}")
    print(f"   - Active categories: {active_categories}")
    
    if total_tests > 0:
        print(f"\n   Database already has {total_tests} tests.")
        response = input("   Do you want to re-run the population commands? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping population. Exiting...")
            return
    
    # Run population commands
    print("\n2. Running investigation tests population commands...")
    
    commands = [
        'populate_investigations',
        'populate_complete_investigations', 
        'populate_remaining_investigations',
        'populate_usg_xray_investigations'
    ]
    
    for command in commands:
        try:
            print(f"\n   Running: {command}")
            call_command(command)
            print(f"   ✓ {command} completed successfully")
        except Exception as e:
            print(f"   ✗ Error running {command}: {e}")
            continue
    
    # Verify final status
    print("\n3. Verifying final database status...")
    final_total_tests = InvestigationTest.objects.count()
    final_active_tests = InvestigationTest.objects.filter(is_active=True).count()
    final_total_categories = InvestigationCategory.objects.count()
    final_active_categories = InvestigationCategory.objects.filter(is_active=True).count()
    
    print(f"   - Total tests: {final_total_tests}")
    print(f"   - Active tests: {final_active_tests}")
    print(f"   - Total categories: {final_total_categories}")
    print(f"   - Active categories: {final_active_categories}")
    
    # Show sample tests
    print("\n4. Sample investigation tests:")
    sample_tests = InvestigationTest.objects.filter(is_active=True)[:10]
    for test in sample_tests:
        print(f"   - {test.name} (category: {test.category.name})")
    
    print("\n" + "=" * 60)
    print("INVESTIGATION TESTS POPULATION COMPLETED!")
    print("=" * 60)
    
    if final_active_tests > 0:
        print(f"\n✓ Successfully populated {final_active_tests} investigation tests")
        print("✓ API endpoint should now return investigation tests")
    else:
        print("\n✗ Warning: No active investigation tests found")
        print("  Please check the database and try again")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
