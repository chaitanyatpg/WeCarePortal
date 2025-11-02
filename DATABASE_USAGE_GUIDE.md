# Django Database Usage Guide for WeCarePortal

## 🗄️ Understanding Django Database System

### What is Django Shell?
Django Shell is an interactive Python environment that:
- **Automatically loads** your Django project settings
- **Connects** to your configured database
- **Imports** all your models and Django features
- **Provides direct access** to database operations
- **Is built into Django** - no external tools needed

## 🚀 Database Access Methods

### Method 1: Django Shell (Interactive)
```bash
# Activate virtual environment
source venv38/bin/activate

# Open Django shell
python manage.py shell

# Now you can run Python commands with Django loaded
>>> from mycareportal_app.models import User, Client, Company
>>> User.objects.all()
>>> Client.objects.filter(company__company_name='CarePlus')
```

### Method 2: Django Shell One-Liner
```bash
# Run single command
python manage.py shell -c "from mycareportal_app.models import User; print(User.objects.count())"
```

### Method 3: Python Script (Like our mock data generator)
```python
# At top of any Python file:
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycareportal.settings')
django.setup()

# Now import and use Django models
from mycareportal_app.models import *
```

### Method 4: Django Admin Interface
```bash
# Create admin superuser
python manage.py createsuperuser

# Access web interface at: http://127.0.0.1:8000/admin/
```

## 📊 Generate Complete Mock Data

### Step 1: Run Mock Data Generator
```bash
# Make sure you're in project directory
cd /Users/uek/Documents/vCare/mycareportal_app

# Activate virtual environment
source venv38/bin/activate

# Run comprehensive mock data generator
python create_mock_data.py
```

### Step 2: Verify Data Creation
```bash
python manage.py shell -c "
from mycareportal_app.models import *
print('=== DATABASE SUMMARY ===')
print(f'Companies: {Company.objects.count()}')
print(f'Users: {User.objects.count()}')
print(f'Caregivers: {Caregiver.objects.count()}')
print(f'Clients: {Client.objects.count()}')
print(f'Care Managers: {CareManager.objects.count()}')
print(f'Caregiver Schedules: {CaregiverSchedule.objects.count()}')
print(f'Providers: {Provider.objects.count()}')
print(f'Family Contacts: {FamilyContact.objects.count()}')
"
```

### ✅ Expected Output After Running Mock Data Generator:
```
🚀 Starting comprehensive mock data generation...
==================================================
✅ Created company: CarePlus Health Services
✅ Created company: WellCare Solutions
✅ Created care manager: Sarah Johnson
✅ Created care manager: Mike Rodriguez
✅ Created care manager: Admin User
✅ Created caregiver: Emma Davis
✅ Created caregiver: James Wilson
✅ Created caregiver: Lisa Brown
✅ Created client: Robert Anderson
✅ Created client: Margaret Thompson
✅ Created client: William Garcia
✅ Created activity category: Personal Care
✅ Created activity category: Medication Management
✅ Created activity category: Meal Preparation
✅ Created activity category: Transportation
✅ Created activity category: Companionship
✅ Created activity category: Light Housekeeping
✅ Created caregiver schedules for clients
✅ Created providers and family contacts
==================================================
✅ Mock data generation complete!
📊 Summary:
   Companies: 3
   Users: 10
   Caregivers: 3
   Clients: 9
   Care Managers: 3
   Caregiver Schedules: 18
   Providers: 2
   Family Contacts: 2
```

## 🎭 Test Login Credentials

After running mock data generator, you can login with:

### Care Managers:
- **Username:** `sarah.johnson` | **Password:** `password123`
- **Username:** `mike.rodriguez` | **Password:** `password123`
- **Username:** `admin` | **Password:** `password123`

### Caregivers:
- **Username:** `emma.davis` | **Password:** `password123`
- **Username:** `james.wilson` | **Password:** `password123`
- **Username:** `lisa.brown` | **Password:** `password123`

### Additional Users Created:
- **Providers:** `provider_jennifer_smith`, `provider_michael_johnson`
- **Family Contacts:** `family_susan_anderson`, `family_david_thompson`

## 📋 Complete Mock Data Details

### 🏢 Companies Created:
1. **CarePlus Health Services** (New York, NY) - Primary test company
2. **WellCare Solutions** (Los Angeles, CA) - Secondary test company

