-- PostgreSQL Database Setup for LinkedIn Job Manager
-- Run this after creating a PostgreSQL service on Railway

CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(300) NOT NULL,
    location VARCHAR(300),
    posted_date VARCHAR(100),
    job_url TEXT NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    applied BOOLEAN DEFAULT FALSE,
    rejected BOOLEAN DEFAULT FALSE,
    is_new BOOLEAN DEFAULT FALSE,
    easy_apply BOOLEAN DEFAULT FALSE, -- LinkedIn Easy Apply indicator
    category VARCHAR(50), -- 'new', 'last_24h', 'existing'
    notes TEXT,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_seen_24h TIMESTAMP WITH TIME ZONE,
    excluded BOOLEAN DEFAULT FALSE,
    country VARCHAR(100), -- extracted from location
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);
CREATE INDEX IF NOT EXISTS idx_jobs_applied ON jobs(applied);
CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);
CREATE INDEX IF NOT EXISTS idx_jobs_location ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_date ON jobs(posted_date);
CREATE INDEX IF NOT EXISTS idx_jobs_scraped_at ON jobs(scraped_at);

-- Create metadata table for tracking scraping sessions
CREATE TABLE IF NOT EXISTS scraping_sessions (
    id SERIAL PRIMARY KEY,
    session_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_jobs_found INTEGER DEFAULT 0,
    new_jobs_count INTEGER DEFAULT 0,
    updated_jobs_count INTEGER DEFAULT 0,
    search_terms TEXT[],
    success BOOLEAN DEFAULT TRUE,
    notes TEXT
);

-- Insert initial metadata
INSERT INTO scraping_sessions (notes)
VALUES ('Database initialized for LinkedIn Job Manager')
ON CONFLICT DO NOTHING;

-- Gamification/Rewards System Tables

-- User rewards and progress tracking
CREATE TABLE IF NOT EXISTS user_rewards (
    user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Track earned badges
CREATE TABLE IF NOT EXISTS user_badges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    badge_id VARCHAR(50) NOT NULL, -- e.g., 'first_step', 'job_hunter', 'week_warrior'
    badge_name VARCHAR(100) NOT NULL,
    badge_description TEXT,
    points_awarded INTEGER DEFAULT 0,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_id)
);

-- Track countries user has applied to (for diversity achievements)
CREATE TABLE IF NOT EXISTS user_countries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    country VARCHAR(100) NOT NULL,
    first_application_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    total_applications INTEGER DEFAULT 1,
    UNIQUE(user_id, country)
);

-- Create indexes for rewards tables
CREATE INDEX IF NOT EXISTS idx_user_rewards_user_id ON user_rewards(user_id);
CREATE INDEX IF NOT EXISTS idx_user_rewards_level ON user_rewards(level);
CREATE INDEX IF NOT EXISTS idx_user_rewards_points ON user_rewards(total_points);
CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_earned_at ON user_badges(earned_at);
CREATE INDEX IF NOT EXISTS idx_user_countries_user_id ON user_countries(user_id);

-- Useful queries for your reference:

-- Get all jobs from last 24 hours
-- SELECT * FROM jobs WHERE posted_date LIKE '%hour%' OR posted_date LIKE '%1 day%';

-- Get applied jobs
-- SELECT * FROM jobs WHERE applied = TRUE;

-- Get Dublin jobs
-- SELECT * FROM jobs WHERE location ILIKE '%dublin%';

-- Get job statistics
-- SELECT 
--     COUNT(*) as total_jobs,
--     COUNT(*) FILTER (WHERE applied = TRUE) as applied_jobs,
--     COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
--     COUNT(*) FILTER (WHERE location ILIKE '%dublin%') as dublin_jobs
-- FROM jobs;