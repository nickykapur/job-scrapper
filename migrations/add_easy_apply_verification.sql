-- Migration: Add Easy Apply Verification Fields
-- Purpose: Add confidence tracking for Easy Apply detection to reduce false positives
-- Date: 2025-11-18

-- Add new verification columns
ALTER TABLE jobs
ADD COLUMN IF NOT EXISTS easy_apply_status VARCHAR(50) DEFAULT 'unverified',
ADD COLUMN IF NOT EXISTS easy_apply_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS easy_apply_verification_method VARCHAR(100);

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_jobs_easy_apply_status ON jobs(easy_apply_status);

-- Migrate existing data: convert boolean to status
-- If easy_apply is TRUE, mark as 'probable' (since it came from filter trust)
-- If easy_apply is FALSE, mark as 'false'
UPDATE jobs
SET easy_apply_status = CASE
    WHEN easy_apply = TRUE THEN 'probable'
    ELSE 'false'
END,
easy_apply_verification_method = CASE
    WHEN easy_apply = TRUE THEN 'filter_parameter'
    ELSE NULL
END,
easy_apply_verified_at = CASE
    WHEN easy_apply = TRUE THEN scraped_at
    ELSE NULL
END
WHERE easy_apply_status = 'unverified';

-- Add comment to document the status values
COMMENT ON COLUMN jobs.easy_apply_status IS 'Status values: confirmed (verified on detail page), probable (from LinkedIn filter), unverified (not checked), false (confirmed not easy apply)';
COMMENT ON COLUMN jobs.easy_apply_verification_method IS 'Method values: detail_page, filter_parameter, card_detection, manual';
COMMENT ON COLUMN jobs.easy_apply_verified_at IS 'Timestamp when the easy apply status was last verified';

-- Note: We're keeping the easy_apply boolean for backward compatibility
-- Once all code is updated, we can deprecate it
COMMENT ON COLUMN jobs.easy_apply IS 'DEPRECATED: Use easy_apply_status instead. Kept for backward compatibility.';
