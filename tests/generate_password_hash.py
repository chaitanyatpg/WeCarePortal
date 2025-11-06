#!/usr/bin/env python3
"""
Django Password Hash Generator
Generates Django-compatible password hashes for user authentication
"""
import os
import sys
import django
from django.conf import settings

# Set the SECRET_KEY to match Railway deployment
os.environ['SECRET_KEY'] = 'pye6yse*@_#*@hhjr(lajgmzfa)zkb0qhlzlml^8-j7+)84alp'

# Add the project directory to Python path
sys.path.append('/Users/uek/Documents/vCare/mycareportal_app')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycareportal.settings')

django.setup()

from django.contrib.auth.hashers import make_password

# Generate the password hash for 'WeCare@123'
new_password = "WeCare@123"
hashed_password = make_password(new_password)

print("Django Password Hash Generator")
print(f"Password: {new_password}")
print(f"Hashed: {hashed_password}")
print()
print("SQL UPDATE Statement:")
print(f"UPDATE mycareportal_app_user SET password = '{hashed_password}';")
print()
print("This will update ALL users in the mycareportal_app_user table to use the password 'WeCare@123'")
print("Run this SQL command in your PostgreSQL database to update all user passwords.")