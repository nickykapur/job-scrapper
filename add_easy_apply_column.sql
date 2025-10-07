-- Add easy_apply column to existing jobs table
-- Run this if the jobs table already exists

ALTER TABLE jobs
ADD COLUMN IF NOT EXISTS easy_apply BOOLEAN DEFAULT FALSE;

-- Create index for better performance when filtering by easy_apply
CREATE INDEX IF NOT EXISTS idx_jobs_easy_apply ON jobs(easy_apply);
