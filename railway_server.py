#!/usr/bin/env python3
"""
Ultra-minimal LinkedIn Job Manager for Railway
Just serves existing job database - no React build needed
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os
from datetime import datetime
import asyncio

# Import database functionality
try:
    from database_models import JobDatabase
    DATABASE_AVAILABLE = True
    print("✅ Database models imported successfully")
except ImportError as e:
    print(f"⚠️  Database models not available: {e}")
    DATABASE_AVAILABLE = False

# Import authentication routes
try:
    from auth_routes import router as auth_router
    from auth_utils import get_current_user
    AUTH_AVAILABLE = True
    print("✅ Authentication routes imported successfully")
except ImportError as e:
    print(f"⚠️  Authentication routes not available: {e}")
    AUTH_AVAILABLE = False
    # Define a dummy get_current_user if auth is not available
    async def get_current_user():
        raise HTTPException(status_code=501, detail="Authentication not available")

app = FastAPI(title="LinkedIn Job Manager", version="1.0.0")

# Include authentication router if available
if AUTH_AVAILABLE:
    app.include_router(auth_router)
    print("✅ Authentication routes registered")

# Initialize database
db = None
if DATABASE_AVAILABLE:
    db = JobDatabase()
    print(f"🗄️  Database initialization: {'PostgreSQL' if db.use_postgres else 'JSON fallback'}")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React app static files
if os.path.exists("job-manager-ui/dist"):
    app.mount("/assets", StaticFiles(directory="job-manager-ui/dist/assets"), name="assets")

# Simple HTML interface
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>LinkedIn Job Manager</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; }
        .job-card { 
            background: white; 
            margin: 10px 0; 
            padding: 15px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .job-title { font-size: 18px; font-weight: bold; color: #0066cc; }
        .job-company { color: #666; margin: 5px 0; }
        .job-location { color: #888; font-size: 14px; }
        .applied { background: #e8f5e8; border-left: 4px solid #4caf50; }
        .new-job { background: #fff3e0; border-left: 4px solid #ff9800; }
        .stats { 
            background: white; 
            padding: 20px; 
            margin-bottom: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-item { display: inline-block; margin: 0 20px; }
        .stat-number { font-size: 24px; font-weight: bold; color: #0066cc; }
        .button { 
            background: #0066cc; 
            color: white; 
            padding: 8px 16px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer;
            margin: 5px;
        }
        .button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 LinkedIn Job Manager</h1>
        <div class="stats" id="stats">Loading...</div>
        <div id="jobs">Loading jobs...</div>
    </div>
    
    <script>
        async function loadJobs() {
            try {
                const response = await fetch('/jobs_database.json');
                const jobs = await response.json();
                displayJobs(jobs);
            } catch (error) {
                document.getElementById('jobs').innerHTML = '<p>Error loading jobs: ' + error.message + '</p>';
            }
        }
        
        function displayJobs(jobs) {
            const jobsArray = Object.values(jobs);
            const total = jobsArray.length;
            const applied = jobsArray.filter(j => j.applied).length;
            const newJobs = jobsArray.filter(j => j.is_new).length;
            
            document.getElementById('stats').innerHTML = `
                <div class="stat-item">
                    <div class="stat-number">${total}</div>
                    <div>Total Jobs</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${applied}</div>
                    <div>Applied</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">${newJobs}</div>
                    <div>New</div>
                </div>
            `;
            
            let html = '';
            jobsArray.forEach(job => {
                const cardClass = job.applied ? 'applied' : (job.is_new ? 'new-job' : '');
                html += `
                    <div class="job-card ${cardClass}">
                        <div class="job-title">${job.title}</div>
                        <div class="job-company">${job.company}</div>
                        <div class="job-location">${job.location}</div>
                        <div style="margin-top: 10px;">
                            <button class="button" onclick="toggleApplied('${job.id}', ${!job.applied})">
                                ${job.applied ? 'Mark Not Applied' : 'Mark Applied'}
                            </button>
                            <a href="${job.job_url}" target="_blank" style="text-decoration: none;">
                                <button class="button">View Job</button>
                            </a>
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('jobs').innerHTML = html;
        }
        
        async function toggleApplied(jobId, applied) {
            try {
                const response = await fetch('/update_job', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ job_id: jobId, applied: applied })
                });
                
                if (response.ok) {
                    loadJobs(); // Reload jobs
                } else {
                    alert('Error updating job');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        // Load jobs on page load
        loadJobs();
    </script>
</body>
</html>
"""

class JobUpdateRequest(BaseModel):
    job_id: str
    applied: Optional[bool] = None
    rejected: Optional[bool] = None

class SyncJobsRequest(BaseModel):
    jobs_data: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    if db and DATABASE_AVAILABLE:
        try:
            await db.init_database()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"⚠️  Database initialization failed: {e}")

async def load_jobs():
    """Load jobs from database ONLY - no JSON fallback"""
    if not db or not DATABASE_AVAILABLE:
        print(f"❌ DEBUG: Database not available - db: {db}, DATABASE_AVAILABLE: {DATABASE_AVAILABLE}")
        raise HTTPException(status_code=500, detail="Database not available")

    print(f"🔄 DEBUG: load_jobs() called - use_postgres: {db.use_postgres if db else 'N/A'}")
    print(f"🔄 DEBUG: DATABASE_URL exists: {bool(os.environ.get('DATABASE_URL'))}")

    try:
        jobs_data = await db.get_all_jobs()

        # DEBUG: Check what we're returning and WHERE it came from
        actual_jobs = {k: v for k, v in jobs_data.items() if not k.startswith('_')}
        rejected_jobs = {k: v for k, v in actual_jobs.items() if v.get('rejected', False)}

        print(f"🔄 DEBUG: load_jobs() returning {len(actual_jobs)} jobs, {len(rejected_jobs)} rejected")
        print(f"🔍 DEBUG: Data source - PostgreSQL: {db.use_postgres}, JSON fallback: {not db.use_postgres}")

        if len(rejected_jobs) > 0:
            print(f"🚫 DEBUG: Rejected jobs being returned:")
            for job_id, job in rejected_jobs.items():
                print(f"   {job_id[:12]}... - rejected: {job.get('rejected')}, applied: {job.get('applied')}")
        else:
            print(f"📋 DEBUG: No rejected jobs found in returned data")

        return jobs_data
    except Exception as e:
        print(f"❌ DEBUG: Database load failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database load failed: {str(e)}")

