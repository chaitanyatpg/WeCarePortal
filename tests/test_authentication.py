#!/usr/bin/env python3
"""
Test User Authentication and Database Connectivity
Tests login functionality and user role management
"""
import os
import sys
import django

# Set environment variables
os.environ['SECRET_KEY'] = 'pye6yse*@_#*@hhjr(lajgmzfa)zkb0qhlzlml^8-j7+)84alp'
os.environ['DATABASE_URL'] = 'postgresql://postgres:iZqiWaqywtjuemKshKnhZrJeHiRnJFfU@trolley.proxy.rlwy.net:32981/restored_db'

# Django setup
sys.path.append('/Users/uek/Documents/vCare/mycareportal_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycareportal.settings')
django.setup()

from mycareportal_app.models import User, UserRoles
from django.contrib.auth import authenticate

print("Testing PostgreSQL Authentication")

# Test user
username = "kumarmanu@yahoo.com"
password = "WeCare@123"

try:
    # Check if user exists
    user = User.objects.get(username=username)
    print(f"SUCCESS: User found: {user.username} (ID: {user.id})")
    print(f"   Active: {user.is_active}")
    print(f"   Email: {user.email}")
    
    # Check roles
    roles = UserRoles.objects.filter(user=user)
    if roles.exists():
        role_list = [r.role for r in roles]
        print(f"   Roles: {role_list}")
    else:
        print("   WARNING: No roles found")
    
    # Test authentication
    auth_user = authenticate(username=username, password=password)
    if auth_user:
        print(f"SUCCESS: User {username} authenticated successfully")
    else:
        print(f"FAILED: Login failed for {username}")
        print(f"   Current password hash: {user.password[:50]}...")
        
except User.DoesNotExist:
    print(f"ERROR: User {username} not found")
except Exception as e:
    print(f"ERROR: {e}")