# 🚀 Step-by-Step Railway Deployment Guide

## 📋 Prerequisites
- ✅ GitHub account
- ✅ Railway account (free signup)
- ✅ Your code pushed to GitHub

---

## 🧹 **STEP 1: Cleanup Project Structure**

### **Files to Remove Before Deployment:**

Run these commands in your project directory:

```bash
# Navigate to your project
cd /your/project/path

# Remove old files we don't need
rm job_manager.html          # Old HTML interface
rm web_server.py            # Old Python server  
rm start_ui.py              # Old launcher
rm debug_selectors.py       # Debug tool
rm fix_job_data.py          # One-time script
rm cleanup_applied_jobs.py  # One-time script
rm linkedin_jobs.json       # Old data format
rm applied_jobs_backup_*.json # Backup files
rm google-chrome-stable_current_amd64.deb # Installer
rm -rf venv/                # Virtual environment
rm -rf netlify/             # Netlify specific
rm -rf functions/           # Netlify functions
rm netlify.toml             # Netlify config
rm lighthouserc.json        # Testing config

# Check if there are nested folders to clean up
ls -la
```

### **Final Clean Structure Should Be:**
```
python-job/
├── job-scrapper/                    # Main backend folder
│   ├── fastapi_server.py           # ✅ Main server
│   ├── linkedin_job_scraper.py     # ✅ Scraper
│   ├── main.py                     # ✅ CLI
│   ├── jobs_database.json          # ✅ Data
│   ├── requirements-fastapi.txt    # ✅ Dependencies
│   └── job-manager-ui/             # ✅ React frontend
│       ├── src/
│       ├── package.json
│       └── ...
├── railway.toml                    # ✅ Railway config
├── Procfile                       # ✅ Process file
└── README.md                      # ✅ Documentation
```

---

## 🚂 **STEP 2: Deploy to Railway**

### **Option A: Deploy via Railway Dashboard (Recommended)**

1. **Sign Up for Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Sign up with GitHub (free)

2. **Create New Project:**
   - Click "Deploy from GitHub repo"
   - Connect your GitHub account
   - Select your `python-job` repository
   - Click "Deploy Now"

3. **Railway Auto-Detection:**
   Railway will automatically detect:
   - ✅ Python backend (FastAPI)
   - ✅ Node.js frontend (React)
   - ✅ Build configuration

### **Option B: Deploy via Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

---

## ⚙️ **STEP 3: Configure Environment Variables**

In Railway Dashboard:

1. **Go to your project**
2. **Click "Variables" tab**
3. **Add these variables:**

```bash
# Required Variables:
NODE_ENV=production
PORT=8000
PYTHONPATH=/app

# Optional Variables:
REACT_APP_API_URL=${{RAILWAY_STATIC_URL}}
LOCATION="Dublin, County Dublin, Ireland"
```

**Railway automatically provides:**
- `RAILWAY_STATIC_URL` - Your app's public URL
- `PORT` - The port to run on

---

## 🔧 **STEP 4: Build Configuration**

Railway should automatically use your `railway.toml` config:

```toml
[build]
builder = "nixpacks"
buildCommand = "cd job-manager-ui && npm install && npm run build && cd .. && pip install -r requirements-fastapi.txt"

[deploy]
startCommand = "python fastapi_server.py"
```

If it doesn't work, manually set:
- **Build Command:** `cd job-manager-ui && npm install && npm run build && cd .. && pip install -r requirements-fastapi.txt`  
- **Start Command:** `python fastapi_server.py`

---

## 📱 **STEP 5: Monitor Deployment**

### **Deployment Logs:**
1. Go to Railway dashboard
2. Click on your project
3. Click "Deployments" tab
4. View real-time logs

### **Common Build Issues & Fixes:**

#### **Issue 1: Python Dependencies**
```bash
# If build fails on Python packages
# Check requirements-fastapi.txt exists and contains:
fastapi==0.104.1
uvicorn[standard]==0.24.0
selenium==4.15.2
beautifulsoup4==4.12.2
requests==2.31.0
webdriver-manager==4.0.1
```

