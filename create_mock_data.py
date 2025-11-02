#!/usr/bin/env python
"""
Comprehensive Mock Data Generator for WeCarePortal
Creates realistic test data for all healthcare management screens
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
import random
import uuid

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycareportal.settings')
django.setup()

# Import all models after Django setup
from mycareportal_app.models import *
from django.contrib.auth.models import Permission

class MockDataGenerator:
    """Generate comprehensive mock data for healthcare portal"""
    
    def __init__(self):
        self.companies = []
        self.users = []
        self.caregivers = []
        self.clients = []
        self.care_managers = []
        
    def create_companies(self):
        """Create sample healthcare companies"""
        company_data = [
            {
                'company_name': 'CarePlus Health Services',
                'contact_number': '+1-555-0123',
                'address': '123 Healthcare Blvd',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10001',
                'time_zone': 'America/New_York',
                'default_dashboard': 'ADMIN',
                'activated': True,
                'tax_rate': 8.25,
                'mileage_rate': 0.65
            },
            {
                'company_name': 'WellCare Solutions',
                'contact_number': '+1-555-0456',
                'address': '456 Medical Center Dr',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90210',
                'time_zone': 'America/Los_Angeles',
                'default_dashboard': 'ADMIN',
                'activated': True,
                'tax_rate': 9.50,
                'mileage_rate': 0.65
            }
        ]
        
        for data in company_data:
            company, created = Company.objects.get_or_create(
                company_name=data['company_name'],
                defaults=data
            )
            self.companies.append(company)
            if created:
                print(f"✅ Created company: {company.company_name}")
    
    def create_care_managers(self):
        """Create care manager users"""
        managers_data = [
            {
                'username': 'sarah.johnson',
                'email': 'sarah.johnson@careplus.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson'
            },
            {
                'username': 'mike.rodriguez',
                'email': 'mike.rodriguez@careplus.com', 
                'first_name': 'Mike',
                'last_name': 'Rodriguez'
            },
            {
                'username': 'admin',
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        ]
        
        for company in self.companies:
            for data in managers_data:
                # Create User
                user, created = User.objects.get_or_create(
                    username=data['username'],
                    defaults={
                        'email': data['email'],
                        'first_name': data['first_name'],
                        'last_name': data['last_name'],
                        'company': company,
                        'account_activated': True,
                        'is_active': True
                    }
                )
                if created:
                    user.set_password('password123')
                    user.save()
                
                # Create CareManager record
                care_manager, created = CareManager.objects.get_or_create(
                    user=user,
                    defaults={
                        'company': company,
                        'email_address': user.email,
                        'can_add': True
                    }
                )
                
                # Create UserRole
                UserRoles.objects.get_or_create(
                    user=user,
                    company=company,
                    defaults={'role': 'CAREMANAGER'}
                )
                
                self.care_managers.append(care_manager)
                if created:
                    print(f"✅ Created care manager: {user.first_name} {user.last_name}")
    
    def create_caregivers(self):
        """Create caregiver staff"""
        caregivers_data = [
            {
                'username': 'emma.davis',
                'email': 'emma.davis@careplus.com',
                'first_name': 'Emma',
                'last_name': 'Davis',
                'phone_number': '+1-555-1001',
                'date_of_birth': datetime.datetime(1985, 5, 15, 0, 0, 0),
                'gender': 'F',
                'address': '321 Caregiver Lane',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10005'
            },
            {
                'username': 'james.wilson',
                'email': 'james.wilson@careplus.com',
                'first_name': 'James', 
                'last_name': 'Wilson',
                'phone_number': '+1-555-1003',
                'date_of_birth': datetime.datetime(1980, 9, 22, 0, 0, 0),
                'gender': 'M',
                'address': '654 Helper Street',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10006'
            },
            {
                'username': 'lisa.brown',
                'email': 'lisa.brown@careplus.com',
                'first_name': 'Lisa',
                'last_name': 'Brown',
                'phone_number': '+1-555-1005',
                'date_of_birth': datetime.datetime(1988, 12, 3, 0, 0, 0),
                'gender': 'F',
                'address': '987 Care Avenue',
                'city': 'New York', 
                'state': 'NY',
                'zip_code': '10007'
            }
        ]
        
        for company in self.companies:
            for data in caregivers_data:
                # Create User
                user, created = User.objects.get_or_create(
                    username=data['username'],
                    defaults={
                        'email': data['email'],
                        'first_name': data['first_name'],
                        'last_name': data['last_name'],
                        'company': company,
                        'account_activated': True,
                        'is_active': True
                    }
                )
                if created:
                    user.set_password('password123')
                    user.save()
                
                # Create Caregiver record
                caregiver, created = Caregiver.objects.get_or_create(
                    user=user,
                    defaults={
                        'company': company,
                        'email_address': user.email,
                        'first_name': data['first_name'],
                        'last_name': data['last_name'],
                        'phone_number': data['phone_number'],
                        'date_of_birth': data['date_of_birth'],
                        'gender': data['gender'],
                        'address': data['address'],
                        'city': data['city'],
                        'state': data['state'],
                        'zip_code': data['zip_code']
                    }
                )
                
                # Create UserRole
                UserRoles.objects.get_or_create(
                    user=user,
                    company=company,
                    defaults={'role': 'CAREGIVER'}
                )
                
                self.caregivers.append(caregiver)
                if created:
                    print(f"✅ Created caregiver: {user.first_name} {user.last_name}")
    
    def create_clients(self):
        """Create client patients"""
        clients_data = [
            {
                'first_name': 'Robert',
                'last_name': 'Anderson',
                'email_address': 'robert.anderson@email.com',
                'phone_number': '+1-555-2001',
                'address': '789 Elm Street',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10002',
                'date_of_birth': datetime.datetime(1945, 3, 15, 0, 0, 0),
                'gender': 'M'
            },
            {
                'first_name': 'Margaret',
                'last_name': 'Thompson',
                'email_address': 'margaret.thompson@email.com',
                'phone_number': '+1-555-2003',
                'address': '456 Oak Avenue',
                'city': 'New York', 
                'state': 'NY',
                'zip_code': '10003',
                'date_of_birth': datetime.datetime(1952, 8, 22, 0, 0, 0),
                'gender': 'F'
            },
            {
                'first_name': 'William',
                'last_name': 'Garcia',
                'email_address': 'william.garcia@email.com',
                'phone_number': '+1-555-2005',
                'address': '123 Pine Street',
                'city': 'New York',
                'state': 'NY', 
                'zip_code': '10004',
                'date_of_birth': datetime.datetime(1938, 12, 10, 0, 0, 0),
                'gender': 'M'
            }
        ]
        
        for company in self.companies:
            for i, data in enumerate(clients_data):
                # Make email unique per company
                unique_email = f"{data['first_name'].lower()}.{data['last_name'].lower()}@{company.company_name.lower().replace(' ', '')}.com"
                client_data = data.copy()
                client_data['email_address'] = unique_email
                
                client, created = Client.objects.get_or_create(
                    email_address=unique_email,
                    company=company,
                    defaults={
                        **client_data,
                        'company': company,
                        'time_zone': company.time_zone
                    }
                )
                
                # Assign caregiver if available (ManyToMany relationship)
                if self.caregivers and created:
                    caregiver = self.caregivers[i % len(self.caregivers)]
                    client.caregiver.add(caregiver)
                
                self.clients.append(client)
                if created:
                    print(f"✅ Created client: {client.first_name} {client.last_name}")
    
    def create_tasks_and_schedules(self):
        """Create tasks and caregiver schedules"""
        task_categories = [
            'Personal Care',
            'Medication Management', 
            'Meal Preparation',
            'Transportation',
            'Companionship',
            'Light Housekeeping'
        ]
        
        # Create Activity Categories
        for category_name in task_categories:
            category, created = ActivityMaster.objects.get_or_create(
                activity_description=category_name,
                defaults={
                    'activity_code': category_name.upper().replace(' ', '_')
                }
            )
            
            if created:
                print(f"✅ Created activity category: {category_name}")
        
        # Create sample caregiver schedules for each client
        for client in self.clients[:3]:  # Limit to first 3 clients
            if client.caregiver.exists():
                caregiver = client.caregiver.first()
                for i in range(3):  # 3 schedule entries per client
                    schedule_date = datetime.datetime.now().date() + timedelta(days=i)
                    
                    CaregiverSchedule.objects.create(
                        company=client.company,
                        client=client,
                        caregiver=caregiver,
                        date=schedule_date,
                        start_time=datetime.time(hour=9, minute=0),  # 9:00 AM
                        end_time=datetime.time(hour=17, minute=0)    # 5:00 PM
                    )
        
        print(f"✅ Created caregiver schedules for clients")
    
    def create_providers_and_contacts(self):
        """Create healthcare providers and family contacts"""
        providers_data = [
            {
                'first_name': 'Jennifer',
                'last_name': 'Smith',
                'email_address': 'dr.smith@medicenter.com',
                'phone_number': '+1-555-3001',
                'provider_type': 'Doctor',
                'speciality': 'Family Medicine'
            },
            {
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'email_address': 'dr.johnson@cardiology.com', 
                'phone_number': '+1-555-3002',
                'provider_type': 'Doctor',
                'speciality': 'Cardiology'
            }
        ]
        
        for company in self.companies[:1]:  # Just first company
            for data in providers_data:
                # Create User for Provider
                user, created = User.objects.get_or_create(
                    username=f"provider_{data['first_name'].lower()}_{data['last_name'].lower()}",
                    defaults={
                        'email': data['email_address'],
                        'first_name': data['first_name'],
                        'last_name': data['last_name'],
                        'company': company,
                        'account_activated': True,
                        'is_active': True
                    }
                )
                
                Provider.objects.get_or_create(
                    email_address=data['email_address'],
                    company=company,
                    defaults={
                        **data,
                        'company': company,
                        'user': user
                    }
                )
        
        # Create family contacts for clients
        family_contacts_data = [
            {
                'first_name': 'Susan',
                'last_name': 'Anderson',
                'email_address': 'susan.anderson@email.com',
                'phone_number': '+1-555-4001',
                'relationship': 'Daughter',
                'address': '456 Family Street',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10008'
            },
            {
                'first_name': 'David',
                'last_name': 'Thompson', 
                'email_address': 'david.thompson@email.com',
                'phone_number': '+1-555-4002',
                'relationship': 'Son',
                'address': '789 Relative Ave',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10009'
            }
        ]
        
        for i, client in enumerate(self.clients[:2]):
            if i < len(family_contacts_data):
                data = family_contacts_data[i]
                # Create User for FamilyContact
                user, created = User.objects.get_or_create(
                    username=f"family_{data['first_name'].lower()}_{data['last_name'].lower()}",
                    defaults={
                        'email': data['email_address'],
                        'first_name': data['first_name'],
                        'last_name': data['last_name'],
                        'company': client.company,
                        'account_activated': True,
                        'is_active': True
                    }
                )
                
                FamilyContact.objects.get_or_create(
                    email_address=data['email_address'],
                    company=client.company,
                    defaults={
                        **data,
                        'company': client.company,
                        'user': user
                    }
                )
        
        print(f"✅ Created providers and family contacts")
    
    def generate_all_data(self):
        """Generate all mock data"""
        print("🚀 Starting comprehensive mock data generation...")
        print("=" * 50)
        
        self.create_companies()
        self.create_care_managers()
        self.create_caregivers()
        self.create_clients()
        self.create_tasks_and_schedules()
        self.create_providers_and_contacts()
        
        print("=" * 50)
        print("✅ Mock data generation complete!")
        print(f"📊 Summary:")
        print(f"   Companies: {Company.objects.count()}")
        print(f"   Users: {User.objects.count()}")
        print(f"   Caregivers: {Caregiver.objects.count()}")
        print(f"   Clients: {Client.objects.count()}")
        print(f"   Care Managers: {CareManager.objects.count()}")
        print(f"   Caregiver Schedules: {CaregiverSchedule.objects.count()}")
        print(f"   Providers: {Provider.objects.count()}")
        print(f"   Family Contacts: {FamilyContact.objects.count()}")

if __name__ == '__main__':
    generator = MockDataGenerator()
    generator.generate_all_data()