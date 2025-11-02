# MyCarePortal - Healthcare Management System

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Architecture](#project-architecture)
- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
- [Project Structure](#project-structure)
- [Key Components](#key-components)
- [Security Considerations](#security-considerations)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

**MyCarePortal** is a comprehensive healthcare management platform built with Django 1.11. It's designed for healthcare organizations to manage caregivers, clients, families, providers, and various care-related activities including home modifications, move management, and comprehensive reporting.

The platform serves as a central hub for coordinating care services, tracking patient progress, managing staff schedules, and facilitating communication between all stakeholders in the healthcare ecosystem.

## Features

### Core Functionality
- **Multi-role User Management**: Care managers, caregivers, clients, families, healthcare providers
- **Patient Care Tracking**: Comprehensive care plans, progress monitoring, and incident reporting
- **Staff Management**: Caregiver scheduling, payroll management, and performance tracking
- **Assessment System**: Regular health assessments and care evaluations
- **Incident Reporting**: Real-time incident tracking and management
- **Communication Hub**: Messaging system between all stakeholders

### Specialized Modules
- **Home Modifications**: Managing accessibility modifications and equipment installations
- **Move Management**: Coordinating patient relocations and transitions
- **Billing & Payments**: Stripe integration for secure payment processing
- **Reporting & Analytics**: Comprehensive reporting dashboard with data visualization
- **Document Management**: File uploads, invoice generation, and document storage

### Technical Features
- **Multi-language Support**: English and Marathi localization
- **Email Notifications**: SendGrid integration for automated communications
- **Cloud Storage**: AWS S3 integration for file and media storage
- **Mobile Responsive**: Tablet and mobile-friendly interface
- **PDF Generation**: Automated invoice and report generation
- **Data Export**: Excel and PDF export capabilities

## Technology Stack

### Backend
- **Framework**: Django 1.11
- **Language**: Python 3.x
- **Database**: SQLite (development) / PostgreSQL (production)
- **Web Server**: Gunicorn (production)
- **Authentication**: Django's built-in authentication with custom backend

### Frontend
- **Template Engine**: Django Templates
- **CSS Framework**: Bootstrap 3.x
- **JavaScript Libraries**:
  - jQuery 3.x
  - Chart.js (data visualization)
  - DataTables (table management)
  - FullCalendar (scheduling)
  - Bootstrap components
  - Form validation libraries

### Third-Party Integrations
- **Cloud Storage**: AWS S3
- **Email Service**: SendGrid
- **Payment Processing**: Stripe
- **PDF Generation**: xhtml2pdf
- **Excel Export**: xlwt

## Project Architecture

### Django Application Structure
```
mycareportal/               # Django project configuration
├── settings.py            # Main configuration file
├── settings_local.py      # Local development settings
├── settings_production.py # Production settings
├── urls.py               # Main URL routing
└── wsgi.py               # WSGI application entry point

mycareportal_app/          # Main Django application
├── models.py             # Database models and business logic
├── views.py              # Main view controllers
├── client_views.py       # Client management views
├── caregiver_views.py    # Caregiver management views
├── family_views.py       # Family member views
├── provider_views.py     # Healthcare provider views
├── assessment_views.py   # Care assessment views
├── home_mod_views.py     # Home modification views
├── move_manage_views.py  # Move management views
├── reporting_views.py    # Reports and analytics views
├── settings_views.py     # Application settings views
├── forms.py              # Form definitions
├── urls.py               # Application URL patterns
├── admin.py              # Django admin configuration
├── context_processors.py # Custom context processors
└── backened.py           # Custom authentication backend
```

### Database Models
The application uses a comprehensive data model including:
- **User Management**: Custom user model with role-based permissions
- **Company Structure**: Multi-tenant company and department management
- **Client Management**: Patient profiles, medical history, care plans
- **Staff Management**: Caregiver profiles, schedules, payroll
- **Care Tracking**: Assessments, incidents, care notes
- **Billing**: Invoice generation, payment tracking

### File Organization
```
templates/                 # HTML templates
├── production/            # Main application templates
├── email/                 # Email templates by role
└── vendors/               # Third-party template assets

static/                    # Static assets
├── build/                 # Compiled CSS/JS
├── vendors/               # Third-party libraries
└── pictures/              # Images and icons

migrations/                # Database migration files
locale/                    # Internationalization files
fixtures/                  # Initial data fixtures
```

## Local Development Setup

### Prerequisites
- Python 3.6+ (tested with Python 3.12.3)
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)
- Git

### Installation Steps

1. **Clone the repository:**
```bash
git clone <repository-url>
cd mycareportal_app
```

2. **Create and activate virtual environment:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure local settings:**
```bash
# Copy local settings template (if needed)
cp mycareportal/settings_local.py.example mycareportal/settings_local.py

# Edit settings for local development
# Update database settings, debug mode, etc.
```

5. **Database setup:**
```bash
# Run migrations to create database tables
python manage.py migrate

# Load initial data (optional)
python manage.py loaddata mycareportal_app/fixtures/initial_data.json
```

6. **Create superuser account:**
```bash
python manage.py createsuperuser
```

7. **Collect static files:**
```bash
python manage.py collectstatic
```

8. **Run development server:**
```bash
python manage.py runserver
```

9. **Access the application:**
- Main application: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin/
- Login with the superuser account created in step 6

### Development Configuration

For local development, ensure these settings in your local configuration:

```python
# Debug mode
DEBUG = True

# Local database (SQLite for development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Disable SSL redirect for local development
# SECURE_SSL_REDIRECT = False

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## Production Deployment

### Heroku Deployment (Current Setup)

The application is configured for Heroku deployment:

```bash
# Install Heroku CLI and login
heroku login

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY='your-secret-key'
heroku config:set DATABASE_URL='your-database-url'

# Deploy to Heroku
git push heroku master

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### Traditional Server Deployment

#### Requirements:
- Ubuntu/CentOS server
- Python 3.6+
- PostgreSQL
- Nginx
- Gunicorn

#### Deployment Steps:

1. **Server Setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx
```

2. **Database Setup:**
```bash
# Create PostgreSQL database
sudo -u postgres createdb mycareportal
sudo -u postgres createuser mycareportaluser
sudo -u postgres psql -c "ALTER USER mycareportaluser WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mycareportal TO mycareportaluser;"
```

3. **Application Deployment:**
```bash
# Clone and setup application
git clone <repository-url> /var/www/mycareportal
cd /var/www/mycareportal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure production settings
# Edit mycareportal/settings_production.py
```

4. **Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /static/ {
        alias /var/www/mycareportal/static/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. **Gunicorn Service:**
```bash
# Create systemd service file
sudo nano /etc/systemd/system/mycareportal.service
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "mycareportal.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@db:5432/mycareportal
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=mycareportal
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Key Components

### User Roles and Permissions
- **Super Admin**: Full system access
- **Care Manager**: Patient and staff management
- **Caregiver**: Patient care and schedule management
- **Family Member**: Limited patient information access
- **Healthcare Provider**: Medical information and assessments
- **Client**: Personal care information access

### Main Modules

#### Client Management (`client_views.py`)
- Patient registration and profiles
- Care plan management
- Incident reporting
- Family member coordination

#### Caregiver Management (`caregiver_views.py`)
- Staff profiles and credentials
- Schedule management
- Payroll and time tracking
- Performance evaluations

#### Assessment System (`assessment_views.py`)
- Regular health assessments
- Care plan updates
- Progress tracking
- Medical history management

#### Home Modifications (`home_mod_views.py`)
- Accessibility assessment
- Equipment installation tracking
- Vendor management
- Cost tracking

#### Move Management (`move_manage_views.py`)
- Relocation planning
- Coordination between facilities
- Document transfer
- Timeline management

#### Reporting (`reporting_views.py`)
- Dashboard analytics
- Financial reports
- Staff performance reports
- Patient outcome reports

## Security Considerations

### Pre-Production Checklist

⚠️ **Critical Security Updates Required:**

1. **Environment Variables:**
```bash
# Required environment variables for production
SECRET_KEY=your-unique-secret-key
DEBUG=False
DATABASE_URL=your-database-url
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
SENDGRID_API_KEY=your-sendgrid-key
STRIPE_PUBLISHABLE_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
```

2. **Security Settings:**
- Update `SECRET_KEY` with a secure, unique value
- Set `DEBUG = False` in production
- Configure `ALLOWED_HOSTS` with your domain
- Enable SSL with `SECURE_SSL_REDIRECT = True`
- Remove hardcoded credentials from settings files

3. **Database Security:**
- Use strong database passwords
- Enable database SSL connections
- Regular database backups
- Implement database access restrictions

4. **File Upload Security:**
- Validate file types and sizes
- Scan uploaded files for malware
- Use secure file storage (AWS S3)

### HIPAA Compliance Considerations

If handling protected health information (PHI):
- Implement audit logging
- Data encryption at rest and in transit
- User access controls and monitoring
- Regular security assessments
- Business associate agreements with third parties

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Document complex functions and classes
- Write unit tests for critical functionality

### Database
- Always create migrations for model changes: `python manage.py makemigrations`
- Test migrations in development before deploying
- Keep migration files in version control

### Version Control
- Use descriptive commit messages
- Create feature branches for new development
- Review code before merging to main branch

## Troubleshooting

### Common Issues

1. **Migration Errors:**
```bash
# Reset migrations (development only)
python manage.py migrate --fake-initial
```

2. **Static Files Not Loading:**
```bash
# Collect static files
python manage.py collectstatic --clear
```

3. **Database Connection Issues:**
- Check database credentials in settings
- Ensure database server is running
- Verify network connectivity

4. **Email Not Sending:**
- Verify SendGrid API key
- Check email template configuration
- Review Django email settings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Support

For technical support or questions:
- Create an issue in the repository
- Review existing documentation
- Check Django 1.11 documentation for framework-specific questions

## License

This project is proprietary software. All rights reserved.

---

**Note**: This is a healthcare management system that may handle sensitive patient information. Ensure compliance with relevant healthcare regulations (HIPAA, GDPR, etc.) in your jurisdiction before deploying to production.