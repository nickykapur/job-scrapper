#!/usr/bin/env python3
"""
Ultra-minimal LinkedIn Job Manager for Railway
Just serves existing job database - no React build needed
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime
import asyncio

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# ── Logging setup ────────────────────────────────────────────────────────────
# Use Python logging instead of print() so Sentry and Railway can filter by level
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("job_scraper")

# ── Sentry: errors + tracing + logs ─────────────────────────────────────────
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

_sentry_dsn = os.environ.get("SENTRY_DSN")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        environment=os.environ.get("RAILWAY_ENVIRONMENT", "development"),
        integrations=[
            FastApiIntegration(),
            AsyncioIntegration(),
            # Forward Python logger.info+ to Sentry logs; errors create Issues
            LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
        ],
        traces_sample_rate=0.2,   # 20% of requests — fine for this traffic level
        profiles_sample_rate=0.0, # Profiling off — not needed at this scale
        # Keep False: we don't want user IPs/passwords sent to a third party
        send_default_pii=False,
        ignore_errors=[KeyboardInterrupt],
    )
    logger.info("Sentry error tracking enabled")

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

# Compress responses — reduces egress on Railway (minimum_size=500 bytes skips tiny responses)
app.add_middleware(GZipMiddleware, minimum_size=500)

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

class BulkRejectRequest(BaseModel):
    company: Optional[str] = None
    country: Optional[str] = None

class ClearInteractionsRequest(BaseModel):
    country: Optional[str] = None
    company: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    if db and DATABASE_AVAILABLE:
        try:
            await db.init_database()
            print("✅ Database initialized successfully")
        except Exception as e:
            print(f"⚠️  Database initialization failed: {e}")

        # Run incremental migrations that may not be in the base schema yet
        try:
            conn = await db.get_connection()
            if conn:
                try:
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS user_activity_events (
                            id BIGSERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            event_type VARCHAR(50) NOT NULL,
                            event_data JSONB DEFAULT '{}',
                            occurred_at TIMESTAMPTZ DEFAULT NOW()
                        );
                        CREATE INDEX IF NOT EXISTS idx_activity_user_time
                            ON user_activity_events(user_id, occurred_at DESC);
                        CREATE INDEX IF NOT EXISTS idx_activity_type_time
                            ON user_activity_events(event_type, occurred_at DESC);
                    """)
                    print("✅ Activity events table ready")
                finally:
                    await db._release(conn)
        except Exception as e:
            print(f"⚠️  Activity events migration failed: {e}")

        # Create job upload queue table
        try:
            conn = await db.get_connection()
            if conn:
                try:
                    await conn.execute("""
                        CREATE TABLE IF NOT EXISTS job_upload_queue (
                            id BIGSERIAL PRIMARY KEY,
                            jobs_data JSONB NOT NULL,
                            job_count INT DEFAULT 0,
                            status VARCHAR(20) DEFAULT 'pending',
                            created_at TIMESTAMPTZ DEFAULT NOW(),
                            started_at TIMESTAMPTZ,
                            finished_at TIMESTAMPTZ,
                            result JSONB,
                            error_text TEXT
                        );
                        ALTER TABLE job_upload_queue ADD COLUMN IF NOT EXISTS job_count INT DEFAULT 0;
                        CREATE INDEX IF NOT EXISTS idx_job_queue_status
                            ON job_upload_queue(status, created_at);
                    """)
                    print("✅ Job upload queue table ready")
                finally:
                    await db._release(conn)
        except Exception as e:
            print(f"⚠️  Job upload queue migration failed: {e}")

        # Start background queue worker
        asyncio.create_task(_queue_worker())
        print("✅ Job upload queue worker started")

async def _process_queue_once() -> bool:
    """Claim and process one pending queue item. Returns True if something was processed."""
    import traceback as _tb

    # Step 1: claim one item using CTE for safe locking
    conn = await db.get_connection()
    if not conn:
        return False
    try:
        row = await conn.fetchrow("""
            WITH next_item AS (
                SELECT id FROM job_upload_queue
                WHERE status = 'pending'
                ORDER BY created_at
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            UPDATE job_upload_queue q
            SET status = 'processing', started_at = NOW()
            FROM next_item
            WHERE q.id = next_item.id
            RETURNING q.id, q.jobs_data::text AS jobs_data_text
        """)
    finally:
        await db._release(conn)

    if not row:
        return False  # Queue empty

    qid = row['id']
    # Parse JSONB safely regardless of asyncpg codec config
    try:
        jobs_data = json.loads(row['jobs_data_text'])
    except Exception as e:
        logger.error("Queue item %s: failed to parse jobs_data: %s", qid, e)
        return True  # Skip this item

    # Step 2: process (uses its own connection from the pool)
    async def _mark(status: str, result_dict=None, error: str = None):
        c = await db.get_connection()
        if not c:
            return
        try:
            if status == 'done':
                await c.execute(
                    "UPDATE job_upload_queue SET status='done', finished_at=NOW(), result=$1::jsonb WHERE id=$2",
                    json.dumps(result_dict or {}), qid
                )
            else:
                await c.execute(
                    "UPDATE job_upload_queue SET status='failed', finished_at=NOW(), error_text=$1 WHERE id=$2",
                    error or 'unknown error', qid
                )
        finally:
            await db._release(c)

    try:
        result = await db.sync_jobs_from_scraper(jobs_data)
        if 'error' in result:
            # sync internally failed — mark as failed with the error message
            logger.error("Queue item %s sync error: %s", qid, result['error'])
            await _mark('failed', error=result['error'])
        else:
            await _mark('done', result_dict=result)
            logger.info("Queue item %s done: %s new, %s updated", qid,
                        result.get('new_jobs', 0), result.get('updated_jobs', 0))
    except Exception as e:
        logger.error("Queue item %s failed: %s\n%s", qid, e, _tb.format_exc())
        await _mark('failed', error=str(e))
    return True

async def _queue_worker():
    """Background task: drain job_upload_queue one batch at a time."""
    import traceback as _tb
    logger.info("Queue worker started")
    while True:
        try:
            processed = await _process_queue_once()
            if not processed:
                await asyncio.sleep(3)  # Nothing pending, poll every 3s
        except Exception as e:
            logger.error("Queue worker loop error: %s\n%s", e, _tb.format_exc())
            await asyncio.sleep(5)

