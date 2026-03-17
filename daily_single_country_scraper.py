#!/usr/bin/env python3
"""
Single Country Job Scraper - For parallel GitHub Actions execution
Scrapes one country at a time for faster execution
Uses parallelization (4 concurrent workers) for 6-8x speed improvement
"""

import argparse
import os
import re
import sys
import requests
import time
import threading
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from linkedin_job_scraper import LinkedInJobScraper

# Safety net: even with date_filter="24h" LinkedIn can slip sponsored jobs through.
# Drop anything with a posted_date that indicates it's more than this many days old.
MAX_JOB_AGE_DAYS = 2

def _posted_date_age_days(posted_date: str):
    """
    Parse LinkedIn's 'X hours/days/weeks/months ago' string.
    Returns approximate age in days, or None if unparseable (job is kept).
    """
    if not posted_date:
        return None
    pd = re.sub(r'^posted\s+', '', posted_date.lower().strip())

    if any(w in pd for w in ('just now', 'moments ago', 'today', 'seconds ago')):
        return 0
    m = re.search(r'(\d+)\s+minute', pd)
    if m: return 0
    m = re.search(r'(\d+)\s+hour', pd)
    if m: return int(m.group(1)) / 24
    m = re.search(r'(\d+)\s+day', pd)
    if m: return int(m.group(1))
    m = re.search(r'(\d+)\s+week', pd)
    if m: return int(m.group(1)) * 7
    m = re.search(r'(\d+)\s+month', pd)
    if m: return int(m.group(1)) * 30
    m = re.search(r'(\d+)\s+year', pd)
    if m: return int(m.group(1)) * 365
    # bare keywords without a number
    if 'week' in pd: return 7
    if 'month' in pd: return 30
    if 'year' in pd: return 365
    return None  # unknown — keep the job

# ── Browser pool (thread-local) ───────────────────────────────────────────────
# Each worker thread reuses ONE Chrome instance across all its search tasks
# instead of creating+destroying a browser for every term (~4s startup saved per term)
_thread_local = threading.local()
_all_scrapers: list = []
_scrapers_lock = threading.Lock()

def _get_thread_scraper(existing_jobs: dict) -> LinkedInJobScraper:
    """Return this thread's reusable scraper, creating it on first use."""
    if not getattr(_thread_local, 'scraper', None):
        scraper = LinkedInJobScraper(headless=True)
        scraper.existing_jobs = existing_jobs
        _thread_local.scraper = scraper
        with _scrapers_lock:
            _all_scrapers.append(scraper)
    else:
        # Keep existing_jobs reference in sync (it's the same shared dict, but be explicit)
        _thread_local.scraper.existing_jobs = existing_jobs
    return _thread_local.scraper

def _close_all_scrapers():
    """Close every browser created during this run."""
    with _scrapers_lock:
        for scraper in _all_scrapers:
            try:
                scraper.close()
            except Exception:
                pass
        _all_scrapers.clear()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("scraper")

# ── Sentry (optional — only active when SENTRY_DSN is set in GitHub Actions) ──
import sentry_sdk
_sentry_dsn = os.environ.get("SENTRY_DSN")
if _sentry_dsn:
    sentry_sdk.init(
        dsn=_sentry_dsn,
        environment="github-actions",
        traces_sample_rate=0.0,   # No tracing needed in scraper
        send_default_pii=False,
    )
    logger.info("Sentry enabled for scraper")

# Configuration for parallelization
MAX_CONCURRENT_SEARCHES = 8  # GitHub Actions has enough headroom for 8 parallel browsers
BATCH_DELAY_SECONDS = 1      # Delay between batches to avoid LinkedIn rate limits