async def save_jobs(jobs_data):
    """Save jobs to database ONLY - no JSON fallback"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        # For save operations, we sync the data to database
        result = await db.sync_jobs_from_scraper(jobs_data)
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"Database save failed: {result['error']}")
        return True
    except Exception as e:
        print(f"❌ Database save failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database save failed: {str(e)}")

@app.get("/")
async def home():
    """Serve the React app or fallback HTML interface"""
    if os.path.exists("job-manager-ui/dist/index.html"):
        return FileResponse("job-manager-ui/dist/index.html")
    else:
        return HTMLResponse(content=HTML_INTERFACE)

@app.get("/health")
async def health():
    """Health check"""
    jobs = await load_jobs()
    return {
        "status": "healthy",
        "jobs_count": len([k for k in jobs.keys() if not k.startswith("_")]),
        "database_type": "postgresql" if (db and db.use_postgres) else "json_fallback"
    }

async def get_current_user_optional(authorization: Optional[str] = Header(None)):
    """Optional authentication - returns user if authenticated, None otherwise"""
    if not authorization or not AUTH_AVAILABLE:
        return None

    try:
        from auth_utils import decode_access_token
        # Remove 'Bearer ' prefix
        token = authorization.replace("Bearer ", "")
        payload = decode_access_token(token)
        return payload
    except:
        return None

@app.get("/api/jobs")
async def get_jobs_api(current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    """Get all jobs from database - filtered by user preferences if authenticated"""
    all_jobs = await load_jobs()

    # If user is not authenticated, return all jobs
    if not current_user:
        return all_jobs

    # If authenticated, filter by user preferences AND user interactions
    try:
        if AUTH_AVAILABLE:
            from user_database import UserDatabase
            user_db = UserDatabase()
            preferences = await user_db.get_user_preferences(current_user['user_id'])

            # Get this user's job interactions to filter out jobs they've already seen/interacted with
            conn = await db.get_connection()
            user_interactions = {}
            user_signatures = set()  # Company+Title pairs user has already applied/rejected to
            if conn:
                try:
                    # Get job IDs user has interacted with
                    interactions = await conn.fetch("""
                        SELECT job_id, applied, rejected, saved
                        FROM user_job_interactions
                        WHERE user_id = $1
                    """, current_user['user_id'])

                    user_interactions = {
                        row['job_id']: {
                            'applied': row['applied'],
                            'rejected': row['rejected'],
                            'saved': row['saved']
                        }
                        for row in interactions
                    }

                    # Also get job signatures (company+title) user has applied to
                    # This catches cases where job was deleted and re-scraped with new ID
                    signatures = await conn.fetch("""
                        SELECT DISTINCT js.company, js.normalized_title
                        FROM job_signatures js
                        WHERE EXISTS (
                            SELECT 1 FROM user_job_interactions uji
                            WHERE uji.user_id = $1
                            AND uji.job_id = js.original_job_id
                            AND (uji.applied = TRUE OR uji.rejected = TRUE)
                        )
                    """, current_user['user_id'])

                    for sig in signatures:
                        signature_key = f"{sig['company'].lower()}|{sig['normalized_title'].lower()}"
                        user_signatures.add(signature_key)

                    print(f"[FILTER] User {current_user['user_id']} has {len(user_interactions)} job interactions, {len(user_signatures)} job signatures")
                except Exception as e:
                    print(f"[FILTER] Error loading user interactions: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    await conn.close()

            if preferences:
                filtered_jobs = {}

                for job_id, job_data in all_jobs.items():
                    # Skip metadata
                    if job_id.startswith('_'):
                        filtered_jobs[job_id] = job_data
                        continue

                    # Merge user interaction status into job data
                    if job_id in user_interactions:
                        interaction = user_interactions[job_id]
                        job_data = {**job_data}  # Create a copy
                        job_data['applied'] = interaction['applied']
                        job_data['rejected'] = interaction['rejected']
                        job_data['saved'] = interaction['saved']

                    # Check if this is a repost of a job they already applied to
                    company = job_data.get('company', '').strip()
                    title = job_data.get('title', '').strip()
                    is_repost = False
                    if company and title:
                        # Normalize title (remove senior, junior, etc.)
                        normalized_title = db.normalize_job_title(title) if db else title.lower()
                        signature_key = f"{company.lower()}|{normalized_title.lower()}"

                        if signature_key in user_signatures and job_id not in user_interactions:
                            # This is a repost - mark as applied/rejected automatically
                            is_repost = True
                            job_data = {**job_data}
                            job_data['applied'] = True  # Auto-mark reposts as applied
                            print(f"[FILTER] Auto-marking repost {job_id[:12]}... as applied - '{title}' at {company}")

                    # Get job details for filtering
                    title_lower = title.lower()
                    description = job_data.get('description', '').lower()
                    location = job_data.get('location', '').lower()
                    title_desc = f"{title_lower} {description} {location}"

                    # Filter by job type - check title/description if job_type field missing
                    if preferences.get('job_types'):
                        job_type = job_data.get('job_type')

                        # If job_type field exists, use it
                        if job_type and job_type not in preferences['job_types']:
                            continue
                        # If job_type field missing, detect from title/description
                        elif not job_type:
                            type_match = False
                            for pref_type in preferences['job_types']:
                                if pref_type == 'software':
                                    # More specific software keywords to avoid catching HR/other engineers
                                    sw_keywords = [
                                        'software engineer', 'software developer', 'developer', 'programmer',
                                        'full stack', 'full-stack', 'backend', 'frontend', 'front-end', 'back-end',
                                        'react', 'angular', 'vue', 'python', 'javascript', 'typescript', 'java developer',
                                        'node.js', 'nodejs', '.net', 'dotnet', 'web developer', 'mobile developer',
                                        'devops', 'sre', 'cloud engineer', 'data engineer', 'ml engineer', 'ai engineer',
                                        'software architect', 'tech lead'
                                    ]
                                    # Exclude HR/non-software jobs
                                    if any(exclude in title_lower for exclude in ['hr ', ' hr', 'human resources', 'recruitment', 'talent acquisition']):
                                        break
                                    if any(kw in title_desc for kw in sw_keywords):
                                        type_match = True
                                        break
                                elif pref_type == 'hr':
                                    hr_keywords = [' hr ', 'human resources', 'recruiter', 'recruitment', 'recruiting', 'talent acquisition', 'talent', 'people operations', 'people', 'hr officer', 'hr coordinator', 'hr generalist', 'hr manager', 'hr business partner', 'hr specialist', 'people partner', 'talent sourcer', 'hr assistant']
                                    # Also check for HR at start/end of title
                                    if title.startswith('hr ') or title.endswith(' hr') or ' hr ' in title:
                                        type_match = True
                                        break
                                    if any(kw in title_desc for kw in hr_keywords):
                                        type_match = True
                                        break
                                elif pref_type == 'cybersecurity' or pref_type == 'security' or pref_type == 'soc':
                                    cyber_keywords = ['soc analyst', 'cybersecurity', 'cyber security', 'security analyst', 'information security', 'infosec', 'security engineer', 'security operations', 'incident response', 'threat', 'vulnerability']
                                    if any(kw in title_desc for kw in cyber_keywords):
                                        type_match = True
                                        break
                                elif pref_type == 'sales' or pref_type == 'business_development' or pref_type == 'account_management':
                                    sales_keywords = ['account manager', 'account executive', 'bdr', 'business development', 'sales development', 'sdr', 'sales representative', 'sales', 'customer success', 'account management', 'revenue']
                                    if any(kw in title_desc for kw in sales_keywords):
                                        type_match = True
                                        break
                                elif pref_type == 'finance' or pref_type == 'accounting' or pref_type == 'financial_analysis':
                                    finance_keywords = ['fp&a', 'financial planning', 'financial analyst', 'fund accounting', 'fund accountant', 'fund operations', 'credit analyst', 'accounting analyst', 'finance analyst', 'treasury analyst', 'investment accounting', 'accountant', 'financial reporting', 'management accountant']
                                    if any(kw in title_desc for kw in finance_keywords):
                                        type_match = True
                                        break
                            if not type_match:
                                continue

                    # Filter by experience level - detect from title if field missing
                    if preferences.get('experience_levels'):
                        job_level = job_data.get('experience_level')

                        if job_level and job_level not in preferences['experience_levels']:
                            continue
                        elif not job_level:
                            # Detect level from title
                            level_match = False
                            if any(lvl in ['entry', 'junior'] for lvl in preferences['experience_levels']):
                                # For HR jobs, "Manager" doesn't always mean senior
                                # Check for truly senior indicators
                                senior_indicators = ['senior', 'sr.', 'lead', 'principal', 'staff', 'director', 'head of', 'chief', 'vp']
                                # Exception: HR Manager, Talent Manager, People Manager are often mid-level
                                hr_manager_titles = ['hr manager', 'talent manager', 'people manager', 'recruitment manager', 'talent acquisition manager']

                                is_hr_manager = any(hr_title in title_lower for hr_title in hr_manager_titles)
                                has_senior_indicator = any(word in title for word in senior_indicators)

                                if is_hr_manager or not has_senior_indicator:
                                    level_match = True
                            if any(lvl in ['mid', 'senior'] for lvl in preferences['experience_levels']):
                                level_match = True  # Allow mid/senior to see all

                            if not level_match:
                                continue

                    # Filter by country - check location string if country field missing
                    if preferences.get('preferred_countries'):
                        job_country = job_data.get('country')

                        if job_country and job_country not in preferences['preferred_countries']:
                            continue
                        elif not job_country:
                            # Check location string
                            country_match = False
                            for country in preferences['preferred_countries']:
                                if country.lower() in location or country.lower() == 'remote' and 'remote' in location:
                                    country_match = True
                                    break
                            if not country_match:
                                continue

                    # Check excluded keywords
                    if preferences.get('excluded_keywords'):
                        if any(keyword.lower() in title_desc for keyword in preferences['excluded_keywords']):
                            continue

                    # Check included keywords - OPTIONAL if job_type already matched
                    # If user has specific keywords, use them as additional boost, not hard requirement
                    # This allows HR jobs to show even if they don't exactly match the keyword list
                    # Keywords are now just preferences, not filters

                    # Filter by remote if specified
                    if preferences.get('remote_only'):
                        if not job_data.get('is_remote', False) and 'remote' not in location:
                            continue

                    # Filter by easy apply if specified
                    if preferences.get('easy_apply_only'):
                        if not job_data.get('easy_apply', False):
                            continue

                    filtered_jobs[job_id] = job_data

                return filtered_jobs
            else:
                # User authenticated but no preferences - merge interactions with all jobs
                merged_jobs = {}
                for job_id, job_data in all_jobs.items():
                    if job_id in user_interactions:
                        interaction = user_interactions[job_id]
                        job_data = {**job_data}
                        job_data['applied'] = interaction['applied']
                        job_data['rejected'] = interaction['rejected']
                        job_data['saved'] = interaction['saved']
                    merged_jobs[job_id] = job_data
                return merged_jobs
    except Exception as e:
        print(f"Error filtering jobs by preferences: {e}")
        # On error, return all jobs

    return all_jobs

@app.get("/api/jobs/{job_id}")
async def get_job_by_id(job_id: str):
    """Get specific job by ID for debugging"""
    jobs = await load_jobs()
    if job_id in jobs:
        return {"job_id": job_id, "job_data": jobs[job_id]}
    else:
        raise HTTPException(status_code=404, detail="Job not found")

@app.get("/api/debug/rejected-jobs")
async def debug_rejected_jobs():
    """Debug endpoint to check rejected jobs in database"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        # Get all jobs directly from database
        all_jobs = await db.get_all_jobs()

        # Filter rejected jobs
        rejected_jobs = {}
        all_jobs_count = 0

        for job_id, job_data in all_jobs.items():
            if job_id.startswith('_'):
                continue

            all_jobs_count += 1
            if job_data.get('rejected', False):
                rejected_jobs[job_id] = {
                    'id': job_id,
                    'title': job_data.get('title', 'Unknown'),
                    'company': job_data.get('company', 'Unknown'),
                    'rejected': job_data.get('rejected'),
                    'applied': job_data.get('applied', False)
                }

        return {
            "total_jobs": all_jobs_count,
            "rejected_count": len(rejected_jobs),
            "rejected_jobs": rejected_jobs,
            "message": f"Found {len(rejected_jobs)} rejected jobs out of {all_jobs_count} total"
        }

    except Exception as e:
        print(f"❌ Debug rejected jobs failed: {e}")
        raise HTTPException(status_code=500, detail=f"Debug failed: {str(e)}")

