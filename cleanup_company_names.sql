-- Cleanup script to remove trailing numbers from company names
-- This fixes entries like "Stripe 4342327281" to "Stripe"

-- First, let's see what we need to clean
SELECT
    company AS original_name,
    REGEXP_REPLACE(company, '\s+\d{4,}$', '', 'g') AS cleaned_name,
    COUNT(*) AS job_count
FROM jobs
WHERE company ~ '\s+\d{4,}$'
GROUP BY company
ORDER BY job_count DESC;

-- Now perform the cleanup
UPDATE jobs
SET company = REGEXP_REPLACE(company, '\s+\d{4,}$', '', 'g')
WHERE company ~ '\s+\d{4,}$';

-- Show summary of unique companies after cleanup
SELECT
    company,
    COUNT(*) AS job_count
FROM jobs
GROUP BY company
HAVING company LIKE '%Stripe%'
ORDER BY company;
