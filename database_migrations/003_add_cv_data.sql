-- Migration 003: Add user CV data table for auto-apply pilot feature
CREATE TABLE IF NOT EXISTS user_cv_data (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name     TEXT,
    email         TEXT,
    phone         TEXT,
    location      TEXT,
    linkedin_url  TEXT,
    github_url    TEXT,
    portfolio_url TEXT,
    skills        JSONB NOT NULL DEFAULT '[]'::jsonb,
    experience    JSONB NOT NULL DEFAULT '[]'::jsonb,
    education     JSONB NOT NULL DEFAULT '[]'::jsonb,
    languages     JSONB NOT NULL DEFAULT '[]'::jsonb,
    summary       TEXT,
    cv_filename   TEXT,
    cv_raw_text   TEXT,
    uploaded_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_cv_data_user_id ON user_cv_data(user_id);
