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
    is_new BOOLEAN DEFAULT FALSE,
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