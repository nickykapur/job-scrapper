-- Migration: Consolidate duplicate jobs by title+company
-- This groups jobs posted in multiple locations into a single entry

-- Step 1: Add new fields
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS locations TEXT[];
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Step 2: Create a temporary table with the new consolidated job IDs
CREATE TEMP TABLE job_id_mapping AS
SELECT
    id AS old_id,
    MD5(LOWER(TRIM(title)) || '|' || LOWER(TRIM(company)))::varchar(12) AS new_id,
    title,
    company,
    location
FROM jobs;

-- Step 3: Show preview of consolidation (jobs that will be merged)
SELECT
    new_id,
    title,
    company,
    ARRAY_AGG(DISTINCT location ORDER BY location) AS all_locations,
    COUNT(*) AS duplicate_count,
    MIN(first_seen) AS earliest_seen,
    MAX(scraped_at) AS latest_seen
FROM job_id_mapping m
JOIN jobs j ON m.old_id = j.id
GROUP BY new_id, title, company
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 20;

-- Step 4: For each group of duplicates, merge them
-- Create a new consolidated jobs table
CREATE TEMP TABLE consolidated_jobs AS
SELECT
    m.new_id AS id,
    j.title,
    j.company,
    -- Use first location alphabetically as primary (for backward compatibility)
    MIN(j.location) AS location,
    -- Aggregate all unique locations into array
    ARRAY_AGG(DISTINCT j.location ORDER BY j.location) AS locations,
    MIN(j.posted_date) AS posted_date,
    -- Use the URL from the most recently scraped job
    (ARRAY_AGG(j.job_url ORDER BY j.scraped_at DESC))[1] AS job_url,
    MIN(j.first_seen) AS first_seen,
    MAX(j.scraped_at) AS last_seen,
    MAX(j.scraped_at) AS scraped_at,
    -- Preserve user interactions (if any job was applied/rejected, keep that status)
    BOOL_OR(j.applied) AS applied,
    BOOL_OR(j.rejected) AS rejected,
    BOOL_OR(j.easy_apply) AS easy_apply,
    MIN(j.category) AS category,
    STRING_AGG(DISTINCT j.notes, '; ') FILTER (WHERE j.notes IS NOT NULL) AS notes,
    BOOL_OR(j.excluded) AS excluded,
    MIN(j.created_at) AS created_at,
    MAX(j.updated_at) AS updated_at,
    MIN(j.job_type) AS job_type,
    MIN(j.experience_level) AS experience_level,
    MIN(j.remote_type) AS remote_type,
    MIN(j.salary_range) AS salary_range,
    (ARRAY_AGG(j.description ORDER BY LENGTH(j.description) DESC NULLS LAST))[1] AS description,
    MIN(j.country) AS country,
    MIN(j.normalized_title) AS normalized_title,
    MIN(j.easy_apply_status) AS easy_apply_status,
    MIN(j.easy_apply_verified_at) AS easy_apply_verified_at,
    MIN(j.easy_apply_verification_method) AS easy_apply_verification_method
FROM job_id_mapping m
JOIN jobs j ON m.old_id = j.id
GROUP BY m.new_id, j.title, j.company;

-- Step 5: Show summary before applying
SELECT
    'Total jobs before consolidation:' AS description,
    COUNT(*) AS count
FROM jobs
UNION ALL
SELECT
    'Total jobs after consolidation:',
    COUNT(*)
FROM consolidated_jobs
UNION ALL
SELECT
    'Jobs that will be removed (duplicates):',
    (SELECT COUNT(*) FROM jobs) - (SELECT COUNT(*) FROM consolidated_jobs);

-- Step 6: Backup original jobs table (optional - comment out if you trust the migration)
-- CREATE TABLE jobs_backup_20251208 AS SELECT * FROM jobs;

-- Step 7: Apply the consolidation
-- First, delete jobs that will be replaced
DELETE FROM jobs
WHERE id IN (SELECT old_id FROM job_id_mapping);

-- Then insert consolidated jobs
INSERT INTO jobs (
    id, title, company, location, locations, posted_date, job_url,
    first_seen, last_seen, scraped_at, applied, rejected, easy_apply,
    category, notes, excluded, created_at, updated_at,
    job_type, experience_level, remote_type, salary_range, description,
    country, normalized_title, easy_apply_status, easy_apply_verified_at,
    easy_apply_verification_method
)
SELECT
    id, title, company, location, locations, posted_date, job_url,
    first_seen, last_seen, scraped_at, applied, rejected, easy_apply,
    category, notes, excluded, created_at, updated_at,
    job_type, experience_level, remote_type, salary_range, description,
    country, normalized_title, easy_apply_status, easy_apply_verified_at,
    easy_apply_verification_method
FROM consolidated_jobs;

-- Step 8: Verify results
SELECT
    'Final job count:' AS description,
    COUNT(*) AS count
FROM jobs
UNION ALL
SELECT
    'Jobs with multiple locations:',
    COUNT(*)
FROM jobs
WHERE ARRAY_LENGTH(locations, 1) > 1;

-- Step 9: Show some examples of consolidated jobs
SELECT
    title,
    company,
    ARRAY_LENGTH(locations, 1) AS location_count,
    locations,
    first_seen,
    last_seen
FROM jobs
WHERE ARRAY_LENGTH(locations, 1) > 1
ORDER BY ARRAY_LENGTH(locations, 1) DESC
LIMIT 10;