@app.delete("/api/jobs/clear-all")
async def clear_all_jobs():
    """Clear all jobs from database - USE WITH CAUTION"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        # Get connection
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Count before deletion
        total_before = await conn.fetchval("SELECT COUNT(*) FROM jobs")

        # Delete all jobs
        await conn.execute("DELETE FROM jobs")

        # Count after deletion
        total_after = await conn.fetchval("SELECT COUNT(*) FROM jobs")

        await conn.close()

        return {
            "success": True,
            "message": "All jobs cleared from database",
            "jobs_deleted": total_before,
            "jobs_remaining": total_after
        }
    except Exception as e:
        print(f"❌ Database clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear database: {str(e)}")

@app.delete("/api/jobs/by-country/{country}")
async def delete_jobs_by_country(country: str):
    """Delete all jobs from a specific country"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        # Get connection
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Count before deletion
        total_before = await conn.fetchval(
            "SELECT COUNT(*) FROM jobs WHERE country = $1",
            country
        )

        # Delete jobs from specified country
        await conn.execute(
            "DELETE FROM jobs WHERE country = $1",
            country
        )

        # Count after deletion to verify
        total_after = await conn.fetchval(
            "SELECT COUNT(*) FROM jobs WHERE country = $1",
            country
        )

        # Get total jobs remaining
        total_jobs = await conn.fetchval("SELECT COUNT(*) FROM jobs")

        await conn.close()

        return {
            "success": True,
            "message": f"Deleted all jobs from {country}",
            "country": country,
            "jobs_deleted": total_before,
            "jobs_remaining_in_country": total_after,
            "total_jobs_in_database": total_jobs
        }
    except Exception as e:
        print(f"❌ Delete by country failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete jobs: {str(e)}")

