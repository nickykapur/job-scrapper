# 🚂 Railway Database Setup Guide

Transform your LinkedIn Job Manager from JSON files to a proper PostgreSQL database!

## 🎯 What This Achieves

✅ **Persistent Applied Job Status** - Never lose your job applications again  
✅ **Better Performance** - Real database queries vs JSON file parsing  
✅ **Cloud Storage** - Data survives Railway deployments  
✅ **Scalability** - Handle thousands of jobs efficiently  
✅ **Local ↔ Cloud Sync** - Run scraper locally, sync to Railway  

---

## 📋 Step 1: Create PostgreSQL Database on Railway

### 1.1 Add PostgreSQL Service
1. Go to your Railway project dashboard
2. Click **"+ New Service"**
3. Select **"Add Database"** → **"PostgreSQL"**
4. Railway will provision your database (takes ~30 seconds)

### 1.2 Get Database Connection URL
1. Click on your new **PostgreSQL service**
2. Go to **"Variables"** tab
3. Copy the `DATABASE_URL` - it looks like:
   ```
   postgresql://postgres:password@host:port/railway
   ```

### 1.3 Add Database URL to Your App
1. Go to your **main app service** (not the database)
2. Go to **"Variables"** tab  
3. Add new variable:
   - **Name**: `DATABASE_URL`
   - **Value**: Paste the connection URL from step 1.2

---

## 📋 Step 2: Initialize Database Schema

### 2.1 Connect to Database (Option A - Railway Console)
1. In your PostgreSQL service, click **"Data"** tab
2. Click **"Connect"** 
3. Copy and paste the contents of `database_setup.sql`:

```sql
-- PostgreSQL Database Setup for LinkedIn Job Manager
CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(300) NOT NULL,
    location VARCHAR(300),
    posted_date VARCHAR(100),
    job_url TEXT NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    applied BOOLEAN DEFAULT FALSE,
    is_new BOOLEAN DEFAULT FALSE,
    category VARCHAR(50),
    notes TEXT,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen_24h TIMESTAMP WITH TIME ZONE,
    excluded BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_applied ON jobs(applied);
CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);

-- Create scraping sessions table
CREATE TABLE IF NOT EXISTS scraping_sessions (
    id SERIAL PRIMARY KEY,
    session_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_jobs_found INTEGER DEFAULT 0,
    new_jobs_count INTEGER DEFAULT 0,
    updated_jobs_count INTEGER DEFAULT 0,
    search_terms TEXT[],
    success BOOLEAN DEFAULT TRUE,
    notes TEXT
);
```

### 2.2 Connect via Command Line (Option B)
If you have `psql` installed:
```bash
psql "postgresql://postgres:password@host:port/railway" -f database_setup.sql
```

---

## 📋 Step 3: Deploy Updated Code

### 3.1 Commit Database Changes
```bash
cd /mnt/c/Users/nicky/OneDrive/Escritorio/Projects/python-job/job-scrapper

# Add all the new database files
git add database_setup.sql
git add database_models.py  
git add sync_to_railway.py
git add requirements-fastapi.txt
git add fastapi_server.py
git add RAILWAY_DATABASE_SETUP.md

# Commit changes
git commit -m "Add PostgreSQL database support

- Add database models and connection handling
- Update FastAPI server to use PostgreSQL/JSON fallback
- Add sync utility for local scraper → Railway database  
- Preserve applied job status across scraper runs
- Add database schema and setup instructions

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to Railway
git push origin main
```

### 3.2 Wait for Deployment
- Railway will automatically rebuild with database support
- Check deployment logs for any errors
- Your app will fallback to JSON if PostgreSQL isn't connected

---

## 📋 Step 4: Test Database Connection

### 4.1 Check Health Endpoint
Visit: `https://your-app.railway.app/api/health`

You should see database info in the response.

### 4.2 Verify Jobs Load
Visit: `https://your-app.railway.app/jobs_database.json`

Should show `"database_type": "postgresql"` in metadata.

---

## 📋 Step 5: Sync Your Existing Jobs

### 5.1 Import Current Jobs to Database
Run this locally to import your existing jobs:

```bash
# Set your Railway app URL
export RAILWAY_URL=https://your-app.railway.app

# Sync current jobs to PostgreSQL  
python sync_to_railway.py
```

### 5.2 Verify Import
- Check your Railway app - should show all your jobs
- Applied statuses should be preserved
- Database metadata should show correct counts

---

## 🔄 Daily Workflow (New Process)

### Old Workflow:
```bash
python daily_dublin_update.py  # Updates JSON file
# Jobs lost on Railway deployment
# Applied status lost on re-scraping
```

### New Workflow:
```bash
# 1. Run scraper locally (as usual)
python daily_dublin_update.py

# 2. Sync to Railway database  
python sync_to_railway.py https://your-app.railway.app

# 3. Check Railway app for updated jobs
# 4. Applied statuses preserved forever!
```

---

## 💰 Costs

- **PostgreSQL**: $5/month for 1GB storage
- **Your current Railway app**: Still free/existing pricing
- **Total additional cost**: $5/month

**Value**: Professional job tracking, persistent applied status, scalable architecture

---

## 🔧 Advanced Features

### Database Queries
You can now run SQL queries on your jobs:

```sql
-- Most active companies
SELECT company, COUNT(*) as job_count 
FROM jobs 
GROUP BY company 
ORDER BY job_count DESC;

-- Applied job statistics  
SELECT 
    COUNT(*) as total_jobs,
    COUNT(*) FILTER (WHERE applied = TRUE) as applied_jobs,
    COUNT(*) FILTER (WHERE location ILIKE '%dublin%') as dublin_jobs
FROM jobs;

-- Recent activity
SELECT * FROM jobs 
WHERE scraped_at > NOW() - INTERVAL '24 hours'
ORDER BY scraped_at DESC;
```

### API Endpoints
- `GET /jobs_database.json` - Get all jobs (PostgreSQL or JSON fallback)
- `POST /update_job` - Update applied status (persisted in PostgreSQL)
- `POST /sync_jobs` - Sync jobs from local scraper
- `GET /api/health` - Check database connection status

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check if DATABASE_URL is set correctly
curl https://your-app.railway.app/api/health
```

### Fallback Mode
If PostgreSQL fails, the app automatically falls back to JSON files - no downtime!

### Local Sync Issues
```bash
# Test connection
curl -X POST https://your-app.railway.app/sync_jobs \
  -H "Content-Type: application/json" \
  -d '{"jobs_data": {"test": "data"}}'
```

---

## 🎉 Success!

After setup, you'll have:

✅ **Professional database** instead of JSON files  
✅ **Persistent applied status** that survives everything  
✅ **Local scraping** with cloud sync  
✅ **Scalable architecture** for future features  
✅ **Zero downtime** with automatic fallback  

Your LinkedIn Job Manager is now enterprise-grade! 🚀