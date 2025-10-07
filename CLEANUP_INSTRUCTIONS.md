# 🧹 Database Cleanup Instructions

## Current State:
- 🇬🇧 **United Kingdom**: 1000+ jobs (need to remove ~700)
- 🇪🇸 **Spain**: 900 jobs (need to remove ~600)
- 🇩🇪 **Germany**: 310 jobs (need to remove ~10)
- 🇮🇪 **Ireland**: ? jobs

**Total jobs to delete**: ~1,310+ old jobs

---

## 🚀 Quick Fix (Run These Commands):

### Option 1: Automated Script (Recommended)

```bash
cd /mnt/c/Users/nicky/OneDrive/Escritorio/Projects/python-job/job-scrapper

# Set your Railway database URL
export DATABASE_URL='your_railway_postgres_connection_string'

# Run the migration script
bash run_database_migrations.sh
```

This will:
1. ✅ Add `easy_apply` column
2. ✅ Delete old jobs (keep 300 newest per country)
3. ✅ Show verification stats

---

### Option 2: Manual Commands

```bash
# Set your Railway database URL
export DATABASE_URL='your_railway_postgres_connection_string'

# Step 1: Add easy_apply column
psql "$DATABASE_URL" -f add_easy_apply_column.sql

# Step 2: Clean up to 300 jobs per country
psql "$DATABASE_URL" -f cleanup_database_300_limit.sql

# Step 3: Verify
psql "$DATABASE_URL" -c "
  SELECT country, COUNT(*) as jobs
  FROM jobs
  GROUP BY country
  ORDER BY jobs DESC;
"
```

---

## 📊 What Will Happen:

### Before Cleanup:
```
United Kingdom: 1000+ jobs
Spain:          900 jobs
Germany:        310 jobs
Ireland:        ? jobs
───────────────────────────
Total:          2200+ jobs ❌
```

### After Cleanup:
```
United Kingdom: 300 jobs ✅
Spain:          300 jobs ✅
Germany:        300 jobs ✅
Ireland:        300 jobs ✅
───────────────────────────
Total:          ~1200 jobs ✅
```

**Jobs deleted**: ~1,000+ old entries

---

## 🔍 How It Chooses Which Jobs to Keep:

The script keeps the **300 most recent jobs** per country based on `scraped_at` timestamp:

```sql
-- Example for UK
SELECT id, title, scraped_at
FROM jobs
WHERE country = 'United Kingdom'
ORDER BY scraped_at DESC  -- Most recent first
LIMIT 300;                -- Keep these
-- Delete the rest
```

So you'll keep:
- ✅ The freshest job listings
- ✅ Most recently scraped jobs
- ✅ Jobs with latest timestamps

You'll delete:
- ❌ Old job listings (no longer relevant)
- ❌ Jobs scraped weeks ago
- ❌ Stale opportunities

---

## ⚠️ Safety Features:

The cleanup script:
1. **Uses transaction (BEGIN/COMMIT)** - Can rollback if something goes wrong
2. **Shows BEFORE counts** - See what you have before deletion
3. **Shows AFTER counts** - Verify 300 limit was applied
4. **Shows date ranges** - See oldest and newest job kept
5. **Asks for confirmation** - Won't delete without your approval

---

## 🎯 Why This Is Important:

### Database Performance:
- **Before**: 2200+ rows → Slow queries
- **After**: 1200 rows → Fast queries ⚡

### UI Performance:
- **Before**: Loading 2200+ jobs → UI lag
- **After**: Loading 1200 jobs → Smooth UI 🚀

### Data Freshness:
- **Before**: Jobs from weeks ago (already filled)
- **After**: Only recent jobs (still available) 📅

### Cost:
- **Before**: Larger database → Higher Railway costs
- **After**: Optimized size → Lower costs 💰

---

## 🔧 Troubleshooting:

### "ERROR: column 'easy_apply' already exists"
**Solution**: This is OK! It means the column was already added. Continue to cleanup.

### "ERROR: column 'scraped_at' does not exist"
**Solution**: Your jobs don't have timestamps. Run:
```sql
ALTER TABLE jobs ADD COLUMN scraped_at TIMESTAMP DEFAULT NOW();
UPDATE jobs SET scraped_at = NOW() WHERE scraped_at IS NULL;
```

### "ERROR: relation 'jobs' does not exist"
**Solution**: Wrong database or table name. Check your DATABASE_URL.

---

## ✅ Verification After Cleanup:

```bash
# Check job counts
psql "$DATABASE_URL" -c "
  SELECT
    country,
    COUNT(*) as total_jobs,
    MAX(scraped_at) as newest,
    MIN(scraped_at) as oldest
  FROM jobs
  GROUP BY country;
"

# Should show:
# United Kingdom | 300 | 2025-01-07 | 2025-01-05
# Spain          | 300 | 2025-01-07 | 2025-01-05
# Germany        | 300 | 2025-01-07 | 2025-01-06
# Ireland        | 300 | 2025-01-07 | 2025-01-06
```

All countries should have ≤ 300 jobs! ✅

---

## 📝 After Cleanup:

1. **Rebuild Frontend**:
```bash
cd job-manager-ui
npm run build
```

2. **Trigger GitHub Action** (or wait for scheduled run):
- Go to: GitHub → Actions → Daily Multi-Country Job Scraper
- Click: "Run workflow"

3. **Check Logs** for:
```
✂️ Applying 300 jobs per country limit...
   ✅ Ireland: 120 jobs (no trim needed)
   ✅ Spain: 295 jobs (no trim needed)
   ✅ Germany: 180 jobs (no trim needed)
   ✅ United Kingdom: 285 jobs (no trim needed)
```

4. **Check UI** for:
- ⚡ Green "Easy Apply" badges
- Clean country tabs
- Faster load times

---

## 🆘 Need Help?

If something goes wrong, you can restore from Railway backup:
1. Go to Railway Dashboard
2. Select your database
3. Click "Backups" tab
4. Restore to before cleanup

---

## 🎉 Expected Result:

After running cleanup:
- ✅ Database: 1,200 jobs (300 per country)
- ✅ All jobs have `easy_apply` column
- ✅ UI shows Easy Apply badges
- ✅ Countries capped at 300 jobs
- ✅ Faster performance
- ✅ Lower costs

**Total deletion**: ~1,000 old jobs (47% reduction) 📉

Ready to clean? Run:
```bash
bash run_database_migrations.sh
```