@app.post("/api/jobs/enforce-country-limit")
async def enforce_country_limit(max_jobs: int = 300):
    """Enforce the max jobs per country limit by removing oldest jobs"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        # Get connection
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Get all jobs grouped by country
        all_jobs = await load_jobs()

        jobs_by_country = {}
        deleted_count = 0

        # Group jobs by country
        for job_id, job_data in all_jobs.items():
            if job_id.startswith("_"):
                continue

            country = job_data.get("country", "Unknown")
            if country not in jobs_by_country:
                jobs_by_country[country] = []

            jobs_by_country[country].append({
                "id": job_id,
                "scraped_at": job_data.get("scraped_at", ""),
                "data": job_data
            })

        # For each country, keep only the most recent max_jobs
        for country, country_jobs in jobs_by_country.items():
            if len(country_jobs) > max_jobs:
                # Sort by scraped_at timestamp (most recent first)
                country_jobs.sort(key=lambda x: x["scraped_at"], reverse=True)

                # Keep only the first max_jobs
                jobs_to_keep = country_jobs[:max_jobs]
                jobs_to_delete = country_jobs[max_jobs:]

                print(f"   ✂️ {country}: Keeping {len(jobs_to_keep)} jobs, deleting {len(jobs_to_delete)} old jobs")

                # Delete old jobs
                for job in jobs_to_delete:
                    await conn.execute(
                        "DELETE FROM jobs WHERE id = $1",
                        job["id"]
                    )
                    deleted_count += 1

        # Get final count
        total_jobs = await conn.fetchval("SELECT COUNT(*) FROM jobs")

        await conn.close()

        return {
            "success": True,
            "message": f"Enforced {max_jobs} jobs per country limit",
            "jobs_deleted": deleted_count,
            "total_jobs_remaining": total_jobs,
            "countries_processed": len(jobs_by_country)
        }
    except Exception as e:
        print(f"❌ Enforce limit failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enforce limit: {str(e)}")

@app.post("/api/migrate-schema")
async def migrate_database_schema():
    """Run database migrations to add missing columns"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        migrations = []

        # Add missing columns
        try:
            await conn.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS country VARCHAR(100);")
            migrations.append("Added country column")
        except Exception as e:
            migrations.append(f"Country column: {str(e)}")

        try:
            await conn.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS job_type VARCHAR(50);")
            migrations.append("Added job_type column")
        except Exception as e:
            migrations.append(f"Job_type column: {str(e)}")

        try:
            await conn.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS experience_level VARCHAR(50);")
            migrations.append("Added experience_level column")
        except Exception as e:
            migrations.append(f"Experience_level column: {str(e)}")

        try:
            await conn.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS excluded BOOLEAN DEFAULT FALSE;")
            migrations.append("Added excluded column")
        except Exception as e:
            migrations.append(f"Excluded column: {str(e)}")

        # Create indexes
        try:
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_country ON jobs(country);")
            migrations.append("Created country index")
        except Exception as e:
            migrations.append(f"Country index: {str(e)}")

        try:
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_job_type ON jobs(job_type);")
            migrations.append("Created job_type index")
        except Exception as e:
            migrations.append(f"Job_type index: {str(e)}")

        try:
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_experience_level ON jobs(experience_level);")
            migrations.append("Created experience_level index")
        except Exception as e:
            migrations.append(f"Experience_level index: {str(e)}")

        await conn.close()

        return {
            "success": True,
            "message": "Database schema migrated successfully",
            "migrations": migrations
        }
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@app.post("/api/backfill-job-fields")
async def backfill_job_fields():
    """Backfill country, job_type, experience_level for existing jobs (run once after migration)"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        from linkedin_job_scraper import LinkedInJobScraper

        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Get all jobs without country
        jobs = await conn.fetch("SELECT id, title, location FROM jobs WHERE country IS NULL OR job_type IS NULL")

        print(f"📊 Backfilling {len(jobs)} jobs...")

        scraper = LinkedInJobScraper(headless=False)  # Don't need browser
        updated = 0

        for job in jobs:
            try:
                job_id = job['id']
                title = job['title']
                location = job['location'] or ""

                # Extract fields
                country = scraper.get_country_from_location(location)
                job_type = scraper.detect_job_type(title)
                experience_level = scraper.detect_experience_level(title)

                # Update
                await conn.execute("""
                    UPDATE jobs
                    SET country = $2, job_type = $3, experience_level = $4
                    WHERE id = $1
                """, job_id, country, job_type, experience_level)

                updated += 1

                if updated % 50 == 0:
                    print(f"   ✅ Updated {updated}/{len(jobs)} jobs...")

            except Exception as e:
                print(f"   ⚠️ Error updating job {job_id}: {e}")
                continue

        # Get distribution
        country_counts = await conn.fetch("""
            SELECT country, COUNT(*) as count
            FROM jobs
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY count DESC
        """)

        type_counts = await conn.fetch("""
            SELECT job_type, COUNT(*) as count
            FROM jobs
            WHERE job_type IS NOT NULL
            GROUP BY job_type
            ORDER BY count DESC
        """)

        await conn.close()
        scraper.close()

        return {
            "success": True,
            "message": f"Backfilled {updated} jobs",
            "jobs_updated": updated,
            "jobs_total": len(jobs),
            "country_distribution": [{"country": r['country'], "count": r['count']} for r in country_counts],
            "type_distribution": [{"type": r['job_type'], "count": r['count']} for r in type_counts]
        }

    except Exception as e:
        print(f"❌ Backfill failed: {e}")
        raise HTTPException(status_code=500, detail=f"Backfill failed: {str(e)}")

@app.get("/jobs_database.json")
async def get_jobs_legacy():
    """Legacy endpoint - redirects to proper API"""
    return await load_jobs()

@app.post("/api/update_job")
async def update_job_api(request: JobUpdateRequest, current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    """Update job applied and/or rejected status - DATABASE ONLY"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        print(f"🔄 DEBUG: Updating job {request.job_id} - applied: {request.applied}, rejected: {request.rejected}")

        # Update the global jobs table (for backward compatibility)
        success = await db.update_job_status(
            job_id=request.job_id,
            applied=request.applied,
            rejected=request.rejected
        )

        # If authenticated, also update user_job_interactions table
        if current_user and success:
            from user_database import UserDatabase
            user_db = UserDatabase()

            user_id = current_user.get('user_id')

            if user_id:
                conn = await db.get_connection()
                if conn:
                    try:
                        # Update or insert user interaction
                        if request.applied:
                            await conn.execute("""
                                INSERT INTO user_job_interactions (user_id, job_id, applied, applied_at, created_at, updated_at)
                                VALUES ($1, $2, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                ON CONFLICT (user_id, job_id) DO UPDATE SET
                                    applied = TRUE,
                                    applied_at = CURRENT_TIMESTAMP,
                                    updated_at = CURRENT_TIMESTAMP
                            """, user_id, request.job_id)
                            print(f"✅ Updated user_job_interactions for user {user_id}: applied")

                        if request.rejected:
                            await conn.execute("""
                                INSERT INTO user_job_interactions (user_id, job_id, rejected, rejected_at, created_at, updated_at)
                                VALUES ($1, $2, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                ON CONFLICT (user_id, job_id) DO UPDATE SET
                                    rejected = TRUE,
                                    rejected_at = CURRENT_TIMESTAMP,
                                    updated_at = CURRENT_TIMESTAMP
                            """, user_id, request.job_id)
                            print(f"✅ Updated user_job_interactions for user {user_id}: rejected")
                    finally:
                        await conn.close()

        if success:
            print(f"✅ DEBUG: Job {request.job_id} updated successfully in database")
            return {"success": True, "message": f"Job {request.job_id} updated"}
        else:
            print(f"❌ DEBUG: Job {request.job_id} not found in database")
            raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        print(f"❌ DEBUG: Database update failed for job {request.job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")