### 👥 Users & Roles Summary:
- **3 Care Managers** across companies with admin privileges
- **3 Caregivers** with complete profiles, schedules, and client assignments
- **9 Clients** (3 per company) with medical info and caregiver relationships  
- **2 Healthcare Providers** with specialties and contact information
- **2 Family Contacts** linked to clients as emergency contacts

### 🗓️ Schedules & Relationships:
- **18 Caregiver Schedule entries** showing work assignments
- **Client-Caregiver assignments** via many-to-many relationships
- **Activity categories** for task management (Personal Care, Medication, etc.)
- **Provider specialties** including Family Medicine and Cardiology

### 📊 Sample Client Data:
```
Robert Anderson (robert.anderson@careplushealthservices.com)
├── Assigned Caregiver: Emma Davis (+1-555-1001)
├── Company: CarePlus Health Services
├── DOB: March 15, 1945 (Age 80)
└── Address: 789 Elm Street, New York, NY

Margaret Thompson (margaret.thompson@careplushealthservices.com) 
├── Assigned Caregiver: James Wilson (+1-555-1003)
├── Company: CarePlus Health Services
├── DOB: August 22, 1952 (Age 73)
└── Address: 456 Oak Avenue, New York, NY

William Garcia (william.garcia@careplushealthservices.com)
├── Assigned Caregiver: Lisa Brown (+1-555-1005)
├── Company: CarePlus Health Services  
├── DOB: December 10, 1938 (Age 86)
└── Address: 123 Pine Street, New York, NY
```

## 🔍 Common Database Operations

### View All Data
```python
# In Django shell:
from mycareportal_app.models import *

# List all clients
for client in Client.objects.all():
    print(f"{client.first_name} {client.last_name} - {client.email_address}")

# List all caregivers  
for caregiver in Caregiver.objects.all():
    print(f"{caregiver.first_name} {caregiver.last_name} - {caregiver.phone_number}")

# List all caregiver schedules
for schedule in CaregiverSchedule.objects.all():
    print(f"{schedule.caregiver.first_name} → {schedule.client.first_name} on {schedule.date}")
```

### Filter Data
```python
# Find clients in specific company
company = Company.objects.get(company_name='CarePlus Health Services')
clients = Client.objects.filter(company=company)

# Find schedules for specific client
client = Client.objects.get(email_address__icontains='robert.anderson')
schedules = CaregiverSchedule.objects.filter(client=client)

# Find caregivers with phone numbers
caregivers = Caregiver.objects.exclude(phone_number__isnull=True)
```

### Create New Data
```python
# Create new client
company = Company.objects.first()
new_client = Client.objects.create(
    first_name='John',
    last_name='Doe',
    email_address='john.doe@email.com',
    phone_number='+1-555-9999',
    company=company,
    time_zone=company.time_zone,
    date_of_birth=datetime.datetime(1970, 1, 1),
    gender='M',
    address='123 Test Street',
    city='Test City',
    state='NY',
    zip_code='12345'
)

# Create new caregiver schedule
caregiver = Caregiver.objects.first()
CaregiverSchedule.objects.create(
    company=company,
    client=new_client,
    caregiver=caregiver,
    date=datetime.date.today(),
    start_time=datetime.time(9, 0),
    end_time=datetime.time(17, 0)
)
```

## 🖥️ Accessing Different Screens

### Dashboard Views
- **Admin Dashboard:** Login as care manager → automatic redirect
- **Caregiver Dashboard:** Login as caregiver → shows assigned tasks
- **Client Dashboard:** Login as family member → shows client info

### Main Screens That Will Have Data:
1. **Client Management** - 9 clients across multiple companies with full profiles
2. **Caregiver Management** - 3 caregivers with complete information and assignments
3. **Schedule Management** - 18 caregiver schedule entries showing work assignments
4. **Provider Directory** - 2 healthcare providers with specialties
5. **Family Contacts** - 2 emergency contacts linked to clients
6. **User Management** - 10 users across different roles and companies
7. **Company Management** - Multiple companies with different settings
8. **Reports** - Rich data for analytics and reporting
9. **Activity Categories** - 6 care task categories for scheduling

## 🎯 Comprehensive Testing Scenarios

### 🔐 Authentication & Role Testing
```bash
# Test different user roles and dashboard access
# Login as Care Manager: sarah.johnson / password123
# Login as Caregiver: emma.davis / password123  
# Login as Provider: provider_jennifer_smith / password123
# Login as Family Contact: family_susan_anderson / password123
```

