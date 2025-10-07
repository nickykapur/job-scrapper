# 🚀 Deployment Checklist - Easy Apply & 300 Jobs Limit

## ✅ What's Already Done

### Backend (Scraper)
- ✅ Easy Apply detection implemented in `linkedin_job_scraper.py`
- ✅ 300 jobs per country limit in `daily_multi_country_update.py`
- ✅ Database schema updated in `database_setup.sql`
- ✅ Migration scripts created

### Frontend (UI)
- ✅ Easy Apply field added to types (`types.ts`)
- ✅ Easy Apply badge in JobCard component
- ✅ Easy Apply chip in JobTable component
- ✅ Country/Category columns removed from table
- ✅ Spain city breakdown removed
- ✅ Countries always visible (even with 0 jobs)

### GitHub Actions
- ✅ Workflow configured to run 7x daily
- ✅ Automatically syncs to Railway

---

## 🔧 What You Need To Do

### Step 1: Update Railway Database Schema

**Add the `easy_apply` column to your existing database:**

```bash
# Connect to Railway PostgreSQL
psql $DATABASE_URL -f add_easy_apply_column.sql
```

This will:
- Add `easy_apply BOOLEAN DEFAULT FALSE` column
- Create index for performance
- Set all existing jobs to `easy_apply = false`

**Verify it worked:**
```sql
-- Check column exists
\d jobs

-- Should see: easy_apply | boolean | | default false
```

---

### Step 2: Optional - Clean Up Old Jobs

**If you have more than 300 jobs per country:**

```bash
psql $DATABASE_URL -f cleanup_old_jobs.sql
```

This will:
- Keep only 300 most recent jobs per country
- Delete older jobs
- Show statistics after cleanup

---

### Step 3: Rebuild and Deploy Frontend

```bash
cd job-manager-ui

# Install dependencies (if needed)
npm install

# Build for production
npm run build

# Deploy to your hosting (Railway/Vercel/etc)
# The exact command depends on your setup
```

---

### Step 4: Test The Scraper Locally (Optional)

**Test Easy Apply detection:**

```bash
python linkedin_job_scraper.py
```

Look for output like:
```
⚡ Easy Apply: 15
```

**Test 300 limit:**

```bash
python daily_multi_country_update.py
```

Look for output like:
```
✂️ Applying 300 jobs per country limit...
   ✂️ Spain: Trimmed to 300 most recent jobs (removed 50 old jobs)
🗑️ Removed 50 old jobs total to maintain 300 jobs per country limit
```

---

### Step 5: Wait for Next GitHub Action Run

The scraper runs automatically at:
- 9 AM, 11 AM, 1 PM, 3 PM, 4 PM, 6 PM, 8 PM (Dublin time)

Or trigger manually:
1. Go to GitHub → Actions tab
2. Select "Daily Multi-Country Job Scraper"
3. Click "Run workflow"

---

## 🔍 How to Verify It's Working

### Check Scraper Logs:
```
✅ Jobs loaded successfully: 450 jobs
⚡ Easy Apply: 85
✂️ Applying 300 jobs per country limit...
   ✂️ Ireland: 120 jobs (no trim needed)
   ✂️ Spain: Trimmed to 300 most recent jobs (removed 87 old jobs)
🗑️ Removed 87 old jobs total
```

### Check Database:
```sql
-- Count jobs with Easy Apply
SELECT country, COUNT(*) as total, COUNT(*) FILTER (WHERE easy_apply = true) as easy_apply_count
FROM jobs
GROUP BY country;

-- Expected output:
-- Ireland  | 120 | 25
-- Spain    | 300 | 45
-- Germany  | 95  | 12
-- UK       | 210 | 38

-- Check jobs per country don't exceed 300
SELECT country, COUNT(*) as job_count
FROM jobs
GROUP BY country
HAVING COUNT(*) > 300;

-- Should return 0 rows
```

### Check Frontend UI:
1. Open your job manager UI
2. Look for green ⚡ "Easy Apply" badges on job cards
3. In table view, look for "Easy Apply" chips next to job titles
4. Verify Spain doesn't show city breakdown anymore
5. Verify categories tabs are all visible (even with 0 jobs)

---

## 🐛 Troubleshooting

### "Easy Apply not showing in UI"

**Cause:** Database doesn't have `easy_apply` column yet

**Fix:**
```bash
psql $DATABASE_URL -f add_easy_apply_column.sql
```

### "Still seeing old jobs (>300 per country)"

**Cause:** Cleanup hasn't run yet

**Fix:**
```bash
# Manual cleanup
psql $DATABASE_URL -f cleanup_old_jobs.sql

# OR wait for next scraper run (it will auto-limit)
```

### "Easy Apply count is 0"

**Cause:**
1. LinkedIn changed their HTML structure
2. Jobs don't have Easy Apply feature
3. Scraper not detecting correctly

**Fix:**
1. Check scraper logs for detection attempts
2. Manually verify some jobs have Easy Apply on LinkedIn
3. Update selectors in `detect_easy_apply()` if needed

### "Countries showing 'Unknown'"

**Cause:** Jobs don't have `country` field populated

**Fix:** This is expected for old jobs. New jobs scraped will have country field.

---

## 📊 Expected Results

After deployment, you should see:

**Per Country:**
- Maximum 300 jobs
- Sorted by most recent `scraped_at`
- Easy Apply count visible

**In UI:**
- ⚡ Green "Easy Apply" badges on applicable jobs
- Clean country-level aggregation (no city breakdown)
- All 4 countries always visible in tabs
- Simpler table (no Category/Country columns)

**In Database:**
- `easy_apply` column exists
- Jobs have `scraped_at` timestamp
- Maximum 300 rows per country

---

## 🎯 Quick Start Command

**Do everything in one go:**

```bash
# 1. Update database schema
psql $DATABASE_URL -f add_easy_apply_column.sql

# 2. Clean up old jobs
psql $DATABASE_URL -f cleanup_old_jobs.sql

# 3. Rebuild frontend
cd job-manager-ui && npm run build

# 4. Trigger GitHub Action (or wait for scheduled run)
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

---

## ✨ Summary

| Feature | Status | Location |
|---------|--------|----------|
| Easy Apply Detection | ✅ Implemented | `linkedin_job_scraper.py:358` |
| Easy Apply UI | ✅ Implemented | `JobCard.tsx:108`, `JobTable.tsx:282` |
| 300 Jobs Limit | ✅ Implemented | `daily_multi_country_update.py:352` |
| DB Schema | ⚠️ **NEEDS MIGRATION** | Run `add_easy_apply_column.sql` |
| UI Build | ⚠️ **NEEDS REBUILD** | Run `npm run build` |

**Once you run the migrations, everything will work automatically!** 🚀