# Title keywords for job type validation
# Only jobs with these keywords in title will be kept for each job type
TITLE_KEYWORDS = {
    'software': ['software', 'developer', 'software engineer', 'cloud engineer', 'frontend', 'backend',
                 'full stack', 'fullstack', 'python', 'java', 'react', 'node', 'devops', 'data engineer',
                 'web developer', 'mobile developer', 'ios', 'android', 'qa', 'sdet', 'programming',
                 'coder', 'ml engineer', 'ai engineer', 'platform engineer'],
    'hr': ['hr', 'human resources', 'recruiter', 'recruiting', 'talent', 'people operations',
           'people partner', 'hiring', 'staffing', 'workforce'],
    'cybersecurity': ['security', 'cyber', 'soc', 'infosec', 'information security', 'penetration',
                      'vulnerability', 'threat', 'incident response', 'ciso'],
    'sales': ['sales', 'account executive', 'account manager', 'business development', 'bdr', 'sdr',
              'revenue', 'quota', 'territory', 'inside sales', 'outside sales'],
    'finance': ['finance', 'financial', 'accountant', 'accounting', 'fp&a', 'controller', 'treasury',
                'audit', 'tax', 'bookkeeper', 'cfo', 'fund', 'investment'],
    'marketing': ['marketing', 'brand', 'content', 'seo', 'sem', 'ppc', 'social media', 'digital marketing',
                  'growth', 'demand generation', 'campaign', 'communications', 'pr ', 'public relations'],
    'biotech': ['scientist', 'research', 'biology', 'biotech', 'biotechnology', 'lab', 'laboratory',
                'crispr', 'cell', 'molecular', 'gene', 'pharma', 'clinical', 'r&d', 'biolog'],
    'engineering': ['engineer', 'engineering', 'mechanical', 'manufacturing', 'industrial', 'aerospace',
                    'process engineer', 'design engineer', 'quality engineer', 'production', 'plant',
                    'cad', 'simulation', 'test engineer'],
    'events': ['event', 'conference', 'meeting planner', 'hospitality', 'venue', 'banquet', 'catering',
               'wedding', 'mice', 'tourism', 'convention', 'exhibition', 'trade show', 'coordinator event']
}

def is_relevant_job(title, job_type):
    """Check if job title contains relevant keywords for the job type"""
    if not title or not job_type:
        return True  # Allow if we can't validate

    keywords = TITLE_KEYWORDS.get(job_type, [])
    if not keywords:
        return True  # No keywords defined, allow all

    title_lower = title.lower()
    return any(kw in title_lower for kw in keywords)

def get_active_job_types(railway_url):
    """Fetch active job types + any user-defined custom keywords from the API.

    Returns Dict[job_type, List[custom_keywords]], e.g.:
        {'software': ['Data Scientist'], 'hr': [], 'biotech': ['Virologist']}

    Custom keywords come from user preferences set in the admin frontend.
    Falls back to all types with no custom keywords if the API is unreachable.
    """
    try:
        if not railway_url.startswith('http'):
            railway_url = f'https://{railway_url}'

        response = requests.get(f"{railway_url}/api/admin/scraping-targets", timeout=15)
        if response.status_code == 200:
            data = response.json()
            result = {}
            for config in data.get('job_type_configs', []):
                jt = config['type']
                result[jt] = config.get('custom_keywords', [])
            if result:
                print(f"[API] Active job types: {', '.join(sorted(result.keys()))}")
                for jt, keywords in result.items():
                    if keywords:
                        print(f"[API]   {jt}: +{len(keywords)} custom keywords from users")
                return result
    except Exception as e:
        print(f"[WARN] Could not fetch active job types: {e}")

    # Fallback: scrape all types, no custom keywords
    all_types = ['software', 'hr', 'cybersecurity', 'sales', 'finance', 'marketing', 'biotech', 'engineering', 'events']
    print(f"[WARN] Falling back to all job types")
    return {t: [] for t in all_types}