#### **Issue 2: Node.js Build Fails**
```bash
# If React build fails
# Check job-manager-ui/package.json has correct scripts:
"scripts": {
  "dev": "vite",
  "build": "tsc && vite build",
  "preview": "vite preview"
}
```

#### **Issue 3: File Paths**
```bash
# Make sure your file structure matches:
# Railway looks for fastapi_server.py in root of repo
# If it's in job-scrapper/ folder, update railway.toml:
startCommand = "cd job-scrapper && python fastapi_server.py"
```

---

## ✅ **STEP 6: Test Your Deployment**

### **Your app will be available at:**
```
https://your-app-name.up.railway.app
```

### **Test these URLs:**
1. **Main App:** `https://your-app.railway.app`
2. **Health Check:** `https://your-app.railway.app/api/health`
3. **API Docs:** `https://your-app.railway.app/docs`
4. **Jobs Data:** `https://your-app.railway.app/jobs_database.json`

### **Test Features:**
- ✅ React UI loads
- ✅ Job list displays
- ✅ Mark as applied works
- ✅ Search functionality works  
- ✅ Company exclusion works
- ✅ Data persists between visits

---

## 🎯 **STEP 7: Setup Automatic Deployments**

### **Enable GitHub Integration:**
1. In Railway dashboard
2. Go to Settings → GitHub
3. Enable "Auto-Deploy"
4. Select branch: `main`

**Now every `git push` to main will auto-deploy! 🎉**

---

## 💰 **STEP 8: Monitor Usage & Costs**

### **Check Usage:**
1. Railway Dashboard → Your Project
2. Click "Usage" tab
3. Monitor CPU, RAM, Network usage

### **Expected Monthly Cost:**
- **Light Usage:** $5/month (covered by $5 credit)
- **Regular Usage:** $5-6/month  
- **Heavy Usage:** $7-10/month

### **Cost Optimization:**
- ✅ App auto-scales to zero when not used
- ✅ Only pay for active usage
- ✅ Set spending limits in settings

---

## 🚨 **Troubleshooting**

### **Deployment Fails:**
1. **Check build logs** in Railway dashboard
2. **Verify file paths** - make sure files are in correct location
3. **Check dependencies** - ensure all packages are listed
4. **Test locally first** - run `python fastapi_server.py` locally

### **App Doesn't Start:**
1. **Check start command** - verify `python fastapi_server.py` works
2. **Check port binding** - ensure app uses `PORT` environment variable
3. **Check file permissions** - ensure files are readable

### **Scraping Doesn't Work:**
1. **Check Chrome installation** - Railway should auto-install
2. **Check headless mode** - ensure `--headless` flag is used
3. **Check timeouts** - increase timeout values if needed

### **Frontend Not Loading:**
1. **Check build output** - ensure React app builds successfully  
2. **Check static file serving** - verify `job-manager-ui/dist` exists
3. **Check CORS settings** - ensure frontend can call backend APIs

---

## 🎉 **Success! Your Job Manager is Live!**

### **What You Now Have:**
- ✅ **Professional hosting** on Railway
- ✅ **Automatic deployments** from GitHub
- ✅ **Full Python backend** with Selenium scraping
- ✅ **Modern React frontend** with Material-UI
- ✅ **Custom domain** (yourapp.railway.app)
- ✅ **SSL certificate** (HTTPS)
- ✅ **24/7 uptime** monitoring

### **Share Your App:**
```bash
🌐 Your Job Manager: https://yourapp.railway.app
📊 API Documentation: https://yourapp.railway.app/docs  
💰 Monthly Cost: ~$5 (incredible value!)
```

---

## 📞 **Need Help?**

### **Railway Support:**
- [Railway Discord](https://discord.gg/railway)  
- [Railway Docs](https://docs.railway.app)
- [Railway Help Center](https://help.railway.com)

### **Common Commands:**
```bash
# View logs
railway logs

# Open app in browser  
railway open

# Check service status
railway status

# Redeploy
railway up --detach
```

**You're now running a professional job management platform! 🚀**