async def load_jobs():
    """Load jobs from database ONLY - no JSON fallback"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        jobs_data = await db.get_all_jobs()
        return jobs_data
    except Exception as e:
        print(f"❌ Database load failed: {e}")
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
    """Health check — lightweight ping, does not load all jobs"""
    db_ok = False
    if db and db.use_postgres and db._pool:
        try:
            conn = await db.get_connection()
            await conn.fetchval("SELECT 1")
            await db._release(conn)
            db_ok = True
        except Exception:
            pass
    return {
        "status": "healthy",
        "database": "postgresql" if db_ok else ("json_fallback" if db else "unavailable"),
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

        # Tell Sentry who this user is — shows up on every error from this request
        if payload and _sentry_dsn:
            sentry_sdk.set_user({
                "id": payload.get("user_id"),
                "username": payload.get("username"),
            })

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
            user_signatures = {}  # Company+Title pairs user has already applied/rejected to
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

                    # Also get job signatures (company+title) user has applied to OR rejected
                    # This catches cases where job was deleted and re-scraped with new ID
                    # Store both applied and rejected status to correctly mark reposts
                    signatures = await conn.fetch("""
                        SELECT DISTINCT
                            js.company,
                            js.normalized_title,
                            MAX(CASE WHEN uji.applied THEN 1 ELSE 0 END)::boolean as was_applied,
                            MAX(CASE WHEN uji.rejected THEN 1 ELSE 0 END)::boolean as was_rejected
                        FROM job_signatures js
                        JOIN user_job_interactions uji ON uji.job_id = js.original_job_id
                        WHERE uji.user_id = $1
                        AND (uji.applied = TRUE OR uji.rejected = TRUE)
                        GROUP BY js.company, js.normalized_title
                    """, current_user['user_id'])

                    for sig in signatures:
                        signature_key = f"{sig['company'].lower()}|{sig['normalized_title'].lower()}"
                        user_signatures[signature_key] = {
                            'applied': sig['was_applied'],
                            'rejected': sig['was_rejected']
                        }

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

                    # Check if this is a repost of a job they already applied to or rejected
                    company = job_data.get('company', '').strip()
                    title = job_data.get('title', '').strip()
                    is_repost = False
                    if company and title:
                        # Normalize title (remove senior, junior, etc.)
                        normalized_title = db.normalize_job_title(title) if db else title.lower()
                        signature_key = f"{company.lower()}|{normalized_title.lower()}"

                        if signature_key in user_signatures and job_id not in user_interactions:
                            # This is a repost - mark with original applied/rejected status
                            is_repost = True
                            job_data = {**job_data}
                            sig_status = user_signatures[signature_key]
                            job_data['applied'] = sig_status['applied']
                            job_data['rejected'] = sig_status['rejected']
                            status_str = "applied" if sig_status['applied'] else "rejected"
                            print(f"[FILTER] Auto-marking repost {job_id[:12]}... as {status_str} - '{title}' at {company}")

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
                                    # Exclude HR/non-software jobs (English and Spanish)
                                    if any(exclude in title_lower for exclude in ['hr ', ' hr', 'human resources', 'recruitment', 'talent acquisition', 'rrhh', 'recursos humanos', 'reclutamiento', 'selección de personal', 'talento humano']):
                                        break
                                    if any(kw in title_desc for kw in sw_keywords):
                                        type_match = True
                                        break
                                elif pref_type == 'hr':
                                    hr_keywords = [' hr ', 'human resources', 'recruiter', 'recruitment', 'recruiting', 'talent acquisition', 'talent', 'people operations', 'people', 'hr officer', 'hr coordinator', 'hr generalist', 'hr manager', 'hr business partner', 'hr specialist', 'people partner', 'talent sourcer', 'hr assistant', 'rrhh', 'recursos humanos', 'reclutador', 'reclutamiento', 'selección', 'talento humano', 'analista de recursos humanos', 'coordinador de rrhh']
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
                                elif pref_type == 'marketing' or pref_type == 'digital_marketing' or pref_type == 'content' or pref_type == 'communications' or pref_type == 'crm' or pref_type == 'analytics':
                                    marketing_keywords = [
                                        'digital marketing', 'marketing manager', 'marketing executive', 'marketing coordinator', 'marketing specialist',
                                        'social media manager', 'social media executive', 'social media marketing', 'community manager',
                                        'seo specialist', 'seo executive', 'seo manager', 'search engine optimization',
                                        'ppc', 'paid media', 'paid social', 'google ads', 'meta ads', 'performance marketing',
                                        'content marketing', 'content manager', 'content strategist', 'copywriter',
                                        'crm manager', 'crm executive', 'email marketing', 'marketing automation', 'hubspot', 'salesforce marketing',
                                        'brand manager', 'brand marketing', 'growth marketing', 'campaign manager',
                                        'communications manager', 'communications executive', 'marketing communications', 'pr executive', 'public relations'
                                    ]
                                    if any(kw in title_desc for kw in marketing_keywords):
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
        print(f"❌ Error filtering jobs by preferences: {e}")
        import traceback
        traceback.print_exc()
        # On error, still return unfiltered jobs with user interactions merged
        # This ensures users at least see their applied/rejected status
        if current_user and user_interactions:
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
    """
    Enforce per-country, per-job-type limits with 72h protection.
    - Always keeps ALL jobs scraped within the last 72 hours (crash safety buffer)
    - Applies per-job-type limits to older jobs only
    - Software jobs are never auto-deleted
    """
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Pure-SQL enforce: uses window functions so no Python iteration over rows.
        # Jobs scraped within the last 72h are ALWAYS protected (crash safety buffer).
        # For older jobs, keep the N most-recent per (country, job_type).
        #
        # Limits per job type (applied only to jobs older than 72h):
        #   software      → 1000  (prevents unbounded accumulation)
        #   marketing     → 100
        #   everything else → 60  (covers account_management, communications, hr, etc.)

        deleted_result = await conn.execute("""
            DELETE FROM jobs
            WHERE id IN (
                SELECT id FROM (
                    SELECT id,
                           ROW_NUMBER() OVER (
                               PARTITION BY country, COALESCE(job_type, 'other')
                               ORDER BY scraped_at DESC
                           ) AS rn,
                           job_type
                    FROM jobs
                    WHERE scraped_at < NOW() - INTERVAL '72 hours'
                ) ranked
                WHERE (job_type = 'software'  AND rn > 1000)
                   OR (job_type = 'marketing' AND rn > 100)
                   OR (job_type NOT IN ('software', 'marketing') AND rn > 60)
                   OR (job_type IS NULL AND rn > 60)
            )
        """)

        # asyncpg returns "DELETE N" — parse the count
        deleted_count = int(deleted_result.split()[-1]) if deleted_result else 0

        total_jobs = await conn.fetchval("SELECT COUNT(*) FROM jobs")
        protected_count = await conn.fetchval(
            "SELECT COUNT(*) FROM jobs WHERE scraped_at >= NOW() - INTERVAL '72 hours'"
        )

        await conn.close()

        print(f"✅ enforce-country-limit: deleted {deleted_count}, remaining {total_jobs}, protected {protected_count}")

        return {
            "success": True,
            "message": "Enforced per-job-type limits with 72h protection (SQL window functions)",
            "jobs_deleted": deleted_count,
            "total_jobs_remaining": total_jobs,
            "protected_24h_jobs": protected_count,
            "countries_processed": -1,  # not tracked in SQL approach
            "job_type_limits": JOB_TYPE_LIMITS
        }
    except Exception as e:
        print(f"❌ Enforce limit failed: {e}")
        import traceback
        traceback.print_exc()
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

    # Initialize encouragement message
    encouragement_message = None

    try:
        logger.info("Job status update: job=%s applied=%s rejected=%s user=%s",
                    request.job_id, request.applied, request.rejected,
                    current_user.get('username') if current_user else 'anonymous')

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
                            logger.info("User %s applied to job %s", user_id, request.job_id)

                            # Create job signature to prevent this job from reappearing
                            job = await conn.fetchrow("""
                                SELECT company, title, country FROM jobs WHERE id = $1
                            """, request.job_id)

                            if job and job['company'] and job['title']:
                                signature_created = await db.add_job_signature(
                                    company=job['company'],
                                    title=job['title'],
                                    country=job['country'] or '',
                                    job_id=request.job_id
                                )
                                if not signature_created:
                                    logger.warning("Failed to create job signature for job %s", request.job_id)

                            # Update streak tracking
                            from datetime import date
                            today = date.today()

                            # Get current rewards data
                            rewards = await conn.fetchrow("""
                                SELECT current_streak, longest_streak, last_activity_date
                                FROM user_rewards
                                WHERE user_id = $1
                            """, user_id)

                            if rewards:
                                current_streak = rewards['current_streak'] or 0
                                longest_streak = rewards['longest_streak'] or 0
                                last_activity = rewards['last_activity_date']

                                # Calculate new streak
                                if last_activity:
                                    days_diff = (today - last_activity).days
                                    if days_diff == 0:
                                        # Same day, no change to streak
                                        new_streak = current_streak
                                    elif days_diff == 1:
                                        # Consecutive day, increment streak
                                        new_streak = current_streak + 1
                                    else:
                                        # Streak broken, restart
                                        new_streak = 1
                                else:
                                    # First activity
                                    new_streak = 1

                                # Update longest streak if needed
                                new_longest = max(longest_streak, new_streak)

                                await conn.execute("""
                                    UPDATE user_rewards
                                    SET current_streak = $2,
                                        longest_streak = $3,
                                        last_activity_date = $4,
                                        updated_at = CURRENT_TIMESTAMP
                                    WHERE user_id = $1
                                """, user_id, new_streak, new_longest, today)
                                logger.info("Streak updated for user %s: %d days", user_id, new_streak)

                            # Generate encouragement messages for milestones
                            # Get job details (country/location)
                            job_details = await conn.fetchrow("""
                                SELECT country, location FROM jobs WHERE id = $1
                            """, request.job_id)

                            if job_details:
                                job_country = job_details['country']
                                job_location = job_details['location']

                                # Get application stats
                                stats = await conn.fetchrow("""
                                    SELECT
                                        COUNT(*) as total_applications,
                                        COUNT(*) FILTER (WHERE DATE(applied_at) = CURRENT_DATE) as today_applications
                                    FROM user_job_interactions uji
                                    JOIN jobs j ON uji.job_id = j.id
                                    WHERE uji.user_id = $1 AND uji.applied = TRUE
                                """, user_id)

                                total_apps = stats['total_applications']
                                today_apps = stats['today_applications']

                                # Check for country-specific milestones
                                if job_country:
                                    country_stats = await conn.fetchrow("""
                                        SELECT COUNT(*) as country_applications
                                        FROM user_job_interactions uji
                                        JOIN jobs j ON uji.job_id = j.id
                                        WHERE uji.user_id = $1 AND uji.applied = TRUE AND j.country = $2
                                    """, user_id, job_country)

                                    country_apps = country_stats['country_applications']

                                    # Country milestones (5, 10, 25, 50)
                                    if country_apps == 5:
                                        encouragement_message = f"🌍 5 applications in {job_country}! You're exploring the market!"
                                    elif country_apps == 10:
                                        encouragement_message = f"🚀 10 applications in {job_country}! You're gaining momentum!"
                                    elif country_apps == 25:
                                        encouragement_message = f"💪 25 applications in {job_country}! You're crushing it!"
                                    elif country_apps == 50:
                                        encouragement_message = f"🏆 50 applications in {job_country}! You're a local legend!"
                                    elif country_apps == 100:
                                        encouragement_message = f"💎 100 applications in {job_country}! Absolutely incredible!"

                                # Overall milestones (5, 10, 25, 50, 100, 200, 500)
                                if not encouragement_message:
                                    if total_apps == 5:
                                        encouragement_message = "🎯 5 applications! You're off to a great start!"
                                    elif total_apps == 10:
                                        encouragement_message = "🌟 10 applications! Double digits, keep it up!"
                                    elif total_apps == 25:
                                        encouragement_message = "🔥 25 applications! You're on fire!"
                                    elif total_apps == 50:
                                        encouragement_message = "💪 50 applications! Half century milestone!"
                                    elif total_apps == 100:
                                        encouragement_message = "🏆 100 applications! Triple digits - amazing dedication!"
                                    elif total_apps == 200:
                                        encouragement_message = "🚀 200 applications! You're unstoppable!"
                                    elif total_apps == 500:
                                        encouragement_message = "💎 500 applications! You're a job hunting legend!"

                                # Today milestones (5, 10, 20)
                                if not encouragement_message:
                                    if today_apps == 5:
                                        encouragement_message = "⚡ 5 applications today! Great daily momentum!"
                                    elif today_apps == 10:
                                        encouragement_message = "🔥 10 applications today! You're crushing today's goal!"
                                    elif today_apps == 20:
                                        encouragement_message = "💪 20 applications today! Incredible productivity!"
                                    elif today_apps == 30:
                                        encouragement_message = "🚀 30 applications today! You're a machine!"

                                # Streak milestones
                                if not encouragement_message and new_streak > current_streak:
                                    if new_streak == 3:
                                        encouragement_message = "🔥 3-day streak! Building consistency!"
                                    elif new_streak == 7:
                                        encouragement_message = "⭐ 7-day streak! A full week of dedication!"
                                    elif new_streak == 14:
                                        encouragement_message = "💪 14-day streak! Two weeks strong!"
                                    elif new_streak == 30:
                                        encouragement_message = "🏆 30-day streak! A full month! You're incredible!"
                                    elif new_streak == 60:
                                        encouragement_message = "💎 60-day streak! Two months of consistency!"
                                    elif new_streak == 100:
                                        encouragement_message = "👑 100-day streak! You're a legend!"

                            # Store encouragement message to return later
                            if encouragement_message:
                                # We'll return this with the response
                                pass

                        if request.rejected:
                            await conn.execute("""
                                INSERT INTO user_job_interactions (user_id, job_id, rejected, rejected_at, created_at, updated_at)
                                VALUES ($1, $2, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                                ON CONFLICT (user_id, job_id) DO UPDATE SET
                                    rejected = TRUE,
                                    rejected_at = CURRENT_TIMESTAMP,
                                    updated_at = CURRENT_TIMESTAMP
                            """, user_id, request.job_id)
                            logger.info("User %s rejected job %s", user_id, request.job_id)

                            # Create job signature to prevent this job from reappearing
                            job = await conn.fetchrow("""
                                SELECT company, title, country FROM jobs WHERE id = $1
                            """, request.job_id)

                            if job and job['company'] and job['title']:
                                signature_created = await db.add_job_signature(
                                    company=job['company'],
                                    title=job['title'],
                                    country=job['country'] or '',
                                    job_id=request.job_id
                                )
                                if not signature_created:
                                    logger.warning("Failed to create job signature for rejected job %s", request.job_id)
                    finally:
                        await db._release(conn)

        if success:
            response = {"success": True, "message": f"Job {request.job_id} updated"}
            if encouragement_message:
                response["encouragement"] = encouragement_message
            return response
        else:
            logger.warning("Job %s not found in database during update", request.job_id)
            raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        logger.error("Database update failed for job %s: %s", request.job_id, e)
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")

@app.post("/update_job")
async def update_job_legacy(request: JobUpdateRequest, current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    """Legacy endpoint - redirects to proper API"""
    return await update_job_api(request, current_user)

@app.post("/sync_jobs")
async def sync_jobs(request: SyncJobsRequest):
    """Sync jobs from local scraper — enqueues for background processing and returns immediately."""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    job_count = sum(1 for k in request.jobs_data if not k.startswith('_'))

    conn = await db.get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    try:
        row = await conn.fetchrow(
            "INSERT INTO job_upload_queue (jobs_data, job_count) VALUES ($1::jsonb, $2) RETURNING id",
            json.dumps(request.jobs_data), job_count
        )
    finally:
        await db._release(conn)

    logger.info("Enqueued %d jobs for background processing (queue_id=%s)", job_count, row['id'])

    # Return success immediately; actual counts are 0 since processing is async.
    # Jobs will appear in the dashboard within seconds as the background worker drains the queue.
    return {
        "success": True,
        "message": f"Queued {job_count} jobs for processing (queue_id={row['id']})",
        "queue_id": row['id'],
        "new_jobs": 0,
        "new_software": 0, "new_hr": 0, "new_cybersecurity": 0,
        "new_sales": 0, "new_finance": 0, "new_marketing": 0,
        "new_biotech": 0, "new_engineering": 0, "new_events": 0,
        "updated_jobs": 0, "skipped_reposts": 0,
    }

@app.post("/api/jobs/bulk-reject")
async def bulk_reject_jobs(
    request: BulkRejectRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    """
    Bulk reject jobs by company or country for current user
    This helps users quickly clear out jobs they're not interested in
    """
    if not current_user or not AUTH_AVAILABLE:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not request.company and not request.country:
        raise HTTPException(status_code=400, detail="Must specify company or country")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        user_id = current_user['user_id']

        # Build query based on filters
        if request.company and request.country:
            # Both company and country
            jobs = await conn.fetch("""
                SELECT id FROM jobs
                WHERE company = $1 AND country = $2
            """, request.company, request.country)
        elif request.company:
            # Company only
            jobs = await conn.fetch("""
                SELECT id FROM jobs
                WHERE company = $1
            """, request.company)
        else:
            # Country only
            jobs = await conn.fetch("""
                SELECT id FROM jobs
                WHERE country = $1
            """, request.country)

        rejected_count = 0
        for job in jobs:
            await conn.execute("""
                INSERT INTO user_job_interactions (user_id, job_id, rejected, rejected_at, created_at, updated_at)
                VALUES ($1, $2, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id, job_id) DO UPDATE SET
                    rejected = TRUE,
                    rejected_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
            """, user_id, job['id'])
            rejected_count += 1

        await conn.close()

        filter_desc = []
        if request.company:
            filter_desc.append(f"company '{request.company}'")
        if request.country:
            filter_desc.append(f"country '{request.country}'")

        return {
            "success": True,
            "message": f"Bulk rejected {rejected_count} jobs from {' and '.join(filter_desc)}",
            "jobs_rejected": rejected_count
        }

    except Exception as e:
        print(f"❌ Bulk reject failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Bulk reject failed: {str(e)}")

@app.post("/api/jobs/clear-interactions")
async def clear_user_job_interactions(
    request: ClearInteractionsRequest,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    """
    Clear user's interactions (applied/rejected) for specific country or company
    This allows users to "reset" and see jobs fresh when new scrapes come in
    """
    if not current_user or not AUTH_AVAILABLE:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        user_id = current_user['user_id']

        # Build query to find job IDs matching the filters
        if request.company and request.country:
            # Both company and country
            job_ids = await conn.fetch("""
                SELECT id FROM jobs
                WHERE company = $1 AND country = $2
            """, request.company, request.country)
        elif request.company:
            # Company only
            job_ids = await conn.fetch("""
                SELECT id FROM jobs
                WHERE company = $1
            """, request.company)
        elif request.country:
            # Country only
            job_ids = await conn.fetch("""
                SELECT id FROM jobs
                WHERE country = $1
            """, request.country)
        else:
            raise HTTPException(status_code=400, detail="Must specify company or country")

        # Delete interactions for these jobs for this user
        cleared_count = 0
        for job in job_ids:
            result = await conn.execute("""
                DELETE FROM user_job_interactions
                WHERE user_id = $1 AND job_id = $2
            """, user_id, job['id'])
            cleared_count += 1

        await conn.close()

        filter_desc = []
        if request.company:
            filter_desc.append(f"company '{request.company}'")
        if request.country:
            filter_desc.append(f"country '{request.country}'")

        return {
            "success": True,
            "message": f"Cleared interactions for {cleared_count} jobs from {' and '.join(filter_desc)}",
            "interactions_cleared": cleared_count,
            "note": "These jobs will now appear as fresh/unseen in your feed"
        }

    except Exception as e:
        print(f"❌ Clear interactions failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Clear interactions failed: {str(e)}")

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

        # Get recent activity (last 24 hours) - ONLY ACTIVE USERS
        recent_activity = await conn.fetch("""
            SELECT
                u.id,
                u.username,
                u.full_name,
                u.is_active,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE AND uji.applied_at > NOW() - INTERVAL '24 hours') as applied_24h,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE AND uji.rejected_at > NOW() - INTERVAL '24 hours') as rejected_24h,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE) as total_applied,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE) as total_rejected
            FROM users u
            LEFT JOIN user_job_interactions uji ON u.id = uji.user_id
            WHERE u.is_active = TRUE
            GROUP BY u.id, u.username, u.full_name, u.is_active
            ORDER BY u.username
        """)

        users = []
        for row in recent_activity:
            users.append({
                'id': row['id'],
                'username': row['username'],
                'full_name': row['full_name'],
                'is_active': row['is_active'],
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

@app.get("/api/admin/users")
async def get_all_users(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all users with their active status (admin only)"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Get all users with their stats and preferences
        users = await conn.fetch("""
            SELECT
                u.id,
                u.username,
                u.email,
                u.full_name,
                u.is_active,
                u.is_admin,
                u.created_at,
                u.last_login,
                up.job_types,
                up.preferred_countries as countries,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.applied = TRUE) as total_applied,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.rejected = TRUE) as total_rejected,
                COUNT(DISTINCT uji.job_id) FILTER (WHERE uji.saved = TRUE) as total_saved,
                MAX(uji.updated_at) as last_interaction
            FROM users u
            LEFT JOIN user_preferences up ON u.id = up.user_id
            LEFT JOIN user_job_interactions uji ON u.id = uji.user_id
            GROUP BY u.id, u.username, u.email, u.full_name, u.is_active, u.is_admin, u.created_at, u.last_login, up.job_types, up.preferred_countries
            ORDER BY u.created_at DESC
        """)

        await db._release(conn)

        user_list = []
        for row in users:
            user_list.append({
                'id': row['id'],
                'username': row['username'],
                'email': row['email'],
                'full_name': row['full_name'],
                'is_active': row['is_active'],
                'is_admin': row['is_admin'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'last_login': row['last_login'].isoformat() if row['last_login'] else None,
                'job_types': row['job_types'],
                'countries': row['countries'],
                'stats': {
                    'total_applied': row['total_applied'],
                    'total_rejected': row['total_rejected'],
                    'total_saved': row['total_saved'],
                    'last_interaction': row['last_interaction'].isoformat() if row['last_interaction'] else None
                }
            })

        return {
            'success': True,
            'users': user_list,
            'total': len(user_list)
        }

    except Exception as e:
        print(f"❌ Failed to get users: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@app.post("/api/admin/users/{user_id}/deactivate")
async def deactivate_user(user_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Deactivate a user (admin only)"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    # Don't allow self-deactivation
    if current_user.get('user_id') == user_id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Check if user exists
        user = await conn.fetchrow("SELECT id, username, is_active FROM users WHERE id = $1", user_id)
        if not user:
            await db._release(conn)
            raise HTTPException(status_code=404, detail="User not found")

        if not user['is_active']:
            await db._release(conn)
            return {
                'success': True,
                'message': 'User is already deactivated',
                'user_id': user_id,
                'username': user['username']
            }

        # Deactivate user
        await conn.execute("""
            UPDATE users
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """, user_id)

        await db._release(conn)

        logger.info("User %s (ID: %d) deactivated by admin %s", user['username'], user_id, current_user.get('username'))

        return {
            'success': True,
            'message': 'User deactivated successfully',
            'user_id': user_id,
            'username': user['username']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to deactivate user %d: %s", user_id, e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to deactivate user: {str(e)}")

@app.post("/api/admin/users/{user_id}/activate")
async def activate_user(user_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Reactivate a user (admin only)"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Check if user exists
        user = await conn.fetchrow("SELECT id, username, is_active FROM users WHERE id = $1", user_id)
        if not user:
            await db._release(conn)
            raise HTTPException(status_code=404, detail="User not found")

        if user['is_active']:
            await db._release(conn)
            return {
                'success': True,
                'message': 'User is already active',
                'user_id': user_id,
                'username': user['username']
            }

        # Reactivate user
        await conn.execute("""
            UPDATE users
            SET is_active = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """, user_id)

        await db._release(conn)

        logger.info("User %s (ID: %d) reactivated by admin %s", user['username'], user_id, current_user.get('username'))

        return {
            'success': True,
            'message': 'User activated successfully',
            'user_id': user_id,
            'username': user['username']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to activate user %d: %s", user_id, e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to activate user: {str(e)}")

@app.delete("/api/admin/users/{user_id}")
async def delete_user_permanently(user_id: int, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Permanently delete a user and all their data (admin only)"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    if current_user.get('user_id') == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    try:
        conn = await db.get_connection()
        try:
            user = await conn.fetchrow("SELECT id, username FROM users WHERE id = $1", user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Delete all user data in order (FK constraints)
            await conn.execute("DELETE FROM user_job_interactions WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM interview_tracker WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM user_preferences WHERE user_id = $1", user_id)
            await conn.execute("DELETE FROM users WHERE id = $1", user_id)

            logger.info("User %s (ID: %d) permanently deleted by admin %s", user['username'], user_id, current_user.get('username'))

            return {'success': True, 'message': f"User '{user['username']}' permanently deleted", 'user_id': user_id}
        finally:
            await db._release(conn)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete user %d: %s", user_id, e)
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

class AdminCreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    is_admin: bool = False
    job_types: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    preferred_countries: Optional[List[str]] = None

class UpdateUserCountriesRequest(BaseModel):
    countries: List[str]

class UpdateUserJobTypesRequest(BaseModel):
    job_types: List[str]

class ActivityEventRequest(BaseModel):
    event_type: str
    event_data: Optional[Dict[str, Any]] = None

@app.post("/api/admin/users")
async def admin_create_user(
    request: AdminCreateUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new user (admin only)"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    from user_database import UserDatabase
    from auth_utils import validate_password_strength, validate_email, validate_username

    valid, error = validate_username(request.username)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    valid, error = validate_email(request.email)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    valid, error = validate_password_strength(request.password)
    if not valid:
        raise HTTPException(status_code=400, detail=error)

    user_db = UserDatabase()
    user = await user_db.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        is_admin=request.is_admin
    )

    if not user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    # Set preferences if provided
    preferences = {}
    if request.job_types:
        preferences['job_types'] = request.job_types
    if request.keywords:
        preferences['keywords'] = request.keywords
    if request.preferred_countries:
        preferences['preferred_countries'] = request.preferred_countries

    if preferences:
        await user_db.update_user_preferences(user['id'], preferences)

    logger.info(f"Admin {current_user.get('username')} created new user: {request.username}")

    return {
        'success': True,
        'message': f"User '{request.username}' created successfully",
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user.get('full_name'),
            'is_admin': user['is_admin']
        }
    }

@app.get("/api/admin/scraping-targets")
async def get_scraping_targets():
    """Get job types and countries that should be scraped based on active users' preferences"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    if not db.use_postgres:
        raise HTTPException(status_code=500, detail="PostgreSQL database required")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Get all active users with their preferences including custom keywords
        users = await conn.fetch("""
            SELECT DISTINCT
                u.id,
                u.username,
                up.job_types,
                up.preferred_countries as countries,
                up.keywords
            FROM users u
            LEFT JOIN user_preferences up ON u.id = up.user_id
            WHERE u.is_active = TRUE
        """)

        await db._release(conn)

        # Aggregate job types, countries, and custom keywords across all active users
        all_job_types = set()
        all_countries = set()
        custom_keywords_by_type = {}  # {job_type: set of keywords}

        for user in users:
            if user['job_types']:
                for job_type in user['job_types']:
                    all_job_types.add(job_type)

            if user['countries']:
                for country in user['countries']:
                    all_countries.add(country)

            # Attach user keywords to each of their job types
            if user['keywords'] and user['job_types']:
                for job_type in user['job_types']:
                    if job_type not in custom_keywords_by_type:
                        custom_keywords_by_type[job_type] = set()
                    for kw in user['keywords']:
                        custom_keywords_by_type[job_type].add(kw)

        if not all_job_types:
            all_job_types = {'software'}
        if not all_countries:
            all_countries = {'Ireland'}

        # Build job_type_configs — consumed by the scraper to add custom keywords on top of defaults
        job_type_configs = [
            {
                'type': jt,
                'custom_keywords': sorted(list(custom_keywords_by_type.get(jt, [])))
            }
            for jt in sorted(all_job_types)
        ]

        return {
            'success': True,
            'active_users_count': len(users),
            'job_types': sorted(list(all_job_types)),       # kept for backward compat
            'job_type_configs': job_type_configs,            # new: includes custom keywords
            'countries': sorted(list(all_countries)),
            'scraping_needed': len(all_job_types) > 0 and len(all_countries) > 0,
            'message': f'Scraping targets generated from {len(users)} active users'
        }

    except Exception as e:
        print(f"❌ Failed to get scraping targets: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get scraping targets: {str(e)}")

