-- Add rejected column to existing jobs table
-- Run this on your Railway PostgreSQL database

-- Add the rejected column if it doesn't exist
ALTER TABLE jobs
ADD COLUMN IF NOT EXISTS rejected BOOLEAN DEFAULT FALSE;

-- Create index for better performance on rejected column
CREATE INDEX IF NOT EXISTS idx_jobs_rejected ON jobs(rejected);

-- Verify the column was added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'jobs'
AND column_name IN ('applied', 'rejected');