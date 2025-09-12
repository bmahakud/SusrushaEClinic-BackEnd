#!/bin/bash

# Sushrusa Healthcare - Investigation Tests Population Script
# ============================================================
# 
# This script populates the production database with investigation tests.
# Run this script on the production server to ensure all investigation tests are available.
#
# Usage:
#     ./populate_investigations.sh
#
# Requirements:
#     - Django environment must be properly configured
#     - Database connection must be working
#     - User must have appropriate permissions

echo "============================================================"
echo "SUSHURSA HEALTHCARE - INVESTIGATION TESTS POPULATION"
echo "============================================================"

# Check if we're in the correct directory
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the Django project root directory."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Virtual environment not detected. Make sure you're using the correct Python environment."
fi

echo ""
echo "1. Checking current database status..."
python manage.py shell -c "
from prescriptions.models import InvestigationTest, InvestigationCategory
total_tests = InvestigationTest.objects.count()
active_tests = InvestigationTest.objects.filter(is_active=True).count()
total_categories = InvestigationCategory.objects.count()
active_categories = InvestigationCategory.objects.filter(is_active=True).count()
print(f'   - Total tests: {total_tests}')
print(f'   - Active tests: {active_tests}')
print(f'   - Total categories: {total_categories}')
print(f'   - Active categories: {active_categories}')
"

echo ""
echo "2. Running investigation tests population commands..."

# Run each management command
commands=(
    "populate_investigations"
    "populate_complete_investigations"
    "populate_remaining_investigations"
    "populate_usg_xray_investigations"
)

for command in "${commands[@]}"; do
    echo ""
    echo "   Running: $command"
    if python manage.py "$command"; then
        echo "   ✓ $command completed successfully"
    else
        echo "   ✗ Error running $command"
    fi
done

echo ""
echo "3. Verifying final database status..."
python manage.py shell -c "
from prescriptions.models import InvestigationTest, InvestigationCategory
final_total_tests = InvestigationTest.objects.count()
final_active_tests = InvestigationTest.objects.filter(is_active=True).count()
final_total_categories = InvestigationCategory.objects.count()
final_active_categories = InvestigationCategory.objects.filter(is_active=True).count()
print(f'   - Total tests: {final_total_tests}')
print(f'   - Active tests: {final_active_tests}')
print(f'   - Total categories: {final_total_categories}')
print(f'   - Active categories: {final_active_categories}')
"

echo ""
echo "4. Sample investigation tests:"
python manage.py shell -c "
from prescriptions.models import InvestigationTest
sample_tests = InvestigationTest.objects.filter(is_active=True)[:10]
for test in sample_tests:
    print(f'   - {test.name} (category: {test.category.name})')
"

echo ""
echo "============================================================"
echo "INVESTIGATION TESTS POPULATION COMPLETED!"
echo "============================================================"

# Check if tests were populated successfully
final_count=$(python manage.py shell -c "from prescriptions.models import InvestigationTest; print(InvestigationTest.objects.filter(is_active=True).count())" 2>/dev/null)

if [ "$final_count" -gt 0 ]; then
    echo ""
    echo "✓ Successfully populated $final_count investigation tests"
    echo "✓ API endpoint should now return investigation tests"
    echo ""
    echo "You can now test the API endpoint:"
    echo "curl -H 'Authorization: Bearer YOUR_TOKEN' https://sushrusaeclinic.com/api/prescriptions/investigations/tests/"
else
    echo ""
    echo "✗ Warning: No active investigation tests found"
    echo "  Please check the database and try again"
    exit 1
fi
