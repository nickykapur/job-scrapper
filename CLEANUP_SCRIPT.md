# 🧹 Project Cleanup for Railway Deployment

## Files to Remove:

```bash
# Remove old HTML interface and Python server
rm job_manager.html
rm web_server.py  
rm start_ui.py

# Remove debug and one-time scripts
rm debug_selectors.py
rm fix_job_data.py
rm cleanup_applied_jobs.py

# Remove old/backup data files  
rm linkedin_jobs.json
rm applied_jobs_backup_121.json

# Remove installers and build artifacts
rm google-chrome-stable_current_amd64.deb
rm -rf venv/

# Remove Netlify-specific files (not needed for Railway)
rm netlify.toml
rm lighthouserc.json
rm -rf netlify/
rm -rf functions/

# Clean up any nested duplicate folders
# Check for duplicate job-manager-ui or job-scrapper folders
```

## Keep These Files:
- ✅ `fastapi_server.py` (main backend)
- ✅ `linkedin_job_scraper.py` (scraper logic)
- ✅ `main.py` (CLI interface)  
- ✅ `jobs_database.json` (current data)
- ✅ `requirements-fastapi.txt` (dependencies)
- ✅ `job-manager-ui/` (React frontend)
- ✅ Documentation files (*.md)
- ✅ Docker files (optional)
- ✅ `.github/workflows/` (CI/CD)

## Final Structure Should Be:
```
python-job/
├── fastapi_server.py       # Main backend server
├── linkedin_job_scraper.py # Scraping logic  
├── main.py                # CLI interface
├── jobs_database.json     # Job data
├── requirements-fastapi.txt # Python deps
├── job-manager-ui/        # React frontend
│   ├── src/
│   ├── package.json
│   └── ...
├── .github/workflows/     # CI/CD
├── README.md
├── DEPLOYMENT.md
└── RAILWAY_PRICING.md
```