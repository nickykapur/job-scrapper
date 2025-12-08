-- Preview: Show what will be consolidated (READ-ONLY)

-- Create temporary ID mapping
CREATE TEMP TABLE job_id_mapping AS
SELECT
    id AS old_id,
    SUBSTRING(MD5(LOWER(TRIM(title)) || '|' || LOWER(TRIM(company))), 1, 12) AS new_id,
    title,
    company,
    location
FROM jobs;

-- Show jobs that will be merged (duplicates by title+company)
SELECT
    new_id,
    title,
    company,
    ARRAY_AGG(DISTINCT location ORDER BY location) AS all_locations,
    COUNT(*) AS duplicate_count,
    MIN(first_seen) AS earliest_seen,
    MAX(scraped_at) AS latest_scraped
FROM job_id_mapping m
JOIN jobs j ON m.old_id = j.id
GROUP BY new_id, title, company
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 30;

-- Summary statistics
SELECT
    'Current total jobs' AS metric,
    COUNT(*)::text AS value
FROM jobs
UNION ALL
SELECT
    'Unique jobs (by title+company)',
    COUNT(DISTINCT new_id)::text
FROM job_id_mapping
UNION ALL
SELECT
    'Duplicate jobs to be removed',
    (COUNT(*) - COUNT(DISTINCT new_id))::text
FROM job_id_mapping
UNION ALL
SELECT
    'Reduction percentage',
    ROUND(((COUNT(*) - COUNT(DISTINCT new_id))::numeric / COUNT(*) * 100), 1)::text || '%'
FROM job_id_mapping;