@app.post("/update_job")
async def update_job_legacy(request: JobUpdateRequest, current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    """Legacy endpoint - redirects to proper API"""
    return await update_job_api(request, current_user)

@app.post("/sync_jobs")
async def sync_jobs(request: SyncJobsRequest):
    """Sync jobs from local scraper to database - DATABASE ONLY"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        # Use database sync method
        result = await db.sync_jobs_from_scraper(request.jobs_data)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return {
            "success": True,
            "message": f"Synced jobs successfully to database",
            "new_jobs": result.get("new_jobs", 0),
            "new_software": result.get("new_software", 0),
            "new_hr": result.get("new_hr", 0),
            "new_cybersecurity": result.get("new_cybersecurity", 0),
            "new_sales": result.get("new_sales", 0),
            "new_finance": result.get("new_finance", 0),
            "updated_jobs": result.get("updated_jobs", 0),
            "skipped_reposts": result.get("skipped_reposts", 0)
        }
    except Exception as e:
        print(f"❌ Database sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database sync failed: {str(e)}")

@app.post("/api/admin/clear-user-interactions")
async def clear_user_interactions():
    """Clear user_job_interactions table to start fresh tracking"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Get count before clearing
        before_count = await conn.fetchval("SELECT COUNT(*) FROM user_job_interactions")

        # Clear all interactions
        await conn.execute("DELETE FROM user_job_interactions")

        after_count = await conn.fetchval("SELECT COUNT(*) FROM user_job_interactions")

        await conn.close()

        return {
            "success": True,
            "message": "Cleared user interactions - fresh start for accurate tracking",
            "interactions_deleted": before_count,
            "interactions_remaining": after_count,
            "note": "Going forward, each user's apply/reject will be tracked individually"
        }

    except Exception as e:
        print(f"❌ Error clearing interactions: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to clear interactions: {str(e)}")

@app.post("/api/admin/fix-analytics")
async def fix_analytics_api():
    """Fix analytics by migrating jobs to user_job_interactions table"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        print("🔍 Checking user_job_interactions table...")

        # Check if table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'user_job_interactions'
            )
        """)

        if not table_exists:
            print("❌ user_job_interactions table does not exist!")
            print("   Running multi-user migration...")

            # Read and execute migration
            with open('database_migrations/001_add_multi_user_support.sql', 'r') as f:
                migration_sql = f.read()

            await conn.execute(migration_sql)
            print("✅ Migration executed successfully")

        # Check current interaction count
        interaction_count = await conn.fetchval("SELECT COUNT(*) FROM user_job_interactions")
        print(f"📊 Current interactions: {interaction_count}")

        print("🔄 Migrating applied/rejected jobs...")

        # Get all users
        users = await conn.fetch("SELECT id, username FROM users")
        results = []

        for user in users:
            user_id = user['id']
            username = user['username']

            # Count jobs to migrate
            applied_jobs = await conn.fetchval("SELECT COUNT(*) FROM jobs WHERE applied = TRUE")
            rejected_jobs = await conn.fetchval("SELECT COUNT(*) FROM jobs WHERE rejected = TRUE")

            # Migrate applied jobs
            await conn.execute("""
                INSERT INTO user_job_interactions (user_id, job_id, applied, applied_at, created_at, updated_at)
                SELECT $1, id, TRUE, COALESCE(updated_at, created_at), COALESCE(updated_at, created_at), CURRENT_TIMESTAMP
                FROM jobs
                WHERE applied = TRUE
                ON CONFLICT (user_id, job_id) DO UPDATE SET
                    applied = TRUE,
                    applied_at = COALESCE(EXCLUDED.applied_at, user_job_interactions.applied_at),
                    updated_at = CURRENT_TIMESTAMP
            """, user_id)

            # Migrate rejected jobs
            await conn.execute("""
                INSERT INTO user_job_interactions (user_id, job_id, rejected, rejected_at, created_at, updated_at)
                SELECT $1, id, TRUE, COALESCE(updated_at, created_at), COALESCE(updated_at, created_at), CURRENT_TIMESTAMP
                FROM jobs
                WHERE rejected = TRUE
                ON CONFLICT (user_id, job_id) DO UPDATE SET
                    rejected = TRUE,
                    rejected_at = COALESCE(EXCLUDED.rejected_at, user_job_interactions.rejected_at),
                    updated_at = CURRENT_TIMESTAMP
            """, user_id)

            results.append({
                "username": username,
                "applied_migrated": applied_jobs,
                "rejected_migrated": rejected_jobs
            })

            print(f"✅ {username}: Migrated {applied_jobs} applied, {rejected_jobs} rejected")

        # Get final count
        final_count = await conn.fetchval("SELECT COUNT(*) FROM user_job_interactions")

        await conn.close()

        return {
            "success": True,
            "message": "Analytics fixed successfully",
            "table_existed": table_exists,
            "interactions_before": interaction_count,
            "interactions_after": final_count,
            "users_processed": len(results),
            "results": results
        }

    except Exception as e:
        print(f"❌ Error fixing analytics: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fix analytics: {str(e)}")

