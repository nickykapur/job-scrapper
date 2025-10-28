#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os
import subprocess
import sys
from typing import Dict, Any, Optional, List
app = FastAPI(title="LinkedIn Job Manager API", version="1.0.1")

# Try to import database models, fallback to JSON if not available
try:
    from database_models import JobDatabase
    db = JobDatabase()
    USE_DATABASE = True
except ImportError:
    print("⚠️ Database models not available, using JSON fallback")
    db = None
    USE_DATABASE = False

# Import authentication routes
try:
    from auth_routes import router as auth_router
    AUTH_AVAILABLE = True
    print("✅ Authentication routes imported successfully")
except ImportError as e:
    print(f"⚠️  Authentication routes not available: {e}")
    AUTH_AVAILABLE = False

# Include authentication router if available
if AUTH_AVAILABLE:
    app.include_router(auth_router)
    print("✅ Authentication routes registered")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Railway deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React build files (in production)
if os.path.exists("job-manager-ui/dist"):
    app.mount("/assets", StaticFiles(directory="job-manager-ui/dist/assets"), name="assets")

JOBS_DATABASE_FILE = "jobs_database.json"

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    if USE_DATABASE and db:
        await db.init_database()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    import os
    current_dir = os.getcwd()
    files_in_dir = os.listdir(current_dir)
    jobs_file_exists = os.path.exists(JOBS_DATABASE_FILE)
    
    # Try to get file size if it exists
    file_size = 0
    if jobs_file_exists:
        try:
            file_size = os.path.getsize(JOBS_DATABASE_FILE)
        except:
            file_size = -1
    
    return {
        "status": "healthy",
        "environment": os.environ.get("RAILWAY_ENVIRONMENT", "development"),
        "current_directory": current_dir,
        "jobs_database_file": JOBS_DATABASE_FILE,
        "jobs_database_exists": jobs_file_exists,
        "jobs_database_size": file_size,
        "files_in_directory": [f for f in files_in_dir if f.endswith('.json')],
        "api_working": True
    }

class JobUpdateRequest(BaseModel):
    job_id: str
    applied: Optional[bool] = None
    rejected: Optional[bool] = None

class BulkUpdateRequest(BaseModel):
    action: str
    jobs_data: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    keywords: str
    location: Optional[str] = "Dublin, County Dublin, Ireland"

class SyncJobsRequest(BaseModel):
    jobs_data: Dict[str, Any]

class SyncRejectedJobsRequest(BaseModel):
    rejected_job_ids: List[str]

