#!/bin/bash
# ============================================================
# JSS College Timetable Generator - Quick Setup Script
# ============================================================
set -e

echo "=================================="
echo " JSS TimetableGen Setup"
echo "=================================="

# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create superuser (optional)
echo ""
echo "Creating default admin account (admin / admin123)..."
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@jss.edu', 'admin123')
    u.role = 'admin'; u.first_name = 'Admin'; u.last_name = 'JSS'; u.save()
    print('  Admin user created.')
else:
    print('  Admin already exists.')
"

# 5. Collect static files
python manage.py collectstatic --noinput

echo ""
echo "=================================="
echo " Setup Complete!"
echo " Run: python manage.py runserver"
echo " Open: http://127.0.0.1:8000"
echo "=================================="
