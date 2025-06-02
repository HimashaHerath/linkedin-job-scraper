import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import csv
import json
import logging
from fake_useragent import UserAgent
from urllib.parse import urlencode, urlparse, parse_qs
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInJobScraper:
    """
    A robust LinkedIn job scraper using requests and BeautifulSoup.
    
    Features:
    - Rate limiting and anti-detection measures
    - Comprehensive error handling and logging
    - Multiple CSS selector fallbacks
    - Data validation and cleaning
    - Export to CSV and JSON formats
    """
    
    def __init__(self, output_dir: str = "data"):
        """
        Initialize the LinkedIn job scraper.
        
        Args:
            output_dir (str): Directory to save output files
        """
        self.ua = UserAgent()
        self.session = requests.Session()
        self.base_url = "https://www.linkedin.com"
        self.jobs_data = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up session headers with anti-detection measures
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Cache-Control': 'max-age=0'
        })
        
        # Request session configuration
        self.session.max_redirects = 3
        
        logger.info("LinkedIn job scraper initialized successfully")
    
    def search_jobs(self, keywords: str = "", location: str = "", 
                   experience_level: str = "", job_type: str = "", 
                   company: str = "", max_pages: int = 5, 
                   delay_range: Tuple[float, float] = (2, 5)) -> List[Dict]:
        """
        Search for jobs on LinkedIn with comprehensive error handling.
        
        Args:
            keywords (str): Job title or keywords to search for
            location (str): Location to search in
            experience_level (str): Experience level filter
            job_type (str): Job type filter (full-time, part-time, etc.)
            company (str): Company name filter
            max_pages (int): Maximum number of pages to scrape
            delay_range (tuple): Random delay range between requests in seconds
            
        Returns:
            List[Dict]: List of job data dictionaries
        """
        if not keywords.strip():
            logger.warning("No keywords provided for job search")
            
        logger.info(f"Starting LinkedIn job search for: '{keywords}' in '{location}'")
        
        # Build search parameters
        search_params = {
            'keywords': keywords.strip(),
            'location': location.strip(),
            'f_E': experience_level,
            'f_JT': job_type,
            'f_C': company,
            'sortBy': 'R'  # Sort by relevance
        }
        
        # Remove empty parameters
        search_params = {k: v for k, v in search_params.items() if v}
        
        successful_pages = 0
        failed_pages = 0
        
        for page in range(max_pages):
            try:
                # Add pagination
                search_params['start'] = page * 25
                
                search_url = f"{self.base_url}/jobs/search?" + urlencode(search_params)
                logger.info(f"Scraping page {page + 1}: {search_url}")
                
                # Make request with random delay and retry logic
                success = self._make_request_with_retry(search_url, delay_range, max_retries=3)
                
                if success:
                    successful_pages += 1
                    logger.info(f"Successfully scraped page {page + 1}")
                else:
                    failed_pages += 1
                    logger.warning(f"Failed to scrape page {page + 1}")
                    
                    # Stop if too many consecutive failures
                    if failed_pages >= 3:
                        logger.error("Too many consecutive failures. Stopping scraper.")
                        break
                        
            except Exception as e:
                failed_pages += 1
                logger.error(f"Unexpected error scraping page {page + 1}: {str(e)}")
                
                if failed_pages >= 3:
                    logger.error("Too many failures. Stopping scraper.")
                    break
                continue
        
        logger.info(f"Scraping completed. Successful pages: {successful_pages}, "
                   f"Failed pages: {failed_pages}, Total jobs found: {len(self.jobs_data)}")
        return self.jobs_data
    
    def _make_request_with_retry(self, url: str, delay_range: Tuple[float, float], 
                                max_retries: int = 3) -> bool:
        """
        Make HTTP request with retry logic and error handling.
        
        Args:
            url (str): URL to request
            delay_range (tuple): Delay range for rate limiting
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            bool: True if successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                # Random delay for rate limiting
                delay = random.uniform(*delay_range)
                time.sleep(delay)
                
                # Rotate user agent for anti-detection
                self.session.headers['User-Agent'] = self.ua.random
                
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    self.parse_job_listings(response.text)
                    return True
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = (attempt + 1) * 10
                    logger.warning(f"Rate limited (429). Waiting {wait_time} seconds before retry {attempt + 1}")
                    time.sleep(wait_time)
                elif response.status_code == 403:
                    logger.error("Access forbidden (403). LinkedIn may have blocked this IP.")
                    return False
                else:
                    logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
        
        return False
    
    def parse_job_listings(self, html_content: str) -> None:
        """
        Parse job listings from HTML content with multiple selector fallbacks.
        
        Args:
            html_content (str): Raw HTML content to parse
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Multiple selector strategies for LinkedIn's changing structure
            selectors = [
                'div.job-search-card',
                'div.base-card',
                'li.job-result-card',
                'div.jobs-search-results__list-item',
                'div[data-entity-urn*="jobPosting"]',
                'li[data-occludable-job-id]'
            ]
            
            job_cards = []
            for selector in selectors:
                job_cards = soup.select(selector)
                if job_cards:
                    logger.debug(f"Found {len(job_cards)} job cards using selector: {selector}")
                    break
            
            if not job_cards:
                logger.warning("No job cards found with any selector")
                return
            
            jobs_parsed = 0
            jobs_failed = 0
            
            for i, card in enumerate(job_cards):
                try:
                    job_data = self.extract_job_data(card)
                    if job_data and self._validate_job_data(job_data):
                        self.jobs_data.append(job_data)
                        jobs_parsed += 1
                    else:
                        jobs_failed += 1
                        
                except Exception as e:
                    jobs_failed += 1
                    logger.error(f"Error parsing job card {i + 1}: {str(e)}")
                    continue
            
            logger.info(f"Parsed {jobs_parsed} jobs successfully, {jobs_failed} failed")
            
        except Exception as e:
            logger.error(f"Error parsing HTML content: {str(e)}")
    
    def extract_job_data(self, job_card) -> Optional[Dict]:
        """
        Extract job data from a job card element with multiple fallbacks.
        
        Args:
            job_card: BeautifulSoup element representing a job card
            
        Returns:
            Optional[Dict]: Job data dictionary or None if extraction fails
        """
        try:
            job_data = {}
            
            # Extract job title with multiple fallbacks
            title_selectors = [
                'h3 a', 'h3', '.job-title-link', 'a[data-cy="job-title"]',
                '.job-search-card__title a', '.base-search-card__title a'
            ]
            title = self._extract_text_with_fallbacks(job_card, title_selectors)
            job_data['title'] = title or "N/A"
            
            # Extract company name
            company_selectors = [
                'h4 a', 'h4', '.job-search-card__subtitle-link', 
                'a[data-cy="job-company-name"]', '.base-search-card__subtitle a'
            ]
            company = self._extract_text_with_fallbacks(job_card, company_selectors)
            job_data['company'] = company or "N/A"
            
            # Extract location
            location_selectors = [
                '.job-search-card__location', '[data-cy="job-location"]',
                '.job-result-card__location', '.base-search-card__metadata'
            ]
            location = self._extract_text_with_fallbacks(job_card, location_selectors)
            job_data['location'] = location or "N/A"
            
            # Extract job URL
            url_selectors = ['a[href*="/jobs/view/"]', 'h3 a', '.job-title-link']
            job_url = self._extract_url_with_fallbacks(job_card, url_selectors)
            job_data['job_url'] = job_url or "N/A"
            
            # Extract posting date
            date_elem = job_card.find('time')
            if date_elem:
                job_data['posted_date'] = date_elem.get('datetime') or date_elem.get_text(strip=True)
            else:
                job_data['posted_date'] = "N/A"
            
            # Extract job summary/description
            summary_selectors = [
                '.job-search-card__snippet', '.job-result-card__snippet',
                '.base-search-card__metadata', 'p[data-cy="job-snippet"]'
            ]
            summary = self._extract_text_with_fallbacks(job_card, summary_selectors)
            job_data['summary'] = summary or "N/A"
            
            # Add metadata
            job_data['scraped_at'] = pd.Timestamp.now().isoformat()
            job_data['source'] = 'linkedin_basic_scraper'
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job data: {str(e)}")
            return None
    
    def _extract_text_with_fallbacks(self, element, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple CSS selector fallbacks."""
        for selector in selectors:
            try:
                found_element = element.select_one(selector)
                if found_element:
                    text = found_element.get_text(strip=True)
                    if text and text != "N/A":
                        return text
            except Exception:
                continue
        return None
    
    def _extract_url_with_fallbacks(self, element, selectors: List[str]) -> Optional[str]:
        """Extract URL using multiple CSS selector fallbacks."""
        for selector in selectors:
            try:
                found_element = element.select_one(selector)
                if found_element and found_element.get('href'):
                    href = found_element['href']
                    if href.startswith('/'):
                        href = self.base_url + href
                    return href
            except Exception:
                continue
        return None
    
    def _validate_job_data(self, job_data: Dict) -> bool:
        """
        Validate job data to ensure quality.
        
        Args:
            job_data (Dict): Job data dictionary
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        required_fields = ['title', 'company']
        
        # Check for required fields
        for field in required_fields:
            if not job_data.get(field) or job_data[field] == "N/A":
                logger.debug(f"Job data missing required field: {field}")
                return False
        
        # Check for duplicate jobs (based on title + company)
        job_signature = f"{job_data['title']}_{job_data['company']}"
        for existing_job in self.jobs_data:
            existing_signature = f"{existing_job['title']}_{existing_job['company']}"
            if job_signature == existing_signature:
                logger.debug(f"Duplicate job found: {job_signature}")
                return False
        
        return True
    
    def save_to_csv(self, filename: str = "linkedin_jobs.csv") -> bool:
        """
        Save scraped jobs to CSV file with error handling.
        
        Args:
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.jobs_data:
            logger.warning("No job data to save to CSV")
            return False
        
        try:
            filepath = self.output_dir / filename
            df = pd.DataFrame(self.jobs_data)
            df.to_csv(filepath, index=False, encoding='utf-8')
            logger.info(f"Saved {len(self.jobs_data)} jobs to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving to CSV: {str(e)}")
            return False
    
    def save_to_json(self, filename: str = "linkedin_jobs.json") -> bool:
        """
        Save scraped jobs to JSON file with error handling.
        
        Args:
            filename (str): Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.jobs_data:
            logger.warning("No job data to save to JSON")
            return False
        
        try:
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.jobs_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"Saved {len(self.jobs_data)} jobs to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving to JSON: {str(e)}")
            return False
    
    def get_job_details(self, job_url: str, delay_range: Tuple[float, float] = (3, 6)) -> Optional[Dict]:
        """
        Get detailed job information from a specific job URL.
        
        Args:
            job_url (str): URL of the job posting
            delay_range (tuple): Delay range for rate limiting
            
        Returns:
            Optional[Dict]: Detailed job information or None if failed
        """
        try:
            time.sleep(random.uniform(*delay_range))
            self.session.headers['User-Agent'] = self.ua.random
            
            response = self.session.get(job_url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                details = {
                    'description': '',
                    'requirements': '',
                    'benefits': '',
                    'job_type': '',
                    'seniority_level': '',
                    'industry': '',
                    'company_size': ''
                }
                
                # Extract job description with multiple selectors
                desc_selectors = [
                    '.description__text', '.jobs-description-content__text',
                    '.jobs-box__html-content', '[data-cy="job-description"]'
                ]
                
                for selector in desc_selectors:
                    desc_elem = soup.select_one(selector)
                    if desc_elem:
                        details['description'] = desc_elem.get_text(strip=True)
                        break
                
                return details
            else:
                logger.warning(f"Failed to get job details. Status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting job details from {job_url}: {str(e)}")
            return None
    
    def print_summary(self) -> None:
        """Print a comprehensive summary of scraped jobs."""
        if not self.jobs_data:
            print("No jobs found.")
            return
        
        try:
            df = pd.DataFrame(self.jobs_data)
            
            print(f"\n{'='*50}")
            print(f"LinkedIn Job Scraping Summary")
            print(f"{'='*50}")
            print(f"Total jobs found: {len(df)}")
            print(f"Unique companies: {df['company'].nunique()}")
            print(f"Unique locations: {df['location'].nunique()}")
            print(f"Jobs with valid URLs: {(df['job_url'] != 'N/A').sum()}")
            
            print(f"\nTop 5 companies by job count:")
            company_counts = df['company'].value_counts().head()
            for company, count in company_counts.items():
                print(f"  {company}: {count}")
            
            print(f"\nTop 5 locations:")
            location_counts = df['location'].value_counts().head()
            for location, count in location_counts.items():
                print(f"  {location}: {count}")
            
            # Data quality metrics
            valid_titles = (df['title'] != 'N/A').sum()
            valid_companies = (df['company'] != 'N/A').sum()
            valid_locations = (df['location'] != 'N/A').sum()
            
            print(f"\nData Quality:")
            print(f"  Valid titles: {valid_titles}/{len(df)} ({(valid_titles/len(df)*100):.1f}%)")
            print(f"  Valid companies: {valid_companies}/{len(df)} ({(valid_companies/len(df)*100):.1f}%)")
            print(f"  Valid locations: {valid_locations}/{len(df)} ({(valid_locations/len(df)*100):.1f}%)")
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            print("Error generating job summary.")
    
    def clear_data(self) -> None:
        """Clear all scraped job data."""
        self.jobs_data.clear()
        logger.info("Cleared all job data")


def main():
    """Main function to run the LinkedIn job scraper with enhanced UX."""
    
    print("LinkedIn Job Scraper")
    print("=" * 50)
    
    try:
        # Initialize scraper
        scraper = LinkedInJobScraper()
        
        # Get user input with validation
        while True:
            keywords = input("Enter job keywords (e.g., 'python developer'): ").strip()
            if keywords:
                break
            print("Keywords are required. Please try again.")
        
        location = input("Enter location (e.g., 'New York, NY') [optional]: ").strip()
        
        while True:
            try:
                max_pages = input("Enter max pages to scrape (1-10, default 3): ").strip()
                max_pages = int(max_pages) if max_pages else 3
                if 1 <= max_pages <= 10:
                    break
                else:
                    print("Please enter a number between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")
        
        print(f"\nStarting scrape with:")
        print(f"  Keywords: {keywords}")
        print(f"  Location: {location or 'Any'}")
        print(f"  Max pages: {max_pages}")
        print("-" * 50)
        
        # Search for jobs
        jobs = scraper.search_jobs(
            keywords=keywords,
            location=location,
            max_pages=max_pages,
            delay_range=(2, 4)
        )
        
        # Save and display results
        if jobs:
            scraper.save_to_csv("linkedin_jobs.csv")
            scraper.save_to_json("linkedin_jobs.json")
            scraper.print_summary()
            
            print(f"\nFiles saved to 'data/' directory:")
            print(f"  - linkedin_jobs.csv")
            print(f"  - linkedin_jobs.json")
            
        else:
            print("\nNo jobs found. This might be due to:")
            print("  - LinkedIn's anti-bot measures")
            print("  - Too restrictive search criteria")
            print("  - Network connectivity issues")
            print("\nConsider:")
            print("  - Using broader search terms")
            print("  - Trying the Selenium version for better results")
            print("  - Checking your internet connection")
    
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main() 