def load_existing_jobs_from_railway(railway_url):
    """Load existing jobs from Railway database via API"""
    try:
        if not railway_url.startswith('http'):
            railway_url = f'https://{railway_url}'

        api_url = f"{railway_url}/api/jobs"
        response = requests.get(api_url, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"[WARN] Could not load existing jobs: {response.status_code}")
            return {}
    except Exception as e:
        print(f"[WARN] Error loading existing jobs: {e}")
        return {}

UPLOAD_CHUNK_SIZE = 100  # Send at most 100 jobs per request to avoid Railway timeouts

def _empty_upload_result(success=False):
    return {
        'success': success,
        'new_jobs': 0, 'new_software': 0, 'new_hr': 0, 'new_cybersecurity': 0,
        'new_sales': 0, 'new_finance': 0, 'new_marketing': 0, 'new_biotech': 0,
        'new_engineering': 0, 'new_events': 0, 'updated_jobs': 0
    }

def upload_jobs_to_railway(railway_url, jobs_data):
    """Upload jobs to Railway database in chunks to avoid request timeouts."""
    if not railway_url.startswith('http'):
        railway_url = f'https://{railway_url}'

    sync_url = f"{railway_url}/sync_jobs"

    # Separate metadata keys (start with '_') from real job entries
    meta = {k: v for k, v in jobs_data.items() if k.startswith('_')}
    job_items = [(k, v) for k, v in jobs_data.items() if not k.startswith('_')]

    total = len(job_items)
    print(f"   [API] Uploading {total} jobs to: {sync_url} (chunks of {UPLOAD_CHUNK_SIZE})")

    totals = _empty_upload_result(success=True)
    failed_chunks = 0

    for chunk_start in range(0, max(total, 1), UPLOAD_CHUNK_SIZE):
        chunk = dict(job_items[chunk_start:chunk_start + UPLOAD_CHUNK_SIZE])
        chunk.update(meta)  # include metadata in every chunk
        chunk_num = chunk_start // UPLOAD_CHUNK_SIZE + 1
        num_chunks = max((total + UPLOAD_CHUNK_SIZE - 1) // UPLOAD_CHUNK_SIZE, 1)
        print(f"   [API] Chunk {chunk_num}/{num_chunks} ({len(chunk) - len(meta)} jobs)...")

        # /sync_jobs just does a DB queue INSERT and returns — should be fast.
        # Use a short 30s timeout; if Railway's proxy is slow, retry once.
        # NOTE: even when the client times out, the INSERT may have succeeded
        # on Railway's side (the queue worker will still process it).  So a
        # timeout is not necessarily data loss — we log WARN not ERROR to avoid
        # generating a noisy Sentry event for a transient proxy delay.
        chunk_ok = False
        for upload_attempt in range(2):  # try twice
            try:
                response = requests.post(
                    sync_url,
                    json={"jobs_data": chunk},
                    timeout=30,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    result = response.json()
                    for key in ('new_jobs', 'new_software', 'new_hr', 'new_cybersecurity',
                                'new_sales', 'new_finance', 'new_marketing', 'new_biotech',
                                'new_engineering', 'new_events', 'updated_jobs'):
                        totals[key] += result.get(key, 0)
                    chunk_ok = True
                    break
                else:
                    print(f"   [ERROR] Chunk {chunk_num} failed: HTTP {response.status_code}")
            except requests.exceptions.Timeout:
                # Timeout ≠ data loss — Railway proxy may have delayed the response
                # while the INSERT already completed.  Retry once, then warn.
                if upload_attempt == 0:
                    print(f"   [WARN] Chunk {chunk_num} timed out, retrying once...")
                else:
                    print(f"   [WARN] Chunk {chunk_num} timed out twice — "
                          "likely queued on Railway but response was too slow")
                    chunk_ok = True  # Assume queued; don't count as failure
            except Exception as e:
                print(f"   [ERROR] Chunk {chunk_num} upload error: {e}")
                break

        if not chunk_ok:
            failed_chunks += 1

    if failed_chunks:
        print(f"   [WARN] {failed_chunks}/{num_chunks} chunks failed")
        if failed_chunks == num_chunks:
            totals['success'] = False

    nj = totals['new_jobs']
    print(f"   [OK] New: {nj} ({totals['new_software']} software, {totals['new_hr']} HR, "
          f"{totals['new_cybersecurity']} cybersecurity, {totals['new_sales']} sales, "
          f"{totals['new_finance']} finance, {totals['new_marketing']} marketing, "
          f"{totals['new_biotech']} biotech, {totals['new_engineering']} engineering, "
          f"{totals['new_events']} events), Updated: {totals['updated_jobs']}")
    return totals

MAX_SEARCH_RETRIES = 2   # Retry a failed search up to this many times
RETRY_DELAY_SECONDS = 8  # Wait between retries (LinkedIn rate-limit cool-down)

def _reset_thread_scraper(existing_jobs):
    """Close the thread's current scraper and return a fresh one."""
    if getattr(_thread_local, 'scraper', None):
        try:
            _thread_local.scraper.close()
        except Exception:
            pass
        _thread_local.scraper = None
    return _get_thread_scraper(existing_jobs)

def search_single_term(term, location, country_name, existing_jobs, job_type, thread_id):
    """
    Search for jobs with a single term (runs in parallel).
    Reuses this thread's Chrome browser across calls — no startup cost after the first term.
    Retries up to MAX_SEARCH_RETRIES times on failure before giving up.
    Returns: dict with jobs found and metadata
    """
    last_error = None
    for attempt in range(1, MAX_SEARCH_RETRIES + 2):  # e.g. 3 total attempts
        try:
            thread_scraper = _get_thread_scraper(existing_jobs)
            if attempt > 1:
                print(f"   [THREAD-{thread_id}] Retry {attempt - 1}/{MAX_SEARCH_RETRIES}: {term}")
            else:
                print(f"   [THREAD-{thread_id}] Searching: {term}")

            all_results = thread_scraper.search_jobs(
                keywords=term,
                location=location,
                date_filter="24h",  # Daily scraper → only last 24h; 7d leaked old sponsored jobs
                easy_apply_filter=False
            )

            results = {}
            if all_results:
                for job_id, job_data in all_results.items():
                    job_data["country"] = country_name
                    job_data["search_location"] = location
                    results[job_id] = job_data
                print(f"   [THREAD-{thread_id}] ✓ {term}: Found {len(all_results)} jobs")
            else:
                print(f"   [THREAD-{thread_id}] ⊗ {term}: No new jobs")

            return {'term': term, 'jobs': results, 'job_type': job_type, 'success': True, 'thread_id': thread_id}

        except Exception as e:
            last_error = str(e)
            is_bot_detection = 'bot detection' in last_error.lower() or 'sign-in wall' in last_error.lower()
            print(f"   [THREAD-{thread_id}] ✗ {term} (attempt {attempt}): {e}")

            # Always reset the browser after any failure
            thread_scraper = _reset_thread_scraper(existing_jobs)

            if attempt <= MAX_SEARCH_RETRIES:
                # For bot detection, wait longer before retrying
                delay = RETRY_DELAY_SECONDS * (2 if is_bot_detection else 1)
                print(f"   [THREAD-{thread_id}] Waiting {delay}s before retry...")
                time.sleep(delay)
            # else fall through and return failure

    print(f"   [THREAD-{thread_id}] ✗ {term}: All {MAX_SEARCH_RETRIES + 1} attempts failed")
    return {'term': term, 'jobs': {}, 'job_type': job_type, 'success': False, 'error': last_error, 'thread_id': thread_id}

def _post_run_log(railway_url: str, payload: dict):
    """Fire-and-forget POST of scraper timing to the backend."""
    try:
        requests.post(
            f"{railway_url}/api/scraper/run-log",
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"},
        )
    except Exception as e:
        logger.warning("Could not POST run log: %s", e)


def scrape_single_country(location, country_name, railway_url, dry_run=False):
    """Scrape jobs for a single country"""

    run_started_at = datetime.utcnow()
    phases: dict = {}
    run_error: str | None = None

    logger.info("=== Scraping %s (%s) ===", country_name, location)

    # Tag this Sentry session with country so errors are grouped by country
    if _sentry_dsn:
        sentry_sdk.set_tag("country", country_name)
        sentry_sdk.set_tag("location", location)

    # Load existing jobs and active job types from Railway
    _t = time.time()
    existing_jobs = load_existing_jobs_from_railway(railway_url)
    phases["fetch_existing"] = round(time.time() - _t, 1)

    _t = time.time()
    active_job_types = get_active_job_types(railway_url)
    phases["fetch_job_types"] = round(time.time() - _t, 1)

    # Search terms - Multi-user configuration
    software_search_terms = [
        "Software Engineer",
        "Python Developer",
        "React Developer",
        "Full Stack Developer",
        "Backend Developer",
        "Frontend Developer",
        "JavaScript Developer",
        "Node.js Developer",
        "Junior Software Engineer",
        "DevOps Engineer",
        "Cloud Engineer",
        "Data Engineer",
        "Machine Learning Engineer",
        "QA Engineer",
        "Software Developer",
        "Web Developer",
        "Mobile Developer",
        "Java Developer",
        "TypeScript Developer",
        ".NET Developer"
    ]

    cybersecurity_search_terms = [
        # English terms
        "SOC Analyst",
        "Cybersecurity Analyst",
        "Security Analyst",
        "Information Security Analyst",
        "Junior SOC Analyst",
        "Security Operations",
        "Incident Response Analyst",
        # Spanish terms (for Panama and Spain)
        "Analista SOC",
        "Analista de Ciberseguridad",
        "Analista de Seguridad",
    ]

    hr_search_terms = [
        "HR Officer",
        "Talent Acquisition Coordinator",
        "Talent Acquisition Specialist",
        "HR Coordinator",
        "HR Generalist",
        "HR Specialist",
        "Junior Recruiter",
        "Recruiter",
        "Recruitment Coordinator",
        "People Operations",
        "People Partner",
        "HR Assistant",
        "HR Manager",
        "Talent Manager",
        "HR Business Partner",
        "Talent Sourcer"
    ]

    sales_search_terms = [
        "Account Manager",
        "Account Executive",
        "BDR",
        "Business Development Representative",
        "Sales Development Representative",
        "SDR",
        "Inside Sales",
        "Sales Representative",
        "Junior Account Executive",
        "SaaS Sales",
        "B2B Sales",
        "Customer Success Manager",
        "Account Management"
    ]

    finance_search_terms = [
        "FP&A Analyst",
        "Financial Planning Analyst",
        "Financial Analyst",
        "Fund Accounting",
        "Fund Accountant",
        "Fund Operations Analyst",
        "Credit Analyst",
        "Junior Financial Analyst",
        "Accounting Analyst",
        "Finance Analyst",
        "Treasury Analyst",
        "Investment Accounting"
    ]

    # Marketing / Digital Marketing search terms
    marketing_search_terms = [
        "Digital Marketing Manager",
        "Performance Marketing",
        "PPC Manager",
        "Paid Media Manager",
        "Social Media Manager",
        "SEO Manager",
        "Content Marketing Manager",
        "CRM Manager",
        "Email Marketing Manager",
        "Marketing Manager",
        "Brand Manager",
        "Growth Marketing",
        "Community Manager",
        "PR Manager",
    ]

    # Biotech / Life Sciences search terms (for Melis - Molecular Biology)
    biotech_search_terms = [
        "Research Scientist",
        "Research Associate",
        "Cell Culture Scientist",
        "Molecular Biologist",
        "Gene Therapy Scientist",
        "CRISPR Scientist",
        "Biotech Scientist",
        "Process Development Scientist",
        "Upstream Process Scientist",
        "Downstream Process Scientist",
        "Lab Technician",
        "Laboratory Technician",
        # German terms (for Germany searches)
        "Wissenschaftler",
        "Laborant",
        "Biotechnologe",
    ]

    # Engineering / Manufacturing search terms (for Maria - Mechanical/Manufacturing Engineering)
    engineering_search_terms = [
        "Mechanical Engineer",
        "Manufacturing Engineer",
        "Production Engineer",
        "Process Engineer",
        "Industrial Engineer",
        "Aerospace Engineer",
        "Design Engineer",
        "R&D Engineer",
        "Quality Engineer",
        "Test Engineer",
        "Simulation Engineer",
        "Continuous Improvement Engineer",
        "Associate Engineer",
        "Entry Level Engineer",
    ]

    # Events / Hospitality search terms (for Blanca - Event Management)
    events_search_terms = [
        "Event Manager",
        "Event Coordinator",
        "Event Planner",
        "Event Executive",
        "Conference Manager",
        "Corporate Event Manager",
        "Meeting Planner",
        "Hospitality Manager",
        "Venue Manager",
        "Catering Manager",
        "Wedding Planner",
        "MICE Coordinator",
        "Events Assistant",
    ]

    # Default search terms per job type (hardcoded fallback/base)
    default_terms = {
        'software':      software_search_terms,
        'hr':            hr_search_terms,
        'cybersecurity': cybersecurity_search_terms,
        'sales':         sales_search_terms,
        'finance':       finance_search_terms,
        'marketing':     marketing_search_terms,
        'biotech':       biotech_search_terms,
        'engineering':   engineering_search_terms,
        'events':        events_search_terms,
    }

    # Build term_to_job_type mapping:
    # - For each active job type, use default terms + any custom keywords set via admin frontend
    # - New job types (not in default_terms) use only their custom keywords
    term_to_job_type = {}
    for job_type, custom_keywords in active_job_types.items():
        base = default_terms.get(job_type, [])
        all_terms = list(dict.fromkeys(base + custom_keywords))  # dedupe, preserve order
        for term in all_terms:
            if term not in term_to_job_type:  # first job type wins on overlap
                term_to_job_type[term] = job_type

    # Initialize shared data structures (thread-safe)
    all_new_jobs = {}
    jobs_by_type = {}   # {job_type: {job_id: job_data}} — supports any job type dynamically
    successful_searches = 0
    lock = threading.Lock()  # For thread-safe dictionary updates

    print(f"\n[LOCATION] Searching in {location}")
    print(f"[PARALLEL] Using {MAX_CONCURRENT_SEARCHES} concurrent workers")
    print(f"[TERMS] Processing {len(term_to_job_type)} search terms across {len(active_job_types)} job types...")

    # Prepare search tasks — one per search term
    search_tasks = [
        {
            'term': term,
            'location': location,
            'country_name': country_name,
            'existing_jobs': existing_jobs,
            'job_type': job_type,
            'thread_id': idx + 1
        }
        for idx, (term, job_type) in enumerate(term_to_job_type.items())
    ]

    # Execute searches in parallel with ThreadPoolExecutor
    _scraping_start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SEARCHES) as executor:
        future_to_task = {
            executor.submit(
                search_single_term,
                task['term'],
                task['location'],
                task['country_name'],
                task['existing_jobs'],
                task['job_type'],
                task['thread_id']
            ): task for task in search_tasks
        }

        # Process completed searches as they finish
        completed = 0
        for future in as_completed(future_to_task):
            completed += 1
            task = future_to_task[future]

            try:
                result = future.result()

                if result['success']:
                    successful_searches += 1

                    # Thread-safe update of shared dictionaries
                    with lock:
                        for job_id, job_data in result['jobs'].items():
                            if job_id not in all_new_jobs:
                                job_type = result['job_type']
                                job_title = job_data.get('title', '')

                                # Validate title matches job type (filters irrelevant LinkedIn results)
                                if not is_relevant_job(job_title, job_type):
                                    continue

                                job_data['job_type'] = job_type
                                jobs_by_type.setdefault(job_type, {})[job_id] = job_data
                                all_new_jobs[job_id] = job_data
                            else:
                                # Update easy_apply flag if set
                                if job_data.get('easy_apply'):
                                    all_new_jobs[job_id]['easy_apply'] = True

            except Exception as e:
                print(f"   [ERROR] Task failed for {task['term']}: {e}")

            # Progress indicator
            if completed % 10 == 0:
                print(f"   [PROGRESS] {completed}/{len(term_to_job_type)} searches completed...")

            # Small delay between batches to avoid overwhelming LinkedIn
            if completed % MAX_CONCURRENT_SEARCHES == 0:
                time.sleep(BATCH_DELAY_SECONDS)

    phases["scraping"] = round(time.time() - _scraping_start, 1)
    logger.info("[COMPLETE] All %d searches finished for %s in %.0fs", len(term_to_job_type), country_name, phases["scraping"])
    _close_all_scrapers()  # Release all reused Chrome instances

    # Alert when too many searches fail — this is the earliest signal that LinkedIn is
    # blocking us and users will see no new jobs.
    total_terms = len(term_to_job_type)
    failure_rate = (total_terms - successful_searches) / total_terms if total_terms else 0
    if failure_rate >= 0.5 and _sentry_dsn:
        sentry_sdk.capture_message(
            f"High scrape failure rate for {country_name}: "
            f"{total_terms - successful_searches}/{total_terms} searches failed ({failure_rate:.0%}) — "
            "possible LinkedIn bot detection or Chrome crash",
            level="error",
        )

    by_type_summary = ", ".join(f"{jt}: {len(jobs)}" for jt, jobs in jobs_by_type.items())
    logger.info("[SUMMARY] %s: %d/%d searches OK, %d new jobs (%s)",
                country_name, successful_searches, len(term_to_job_type),
                len(all_new_jobs), by_type_summary or "none")

    # Drop stale jobs that LinkedIn slipped through despite the date filter
    stale_count = 0
    fresh_jobs = {}
    for job_id, job_data in all_new_jobs.items():
        age = _posted_date_age_days(job_data.get('posted_date', ''))
        if age is not None and age > MAX_JOB_AGE_DAYS:
            stale_count += 1
        else:
            fresh_jobs[job_id] = job_data
    if stale_count:
        logger.info("[FILTER] Dropped %d stale jobs (posted >%d days ago) for %s",
                    stale_count, MAX_JOB_AGE_DAYS, country_name)
    all_new_jobs = fresh_jobs

    actual_new_total = 0

    if all_new_jobs:
        if dry_run:
            # Dry-run: save to JSON artifact instead of uploading to Railway
            import json as _json
            output_file = f"scraped_jobs_{country_name.lower().replace(' ', '_')}.json"
            with open(output_file, 'w') as f:
                _json.dump({
                    'country': country_name,
                    'location': location,
                    'total_scraped': len(all_new_jobs),
                    'by_type': {jt: len(jobs) for jt, jobs in jobs_by_type.items()},
                    'jobs': list(all_new_jobs.values())
                }, f, indent=2, default=str)
            actual_new_total = len(all_new_jobs)
            logger.info("[DRY-RUN] Saved %d jobs to %s (no upload to Railway)", actual_new_total, output_file)
        else:
            logger.info("[UPLOAD] Uploading %d jobs to Railway...", len(all_new_jobs))
            _t = time.time()
            upload_result = upload_jobs_to_railway(railway_url, all_new_jobs)
            phases["upload"] = round(time.time() - _t, 1)

            if upload_result['success']:
                actual_new_total = upload_result['new_jobs']
                logger.info("[UPLOAD] Success: %d new jobs added to DB for %s", actual_new_total, country_name)
                if _sentry_dsn:
                    sentry_sdk.add_breadcrumb(
                        message=f"{country_name}: {actual_new_total} new jobs uploaded",
                        data={"country": country_name, "new_jobs": actual_new_total, **{f"{jt}_jobs": len(jobs) for jt, jobs in jobs_by_type.items()}},
                        level="info",
                    )
            else:
                # Use warning not error — upload timeouts are often Railway proxy
                # delays where the INSERT already completed on the server side.
                # logger.error would fire a Sentry event for a false alarm.
                logger.warning("[UPLOAD] Upload reported failure for %s (jobs may still be queued on Railway)", country_name)
                run_error = "upload_failed"
    else:
        logger.info("[SKIP] No jobs scraped for %s", country_name)

    # ── POST timing log to backend ────────────────────────────────────────────
    total_duration = int(time.time() - run_started_at.timestamp())
    failed_searches = len(term_to_job_type) - successful_searches
    if railway_url and not dry_run:
        _post_run_log(railway_url, {
            "country": country_name,
            "github_run_id": os.environ.get("GITHUB_RUN_ID"),
            "github_run_number": int(os.environ["GITHUB_RUN_NUMBER"]) if os.environ.get("GITHUB_RUN_NUMBER") else None,
            "started_at": run_started_at.isoformat() + "Z",
            "duration_seconds": total_duration,
            "phase_fetch_existing_seconds": phases.get("fetch_existing"),
            "phase_fetch_job_types_seconds": phases.get("fetch_job_types"),
            "phase_scraping_seconds": phases.get("scraping"),
            "phase_upload_seconds": phases.get("upload"),
            "total_terms": len(term_to_job_type),
            "successful_searches": successful_searches,
            "failed_searches": failed_searches,
            "jobs_scraped": len(all_new_jobs),
            "new_jobs": actual_new_total,
            "dry_run": dry_run,
            "error": run_error,
        })
    logger.info(
        "[TIMING] %s — total %ds | fetch_existing=%.0fs | fetch_job_types=%.0fs | scraping=%.0fs | upload=%.0fs",
        country_name, total_duration,
        phases.get("fetch_existing", 0), phases.get("fetch_job_types", 0),
        phases.get("scraping", 0), phases.get("upload", 0),
    )

    # Set output for GitHub Actions
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
            f.write(f"jobs_found={actual_new_total}\n")
            f.write(f"country={country_name}\n")
            for jt, jobs in jobs_by_type.items():
                f.write(f"{jt}_jobs={len(jobs)}\n")
            f.write(f"dry_run={'true' if dry_run else 'false'}\n")

    logger.info("=== %s scraping complete ===", country_name)
    return run_error is None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape jobs for a single country')
    parser.add_argument('--location', required=True, help='Location string (e.g., "Dublin, County Dublin, Ireland")')
    parser.add_argument('--country', required=True, help='Country name (e.g., "Ireland")')
    parser.add_argument('--railway-url', help='Railway URL (default from env)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Scrape but save results to JSON file instead of uploading to Railway')

    args = parser.parse_args()

    railway_url = args.railway_url or os.environ.get('RAILWAY_URL', '')

    if not args.dry_run and not railway_url:
        print("❌ Error: RAILWAY_URL not provided (use --dry-run to skip upload)")
        sys.exit(1)

    try:
        success = scrape_single_country(args.location, args.country, railway_url, dry_run=args.dry_run)
    except Exception as e:
        logger.error("Scraper crashed for %s: %s", args.country, e, exc_info=True)
        if _sentry_dsn:
            sentry_sdk.capture_exception(e)
        sys.exit(1)

    if not success:
        logger.error("Scraping failed for %s (no exception, returned False)", args.country)
        if _sentry_dsn:
            sentry_sdk.capture_message(f"Scraping returned False for {args.country}", level="error")

    sys.exit(0 if success else 1)
