#!/usr/bin/env python3
"""
Check Users and Reset Passwords
Utility script to check existing users and reset all passwords to a standard value
Note: This script modifies the database settings - use with caution
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.append('/Users/uek/Documents/vCare/mycareportal_app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycareportal_app.settings')

# Update database settings to point to restored_db
settings.DATABASES['default']['NAME'] = 'restored_db'

django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import make_password

print("Checking existing users in restored_db")
users = User.objects.all()
print(f"Total users found: {users.count()}")

for user in users:
    print(f"Username: {user.username}, Email: {user.email}, Active: {user.is_active}, Staff: {user.is_staff}, Superuser: {user.is_superuser}")

print("Resetting all passwords to 'WeCare@123'")
new_password = "WeCare@123"
hashed_password = make_password(new_password)

updated_count = User.objects.update(password=hashed_password)
print(f"Updated {updated_count} user passwords")

print("Verification")
# Test authentication for first user
if users.exists():
    from django.contrib.auth import authenticate
    first_user = users.first()
    auth_user = authenticate(username=first_user.username, password=new_password)
    if auth_user:
        print(f"SUCCESS: Password reset successful - can authenticate user '{first_user.username}'")
    else:
        print(f"ERROR: Password reset failed - cannot authenticate user '{first_user.username}'")