-- Migration: Add job deduplication support
-- This prevents reposted jobs from appearing again after you've applied

-- Add new fields to jobs table
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS is_likely_repost BOOLEAN DEFAULT FALSE;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS original_job_id VARCHAR(50) REFERENCES jobs(id);
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS normalized_title VARCHAR(500);

-- Create job_signatures table to track applied jobs by company
-- This helps identify when a company reposts a similar job
CREATE TABLE IF NOT EXISTS job_signatures (
    id SERIAL PRIMARY KEY,
    company VARCHAR(300) NOT NULL,
    normalized_title VARCHAR(500) NOT NULL,
    country VARCHAR(100),
    applied_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    original_job_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Ensure we don't duplicate signatures
    UNIQUE(company, normalized_title, country)
);

-- Create indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_job_signatures_company ON job_signatures(company);
CREATE INDEX IF NOT EXISTS idx_job_signatures_normalized_title ON job_signatures(normalized_title);
CREATE INDEX IF NOT EXISTS idx_job_signatures_applied_date ON job_signatures(applied_date);
CREATE INDEX IF NOT EXISTS idx_jobs_is_likely_repost ON jobs(is_likely_repost);
CREATE INDEX IF NOT EXISTS idx_jobs_normalized_title ON jobs(normalized_title);

-- Create a function to normalize job titles (remove common variations)
CREATE OR REPLACE FUNCTION normalize_job_title(title TEXT) RETURNS TEXT AS $$
BEGIN
    -- Convert to lowercase and remove extra whitespace
    title := LOWER(TRIM(title));

    -- Remove common seniority levels and numbers
    title := REGEXP_REPLACE(title, '\b(senior|sr\.?|junior|jr\.?|mid-level|mid level|lead|principal|staff|i|ii|iii|iv|v)\b', '', 'gi');

    -- Remove common variations
    title := REGEXP_REPLACE(title, '\b(remote|hybrid|onsite|on-site)\b', '', 'gi');
    title := REGEXP_REPLACE(title, '\b(full time|full-time|part time|part-time|contract|temporary)\b', '', 'gi');

    -- Remove special characters except spaces and dashes
    title := REGEXP_REPLACE(title, '[^a-z0-9\s\-]', '', 'g');

    -- Collapse multiple spaces into one
    title := REGEXP_REPLACE(title, '\s+', ' ', 'g');

    RETURN TRIM(title);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Populate normalized_title for existing jobs
UPDATE jobs
SET normalized_title = normalize_job_title(title)
WHERE normalized_title IS NULL;

-- Create a trigger to automatically normalize titles on insert/update
CREATE OR REPLACE FUNCTION auto_normalize_job_title() RETURNS TRIGGER AS $$
BEGIN
    NEW.normalized_title := normalize_job_title(NEW.title);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_normalize_job_title ON jobs;
CREATE TRIGGER trigger_normalize_job_title
    BEFORE INSERT OR UPDATE OF title ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION auto_normalize_job_title();
