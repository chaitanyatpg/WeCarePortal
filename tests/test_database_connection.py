#!/usr/bin/env python3
"""
Test Database Connection and Basic Authentication
Tests Django setup and database connectivity
"""
import os
import sys
import django

# Add project path
sys.path.append('/Users/uek/Documents/vCare/mycareportal_app')

# Load .env and setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycareportal.settings')

try:
    django.setup()
    from mycareportal_app.models import User, UserRoles
    from django.contrib.auth import authenticate
    
    print("SUCCESS: Django setup successful")
    print(f"Database: {os.environ.get('DATABASE_URL', 'Not set')}")
    
    # Test connection
    user_count = User.objects.count()
    print(f"SUCCESS: Connected! Found {user_count} users")
    
    # Test specific user
    user = User.objects.get(username='kumarmanu@yahoo.com')
    print(f"User: {user.username} (Active: {user.is_active})")
    
    # Test authentication
    auth_result = authenticate(username='kumarmanu@yahoo.com', password='WeCare@123')
    print(f"Authentication: {'SUCCESS' if auth_result else 'FAILED'}")
    
    if not auth_result:
        print("NOTE: Check if user is active and password hash is correct")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("Make sure to update DATABASE_URL in .env file with your Railway external URL")