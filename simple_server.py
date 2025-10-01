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
    applied: Optional[bool] = None
    rejected: Optional[bool] = None

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
    """Update a specific job's applied and/or rejected status"""
    try:
        jobs_data = load_jobs_database()

        if request.job_id not in jobs_data:
            raise HTTPException(status_code=404, detail="Job not found")

        # Update applied status if provided
        if request.applied is not None:
            jobs_data[request.job_id]["applied"] = request.applied

        # Update rejected status if provided
        if request.rejected is not None:
            jobs_data[request.job_id]["rejected"] = request.rejected
            # If rejecting, also set applied to False
            if request.rejected:
                jobs_data[request.job_id]["applied"] = False

        if save_jobs_database(jobs_data):
            return {"success": True, "message": f"Job {request.job_id} updated"}
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
    """Serve the HTML job manager interface"""
    # Always serve the HTML interface since React isn't built
    HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>LinkedIn Job Manager</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 20px; text-align: center; }
        .header h1 { color: #0066cc; font-size: 32px; margin-bottom: 10px; }
        .header .subtitle { color: #666; font-size: 16px; }
        
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); text-align: center; }
        .stat-number { font-size: 36px; font-weight: bold; color: #0066cc; margin-bottom: 5px; }
        .stat-label { color: #666; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
        
        .controls { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 20px; }
        .filter-row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin-bottom: 15px; }
        .filter-select, .search-input { padding: 10px; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 14px; }
        .filter-select:focus, .search-input:focus { outline: none; border-color: #0066cc; }
        .search-input { flex: 1; min-width: 250px; }
        
        .job-grid { display: grid; gap: 15px; }
        .job-card { 
            background: white; 
            padding: 20px; 
            border-radius: 12px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border-left: 4px solid #ddd;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .job-card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.12); }
        .job-card.applied { border-left-color: #4caf50; background: #f8fff8; }
        .job-card.new { border-left-color: #ff9800; background: #fff8f0; }
        
        .job-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
        .job-title { font-size: 20px; font-weight: 600; color: #0066cc; margin-bottom: 5px; }
        .job-company { font-size: 16px; color: #666; margin-bottom: 5px; }
        .job-location { font-size: 14px; color: #888; }
        
        .job-tags { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 15px; }
        .tag { background: #e3f2fd; color: #1976d2; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 500; }
        .tag.applied { background: #e8f5e8; color: #2e7d32; }
        .tag.new { background: #fff3e0; color: #f57c00; }
        
        .job-actions { display: flex; gap: 10px; flex-wrap: wrap; }
        .btn { 
            padding: 10px 16px; 
            border: none; 
            border-radius: 8px; 
            font-size: 14px; 
            font-weight: 500;
            cursor: pointer; 
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s ease;
        }
        .btn-primary { background: #0066cc; color: white; }
        .btn-primary:hover { background: #0056b3; }
        .btn-success { background: #4caf50; color: white; }
        .btn-success:hover { background: #45a049; }
        .btn-outline { background: white; color: #0066cc; border: 2px solid #0066cc; }
        .btn-outline:hover { background: #0066cc; color: white; }
        
        .loading { text-align: center; padding: 40px; color: #666; }
        .empty-state { text-align: center; padding: 60px 20px; color: #666; }
        .empty-state h3 { margin-bottom: 10px; }
        
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .stats { grid-template-columns: repeat(2, 1fr); }
            .filter-row { flex-direction: column; align-items: stretch; }
            .job-header { flex-direction: column; gap: 10px; }
            .job-actions { justify-content: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔗 LinkedIn Job Manager</h1>
            <div class="subtitle">Manage your job applications efficiently</div>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-number" id="total-count">-</div>
                <div class="stat-label">Total Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="applied-count">-</div>
                <div class="stat-label">Applied</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="new-count">-</div>
                <div class="stat-label">New Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="pending-count">-</div>
                <div class="stat-label">Pending</div>
            </div>
        </div>
        
        <div class="controls">
            <div class="filter-row">
                <select class="filter-select" id="status-filter">
                    <option value="all">All Jobs</option>
                    <option value="applied">Applied</option>
                    <option value="pending">Pending</option>
                    <option value="new">New Jobs</option>
                </select>
                <select class="filter-select" id="sort-filter">
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="company">By Company</option>
                    <option value="title">By Title</option>
                </select>
                <input type="text" class="search-input" id="search-input" placeholder="Search jobs, companies, titles...">
            </div>
        </div>
        
        <div class="job-grid" id="jobs-container">
            <div class="loading">Loading jobs...</div>
        </div>
    </div>
    
    <script>
        let allJobs = [];
        let filteredJobs = [];
        
        // Load jobs on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadJobs();
            setupEventListeners();
        });
        
        function setupEventListeners() {
            document.getElementById('status-filter').addEventListener('change', filterJobs);
            document.getElementById('sort-filter').addEventListener('change', filterJobs);
            document.getElementById('search-input').addEventListener('input', filterJobs);
        }
        
        async function loadJobs() {
            try {
                const response = await fetch('/jobs_database.json');
                const jobsData = await response.json();
                allJobs = Object.values(jobsData);
                updateStats();
                filterJobs();
            } catch (error) {
                console.error('Error loading jobs:', error);
                document.getElementById('jobs-container').innerHTML = 
                    '<div class="empty-state"><h3>Error Loading Jobs</h3><p>Unable to load job database. Please refresh the page.</p></div>';
            }
        }
        
        function updateStats() {
            const total = allJobs.length;
            const applied = allJobs.filter(job => job.applied).length;
            const newJobs = allJobs.filter(job => job.is_new).length;
            const pending = total - applied;
            
            document.getElementById('total-count').textContent = total;
            document.getElementById('applied-count').textContent = applied;
            document.getElementById('new-count').textContent = newJobs;
            document.getElementById('pending-count').textContent = pending;
        }
        
        function filterJobs() {
            const statusFilter = document.getElementById('status-filter').value;
            const sortFilter = document.getElementById('sort-filter').value;
            const searchTerm = document.getElementById('search-input').value.toLowerCase();
            
            // Apply filters
            filteredJobs = allJobs.filter(job => {
                // Status filter
                if (statusFilter === 'applied' && !job.applied) return false;
                if (statusFilter === 'pending' && job.applied) return false;
                if (statusFilter === 'new' && !job.is_new) return false;
                
                // Search filter
                if (searchTerm && !job.title.toLowerCase().includes(searchTerm) && 
                    !job.company.toLowerCase().includes(searchTerm) && 
                    !job.location.toLowerCase().includes(searchTerm)) {
                    return false;
                }
                
                return true;
            });
            
            // Apply sorting
            filteredJobs.sort((a, b) => {
                switch (sortFilter) {
                    case 'newest':
                        return new Date(b.scraped_at) - new Date(a.scraped_at);
                    case 'oldest':
                        return new Date(a.scraped_at) - new Date(b.scraped_at);
                    case 'company':
                        return a.company.localeCompare(b.company);
                    case 'title':
                        return a.title.localeCompare(b.title);
                    default:
                        return 0;
                }
            });
            
            displayJobs();
        }
        
        function displayJobs() {
            const container = document.getElementById('jobs-container');
            
            if (filteredJobs.length === 0) {
                container.innerHTML = '<div class="empty-state"><h3>No Jobs Found</h3><p>Try adjusting your filters or search terms.</p></div>';
                return;
            }
            
            const jobsHTML = filteredJobs.map(job => `
                <div class="job-card ${job.applied ? 'applied' : ''} ${job.is_new ? 'new' : ''}" onclick="toggleJobDetails('${job.id}')">
                    <div class="job-header">
                        <div>
                            <div class="job-title">${job.title}</div>
                            <div class="job-company">${job.company}</div>
                            <div class="job-location">${job.location}</div>
                        </div>
                        <div class="job-tags">
                            ${job.applied ? '<span class="tag applied">Applied</span>' : '<span class="tag">Pending</span>'}
                            ${job.is_new ? '<span class="tag new">New</span>' : ''}
                        </div>
                    </div>
                    <div class="job-actions">
                        <button class="btn ${job.applied ? 'btn-success' : 'btn-primary'}" 
                                onclick="event.stopPropagation(); toggleApplied('${job.id}', ${!job.applied})">
                            ${job.applied ? '✓ Applied' : 'Mark Applied'}
                        </button>
                        <a href="${job.job_url}" target="_blank" class="btn btn-outline" onclick="event.stopPropagation();">
                            🔗 View Job
                        </a>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = jobsHTML;
        }
        
        async function toggleApplied(jobId, applied) {
            try {
                const response = await fetch('/update_job', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ job_id: jobId, applied: applied })
                });
                
                if (response.ok) {
                    // Update local data
                    const job = allJobs.find(j => j.id === jobId);
                    if (job) {
                        job.applied = applied;
                        updateStats();
                        filterJobs();
                    }
                } else {
                    alert('Error updating job status');
                }
            } catch (error) {
                console.error('Error updating job:', error);
                alert('Network error. Please try again.');
            }
        }
        
        function toggleJobDetails(jobId) {
            // Could expand to show more job details in a modal
            console.log('Show details for job:', jobId);
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=HTML_INTERFACE)

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