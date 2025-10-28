-- Migration: Add Multi-User Support
-- Description: Adds users, user_preferences, and user_job_interactions tables
-- Date: 2025-10-28

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- ============================================================================
-- 2. USER PREFERENCES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,

    -- Job type preferences
    job_types TEXT[] DEFAULT ARRAY['software'], -- ['software', 'marketing', 'design', 'data', 'sales']
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[], -- ['python', 'react', 'machine learning']
    excluded_keywords TEXT[] DEFAULT ARRAY[]::TEXT[], -- ['senior', 'lead']

    -- Experience level filters
    experience_levels TEXT[] DEFAULT ARRAY['entry', 'junior', 'mid'], -- ['entry', 'junior', 'mid', 'senior', 'executive']
    exclude_senior BOOLEAN DEFAULT TRUE,

    -- Location preferences
    preferred_countries TEXT[] DEFAULT ARRAY['Ireland'], -- ['Ireland', 'Spain', 'Remote']
    preferred_cities TEXT[] DEFAULT ARRAY[]::TEXT[],
    exclude_locations TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Company preferences
    excluded_companies TEXT[] DEFAULT ARRAY[]::TEXT[], -- Personal blacklist
    preferred_companies TEXT[] DEFAULT ARRAY[]::TEXT[], -- Companies user likes

    -- Filters
    easy_apply_only BOOLEAN DEFAULT FALSE,
    remote_only BOOLEAN DEFAULT FALSE,

    -- Notification preferences
    email_notifications BOOLEAN DEFAULT TRUE,
    daily_digest BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for user lookups
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- ============================================================================
-- 3. USER JOB INTERACTIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_job_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(50) REFERENCES jobs(id) ON DELETE CASCADE,

    -- Interaction status
    applied BOOLEAN DEFAULT FALSE,
    rejected BOOLEAN DEFAULT FALSE,
    saved BOOLEAN DEFAULT FALSE,
    hidden BOOLEAN DEFAULT FALSE,

    -- Additional info
    notes TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5), -- Optional: rate job 1-5

    -- Timestamps
    applied_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    saved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Ensure one interaction per user per job
    UNIQUE(user_id, job_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_user_id ON user_job_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_job_id ON user_job_interactions(job_id);
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_applied ON user_job_interactions(user_id, applied);
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_rejected ON user_job_interactions(user_id, rejected);
CREATE INDEX IF NOT EXISTS idx_user_job_interactions_saved ON user_job_interactions(user_id, saved);

-- ============================================================================
-- 4. UPDATE JOBS TABLE - Add new columns for classification
-- ============================================================================

-- Add columns for job classification (if they don't exist)
ALTER TABLE jobs
ADD COLUMN IF NOT EXISTS job_type VARCHAR(100), -- 'software', 'marketing', 'design', 'data', 'sales'
ADD COLUMN IF NOT EXISTS experience_level VARCHAR(50), -- 'entry', 'junior', 'mid', 'senior', 'executive'
ADD COLUMN IF NOT EXISTS remote_type VARCHAR(50), -- 'remote', 'hybrid', 'onsite', 'unknown'
ADD COLUMN IF NOT EXISTS salary_range VARCHAR(100),
ADD COLUMN IF NOT EXISTS description TEXT; -- Full job description (for better filtering)

-- Create indexes for new columns
CREATE INDEX IF NOT EXISTS idx_jobs_job_type ON jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_jobs_experience_level ON jobs(experience_level);
CREATE INDEX IF NOT EXISTS idx_jobs_remote_type ON jobs(remote_type);
CREATE INDEX IF NOT EXISTS idx_jobs_country ON jobs(country);

-- ============================================================================
-- 5. CREATE DEFAULT ADMIN USER (optional - can be done via API)
-- ============================================================================

-- Note: Password will be set via API on first run
-- This is just a placeholder that should be updated with proper auth

-- ============================================================================
-- 6. HELPER FUNCTIONS
-- ============================================================================

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to relevant tables
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_job_interactions_updated_at ON user_job_interactions;
CREATE TRIGGER update_user_job_interactions_updated_at
    BEFORE UPDATE ON user_job_interactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 7. MIGRATION DATA - Move existing data to new schema
-- ============================================================================

-- This will be handled by a separate migration script to:
-- 1. Create an admin user from existing data
-- 2. Migrate existing applied/rejected jobs to user_job_interactions
-- 3. Set default preferences

-- Note: Run this manually after setting up the first admin user
-- See: migrate_existing_data.py

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables exist
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('users', 'user_preferences', 'user_job_interactions');

-- Check user preferences structure
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user_preferences';

-- Count jobs by type
-- SELECT job_type, COUNT(*) FROM jobs GROUP BY job_type;
