# Multi-User Job Scraper - Implementation Plan

## Overview
Transform the single-user job tracker into a multi-user system for 2-5 friends/family members, where each user can track different job types and experience levels from a shared job pool.

## Architecture

### Core Concept: "Shared Pool, Personal Filters"
```
┌─────────────────────────────────────┐
│   Daily Scraper (Expanded Scope)   │
│  ├─ Software Engineering Jobs       │
│  ├─ Marketing/Sales Jobs            │
│  ├─ Design Jobs                     │
│  ├─ Finance Jobs                    │
│  └─ All Experience Levels           │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│       Shared Job Database           │
│     (PostgreSQL - 1000s of jobs)    │
└─────────────────────────────────────┘
           ↓           ↓
    ┌──────────┐  ┌──────────┐
    │  User A  │  │  User B  │
    │ Software │  │ Marketing│
    │ Junior   │  │ Senior   │
    └──────────┘  └──────────┘
```

## Database Schema Changes

### 1. New Tables

#### `users` table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### `user_preferences` table
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    -- Job type preferences (JSON array)
    job_types TEXT[], -- ['software', 'data', 'devops', etc.]
    keywords TEXT[], -- ['python', 'react', 'machine learning']

    -- Experience level filters
    experience_levels TEXT[], -- ['entry', 'junior', 'mid', 'senior']
    exclude_senior BOOLEAN DEFAULT FALSE,

    -- Location preferences
    preferred_countries TEXT[], -- ['Ireland', 'Spain', 'Remote']
    preferred_cities TEXT[],

    -- Company preferences
    excluded_companies TEXT[], -- Personal blacklist
    preferred_companies TEXT[], -- Companies user likes

    -- Filters
    easy_apply_only BOOLEAN DEFAULT FALSE,
    remote_only BOOLEAN DEFAULT FALSE,

    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### `user_job_interactions` table
```sql
CREATE TABLE user_job_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(50) REFERENCES jobs(id) ON DELETE CASCADE,
    applied BOOLEAN DEFAULT FALSE,
    rejected BOOLEAN DEFAULT FALSE,
    saved BOOLEAN DEFAULT FALSE,
    notes TEXT,
    applied_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, job_id)
);
```

### 2. Modify Existing `jobs` table
```sql
-- Add new columns to support more job types
ALTER TABLE jobs
ADD COLUMN IF NOT EXISTS job_type VARCHAR(100), -- 'software', 'marketing', 'design', etc.
ADD COLUMN IF NOT EXISTS experience_level VARCHAR(50), -- 'entry', 'junior', 'mid', 'senior'
ADD COLUMN IF NOT EXISTS remote_type VARCHAR(50), -- 'remote', 'hybrid', 'onsite'
ADD COLUMN IF NOT EXISTS salary_range VARCHAR(100);

-- Remove user-specific columns (move to user_job_interactions)
-- applied, rejected will be in user_job_interactions table
```

## API Changes

### New Authentication Endpoints

```python
POST   /api/auth/register          # Register new user
POST   /api/auth/login             # Login (returns JWT token)
POST   /api/auth/logout            # Logout
GET    /api/auth/me                # Get current user info
PUT    /api/auth/change-password   # Change password
```

### New User Preference Endpoints

```python
GET    /api/users/me/preferences   # Get user preferences
PUT    /api/users/me/preferences   # Update user preferences
GET    /api/users/me/stats         # Get user-specific statistics
```

### Modified Job Endpoints

```python
# All job endpoints now filter by user preferences + authentication
GET    /api/jobs                   # Get jobs filtered by user preferences
GET    /api/jobs/{job_id}          # Get specific job
POST   /api/jobs/{job_id}/apply    # Mark job as applied (user-specific)
POST   /api/jobs/{job_id}/reject   # Mark job as rejected (user-specific)
POST   /api/jobs/{job_id}/save     # Save job for later
GET    /api/jobs/applied           # Get user's applied jobs
GET    /api/jobs/rejected          # Get user's rejected jobs
GET    /api/jobs/saved             # Get user's saved jobs
```

### Admin Endpoints (for managing scraping)

```python
POST   /api/admin/scrape           # Trigger manual scrape (admin only)
GET    /api/admin/users            # List all users (admin only)
DELETE /api/admin/users/{user_id}  # Delete user (admin only)
```

## Scraper Changes

### Expand Job Type Coverage

```python
# New search configuration
JOB_CATEGORIES = {
    'software': [
        'Software Engineer',
        'Full Stack Developer',
        'Backend Developer',
        'Frontend Developer',
        'DevOps Engineer',
        # ... existing software keywords
    ],
    'marketing': [
        'Marketing Manager',
        'Digital Marketing',
        'Content Marketing',
        'SEO Specialist',
        'Social Media Manager',
    ],
    'design': [
        'Product Designer',
        'UX Designer',
        'UI Designer',
        'Graphic Designer',
    ],
    'data': [
        'Data Analyst',
        'Data Scientist',
        'Business Analyst',
        'Data Engineer',
    ],
    'sales': [
        'Sales Manager',
        'Account Executive',
        'Business Development',
    ]
}
```

### Experience Level Detection

