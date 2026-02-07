"""
Foorilla.com job source adapter

Strategy:
1. Try documented API first (if available)
2. Fall back to HTML scraping
3. Handle failures gracefully with retries
"""
import logging
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, quote
import time
from bs4 import BeautifulSoup

from .base import JobSourceAdapter

logger = logging.getLogger(__name__)


class FoorillaAPIClient:
    """Foorilla API client with retry logic"""
    
    BASE_URL = "https://www.foorilla.com"
    
    # Try common API endpoints
    API_ENDPOINTS = [
        "/api/v1/jobs",
        "/api/jobs",
        "/api/v2/jobs",
        "/jobs/search"
    ]
    
    # User agent to avoid blocking
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    def __init__(self, max_retries: int = 3, timeout: int = 10):
        """
        Initialize API client
        
        Args:
            max_retries: Number of retries on failure
            timeout: Request timeout in seconds
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def search_api(self, query: str, location: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        Search jobs via API with retry logic
        
        Args:
            query: Search keyword
            location: Job location
            limit: Max results
        
        Returns:
            List of job data or None if all attempts fail
        """
        for endpoint in self.API_ENDPOINTS:
            url = urljoin(self.BASE_URL, endpoint)
            
            params = {
                "keyword": query,
                "location": location,
                "limit": limit,
                "q": query,  # Some APIs use 'q'
                "city": location,  # Some APIs use 'city'
            }
            
            for attempt in range(self.max_retries):
                try:
                    logger.debug(f"API attempt {attempt + 1}/{self.max_retries}: {url}")
                    
                    response = self.session.get(url, params=params, timeout=self.timeout)
                    response.raise_for_status()
                    
                    data = response.json()
                    jobs = data.get("jobs", data.get("results", data.get("data", [])))
                    
                    if jobs:
                        logger.info(f"API success: Found {len(jobs)} jobs from {endpoint}")
                        return jobs
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"API timeout on {endpoint} (attempt {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                
                except requests.exceptions.ConnectionError:
                    logger.warning(f"API connection error on {endpoint} (attempt {attempt + 1})")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                
                except requests.exceptions.HTTPError as e:
                    logger.debug(f"API HTTP error on {endpoint}: {e.response.status_code}")
                    break  # Don't retry on HTTP errors, try next endpoint
                
                except ValueError:
                    logger.debug(f"Invalid JSON from {endpoint}")
                    break  # Try next endpoint
                
                except Exception as e:
                    logger.debug(f"API error on {endpoint}: {e}")
                    break
        
        logger.warning("All API endpoints exhausted, will try scraping")
        return None


