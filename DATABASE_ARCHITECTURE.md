# MyCarePortal Database Architecture & App Working Guide

## Overview
MyCarePortal is a multi-tenant healthcare management system built with Django 1.11. It manages care coordination between caregivers, clients, families, and healthcare providers.

## Database Architecture

### Core Entity Relationship Model

```
Company (Multi-tenant)
  ├── Users (All user types)
  ├── Clients (Patients)
  ├── Caregivers (Staff)
  ├── Care Managers
  ├── Family Users
  └── Provider Users
```

## 1. User Management & Authentication

### Core User Models
- **Company**: Multi-tenant organization container
  - `company_id` (Primary Key)
  - `company_name` (Unique)
  - `uid` (UUID for external references)
  
- **User**: Custom user model extending Django's AbstractUser
  - Links to `Company` (Foreign Key)
  - `account_activated` (Boolean)
  - Email notification preferences
  - **Authentication**: Uses `CaseInsensitiveModelBackend` for username lookup

### User Type Hierarchy
```
User (Base)
├── CareManager (Manages clients and caregivers)
├── Caregiver (Provides direct care)
├── FamilyUser (Client's family members)
├── ProviderUser (Healthcare providers)
├── HomeModificationUser (Home modification specialists)
└── MoveManager (Relocation coordinators)
```

## 2. Client Management System

### Client Entity Structure
- **Client**: Central patient record
  - Personal information (name, DOB, address)
  - Medical details (diagnoses, medications)
  - Care preferences and notes
  - Links to `Company` and assigned `Caregiver`

### Client Support Network
- **FamilyContact**: Client's family members and emergency contacts
- **Provider**: Healthcare providers (doctors, therapists)
- **Pharmacy**: Medication management
- **Payer**: Insurance and payment sources

## 3. Task & Care Management

### Task Hierarchy
```
ActivityMaster
├── ActivitySubCategory
    ├── DefaultTasks (Templates)
    └── Tasks (Actual assignments)
        ├── TaskSchedule (When to do)
        ├── TaskComment (Progress notes)
        ├── TaskAttachment (Files/photos)
        └── TaskLink (Related tasks)
```

### Task Templates System
- **TaskTemplate**: Reusable care plan templates
- **TaskTemplateSubcategory**: Grouped template sections
- **TaskTemplateEntry**: Individual template tasks
- **TaskTemplateInstance**: Applied templates to clients

## 4. Scheduling & Time Management

### Caregiver Scheduling
- **CaregiverScheduleHeader**: Schedule periods
- **CaregiverSchedule**: Individual shifts and assignments
- **CaregiverTimeSheet**: Time tracking and payroll data

### Assessment System
- **AssessmentCategories**: Types of assessments
- **AssessmentTask**: Standard assessment items
- **ClientAssessmentMap**: Client-specific assessments

## 5. Incident & Safety Management

### Incident Tracking
- **DefaultIncidents**: Standard incident types
- **IncidentLocations**: Where incidents occur
- **IncidentReport**: Actual incident records linked to tasks

## 6. Specialized Modules

### Home Modification Workflow
```
Client Need → HomeModificationTask → HomeModTaskBid → HomeModProject
                                         ↓
                              Progress/Budget/Duration Logs
```

### Move Management Workflow
```
Client Relocation → MoveManageTask → MoveManageTaskBid → MoveManagementProject
                                         ↓
                                   Inventory Tracking
```

### End-of-Life Care
- **ClientEndOfLife**: End-of-life care planning
- **EndOfLifeComment**: Care notes and decisions
- **EndOfLifeAttachment**: Important documents

## 7. Business Management

### Financial Management
- **InvoiceHeader/InvoiceLineItem**: Client billing
- **PayrollHeader/PayrollLineItem**: Staff payroll
- **InvoiceRateType**: Billing rate structures

### CRM System
- **CrmClientLead**: Prospective clients
- **CrmNotes**: Sales and follow-up notes

## 8. System Configuration

### Matching & Criteria
- **ClientMatchCategory/ClientMatchCriteria**: Client care requirements
- **CaregiverCriteriaMap**: Caregiver qualifications
- **ClientCertificationMap/CaregiverCertificationMap**: Certifications tracking

### Notifications & Communication
- **UserFcmTokenMap**: Mobile push notifications
- **NotifyClientVitalTask**: Health monitoring alerts

## Authentication Flow

### Login Process
1. **URL**: `/login` → `auth_views.LoginView`
2. **Template**: `production/wecare_login.html`
3. **Authentication Backend**: `CaseInsensitiveModelBackend`
4. **Process**:
   ```python
   # mycareportal_app/backened.py
   def authenticate(username, password):
       # Case-insensitive username lookup
       user = User.objects.get(username__iexact=username)
       if user.check_password(password) and user.account_activated:
           return user
   ```

### User Roles & Permissions
- Users are assigned to specific user type models
- Company-based data isolation (multi-tenancy)
- Role-based access control through user type checking

## Key Features

### Multi-Tenancy
- All data is company-scoped
- Users can only access their company's data
- Shared system with isolated data

### Soft Deletion
- `SoftDeletionModel` base class for recoverable deletions
- Maintains data integrity while allowing "deletion"

### Audit Trail
- Progress logs for projects (budget, duration, status)
- Comment and attachment systems for documentation
- Time tracking for accountability

### Mobile Integration
- FCM tokens for push notifications
- Tablet registration for field workers
- Location tracking capabilities

## File Storage
- **Local Development**: Files stored in `mycareportal_app/media/`
- **Production**: AWS S3 integration for scalable file storage

## Database Setup for Development
```bash
# Run migrations
python manage.py migrate

# Create test data
python manage.py shell -c "
from mycareportal_app.models import Company, User
company = Company.objects.create(company_name='Test Company')
user = User.objects.create_user(
    username='admin',
    password='admin123', 
    email='admin@test.com',
    company=company,
    account_activated=True
)
"
```

## Debugging Login Issues
1. Set breakpoints in `mycareportal_app/backened.py:7` (authenticate method)
2. Check user exists: `User.objects.filter(username__iexact='username')`
3. Verify password: `user.check_password('password')`
4. Confirm activation: `user.account_activated == True`
5. Check company association: `user.company` exists

## API Endpoints Structure
- **No REST API**: Traditional Django views with form-based interactions
- **AJAX endpoints**: Various `get_*_with_*` endpoints for dynamic data loading
- **File uploads**: Attachment handling for documents and images