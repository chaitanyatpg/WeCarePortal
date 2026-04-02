#!/usr/bin/env python3
"""
Debug User Authentication with External Database
Run this script to test user authentication against restored database
Requires DATABASE_URL environment variable to be set
"""
import os
import sys

# Check for required environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: Please set DATABASE_URL environment variable")
    print("Example:")
    print("export DATABASE_URL='postgresql://postgres:password@containers-us-west-123.railway.app:1234/restored_db'")
    print("python debug_user_authentication.py")
    sys.exit(1)

print(f"Using database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

# Set environment variables
os.environ['SECRET_KEY'] = 'pye6yse*@_#*@hhjr(lajgmzfa)zkb0qhlzlml^8-j7+)84alp'
os.environ['DEBUG'] = 'True'

# Add project path
sys.path.append('/Users/uek/Documents/vCare/mycareportal_app')

# Import after setting env vars
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycareportal.settings')

try:
    django.setup()
    from mycareportal_app.models import User, UserRoles
    from django.contrib.auth import authenticate
    from django.contrib.auth.hashers import check_password
    
    print("SUCCESS: Django setup successful")
    
    # Test database connection
    user_count = User.objects.count()
    print(f"SUCCESS: Database connected - {user_count} users found")
    
    # Test specific user
    test_email = "kumarmanu@yahoo.com"
    test_password = "WeCare@123"
    
    try:
        user = User.objects.get(username=test_email)
        print(f"User found: {user.username} (ID: {user.id})")
        print(f"   Email: {user.email}")
        print(f"   Active: {user.is_active}")
        print(f"   Company: {user.company}")
        
        # Check roles
        user_roles = UserRoles.objects.filter(user=user)
        if user_roles.exists():
            roles = [ur.role for ur in user_roles]
            print(f"   Roles: {roles}")
        else:
            print("   WARNING: No roles assigned!")
        
        # Test authentication
        print(f"Testing authentication with password: {test_password}")
        
        # Direct password check
        password_valid = check_password(test_password, user.password)
        print(f"   Direct password check: {'VALID' if password_valid else 'INVALID'}")
        
        # Django authenticate
        auth_user = authenticate(username=test_email, password=test_password)
        print(f"   Django authenticate: {'SUCCESS' if auth_user else 'FAILED'}")
        
        if not auth_user:
            print(f"Current password hash: {user.password}")
            print("Try updating the password hash in the database with:")
            print("   UPDATE mycareportal_app_user SET password = 'pbkdf2_sha256$36000$6slCCLpQdAor+5S4$AU/p/LiJl8Bg3IIpoLq8ziAK7Fufv8DulOa6hAP5gYM=' WHERE username = 'kumarmanu@yahoo.com';")
        
    except User.DoesNotExist:
        print(f"ERROR: User '{test_email}' not found")
        print("Available users:")
        for user in User.objects.all()[:10]:
            print(f"   - {user.username}")
            
except Exception as e:
    print(f"ERROR: {e}")
    print("Possible issues:")
    print("1. Wrong DATABASE_URL")
    print("2. Database not accessible from local network")
    print("3. Django version compatibility")