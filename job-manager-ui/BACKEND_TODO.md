# Backend Implementation Required

## Issues Fixed in Frontend:
✅ System Design Object.entries error - Fixed with better null checking
✅ Local storage for rejected jobs - Implemented with cloud sync ready

## Backend Endpoints Needed:

### 1. Update the `/update_job` endpoint to handle rejected status:
```python
@app.post("/update_job")
async def update_job(request: UpdateJobRequest):
    # Current: handles job_id, applied
    # NEEDED: also handle rejected field
    # Example: {"job_id": "123", "rejected": true}
```

### 2. New endpoint: Get rejected jobs from database
```python
@app.get("/rejected_jobs")
async def get_rejected_jobs():
    # Return list of rejected job IDs from PostgreSQL
    return {"rejected_job_ids": ["job1", "job2", "job3"]}
```

### 3. New endpoint: Bulk sync rejected jobs
```python
@app.post("/sync_rejected_jobs")
async def sync_rejected_jobs(request: SyncRejectedJobsRequest):
    # Accept: {"rejected_job_ids": ["job1", "job2"]}
    # Update PostgreSQL to mark these jobs as rejected
    return {"success": True, "synced_count": 2}
```

## Current Status:
- Frontend is ready and working with local storage fallback
- Rejected jobs are stored locally when API calls fail
- Sync button appears when local rejected jobs need syncing
- All endpoints have mock implementations to prevent errors

## Benefits Once Implemented:
- Rejected jobs will sync across devices
- No more lost rejected job preferences
- Offline-first functionality with cloud backup
- Automatic sync when connection is restored