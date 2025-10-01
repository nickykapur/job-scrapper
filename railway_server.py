#!/usr/bin/env python3
"""
Ultra-minimal LinkedIn Job Manager for Railway
Just serves existing job database - no React build needed
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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

app = FastAPI(title="LinkedIn Job Manager", version="1.0.0")

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
    """Load jobs from database or JSON fallback"""
    if db and DATABASE_AVAILABLE:
        try:
            return await db.get_all_jobs()
        except Exception as e:
            print(f"❌ Database load failed: {e}, falling back to JSON")

    # JSON fallback
    jobs_file = "jobs_database.json"
    if os.path.exists(jobs_file):
        try:
            with open(jobs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

async def save_jobs(jobs_data):
    """Save jobs to database or JSON fallback"""
    if db and DATABASE_AVAILABLE:
        try:
            # For save operations, we sync the data to database
            result = await db.sync_jobs_from_scraper(jobs_data)
            return not ("error" in result)
        except Exception as e:
            print(f"❌ Database save failed: {e}, falling back to JSON")

    # JSON fallback
    jobs_file = "jobs_database.json"
    try:
        with open(jobs_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        return True
    except:
        return False

@app.get("/")
async def home():
    """Serve the HTML interface"""
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

@app.get("/jobs_database.json")
async def get_jobs():
    """Get all jobs"""
    return await load_jobs()

@app.post("/update_job")
async def update_job(request: JobUpdateRequest):
    """Update job applied and/or rejected status"""
    if db and DATABASE_AVAILABLE:
        # Use database update method
        try:
            success = await db.update_job_status(
                job_id=request.job_id,
                applied=request.applied,
                rejected=request.rejected
            )
            if success:
                return {"success": True, "message": f"Job {request.job_id} updated"}
            else:
                raise HTTPException(status_code=404, detail="Job not found")
        except Exception as e:
            print(f"❌ Database update failed: {e}, falling back to JSON")

    # JSON fallback
    jobs = await load_jobs()
    if request.job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    # Update applied status if provided
    if request.applied is not None:
        jobs[request.job_id]["applied"] = request.applied

    # Update rejected status if provided
    if request.rejected is not None:
        jobs[request.job_id]["rejected"] = request.rejected
        # If rejecting, also set applied to False
        if request.rejected:
            jobs[request.job_id]["applied"] = False

    if await save_jobs(jobs):
        return {"success": True, "message": f"Job {request.job_id} updated"}
    else:
        raise HTTPException(status_code=500, detail="Failed to save")

@app.post("/sync_jobs")
async def sync_jobs(request: SyncJobsRequest):
    """Sync jobs from local scraper to database"""
    try:
        if db and DATABASE_AVAILABLE:
            # Use database sync method
            result = await db.sync_jobs_from_scraper(request.jobs_data)
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])

            return {
                "success": True,
                "message": f"Synced jobs successfully to database",
                "new_jobs": result.get("new_jobs", 0),
                "updated_jobs": result.get("updated_jobs", 0)
            }

        # JSON fallback
        existing_data = await load_jobs()

        new_jobs = 0
        updated_jobs = 0

        # Merge new data with existing, preserving applied/rejected status
        for job_id, job_data in request.jobs_data.items():
            if job_id.startswith("_"):  # Skip metadata
                continue

            if job_id in existing_data:
                # Preserve applied and rejected status from existing data
                job_data['applied'] = existing_data[job_id].get('applied', False)
                job_data['rejected'] = existing_data[job_id].get('rejected', False)
                updated_jobs += 1
            else:
                new_jobs += 1

            existing_data[job_id] = job_data

        # Update metadata
        existing_data["_metadata"] = {
            "last_updated": datetime.now().isoformat(),
            "total_jobs": len([k for k in existing_data.keys() if not k.startswith("_")]),
            "database_type": "json_sync",
            "last_sync": datetime.now().isoformat()
        }

        # Save updated data
        if await save_jobs(existing_data):
            return {
                "success": True,
                "message": f"Synced jobs successfully to JSON",
                "new_jobs": new_jobs,
                "updated_jobs": updated_jobs
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save synced jobs")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)