@app.post("/api/admin/update-all-user-countries")
async def update_all_user_countries():
    """Update all users to include all countries being scraped"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        from user_database import UserDatabase
        user_db = UserDatabase()

        # All countries being scraped
        all_countries = [
            "Ireland", "Spain", "Panama", "Chile",
            "Netherlands", "Germany", "Sweden",
            "Belgium", "Denmark", "Luxembourg"
        ]

        results = []

        # Get all users
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        users = await conn.fetch("SELECT id, username FROM users")

        for user in users:
            user_id = user['id']
            username = user['username']

            # Get current preferences
            prefs = await user_db.get_user_preferences(user_id)

            if prefs:
                # Update to include all countries
                prefs['preferred_countries'] = all_countries

                success = await user_db.update_user_preferences(user_id, prefs)

                results.append({
                    "user_id": user_id,
                    "username": username,
                    "success": success,
                    "countries_set": all_countries
                })

                print(f"✅ Updated {username} to include all {len(all_countries)} countries")

        await conn.close()

        return {
            "success": True,
            "message": f"Updated {len(results)} users to include all countries",
            "results": results,
            "countries": all_countries
        }

    except Exception as e:
        print(f"❌ Failed to update user countries: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")

@app.post("/api/admin/create-glo-user")
async def create_glo_user_api():
    """Create Glo user for cybersecurity jobs"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        from user_database import UserDatabase

        user_db = UserDatabase()

        # Check if user already exists
        existing_user = await user_db.get_user_by_username("glo")
        if existing_user:
            return {
                "success": False,
                "message": "User 'glo' already exists",
                "user_id": existing_user['id']
            }

        print("🎯 Creating Glo user for cybersecurity jobs...")

        # Create user
        user = await user_db.create_user(
            username="glo",
            email="glo@jobtracker.local",
            password="GloSecure2024!",
            full_name="Glo - Cybersecurity",
            is_admin=False
        )

        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")

        print(f"✅ User created: {user['username']} (ID: {user['id']})")

        # Set cybersecurity preferences
        cyber_preferences = {
            "job_types": ["cybersecurity", "security", "soc"],
            "keywords": [
                "SOC Analyst", "Cybersecurity Analyst", "Security Analyst",
                "Information Security Analyst", "Junior SOC Analyst",
                "Security Operations", "Incident Response Analyst",
                "Analista SOC", "Analista de Ciberseguridad", "Analista de Seguridad"
            ],
            "excluded_keywords": ["Physical Security", "Security Guard"],
            "experience_levels": ["junior", "mid", "senior"],
            "exclude_senior": False,
            "preferred_countries": ["Spain", "Panama"],
            "preferred_cities": ["Madrid", "Barcelona", "Panama City"],
            "excluded_companies": [],
            "preferred_companies": [],
            "easy_apply_only": False,
            "remote_only": False,
            "email_notifications": True,
            "daily_digest": False
        }

        success = await user_db.update_user_preferences(
            user_id=user['id'],
            preferences=cyber_preferences
        )

        if not success:
            print("⚠️ User created but preferences not set")
        else:
            print("✅ Preferences set successfully")

        return {
            "success": True,
            "message": "Glo user created successfully",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "full_name": user['full_name']
            },
            "credentials": {
                "username": "glo",
                "password": "GloSecure2024!"
            },
            "preferences": {
                "job_types": "Cybersecurity, Security, SOC",
                "countries": "Spain, Panama",
                "languages": "English + Spanish"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to create Glo user: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@app.post("/api/admin/create-sales-user")
async def create_sales_user_api():
    """Create Sales user for business development and sales jobs"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        from user_database import UserDatabase

        user_db = UserDatabase()

        # Check if user already exists
        existing_user = await user_db.get_user_by_username("sales")
        if existing_user:
            return {
                "success": False,
                "message": "User 'sales' already exists",
                "user_id": existing_user['id']
            }

        print("🎯 Creating Sales user for business development jobs...")

        # Create user
        user = await user_db.create_user(
            username="sales",
            email="sales@jobtracker.local",
            password="SalesPro2024!",
            full_name="Sales - Business Development",
            is_admin=False
        )

        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")

        print(f"✅ User created: {user['username']} (ID: {user['id']})")

        # Set sales preferences
        sales_preferences = {
            "job_types": ["sales", "business_development", "account_management"],
            "keywords": [
                "Account Manager", "Account Executive", "BDR",
                "Business Development Representative", "Sales Development Representative", "SDR",
                "Inside Sales", "Sales Representative", "Junior Account Executive",
                "SaaS Sales", "B2B Sales", "Customer Success Manager",
                "Account Management", "Business Development Manager"
            ],
            "excluded_keywords": ["Director", "VP", "Head of", "Chief", "Retail", "Insurance", "Real Estate"],
            "experience_levels": ["entry", "junior", "mid"],
            "exclude_senior": True,
            "preferred_countries": [
                "Ireland", "Spain", "Panama", "Chile",
                "Netherlands", "Germany", "Sweden", "Belgium",
                "Denmark", "Luxembourg"
            ],
            "preferred_cities": [],
            "excluded_companies": [],
            "preferred_companies": [],
            "easy_apply_only": False,
            "remote_only": False,
            "email_notifications": True,
            "daily_digest": False
        }

        success = await user_db.update_user_preferences(
            user_id=user['id'],
            preferences=sales_preferences
        )

        if not success:
            print("⚠️ User created but preferences not set")
        else:
            print("✅ Preferences set successfully")

        return {
            "success": True,
            "message": "Sales user created successfully",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "full_name": user['full_name']
            },
            "credentials": {
                "username": "sales",
                "password": "SalesPro2024!"
            },
            "preferences": {
                "job_types": "Sales, BDR, SDR, Account Executive",
                "countries": "All 10 countries",
                "focus": "SaaS, B2B Sales, Entry to Mid-Level"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to create Sales user: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@app.post("/api/admin/create-finance-user")
async def create_finance_user_api():
    """Create Finance user for FP&A, fund accounting, and credit analyst jobs"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        from user_database import UserDatabase

        user_db = UserDatabase()

        # Check if user already exists
        existing_user = await user_db.get_user_by_username("finance")
        if existing_user:
            return {
                "success": False,
                "message": "User 'finance' already exists",
                "user_id": existing_user['id']
            }

        print("🎯 Creating Finance user for FP&A and accounting jobs...")

        # Create user
        user = await user_db.create_user(
            username="finance",
            email="finance@jobtracker.local",
            password="FinancePro2024!",
            full_name="Finance - FP&A & Accounting",
            is_admin=False
        )

        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")

        print(f"✅ User created: {user['username']} (ID: {user['id']})")

        # Set finance preferences
        finance_preferences = {
            "job_types": ["finance", "accounting", "financial_analysis"],
            "keywords": [
                "FP&A Analyst", "FP&A", "Financial Planning and Analysis",
                "Financial Planning Analyst", "Financial Analyst", "Junior Financial Analyst",
                "Fund Accounting", "Fund Accountant", "Fund Accounting Associate",
                "Fund Administrator", "Investment Accounting", "Portfolio Accounting",
                "Fund Operations", "Fund Operations Analyst", "Fund Operations Associate",
                "Investment Operations", "Asset Management Operations",
                "Credit Analyst", "Credit Risk Analyst", "Junior Credit Analyst",
                "Financial Reporting", "Management Accountant", "Accountant",
                "Junior Accountant", "Accounting Analyst", "Finance Associate",
                "Finance Analyst", "Treasury Analyst", "Cash Management",
                "Corporate Finance", "Finance Business Partner", "Financial Reporting Analyst",
                "Financial Modeling", "Variance Analysis", "Budgeting Analyst", "Forecasting Analyst"
            ],
            "excluded_keywords": [
                "CFO", "Director", "VP", "Head of", "Chief",
                "10+ years", "15+ years", "Tax", "Audit Partner", "Managing Director"
            ],
            "experience_levels": ["entry", "junior", "mid"],
            "exclude_senior": True,
            "preferred_countries": [
                "Ireland", "United Kingdom",
                "Netherlands", "Germany", "Sweden", "Belgium",
                "Denmark", "Luxembourg"
            ],
            "preferred_cities": [],
            "excluded_companies": [],
            "preferred_companies": [],
            "easy_apply_only": False,
            "remote_only": False,
            "email_notifications": True,
            "daily_digest": False
        }

        success = await user_db.update_user_preferences(
            user_id=user['id'],
            preferences=finance_preferences
        )

        if not success:
            print("⚠️ User created but preferences not set")
        else:
            print("✅ Preferences set successfully")

        return {
            "success": True,
            "message": "Finance user created successfully",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "full_name": user['full_name']
            },
            "credentials": {
                "username": "finance",
                "password": "FinancePro2024!"
            },
            "preferences": {
                "job_types": "FP&A, Fund Accounting, Fund Operations, Credit Analyst",
                "countries": "8 English-speaking countries (excl. Panama, Spain, Chile)",
                "focus": "Finance, Accounting, Entry to Mid-Level"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Failed to create Finance user: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@app.get("/api/admin/user-activity")
async def get_user_activity():
    """Get user activity for last 24 hours"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Get recent activity (last 24 hours)
        recent_activity = await conn.fetch("""
            SELECT
                u.username,
                u.full_name,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE AND uji.applied_at > NOW() - INTERVAL '24 hours') as applied_24h,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE AND uji.rejected_at > NOW() - INTERVAL '24 hours') as rejected_24h,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE) as total_applied,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE) as total_rejected
            FROM users u
            LEFT JOIN user_job_interactions uji ON u.id = uji.user_id
            GROUP BY u.username, u.full_name
            ORDER BY u.username
        """)

        users = []
        for row in recent_activity:
            users.append({
                'username': row['username'],
                'full_name': row['full_name'],
                'applied_24h': row['applied_24h'],
                'rejected_24h': row['rejected_24h'],
                'total_applied': row['total_applied'],
                'total_rejected': row['total_rejected']
            })

        return {
            'success': True,
            'users': users,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Failed to get user activity: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get user activity: {str(e)}")

@app.post("/api/admin/backfill-rejected-signatures")
async def backfill_rejected_signatures():
    """Backfill job signatures for rejected jobs"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        print("🚀 Backfilling job signatures for rejected jobs...")

        # Connect to database
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Get all rejected jobs
        rejected_jobs = await conn.fetch("""
            SELECT id, title, company, country
            FROM jobs
            WHERE rejected = TRUE
            ORDER BY scraped_at DESC
        """)

        print(f"📊 Found {len(rejected_jobs)} rejected jobs")

        backfilled = 0
        errors = 0

        for job in rejected_jobs:
            try:
                # Add job signature
                success = await db.add_job_signature(
                    company=job['company'],
                    title=job['title'],
                    country=job['country'],
                    job_id=job['id']
                )

                if success:
                    backfilled += 1

            except Exception as e:
                print(f"⚠️  Error backfilling signature for job {job['id']}: {e}")
                errors += 1
                continue

        await conn.close()

        print(f"✅ Backfilled {backfilled} job signatures for rejected jobs")

        return {
            "success": True,
            "message": "Backfill completed successfully",
            "rejected_jobs_found": len(rejected_jobs),
            "signatures_created": backfilled,
            "errors": errors,
            "info": {
                "description": "Rejected jobs are now tracked",
                "benefit": "Companies that repost jobs you've rejected will be skipped automatically"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Backfill failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Backfill failed: {str(e)}")

@app.post("/api/admin/run-deduplication-migration")
async def run_deduplication_migration():
    """Run the job deduplication migration"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required for migration")

    try:
        print("🚀 Starting job deduplication migration...")

        # Connect to database
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Read and execute migration SQL
        migration_file = 'database_migrations/002_add_job_deduplication.sql'

        if not os.path.exists(migration_file):
            raise HTTPException(status_code=404, detail=f"Migration file not found: {migration_file}")

        print(f"📄 Reading migration file: {migration_file}")
        with open(migration_file, 'r') as f:
            migration_sql = f.read()

        print("🔄 Executing migration SQL...")
        await conn.execute(migration_sql)
        print("✅ Migration SQL executed successfully")

        # Backfill job signatures for existing applied jobs
        print("\n🔄 Backfilling job signatures for existing applied jobs...")

        applied_jobs = await conn.fetch("""
            SELECT id, title, company, country
            FROM jobs
            WHERE applied = TRUE
            ORDER BY scraped_at DESC
        """)

        print(f"📊 Found {len(applied_jobs)} applied jobs")

        backfilled = 0
        errors = 0

        for job in applied_jobs:
            try:
                # Add job signature
                success = await db.add_job_signature(
                    company=job['company'],
                    title=job['title'],
                    country=job['country'],
                    job_id=job['id']
                )

                if success:
                    backfilled += 1

            except Exception as e:
                print(f"⚠️  Error backfilling signature for job {job['id']}: {e}")
                errors += 1
                continue

        await conn.close()

        print(f"✅ Backfilled {backfilled} job signatures")
        print("✅ Migration completed successfully!")

        return {
            "success": True,
            "message": "Deduplication migration completed successfully",
            "applied_jobs_found": len(applied_jobs),
            "signatures_created": backfilled,
            "errors": errors,
            "info": {
                "description": "Job deduplication is now active",
                "features": [
                    "Automatically detects and skips reposted jobs",
                    "Tracks jobs for 30 days after application",
                    "Normalizes job titles to match variations",
                    "Works automatically during scraping"
                ]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@app.get("/api/admin/analytics")
async def get_analytics():
    """Get analytics for all users - admin only"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        from user_database import UserDatabase
        user_db = UserDatabase()

        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Get all users with their analytics
        users_analytics = await conn.fetch("""
            SELECT
                u.id,
                u.username,
                u.email,
                u.full_name,
                u.created_at,
                u.last_login,
                u.is_admin,
                up.job_types,
                up.preferred_countries,
                up.experience_levels,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE) as jobs_applied,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE) as jobs_rejected,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.saved = TRUE) as jobs_saved,
                MAX(uji.applied_at) FILTER (WHERE uji.applied = TRUE) as last_application_date,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE AND uji.applied_at >= NOW() - INTERVAL '7 days') as applications_last_7_days,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE AND uji.applied_at >= NOW() - INTERVAL '30 days') as applications_last_30_days
            FROM users u
            LEFT JOIN user_preferences up ON u.id = up.user_id
            LEFT JOIN user_job_interactions uji ON u.id = uji.user_id
            GROUP BY u.id, u.username, u.email, u.full_name, u.created_at, u.last_login, u.is_admin, up.job_types, up.preferred_countries, up.experience_levels
            ORDER BY u.created_at DESC
        """)

        # Get job type statistics
        job_type_stats = await conn.fetch("""
            SELECT
                job_type,
                COUNT(*) as total_jobs,
                COUNT(*) FILTER (WHERE applied = TRUE) as applied_jobs,
                COUNT(*) FILTER (WHERE rejected = TRUE) as rejected_jobs,
                COUNT(*) FILTER (WHERE applied = FALSE AND rejected = FALSE) as available_jobs
            FROM jobs
            WHERE job_type IS NOT NULL
            GROUP BY job_type
            ORDER BY total_jobs DESC
        """)

        # Get country statistics
        country_stats = await conn.fetch("""
            SELECT
                country,
                COUNT(*) as total_jobs,
                COUNT(*) FILTER (WHERE applied = TRUE) as applied_jobs,
                COUNT(*) FILTER (WHERE rejected = TRUE) as rejected_jobs
            FROM jobs
            WHERE country IS NOT NULL
            GROUP BY country
            ORDER BY total_jobs DESC
        """)

        # Get application timeline (last 30 days)
        timeline_stats = await conn.fetch("""
            SELECT
                DATE(applied_at) as date,
                COUNT(DISTINCT job_id) as applications
            FROM user_job_interactions
            WHERE applied = TRUE
            AND applied_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(applied_at)
            ORDER BY date ASC
        """)

        await conn.close()

        # Format results
        users = []
        for user in users_analytics:
            users.append({
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "full_name": user['full_name'],
                "created_at": user['created_at'].isoformat() if user['created_at'] else None,
                "last_login": user['last_login'].isoformat() if user['last_login'] else None,
                "is_admin": user['is_admin'],
                "job_types": user['job_types'] or [],
                "preferred_countries": user['preferred_countries'] or [],
                "experience_levels": user['experience_levels'] or [],
                "stats": {
                    "jobs_applied": user['jobs_applied'],
                    "jobs_rejected": user['jobs_rejected'],
                    "jobs_saved": user['jobs_saved'],
                    "last_application_date": user['last_application_date'].isoformat() if user['last_application_date'] else None,
                    "applications_last_7_days": user['applications_last_7_days'],
                    "applications_last_30_days": user['applications_last_30_days']
                }
            })

        job_types = [
            {
                "job_type": row['job_type'],
                "total_jobs": row['total_jobs'],
                "applied_jobs": row['applied_jobs'],
                "rejected_jobs": row['rejected_jobs'],
                "available_jobs": row['available_jobs']
            }
            for row in job_type_stats
        ]

        countries = [
            {
                "country": row['country'],
                "total_jobs": row['total_jobs'],
                "applied_jobs": row['applied_jobs'],
                "rejected_jobs": row['rejected_jobs']
            }
            for row in country_stats
        ]

        timeline = [
            {
                "date": row['date'].isoformat(),
                "applications": row['applications']
            }
            for row in timeline_stats
        ]

        return {
            "users": users,
            "job_types": job_types,
            "countries": countries,
            "application_timeline": timeline,
            "summary": {
                "total_users": len(users),
                "total_applications": sum(u['stats']['jobs_applied'] for u in users),
                "total_rejections": sum(u['stats']['jobs_rejected'] for u in users),
                "applications_last_7_days": sum(u['stats']['applications_last_7_days'] for u in users),
                "applications_last_30_days": sum(u['stats']['applications_last_30_days'] for u in users)
            }
        }

    except Exception as e:
        print(f"❌ Error getting analytics: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@app.get("/api/analytics/personal")
async def get_personal_analytics(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get personal analytics for the authenticated user - time patterns, country stats, application velocity"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        user_id = current_user['user_id']

        # 1. Time-based patterns - Hour of day when user applies most
        hourly_pattern = await conn.fetch("""
            SELECT
                EXTRACT(HOUR FROM applied_at) as hour,
                COUNT(*) as applications
            FROM user_job_interactions
            WHERE user_id = $1 AND applied = TRUE AND applied_at IS NOT NULL
            GROUP BY EXTRACT(HOUR FROM applied_at)
            ORDER BY hour
        """, user_id)

        # 2. Day of week pattern
        daily_pattern = await conn.fetch("""
            SELECT
                EXTRACT(DOW FROM applied_at) as day_of_week,
                COUNT(*) as applications
            FROM user_job_interactions
            WHERE user_id = $1 AND applied = TRUE AND applied_at IS NOT NULL
            GROUP BY EXTRACT(DOW FROM applied_at)
            ORDER BY day_of_week
        """, user_id)

        # 3. Country-wise application distribution
        country_stats = await conn.fetch("""
            SELECT
                j.country,
                COUNT(*) FILTER (WHERE uji.applied = TRUE) as applied_count,
                COUNT(*) FILTER (WHERE uji.rejected = TRUE) as rejected_count,
                COUNT(*) FILTER (WHERE uji.saved = TRUE) as saved_count
            FROM user_job_interactions uji
            JOIN jobs j ON uji.job_id = j.id
            WHERE uji.user_id = $1 AND j.country IS NOT NULL
            GROUP BY j.country
            ORDER BY applied_count DESC
        """, user_id)

        # 4. Application velocity - Applications per day for last 30 days
        velocity_stats = await conn.fetch("""
            SELECT
                DATE(applied_at) as date,
                COUNT(*) as applications
            FROM user_job_interactions
            WHERE user_id = $1
            AND applied = TRUE
            AND applied_at >= NOW() - INTERVAL '30 days'
            GROUP BY DATE(applied_at)
            ORDER BY date ASC
        """, user_id)

        # 5. Overall stats and streaks
        overall_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) FILTER (WHERE applied = TRUE) as total_applied,
                COUNT(*) FILTER (WHERE rejected = TRUE) as total_rejected,
                COUNT(*) FILTER (WHERE saved = TRUE) as total_saved,
                COUNT(*) FILTER (WHERE applied = TRUE AND applied_at >= NOW() - INTERVAL '7 days') as applied_last_7_days,
                COUNT(*) FILTER (WHERE applied = TRUE AND applied_at >= NOW() - INTERVAL '30 days') as applied_last_30_days,
                MIN(applied_at) FILTER (WHERE applied = TRUE) as first_application,
                MAX(applied_at) FILTER (WHERE applied = TRUE) as last_application
            FROM user_job_interactions
            WHERE user_id = $1
        """, user_id)

        # 6. Job type preferences
        job_type_stats = await conn.fetch("""
            SELECT
                j.job_type,
                COUNT(*) FILTER (WHERE uji.applied = TRUE) as applied_count,
                COUNT(*) FILTER (WHERE uji.rejected = TRUE) as rejected_count
            FROM user_job_interactions uji
            JOIN jobs j ON uji.job_id = j.id
            WHERE uji.user_id = $1 AND j.job_type IS NOT NULL
            GROUP BY j.job_type
            ORDER BY applied_count DESC
        """, user_id)

        # 7. Application success rate by experience level
        experience_stats = await conn.fetch("""
            SELECT
                j.experience_level,
                COUNT(*) FILTER (WHERE uji.applied = TRUE) as applied_count,
                COUNT(*) FILTER (WHERE uji.rejected = TRUE) as rejected_count
            FROM user_job_interactions uji
            JOIN jobs j ON uji.job_id = j.id
            WHERE uji.user_id = $1 AND j.experience_level IS NOT NULL
            GROUP BY j.experience_level
            ORDER BY applied_count DESC
        """, user_id)

        await conn.close()

        # Calculate success rate
        total_applied = overall_stats['total_applied'] or 0
        total_rejected = overall_stats['total_rejected'] or 0
        total_interactions = total_applied + total_rejected
        success_rate = (total_applied / total_interactions * 100) if total_interactions > 0 else 0

        # Calculate average applications per day (only counting days with activity)
        days_active = len(velocity_stats)
        avg_per_active_day = (total_applied / days_active) if days_active > 0 else 0

        # Format day of week names
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        return {
            "hourly_pattern": [
                {"hour": int(row['hour']), "applications": row['applications']}
                for row in hourly_pattern
            ],
            "daily_pattern": [
                {"day": day_names[int(row['day_of_week'])], "day_number": int(row['day_of_week']), "applications": row['applications']}
                for row in daily_pattern
            ],
            "countries": [
                {
                    "country": row['country'],
                    "applied": row['applied_count'],
                    "rejected": row['rejected_count'],
                    "saved": row['saved_count']
                }
                for row in country_stats
            ],
            "velocity": [
                {"date": row['date'].isoformat(), "applications": row['applications']}
                for row in velocity_stats
            ],
            "job_types": [
                {
                    "job_type": row['job_type'],
                    "applied": row['applied_count'],
                    "rejected": row['rejected_count']
                }
                for row in job_type_stats
            ],
            "experience_levels": [
                {
                    "level": row['experience_level'],
                    "applied": row['applied_count'],
                    "rejected": row['rejected_count']
                }
                for row in experience_stats
            ],
            "summary": {
                "total_applied": total_applied,
                "total_rejected": total_rejected,
                "total_saved": overall_stats['total_saved'] or 0,
                "applied_last_7_days": overall_stats['applied_last_7_days'] or 0,
                "applied_last_30_days": overall_stats['applied_last_30_days'] or 0,
                "first_application": overall_stats['first_application'].isoformat() if overall_stats['first_application'] else None,
                "last_application": overall_stats['last_application'].isoformat() if overall_stats['last_application'] else None,
                "success_rate": round(success_rate, 1),
                "avg_per_active_day": round(avg_per_active_day, 1),
                "days_active": days_active
            }
        }

    except Exception as e:
        print(f"❌ Error getting personal analytics: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get personal analytics: {str(e)}")

# Catch-all route for React Router (SPA routing)
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Serve React app for all other routes (SPA routing)"""
    if os.path.exists("job-manager-ui/dist/index.html"):
        return FileResponse("job-manager-ui/dist/index.html")
    else:
        return HTMLResponse(content=HTML_INTERFACE)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)