### 👥 Client-Caregiver Relationship Testing
- View client profiles with assigned caregivers
- Check caregiver schedules and assignments
- Test many-to-many relationships between clients and caregivers
- Verify client information displays correctly across companies

### 📅 Schedule & Time Management Testing
- View caregiver schedules (18 entries created)
- Test schedule filtering by date, caregiver, or client
- Verify schedule conflicts and availability
- Test time tracking features with real assignments

### 🏥 Healthcare Provider Integration
- Browse provider directory with Dr. Smith (Family Medicine) and Dr. Johnson (Cardiology)
- Test provider contact information and specialties
- Verify provider-client relationship features

### 👨‍👩‍👧‍👦 Family Contact Management
- View emergency contacts for clients
- Test family member access and permissions
- Verify contact information and relationships

### 🏢 Multi-Company Testing
- Switch between CarePlus Health Services and WellCare Solutions
- Test company-specific data isolation
- Verify users can only access their company's data
- Test company settings and configurations

## 🗃️ Database Files Location

### SQLite Database (Development)
- **File:** `db.sqlite3` (in project root)
- **Size:** ~2MB when populated
- **Status:** Ignored by Git (safe)
- **Backup:** Just copy the file

### Database Reset
```bash
# Complete reset (WARNING: Deletes all data)
rm db.sqlite3
python manage.py migrate
python create_mock_data.py
```

## 🔧 Advanced Operations

### Export Data
```bash
# Export all data to JSON
python manage.py dumpdata > backup.json

# Export specific app data
python manage.py dumpdata mycareportal_app > app_data.json
```

### Import Data
```bash
# Import from JSON backup
python manage.py loaddata backup.json
```

### Database Schema
```bash
# View database structure
python manage.py dbshell
.schema  # (if SQLite)
```

## 🎯 Testing All Features

With mock data generated, you can test:

### 🏥 Care Management Features
- View client profiles with medical info
- Assign caregivers to clients
- Schedule care tasks
- Track medication schedules

### 👥 User Management
- Different user roles (Manager, Caregiver, Family)
- Role-based dashboard views
- Permission-based access

### 📊 Reporting & Analytics
- Client care statistics
- Caregiver performance metrics
- Task completion rates
- Time tracking reports

### 💰 Business Features
- Invoice generation
- Payroll calculation
- Provider management
- Insurance tracking

## 🚨 Important Notes

1. **Local Only:** This database is only on your machine
2. **Development Use:** Perfect for testing and development
3. **Not Production:** Real deployment would use PostgreSQL
4. **Git Ignored:** Database file won't be committed to repository
5. **Easy Reset:** Can delete and recreate anytime

## 🔧 Troubleshooting

### Static Files Issue
If you see many `static/` files in Git changes:
```bash
# These are Django admin files that auto-generate
# They're already ignored in .gitignore, just don't commit them
git status --ignored  # Shows ignored files
```

### Mock Data Generator Errors
```bash
# If you get model field errors, the models may have changed
# Check the actual model fields in mycareportal_app/models.py
python manage.py shell -c "from mycareportal_app.models import Client; print([f.name for f in Client._meta.fields])"

# Reset database if needed
rm db.sqlite3
python manage.py migrate
python create_mock_data.py
```

### Login Issues
```bash
# Check if users were created successfully
python manage.py shell -c "from mycareportal_app.models import User; print([(u.username, u.is_active, u.account_activated) for u in User.objects.all()])"

# If care manager login fails, check CareManager records
python manage.py shell -c "from mycareportal_app.models import CareManager; print(CareManager.objects.count())"
```

### Database Schema Changes
```bash
# If you modify models, create and run migrations
python manage.py makemigrations
python manage.py migrate
python create_mock_data.py  # Recreate test data
```

## 🎯 Next Steps

With comprehensive mock data now loaded, you can:

1. **Test All User Roles** - Login as different user types and explore dashboards
2. **Verify Relationships** - Check client-caregiver assignments and schedules  
3. **Test Multi-Company** - Switch between companies and verify data isolation
4. **Explore Features** - Use all healthcare management features with realistic data
5. **Generate Reports** - Create analytics and reports with the rich dataset
6. **Test Workflows** - Follow complete care management workflows end-to-end

This gives you a complete healthcare management system with realistic data to explore every feature! 🎉