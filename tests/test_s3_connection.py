#!/usr/bin/env python3
"""
Test S3 Configuration and Connectivity
Tests AWS S3 bucket access and media file handling
"""
import os
import sys
import django

# Set environment variables
os.environ['SECRET_KEY'] = 'pye6yse*@_#*@hhjr(lajgmzfa)zkb0qhlzlml^8-j7+)84alp'
os.environ['DATABASE_URL'] = 'postgresql://postgres:iZqiWaqywtjuemKshKnhZrJeHiRnJFfU@trolley.proxy.rlwy.net:32981/restored_db'
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAY7FAJLEMWICEXUL2'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'

# Django setup
sys.path.append('/Users/uek/Documents/vCare/mycareportal_app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycareportal.settings')
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError

print("Testing S3 Configuration")
print(f"Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"Region: {getattr(settings, 'AWS_S3_REGION_NAME', 'Not set')}")
print(f"Custom Domain: {settings.AWS_S3_CUSTOM_DOMAIN}")
print(f"Media URL: {settings.MEDIA_URL}")

try:
    # Test S3 connection
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
    )
    
    # Test bucket access
    response = s3_client.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
    print("SUCCESS: S3 bucket access successful")
    
    # List first few objects
    response = s3_client.list_objects_v2(Bucket=settings.AWS_STORAGE_BUCKET_NAME, MaxKeys=5)
    if 'Contents' in response:
        print(f"Found {len(response['Contents'])} objects in bucket:")
        for obj in response['Contents'][:3]:
            print(f"   - {obj['Key']}")
    else:
        print("Bucket is empty")
        
except ClientError as e:
    print(f"ERROR: S3 Error: {e}")
except Exception as e:
    print(f"ERROR: General Error: {e}")

# Test media file generation
from mycareportal_app.models import HomeModificationUser
try:
    home_mod_user = HomeModificationUser.objects.filter(user__username='kumarmanu@yahoo.com').first()
    if home_mod_user and home_mod_user.profile_picture:
        print(f"User profile picture: {home_mod_user.profile_picture.url}")
    else:
        print("No profile picture found for user")
except Exception as e:
    print(f"ERROR: Profile picture error: {e}")