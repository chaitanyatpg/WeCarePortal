# 🔒 Production Deployment Checklist

## ⚠️ **CRITICAL SECURITY FIXES** (Must Do Before Deployment)

### 1. **Remove Sensitive Data from Code**
```python
# ❌ REMOVE from settings.py:
SECRET_KEY = 'ylwi3hn#79&v2(%#k&por1szkfssgih4nn)13t4q9v0sz47*eg'
AWS_ACCESS_KEY_ID = 'AKIAI2SFPXGFAAHZ5XCQ'
AWS_SECRET_ACCESS_KEY = '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'

# ✅ USE environment variables instead:
SECRET_KEY = os.environ.get('SECRET_KEY')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
```

### 2. **Production Settings**
- [ ] Set `DEBUG = False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Generate new `SECRET_KEY`
- [ ] Remove AWS credentials from code
- [ ] Enable CSRF protection
- [ ] Configure secure headers

## 🚀 **Quick Deployment Options**

### **Option 1: Railway (EASIEST - 5 minutes)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Add PostgreSQL database
railway add postgresql

# Set environment variables in Railway dashboard:
# - SECRET_KEY=your-new-secret-key
# - DJANGO_SETTINGS_MODULE=mycareportal.production_settings
```

### **Option 2: Render (FREE TIER)**
1. Go to [render.com](https://render.com)
2. Connect GitHub repository
3. Choose "Web Service"
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python manage.py runserver 0.0.0.0:10000`
6. Add PostgreSQL database
7. Set environment variables

### **Option 3: Docker (ANY PLATFORM)**
```bash
# Build and test locally
docker-compose up --build

# Deploy to any cloud provider
# (DigitalOcean, AWS, Google Cloud, etc.)
```

## 📋 **Pre-Deployment Checklist**

### **Code Security**
- [ ] Remove hardcoded secrets from `settings.py`
- [ ] Add environment variables for sensitive data
- [ ] Set `DEBUG = False` in production
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Generate new `SECRET_KEY` for production

### **Database**
- [ ] Switch from SQLite to PostgreSQL for production
- [ ] Configure database backups
- [ ] Test database migrations
- [ ] Verify mock data loads correctly

### **Static Files**
- [ ] Configure static file serving (WhiteNoise)
- [ ] Test `python manage.py collectstatic`
- [ ] Verify CSS/JS files load properly

### **Dependencies**
- [ ] Update `requirements.txt` if needed
- [ ] Test app with Python 3.8
- [ ] Verify all dependencies install correctly

## 🔧 **Environment Variables to Set**

```bash
# Required
SECRET_KEY=your-super-secret-production-key
DJANGO_SETTINGS_MODULE=mycareportal.production_settings
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (auto-provided by most platforms)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Email (if using SendGrid)
SENDGRID_API_KEY=your-sendgrid-key

# AWS (if using S3 for media files)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

## 🏥 **Healthcare App Specific Checks**

### **HIPAA Compliance Considerations**
- [ ] Enable HTTPS (SSL/TLS) - most platforms auto-provide
- [ ] Configure secure session cookies
- [ ] Set up proper access controls
- [ ] Enable audit logging
- [ ] Review data retention policies
- [ ] Consider PHI data encryption

### **Mock Data**
- [ ] Verify mock data loads automatically on deployment
- [ ] Test all user login credentials work
- [ ] Confirm client-caregiver relationships display
- [ ] Check schedule data appears correctly

### **User Testing**
- [ ] Test Care Manager login: `sarah.johnson / password123`
- [ ] Test Caregiver login: `emma.davis / password123`
- [ ] Test Provider login: `provider_jennifer_smith / password123`
- [ ] Verify different dashboard views work
- [ ] Test multi-company data isolation

## 🔄 **Post-Deployment Steps**

### **Immediate Actions**
1. **Test the live app** - Open your deployed URL
2. **Login with test accounts** - Verify authentication works
3. **Check database** - Confirm mock data is present
4. **Test key features** - Client management, schedules, etc.
5. **Verify static files** - CSS/JS should load properly

### **Monitor & Maintain**
- [ ] Set up monitoring/alerts
- [ ] Configure automated backups
- [ ] Review application logs
- [ ] Plan for scaling if needed
- [ ] Set up custom domain (optional)

## 🆘 **Common Issues & Solutions**

### **Static Files Not Loading**
```bash
# Solution: Run collectstatic
python manage.py collectstatic --noinput
```

### **Database Migration Errors**
```bash
# Solution: Reset database
railway run python manage.py migrate --run-syncdb
railway run python create_mock_data.py
```

### **Internal Server Error (500)**
```bash
# Solution: Check logs and environment variables
railway logs
# Ensure SECRET_KEY and DATABASE_URL are set
```

### **CSRF Token Missing**
```python
# Solution: Add to production_settings.py
CSRF_TRUSTED_ORIGINS = ['https://your-domain.com']
```

## ✅ **Success Criteria**

Your deployment is successful when:
- ✅ App loads at your public URL
- ✅ Login works with test credentials
- ✅ Dashboard shows mock data
- ✅ Client-caregiver relationships display
- ✅ Static files (CSS/JS) load properly
- ✅ No console errors in browser

## 🎯 **Recommended: Railway Deployment**

**Why Railway is perfect for your healthcare app:**
- **1-click PostgreSQL** database provisioning
- **Automatic HTTPS** and domain
- **Environment variables** management
- **GitHub integration** for auto-deploy
- **$5/month** production pricing
- **Built-in monitoring** and logs

**Deploy in 30 seconds:**
```bash
railway login && railway deploy
```

Your WeCarePortal will be live with all mock data! 🏥🚀