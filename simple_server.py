#!/usr/bin/env python3
"""
Minimal FastAPI server for Railway deployment
Serves existing job database without scraping capabilities
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
import os
from typing import Dict, Any, Optional

app = FastAPI(title="LinkedIn Job Manager API", version="1.0.0")

# Enable CORS for all origins (Railway deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React build files
if os.path.exists("job-manager-ui/dist"):
    app.mount("/static", StaticFiles(directory="job-manager-ui/dist/assets"), name="static")

JOBS_DATABASE_FILE = "jobs_database.json"

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "jobs_database_exists": os.path.exists(JOBS_DATABASE_FILE),
        "environment": "railway"
    }

class JobUpdateRequest(BaseModel):
    job_id: str
    applied: bool

class BulkUpdateRequest(BaseModel):
    job_ids: list[str]
    applied: bool

class SearchRequest(BaseModel):
    keywords: str

def load_jobs_database():
    """Load jobs from database file"""
    if os.path.exists(JOBS_DATABASE_FILE):
        try:
            with open(JOBS_DATABASE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading jobs database: {e}")
            return {}
    return {}

def save_jobs_database(jobs_data):
    """Save jobs to database file"""
    try:
        with open(JOBS_DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving jobs database: {e}")
        return False

@app.get("/jobs_database.json")
async def get_jobs_database():
    """Get the current jobs database"""
    jobs_data = load_jobs_database()
    return jobs_data

@app.post("/update_job")
async def update_job(request: JobUpdateRequest):
    """Update a specific job's applied status"""
    try:
        jobs_data = load_jobs_database()
        
        if request.job_id not in jobs_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        jobs_data[request.job_id]["applied"] = request.applied
        
        if save_jobs_database(jobs_data):
            return {"success": True, "message": "Job updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save job update")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bulk_update")
async def bulk_update_jobs(request: BulkUpdateRequest):
    """Bulk update multiple jobs' applied status"""
    try:
        jobs_data = load_jobs_database()
        updated_count = 0
        
        for job_id in request.job_ids:
            if job_id in jobs_data:
                jobs_data[job_id]["applied"] = request.applied
                updated_count += 1
        
        if save_jobs_database(jobs_data):
            return {
                "success": True, 
                "message": f"Updated {updated_count} jobs successfully",
                "updated_count": updated_count
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save bulk update")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_jobs")
async def search_jobs(request: SearchRequest):
    """Job scraping disabled on Railway"""
    return {
        "success": False, 
        "message": "Job scraping is not available on Railway due to browser limitations. Use this app to manage your existing job database, or run scraping locally and sync your data.",
        "new_jobs": 0
    }

# Serve React app for all other routes
@app.get("/")
async def serve_app():
    """Serve React app"""
    if os.path.exists("job-manager-ui/dist/index.html"):
        return FileResponse("job-manager-ui/dist/index.html")
    return {"message": "LinkedIn Job Manager API", "status": "active", "frontend": "not built"}

@app.get("/{path:path}")
async def catch_all(path: str):
    """Serve React app for client-side routing"""
    if os.path.exists("job-manager-ui/dist/index.html"):
        return FileResponse("job-manager-ui/dist/index.html")
    return {"error": "Frontend not found", "path": path}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)