ALL_COUNTRIES = ['Ireland', 'Spain', 'Panama', 'Luxembourg', 'Germany', 'Switzerland', 'United States']

class ScraperRunLogRequest(BaseModel):
    country: str
    github_run_id: Optional[str] = None
    github_run_number: Optional[int] = None
    started_at: str  # ISO timestamp
    duration_seconds: Optional[int] = None
    phase_fetch_existing_seconds: Optional[float] = None
    phase_fetch_job_types_seconds: Optional[float] = None
    phase_scraping_seconds: Optional[float] = None
    phase_upload_seconds: Optional[float] = None
    total_terms: Optional[int] = None
    successful_searches: Optional[int] = None
    failed_searches: Optional[int] = None
    jobs_scraped: Optional[int] = None
    new_jobs: Optional[int] = None
    dry_run: bool = False
    error: Optional[str] = None

@app.post("/api/scraper/run-log")
async def post_scraper_run_log(request: ScraperRunLogRequest):
    """Called by GitHub Actions scraper after each country finishes — no user auth needed"""
    if not db or not DATABASE_AVAILABLE or not db.use_postgres:
        return {"success": False, "reason": "database unavailable"}
    conn = None
    try:
        conn = await db.get_connection()
        if not conn:
            return {"success": False, "reason": "no connection"}
        await conn.execute("""
            INSERT INTO scraper_run_logs (
                country, github_run_id, github_run_number, started_at, duration_seconds,
                phase_fetch_existing_seconds, phase_fetch_job_types_seconds,
                phase_scraping_seconds, phase_upload_seconds,
                total_terms, successful_searches, failed_searches,
                jobs_scraped, new_jobs, dry_run, error
            ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)
        """,
            request.country, request.github_run_id, request.github_run_number,
            datetime.fromisoformat(request.started_at.replace("Z", "+00:00")),
            request.duration_seconds,
            request.phase_fetch_existing_seconds, request.phase_fetch_job_types_seconds,
            request.phase_scraping_seconds, request.phase_upload_seconds,
            request.total_terms, request.successful_searches, request.failed_searches,
            request.jobs_scraped, request.new_jobs, request.dry_run, request.error
        )
        logger.info("Scraper run log saved: %s (%ds)", request.country, request.duration_seconds or 0)
        return {"success": True}
    except Exception as e:
        logger.error("Failed to save scraper run log: %s", e)
        return {"success": False, "reason": str(e)}
    finally:
        if conn:
            await db._release(conn)

