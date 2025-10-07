-- Cleanup script to maintain only 300 most recent jobs per country
-- Run this periodically or add to a cron job

-- This script keeps the 300 most recent jobs (by scraped_at) for each country
-- and deletes the older ones

DO $$
DECLARE
    country_name TEXT;
    deleted_count INTEGER := 0;
BEGIN
    -- Loop through each country
    FOR country_name IN
        SELECT DISTINCT country FROM jobs WHERE country IS NOT NULL
    LOOP
        -- Delete old jobs for this country, keeping only the 300 most recent
        WITH ranked_jobs AS (
            SELECT
                id,
                ROW_NUMBER() OVER (PARTITION BY country ORDER BY scraped_at DESC) as rn
            FROM jobs
            WHERE country = country_name
        )
        DELETE FROM jobs
        WHERE id IN (
            SELECT id FROM ranked_jobs WHERE rn > 300
        );

        GET DIAGNOSTICS deleted_count = ROW_COUNT;

        IF deleted_count > 0 THEN
            RAISE NOTICE 'Deleted % old jobs from %', deleted_count, country_name;
        END IF;
    END LOOP;

    RAISE NOTICE 'Cleanup completed successfully';
END $$;

-- Optional: Get statistics after cleanup
SELECT
    country,
    COUNT(*) as total_jobs,
    MAX(scraped_at) as latest_job,
    MIN(scraped_at) as oldest_job
FROM jobs
WHERE country IS NOT NULL
GROUP BY country
ORDER BY total_jobs DESC;
