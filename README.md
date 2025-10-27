# Job Application Tracker

Automated job search and application tracking system for LinkedIn.

## Features

- Multi-country job search (7 countries)
- Automated filtering by experience level
- Company-specific targeting for key markets
- Application status tracking
- Web-based management interface
- Automated database cleanup
- Railway cloud deployment

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Automated Scraping (GitHub Actions)

The system runs automatically via GitHub Actions:
- Executes 7 times daily
- Targets 7 countries
- Automatic cleanup of jobs > 2 days old
- Syncs to Railway cloud database

### Manual Scraping

```bash
python3 daily_multi_country_update.py
```

### Database Cleanup

```bash
python3 cleanup_old_jobs.py
```

### Web Interface

```bash
cd job-manager-ui
npm install
npm run dev
```

Access at http://localhost:5173

## Configuration

### Target Countries
- Ireland (unlimited storage)
- Spain, Panama, Chile (20 jobs each)
- Netherlands, Germany, Sweden (top tech companies only)

### Filters
- Experience: < 5 years
- Age: < 2 days (with automatic cleanup)
- Language: No German fluency requirement

### Database Limits
- Maximum: 300 jobs
- Automatic cleanup triggers when exceeded
- Applied jobs never removed

## Architecture

- **Backend**: Python with Selenium
- **Frontend**: React + TypeScript + MUI
- **Database**: JSON file storage
- **Deployment**: Railway (cloud)
- **Automation**: GitHub Actions

## Development

```bash
# Run scraper locally
python3 daily_multi_country_update.py

# Start web interface
cd job-manager-ui && npm run dev

# Clean database
python3 cleanup_old_jobs.py

# Sync to Railway
python3 sync_to_railway.py
```

## Notes

- Chrome/Firefox browser required
- Uses headless mode by default
- Rate limiting implemented
- Respects LinkedIn ToS