async def _fetch_queue_snapshot() -> dict:
    """Fetch current queue status from DB. Used by both REST and SSE endpoints."""
    conn = await db.get_connection()
    if not conn:
        return {"error": "Database connection failed"}
    try:
        counts_rows = await conn.fetch(
            "SELECT status, COUNT(*) AS count FROM job_upload_queue GROUP BY status"
        )
        counts = {r['status']: r['count'] for r in counts_rows}

        items = await conn.fetch("""
            SELECT id, job_count, status,
                   created_at, started_at, finished_at,
                   EXTRACT(EPOCH FROM (COALESCE(finished_at, NOW()) - started_at))::int AS processing_secs,
                   result->>'new_jobs'     AS new_jobs,
                   result->>'updated_jobs' AS updated_jobs,
                   error_text
            FROM job_upload_queue
            ORDER BY created_at DESC
            LIMIT 30
        """)

        return {
            "summary": {
                "pending":    counts.get("pending",    0),
                "processing": counts.get("processing", 0),
                "done":       counts.get("done",       0),
                "failed":     counts.get("failed",     0),
            },
            "items": [
                {
                    "id":              r["id"],
                    "job_count":       r["job_count"],
                    "status":          r["status"],
                    "created_at":      r["created_at"].isoformat() if r["created_at"] else None,
                    "started_at":      r["started_at"].isoformat() if r["started_at"] else None,
                    "finished_at":     r["finished_at"].isoformat() if r["finished_at"] else None,
                    "processing_secs": r["processing_secs"],
                    "new_jobs":        int(r["new_jobs"] or 0),
                    "updated_jobs":    int(r["updated_jobs"] or 0),
                    "error_text":      r["error_text"],
                }
                for r in items
            ],
        }
    finally:
        await db._release(conn)


