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
    AUTH_AVAILABLE = True
    print("✅ Authentication routes imported successfully")
except ImportError as e:
    print(f"⚠️  Authentication routes not available: {e}")
    AUTH_AVAILABLE = False

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

    # If authenticated, filter by user preferences
    try:
        if AUTH_AVAILABLE:
            from user_database import UserDatabase
            user_db = UserDatabase()
            preferences = await user_db.get_user_preferences(current_user['user_id'])

            if preferences:
                filtered_jobs = {}

                for job_id, job_data in all_jobs.items():
                    # Skip metadata
                    if job_id.startswith('_'):
                        filtered_jobs[job_id] = job_data
                        continue

                    # Get job details for filtering
                    title = job_data.get('title', '')
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
async def update_job_api(request: JobUpdateRequest):
    """Update job applied and/or rejected status - DATABASE ONLY"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        print(f"🔄 DEBUG: Updating job {request.job_id} - applied: {request.applied}, rejected: {request.rejected}")

        success = await db.update_job_status(
            job_id=request.job_id,
            applied=request.applied,
            rejected=request.rejected
        )

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
async def update_job_legacy(request: JobUpdateRequest):
    """Legacy endpoint - redirects to proper API"""
    return await update_job_api(request)

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
            "updated_jobs": result.get("updated_jobs", 0)
        }
    except Exception as e:
        print(f"❌ Database sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database sync failed: {str(e)}")

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