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
        
        # Company exclusion list
        self.excluded_companies = [
            'BENDING SPOONS',
            'Bending Spoons'
        ]

        # Top tech companies by country (for filtering)
        self.top_tech_companies = {
            'Netherlands': [
                'Booking.com', 'Booking', 'Adyen', 'Elastic', 'TomTom', 'Mollie',
                'WeTransfer', 'Picnic', 'Backbase', 'Exact', 'Coolblue',
                'Uber', 'Netflix', 'Spotify', 'Databricks', 'Atlassian',
                'Salesforce', 'Google', 'Meta', 'Amazon', 'Microsoft'
            ],
            'Germany': [
                'SAP', 'Zalando', 'Delivery Hero', 'N26', 'SoundCloud',
                'HelloFresh', 'Auto1', 'FlixBus', 'Celonis', 'Personio',
                'Contentful', 'Adjust', 'GetYourGuide', 'Babbel', 'Trade Republic',
                'Google', 'Amazon', 'Microsoft', 'Apple', 'Meta',
                'Stripe', 'Spotify', 'Tesla', 'Siemens', 'BMW'
            ],
            'Sweden': [
                'Spotify', 'Klarna', 'King', 'Ericsson', 'Mojang',
                'iZettle', 'Truecaller', 'Tink', 'Northvolt', 'Paradox Interactive',
                'Epidemic Sound', 'Einride', 'Polestar', 'Volvo Cars', 'Volvo',
                'Google', 'Amazon', 'Microsoft', 'Apple', 'Meta', 'Unity'
            ],
            # Existing countries - no filtering
            'Ireland': [],
            'Spain': [],
            'Panama': [],
            'Chile': [],
            'Switzerland': []
        }
        
    def generate_job_id(self, title, company, location=None):
        """
        Generate a unique ID for a job based on title and company only.
        This groups the same job posted in multiple locations together.
        Location is kept as parameter for backward compatibility but not used.
        """
        # Normalize title and company for consistent ID generation
        normalized_title = title.strip().lower()
        normalized_company = company.strip().lower()

        job_string = f"{normalized_title}|{normalized_company}"
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

            # Railway-optimized Chrome options
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Railway environment detection
            if os.environ.get("RAILWAY_ENVIRONMENT") == "production":
                chrome_options.add_argument("--single-process")
                chrome_options.add_argument("--disable-web-security")
                chrome_options.add_argument("--ignore-certificate-errors")
                chrome_options.binary_location = "/usr/bin/google-chrome-stable"
                print("🐳 Railway environment detected - using optimized Chrome settings")

            chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
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
        
    def search_jobs(self, keywords, location="", date_filter="24h", easy_apply_filter=False):
        if not self.driver:
            self.setup_driver()

        # LinkedIn job search URL with filters
        base_url = "https://www.linkedin.com/jobs/search"

        # Map date filters to LinkedIn time parameters
        time_filters = {
            "24h": "r86400",    # 24 hours (86400 seconds)
            "1d": "r86400",     # 1 day
            "7d": "r604800",    # 7 days (604800 seconds)
            "1w": "r604800",    # 1 week
            "30d": "r2592000",  # 30 days (2592000 seconds)
            "1m": "r2592000"    # 1 month
        }

        f_tpr_value = time_filters.get(date_filter, "r86400")  # Default to 24h

        params = {
            "keywords": keywords,
            "location": location,
            "f_TPR": f_tpr_value,
            "position": "1",
            "pageNum": "0"
        }

        # Add Easy Apply filter if requested
        if easy_apply_filter:
            params["f_AL"] = "true"

        # Construct URL
        url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items() if v])

        filter_label = " [Easy Apply]" if easy_apply_filter else ""
        print(f"Searching jobs{filter_label}: {url}")
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

        return self.scrape_job_listings(easy_apply_filter=easy_apply_filter)
    
    def scrape_job_listings(self, easy_apply_filter=False):
        jobs_dict = {}

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

        filter_label = " (Easy Apply filter)" if easy_apply_filter else ""
        print(f"Found {len(job_cards)} job listings{filter_label}")

        # Process all cards quickly without excessive scrolling
        extracted_count = 0

        for card in job_cards:
            try:
                job_data = self.extract_job_data(card, easy_apply_from_filter=easy_apply_filter)
                if job_data:
                    # Check if this job already exists
                    if job_data['id'] in self.existing_jobs:
                        existing_job = self.existing_jobs[job_data['id']]

                        # Skip jobs that have been rejected to avoid repetitive results
                        if existing_job.get('rejected', False):
                            print(f"Skipping rejected job: '{job_data['title']}' at {job_data['company']}")
                            continue

                        # Preserve applied status and other fields
                        job_data['applied'] = existing_job.get('applied', False)
                        job_data['rejected'] = existing_job.get('rejected', False)
                        job_data['is_new'] = False
                        # Update easy_apply status if this search used the Easy Apply filter
                        if easy_apply_filter:
                            job_data['easy_apply'] = True
                    else:
                        job_data['is_new'] = True
                        job_data['rejected'] = False

                    jobs_dict[job_data['id']] = job_data
                    extracted_count += 1

                    # Update existing jobs database
                    self.existing_jobs[job_data['id']] = job_data

            except Exception as e:
                print(f"Error extracting job data: {e}")
                continue

        print(f"Successfully extracted {extracted_count} jobs out of {len(job_cards)} found")

        self.jobs_data = list(jobs_dict.values())
        # Save updated database
        self.save_jobs_database()
        return jobs_dict
    
    def detect_job_language(self, title, location=""):
        """
        Detect if a job title is in an acceptable language for the location.
        - English-speaking countries: Only English
        - Spanish-speaking countries: English or Spanish
        - Other countries: Only English
        """
        if not title:
            return False

        title_lower = title.lower()

        # Determine if location is in a Spanish-speaking country
        location_lower = location.lower() if location else ""
        spanish_speaking_countries = ['spain', 'españa', 'panama', 'chile', 'santiago', 'madrid', 'barcelona']
        is_spanish_location = any(country in location_lower for country in spanish_speaking_countries)

        # Spanish-specific indicators (only check if NOT in Spanish-speaking country)
        # These are job-related words that are clearly Spanish
        spanish_indicators = [
            'desarrollador', 'programador', 'ingeniero', 'ingeniería',
            'científico', 'analista', 'arquitecto', 'datos'
        ]

        # Common words that appear in non-English job titles
        # NOTE: Avoid common English/Spanish words like "senior", "de", "e", etc.
        # These indicators should be UNIQUE to non-English/Spanish languages

        # German-specific indicators
        german_indicators = [
            'und', 'für', 'mit', 'oder', 'als', 'bei', 'von', 'zu', 'im', 'am',
            'entwickler', 'ingenieur', 'softwareentwickler'
        ]

        # French-specific indicators
        french_indicators = [
            'et', 'ou', 'avec', 'dans', 'sur', 'le', 'la', 'les', 'des',
            'développeur', 'ingénieur', 'chef', 'responsable'
        ]

        # Italian-specific indicators
        italian_indicators = [
            'per', 'con', 'il', 'lo', 'gli', 'le', 'del', 'della',
            'sviluppatore', 'ingegnere', 'responsabile'
        ]

        # Portuguese-specific indicators
        portuguese_indicators = [
            'ou', 'com', 'do', 'da', 'dos', 'das',
            'desenvolvedor', 'engenheiro'
        ]

        # Build list of non-acceptable language indicators
        non_acceptable_indicators = german_indicators + french_indicators + italian_indicators + portuguese_indicators

        # If NOT in Spanish-speaking country, also reject Spanish
        if not is_spanish_location:
            non_acceptable_indicators.extend(spanish_indicators)

        # Split title into words
        words = title_lower.split()

        # If we find any non-acceptable language indicators, reject
        # Even a single strong indicator (like "desarrollador", "ingeniero") is enough
        # For Spanish in non-Spanish countries: 10% threshold (1 word in 10)
        # For other languages: any indicator triggers rejection
        indicator_count = sum(1 for word in words if word in non_acceptable_indicators)

        if indicator_count > 0:
            percentage = indicator_count / len(words) if len(words) > 0 else 0
            # Very low threshold (10%) since our indicators are very specific
            if percentage > 0.1:
                return False

        return True

    def is_software_related_job(self, title, location=""):
        """Check if a job title is relevant (software OR HR/recruitment OR cybersecurity)"""
        if not title:
            return False

        title_lower = title.lower()

        # First check language - filter out non-English/Spanish jobs (location-aware)
        if not self.detect_job_language(title, location):
            print(f"Skipping non-English/Spanish job: '{title}' in {location if location else 'unknown location'}")
            return False

        # Cybersecurity keywords (English and Spanish)
        cybersecurity_keywords = [
            'soc analyst', 'cybersecurity', 'cyber security', 'security analyst',
            'information security', 'infosec', 'security operations', 'siem',
            'threat detection', 'incident response', 'security engineer',
            'penetration test', 'ethical hacker', 'security architect',
            'vulnerability', 'compliance', 'risk analyst',
            # Spanish
            'analista soc', 'analista de ciberseguridad', 'seguridad de la información',
            'operaciones de seguridad', 'respuesta a incidentes', 'ingeniero de seguridad'
        ]

        # Software-related keywords
        software_keywords = [
            # Core programming roles
            'software', 'developer', 'engineer', 'programming', 'programmer',
            'development', 'coding', 'technical',

            # Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'html', 'css', 'rust', 'go', 'scala',
            'kotlin', 'swift', 'php', 'ruby', 'perl', 'r programming', 'matlab',

            # Frameworks
            'react', 'angular', 'vue', 'node', 'nodejs', 'express', 'frontend', 'backend',
            'full stack', 'fullstack', 'full-stack', 'django', 'flask', 'spring', 'fastapi',
            'next.js', 'nextjs', 'svelte', 'ember',

            # Cloud platforms
            'cloud', 'aws', 'azure', 'firebase', 'lambda', 'devops', 'gcp', 'google cloud',
            'cloudflare', 'heroku', 'digital ocean', 'kubernetes', 'k8s', 'docker', 'terraform',

            # Data skills (EXPANDED)
            'data', 'analytics', 'machine learning', 'ai', 'artificial intelligence',
            'data science', 'data scientist', 'data engineer', 'data engineering',
            'data analyst', 'data analytics', 'business intelligence', 'bi analyst',
            'tableau', 'power bi', 'looker', 'visualization', 'data visualization',
            'big data', 'hadoop', 'spark', 'kafka', 'airflow', 'etl', 'elt',
            'data pipeline', 'data warehouse', 'data lake', 'snowflake', 'redshift',
            'databricks', 'dbt', 'data modeling', 'ml engineer', 'mlops',
            'deep learning', 'neural network', 'nlp', 'natural language processing',
            'computer vision', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas',
            'numpy', 'jupyter', 'data mining', 'predictive analytics', 'statistical analysis',
            'quantitative analyst', 'research scientist', 'applied scientist',

            # Database
            'database', 'sql', 'nosql', 'mysql', 'postgresql', 'mongodb', 'oracle',
            'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'mariadb',

            # Mobile development
            'mobile', 'react native', 'ios', 'android', 'flutter', 'xamarin',

            # Leadership roles
            'technical lead', 'tech lead', 'lead developer', 'senior', 'principal',
            'architect', 'staff engineer', 'team lead', 'engineering manager',

            # Testing
            'qa', 'quality assurance', 'test', 'testing', 'automation', 'test engineer',
            'sdet', 'qa engineer', 'test automation',

            # Other tech roles
            'web developer', 'api', 'microservices', 'integration', 'platform',
            'system', 'application', 'solution', 'product engineer', 'site reliability',
            'sre', 'reliability engineer', 'build engineer', 'release engineer'
        ]

        # HR/Recruitment keywords (User 2)
        hr_keywords = [
            'hr officer', 'hr coordinator', 'hr generalist', 'hr specialist',
            'talent acquisition', 'recruiter', 'recruitment', 'recruiting',
            'people operations', 'people ops', 'people partner', 'hr business partner',
            'hr assistant', 'hr administrator', 'talent coordinator',
            'recruiting coordinator', 'recruitment consultant', 'talent specialist',
            'human resources', 'employee relations', 'hr manager'
        ]

        # Strict exclusions - jobs that are clearly not relevant
        exclude_keywords = [
            # Sales/Marketing (unless technical)
            'account manager', 'sales rep', 'marketing coordinator', 'business development rep',

            # Administrative (non-HR)
            'finance', 'accounting', 'legal', 'admin assistant',
            'customer service rep', 'receptionist', 'office manager',

            # Manual labor & Construction
            'warehouse', 'logistics coordinator', 'construction', 'driver', 'delivery',
            'maintenance tech', 'cleaner', 'janitor',

            # Non-software engineering roles (EXPANDED)
            'civil engineer', 'structural engineer', 'mechanical engineer', 'electrical engineer',
            'chemical engineer', 'industrial engineer', 'manufacturing engineer',
            'process engineer', 'project engineer', 'field engineer', 'design engineer',
            'hardware engineer', 'electronics engineer', 'automotive engineer',
            'aerospace engineer', 'biomedical engineer', 'environmental engineer',
            'geotechnical engineer', 'hydraulic engineer', 'marine engineer',
            'mining engineer', 'nuclear engineer', 'petroleum engineer',
            'quality engineer', 'safety engineer', 'systems engineer',
            'telecommunications engineer', 'transportation engineer',

            # Infrastructure (construction-related)
            'infrastructure project', 'infrastructure planning', 'infrastructure construction',
            'roads and bridges', 'public works', 'utilities engineer',

            # Physical security (not cybersecurity)
            'security guard', 'security officer',
        ]

        # Check for hard exclusions FIRST (before checking positive keywords)
        # This prevents civil engineers, infrastructure engineers, etc. from passing through
        for exclude in exclude_keywords:
            if exclude in title_lower:
                # Exception: Allow if cybersecurity-related
                if any(cyber in title_lower for cyber in ['security analyst', 'security engineer', 'cybersecurity']):
                    continue
                # Exception: Allow if it's clearly a software/data/tech role despite containing exclusion keyword
                if any(sw in title_lower for sw in [
                    'software', 'developer', 'programming',
                    'data engineer', 'data scientist', 'data analyst', 'analytics engineer',
                    'ml engineer', 'mlops', 'ai engineer', 'machine learning',
                    'cloud infrastructure', 'infrastructure as code', 'devops', 'sre'
                ]):
                    continue
                # Otherwise, reject this job
                return False

        # Special handling for borderline cases (only check after exclusions)
        borderline_positive = [
            'marketing tools', 'finance automation', 'revenue', 'compiler',
            'cloud infrastructure', 'infrastructure engineer', 'infrastructure as code',  # Technical infrastructure only
            'operations', 'integration', 'reliability',
            'workday', 'salesforce', 'data operations'
        ]

        # Check if it contains borderline positive terms
        # But make sure it's not a civil/construction infrastructure role
        for positive in borderline_positive:
            if positive in title_lower:
                # Double-check it's not construction-related
                if any(construction in title_lower for construction in ['civil', 'structural', 'construction', 'roads', 'bridges']):
                    return False
                return True

        # Check for cybersecurity keywords
        for keyword in cybersecurity_keywords:
            if keyword in title_lower:
                return True

        # Check for software keywords
        for keyword in software_keywords:
            if keyword in title_lower:
                return True

        # Check for HR keywords
        for keyword in hr_keywords:
            if keyword in title_lower:
                return True

        return False

    def clean_company_name(self, company):
        """
        Clean company name by removing trailing numbers and extra metadata.
        LinkedIn sometimes appends tracking numbers like "Stripe 4342327281"
        """
        if not company:
            return company

        # Remove leading/trailing whitespace
        company = company.strip()

        # Pattern: Remove trailing space followed by numbers (e.g., " 4342327281")
        # This regex matches a space followed by 4 or more consecutive digits at the end
        import re
        cleaned = re.sub(r'\s+\d{4,}$', '', company)

        return cleaned.strip()

    def is_excluded_company(self, company):
        """Check if a company is in the exclusion list"""
        if not company:
            return False

        company_lower = company.lower().strip()

        for excluded in self.excluded_companies:
            if excluded.lower() in company_lower:
                return True

        return False

    def is_top_tech_company(self, company, country):
        """Check if a company is in the top tech companies list for the given country

        Args:
            company: Company name to check
            country: Country name (e.g., 'Netherlands', 'Germany', 'Sweden')

        Returns:
            True if company is in top tech list for country, or if country has no restrictions
        """
        if not company or not country:
            return True  # Default to including if info missing

        # If country has no restriction list, include all companies
        if country not in self.top_tech_companies or not self.top_tech_companies[country]:
            return True

        company_lower = company.lower().strip()

        # Check if company matches any in the top tech list
        for top_company in self.top_tech_companies[country]:
            top_company_lower = top_company.lower()

            # Flexible matching: check if either name contains the other
            if top_company_lower in company_lower or company_lower in top_company_lower:
                return True

        return False

    def get_country_from_location(self, location):
        """Extract country name from location string"""
        location_lower = location.lower()
        if "ireland" in location_lower or "dublin" in location_lower:
            return "Ireland"
        elif "spain" in location_lower or "barcelona" in location_lower or "madrid" in location_lower:
            return "Spain"
        elif "panama" in location_lower:
            return "Panama"
        elif "chile" in location_lower or "santiago" in location_lower:
            return "Chile"
        elif "switzerland" in location_lower:
            return "Switzerland"
        elif "netherlands" in location_lower or "amsterdam" in location_lower:
            return "Netherlands"
        elif "germany" in location_lower or "berlin" in location_lower or "munich" in location_lower:
            return "Germany"
        elif "sweden" in location_lower or "stockholm" in location_lower:
            return "Sweden"
        elif "belgium" in location_lower or "brussels" in location_lower:
            return "Belgium"
        elif "denmark" in location_lower or "copenhagen" in location_lower:
            return "Denmark"
        elif "france" in location_lower:
            return "France"
        elif "italy" in location_lower:
            return "Italy"
        elif "remote" in location_lower or "anywhere" in location_lower:
            return "Remote"
        else:
            return "Unknown"

    def detect_job_type(self, title, description=""):
        """Detect job type from title and description"""
        text = f"{title} {description}".lower()

        # Cybersecurity keywords (check first - most specific)
        cybersecurity_keywords = [
            'soc analyst', 'cybersecurity', 'cyber security', 'security analyst',
            'information security', 'infosec', 'security operations', 'siem',
            'threat detection', 'incident response', 'security engineer',
            'penetration test', 'ethical hacker', 'security architect',
            'analista soc', 'analista de ciberseguridad', 'seguridad de la información',
            'operaciones de seguridad', 'respuesta a incidentes'
        ]

        # Sales/Business Development keywords (English and Spanish)
        sales_keywords = [
            # English
            'account manager', 'account executive', 'bdr', 'sdr',
            'business development representative', 'sales development representative',
            'sales representative', 'inside sales', 'outbound sales',
            'saas sales', 'b2b sales', 'customer success manager',
            'account management', 'business development manager',
            # Spanish
            'ejecutivo de ventas', 'gerente de cuenta', 'representante de ventas',
            'desarrollo de negocios', 'ventas', 'ejecutivo comercial'
        ]

        # Finance/Accounting keywords (English and Spanish)
        finance_keywords = [
            # English
            'fp&a analyst', 'fp&a', 'financial planning and analysis',
            'financial planning analyst', 'financial analyst', 'junior financial analyst',
            'fund accounting', 'fund accountant', 'fund accounting associate',
            'fund administrator', 'investment accounting', 'portfolio accounting',
            'fund operations', 'fund operations analyst', 'fund operations associate',
            'investment operations', 'asset management operations',
            'credit analyst', 'credit risk analyst', 'junior credit analyst',
            'financial reporting', 'management accountant', 'accountant',
            'junior accountant', 'accounting analyst', 'finance associate',
            'finance analyst', 'treasury analyst', 'cash management',
            'corporate finance', 'finance business partner', 'financial reporting analyst',
            'financial modeling', 'variance analysis', 'budgeting analyst', 'forecasting analyst',
            # Spanish
            'analista financiero', 'contador', 'contabilidad', 'finanzas',
            'analista de crédito', 'tesorería', 'contable', 'analista contable'
        ]

        # HR/Recruitment keywords (English and Spanish)
        hr_keywords = [
            # English
            'hr officer', 'hr coordinator', 'hr generalist', 'hr specialist',
            'talent acquisition', 'recruiter', 'recruitment', 'recruiting',
            'people operations', 'people ops', 'people partner',
            'hr assistant', 'human resources',
            # Spanish
            'recursos humanos', 'reclutador', 'reclutamiento', 'selección',
            'talento humano', 'analista de recursos humanos', 'coordinador de rrhh'
        ]

        # Software keywords (English and Spanish) - EXPANDED
        software_keywords = [
            # English - Core programming roles
            'software', 'developer', 'engineer', 'programming', 'programmer',
            'frontend', 'backend', 'full stack', 'devops', 'react', 'python',
            'javascript', 'node', 'java', 'web developer', 'mobile developer',

            # Data science & engineering roles (EXPANDED)
            'data scientist', 'data engineer', 'data engineering', 'data analyst',
            'data analytics', 'machine learning', 'ml engineer', 'mlops',
            'business intelligence', 'bi analyst', 'data science', 'big data',
            'data pipeline', 'data warehouse', 'data lake', 'etl', 'elt',
            'analytics engineer', 'analytics', 'quantitative analyst', 'research scientist',
            'applied scientist', 'ai engineer', 'deep learning', 'nlp engineer',
            'computer vision', 'data modeling', 'statistical analyst',

            # Spanish
            'desarrollador', 'programador', 'ingeniero de software', 'ingeniero software',
            'desarrollador web', 'desarrollador fullstack', 'desarrollador full stack',
            'desarrollador frontend', 'desarrollador backend', 'arquitecto de software',
            'arquitecto software', 'ingeniero', 'dev ', ' dev', 'qa automation',
            'qa automatizador', 'desarrollador mobile', 'desarrollador móvil',
            'científico de datos', 'ingeniero de datos', 'analista de datos'
        ]

        # Check for cybersecurity first (most specific)
        for keyword in cybersecurity_keywords:
            if keyword in text:
                return 'cybersecurity'

        # Check for sales (before HR and software to avoid false positives)
        for keyword in sales_keywords:
            if keyword in text:
                return 'sales'

        # Check for finance (before HR to avoid false positives with "financial" in other contexts)
        for keyword in finance_keywords:
            if keyword in text:
                return 'finance'

        # Check for HR (more specific than software)
        for keyword in hr_keywords:
            if keyword in text:
                return 'hr'

        # Check for software
        for keyword in software_keywords:
            if keyword in text:
                return 'software'

        # Default
        return 'other'

    def detect_experience_level(self, title):
        """Detect experience level from job title"""
        title_lower = title.lower()

        # Senior level indicators
        senior_keywords = ['senior', 'sr.', 'lead', 'principal', 'staff', 'director', 'head of', 'chief', 'vp', 'vice president']
        if any(keyword in title_lower for keyword in senior_keywords):
            return 'senior'

        # Junior level indicators
        junior_keywords = ['junior', 'jr.', 'entry', 'entry-level', 'graduate', 'intern', 'trainee', 'associate']
        if any(keyword in title_lower for keyword in junior_keywords):
            return 'junior'

        # If no specific indicator, assume mid-level
        return 'mid'

    def preserve_applied_status(self, job_id, new_job_data):
        """Preserve the applied and rejected status from existing jobs when updating"""
        if job_id in self.existing_jobs:
            existing_job = self.existing_jobs[job_id]
            # Preserve applied and rejected status and any manual updates
            new_job_data["applied"] = existing_job.get("applied", False)
            new_job_data["rejected"] = existing_job.get("rejected", False)
            # Also preserve any manual notes or custom fields
            if "notes" in existing_job:
                new_job_data["notes"] = existing_job["notes"]
        return new_job_data

    def detect_easy_apply(self, card):
        """Detect if a job has LinkedIn Easy Apply from card view"""
        easy_apply_selectors = [
            ".job-search-card__easy-apply-label",
            "[aria-label*='Easy Apply']",
            ".artdeco-entity-lockup__badge--easy-apply",
            "li-icon[type='easy-apply-logo']",
            ".job-card-list__easy-apply"
        ]

        for selector in easy_apply_selectors:
            try:
                elements = card.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        text = element.text.lower()
                        if 'easy apply' in text or element.get_attribute('type') == 'easy-apply-logo':
                            return True
            except:
                continue

        # Also check for Easy Apply in the card's inner HTML/text
        try:
            card_text = card.text.lower()
            if 'easy apply' in card_text:
                return True
        except:
            pass

        return False

    def verify_easy_apply_on_detail_page(self, job_url, max_wait_seconds=3):
        """
        Verify Easy Apply status by checking the job detail page.
        This is more accurate than card detection or filter trust.

        Returns: (bool, str) - (has_easy_apply, verification_method)
        """
        try:
            # Save current URL to return to it later
            current_url = self.driver.current_url

            # Navigate to job detail page
            self.driver.get(job_url)
            time.sleep(max_wait_seconds)  # Wait for page to load

            # Selectors for Easy Apply button on detail page
            easy_apply_button_selectors = [
                "button[class*='jobs-apply-button']",
                "button[aria-label*='Easy Apply']",
                ".jobs-apply-button--top-card",
                "button:contains('Easy Apply')",
                "[data-control-name='jobdetails_topcard_inapply']"
            ]

            # Check if Easy Apply button exists
            for selector in easy_apply_button_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            button_text = element.text.lower()
                            aria_label = element.get_attribute('aria-label') or ""

                            if 'easy apply' in button_text or 'easy apply' in aria_label.lower():
                                # Confirmed Easy Apply
                                return True, 'detail_page_verified'
                except:
                    continue

            # If no Easy Apply button found, check for regular Apply button (means NOT easy apply)
            regular_apply_selectors = [
                "button:contains('Apply')",
                "a[class*='jobs-apply-button']"
            ]

            for selector in regular_apply_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            button_text = element.text.lower()
                            # If it says "Apply" but NOT "Easy Apply", it's a regular application
                            if 'apply' in button_text and 'easy' not in button_text:
                                return False, 'detail_page_verified'
                except:
                    continue

            # Could not determine - return unverified
            return False, 'detail_page_unverified'

        except Exception as e:
            print(f"⚠️  Warning: Could not verify Easy Apply on detail page: {e}")
            return False, 'detail_page_error'
        finally:
            # Return to original page (optional - may slow down scraping)
            # Commenting out to improve performance
            # try:
            #     if current_url and current_url != job_url:
            #         self.driver.get(current_url)
            # except:
            #     pass
            pass

    def extract_job_data(self, card, easy_apply_from_filter=False):
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
                        # Clean the company name to remove trailing numbers
                        company = self.clean_company_name(company)
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

            # Filter out jobs in non-English/Spanish languages (location-aware)
            if not self.detect_job_language(title, location):
                print(f"Skipping non-English/Spanish job: '{title}' in {location}")
                return None

            # Filter out irrelevant jobs (keep both software and HR jobs)
            job_type = self.detect_job_type(title)
            if job_type == 'other':
                print(f"Skipping irrelevant job: '{title}' (type: {job_type})")
                return None
            
            # Filter out excluded companies
            if self.is_excluded_company(company):
                print(f"Skipping excluded company: '{company}' - Job: '{title}'")
                return None
            
            # Generate unique job ID
            job_id = self.generate_job_id(title, company, location)

            # Detect Easy Apply status with confidence tracking
            # NEW STRATEGY: Determine status and verification method
            easy_apply = False
            easy_apply_status = 'unverified'
            easy_apply_verification_method = None

            if easy_apply_from_filter:
                # Jobs from filter are marked as 'probable' but not confirmed
                # We trust the filter but acknowledge it may have false positives
                easy_apply = True
                easy_apply_status = 'probable'
                easy_apply_verification_method = 'filter_parameter'
            else:
                # Try card detection for jobs not from filter
                card_detected = self.detect_easy_apply(card)
                if card_detected:
                    easy_apply = True
                    easy_apply_status = 'probable'
                    easy_apply_verification_method = 'card_detection'
                else:
                    easy_apply = False
                    easy_apply_status = 'false'
                    easy_apply_verification_method = None

            # Derive country from location
            country = self.get_country_from_location(location or "")

            # Job type already detected above during filtering (line 681)
            # job_type is already set

            # Detect experience level (senior, mid, junior)
            experience_level = self.detect_experience_level(title)

            # Create job data with verification fields
            current_time = datetime.now().isoformat()

            # Check if this job already exists
            is_new = job_id not in self.existing_jobs

            # For existing jobs, preserve first_seen and accumulate locations
            if not is_new:
                existing_job = self.existing_jobs[job_id]
                first_seen = existing_job.get('first_seen', current_time)

                # Accumulate locations (store as list)
                existing_locations = existing_job.get('locations', [])
                if isinstance(existing_locations, str):
                    # Convert old single location to list
                    existing_locations = [existing_locations] if existing_locations else []

                # Add new location if not already in list
                current_location = location or "Unknown Location"
                if current_location not in existing_locations:
                    existing_locations.append(current_location)
                locations = existing_locations
            else:
                first_seen = current_time
                locations = [location or "Unknown Location"]

            job_data = {
                "id": job_id,
                "title": title,
                "company": company or "Unknown Company",
                "location": location or "Unknown Location",  # Keep for backward compatibility
                "locations": locations,  # New: array of all locations
                "country": country,  # Add country field
                "job_type": job_type,  # Add job type classification
                "experience_level": experience_level,  # Add experience level
                "posted_date": posted_date or "Unknown",
                "job_url": job_url,
                "first_seen": first_seen,  # New: when first encountered
                "last_seen": current_time,  # New: when last seen
                "scraped_at": current_time,
                "applied": False,
                "rejected": False,
                "easy_apply": easy_apply,  # Keep for backward compatibility
                "easy_apply_status": easy_apply_status,  # New: confidence level
                "easy_apply_verified_at": current_time if easy_apply_verification_method else None,
                "easy_apply_verification_method": easy_apply_verification_method,  # New: how it was detected
                "is_new": is_new
            }
            
            # Preserve applied status if job already exists
            job_data = self.preserve_applied_status(job_id, job_data)
            
            return job_data
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
        easy_apply_jobs = len([job for job in self.jobs_data if job.get('easy_apply', False)])

        return {
            'total': total_jobs,
            'new': new_jobs,
            'existing': existing_jobs,
            'applied': applied_jobs,
            'not_applied': total_jobs - applied_jobs,
            'easy_apply': easy_apply_jobs
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
        print(f"⚡ Easy Apply: {stats['easy_apply']}")
        print("=" * 60)

        for i, job in enumerate(self.jobs_data, 1):
            status_icons = []
            if job.get('is_new', False):
                status_icons.append("🆕")
            if job.get('applied', False):
                status_icons.append("✅")
            else:
                status_icons.append("⏳")
            if job.get('easy_apply', False):
                status_icons.append("⚡")

            status_str = " ".join(status_icons)

            print(f"\n{i}. [{job['id']}] {job['title']} {status_str}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Posted: {job['posted_date']}")
            if job.get('easy_apply', False):
                print(f"   ⚡ Easy Apply Available")
            print(f"   URL: {job['job_url']}")
            print("-" * 60)
    
    def close(self):
        if self.driver:
            self.driver.quit()