import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from datetime import datetime, timedelta
import time
import json
import re
import os
import hashlib


class LinkedInJobScraper:
    def __init__(self, headless=True, storage_file="jobs_database.json"):
        self.headless = headless
        self.driver = None
        self.jobs_data = []
        self.storage_file = storage_file
        self.existing_jobs = self.load_existing_jobs()
        
    def generate_job_id(self, title, company, location):
        """Generate a unique ID for a job based on title, company, and location"""
        job_string = f"{title}|{company}|{location}".lower()
        return hashlib.md5(job_string.encode()).hexdigest()[:12]
        
    def load_existing_jobs(self):
        """Load existing jobs from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading existing jobs: {e}")
                return {}
        return {}
        
    def save_jobs_database(self):
        """Save all jobs to persistent storage"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.existing_jobs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving jobs database: {e}")
    
    def setup_driver(self):
        # Try Chrome first, then Firefox
        try:
            chrome_options = ChromeOptions()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Try to use chromedriver from PATH first
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                print("Using Chrome browser with system chromedriver")
            except:
                # Fall back to webdriver-manager
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("Using Chrome browser with downloaded chromedriver")
                
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as chrome_error:
            print(f"Chrome not available: {chrome_error}")
            print("Trying Firefox...")
            
            try:
                firefox_options = FirefoxOptions()
                if self.headless:
                    firefox_options.add_argument("--headless")
                firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                
                try:
                    self.driver = webdriver.Firefox(options=firefox_options)
                    print("Using Firefox browser with system geckodriver")
                except:
                    service = FirefoxService(GeckoDriverManager().install())
                    self.driver = webdriver.Firefox(service=service, options=firefox_options)
                    print("Using Firefox browser with downloaded geckodriver")
                
            except Exception as firefox_error:
                print(f"Firefox not available: {firefox_error}")
                raise Exception("Neither Chrome nor Firefox browser is available. Please install one of them.")
        
    def search_jobs(self, keywords, location="", date_filter="7d"):
        if not self.driver:
            self.setup_driver()
            
        # LinkedIn job search URL with filters
        base_url = "https://www.linkedin.com/jobs/search"
        params = {
            "keywords": keywords,
            "location": location,
            "f_TPR": "r86400",  # 24 hours (86400 seconds)
            "position": "1",
            "pageNum": "0"
        }
        
        # Construct URL
        url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items() if v])
        
        print(f"Searching jobs: {url}")
        self.driver.get(url)
        time.sleep(3)
        
        # Wait for job listings to load
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".job-search-card"))
            )
        except:
            print("No job listings found or page didn't load properly")
            return []
        
        # Additional wait for dynamic content to load
        time.sleep(3)
        
        # Try to dismiss any popups or overlays
        try:
            # Common LinkedIn popup dismissal
            dismiss_buttons = self.driver.find_elements(By.CSS_SELECTOR, '[aria-label="Dismiss"], .artdeco-modal__dismiss')
            for button in dismiss_buttons:
                try:
                    if button.is_displayed():
                        button.click()
                        time.sleep(1)
                except:
                    pass
        except:
            pass
            
        return self.scrape_job_listings()
    
    def scrape_job_listings(self):
        jobs = []
        
        # Scroll to load more jobs
        self.scroll_to_load_jobs()
        
        # Find all job cards - try multiple selectors
        job_cards = []
        selectors = [".job-search-card", ".base-card", ".job-result-card", "[data-entity-urn*='job']"]
        
        for selector in selectors:
            cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if cards:
                job_cards = cards
                break
        
        print(f"Found {len(job_cards)} job listings")
        
        # Process all cards quickly without excessive scrolling
        extracted_count = 0
        
        for card in job_cards:
            try:
                job_data = self.extract_job_data(card)
                if job_data:
                    # Check if this job already exists and preserve applied status
                    if job_data['id'] in self.existing_jobs:
                        job_data['applied'] = self.existing_jobs[job_data['id']].get('applied', False)
                        job_data['is_new'] = False
                    else:
                        job_data['is_new'] = True
                    
                    jobs.append(job_data)
                    extracted_count += 1
                    
                    # Update existing jobs database
                    self.existing_jobs[job_data['id']] = job_data
                    
            except Exception as e:
                print(f"Error extracting job data: {e}")
                continue
        
        print(f"Successfully extracted {extracted_count} jobs out of {len(job_cards)} found")
        
        self.jobs_data = jobs
        # Save updated database
        self.save_jobs_database()
        return jobs
    
    def is_software_related_job(self, title):
        """Check if a job title is software/tech related"""
        if not title:
            return False
            
        title_lower = title.lower()
        
        # Software-related keywords (must contain at least one)
        software_keywords = [
            'software', 'developer', 'engineer', 'programming', 'python', 'java', 
            'javascript', 'react', 'angular', 'vue', 'node', 'backend', 'frontend',
            'full stack', 'fullstack', 'devops', 'cloud', 'aws', 'azure', 'gcp',
            'data engineer', 'machine learning', 'ai', 'artificial intelligence',
            'mobile developer', 'ios developer', 'android developer', 'flutter',
            'technical lead', 'tech lead', 'architect', 'principal engineer',
            'senior engineer', 'junior engineer', 'intern developer', 'graduate developer',
            'web developer', 'game developer', 'security engineer', 'qa engineer',
            'test engineer', 'automation', 'ci/cd', 'database', 'sql', 'nosql'
        ]
        
        # Exclude non-software roles (if title contains these, likely not software)
        exclude_keywords = [
            'account manager', 'sales', 'marketing', 'business development', 'hr',
            'human resources', 'finance', 'accounting', 'legal', 'administrative',
            'customer service', 'support specialist', 'office manager', 'receptionist',
            'warehouse', 'logistics', 'construction', 'project manager', 'operations',
            'business analyst', 'consultant', 'advisor', 'coordinator', 'assistant',
            'clerk', 'executive assistant', 'admin', 'payroll', 'procurement',
            'facilities', 'maintenance', 'security guard', 'driver', 'delivery'
        ]
        
        # Check for exclusions first
        for exclude in exclude_keywords:
            if exclude in title_lower:
                return False
        
        # Check for software keywords
        for keyword in software_keywords:
            if keyword in title_lower:
                return True
                
        return False

    def extract_job_data(self, card):
        try:
            # Try multiple selectors for job title
            title = ""
            title_selectors = [
                ".base-search-card__title a span[aria-hidden='true']",
                ".base-search-card__title a",
                ".base-search-card__title",
                ".job-search-card__title a span", 
                ".job-search-card__title", 
                "h3 a span[aria-hidden='true']",
                "h3 a span",
                "h3 a",
                "a span[aria-hidden='true']",
                ".sr-only"
            ]
            
            for selector in title_selectors:
                try:
                    title_element = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip()
                    if title and title != "N/A" and len(title) > 3:
                        break
                except:
                    continue
            
            # Try multiple selectors for company
            company = ""
            company_selectors = [
                ".base-search-card__subtitle a span[aria-hidden='true']",
                ".base-search-card__subtitle a",
                ".base-search-card__subtitle",
                ".job-search-card__subtitle-link span",
                ".job-search-card__subtitle-link",
                ".job-search-card__subtitle",
                "h4 a span[aria-hidden='true']",
                "h4 a span",
                "h4 a",
                ".hidden-nested-link"
            ]
            
            for selector in company_selectors:
                try:
                    company_element = card.find_element(By.CSS_SELECTOR, selector)
                    company = company_element.text.strip()
                    if company and company != "N/A" and len(company) > 1:
                        break
                except:
                    continue
            
            # Try multiple selectors for location
            location = ""
            location_selectors = [
                ".job-search-card__location",
                ".job-search-card__location span",
                ".job-result-card__location"
            ]
            
            for selector in location_selectors:
                try:
                    location_element = card.find_element(By.CSS_SELECTOR, selector)
                    location = location_element.text.strip()
                    if location and location != "N/A":
                        break
                except:
                    continue
            
            # Try multiple selectors for job URL
            job_url = ""
            link_selectors = [
                ".base-card__full-link",
                ".job-search-card__title-link",
                "h3 a",
                "a[data-tracking-control-name*='job']"
            ]
            
            for selector in link_selectors:
                try:
                    link_element = card.find_element(By.CSS_SELECTOR, selector)
                    job_url = link_element.get_attribute("href")
                    if job_url:
                        break
                except:
                    continue
            
            # Try multiple selectors for posted date
            posted_date = ""
            date_selectors = [
                ".job-search-card__listdate",
                ".job-search-card__listdate--new",
                ".job-result-card__listdate",
                "time"
            ]
            
            for selector in date_selectors:
                try:
                    posted_element = card.find_element(By.CSS_SELECTOR, selector)
                    posted_date = posted_element.text.strip()
                    if posted_date:
                        break
                except:
                    continue
            
            # If we have a URL but no title, try to extract title from URL
            if not title and job_url:
                try:
                    # Extract job title from LinkedIn URL patterns
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(job_url)
                    path_parts = parsed_url.path.split('/')
                    
                    # Try to extract from 'at-company' pattern first (most reliable)
                    for part in path_parts:
                        if '-at-' in part and len(part) > 10:  # Reasonable length filter
                            title_part, company_part = part.split('-at-', 1)
                            title = title_part.replace('-', ' ').title()
                            if not company:
                                company = company_part.replace('-', ' ').title()
                            break
                    
                    # Fallback: look for common job title patterns
                    if not title:
                        job_patterns = [
                            'software-engineer', 'python-developer', 'data-engineer', 'full-stack',
                            'frontend-developer', 'backend-developer', 'devops-engineer',
                            'senior-software', 'junior-software', 'lead-developer',
                            'engineering-manager', 'technical-lead', 'architect'
                        ]
                        
                        for part in path_parts:
                            for pattern in job_patterns:
                                if pattern in part.lower():
                                    title = part.replace('-', ' ').title()
                                    break
                            if title:
                                break
                except:
                    pass
            
            # Skip if we couldn't extract essential data
            if not title or not job_url:
                print(f"Skipping job card - missing essential data. Title: '{title}', URL: '{job_url}'")
                return None
                
            # Filter out non-software related jobs
            if not self.is_software_related_job(title):
                print(f"Skipping non-software job: '{title}'")
                return None
            
            # Generate unique job ID
            job_id = self.generate_job_id(title, company, location)
            
            return {
                "id": job_id,
                "title": title,
                "company": company or "Unknown Company",
                "location": location or "Unknown Location", 
                "posted_date": posted_date or "Unknown",
                "job_url": job_url,
                "scraped_at": datetime.now().isoformat(),
                "applied": False,
                "is_new": job_id not in self.existing_jobs
            }
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None
    
    def scroll_to_load_jobs(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scrolls = 5
        
        while scroll_attempts < max_scrolls:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
                
            last_height = new_height
            scroll_attempts += 1
    
    def is_within_24_hours(self, posted_date_str):
        if not posted_date_str or posted_date_str == "N/A":
            return True  # Include if we can't determine the date
            
        posted_date_str = posted_date_str.lower()
        
        # Handle different date formats
        if "minute" in posted_date_str or "hour" in posted_date_str:
            return True
        elif "day" in posted_date_str:
            # Extract number of days
            days_match = re.search(r'(\d+)\s*day', posted_date_str)
            if days_match:
                days = int(days_match.group(1))
                return days <= 1
        
        return True  # Default to include if format is unclear
    
    def mark_job_as_applied(self, job_id):
        """Mark a job as applied"""
        if job_id in self.existing_jobs:
            self.existing_jobs[job_id]['applied'] = True
            self.save_jobs_database()
            return True
        return False
    
    def get_job_stats(self):
        """Get statistics about new vs existing jobs"""
        total_jobs = len(self.jobs_data)
        new_jobs = len([job for job in self.jobs_data if job.get('is_new', False)])
        existing_jobs = total_jobs - new_jobs
        applied_jobs = len([job for job in self.jobs_data if job.get('applied', False)])
        
        return {
            'total': total_jobs,
            'new': new_jobs,
            'existing': existing_jobs,
            'applied': applied_jobs,
            'not_applied': total_jobs - applied_jobs
        }
    
    def save_jobs_to_file(self, filename="linkedin_jobs.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.jobs_data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.jobs_data)} jobs to {filename}")
    
    def print_jobs_summary(self):
        if not self.jobs_data:
            print("No jobs found")
            return
            
        stats = self.get_job_stats()
        
        print(f"\n=== Job Search Results ===")
        print(f"📊 Total: {stats['total']} | 🆕 New: {stats['new']} | 🔄 Existing: {stats['existing']}")
        print(f"✅ Applied: {stats['applied']} | ⏳ Not Applied: {stats['not_applied']}")
        print("=" * 60)
        
        for i, job in enumerate(self.jobs_data, 1):
            status_icons = []
            if job.get('is_new', False):
                status_icons.append("🆕")
            if job.get('applied', False):
                status_icons.append("✅")
            else:
                status_icons.append("⏳")
                
            status_str = " ".join(status_icons)
            
            print(f"\n{i}. [{job['id']}] {job['title']} {status_str}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Posted: {job['posted_date']}")
            print(f"   URL: {job['job_url']}")
            print("-" * 60)
    
    def close(self):
        if self.driver:
            self.driver.quit()