class FoorillaScraperClient:
    """Foorilla HTML scraper (fallback)"""
    
    BASE_URL = "https://www.foorilla.com"
    SEARCH_PATH = "/jobs"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    def __init__(self, timeout: int = 10):
        """Initialize scraper"""
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
    
    def scrape_jobs(self, query: str, location: str, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        Scrape jobs via HTML parsing (fallback)
        
        Args:
            query: Search keyword
            location: Job location
            limit: Max results
        
        Returns:
            List of parsed job data or None if scraping fails
        """
        try:
            # Build search URL
            search_url = urljoin(self.BASE_URL, self.SEARCH_PATH)
            params = {"q": query, "location": location}
            
            logger.debug(f"Scraping jobs from {search_url}")
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            jobs = []
            
            # Try common job listing selectors
            job_selectors = [
                ".job-listing",
                ".job-card",
                "[data-job-id]",
                ".job-item",
                "article.job"
            ]
            
            job_elements = []
            for selector in job_selectors:
                job_elements = soup.select(selector)
                if job_elements:
                    logger.debug(f"Found {len(job_elements)} jobs using selector: {selector}")
                    break
            
            if not job_elements:
                logger.warning("No job elements found in HTML")
                return None
            
            for element in job_elements[:limit]:
                try:
                    job = self._parse_job_element(element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Error parsing job element: {e}")
                    continue
            
            if jobs:
                logger.info(f"Scraping success: Found {len(jobs)} jobs")
                return jobs
            
            return None
        
        except requests.exceptions.Timeout:
            logger.warning("Scraping timeout")
            return None
        
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return None
    
    def _parse_job_element(self, element) -> Optional[Dict[str, Any]]:
        """
        Parse individual job element from HTML
        
        Args:
            element: BeautifulSoup element
        
        Returns:
            Parsed job dictionary or None
        """
        job = {}
        
        # Try to extract common fields
        title_selectors = [".job-title", "h2", "h3", "[data-job-title]", ".title"]
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                job["title"] = title_elem.get_text(strip=True)
                break
        
        company_selectors = [".company", "[data-company]", ".employer", ".organization"]
        for selector in company_selectors:
            company_elem = element.select_one(selector)
            if company_elem:
                job["company"] = company_elem.get_text(strip=True)
                break
        
        location_selectors = [".location", "[data-location]", ".city", ".place"]
        for selector in location_selectors:
            location_elem = element.select_one(selector)
            if location_elem:
                job["location"] = location_elem.get_text(strip=True)
                break
        
        desc_selectors = [".description", ".summary", "[data-description]", ".job-description"]
        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                job["description"] = desc_elem.get_text(strip=True)[:500]  # Limit description
                break
        
        link_elem = element.select_one("a")
        if link_elem and link_elem.get("href"):
            job["job_url"] = urljoin(self.BASE_URL, link_elem["href"])
        
        # Extract job ID from URL or element
        job["id"] = element.get("data-job-id", str(hash(job.get("job_url", ""))))
        job["posted_date"] = datetime.now().isoformat()
        
        # Only return if we have minimum required fields
        if job.get("title") and job.get("company"):
            return job
        
        return None


class FoorillaJobSource(JobSourceAdapter):
    """
    Foorilla.com job source adapter
    
    Uses hybrid approach:
    1. Try API first (fast, reliable)
    2. Fall back to HTML scraping (robust)
    """
    
    def __init__(self):
        """Initialize Foorilla adapter"""
        self.api_client = FoorillaAPIClient()
        self.scraper_client = FoorillaScraperClient()
    
    def get_source_name(self) -> str:
        """Get source identifier"""
        return "foorilla"
    
    def search_jobs(self, query: str, location: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for jobs on Foorilla.com
        
        Strategy:
        1. Try API (if available)
        2. Fall back to scraping
        3. Return empty list on complete failure
        
        Args:
            query: Job search keyword
            location: Job location filter
            limit: Maximum results
        
        Returns:
            List of normalized jobs
        """
        logger.info(f"Searching Foorilla: query='{query}', location='{location}'")
        
        raw_jobs = []
        
        # Step 1: Try API
        try:
            raw_jobs = self.api_client.search_api(query, location, limit)
        except Exception as e:
            logger.warning(f"API attempt failed: {e}")
        
        # Step 2: Fall back to scraping if API didn't work
        if not raw_jobs:
            logger.info("Falling back to HTML scraping...")
            try:
                raw_jobs = self.scraper_client.scrape_jobs(query, location, limit)
            except Exception as e:
                logger.error(f"Scraping attempt failed: {e}")
        
        # Step 3: Normalize and return
        if raw_jobs:
            normalized = [self.normalize_foorilla_job(job) for job in raw_jobs]
            logger.info(f"Returning {len(normalized)} normalized jobs from Foorilla")
            return normalized
        
        logger.warning(f"No jobs found from Foorilla for query='{query}', location='{location}'")
        return []
    
    def normalize_foorilla_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Foorilla job data to common schema
        
        Handles both API and scraped data
        """
        normalized = super().normalize_job(job)
        
        # Extract requirements from tags if available
        if "tags" in job:
            normalized["requirements"] = job["tags"] if isinstance(job["tags"], list) else [job["tags"]]
        
        # Extract salary if present
        if "salary" in job:
            salary = job["salary"]
            if isinstance(salary, dict):
                normalized["salary_min"] = salary.get("min")
                normalized["salary_max"] = salary.get("max")
            elif isinstance(salary, str) and "-" in salary:
                try:
                    parts = salary.replace(",", "").split("-")
                    normalized["salary_min"] = float(parts[0].strip())
                    normalized["salary_max"] = float(parts[1].strip())
                except:
                    pass
        
        # Ensure all required fields have defaults
        normalized.setdefault("id", "")
        normalized.setdefault("title", "")
        normalized.setdefault("company", "")
        normalized.setdefault("description", "")
        normalized.setdefault("location", "")
        normalized.setdefault("job_url", "")
        
        return normalized
