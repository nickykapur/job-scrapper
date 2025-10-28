# Multi-User Setup Guide

Complete guide to setting up the multi-user job scraper system.

## Overview

This upgrade transforms your single-user job tracker into a multi-user system supporting 2-5 users with:
- User authentication (username/password + JWT)
- Personal job preferences per user
- Individual applied/rejected tracking
- Shared job database with personal filters

## Prerequisites

- PostgreSQL database (Railway or local)
- Python 3.10+
- Existing job scraper installation

## Step 1: Install Dependencies

```bash
# Install new authentication packages
pip install -r requirements.txt

# This installs:
# - python-jose[cryptography] - JWT tokens
# - passlib[bcrypt] - Password hashing
# - python-multipart - Form data support
# - pydantic[email] - Email validation
```

## Step 2: Set Environment Variables

Add these to your `.env` file or Railway environment variables:

```bash
# Database (existing)
DATABASE_URL=postgresql://user:password@host:port/database

# JWT Secret Key (IMPORTANT: Generate a secure random string!)
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production-use-long-random-string

# Optional: Token expiration (days)
ACCESS_TOKEN_EXPIRE_DAYS=7
```

### Generate a Secure JWT Secret Key

```bash
# Option 1: Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Using OpenSSL
openssl rand -base64 32

# Copy the output and set it as JWT_SECRET_KEY
```

## Step 3: Run Database Migration

### Option A: Using Railway Dashboard (Recommended for Production)

1. Go to your Railway project
2. Click on your PostgreSQL service
3. Click "Query" tab
4. Copy and paste the contents of `database_migrations/001_add_multi_user_support.sql`
5. Click "Execute"

### Option B: Using psql CLI (For Local Development)

```bash
# Connect to your database
psql $DATABASE_URL

# Run the migration
\i database_migrations/001_add_multi_user_support.sql

# Verify tables were created
\dt

# You should see:
# - users
# - user_preferences
# - user_job_interactions

# Exit psql
\q
```

### Option C: Using Python Script

```python
# Create run_migration.py
import asyncio
import asyncpg
import os

async def run_migration():
    conn = await asyncpg.connect(os.environ['DATABASE_URL'])

    with open('database_migrations/001_add_multi_user_support.sql', 'r') as f:
        migration_sql = f.read()

    await conn.execute(migration_sql)
    print("✅ Migration completed successfully!")

    await conn.close()

asyncio.run(run_migration())
```

```bash
python run_migration.py
```

## Step 4: Create First Admin User

### Method 1: Using API Endpoint

```bash
# Start the server
python railway_server.py

# Register first user (will be admin)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "SecurePassword123",
    "full_name": "Admin User"
  }'

# You'll receive a response with access_token
# Save this token!
```

### Method 2: Using Python Script

```python
# create_admin.py
import asyncio
from user_database import UserDatabase

async def create_admin():
    db = UserDatabase()

    user = await db.create_user(
        username="admin",
        email="admin@example.com",
        password="SecurePassword123",  # Change this!
        full_name="Admin User",
        is_admin=True  # Make this user an admin
    )

    if user:
        print(f"✅ Admin user created: {user['username']}")
        print(f"   User ID: {user['id']}")
        print(f"   Email: {user['email']}")
    else:
        print("❌ Failed to create admin user (may already exist)")

asyncio.run(create_admin())
```

```bash
python create_admin.py
```

## Step 5: Test Authentication

### Test Login

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "SecurePassword123"
  }'

# Response will contain:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer",
#   "user": { ... }
# }
```

### Test Protected Endpoint

```bash
# Get current user info (requires auth)
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Test User Preferences

```bash
# Get preferences
curl -X GET http://localhost:8000/api/auth/preferences \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"

# Update preferences
curl -X PUT http://localhost:8000/api/auth/preferences \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "job_types": ["software", "data"],
    "experience_levels": ["junior", "mid"],
    "preferred_countries": ["Ireland", "Spain"]
  }'
```

## Step 6: Create Additional Users

### For Each Friend/Family Member

```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword456",
    "full_name": "John Doe"
  }'

# Each user should:
# 1. Save their access_token
# 2. Set up their preferences
# 3. Start browsing jobs!
```

## Step 7: Verify Installation

### Run System Check

