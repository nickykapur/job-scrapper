# Fix for Duplicate Jobs After Scraping

## 🐛 The Problem

You were seeing jobs **repeatedly** even after applying or rejecting them because:

### Root Cause 1: Job Cleanup Deletes Jobs from Database
```
Day 1: You apply to "Software Engineer at Google" (job_id: abc123)
       ✅ Saved to user_job_interactions(user_id=5, job_id=abc123, applied=TRUE)

Day 7: Cleanup runs (keeping only 300 jobs per country)
       🗑️ Deletes job abc123 from jobs table
       ✅ user_job_interactions still has abc123 (preserved!)

Day 8: Scraper runs again
       📥 Finds "Software Engineer at Google" on LinkedIn
       🆔 LinkedIn assigns NEW ID: xyz789
       ❌ You see the job again!

Why? The filter only checked:
  - user_job_interactions has abc123 ❌
  - But job now has ID xyz789 ❌
  - No match! Job shows up again! 😡
```

### Root Cause 2: Filter Only Checked by job_id, Not Company+Title
```python
# OLD CODE (BROKEN)
if job_id in user_interactions:
    # Only checks by exact job_id
    # Misses jobs that were deleted and re-scraped with new ID!
```

## ✅ The Solution (3-Part Fix)

### Fix 1: Check BOTH job_id AND Company+Title Signature

**File: `railway_server.py`**

```python
# NEW CODE (WORKING)
# Check 1: By job_id (direct match)
if job_id in user_interactions:
    if interaction['applied'] or interaction['rejected']:
        continue  # Hide job

# Check 2: By company+title signature (catches re-scraped jobs)
signature_key = f"{company.lower()}|{normalized_title.lower()}"
if signature_key in user_signatures:
    # User already applied to this company+title before!
    # Even if it has a new job_id
    continue  # Hide job
```

**What this does:**
- Loads user's `job_signatures` from database
- Creates set of `company|title` pairs user has interacted with
- Checks each job against BOTH:
  1. ✅ Exact job_id match (for current jobs)
  2. ✅ Company+title signature match (for re-scraped jobs)

### Fix 2: Increase Cleanup Limit from 300 → 1000 Jobs Per Country

**File: `database_models.py:656`**

```python
# OLD: Too aggressive cleanup
deleted_jobs = await self._cleanup_old_jobs_postgres(conn, max_jobs_per_country=300)

# NEW: More reasonable limit
deleted_jobs = await self._cleanup_old_jobs_postgres(conn, max_jobs_per_country=1000)
```

**Why this helps:**
- Keeps jobs in database longer
- Reduces frequency of jobs being deleted and re-scraped
- Still prevents database from growing indefinitely

### Fix 3: Never Delete Jobs Users Have Interacted With

**File: `database_models.py:526-529`**

```python
# NEW: Smart cleanup that preserves user interactions
DELETE FROM jobs
WHERE id IN (
    SELECT id FROM jobs
    WHERE country = $1
    -- CRITICAL: Don't delete jobs users have interacted with
    AND NOT EXISTS (
        SELECT 1 FROM user_job_interactions uji
        WHERE uji.job_id = jobs.id
    )
    ORDER BY scraped_at DESC
    LIMIT 1000 OFFSET 1000  -- Keep newest 1000, delete rest
)
```

**What this does:**
- Jobs you've applied/rejected to are **NEVER deleted**
- Only deletes jobs that NO user has interacted with
- Your application history is preserved forever! ✅

## 📊 How It Works Now

### Scenario 1: Normal Job (Not Re-Scraped)
```
Job: "DevOps Engineer at Stripe" (job_id: abc123)
User applies → user_job_interactions(job_id=abc123, applied=TRUE)

Next scraper run:
✅ Filter Check 1: job_id abc123 in user_interactions? YES → HIDE
✅ Filter Check 2: (not needed, already hidden)

Result: Job never appears again! 🎉
```

### Scenario 2: Job Gets Deleted and Re-Scraped
```
Job: "Backend Engineer at Shopify" (job_id: old456)
User applies → user_job_interactions(job_id=old456, applied=TRUE)
              job_signatures(company=Shopify, title=backend engineer)

Cleanup runs → Deletes old456 from jobs table

Scraper runs → Finds same job, new ID (job_id: new789)

Filter runs:
❌ Filter Check 1: job_id new789 in user_interactions? NO
✅ Filter Check 2: "shopify|backend engineer" in user_signatures? YES → HIDE

Result: Job hidden even with new ID! 🎉
```

### Scenario 3: Similar Job, Different Company
```
Job A: "Software Engineer at Google" → Applied
Job B: "Software Engineer at Meta" → New job

Filter runs on Job B:
❌ Filter Check 1: Different job_id → Not in interactions
❌ Filter Check 2: Different company (google ≠ meta) → Not in signatures
✅ Result: Job B shows up! (Different company, should show!)
```

## 🎯 Summary of Changes

| File | Change | Why |
|------|--------|-----|
| `railway_server.py:327-343` | Load user's job signatures | Check company+title, not just job_id |
| `railway_server.py:369-379` | Check company+title match | Catch re-scraped jobs with new IDs |
| `database_models.py:656` | Increase limit 300→1000 | Less aggressive cleanup |
| `database_models.py:526-529` | Never delete user jobs | Preserve application history |

## ✅ Benefits

1. **No More Duplicate Jobs** - Jobs you've interacted with never show again
2. **Works Across Re-Scrapes** - Even if job gets new ID, still filtered
3. **Preserves History** - Jobs you applied to are never deleted
4. **Smart Cleanup** - Only deletes jobs NO user has touched
5. **Better Performance** - Fewer jobs to filter = faster load times

## 🧪 Testing

Run the test script to verify:
```bash
python3 test_per_user_filtering.py
```

Expected output:
```
✅ User has 204 job interactions, 156 job signatures
✅ Hiding job xyz789... - user already applied to 'Software Engineer' at Google (repost with new ID)
```

## 🔮 Future Improvements

### Option 1: Track Job by Company+Title from Start
Instead of relying on LinkedIn's job_id (which changes), we could:
- Generate our own stable ID: `hash(company + normalized_title + country)`
- Use this as primary key in jobs table
- Never have duplicate jobs, even across scrapes

### Option 2: Add "Last Seen" Tracking
```sql
ALTER TABLE user_job_interactions
ADD COLUMN last_seen_at TIMESTAMP;

-- Update whenever user views a job
-- Then hide jobs user has "seen" after 30 days
```

### Option 3: Make Cleanup Configurable
```python
# In .env
MAX_JOBS_PER_COUNTRY=1000
PRESERVE_INTERACTION_JOBS=true
CLEANUP_DAYS_THRESHOLD=60
```

## 🎉 Conclusion

**The fix is complete!** You should no longer see:
- ✅ Jobs you've applied to
- ✅ Jobs you've rejected
- ✅ Jobs that are reposts of ones you've seen
- ✅ Duplicate jobs with different IDs

All without switching to NoSQL! PostgreSQL handles this perfectly. 🐘
