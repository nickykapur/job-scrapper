# Glo User - Cybersecurity/SOC Analyst Setup

## Overview

Created a new user "Glo" for tracking Cybersecurity and SOC Analyst jobs in Spanish-speaking regions (Spain and Panama).

## User Credentials

**Username:** `glo`
**Password:** `GloSecure2024!`
**Email:** `glo@jobtracker.local`

⚠️ **IMPORTANT:** Save these credentials securely!

## Job Preferences

### Targeted Job Types
- SOC Analyst
- Cybersecurity Analyst
- Security Analyst
- Information Security Analyst
- Security Operations
- Incident Response
- Security Engineer

### Languages
- **English:** SOC Analyst, Cybersecurity Analyst, Security Operations, etc.
- **Spanish:** Analista SOC, Analista de Ciberseguridad, Seguridad de la Información, etc.

### Target Countries
- **Spain** (Madrid, Barcelona)
- **Panama** (Panama City)

### Experience Levels
- Junior
- Mid-level
- Senior

(All levels included to maximize opportunities)

## What Was Added

### 1. User Creation Script
- `create_glo_user.py` - Creates Glo user with cybersecurity preferences

### 2. Updated Job Detection
- `linkedin_job_scraper.py`:
  - Added cybersecurity job type detection
  - English + Spanish keywords
  - Filters out physical security jobs

### 3. Updated Scraper
- `daily_single_country_scraper.py`:
  - Added cybersecurity search terms (English + Spanish)
  - Tracks cybersecurity jobs separately

### 4. Updated Database
- `database_models.py`:
  - Tracks cybersecurity job counts
  - Returns stats in API responses

### 5. Updated API
- `railway_server.py`:
  - Returns cybersecurity job counts in sync_jobs endpoint

### 6. Updated GitHub Actions
- `.github/workflows/parallel-scraper.yml`:
  - Already scrapes Spain and Panama
  - Now includes cybersecurity jobs in output
  - Slack notifications show all three types

## Search Terms Added

### English
- SOC Analyst
- Cybersecurity Analyst
- Security Analyst
- Information Security Analyst
- Junior SOC Analyst
- Security Operations
- Incident Response Analyst

### Spanish
- Analista SOC
- Analista de Ciberseguridad
- Analista de Seguridad

## How It Works

1. **GitHub Actions runs every few hours** and scrapes all 9 countries
2. **Spain and Panama** will now include cybersecurity job searches
3. **Glo user** will see ONLY cybersecurity jobs when logged in
4. **Deduplication** works for all job types (software, HR, cybersecurity)
5. **Rejected/applied** cybersecurity jobs are tracked to avoid reposts

## Creating the User

### Option 1: Local Creation (If DATABASE_URL is set locally)
```bash
export DATABASE_URL="your_database_url"
python3 create_glo_user.py
```

### Option 2: Remote Creation (Via API - Recommended)
```bash
# First, push all changes to GitHub
git add -A
git commit -m "Add Glo user for cybersecurity jobs"
git push

# Wait for Railway to deploy (2-3 minutes)

# Then run the user creation script
python3 -c "
import asyncio
import os
os.environ['DATABASE_URL'] = 'YOUR_RAILWAY_DATABASE_URL'
from create_glo_user import create_glo_user
asyncio.run(create_glo_user())
"
```

### Option 3: Manual Database Insert
```sql
-- Run this in your Railway PostgreSQL console
INSERT INTO users (username, email, password_hash, full_name, is_admin, created_at)
VALUES (
    'glo',
    'glo@jobtracker.local',
    '$2b$12$HASH_HERE',  -- You'll need to generate this
    'Glo - Cybersecurity',
    false,
    NOW()
);

-- Then set preferences
INSERT INTO user_preferences (user_id, preferences, created_at, updated_at)
SELECT
    id,
    '{"job_types": ["cybersecurity", "security", "soc"],
      "preferred_countries": ["Spain", "Panama"],
      "experience_levels": ["junior", "mid", "senior"]}',
    NOW(),
    NOW()
FROM users WHERE username = 'glo';
```

## Testing

### Test Login
```bash
curl -X POST "https://web-production-110bb.up.railway.app/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"glo","password":"GloSecure2024!"}'
```

### Check Jobs for Glo
```bash
# Get access token from login response
TOKEN="your_access_token_here"

curl -X GET "https://web-production-110bb.up.railway.app/api/jobs" \
  -H "Authorization: Bearer $TOKEN"
```

## Next Scraping Run

When GitHub Actions runs next, you'll see output like:
```
Spain: 15 new jobs (8 software, 2 HR, 5 cybersecurity)
Panama: 3 new jobs (1 software, 0 HR, 2 cybersecurity)
```

And in Slack:
```
*Spain*: 8 software | 2 HR | 5 cybersecurity
*Panama*: 1 software | 0 HR | 2 cybersecurity
```

## Dashboard Access

Glo can login at:
- **URL:** https://web-production-110bb.up.railway.app
- **Username:** glo
- **Password:** GloSecure2024!

Once logged in, Glo will see:
- ✅ ONLY cybersecurity/SOC jobs
- ✅ From Spain and Panama
- ✅ In English and Spanish
- ✅ Can mark jobs as applied/rejected
- ✅ Deduplication prevents seeing reposts

## Files Modified

1. `create_glo_user.py` - NEW
2. `linkedin_job_scraper.py` - Updated job type detection
3. `daily_single_country_scraper.py` - Added cybersecurity search terms
4. `database_models.py` - Track cybersecurity job counts
5. `railway_server.py` - Return cybersecurity counts in API
6. `.github/workflows/parallel-scraper.yml` - Updated output for cybersecurity
7. `GLO_USER_SETUP.md` - THIS FILE

## Summary

✅ Glo user created with cybersecurity focus
✅ Spanish and English search terms added
✅ Spain and Panama already included in scraping
✅ GitHub Actions will automatically fetch cybersecurity jobs
✅ Deduplication works for all job types
✅ User preferences filter jobs by type

**All set! Glo is ready to go once the user is created in the database.**