```python
def detect_experience_level(job_data):
    """Detect experience level from job title and description"""
    text = f"{job_data['title']} {job_data.get('description', '')}".lower()

    if any(word in text for word in ['intern', 'entry', 'graduate', 'trainee']):
        return 'entry'
    elif any(word in text for word in ['junior', '0-2 years']):
        return 'junior'
    elif any(word in text for word in ['senior', 'lead', '5+ years', 'principal']):
        return 'senior'
    elif any(word in text for word in ['staff', 'architect', 'director', 'head of']):
        return 'executive'
    else:
        return 'mid'  # Default

def detect_job_type(job_data):
    """Detect job type from title and description"""
    title = job_data['title'].lower()

    # Check each category
    if any(word in title for word in ['engineer', 'developer', 'programmer']):
        return 'software'
    elif any(word in title for word in ['marketing', 'seo', 'content']):
        return 'marketing'
    elif any(word in title for word in ['designer', 'ux', 'ui']):
        return 'design'
    elif any(word in title for word in ['data analyst', 'data scientist']):
        return 'data'
    elif any(word in title for word in ['sales', 'account executive']):
        return 'sales'
    else:
        return 'other'
```

## Frontend Changes

### 1. Add Authentication Pages

```
/login          → Login page
/register       → Registration page
/settings       → User preferences page
/profile        → User profile page
```

### 2. Update Job Dashboard

```typescript
// Add user preference filters to UI
interface UserPreferences {
    jobTypes: string[];
    keywords: string[];
    experienceLevels: string[];
    excludedCompanies: string[];
    easyApplyOnly: boolean;
}

// Jobs are now filtered server-side by user preferences
// UI just displays what the API returns
```

### 3. Add Settings Page

```
User Settings Page:
├─ Job Preferences
│  ├─ Job Types (checkboxes: Software, Marketing, Design...)
│  ├─ Keywords (tags input)
│  └─ Experience Levels (checkboxes: Entry, Junior, Mid, Senior)
├─ Location Preferences
│  ├─ Preferred Countries
│  └─ Remote/Hybrid/Onsite
├─ Company Preferences
│  ├─ Excluded Companies
│  └─ Preferred Companies
└─ Filters
   ├─ Easy Apply Only
   └─ Remote Only
```

## Implementation Steps

### Phase 1: Database & Auth (Week 1)
1. ✅ Create new database schema
2. ✅ Implement user authentication (JWT)
3. ✅ Add password hashing (bcrypt)
4. ✅ Create user registration/login endpoints
5. ✅ Add authentication middleware

### Phase 2: User Preferences (Week 2)
1. ✅ Create user preferences table
2. ✅ Build preferences management endpoints
3. ✅ Add default preferences for new users
4. ✅ Create user_job_interactions table

### Phase 3: Scraper Updates (Week 2-3)
1. ✅ Expand job type keywords
2. ✅ Add experience level detection
3. ✅ Add job type classification
4. ✅ Update daily scraper to fetch diverse jobs
5. ✅ Test with different job types

### Phase 4: API Updates (Week 3)
1. ✅ Modify job endpoints to filter by user
2. ✅ Add user-specific applied/rejected tracking
3. ✅ Update job listing with preference filtering
4. ✅ Add statistics per user

### Phase 5: Frontend (Week 4)
1. ✅ Add login/register pages
2. ✅ Add authentication state management
3. ✅ Update job dashboard for multi-user
4. ✅ Add settings page
5. ✅ Add user profile page

### Phase 6: Testing & Deployment (Week 5)
1. ✅ Test with multiple users
2. ✅ Add user data isolation tests
3. ✅ Deploy to Railway
4. ✅ Create initial user accounts

## Security Considerations

1. **Password Security**
   - Use bcrypt for password hashing
   - Enforce minimum password length (8 characters)
   - Optional: Add password strength requirements

2. **JWT Tokens**
   - Set reasonable expiration (7 days)
   - Store JWT secret in environment variable
   - Add refresh token mechanism (optional)

3. **Rate Limiting**
   - Limit login attempts (5 per 15 minutes)
   - Rate limit API calls per user

4. **Data Isolation**
   - Ensure users can only see their own applied/rejected jobs
   - Validate user_id in all queries

## Migration Strategy

### For Existing Data
```python
# Migration script to assign existing jobs to "admin" user
# 1. Create admin user account
# 2. Move existing applied/rejected to user_job_interactions
# 3. Set default preferences for admin user
```

## Estimated Resources

- **Database Size**: ~50MB for 1000 jobs × 5 users = Minimal
- **API Load**: 5 users × 20 requests/day = 100 requests/day = Negligible
- **Scraping**: Same as current (one daily scrape, just wider coverage)

## Future Enhancements (Optional)

1. **Email Notifications**
   - Daily digest of new jobs matching preferences
   - Job application reminders

2. **Saved Searches**
   - Users can save specific search combinations
   - One-click reapply saved searches

3. **Job Recommendations**
   - ML-based job recommendations
   - "Jobs similar to ones you applied to"

4. **Team Features**
   - Share jobs between users
   - Collaborative notes on jobs/companies

5. **Analytics Dashboard**
   - Application success rate
   - Time-to-hire metrics
   - Industry trends

## Questions to Resolve

1. Should users be able to see how many other users applied to the same job?
2. Should there be a "super admin" role to manage other users?
3. Should users be able to add custom job sources beyond LinkedIn?
4. Should there be usage limits per user (e.g., max 50 applications tracked)?

---

**Ready to proceed? Let's start with Phase 1: Database & Authentication!**
