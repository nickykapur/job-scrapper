# LinkedIn Job Bot

A Python bot that scrapes LinkedIn for jobs and tracks your application status.

## Features

- Search LinkedIn jobs by keywords and location
- Filter jobs posted in the last 7 days
- Track new vs existing jobs
- Mark jobs as applied and maintain application status
- Persistent job database with JSON storage
- Export results to JSON format
- Command-line interface with multiple commands
- Headless browser support
- Rate limiting and respectful scraping

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Search for Jobs

```bash
# Basic search (backward compatible)
python3 main.py "Python Developer"

# Using search command
python3 main.py search "Python Developer"

# Search with custom location
python3 main.py search "Data Scientist" -l "Remote"

# Show browser window (for debugging)
python3 main.py search "DevOps Engineer" --show-browser
```

### Mark Jobs as Applied

```bash
# Mark a job as applied using its ID
python3 main.py apply 1a2b3c4d5e6f

# The job ID is shown in brackets in the search results
```

### Command Line Arguments

#### Search Command
- `keywords`: Job search keywords (required)
- `-l, --location`: Job location (default: Dublin, County Dublin, Ireland)
- `-o, --output`: Output file name (default: linkedin_jobs.json)
- `--headless`: Run browser in headless mode (default: True)
- `--show-browser`: Show browser window for debugging

#### Apply Command
- `job_id`: The unique ID of the job to mark as applied

## Examples

```bash
# Search for Python developer jobs in Dublin
python3 main.py search "Python Developer"

# Search for remote data science jobs
python3 main.py search "Data Scientist" -l "Remote"

# Search for frontend jobs in San Francisco
python3 main.py search "Frontend Developer" -l "San Francisco"

# Mark a specific job as applied
python3 main.py apply 1a2b3c4d5e6f

# Search and show browser for debugging
python3 main.py search "Software Engineer" --show-browser
```

## Output

The bot will:
1. Display statistics about new vs existing jobs
2. Show applied status for each job
3. Display a detailed summary of found jobs in the terminal
4. Save job information to persistent database (`jobs_database.json`)
5. Save current search results to output file

### Terminal Output Example

```
=== Job Search Results ===
📊 Total: 15 | 🆕 New: 3 | 🔄 Existing: 12
✅ Applied: 5 | ⏳ Not Applied: 10
============================================================

1. [a1b2c3d4e5f6] Senior Python Developer 🆕 ⏳
   Company: Tech Company Inc.
   Location: Dublin, County Dublin, Ireland
   Posted: 2 days ago
   URL: https://linkedin.com/jobs/view/...
------------------------------------------------------------

2. [f6e5d4c3b2a1] Data Scientist ✅
   Company: Data Corp
   Location: Dublin, County Dublin, Ireland
   Posted: 1 day ago
   URL: https://linkedin.com/jobs/view/...
------------------------------------------------------------
```

### Icons Legend
- 🆕 = New job (first time seeing this job)
- 🔄 = Existing job (seen before)
- ✅ = Applied to this job
- ⏳ = Not applied yet

### JSON Database Format

The bot maintains a persistent database (`jobs_database.json`) with all tracked jobs:

```json
{
  "a1b2c3d4e5f6": {
    "id": "a1b2c3d4e5f6",
    "title": "Senior Python Developer",
    "company": "Tech Company Inc.",
    "location": "Dublin, County Dublin, Ireland",
    "posted_date": "2 days ago",
    "job_url": "https://linkedin.com/jobs/view/...",
    "scraped_at": "2023-12-07T10:30:00",
    "applied": false,
    "is_new": true
  }
}
```

## Important Notes

- This bot is for educational and personal use only
- Respect LinkedIn's terms of service and rate limits
- The bot includes delays and respectful scraping practices
- LinkedIn may block automated access - use responsibly
- Consider using LinkedIn's official API for production use

## Troubleshooting

1. **Browser Issues**: Make sure Chrome is installed on your system
2. **No Jobs Found**: Try different keywords or broader location terms
3. **Blocked by LinkedIn**: Wait some time before running again, or try with `--show-browser` to see what's happening

## Requirements

- Python 3.7+
- Chrome browser
- Internet connection