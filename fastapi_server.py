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
from typing import Dict, Any, Optional
from database_models import JobDatabase

app = FastAPI(title="LinkedIn Job Manager API", version="1.0.0")

# Initialize database
db = JobDatabase()

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

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
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
    applied: bool

class BulkUpdateRequest(BaseModel):
    action: str
    jobs_data: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    keywords: str

class SyncJobsRequest(BaseModel):
    jobs_data: Dict[str, Any]

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
        data = await db.get_all_jobs()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading jobs: {str(e)}")

@app.post("/update_job")
async def update_job(request: JobUpdateRequest):
    """Update a single job's applied status"""
    try:
        success = await db.update_job_applied_status(request.job_id, request.applied)
        if success:
            return {"success": True, "message": f"Job {request.job_id} updated"}
        else:
            raise HTTPException(status_code=404, detail=f"Job {request.job_id} not found")
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
        
        # Check if we're in Railway environment
        if os.environ.get("RAILWAY_ENVIRONMENT") == "production":
            return {
                "success": False, 
                "message": "Job scraping is disabled on Railway due to browser limitations. Please use the app with your existing job database or run scraping locally.",
                "new_jobs": 0
            }
        
        # Run the job scraper (local development only)
        result = subprocess.run([
            sys.executable, 'main.py', 'search', request.keywords.strip(), '--headless'
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
        result = await db.sync_jobs_from_scraper(request.jobs_data)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "message": f"Synced jobs successfully",
            "new_jobs": result.get("new_jobs", 0),
            "updated_jobs": result.get("updated_jobs", 0)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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