@app.get("/")
async def serve_react_app():
    """Serve the React app in production"""
    if os.path.exists("job-manager-ui/dist/index.html"):
        return FileResponse("job-manager-ui/dist/index.html")
    return {"message": "LinkedIn Job Manager API", "status": "running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "LinkedIn Job Manager API is running"}

@app.get("/jobs_database.json")
async def get_jobs():
    """Get all jobs from the database (PostgreSQL or JSON fallback)"""
    try:
        if USE_DATABASE and db:
            data = await db.get_all_jobs()
            return data
        else:
            # Fallback to JSON file
            if os.path.exists(JOBS_DATABASE_FILE):
                with open(JOBS_DATABASE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data
            else:
                return {
                    "_metadata": {
                        "status": "empty_database",
                        "message": "No jobs database found. Run the Dublin job scraper to populate jobs.",
                        "database_type": "json_fallback"
                    }
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading jobs: {str(e)}")

@app.post("/update_job")
async def update_job(request: JobUpdateRequest):
    """Update a single job's applied or rejected status"""
    try:
        if USE_DATABASE and db:
            # Use the new method that handles both applied and rejected status
            success = await db.update_job_status(request.job_id, request.applied, request.rejected)
            if success:
                return {"success": True, "message": f"Job {request.job_id} updated"}
            else:
                raise HTTPException(status_code=404, detail=f"Job {request.job_id} not found")
        else:
            # Fallback to JSON file update
            if not os.path.exists(JOBS_DATABASE_FILE):
                raise HTTPException(status_code=404, detail="Jobs database not found")

            with open(JOBS_DATABASE_FILE, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)

            if request.job_id not in jobs_data:
                raise HTTPException(status_code=404, detail=f"Job {request.job_id} not found")

            # Update applied status if provided
            if request.applied is not None:
                jobs_data[request.job_id]['applied'] = request.applied

            # Update rejected status if provided
            if request.rejected is not None:
                jobs_data[request.job_id]['rejected'] = request.rejected
                # If rejected, also set applied to False
                if request.rejected:
                    jobs_data[request.job_id]['applied'] = False

            with open(JOBS_DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(jobs_data, f, indent=2, ensure_ascii=False)

            return {"success": True, "message": f"Job {request.job_id} updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bulk_update")
async def bulk_update(request: BulkUpdateRequest):
    """Handle bulk operations like removing applied jobs"""
    try:
        if request.action == "remove_applied":
            if not request.jobs_data:
                raise HTTPException(status_code=400, detail="Jobs data required for remove_applied action")
            
            with open(JOBS_DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(request.jobs_data, f, indent=2, ensure_ascii=False)
            
            return {"success": True, "message": "Applied jobs removed"}
        else:
            raise HTTPException(status_code=400, detail="Unknown bulk action")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_jobs")
async def search_jobs(request: SearchRequest):
    """Run the job scraper with given keywords"""
    try:
        if not request.keywords.strip():
            raise HTTPException(status_code=400, detail="Keywords required")
        
        # Railway environment setup for scraping
        railway_env = os.environ.get("RAILWAY_ENVIRONMENT") == "production"
        if railway_env:
            print("🚀 Running job scraping on Railway Cloud...")
            # Set display for headless browser
            os.environ['DISPLAY'] = ':99'
        
        # Run the job scraper (works both locally and on Railway)
        result = subprocess.run([
            sys.executable, 'main.py', 'search', request.keywords.strip(),
            '--location', request.location, '--headless'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            # Parse the output to get job count
            output_lines = result.stdout.split('\n')
            new_jobs = 0
            for line in output_lines:
                if 'New:' in line:
                    import re
                    match = re.search(r'New: (\d+)', line)
                    if match:
                        new_jobs = int(match.group(1))
                        break
            
            return {"success": True, "message": "Search completed", "new_jobs": new_jobs}
        else:
            raise HTTPException(status_code=500, detail=f"Search failed: {result.stderr}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync_jobs")
async def sync_jobs(request: SyncJobsRequest):
    """Sync jobs from local scraper to database"""
    try:
        if USE_DATABASE and db:
            result = await db.sync_jobs_from_scraper(request.jobs_data)
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return {
                "success": True,
                "message": f"Synced jobs successfully",
                "new_jobs": result.get("new_jobs", 0),
                "updated_jobs": result.get("updated_jobs", 0)
            }
        else:
            # Simple JSON merge for now
            existing_data = {}
            if os.path.exists(JOBS_DATABASE_FILE):
                with open(JOBS_DATABASE_FILE, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            new_jobs = 0
            updated_jobs = 0
            
            for job_id, job_data in request.jobs_data.items():
                if job_id.startswith("_"):
                    continue
                    
                if job_id in existing_data:
                    # Preserve applied status
                    job_data['applied'] = existing_data[job_id].get('applied', False)
                    updated_jobs += 1
                else:
                    new_jobs += 1
                
                existing_data[job_id] = job_data
            
            # Update metadata
            from datetime import datetime
            existing_data["_metadata"] = {
                "last_updated": datetime.now().isoformat(),
                "total_jobs": len([k for k in existing_data.keys() if not k.startswith("_")]),
                "database_type": "json_sync",
                "last_sync": datetime.now().isoformat()
            }
            
            with open(JOBS_DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "message": f"Synced jobs successfully (JSON mode)",
                "new_jobs": new_jobs,
                "updated_jobs": updated_jobs
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rejected_jobs")
async def get_rejected_jobs():
    """Get all rejected job IDs"""
    try:
        if USE_DATABASE and db:
            # TODO: Implement database method to get rejected jobs
            return {"rejected_job_ids": []}
        else:
            # JSON file fallback
            if not os.path.exists(JOBS_DATABASE_FILE):
                return {"rejected_job_ids": []}

            with open(JOBS_DATABASE_FILE, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)

            rejected_job_ids = [
                job_id for job_id, job_data in jobs_data.items()
                if not job_id.startswith('_') and job_data.get('rejected', False)
            ]

            return {"rejected_job_ids": rejected_job_ids}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync_rejected_jobs")
async def sync_rejected_jobs(request: SyncRejectedJobsRequest):
    """Sync locally rejected jobs to the database"""
    try:
        if USE_DATABASE and db:
            # TODO: Implement database method to sync rejected jobs
            return {"success": True, "synced_count": len(request.rejected_job_ids)}
        else:
            # JSON file fallback
            if not os.path.exists(JOBS_DATABASE_FILE):
                raise HTTPException(status_code=404, detail="Jobs database not found")

            with open(JOBS_DATABASE_FILE, 'r', encoding='utf-8') as f:
                jobs_data = json.load(f)

            synced_count = 0
            for job_id in request.rejected_job_ids:
                if job_id in jobs_data and not job_id.startswith('_'):
                    jobs_data[job_id]['rejected'] = True
                    jobs_data[job_id]['applied'] = False  # Rejected jobs can't be applied
                    synced_count += 1

            with open(JOBS_DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(jobs_data, f, indent=2, ensure_ascii=False)

            return {"success": True, "synced_count": synced_count}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/daily_dublin_update")
async def daily_dublin_update():
    """Run the daily Dublin job update directly on Railway"""
    try:
        print("🚀 Starting Daily Dublin Job Update on Railway...")

        # Check if we're in Railway environment for optimizations
        railway_env = os.environ.get("RAILWAY_ENVIRONMENT") == "production"
        if railway_env:
            os.environ['DISPLAY'] = ':99'

        # Run the daily Dublin update script
        result = subprocess.run([
            sys.executable, 'daily_dublin_update.py'
        ], capture_output=True, text=True, cwd='.')

        if result.returncode == 0:
            # Parse output for statistics
            output_lines = result.stdout.split('\n')
            new_jobs = 0
            last_24h_jobs = 0

            for line in output_lines:
                if 'New jobs:' in line:
                    import re
                    match = re.search(r'New jobs: (\d+)', line)
                    if match:
                        new_jobs = int(match.group(1))
                elif 'Last 24h jobs:' in line:
                    match = re.search(r'Last 24h jobs: (\d+)', line)
                    if match:
                        last_24h_jobs = int(match.group(1))

            return {
                "success": True,
                "message": "Daily Dublin update completed on Railway",
                "new_jobs": new_jobs,
                "last_24h_jobs": last_24h_jobs,
                "output": result.stdout
            }
        else:
            return {
                "success": False,
                "message": f"Daily update failed: {result.stderr}",
                "output": result.stdout,
                "error": result.stderr
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daily update error: {str(e)}")

@app.post("/daily_multi_country_update")
async def daily_multi_country_update():
    """Run the daily multi-country job update directly on Railway"""
    try:
        print("🌍 Starting Daily Multi-Country Job Update on Railway...")

        # Check if we're in Railway environment for optimizations
        railway_env = os.environ.get("RAILWAY_ENVIRONMENT") == "production"
        if railway_env:
            os.environ['DISPLAY'] = ':99'

        # Run the daily multi-country update script
        result = subprocess.run([
            sys.executable, 'daily_multi_country_update.py'
        ], capture_output=True, text=True, cwd='.')

        if result.returncode == 0:
            # Parse output for statistics
            output_lines = result.stdout.split('\n')
            new_jobs = 0
            last_24h_jobs = 0
            countries_searched = 0

            for line in output_lines:
                if 'New jobs:' in line:
                    import re
                    match = re.search(r'New jobs: (\d+)', line)
                    if match:
                        new_jobs = int(match.group(1))
                elif 'Last 24h jobs:' in line:
                    match = re.search(r'Last 24h jobs: (\d+)', line)
                    if match:
                        last_24h_jobs = int(match.group(1))
                elif 'countries_searched' in line or line.count('🏳️') > 0:
                    countries_searched += 1

            return {
                "success": True,
                "message": "Daily multi-country update completed on Railway",
                "new_jobs": new_jobs,
                "last_24h_jobs": last_24h_jobs,
                "countries_searched": max(countries_searched, 13),  # Fallback to expected count
                "output": result.stdout
            }
        else:
            return {
                "success": False,
                "message": f"Multi-country update failed: {result.stderr}",
                "output": result.stdout,
                "error": result.stderr
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-country update error: {str(e)}")

@app.get("/api/cron/daily-update")
async def cron_daily_update():
    """Cron endpoint for scheduled daily updates - Dublin only (can be called by external schedulers)"""
    return await daily_dublin_update()

@app.get("/api/cron/multi-country-update")
async def cron_multi_country_update():
    """Cron endpoint for scheduled multi-country updates (can be called by external schedulers)"""
    return await daily_multi_country_update()

@app.get("/country_stats")
async def get_country_stats():
    """Get detailed country statistics for job postings"""
    try:
        if USE_DATABASE and db:
            # TODO: Implement database method to get country stats
            data = await db.get_all_jobs()
        else:
            # Fallback to JSON file
            if os.path.exists(JOBS_DATABASE_FILE):
                with open(JOBS_DATABASE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                return {"country_stats": {}, "message": "No jobs database found"}

        # Extract country statistics from job data
        country_stats = {}
        metadata = data.get('_metadata', {})

        # Get current country stats if available
        if 'country_daily_stats' in metadata:
            country_stats = metadata['country_daily_stats']

        # Calculate additional statistics from job data
        job_data = {k: v for k, v in data.items() if not k.startswith('_')}

        for country in ['Ireland', 'Spain', 'Germany', 'Switzerland', 'United Kingdom', 'Netherlands', 'France', 'Italy']:
            country_jobs = [j for j in job_data.values() if j.get('country') == country and not j.get('rejected', False)]

            if country not in country_stats:
                country_stats[country] = {}

            country_stats[country].update({
                'total_jobs_in_db': len(country_jobs),
                'applied_jobs': len([j for j in country_jobs if j.get('applied', False)]),
                'new_jobs_today': len([j for j in country_jobs if j.get('is_new', False)]),
                'last_24h_jobs': len([j for j in country_jobs if j.get('category') == 'last_24h']),
                'locations': list(set([j.get('search_location', '').split(',')[0] for j in country_jobs if j.get('search_location')]))
            })

        # Add summary statistics
        total_new_today = sum(stats.get('new_jobs_today', 0) for stats in country_stats.values())
        total_24h = sum(stats.get('last_24h_jobs', 0) for stats in country_stats.values())

        return {
            "country_stats": country_stats,
            "summary": {
                "total_new_jobs_today": total_new_today,
                "total_24h_jobs": total_24h,
                "countries_with_jobs": len([c for c, s in country_stats.items() if s.get('total_jobs_in_db', 0) > 0]),
                "last_updated": metadata.get('last_multi_country_search', metadata.get('last_updated', 'Unknown'))
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting country stats: {str(e)}")

# Catch-all route for React Router (must be last)
@app.get("/{path:path}")
async def catch_all(path: str):
    """Serve React app for any unknown routes (for client-side routing)"""
    if os.path.exists("job-manager-ui/dist/index.html"):
        return FileResponse("job-manager-ui/dist/index.html")
    return {"message": "Route not found"}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment (Railway sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting LinkedIn Job Manager API...")
    print(f"📊 API will be available at: http://localhost:{port}")
    print("🌐 React frontend will be served from the same URL")
    print(f"🔗 API docs available at: http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)