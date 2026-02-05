#!/usr/bin/env python3
"""
Single Country Job Scraper - For parallel GitHub Actions execution
Scrapes one country at a time for faster execution
Uses parallelization (4 concurrent workers) for 6-8x speed improvement
"""

import argparse
import os
import sys
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from linkedin_job_scraper import LinkedInJobScraper

# Configuration for parallelization
MAX_CONCURRENT_SEARCHES = 4  # Safe for GitHub Actions (2 cores, 7GB RAM)
BATCH_DELAY_SECONDS = 2      # Delay between batches to avoid LinkedIn rate limits

# Title keywords for job type validation
# Only jobs with these keywords in title will be kept for each job type
TITLE_KEYWORDS = {
    'software': ['software', 'developer', 'engineer', 'frontend', 'backend', 'full stack', 'fullstack',
                 'python', 'java', 'react', 'node', 'devops', 'cloud', 'data engineer', 'web developer',
                 'mobile developer', 'ios', 'android', 'qa', 'sdet', 'programming', 'coder'],
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

def upload_jobs_to_railway(railway_url, jobs_data):
    """Upload jobs to Railway database and return actual new/updated counts"""
    try:
        if not railway_url.startswith('http'):
            railway_url = f'https://{railway_url}'

        sync_url = f"{railway_url}/sync_jobs"

        print(f"   [API] Uploading to: {sync_url}")
        response = requests.post(
            sync_url,
            json={"jobs_data": jobs_data},
            timeout=60,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            new_jobs = result.get('new_jobs', 0)
            new_software = result.get('new_software', 0)
            new_hr = result.get('new_hr', 0)
            new_cybersecurity = result.get('new_cybersecurity', 0)
            new_sales = result.get('new_sales', 0)
            new_finance = result.get('new_finance', 0)
            new_marketing = result.get('new_marketing', 0)
            new_biotech = result.get('new_biotech', 0)
            new_engineering = result.get('new_engineering', 0)
            new_events = result.get('new_events', 0)
            updated_jobs = result.get('updated_jobs', 0)
            print(f"   [OK] New: {new_jobs} ({new_software} software, {new_hr} HR, {new_cybersecurity} cybersecurity, {new_sales} sales, {new_finance} finance, {new_marketing} marketing, {new_biotech} biotech, {new_engineering} engineering, {new_events} events), Updated: {updated_jobs}")
            return {
                'success': True,
                'new_jobs': new_jobs,
                'new_software': new_software,
                'new_hr': new_hr,
                'new_cybersecurity': new_cybersecurity,
                'new_sales': new_sales,
                'new_finance': new_finance,
                'new_marketing': new_marketing,
                'new_biotech': new_biotech,
                'new_engineering': new_engineering,
                'new_events': new_events,
                'updated_jobs': updated_jobs
            }
        else:
            print(f"   [ERROR] Upload failed: {response.status_code}")
            return {'success': False, 'new_jobs': 0, 'new_software': 0, 'new_hr': 0, 'new_cybersecurity': 0, 'new_sales': 0, 'new_finance': 0, 'new_marketing': 0, 'new_biotech': 0, 'new_engineering': 0, 'new_events': 0, 'updated_jobs': 0}
    except Exception as e:
        print(f"   [ERROR] Upload error: {e}")
        return {'success': False, 'new_jobs': 0, 'new_software': 0, 'new_hr': 0, 'new_cybersecurity': 0, 'new_sales': 0, 'new_finance': 0, 'new_marketing': 0, 'new_biotech': 0, 'new_engineering': 0, 'new_events': 0, 'updated_jobs': 0}

def search_single_term(term, location, country_name, existing_jobs, is_software, is_cybersecurity, is_sales, is_finance, is_marketing, is_biotech, is_engineering, is_events, thread_id):
    """
    Search for jobs with a single term (runs in parallel)
    Returns: dict with jobs found and metadata
    """
    thread_scraper = None
    try:
        # Each thread gets its own browser instance
        thread_scraper = LinkedInJobScraper(headless=True)
        thread_scraper.existing_jobs = existing_jobs

        print(f"   [THREAD-{thread_id}] Searching: {term}")

        results = {}
        easy_apply_count = 0

        # First pass: Get ALL jobs (without Easy Apply filter)
        # Changed from "24h" to "week" to get more job coverage (7 days)
        all_results = thread_scraper.search_jobs(
            keywords=term,
            location=location,
            date_filter="week",
            easy_apply_filter=False
        )

        if all_results:
            # Add country info to all jobs
            for job_id, job_data in all_results.items():
                job_data["country"] = country_name
                job_data["search_location"] = location
                results[job_id] = job_data

            print(f"   [THREAD-{thread_id}] ✓ {term}: Found {len(all_results)} jobs")

            # Second pass: Get Easy Apply jobs ONLY to mark them
            try:
                easy_apply_results = thread_scraper.search_jobs(
                    keywords=term,
                    location=location,
                    date_filter="week",
                    easy_apply_filter=True
                )

                if easy_apply_results:
                    for job_id, job_data in easy_apply_results.items():
                        if job_id in results:
                            results[job_id]['easy_apply'] = True
                            easy_apply_count += 1
                        else:
                            # Add new job that wasn't in first pass
                            job_data["country"] = country_name
                            job_data["search_location"] = location
                            job_data['easy_apply'] = True
                            results[job_id] = job_data

                    print(f"   [THREAD-{thread_id}] ⚡ {term}: Marked {easy_apply_count} as Easy Apply")
            except Exception as ea_error:
                print(f"   [THREAD-{thread_id}] ⚠ {term}: Easy Apply failed: {ea_error}")
        else:
            print(f"   [THREAD-{thread_id}] ⊗ {term}: No new jobs")

        return {
            'term': term,
            'jobs': results,
            'is_software': is_software,
            'is_cybersecurity': is_cybersecurity,
            'is_sales': is_sales,
            'is_finance': is_finance,
            'is_marketing': is_marketing,
            'is_biotech': is_biotech,
            'is_engineering': is_engineering,
            'is_events': is_events,
            'success': True,
            'thread_id': thread_id
        }

    except Exception as e:
        print(f"   [THREAD-{thread_id}] ✗ {term}: Search failed: {e}")
        return {
            'term': term,
            'jobs': {},
            'is_software': is_software,
            'is_cybersecurity': is_cybersecurity,
            'is_sales': is_sales,
            'is_finance': is_finance,
            'is_marketing': is_marketing,
            'is_biotech': is_biotech,
            'is_engineering': is_engineering,
            'is_events': is_events,
            'success': False,
            'error': str(e),
            'thread_id': thread_id
        }
    finally:
        # Clean up browser for this thread
        if thread_scraper:
            try:
                thread_scraper.close()
            except:
                pass

def scrape_single_country(location, country_name, railway_url):
    """Scrape jobs for a single country"""

    print(f"\n{'='*80}")
    print(f"🌍 Scraping {country_name} - {location}")
    print(f"{'='*80}\n")

    # Load existing jobs from Railway
    existing_jobs = load_existing_jobs_from_railway(railway_url)

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
        # Digital Marketing
        "Digital Marketing",
        "Digital Marketing Manager",
        "Digital Marketing Executive",
        "Digital Marketing Specialist",
        "Digital Marketing Coordinator",
        # PPC & Paid Media
        "PPC Executive",
        "PPC Manager",
        "Paid Media Manager",
        "Paid Social Manager",
        "Performance Marketing",
        # Social Media
        "Social Media Manager",
        "Social Media Executive",
        "Social Media Marketing",
        "Community Manager",
        # SEO & Content
        "SEO Specialist",
        "SEO Executive",
        "SEO Manager",
        "Content Marketing Manager",
        "Content Marketing Specialist",
        # CRM & Email
        "CRM Manager",
        "CRM Executive",
        "Email Marketing Manager",
        "Marketing Automation",
        # General Marketing
        "Marketing Manager",
        "Marketing Executive",
        "Marketing Coordinator",
        "Marketing Specialist",
        "Brand Manager",
        "Growth Marketing",
        # Communications
        "Communications Manager",
        "Communications Executive",
        "Marketing Communications",
        "PR Executive"
    ]

    # Biotech / Life Sciences search terms (for Melis - Molecular Biology)
    biotech_search_terms = [
        # Research Scientist roles
        "Research Scientist",
        "Scientist",
        "Research Associate",
        "Junior Scientist",
        "Associate Scientist",
        "R&D Scientist",
        "Lab Scientist",
        # Molecular Biology specific
        "Molecular Biologist",
        "Cell Biologist",
        "Cell Culture Scientist",
        # Gene Editing & Gene Therapy
        "Gene Therapy Scientist",
        "CRISPR Scientist",
        "Gene Editing",
        # Biotech specific
        "Biotechnology",
        "Biotech Scientist",
        "Biologics",
        "Biopharmaceutical",
        # Viral Vectors
        "Viral Vector",
        "AAV Scientist",
        "Vector Production",
        # Process Development
        "Process Development Scientist",
        "Upstream Process",
        "Downstream Process",
        # Lab Technician roles
        "Lab Technician",
        "Research Technician",
        "Laboratory Technician",
        # German terms
        "Wissenschaftler",
        "Laborant",
        "Biotechnologe",
        "Molekularbiologe"
    ]

    # Engineering / Manufacturing search terms (for Maria - Mechanical/Manufacturing Engineering)
    engineering_search_terms = [
        # Mechanical Engineering
        "Mechanical Engineer",
        "Junior Mechanical Engineer",
        "Mechanical Design Engineer",
        "Mechanical Engineer Entry Level",
        # Manufacturing Engineering
        "Manufacturing Engineer",
        "Junior Manufacturing Engineer",
        "Production Engineer",
        "Process Engineer",
        "Manufacturing Process Engineer",
        # Industrial Engineering
        "Industrial Engineer",
        "Junior Industrial Engineer",
        "Operations Engineer",
        "Continuous Improvement Engineer",
        "Lean Engineer",
        # Aerospace Engineering
        "Aerospace Engineer",
        "Junior Aerospace Engineer",
        "Propulsion Engineer",
        # Design & CAD
        "Design Engineer",
        "CAD Engineer",
        "Product Design Engineer",
        "R&D Engineer",
        # Quality & Testing
        "Quality Engineer",
        "Test Engineer",
        "Reliability Engineer",
        # Data & Simulation
        "Simulation Engineer",
        "Data Analyst Manufacturing",
        "Process Optimization",
        # Entry level
        "Entry Level Engineer",
        "Associate Engineer",
        "Engineering Trainee"
    ]

    # Events / Hospitality search terms (for Blanca - Event Management)
    events_search_terms = [
        # Event Management
        "Event Manager",
        "Event Coordinator",
        "Event Executive",
        "Event Planner",
        "Events Manager",
        "Events Coordinator",
        "Junior Event Manager",
        "Event Assistant",
        # Conference & Meetings
        "Conference Manager",
        "Conference Coordinator",
        "Meeting Planner",
        "Meeting Coordinator",
        "Corporate Events",
        "Corporate Event Manager",
        # Hospitality
        "Hospitality Manager",
        "Hospitality Coordinator",
        "Venue Manager",
        "Venue Coordinator",
        "Banquet Manager",
        "Catering Manager",
        # Weddings & Social
        "Wedding Planner",
        "Wedding Coordinator",
        "Social Events Manager",
        # Tourism
        "Tourism Manager",
        "Business Tourism",
        "MICE Coordinator",
        # Entry level
        "Event Intern",
        "Events Assistant",
        "Hospitality Assistant"
    ]

    search_terms = software_search_terms + hr_search_terms + cybersecurity_search_terms + sales_search_terms + finance_search_terms + marketing_search_terms + biotech_search_terms + engineering_search_terms + events_search_terms

    # Initialize shared data structures (thread-safe)
    all_new_jobs = {}
    software_jobs = {}
    hr_jobs = {}
    cybersecurity_jobs = {}
    sales_jobs = {}
    finance_jobs = {}
    marketing_jobs = {}
    biotech_jobs = {}
    engineering_jobs = {}
    events_jobs = {}
    successful_searches = 0
    lock = threading.Lock()  # For thread-safe dictionary updates

    print(f"\n[LOCATION] Searching in {location}")
    print(f"[PARALLEL] Using {MAX_CONCURRENT_SEARCHES} concurrent workers")
    print(f"[TERMS] Processing {len(search_terms)} search terms...")

    # Prepare search tasks
    search_tasks = []
    for idx, term in enumerate(search_terms):
        is_software = term in software_search_terms
        is_cybersecurity = term in cybersecurity_search_terms
        is_sales = term in sales_search_terms
        is_finance = term in finance_search_terms
        is_marketing = term in marketing_search_terms
        is_biotech = term in biotech_search_terms
        is_engineering = term in engineering_search_terms
        is_events = term in events_search_terms

        search_tasks.append({
            'term': term,
            'location': location,
            'country_name': country_name,
            'existing_jobs': existing_jobs,
            'is_software': is_software,
            'is_cybersecurity': is_cybersecurity,
            'is_sales': is_sales,
            'is_finance': is_finance,
            'is_marketing': is_marketing,
            'is_biotech': is_biotech,
            'is_engineering': is_engineering,
            'is_events': is_events,
            'thread_id': idx + 1
        })

    # Execute searches in parallel with ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SEARCHES) as executor:
        # Submit all tasks
        future_to_task = {
            executor.submit(
                search_single_term,
                task['term'],
                task['location'],
                task['country_name'],
                task['existing_jobs'],
                task['is_software'],
                task['is_cybersecurity'],
                task['is_sales'],
                task['is_finance'],
                task['is_marketing'],
                task['is_biotech'],
                task['is_engineering'],
                task['is_events'],
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
                                # Determine job_type based on search category
                                job_title = job_data.get('title', '')
                                job_type = None
                                job_dict = None

                                if result['is_software']:
                                    job_type = 'software'
                                    job_dict = software_jobs
                                elif result['is_cybersecurity']:
                                    job_type = 'cybersecurity'
                                    job_dict = cybersecurity_jobs
                                elif result['is_sales']:
                                    job_type = 'sales'
                                    job_dict = sales_jobs
                                elif result['is_finance']:
                                    job_type = 'finance'
                                    job_dict = finance_jobs
                                elif result['is_marketing']:
                                    job_type = 'marketing'
                                    job_dict = marketing_jobs
                                elif result.get('is_biotech'):
                                    job_type = 'biotech'
                                    job_dict = biotech_jobs
                                elif result.get('is_engineering'):
                                    job_type = 'engineering'
                                    job_dict = engineering_jobs
                                elif result.get('is_events'):
                                    job_type = 'events'
                                    job_dict = events_jobs
                                else:
                                    job_type = 'hr'
                                    job_dict = hr_jobs

                                # Validate job title matches job type (filter irrelevant LinkedIn results)
                                if not is_relevant_job(job_title, job_type):
                                    # Skip jobs that don't match the job type keywords
                                    continue

                                # Set job_type and add to appropriate dictionary
                                job_data['job_type'] = job_type
                                job_dict[job_id] = job_data
                                all_new_jobs[job_id] = job_data
                            else:
                                # Update easy_apply flag if set
                                if job_data.get('easy_apply'):
                                    all_new_jobs[job_id]['easy_apply'] = True

            except Exception as e:
                print(f"   [ERROR] Task failed for {task['term']}: {e}")

            # Progress indicator
            if completed % 10 == 0:
                print(f"   [PROGRESS] {completed}/{len(search_terms)} searches completed...")

            # Small delay between batches to avoid overwhelming LinkedIn
            if completed % MAX_CONCURRENT_SEARCHES == 0:
                time.sleep(BATCH_DELAY_SECONDS)

    print(f"   [COMPLETE] All {len(search_terms)} searches finished!")

    print(f"\n[SUMMARY] {country_name}:")
    print(f"   • Searches: {successful_searches}/{len(search_terms)}")
    print(f"   • New jobs found: {len(all_new_jobs)} (Software: {len(software_jobs)}, HR: {len(hr_jobs)}, Cybersecurity: {len(cybersecurity_jobs)}, Sales: {len(sales_jobs)}, Finance: {len(finance_jobs)}, Marketing: {len(marketing_jobs)}, Biotech: {len(biotech_jobs)}, Engineering: {len(engineering_jobs)}, Events: {len(events_jobs)})")

    # Upload to Railway and get actual new job counts
    actual_new_software = 0
    actual_new_hr = 0
    actual_new_cybersecurity = 0
    actual_new_sales = 0
    actual_new_finance = 0
    actual_new_marketing = 0
    actual_new_biotech = 0
    actual_new_engineering = 0
    actual_new_events = 0
    actual_new_total = 0

    if all_new_jobs:
        print(f"\n[UPLOAD] Uploading {len(all_new_jobs)} jobs to Railway...")
        upload_result = upload_jobs_to_railway(railway_url, all_new_jobs)

        if upload_result['success']:
            actual_new_total = upload_result['new_jobs']
            actual_new_software = upload_result['new_software']
            actual_new_hr = upload_result['new_hr']
            actual_new_cybersecurity = upload_result['new_cybersecurity']
            actual_new_sales = upload_result.get('new_sales', 0)
            actual_new_finance = upload_result.get('new_finance', 0)
            actual_new_marketing = upload_result.get('new_marketing', 0)
            actual_new_biotech = upload_result.get('new_biotech', 0)
            actual_new_engineering = upload_result.get('new_engineering', 0)
            actual_new_events = upload_result.get('new_events', 0)
            print(f"   ✅ Upload successful!")
            print(f"   📊 Actually added to DB: {actual_new_total} new ({actual_new_software} software, {actual_new_hr} HR, {actual_new_cybersecurity} cybersecurity, {actual_new_sales} sales, {actual_new_finance} finance, {actual_new_marketing} marketing, {actual_new_biotech} biotech, {actual_new_engineering} engineering, {actual_new_events} events)")
        else:
            print(f"   ❌ Upload failed!")
            return False
    else:
        print(f"\n[SKIP] No new jobs to upload")

    # Output for GitHub Actions summary
    print(f"\n::notice title={country_name} Complete::{actual_new_total} new jobs added ({actual_new_software} software, {actual_new_hr} HR, {actual_new_cybersecurity} cybersecurity, {actual_new_sales} sales, {actual_new_finance} finance, {actual_new_marketing} marketing, {actual_new_biotech} biotech, {actual_new_engineering} engineering, {actual_new_events} events)")

    # Set output for GitHub Actions - use ACTUAL new counts, not scraped counts
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.getenv('GITHUB_OUTPUT'), 'a') as f:
            f.write(f"jobs_found={actual_new_total}\n")
            f.write(f"software_jobs={actual_new_software}\n")
            f.write(f"hr_jobs={actual_new_hr}\n")
            f.write(f"cybersecurity_jobs={actual_new_cybersecurity}\n")
            f.write(f"sales_jobs={actual_new_sales}\n")
            f.write(f"finance_jobs={actual_new_finance}\n")
            f.write(f"marketing_jobs={actual_new_marketing}\n")
            f.write(f"biotech_jobs={actual_new_biotech}\n")
            f.write(f"engineering_jobs={actual_new_engineering}\n")
            f.write(f"events_jobs={actual_new_events}\n")
            f.write(f"country={country_name}\n")

    print(f"\n✅ {country_name} scraping complete!")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape jobs for a single country')
    parser.add_argument('--location', required=True, help='Location string (e.g., "Dublin, County Dublin, Ireland")')
    parser.add_argument('--country', required=True, help='Country name (e.g., "Ireland")')
    parser.add_argument('--railway-url', help='Railway URL (default from env)')

    args = parser.parse_args()

    railway_url = args.railway_url or os.environ.get('RAILWAY_URL')

    if not railway_url:
        print("❌ Error: RAILWAY_URL not provided")
        sys.exit(1)

    success = scrape_single_country(args.location, args.country, railway_url)
    sys.exit(0 if success else 1)
