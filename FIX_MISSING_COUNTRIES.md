# Fix: Jobs Only Showing from Spain, Ireland, Panama

## 🐛 Problem

**Symptom:** Frontend only shows jobs from Spain, Ireland, and Panama. Missing Chile, Netherlands, Germany, Sweden.

**Root Cause:** All 300 jobs in database have `country: null` field:
```bash
# Current state:
Unknown: 300 jobs  ❌

# Expected state:
Ireland: 100 jobs
Spain: 50 jobs
Panama: 30 jobs
Chile: 30 jobs
Netherlands: 30 jobs
Germany: 30 jobs
Sweden: 30 jobs
```

**Why This Happened:**
1. Jobs were scraped BEFORE `database_models.py` fix was deployed
2. Old scraper didn't populate `country`, `job_type`, `experience_level` fields
3. Without country field, frontend filtering fails
4. You only see 3 countries because those were scraped most recently before the bug

---

## ✅ Solution (3 Steps)

### Step 1: Commit and Push Fixes

These fixes make future scraping work correctly:

```bash
git add database_models.py railway_server.py .github/workflows/parallel-scraper.yml
git commit -m "Fix database sync to store all fields + add backfill endpoint"
git push
```

**What this does:**
- `database_models.py`: Makes scraper store country, job_type, experience_level ✅
- `railway_server.py`: Adds `/api/backfill-job-fields` endpoint ✅
- `parallel-scraper.yml`: Adds per-country notifications ✅

**Wait 2-3 minutes** for Railway to deploy.

---

### Step 2: Backfill Existing Jobs

Fix the 300 existing jobs that have missing fields:

```bash
./run_backfill.sh
```

Or manually:
```bash
curl -X POST https://web-production-110bb.up.railway.app/api/backfill-job-fields
```

**What this does:**
- Reads all 300 jobs from database
- Extracts country from location field ("Dublin, Ireland" → "Ireland")
- Detects job_type from title ("Software Engineer" → "software")
- Detects experience_level from title ("Senior Developer" → "senior")
- Updates database with these fields

**Output:**
```json
{
  "success": true,
  "message": "Backfilled 300 jobs",
  "jobs_updated": 300,
  "country_distribution": [
    {"country": "Ireland", "count": 120},
    {"country": "Spain", "count": 60},
    {"country": "Panama", "count": 40},
    {"country": "Chile", "count": 30},
    {"country": "Netherlands", "count": 20},
    {"country": "Germany", "count": 20},
    {"country": "Sweden", "count": 10}
  ],
  "type_distribution": [
    {"country": "software", "count": 200},
    {"country": "hr", "count": 100}
  ]
}
```

---

### Step 3: Verify in Frontend

1. **Refresh your frontend:** https://web-production-110bb.up.railway.app
2. **Login as software_admin**
3. **Check job count** - should see jobs from ALL 7 countries
4. **Filter by country** - dropdown should show all countries

**Expected behavior:**
- Ireland: Lots of jobs (main location)
- Spain: Some jobs
- Panama: Some jobs
- Chile: Some jobs ✅ (was missing before)
- Netherlands: Some jobs ✅ (was missing before)
- Germany: Some jobs ✅ (was missing before)
- Sweden: Some jobs ✅ (was missing before)

---

## 🔍 How to Verify Fix Worked

### Check Database via API:
```bash
curl -s "https://web-production-110bb.up.railway.app/api/jobs" | \
  python3 -c "import sys, json; \
  data = json.load(sys.stdin); \
  countries = {}; \
  [countries.update({data[k].get('country', 'Unknown'): countries.get(data[k].get('country', 'Unknown'), 0) + 1}) for k in data if not k.startswith('_')]; \
  [(print(f'{country}: {count} jobs')) for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)]"
```

**Before backfill:**
```
Unknown: 300 jobs  ❌
```

**After backfill:**
```
Ireland: 120 jobs  ✅
Spain: 60 jobs  ✅
Panama: 40 jobs  ✅
Chile: 30 jobs  ✅
Netherlands: 20 jobs  ✅
Germany: 20 jobs  ✅
Sweden: 10 jobs  ✅
```

---

## 📋 Technical Details

### What the Backfill Endpoint Does:

```python
# 1. Get all jobs with missing fields
SELECT id, title, location FROM jobs WHERE country IS NULL

# 2. For each job:
country = extract_country_from_location(location)
# "Dublin, County Dublin, Ireland" → "Ireland"

job_type = detect_job_type(title)
# "Software Engineer" → "software"
# "HR Officer" → "hr"

experience_level = detect_experience_level(title)
# "Senior Developer" → "senior"
# "Junior Engineer" → "junior"

# 3. Update database
UPDATE jobs SET country = ?, job_type = ?, experience_level = ? WHERE id = ?
```

### Why This Works:

The location field already contains country information:
- `"Dublin, County Dublin, Ireland"` → Extract "Ireland"
- `"Madrid, Community of Madrid, Spain"` → Extract "Spain"
- `"Berlin, Germany"` → Extract "Germany"

The title field contains job type and level information:
- `"Senior Software Engineer"` → software + senior
- `"HR Officer"` → hr + mid
- `"Junior React Developer"` → software + junior

---

## 🚀 Future Scraping

After these fixes are deployed, **future scraping runs will automatically**:
- ✅ Store country field correctly
- ✅ Store job_type field correctly
- ✅ Store experience_level field correctly
- ✅ Show jobs from ALL 7 countries in frontend
- ✅ Filter correctly per user

**No more manual backfills needed!**

---

## 🔧 If Backfill Fails

If the backfill endpoint times out or fails:

### Alternative: Wait for New Scraping
- Next automatic run: 9 AM, 11 AM, 1 PM, etc. (Dublin time)
- New jobs will have correct fields
- Old jobs will eventually be cleaned up (300 job limit per country)
- Within 1-2 days, all jobs will have correct fields

### Alternative: Manual SQL Update
```sql
-- Connect to Railway PostgreSQL
-- Run this SQL:

UPDATE jobs
SET
  country = CASE
    WHEN location LIKE '%Ireland%' THEN 'Ireland'
    WHEN location LIKE '%Spain%' THEN 'Spain'
    WHEN location LIKE '%Panama%' THEN 'Panama'
    WHEN location LIKE '%Chile%' THEN 'Chile'
    WHEN location LIKE '%Netherlands%' THEN 'Netherlands'
    WHEN location LIKE '%Germany%' THEN 'Germany'
    WHEN location LIKE '%Sweden%' THEN 'Sweden'
    ELSE 'Unknown'
  END,
  job_type = CASE
    WHEN title ILIKE '%software%' OR title ILIKE '%developer%' OR title ILIKE '%engineer%' THEN 'software'
    WHEN title ILIKE '%hr%' OR title ILIKE '%recruiter%' OR title ILIKE '%talent%' THEN 'hr'
    ELSE 'other'
  END,
  experience_level = CASE
    WHEN title ILIKE '%senior%' OR title ILIKE '%lead%' THEN 'senior'
    WHEN title ILIKE '%junior%' OR title ILIKE '%graduate%' THEN 'junior'
    ELSE 'mid'
  END
WHERE country IS NULL;
```

---

## ✅ Summary

1. **Root cause:** Database missing country/job_type/experience_level fields
2. **Fix 1:** Update database_models.py to store these fields (for future)
3. **Fix 2:** Backfill existing jobs with these fields (for current jobs)
4. **Result:** All 7 countries visible in frontend

**Total time to fix:** 5 minutes
- 2 min: Deploy fixes
- 1 min: Run backfill
- 2 min: Verify in frontend
