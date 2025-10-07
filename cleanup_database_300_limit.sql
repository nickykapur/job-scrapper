-- Emergency cleanup: Reduce to 300 most recent jobs per country
-- Current state: UK=1000+, Spain=900, Germany=310
-- Target: 300 jobs per country (most recent by scraped_at)

-- Start transaction for safety
BEGIN;

-- Show current counts
SELECT 'BEFORE CLEANUP:' as status;
SELECT
    country,
    COUNT(*) as job_count
FROM jobs
WHERE country IS NOT NULL
GROUP BY country
ORDER BY job_count DESC;

-- Delete old jobs for United Kingdom (keep 300 newest)
WITH ranked_jobs AS (
    SELECT
        id,
        ROW_NUMBER() OVER (PARTITION BY country ORDER BY scraped_at DESC NULLS LAST) as rn
    FROM jobs
    WHERE country = 'United Kingdom'
)
DELETE FROM jobs
WHERE id IN (
    SELECT id FROM ranked_jobs WHERE rn > 300
);

-- Delete old jobs for Spain (keep 300 newest)
WITH ranked_jobs AS (
    SELECT
        id,
        ROW_NUMBER() OVER (PARTITION BY country ORDER BY scraped_at DESC NULLS LAST) as rn
    FROM jobs
    WHERE country = 'Spain'
)
DELETE FROM jobs
WHERE id IN (
    SELECT id FROM ranked_jobs WHERE rn > 300
);

-- Delete old jobs for Germany (keep 300 newest)
WITH ranked_jobs AS (
    SELECT
        id,
        ROW_NUMBER() OVER (PARTITION BY country ORDER BY scraped_at DESC NULLS LAST) as rn
    FROM jobs
    WHERE country = 'Germany'
)
DELETE FROM jobs
WHERE id IN (
    SELECT id FROM ranked_jobs WHERE rn > 300
);

-- Delete old jobs for Ireland (keep 300 newest)
WITH ranked_jobs AS (
    SELECT
        id,
        ROW_NUMBER() OVER (PARTITION BY country ORDER BY scraped_at DESC NULLS LAST) as rn
    FROM jobs
    WHERE country = 'Ireland'
)
DELETE FROM jobs
WHERE id IN (
    SELECT id FROM ranked_jobs WHERE rn > 300
);

-- Show counts after cleanup
SELECT 'AFTER CLEANUP:' as status;
SELECT
    country,
    COUNT(*) as job_count,
    MAX(scraped_at) as newest_job,
    MIN(scraped_at) as oldest_job
FROM jobs
WHERE country IS NOT NULL
GROUP BY country
ORDER BY job_count DESC;

-- Show how many jobs were deleted
SELECT 'CLEANUP SUMMARY:' as status;
SELECT
    '✅ United Kingdom' as country,
    CASE
        WHEN (SELECT COUNT(*) FROM jobs WHERE country = 'United Kingdom') <= 300
        THEN 'Cleaned ✓'
        ELSE 'NEEDS REVIEW'
    END as status
UNION ALL
SELECT
    '🇪🇸 Spain' as country,
    CASE
        WHEN (SELECT COUNT(*) FROM jobs WHERE country = 'Spain') <= 300
        THEN 'Cleaned ✓'
        ELSE 'NEEDS REVIEW'
    END as status
UNION ALL
SELECT
    '🇩🇪 Germany' as country,
    CASE
        WHEN (SELECT COUNT(*) FROM jobs WHERE country = 'Germany') <= 300
        THEN 'Cleaned ✓'
        ELSE 'NEEDS REVIEW'
    END as status
UNION ALL
SELECT
    '🇮🇪 Ireland' as country,
    CASE
        WHEN (SELECT COUNT(*) FROM jobs WHERE country = 'Ireland') <= 300
        THEN 'Cleaned ✓'
        ELSE 'NEEDS REVIEW'
    END as status;

-- Commit the changes
COMMIT;

-- Final verification
SELECT
    '🎉 FINAL STATE:' as message,
    COUNT(*) as total_jobs_in_db,
    COUNT(DISTINCT country) as countries,
    MAX(scraped_at) as most_recent_job
FROM jobs;
