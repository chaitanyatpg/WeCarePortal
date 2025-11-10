# 🚂 Railway Environment Variables Setup

## 🔐 **REQUIRED Environment Variables**

Copy these into your Railway dashboard after deployment:

### **1. Django Secret Key**
```
SECRET_KEY=your-new-super-secret-key-here-make-it-long-and-random
```
**⚠️ Generate a new one:** https://djecrety.ir/

### **2. Debug Setting**
```
DEBUG=False
```

### **3. Domain Configuration**
```
ALLOWED_HOSTS=your-app-name.railway.app,*.railway.app
```
*Railway will auto-provide your domain*

---

## 📧 **OPTIONAL: Email Configuration (SendGrid)**

Only add these if you want email functionality:

```
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
```

---

## ☁️ **OPTIONAL: AWS S3 Configuration**

Only add these if you want to use AWS S3 for file storage:

```
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

---

## 🎯 **Railway Setup Steps**

### **Step 1: Initial Deployment**
```bash
# Railway automatically detects and deploys Django apps
# No environment variables needed for initial deployment
```

### **Step 2: PostgreSQL Database Configuration**
**Database URLs for this deployment:**
```bash
# Public Database URL (for external connections):
DATABASE_URL=postgresql://postgres:cGxXsRPAXiFqnzBkHaCLJlTFsRuHpPgY@maglev.proxy.rlwy.net:16226/railway

# Internal Database URL (for Railway services):
DATABASE_URL=postgresql://postgres:cGxXsRPAXiFqnzBkHaCLJlTFsRuHpPgY@postgres.railway.internal:5432/railway
```

### **Step 3: Set Environment Variables**
In Railway dashboard, go to your app → Variables tab:

**REQUIRED:**
- `SECRET_KEY` = `your-new-secret-key`
- `DEBUG` = `False`

**That's it!** Railway auto-provides `DATABASE_URL`

### **Step 4: Deploy & Test**
```bash
# Railway automatically:
# 1. Runs migrations
# 2. Loads mock data  
# 3. Starts your app
```

---

## 🧪 **Test Your Deployment**

After Railway deploys, test these URLs:

1. **App Home:** `https://your-app.railway.app`
2. **Admin Login:** `https://your-app.railway.app/admin`
3. **Care Manager:** Login with `sarah.johnson / password123`
4. **Caregiver:** Login with `emma.davis / password123`

---

## 🚨 **Important Notes**

- **PostgreSQL:** Railway auto-provisions and connects
- **Static Files:** Automatically served by Django  
- **Mock Data:** Loads automatically on first deployment
- **SSL/HTTPS:** Railway provides automatically
- **Domain:** Get free .railway.app subdomain

---

## 🎉 **You're Ready!**

Your Railway environment is configured for:
✅ **10 test users** ready to login  
✅ **9 clients** with medical profiles  
✅ **18 caregiver schedules**  
✅ **2 healthcare providers**  
✅ **Full multi-company setup**  

Just deploy and start testing! 🚀