```python
# system_check.py
import asyncio
from user_database import UserDatabase
from database_models import JobDatabase

async def check_system():
    print("🔍 Checking Multi-User System...\n")

    # Check user database
    user_db = UserDatabase()
    if not user_db.use_postgres:
        print("❌ PostgreSQL not available - multi-user requires PostgreSQL")
        return

    print("✅ PostgreSQL connected")

    # Try to get a user
    conn = await user_db.get_connection()
    if conn:
        user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        pref_count = await conn.fetchval("SELECT COUNT(*) FROM user_preferences")
        print(f"✅ Users table: {user_count} users")
        print(f"✅ Preferences table: {pref_count} preferences")

        await conn.close()

    # Check job database
    job_db = JobDatabase()
    if job_db.use_postgres:
        conn = await job_db.get_connection()
        if conn:
            job_count = await conn.fetchval("SELECT COUNT(*) FROM jobs")
            print(f"✅ Jobs table: {job_count} jobs")

            # Check if new columns exist
            columns = await conn.fetch("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'jobs' AND column_name IN ('job_type', 'experience_level', 'remote_type')
            """)
            print(f"✅ New job columns: {len(columns)}/3 present")

            await conn.close()

    print("\n✨ System check complete!")

asyncio.run(check_system())
```

```bash
python system_check.py
```

## API Endpoints Reference

### Authentication

```
POST   /api/auth/register          # Register new user
POST   /api/auth/login             # Login
GET    /api/auth/me                # Get current user
PUT    /api/auth/profile           # Update profile
POST   /api/auth/change-password   # Change password
POST   /api/auth/logout            # Logout
```

### User Preferences

```
GET    /api/auth/preferences       # Get preferences
PUT    /api/auth/preferences       # Update preferences
GET    /api/auth/stats             # Get user statistics
```

### Admin (Admin users only)

```
GET    /api/auth/admin/users       # List all users
DELETE /api/auth/admin/users/{id}  # Delete user
```

## Common Issues & Solutions

### Issue: "Database connection failed"

**Solution:**
- Check `DATABASE_URL` environment variable
- Ensure PostgreSQL is running
- Verify database credentials

### Issue: "Could not validate credentials"

**Solution:**
- Check that JWT_SECRET_KEY is set
- Verify token hasn't expired
- Make sure token is sent in Authorization header as "Bearer TOKEN"

### Issue: "Username or email already exists"

**Solution:**
- Use a different username/email
- Or login with existing credentials

### Issue: "Migration failed"

**Solution:**
- Check if tables already exist: `\dt` in psql
- Drop existing tables if needed (CAUTION: deletes data!)
- Re-run migration

### Issue: "Auth routes not available"

**Solution:**
```bash
# Install missing dependencies
pip install python-jose[cryptography] passlib[bcrypt]

# Restart server
```

## Security Best Practices

1. **JWT Secret Key**
   - Use a long, random string (32+ characters)
   - NEVER commit it to git
   - Use different keys for dev/prod

2. **Passwords**
   - Enforce minimum 8 characters
   - Require letters AND numbers
   - Consider adding special character requirement

3. **HTTPS**
   - Use HTTPS in production (Railway provides this automatically)
   - Tokens sent over HTTP are insecure

4. **Rate Limiting**
   - Consider adding rate limiting to login endpoint
   - Prevent brute force attacks

5. **Token Expiration**
   - Default: 7 days
   - Consider shorter expiration for sensitive apps
   - Implement refresh tokens for longer sessions

## Next Steps

1. ✅ Phase 1 Complete: Authentication & User Management

2. **Phase 2: Update Job Filtering** (Next)
   - Modify job listing endpoints to filter by user preferences
   - Add user-specific applied/rejected tracking
   - Update scraper to classify jobs by type/experience

3. **Phase 3: Frontend Updates**
   - Add login/register pages
   - Add settings page for preferences
   - Update job dashboard with user-specific data

4. **Phase 4: Testing**
   - Test with multiple users
   - Verify data isolation
   - Performance testing

## Support

If you encounter issues:

1. Check logs: `docker logs <container_id>` or Railway logs
2. Verify environment variables are set
3. Test database connection
4. Check API documentation: `http://localhost:8000/docs`

## Rollback

If you need to rollback:

```sql
-- Drop new tables (CAUTION: Deletes all user data!)
DROP TABLE IF EXISTS user_job_interactions CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Remove new job columns
ALTER TABLE jobs
DROP COLUMN IF EXISTS job_type,
DROP COLUMN IF EXISTS experience_level,
DROP COLUMN IF EXISTS remote_type,
DROP COLUMN IF EXISTS salary_range,
DROP COLUMN IF EXISTS description;
```

---

**Congratulations!** 🎉

Your job scraper now supports multiple users with individual preferences and tracking!
