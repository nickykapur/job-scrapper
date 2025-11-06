# Job Deduplication System

## Problem

Companies frequently repost the same job listings after a few days or weeks, which results in:
- Seeing duplicate jobs you've already applied to
- Wasting time reviewing the same positions
- Cluttering your job dashboard with reposts

## Solution

The job deduplication system automatically detects and filters out reposted jobs by:

1. **Normalizing job titles** - Removes variations like seniority levels (Senior, Junior), location info (Remote, Hybrid), and employment types
2. **Tracking applied jobs** - Creates a "signature" for each job you apply to based on company + normalized title + country
3. **Detecting reposts** - When scraping new jobs, checks if you've applied to a similar job at the same company within the last 30 days
4. **Automatically skipping duplicates** - Prevents reposted jobs from appearing in your dashboard

## Architecture

### Database Schema

**New Table: `job_signatures`**
```sql
- company VARCHAR(300) - Company name
- normalized_title VARCHAR(500) - Job title without variations
- country VARCHAR(100) - Job location country
- applied_date TIMESTAMP - When you applied
- original_job_id VARCHAR(50) - Reference to the original job
```

**New Fields in `jobs` table:**
```sql
- normalized_title VARCHAR(500) - Automatically computed from title
- is_likely_repost BOOLEAN - Flags potential reposts (currently unused, skipped instead)
- original_job_id VARCHAR(50) - Links to original job if it's a repost
```

### Title Normalization

The system normalizes job titles to detect similar postings:

**Original:** "Senior Software Engineer - Remote (Full Time)"
**Normalized:** "software engineer"

**Original:** "Junior Python Developer"
**Normalized:** "python developer"

This allows the system to recognize that "Senior Software Engineer" and "Staff Software Engineer" at the same company are likely the same role reposted.

### How It Works

1. **When you mark a job as applied:**
   - System creates a job signature with normalized title + company + country
   - Stored in `job_signatures` table with current timestamp

2. **When scraping new jobs:**
   - For each new job, system checks if a similar job signature exists
   - Looks for matches: same company + normalized title + country
   - Only checks signatures from last 30 days
   - If match found, skips the job entirely

3. **What gets tracked:**
   - ✅ Company name (case-insensitive)
   - ✅ Normalized job title
   - ✅ Country
   - ✅ Date you applied
   - ⏰ 30-day time window

## Installation

### Step 1: Run the Migration

```bash
# Set your DATABASE_URL if not already set
export DATABASE_URL="postgresql://user:password@host:port/database"

# Run the migration script
python3 run_deduplication_migration.py
```

This will:
- Add new database tables and fields
- Create a job signature for every job you've marked as "applied"
- Set up automatic title normalization

### Step 2: Verify Installation

The migration script will show you:
- Number of applied jobs found
- Number of job signatures created
- Any errors encountered

## Usage

### No Changes Required!

The deduplication system works automatically once installed:

1. **When scraping:** Reposts are automatically detected and skipped
2. **When applying:** Job signature is automatically created
3. **In logs:** You'll see messages like:
   ```
   ⏭️  Skipping repost: 'Software Engineer' at Google (you applied to a similar job)
   ⏭️  Skipped 3 reposted jobs (already applied to similar positions)
   ```

### Adjusting the Time Window

By default, jobs are considered reposts if they appear within 30 days. To change this:

**In `database_models.py`:**
```python
# Change days_window parameter (default is 30)
is_repost, original_job_id = await self.check_if_repost(
    company, title, country, days_window=45  # Change to 45 days
)
```

## Examples

### Example 1: Direct Repost
```
Day 1:  Apply to "Senior Software Engineer" at Google
Day 5:  Google reposts "Senior Software Engineer"
Result: ⏭️  Skipped (exact match)
```

### Example 2: Variation Repost
```
Day 1:  Apply to "Senior Software Engineer - Remote" at Google
Day 10: Google posts "Staff Software Engineer"
Result: ⏭️  Skipped (normalized: "software engineer" at Google)
```

### Example 3: Different Company
```
Day 1:  Apply to "Software Engineer" at Google
Day 5:  Amazon posts "Software Engineer"
Result: ✅ Shows up (different company)
```

### Example 4: After Time Window
```
Day 1:  Apply to "Software Engineer" at Google
Day 40: Google reposts "Software Engineer"
Result: ✅ Shows up (outside 30-day window)
```

## Monitoring

### View Job Signatures

```sql
-- See all tracked job signatures
SELECT company, normalized_title, country, applied_date
FROM job_signatures
ORDER BY applied_date DESC;

-- See duplicates by company
SELECT company, normalized_title, COUNT(*) as times_applied
FROM job_signatures
GROUP BY company, normalized_title
HAVING COUNT(*) > 1;
```

### Check Normalized Titles

```sql
-- Compare original vs normalized titles
SELECT title, normalized_title
FROM jobs
WHERE applied = TRUE
ORDER BY scraped_at DESC
LIMIT 20;
```

## Troubleshooting

### Issue: Still seeing duplicate jobs

**Possible causes:**
1. Job title is significantly different (e.g., "Backend Engineer" vs "Python Developer")
2. Company name has changed (e.g., "Google" vs "Google LLC")
3. Job is outside the 30-day window
4. Job signature wasn't created (check if job was marked as applied)

**Solution:**
```bash
# Re-run migration to backfill signatures
python3 run_deduplication_migration.py
```

### Issue: Missing legitimate job opportunities

**Possible causes:**
- Title normalization is too aggressive
- Time window is too long

**Solution:**
- Reduce the `days_window` parameter to 14 or 7 days
- Adjust normalization rules in `normalize_job_title()` function

### Issue: Migration fails

**Check:**
1. DATABASE_URL is set correctly
2. Database is accessible
3. You have permission to create tables/functions

## Technical Details

### Performance

- **Indexes:** Created on company, normalized_title, and applied_date
- **Query complexity:** O(1) lookup per job using indexed queries
- **Overhead:** ~5-10ms per job during scraping (negligible)

### Database Functions

The migration creates a PostgreSQL function `normalize_job_title()` that:
- Is marked as `IMMUTABLE` for query optimization
- Automatically runs on INSERT/UPDATE via trigger
- Ensures consistency between Python and SQL normalization

### Signature Uniqueness

Job signatures use a UNIQUE constraint on `(company, normalized_title, country)`:
- Prevents duplicate signatures
- Automatically updates `applied_date` if you reapply
- Uses `ON CONFLICT DO UPDATE` for idempotency

## Future Enhancements

Potential improvements to consider:

1. **Fuzzy matching:** Use Levenshtein distance for company names
2. **Description similarity:** Compare job descriptions using TF-IDF
3. **User preferences:** Allow customizing which fields to consider
4. **Smart window:** Adjust time window based on job type (senior roles might have longer windows)
5. **UI indicator:** Show "previously applied" badge instead of hiding completely

## Support

If you encounter issues or have suggestions:
1. Check the logs during scraping
2. Verify job signatures are being created: `SELECT * FROM job_signatures LIMIT 10;`
3. Test title normalization: `SELECT normalize_job_title('Your Job Title');`