@app.get("/api/admin/queue-status")
async def get_queue_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return job upload queue summary and recent items (single snapshot)."""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")
    return await _fetch_queue_snapshot()


@app.get("/api/admin/queue-status/stream")
async def queue_status_stream(token: str = ""):
    """SSE stream: pushes queue status every 2 seconds. Auth via ?token= query param."""
    from fastapi.responses import StreamingResponse as _SR

    # Validate token manually (EventSource can't send Authorization header)
    if not token or not AUTH_AVAILABLE:
        return _SR(iter([b"data: {\"error\": \"unauthorized\"}\n\n"]),
                   media_type="text/event-stream", status_code=401)
    try:
        from auth_utils import decode_access_token
        user = decode_access_token(token)
        if not user or not user.get("is_admin"):
            return _SR(iter([b"data: {\"error\": \"forbidden\"}\n\n"]),
                       media_type="text/event-stream", status_code=403)
    except Exception:
        return _SR(iter([b"data: {\"error\": \"unauthorized\"}\n\n"]),
                   media_type="text/event-stream", status_code=401)

    async def event_generator():
        try:
            while True:
                try:
                    if db and DATABASE_AVAILABLE:
                        data = await _fetch_queue_snapshot()
                    else:
                        data = {"error": "Database not available"}
                    yield f"data: {json.dumps(data)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            pass  # Client disconnected

    from fastapi.responses import StreamingResponse as _SR2
    return _SR2(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/admin/monitoring")
async def get_monitoring(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get GitHub Actions pipeline status, DB stats, and Sentry info"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    import requests as req_lib

    github_token = os.environ.get("GITHUB_TOKEN", "")
    sentry_dsn = os.environ.get("SENTRY_DSN", "")
    workflows = ["parallel-scraper.yml", "test-scraper.yml"]

    async def fetch_workflow_runs(filename: str):
        url = f"https://api.github.com/repos/nickykapur/job-scrapper/actions/workflows/{filename}/runs?per_page=5"
        headers = {"Authorization": f"Bearer {github_token}", "Accept": "application/vnd.github+json"}
        try:
            resp = await asyncio.to_thread(req_lib.get, url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                runs = []
                for r in data.get("workflow_runs", []):
                    started = r.get("run_started_at") or r.get("created_at")
                    updated = r.get("updated_at")
                    duration = None
                    if started and updated:
                        try:
                            from datetime import timezone
                            s = datetime.fromisoformat(started.replace("Z", "+00:00"))
                            e = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                            duration = int((e - s).total_seconds())
                        except Exception:
                            pass
                    runs.append({
                        "id": r.get("id"),
                        "status": r.get("status"),
                        "conclusion": r.get("conclusion"),
                        "event": r.get("event"),
                        "run_started_at": started,
                        "updated_at": updated,
                        "duration_seconds": duration,
                        "html_url": r.get("html_url"),
                        "run_number": r.get("run_number"),
                    })
                return {"name": filename, "runs": runs, "error": None}
            else:
                return {"name": filename, "runs": [], "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"name": filename, "runs": [], "error": str(e)}

    workflow_results = await asyncio.gather(*[fetch_workflow_runs(w) for w in workflows])

    # DB stats
    db_stats = {"total_jobs": 0, "by_country": [], "by_job_type": [], "storage": None, "oldest_job": None, "newest_job": None, "error": None}
    if db and DATABASE_AVAILABLE and db.use_postgres:
        conn = None
        try:
            conn = await db.get_connection()
            if conn:
                country_rows = await conn.fetch("""
                    SELECT country, COUNT(*) as count, MAX(scraped_at) as last_scraped
                    FROM jobs
                    GROUP BY country
                    ORDER BY count DESC
                """)
                job_type_rows = await conn.fetch("""
                    SELECT job_type, COUNT(*) as count
                    FROM jobs
                    GROUP BY job_type
                    ORDER BY count DESC
                """)
                total_row = await conn.fetchrow("SELECT COUNT(*) as total FROM jobs")
                db_stats["total_jobs"] = total_row["total"] if total_row else 0
                db_stats["by_country"] = [
                    {"country": r["country"], "count": r["count"], "last_scraped": r["last_scraped"].isoformat() if r["last_scraped"] else None}
                    for r in country_rows
                ]
                db_stats["by_job_type"] = [
                    {"job_type": r["job_type"] or "unknown", "count": r["count"]}
                    for r in job_type_rows
                ]

                # Storage metrics
                storage_row = await conn.fetchrow("""
                    SELECT
                        pg_database_size(current_database()) AS db_bytes,
                        pg_total_relation_size('jobs') AS jobs_total_bytes,
                        pg_relation_size('jobs') AS jobs_data_bytes,
                        pg_indexes_size('jobs') AS jobs_index_bytes
                """)
                if storage_row:
                    db_stats["storage"] = {
                        "db_bytes": storage_row["db_bytes"],
                        "jobs_total_bytes": storage_row["jobs_total_bytes"],
                        "jobs_data_bytes": storage_row["jobs_data_bytes"],
                        "jobs_index_bytes": storage_row["jobs_index_bytes"],
                    }

                # Table sizes for all tables
                table_rows = await conn.fetch("""
                    SELECT
                        relname AS table_name,
                        pg_total_relation_size(relid) AS total_bytes,
                        pg_relation_size(relid) AS data_bytes,
                        n_live_tup AS row_estimate
                    FROM pg_stat_user_tables
                    ORDER BY total_bytes DESC
                """)
                db_stats["tables"] = [
                    {
                        "table_name": r["table_name"],
                        "total_bytes": r["total_bytes"],
                        "data_bytes": r["data_bytes"],
                        "row_estimate": r["row_estimate"],
                    }
                    for r in table_rows
                ]

                # Oldest/newest jobs for cleanup guidance
                date_row = await conn.fetchrow("""
                    SELECT MIN(scraped_at) AS oldest, MAX(scraped_at) AS newest FROM jobs
                """)
                if date_row:
                    db_stats["oldest_job"] = date_row["oldest"].isoformat() if date_row["oldest"] else None
                    db_stats["newest_job"] = date_row["newest"].isoformat() if date_row["newest"] else None

                # Rejected + applied job counts (safe to delete)
                cleanup_row = await conn.fetchrow("""
                    SELECT
                        COUNT(*) FILTER (WHERE rejected = TRUE) AS rejected_count,
                        COUNT(*) FILTER (WHERE applied = TRUE) AS applied_count,
                        COUNT(*) FILTER (WHERE first_seen < NOW() - INTERVAL '30 days' AND rejected = FALSE AND applied = FALSE) AS older_than_30d,
                        COUNT(*) FILTER (WHERE first_seen < NOW() - INTERVAL '60 days' AND rejected = FALSE AND applied = FALSE) AS older_than_60d,
                        COUNT(*) FILTER (WHERE applied = FALSE AND rejected = FALSE AND first_seen < NOW() - INTERVAL '7 days') AS stale_posted_date
                    FROM jobs
                """)
                if cleanup_row:
                    db_stats["cleanup_candidates"] = {
                        "rejected": cleanup_row["rejected_count"],
                        "applied": cleanup_row["applied_count"],
                        "older_than_30d": cleanup_row["older_than_30d"],
                        "older_than_60d": cleanup_row["older_than_60d"],
                        "stale_posted_date": cleanup_row["stale_posted_date"],
                    }

                # Recent scraper run logs (last 50 rows grouped by github_run_id)
                try:
                    run_logs = await conn.fetch("""
                        SELECT
                            country, github_run_id, github_run_number,
                            started_at, duration_seconds,
                            phase_fetch_existing_seconds, phase_fetch_job_types_seconds,
                            phase_scraping_seconds, phase_upload_seconds,
                            total_terms, successful_searches, failed_searches,
                            jobs_scraped, new_jobs, dry_run, error
                        FROM scraper_run_logs
                        ORDER BY started_at DESC
                        LIMIT 50
                    """)
                    db_stats["scraper_runs"] = [
                        {
                            "country": r["country"],
                            "github_run_id": r["github_run_id"],
                            "github_run_number": r["github_run_number"],
                            "started_at": r["started_at"].isoformat() if r["started_at"] else None,
                            "duration_seconds": r["duration_seconds"],
                            "phases": {
                                "fetch_existing": r["phase_fetch_existing_seconds"],
                                "fetch_job_types": r["phase_fetch_job_types_seconds"],
                                "scraping": r["phase_scraping_seconds"],
                                "upload": r["phase_upload_seconds"],
                            },
                            "total_terms": r["total_terms"],
                            "successful_searches": r["successful_searches"],
                            "failed_searches": r["failed_searches"],
                            "jobs_scraped": r["jobs_scraped"],
                            "new_jobs": r["new_jobs"],
                            "dry_run": r["dry_run"],
                            "error": r["error"],
                        }
                        for r in run_logs
                    ]
                except Exception:
                    db_stats["scraper_runs"] = []

        except Exception as e:
            db_stats["error"] = str(e)
        finally:
            if conn:
                await db._release(conn)
    else:
        db_stats["error"] = "Database not available"

    # Sentry link
    sentry_info = {"configured": bool(sentry_dsn), "url": None}
    if sentry_dsn:
        try:
            # DSN format: https://<key>@<org>.ingest.sentry.io/<project>
            parts = sentry_dsn.split("@")
            if len(parts) == 2:
                host_part = parts[1].split("/")[0]
                org = host_part.replace(".ingest.sentry.io", "")
                sentry_info["url"] = f"https://sentry.io/organizations/{org}/issues/"
        except Exception:
            pass

    return {
        "success": True,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "github": {
            "token_configured": bool(github_token),
            "workflows": workflow_results,
        },
        "database": db_stats,
        "sentry": sentry_info,
    }


@app.get("/api/admin/user-countries")
async def get_user_countries(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all users with their enabled countries and per-country job counts"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    if not db or not DATABASE_AVAILABLE or not db.use_postgres:
        raise HTTPException(status_code=500, detail="Database not available")

    conn = None
    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        users_rows = await conn.fetch("""
            SELECT u.id, u.username, u.full_name, u.is_active,
                   up.preferred_countries, up.job_types
            FROM users u
            LEFT JOIN user_preferences up ON u.id = up.user_id
            WHERE u.is_active = TRUE
            ORDER BY u.id
        """)

        # Job counts by country + job_type
        job_rows = await conn.fetch("""
            SELECT country, job_type, COUNT(*) as count
            FROM jobs
            GROUP BY country, job_type
        """)

        # Build lookup: {country: {job_type: count}}
        jobs_lookup: Dict[str, Dict[str, int]] = {}
        for row in job_rows:
            c = row["country"] or "Unknown"
            jt = row["job_type"] or "unknown"
            jobs_lookup.setdefault(c, {})[jt] = row["count"]

        users_out = []
        for u in users_rows:
            enabled_countries = list(u["preferred_countries"] or [])
            user_job_types = list(u["job_types"] or [])

            country_breakdown = []
            for country in ALL_COUNTRIES:
                enabled = country in enabled_countries
                if user_job_types:
                    job_count = sum(
                        jobs_lookup.get(country, {}).get(jt, 0)
                        for jt in user_job_types
                    )
                else:
                    job_count = sum(jobs_lookup.get(country, {}).values())
                country_breakdown.append({
                    "country": country,
                    "enabled": enabled,
                    "job_count": job_count,
                })

            users_out.append({
                "id": u["id"],
                "username": u["username"],
                "full_name": u["full_name"],
                "enabled_countries": enabled_countries,
                "job_types": user_job_types,
                "country_breakdown": country_breakdown,
            })

        return {"success": True, "users": users_out}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user countries: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to get user countries: {str(e)}")
    finally:
        if conn:
            await db._release(conn)


@app.post("/api/admin/users/{user_id}/countries")
async def update_user_countries(
    user_id: int,
    request: UpdateUserCountriesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update which countries are enabled for a user"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    invalid = [c for c in request.countries if c not in ALL_COUNTRIES]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid countries: {invalid}")

    from user_database import UserDatabase
    user_db = UserDatabase()
    result = await user_db.update_user_preferences(user_id, {"preferred_countries": request.countries})
    if not result:
        raise HTTPException(status_code=404, detail="User not found or update failed")

    logger.info(
        "Admin %s updated countries for user %d: %s",
        current_user.get("username"), user_id, request.countries
    )
    return {"success": True, "user_id": user_id, "countries": request.countries}


ALL_JOB_TYPES = ['software', 'hr', 'cybersecurity', 'sales', 'finance', 'marketing', 'data', 'design', 'biotech', 'engineering', 'events']

@app.post("/api/admin/users/{user_id}/job-types")
async def update_user_job_types(
    user_id: int,
    request: UpdateUserJobTypesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Update which job types are enabled for a user"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    invalid = [jt for jt in request.job_types if jt not in ALL_JOB_TYPES]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Invalid job types: {invalid}")

    from user_database import UserDatabase
    user_db = UserDatabase()
    result = await user_db.update_user_preferences(user_id, {"job_types": request.job_types})
    if not result:
        raise HTTPException(status_code=404, detail="User not found or update failed")

    logger.info(
        "Admin %s updated job_types for user %d: %s",
        current_user.get("username"), user_id, request.job_types
    )
    return {"success": True, "user_id": user_id, "job_types": request.job_types}


async def _store_activity_event(user_id: int, event_type: str, event_data: dict):
    """Background task to store activity event without blocking the response"""
    try:
        conn = await db.get_connection()
        try:
            await conn.execute(
                "INSERT INTO user_activity_events (user_id, event_type, event_data) VALUES ($1, $2, $3::jsonb)",
                user_id, event_type, json.dumps(event_data)
            )
        finally:
            await db._release(conn)
    except Exception as e:
        logger.warning("Failed to store activity event: %s", e)

@app.post("/api/activity", status_code=202)
async def track_activity(
    request: ActivityEventRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Track a user activity event — fire and forget (202 Accepted)"""
    asyncio.create_task(_store_activity_event(
        current_user.get('user_id'),
        request.event_type,
        request.event_data or {}
    ))
    return {"accepted": True}

@app.get("/api/admin/activity")
async def get_activity_feed(
    limit: int = 150,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get recent user activity events + aggregated stats (admin only)"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")
    conn = await db.get_connection()
    try:
        events = await conn.fetch("""
            SELECT e.id, e.user_id, u.username, COALESCE(u.full_name, u.username) as display_name,
                   e.event_type, e.event_data::text as event_data, e.occurred_at
            FROM user_activity_events e
            JOIN users u ON u.id = e.user_id
            ORDER BY e.occurred_at DESC
            LIMIT $1
        """, limit)

        page_counts = await conn.fetch("""
            SELECT event_data->>'page' as page, COUNT(*) as count
            FROM user_activity_events
            WHERE event_type = 'page_view' AND occurred_at > NOW() - INTERVAL '7 days'
            GROUP BY event_data->>'page'
            ORDER BY count DESC
        """)

        active_today = await conn.fetchval("""
            SELECT COUNT(DISTINCT user_id) FROM user_activity_events
            WHERE occurred_at > NOW() - INTERVAL '24 hours'
        """) or 0

        total_events_7d = await conn.fetchval("""
            SELECT COUNT(*) FROM user_activity_events
            WHERE occurred_at > NOW() - INTERVAL '7 days'
        """) or 0

        def parse_event_data(raw):
            if not raw:
                return {}
            if isinstance(raw, dict):
                return raw
            try:
                return json.loads(raw)
            except Exception:
                return {}

        return {
            "success": True,
            "active_today": int(active_today),
            "total_events_7d": int(total_events_7d),
            "page_views_7d": [{"page": r["page"], "count": int(r["count"])} for r in page_counts if r["page"]],
            "events": [
                {
                    "id": r["id"],
                    "user_id": r["user_id"],
                    "username": r["username"],
                    "display_name": r["display_name"],
                    "event_type": r["event_type"],
                    "event_data": parse_event_data(r["event_data"]),
                    "occurred_at": r["occurred_at"].isoformat() if r["occurred_at"] else None,
                }
                for r in events
            ],
        }
    except Exception as e:
        logger.error("Activity feed error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await db._release(conn)


@app.post("/api/admin/cleanup")
async def admin_cleanup_jobs(
    action: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Delete jobs by category to free DB space. action: rejected|applied|older_30d|older_60d|stale_posted_date"""
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    if not db or not DATABASE_AVAILABLE or not db.use_postgres:
        raise HTTPException(status_code=500, detail="Database not available")

    # WHERE clause for each action — used to nullify FK refs then delete
    action_where = {
        "rejected":          "rejected = TRUE",
        "applied":           "applied = TRUE AND rejected = FALSE",
        "older_30d":         "first_seen < NOW() - INTERVAL '30 days' AND rejected = FALSE AND applied = FALSE",
        "older_60d":         "first_seen < NOW() - INTERVAL '60 days' AND rejected = FALSE AND applied = FALSE",
        # first_seen > 7 days = job has been in DB for a week and is almost certainly expired
        "stale_posted_date": "applied = FALSE AND rejected = FALSE AND first_seen < NOW() - INTERVAL '7 days'",
    }
    if action not in action_where:
        raise HTTPException(status_code=400, detail=f"Unknown action. Use: {list(action_where.keys())}")

    where = action_where[action]
    BATCH_SIZE = 500
    total_deleted = 0

    conn = None
    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # Collect all IDs to delete upfront (avoids long-running DELETE scan)
        ids_to_delete = [row['id'] for row in await conn.fetch(f"SELECT id FROM jobs WHERE {where}")]
        logger.info("Cleanup '%s': found %d jobs to delete", action, len(ids_to_delete))

        if not ids_to_delete:
            return {"success": True, "action": action, "deleted": 0}

        # Process in batches to avoid Railway proxy timeout on large deletions
        for i in range(0, len(ids_to_delete), BATCH_SIZE):
            batch = ids_to_delete[i:i + BATCH_SIZE]
            # Nullify self-referential FK (original_job_id) before deleting to avoid FK constraint errors
            await conn.execute(
                "UPDATE jobs SET original_job_id = NULL WHERE original_job_id = ANY($1::text[])",
                batch
            )
            result = await conn.execute(
                "DELETE FROM jobs WHERE id = ANY($1::text[])",
                batch
            )
            batch_deleted = int(result.split()[-1]) if result else 0
            total_deleted += batch_deleted
            logger.info("Cleanup '%s': batch %d-%d deleted %d", action, i, i + len(batch), batch_deleted)

        logger.info("Admin %s cleanup action '%s': deleted %d jobs total", current_user.get("username"), action, total_deleted)
        return {"success": True, "action": action, "deleted": total_deleted}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Cleanup '%s' failed after %d deleted: %s", action, total_deleted, e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
    finally:
        if conn:
            await db._release(conn)


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

@app.get("/api/admin/country-analytics")
async def get_country_analytics(
    current_user: Dict[str, Any] = Depends(get_current_user),
    days: int = 90
):
    """
    Get comprehensive country-level analytics for admin dashboard
    - Jobs posted per country over time
    - Day of week patterns by country
    - Top companies by country
    - Time series trends
    """
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail="Admin access required")

    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        # 1. Jobs posted per country per day (time series)
        jobs_by_country_date = await conn.fetch("""
            SELECT
                DATE(scraped_at) as date,
                COALESCE(country, 'Unknown') as country,
                COUNT(*) as total_jobs,
                COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                COUNT(DISTINCT company) as unique_companies
            FROM jobs
            WHERE scraped_at >= CURRENT_DATE - INTERVAL '$1 days'
            GROUP BY DATE(scraped_at), country
            ORDER BY date DESC, country
        """.replace('$1', str(days)))

        # 2. Day of week patterns by country
        day_of_week_patterns = await conn.fetch("""
            SELECT
                TO_CHAR(scraped_at, 'Day') as day_name,
                EXTRACT(DOW FROM scraped_at) as day_number,
                COALESCE(country, 'Unknown') as country,
                COUNT(*) as total_jobs,
                COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                ROUND(AVG(CASE WHEN is_new THEN 1 ELSE 0 END) * 100, 2) as new_job_percentage
            FROM jobs
            WHERE scraped_at >= CURRENT_DATE - INTERVAL '$1 days'
            GROUP BY day_name, day_number, country
            ORDER BY day_number, country
        """.replace('$1', str(days)))

        # 3. Top companies by country
        top_companies_by_country = await conn.fetch("""
            SELECT
                COALESCE(country, 'Unknown') as country,
                company,
                COUNT(*) as total_jobs,
                COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                COUNT(*) FILTER (WHERE easy_apply = TRUE) as easy_apply_jobs,
                MAX(scraped_at) as last_posted,
                MIN(scraped_at) as first_posted
            FROM jobs
            WHERE scraped_at >= CURRENT_DATE - INTERVAL '$1 days'
            GROUP BY country, company
            ORDER BY country, total_jobs DESC
        """.replace('$1', str(days)))

        # 4. Country summary stats
        country_summary = await conn.fetch("""
            SELECT
                COALESCE(country, 'Unknown') as country,
                COUNT(*) as total_jobs,
                COUNT(DISTINCT company) as unique_companies,
                COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                COUNT(*) FILTER (WHERE easy_apply = TRUE) as easy_apply_jobs,
                COUNT(DISTINCT DATE(scraped_at)) as active_days,
                MIN(DATE(scraped_at)) as first_scrape,
                MAX(DATE(scraped_at)) as last_scrape,
                ROUND(COUNT(*)::NUMERIC / NULLIF(COUNT(DISTINCT DATE(scraped_at)), 0), 2) as avg_jobs_per_day
            FROM jobs
            WHERE scraped_at >= CURRENT_DATE - INTERVAL '$1 days'
            GROUP BY country
            ORDER BY total_jobs DESC
        """.replace('$1', str(days)))

        # 5. Hourly posting patterns (when are jobs posted - useful for scraper timing)
        hourly_patterns = await conn.fetch("""
            SELECT
                EXTRACT(HOUR FROM scraped_at) as hour,
                COALESCE(country, 'Unknown') as country,
                COUNT(*) as total_jobs
            FROM jobs
            WHERE scraped_at >= CURRENT_DATE - INTERVAL '$1 days'
            GROUP BY hour, country
            ORDER BY hour, country
        """.replace('$1', str(days)))

        # 6. Weekly trends (last N weeks)
        weekly_trends = await conn.fetch("""
            SELECT
                DATE_TRUNC('week', scraped_at) as week_start,
                COALESCE(country, 'Unknown') as country,
                COUNT(*) as total_jobs,
                COUNT(*) FILTER (WHERE is_new = TRUE) as new_jobs,
                COUNT(DISTINCT company) as unique_companies
            FROM jobs
            WHERE scraped_at >= CURRENT_DATE - INTERVAL '$1 days'
            GROUP BY week_start, country
            ORDER BY week_start DESC, country
        """.replace('$1', str(days)))

        await conn.close()

        # Format response
        return {
            "time_range_days": days,
            "generated_at": datetime.now().isoformat(),
            "country_summary": [
                {
                    "country": row['country'],
                    "total_jobs": row['total_jobs'],
                    "unique_companies": row['unique_companies'],
                    "new_jobs": row['new_jobs'],
                    "easy_apply_jobs": row['easy_apply_jobs'],
                    "active_days": row['active_days'],
                    "first_scrape": row['first_scrape'].isoformat() if row['first_scrape'] else None,
                    "last_scrape": row['last_scrape'].isoformat() if row['last_scrape'] else None,
                    "avg_jobs_per_day": float(row['avg_jobs_per_day']) if row['avg_jobs_per_day'] else 0
                }
                for row in country_summary
            ],
            "daily_trends": [
                {
                    "date": row['date'].isoformat(),
                    "country": row['country'],
                    "total_jobs": row['total_jobs'],
                    "new_jobs": row['new_jobs'],
                    "unique_companies": row['unique_companies']
                }
                for row in jobs_by_country_date
            ],
            "day_of_week_patterns": [
                {
                    "day_name": row['day_name'].strip(),
                    "day_number": int(row['day_number']),
                    "country": row['country'],
                    "total_jobs": row['total_jobs'],
                    "new_jobs": row['new_jobs'],
                    "new_job_percentage": float(row['new_job_percentage'])
                }
                for row in day_of_week_patterns
            ],
            "top_companies": [
                {
                    "country": row['country'],
                    "company": row['company'],
                    "total_jobs": row['total_jobs'],
                    "new_jobs": row['new_jobs'],
                    "easy_apply_jobs": row['easy_apply_jobs'],
                    "last_posted": row['last_posted'].isoformat() if row['last_posted'] else None,
                    "first_posted": row['first_posted'].isoformat() if row['first_posted'] else None
                }
                for row in top_companies_by_country
            ],
            "hourly_patterns": [
                {
                    "hour": int(row['hour']),
                    "country": row['country'],
                    "total_jobs": row['total_jobs']
                }
                for row in hourly_patterns
            ],
            "weekly_trends": [
                {
                    "week_start": row['week_start'].isoformat() if row['week_start'] else None,
                    "country": row['country'],
                    "total_jobs": row['total_jobs'],
                    "new_jobs": row['new_jobs'],
                    "unique_companies": row['unique_companies']
                }
                for row in weekly_trends
            ]
        }

    except Exception as e:
        print(f"❌ Error getting country analytics: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get country analytics: {str(e)}")

@app.get("/api/rewards")
async def get_user_rewards(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get gamification rewards for the authenticated user - points, badges, streaks, level"""
    if not db or not DATABASE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Could not connect to database")

        user_id = current_user['user_id']

        # Ensure user has a rewards record
        await conn.execute("""
            INSERT INTO user_rewards (user_id)
            VALUES ($1)
            ON CONFLICT (user_id) DO NOTHING
        """, user_id)

        # Get current rewards data
        rewards_data = await conn.fetchrow("""
            SELECT total_points, level, current_streak, longest_streak, last_activity_date
            FROM user_rewards
            WHERE user_id = $1
        """, user_id)

        # Calculate streak (check if user applied today or yesterday)
        today = datetime.now().date()
        current_streak = rewards_data['current_streak'] if rewards_data else 0
        last_activity = rewards_data['last_activity_date'] if rewards_data else None

        if last_activity:
            days_since_activity = (today - last_activity).days
            if days_since_activity > 1:
                # Streak broken
                current_streak = 0

        # Get total applications breakdown
        app_stats = await conn.fetchrow("""
            SELECT
                COUNT(*) FILTER (WHERE applied = TRUE) as total_applied,
                COUNT(*) FILTER (WHERE saved = TRUE) as total_saved,
                COUNT(*) FILTER (WHERE rejected = TRUE) as total_rejected,
                COUNT(*) FILTER (WHERE applied = TRUE AND applied_at >= NOW() - INTERVAL '7 days') as applied_last_7_days,
                COUNT(*) FILTER (WHERE applied = TRUE AND DATE(applied_at) = CURRENT_DATE) as applied_today,
                COUNT(DISTINCT DATE(applied_at)) FILTER (WHERE applied = TRUE) as active_days
            FROM user_job_interactions
            WHERE user_id = $1
        """, user_id)

        total_applied = app_stats['total_applied'] or 0
        total_saved = app_stats['total_saved'] or 0
        total_rejected = app_stats['total_rejected'] or 0

        # Calculate points (Base points without multipliers for now)
        # Only applying (+10) and saving (+2) give points, rejecting gives 0
        calculated_points = (total_applied * 10) + (total_saved * 2)

        # Determine level based on points
        levels = [
            (0, 1, "Beginner", "👶"),
            (100, 2, "Applicant", "📝"),
            (300, 3, "Job Seeker", "🎯"),
            (750, 4, "Career Hunter", "💼"),
            (1500, 5, "Application Pro", "⭐"),
            (3000, 6, "Job Master", "👑"),
            (7500, 7, "Career Legend", "🏆"),
            (15000, 8, "Elite Hunter", "💎"),
        ]

        current_level = 1
        level_name = "Beginner"
        level_icon = "👶"
        next_level_points = 100

        for points_required, level, name, icon in levels:
            if calculated_points >= points_required:
                current_level = level
                level_name = name
                level_icon = icon

        # Find next level
        for points_required, level, name, icon in levels:
            if level > current_level:
                next_level_points = points_required
                break

        # Check and award badges
        badge_definitions = [
            # Volume badges
            {'id': 'first_step', 'name': 'First Step', 'desc': 'Applied to first job', 'requirement': lambda stats: stats['total_applied'] >= 1, 'points': 50, 'category': 'volume', 'threshold': 1, 'metric': 'applications', 'icon': '🎯'},
            {'id': 'getting_started', 'name': 'Getting Started', 'desc': 'Applied to 5 jobs', 'requirement': lambda stats: stats['total_applied'] >= 5, 'points': 100, 'category': 'volume', 'threshold': 5, 'metric': 'applications', 'icon': '📝'},
            {'id': 'job_hunter', 'name': 'Job Hunter', 'desc': 'Applied to 25 jobs', 'requirement': lambda stats: stats['total_applied'] >= 25, 'points': 250, 'category': 'volume', 'threshold': 25, 'metric': 'applications', 'icon': '🎯'},
            {'id': 'career_seeker', 'name': 'Career Seeker', 'desc': 'Applied to 50 jobs', 'requirement': lambda stats: stats['total_applied'] >= 50, 'points': 500, 'category': 'volume', 'threshold': 50, 'metric': 'applications', 'icon': '💼'},
            {'id': 'application_master', 'name': 'Application Master', 'desc': 'Applied to 100 jobs', 'requirement': lambda stats: stats['total_applied'] >= 100, 'points': 1000, 'category': 'volume', 'threshold': 100, 'metric': 'applications', 'icon': '⭐'},

            # Streak badges
            {'id': 'daily_grinder', 'name': 'Daily Grinder', 'desc': '3 day streak', 'requirement': lambda stats: current_streak >= 3, 'points': 100, 'category': 'streak', 'threshold': 3, 'metric': 'days', 'icon': '🔥'},
            {'id': 'week_warrior', 'name': 'Week Warrior', 'desc': '7 day streak', 'requirement': lambda stats: current_streak >= 7, 'points': 300, 'category': 'streak', 'threshold': 7, 'metric': 'days', 'icon': '💪'},
            {'id': 'month_marathon', 'name': 'Month Marathon', 'desc': '30 day streak', 'requirement': lambda stats: current_streak >= 30, 'points': 1500, 'category': 'streak', 'threshold': 30, 'metric': 'days', 'icon': '🏆'},
        ]

        stats_for_badges = {
            'total_applied': total_applied,
            'total_saved': total_saved,
            'total_rejected': total_rejected,
        }

        # Get already earned badges
        earned_badges = await conn.fetch("""
            SELECT badge_id, badge_name, badge_description, points_awarded, earned_at
            FROM user_badges
            WHERE user_id = $1
            ORDER BY earned_at DESC
        """, user_id)

        earned_badge_ids = {b['badge_id'] for b in earned_badges}

        # Award new badges
        new_badges_awarded = []
        for badge_def in badge_definitions:
            if badge_def['id'] not in earned_badge_ids and badge_def['requirement'](stats_for_badges):
                # Award badge
                await conn.execute("""
                    INSERT INTO user_badges (user_id, badge_id, badge_name, badge_description, points_awarded)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id, badge_id) DO NOTHING
                """, user_id, badge_def['id'], badge_def['name'], badge_def['desc'], badge_def['points'])

                new_badges_awarded.append({
                    'id': badge_def['id'],
                    'name': badge_def['name'],
                    'description': badge_def['desc'],
                    'icon': badge_def['icon'],
                    'points': badge_def['points']
                })

                # Add badge points to total
                calculated_points += badge_def['points']

        # Update rewards record
        await conn.execute("""
            UPDATE user_rewards
            SET total_points = $2,
                level = $3,
                current_streak = $4,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $1
        """, user_id, calculated_points, current_level, current_streak)

        # Get country diversity count
        countries_count = await conn.fetchval("""
            SELECT COUNT(DISTINCT country)
            FROM user_countries
            WHERE user_id = $1
        """, user_id) or 0

        # Prepare all badges with progress information
        all_badges = []
        for badge_def in badge_definitions:
            is_earned = badge_def['id'] in earned_badge_ids

            # Calculate current progress
            if badge_def['metric'] == 'applications':
                current_value = total_applied
            elif badge_def['metric'] == 'days':
                current_value = current_streak
            else:
                current_value = 0

            # Get earned date if badge is earned
            earned_at = None
            if is_earned:
                for b in earned_badges:
                    if b['badge_id'] == badge_def['id']:
                        earned_at = b['earned_at'].isoformat()
                        break

            all_badges.append({
                'id': badge_def['id'],
                'name': badge_def['name'],
                'description': badge_def['desc'],
                'points': badge_def['points'],
                'category': badge_def['category'],
                'threshold': badge_def['threshold'],
                'metric': badge_def['metric'],
                'icon': badge_def['icon'],
                'earned': is_earned,
                'earned_at': earned_at,
                'progress': current_value,
                'progress_percentage': min(100, int((current_value / badge_def['threshold']) * 100)) if badge_def['threshold'] > 0 else 0,
                'remaining': max(0, badge_def['threshold'] - current_value)
            })

        await conn.close()

        return {
            'points': calculated_points,
            'level': current_level,
            'level_name': level_name,
            'level_icon': level_icon,
            'next_level_points': next_level_points,
            'points_to_next_level': max(0, next_level_points - calculated_points),
            'current_streak': current_streak,
            'longest_streak': rewards_data['longest_streak'] if rewards_data else 0,
            'badges': [{
                'id': b['badge_id'],
                'name': b['badge_name'],
                'description': b['badge_description'],
                'points': b['points_awarded'],
                'earned_at': b['earned_at'].isoformat()
            } for b in earned_badges],
            'new_badges': new_badges_awarded,
            'all_badges': all_badges,  # NEW: All badges with progress
            'stats': {
                'total_applied': total_applied,
                'total_saved': total_saved,
                'total_rejected': total_rejected,
                'applied_today': app_stats['applied_today'] or 0,
                'applied_last_7_days': app_stats['applied_last_7_days'] or 0,
                'active_days': app_stats['active_days'] or 0,
                'countries_explored': countries_count
            }
        }

    except Exception as e:
        print(f"❌ Error getting rewards: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get rewards: {str(e)}")

@app.get("/api/insights")
async def get_job_search_insights(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get personalized job search insights and recommendations"""

    try:
        user_id = current_user.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found")

        conn = await db.get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="Database connection failed")

        insights = []

        # Get country application distribution
        country_stats = await conn.fetch("""
            SELECT
                j.country,
                COUNT(*) as applications,
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
            FROM user_job_interactions uji
            JOIN jobs j ON uji.job_id = j.id
            WHERE uji.user_id = $1 AND uji.applied = TRUE AND j.country IS NOT NULL
            GROUP BY j.country
            ORDER BY applications DESC
        """, user_id)

        total_applications = sum(stat['applications'] for stat in country_stats)

        if total_applications >= 10:
            # Check if user is too concentrated in one country
            if country_stats:
                top_country = country_stats[0]
                top_country_name = top_country['country']
                top_country_pct = top_country['percentage']
                top_country_apps = top_country['applications']

                # If more than 70% of applications are in one country
                if top_country_pct > 70 and total_applications >= 15:
                    other_countries = [c['country'] for c in country_stats[1:4] if c['country']]

                    insight = {
                        'type': 'diversification',
                        'severity': 'high',
                        'title': 'Consider Diversifying Your Search',
                        'message': f"You've applied to {top_country_apps} jobs in {top_country_name} ({top_country_pct:.0f}% of total). Expanding to other markets could increase your opportunities!",
                        'action': f"Try exploring: {', '.join(other_countries) if other_countries else 'other countries'}"
                    }
                    insights.append(insight)

                # If more than 50% but less than 70%
                elif top_country_pct > 50 and total_applications >= 20:
                    insight = {
                        'type': 'diversification',
                        'severity': 'medium',
                        'title': 'Good Market Focus',
                        'message': f"You're focusing on {top_country_name} ({top_country_pct:.0f}%). Consider gradually expanding to other regions for more opportunities.",
                        'action': 'Explore 1-2 additional countries'
                    }
                    insights.append(insight)

        # Get available countries user hasn't applied to yet
        unexplored_countries = await conn.fetch("""
            SELECT DISTINCT j.country, COUNT(*) as available_jobs
            FROM jobs j
            WHERE j.country IS NOT NULL
            AND j.country NOT IN (
                SELECT DISTINCT j2.country
                FROM user_job_interactions uji
                JOIN jobs j2 ON uji.job_id = j2.id
                WHERE uji.user_id = $1 AND uji.applied = TRUE AND j2.country IS NOT NULL
            )
            GROUP BY j.country
            HAVING COUNT(*) >= 5
            ORDER BY available_jobs DESC
            LIMIT 5
        """, user_id)

        if unexplored_countries and total_applications >= 10:
            unexplored_list = [f"{c['country']} ({c['available_jobs']} jobs)" for c in unexplored_countries[:3]]
            insight = {
                'type': 'opportunity',
                'severity': 'info',
                'title': 'Untapped Markets',
                'message': f"There are {len(unexplored_countries)} countries with open positions you haven't explored yet.",
                'action': f"Consider: {', '.join(unexplored_list)}"
            }
            insights.append(insight)

        # Check application velocity (daily average)
        velocity_stats = await conn.fetchrow("""
            SELECT
                COUNT(DISTINCT DATE(applied_at)) as active_days,
                COUNT(*) as total_apps,
                MAX(DATE(applied_at)) as last_application_date,
                MIN(DATE(applied_at)) as first_application_date
            FROM user_job_interactions
            WHERE user_id = $1 AND applied = TRUE
        """, user_id)

        if velocity_stats and velocity_stats['active_days']:
            active_days = velocity_stats['active_days']
            total_apps = velocity_stats['total_apps']
            avg_per_day = total_apps / active_days

            # Get recent 7 days activity
            recent_activity = await conn.fetchrow("""
                SELECT COUNT(*) as recent_apps
                FROM user_job_interactions
                WHERE user_id = $1 AND applied = TRUE
                AND applied_at >= CURRENT_DATE - INTERVAL '7 days'
            """, user_id)

            recent_apps = recent_activity['recent_apps'] if recent_activity else 0

            # If user was active but has slowed down
            if avg_per_day >= 2 and recent_apps < 5 and total_apps >= 20:
                insight = {
                    'type': 'motivation',
                    'severity': 'medium',
                    'title': 'Keep the Momentum Going!',
                    'message': f"You were averaging {avg_per_day:.1f} applications per active day, but only {recent_apps} in the last week.",
                    'action': 'Set a goal of 5-10 applications this week to rebuild momentum'
                }
                insights.append(insight)

            # If user is doing well
            elif recent_apps >= 10:
                insight = {
                    'type': 'success',
                    'severity': 'positive',
                    'title': 'Great Momentum!',
                    'message': f"You've applied to {recent_apps} jobs in the last 7 days! You're on fire!",
                    'action': 'Keep up this excellent pace'
                }
                insights.append(insight)

        # Check if user should diversify job types
        job_type_stats = await conn.fetch("""
            SELECT
                j.job_type,
                COUNT(*) as applications,
                COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() as percentage
            FROM user_job_interactions uji
            JOIN jobs j ON uji.job_id = j.id
            WHERE uji.user_id = $1 AND uji.applied = TRUE AND j.job_type IS NOT NULL
            GROUP BY j.job_type
            ORDER BY applications DESC
        """, user_id)

        if job_type_stats and total_applications >= 15:
            top_type = job_type_stats[0]
            if top_type['percentage'] > 80:
                other_types = [jt['job_type'] for jt in job_type_stats[1:] if jt['job_type']]
                insight = {
                    'type': 'diversification',
                    'severity': 'medium',
                    'title': 'Expand Your Job Types',
                    'message': f"Most of your applications are for {top_type['job_type']} roles ({top_type['percentage']:.0f}%).",
                    'action': f"Consider exploring: {', '.join(other_types) if other_types else 'related positions'}"
                }
                insights.append(insight)

        # Time-based insights - Best application times
        time_stats = await conn.fetch("""
            SELECT
                EXTRACT(HOUR FROM applied_at) as hour,
                COUNT(*) as applications
            FROM user_job_interactions
            WHERE user_id = $1 AND applied = TRUE
            GROUP BY EXTRACT(HOUR FROM applied_at)
            ORDER BY applications DESC
            LIMIT 3
        """, user_id)

        if time_stats and total_applications >= 20:
            peak_hours = [int(ts['hour']) for ts in time_stats]
            if peak_hours:
                formatted_hours = [f"{h:02d}:00" for h in peak_hours[:2]]
                insight = {
                    'type': 'pattern',
                    'severity': 'info',
                    'title': 'Your Peak Application Times',
                    'message': f"You're most productive around {' and '.join(formatted_hours)}.",
                    'action': 'Schedule your job search during these peak hours for best results'
                }
                insights.append(insight)

        # If user has very few applications, motivate them
        if total_applications < 5:
            insight = {
                'type': 'motivation',
                'severity': 'info',
                'title': 'Start Strong!',
                'message': "You're just getting started. The more applications you submit, the better your chances!",
                'action': 'Aim for 5 applications this week to build momentum'
            }
            insights.append(insight)

        await conn.close()

        return {
            'insights': insights,
            'total_insights': len(insights),
            'generated_at': datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"❌ Error getting insights: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

# ==================== Interview Tracker Endpoints ====================

@app.get("/api/interview-tracker")
async def get_interview_tracker(current_user: dict = Depends(get_current_user)):
    """Get all interview tracker entries for the current user"""
    if not db or not db.use_postgres:
        raise HTTPException(status_code=503, detail="Database not available")

    user_id = current_user.get('id') or current_user.get('user_id')
    conn = await db.get_connection()

    try:
        rows = await conn.fetch("""
            SELECT * FROM interview_tracker
            WHERE user_id = $1
            ORDER BY last_updated DESC
        """, user_id)

        applications = []
        for row in rows:
            applications.append({
                'id': row['id'],
                'company': row['company'],
                'position': row['position'],
                'location': row['location'],
                'stage': row['stage'],
                'applicationDate': row['application_date'].isoformat() if row['application_date'] else None,
                'recruiterDate': row['recruiter_date'].isoformat() if row['recruiter_date'] else None,
                'technicalDate': row['technical_date'].isoformat() if row['technical_date'] else None,
                'finalDate': row['final_date'].isoformat() if row['final_date'] else None,
                'expectedResponseDate': row['expected_response_date'].isoformat() if row['expected_response_date'] else None,
                'salaryRange': row['salary_range'],
                'recruiterContact': row['recruiter_contact'],
                'recruiterEmail': row['recruiter_email'],
                'notes': row['notes'],
                'stageNotes': row['stage_notes'] or {},
                'lastUpdated': row['last_updated'].isoformat(),
                'archived': row['archived'],
                'archiveOutcome': row['archive_outcome'],
                'archiveDate': row['archive_date'].isoformat() if row['archive_date'] else None,
                'archiveNotes': row['archive_notes'],
                'rejectionStage': row['rejection_stage'],
                'rejectionReasons': row['rejection_reasons'] or [],
                'rejectionDetails': row['rejection_details'],
            })

        return applications

    except Exception as e:
        print(f"❌ Error getting interview tracker: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

@app.post("/api/interview-tracker")
async def save_interview_tracker(
    applications: List[Dict[str, Any]],
    current_user: dict = Depends(get_current_user)
):
    """Save or update interview tracker entries for the current user"""
    if not db or not db.use_postgres:
        raise HTTPException(status_code=503, detail="Database not available")

    user_id = current_user.get('id') or current_user.get('user_id')
    conn = await db.get_connection()

    try:
        # Delete existing entries for this user
        await conn.execute("""
            DELETE FROM interview_tracker WHERE user_id = $1
        """, user_id)

        # Insert new entries
        for app in applications:
            # Helper to parse date strings to date objects
            def parse_date(date_str):
                if not date_str:
                    return None
                try:
                    if isinstance(date_str, str):
                        return datetime.fromisoformat(date_str.split('T')[0]).date()
                    return date_str
                except:
                    return None

            await conn.execute("""
                INSERT INTO interview_tracker (
                    id, user_id, company, position, location, stage,
                    application_date, recruiter_date, technical_date, final_date,
                    expected_response_date, salary_range, recruiter_contact,
                    recruiter_email, notes, stage_notes, last_updated,
                    archived, archive_outcome, archive_date, archive_notes,
                    rejection_stage, rejection_reasons, rejection_details
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13,
                    $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24
                )
            """,
                app['id'],
                user_id,
                app['company'],
                app['position'],
                app['location'],
                app['stage'],
                parse_date(app.get('applicationDate')),
                parse_date(app.get('recruiterDate')),
                parse_date(app.get('technicalDate')),
                parse_date(app.get('finalDate')),
                parse_date(app.get('expectedResponseDate')),
                app.get('salaryRange') or None,
                app.get('recruiterContact') or None,
                app.get('recruiterEmail') or None,
                app.get('notes') or None,
                json.dumps(app.get('stageNotes') or {}),  # Convert dict to JSON string for JSONB
                datetime.fromisoformat(app.get('lastUpdated').replace('Z', '').replace('+00:00', '')) if app.get('lastUpdated') else datetime.now(),
                app.get('archived', False),
                app.get('archiveOutcome') or None,
                datetime.fromisoformat(app.get('archiveDate').replace('Z', '').replace('+00:00', '')) if app.get('archiveDate') else None,
                app.get('archiveNotes') or None,
                app.get('rejectionStage') or None,
                app.get('rejectionReasons') or [],
                app.get('rejectionDetails') or None
            )

        return {"success": True, "count": len(applications)}

    except Exception as e:
        print(f"❌ Error saving interview tracker: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await conn.close()

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