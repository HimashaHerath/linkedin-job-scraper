from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException,
    ElementClickInterceptedException, ElementNotInteractableException
)
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random
import json
import os
import logging
import platform
import subprocess
from fake_useragent import UserAgent
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/selenium_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInSeleniumScraper:
    """
    Enhanced LinkedIn job scraper using Selenium WebDriver.
    
    Features:
    - Cross-platform compatibility (including ARM64 Mac)
    - Local ChromeDriver support
    - Comprehensive error handling and logging
    - Anti-detection measures
    - Robust element waiting and interaction
    - Data validation and cleaning
    """
    
    def __init__(self, headless: bool = True, output_dir: str = "data"):
        """
        Initialize the Selenium scraper.
        
        Args:
            headless (bool): Run in headless mode
            output_dir (str): Directory to save output files
        """
        self.ua = UserAgent()
        self.jobs_data = []
        self.driver = None
        self.headless = headless
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up local driver path
        self.project_root = Path(__file__).parent.parent.parent
        self.local_driver_path = self.project_root / "drivers" / "chromedriver"
        
        # Platform detection for compatibility
        self.platform_info = {
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
        
        logger.info(f"Initializing Selenium scraper on {self.platform_info}")
        logger.info(f"Local driver path: {self.local_driver_path}")
        
        try:
            self.setup_driver()
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise
    
    def setup_driver(self) -> None:
        """Set up Chrome WebDriver with enhanced compatibility and anti-detection."""
        chrome_options = Options()
        
        # Basic options
        if self.headless:
            chrome_options.add_argument("--headless=new")  # Use new headless mode
        
        # Enhanced anti-detection options
        chrome_options.add_argument(f"--user-agent={self.ua.random}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # Performance optimizations
        chrome_options.add_argument("--memory-pressure-off")
        chrome_options.add_argument("--max_old_space_size=4096")
        
        # Additional prefs for anti-detection
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 2
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            # First try: Use local ChromeDriver if available
            if self.local_driver_path.exists():
                logger.info(f"Using local ChromeDriver at: {self.local_driver_path}")
                service = Service(str(self.local_driver_path))
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.info("Successfully initialized with local ChromeDriver")
            else:
                logger.info("Local ChromeDriver not found, using WebDriver Manager...")
                
                try:
                    # Clear any cached drivers that might be incompatible
                    import webdriver_manager.chrome
                    cache_dir = Path.home() / ".wdm"
                    if cache_dir.exists() and self.platform_info['machine'] == 'arm64':
                        logger.info("Detected ARM64 Mac - clearing WebDriver cache for compatibility")
                        import shutil
                        shutil.rmtree(cache_dir, ignore_errors=True)
                    
                    # Install compatible ChromeDriver
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    
                except Exception as e:
                    logger.warning(f"WebDriver Manager failed: {str(e)}")
                    
                    # Third try: Use system Chrome binary if available
                    logger.info("Trying to use system Chrome installation...")
                    
                    chrome_paths = self._find_chrome_executable()
                    if chrome_paths:
                        for chrome_path in chrome_paths:
                            try:
                                chrome_options.binary_location = chrome_path
                                self.driver = webdriver.Chrome(options=chrome_options)
                                logger.info(f"Successfully using Chrome at: {chrome_path}")
                                break
                            except Exception as path_error:
                                logger.warning(f"Failed with Chrome at {chrome_path}: {str(path_error)}")
                                continue
                    else:
                        raise WebDriverException("No Chrome installation found")
                    
                    if not self.driver:
                        raise WebDriverException("All Chrome setup attempts failed")
            
            # Configure driver settings
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # Execute anti-detection scripts
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                window.chrome = {
                    runtime: {}
                };
            """)
            
            logger.info("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing WebDriver: {str(e)}")
            if self.driver:
                self.driver.quit()
            raise
    
    def _find_chrome_executable(self) -> List[str]:
        """Find Chrome executable paths for different platforms."""
        chrome_paths = []
        
        if self.platform_info['system'] == 'Darwin':  # macOS
            possible_paths = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Chromium.app/Contents/MacOS/Chromium',
                '/usr/local/bin/chrome',
                '/usr/local/bin/google-chrome'
            ]
        elif self.platform_info['system'] == 'Linux':
            possible_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium-browser',
                '/usr/bin/chromium',
                '/snap/bin/chromium'
            ]
        elif self.platform_info['system'] == 'Windows':
            possible_paths = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                r'C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe'.format(os.getenv('USERNAME'))
            ]
        else:
            possible_paths = []
        
        for path in possible_paths:
            if os.path.exists(path):
                chrome_paths.append(path)
                logger.debug(f"Found Chrome at: {path}")
        
        return chrome_paths
    
    def search_jobs(self, keywords: str = "", location: str = "", 
                   max_pages: int = 5, delay_range: Tuple[float, float] = (3, 6)) -> List[Dict]:
        """
        Search for jobs on LinkedIn using Selenium with comprehensive error handling.
        
        Args:
            keywords (str): Job title or keywords to search for
            location (str): Location to search in
            max_pages (int): Maximum number of pages to scrape
            delay_range (tuple): Random delay range between actions in seconds
            
        Returns:
            List[Dict]: List of job data dictionaries
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            logger.info(f"Starting LinkedIn job search for: '{keywords}' in '{location}'")
            
            # Navigate to LinkedIn jobs page with retry
            success = self._navigate_to_jobs_page(delay_range)
            if not success:
                logger.error("Failed to navigate to LinkedIn jobs page")
                return self.jobs_data
            
            # Perform search with error handling
            success = self.perform_search(keywords, location, delay_range)
            if not success:
                logger.error("Failed to perform job search")
                return self.jobs_data
            
            # Scrape multiple pages
            for page in range(max_pages):
                logger.info(f"Scraping page {page + 1}...")
                
                try:
                    # Wait for job listings to load
                    if not self.wait_for_jobs_to_load():
                        logger.warning(f"Jobs failed to load on page {page + 1}")
                        break
                    
                    # Extract job data from current page
                    jobs_extracted = self.extract_jobs_from_page()
                    logger.info(f"Extracted {jobs_extracted} jobs from page {page + 1}")
                    
                    # Navigate to next page
                    if page < max_pages - 1:
                        if not self.go_to_next_page(delay_range):
                            logger.info("No more pages available or failed to navigate")
                            break
                    
                    # Random delay between pages
                    time.sleep(random.uniform(*delay_range))
                    
                except Exception as e:
                    logger.error(f"Error on page {page + 1}: {str(e)}")
                    continue
            
            logger.info(f"Scraping completed. Found {len(self.jobs_data)} jobs.")
            return self.jobs_data
            
        except Exception as e:
            logger.error(f"Error during job search: {str(e)}")
            return self.jobs_data
        finally:
            self.close_driver()
    
    def _navigate_to_jobs_page(self, delay_range: Tuple[float, float], max_retries: int = 3) -> bool:
        """Navigate to LinkedIn jobs page with retry logic."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Navigating to LinkedIn jobs page (attempt {attempt + 1})")
                self.driver.get("https://www.linkedin.com/jobs/")
                
                # Wait for page to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                time.sleep(random.uniform(*delay_range))
                
                # Check if we're on the jobs page
                if "jobs" in self.driver.current_url.lower():
                    logger.info("Successfully navigated to LinkedIn jobs page")
                    return True
                else:
                    logger.warning(f"Unexpected URL: {self.driver.current_url}")
                    
            except TimeoutException:
                logger.warning(f"Timeout on navigation attempt {attempt + 1}")
            except Exception as e:
                logger.warning(f"Navigation error on attempt {attempt + 1}: {str(e)}")
            
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait before retry
        
        return False
    
    def perform_search(self, keywords: str, location: str, 
                      delay_range: Tuple[float, float]) -> bool:
        """Perform the job search on LinkedIn with enhanced error handling."""
        try:
            logger.info(f"Performing search: keywords='{keywords}', location='{location}'")
            
            # Find and fill the keywords search box
            if keywords:
                keywords_selectors = [
                    "input[aria-label*='Search job titles']",
                    "input[aria-label*='Search jobs']",
                    "input[placeholder*='Search job titles']",
                    ".jobs-search-box__text-input[aria-label*='Search']"
                ]
                
                keywords_box = self._find_element_with_fallbacks(keywords_selectors)
                if keywords_box:
                    self._safe_clear_and_type(keywords_box, keywords, delay_range)
                else:
                    logger.error("Could not find keywords search box")
                    return False
            
            # Find and fill the location search box
            if location:
                location_selectors = [
                    "input[aria-label*='Search job locations']",
                    "input[aria-label*='Search locations']",
                    "input[placeholder*='Search job locations']",
                    ".jobs-search-box__text-input[aria-label*='Location']"
                ]
                
                location_box = self._find_element_with_fallbacks(location_selectors)
                if location_box:
                    self._safe_clear_and_type(location_box, location, delay_range)
                else:
                    logger.warning("Could not find location search box")
            
            # Click search button
            search_selectors = [
                "button[aria-label='Search']",
                "button[aria-label*='Search']",
                ".jobs-search-box__submit-button",
                "button[type='submit']"
            ]
            
            search_button = self._find_element_with_fallbacks(search_selectors)
            if search_button:
                self._safe_click(search_button)
                time.sleep(random.uniform(*delay_range))
                return True
            else:
                logger.error("Could not find search button")
                return False
                
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return False
    
    def _find_element_with_fallbacks(self, selectors: List[str], timeout: int = 10):
        """Find element using multiple selector fallbacks."""
        for selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.debug(f"Found element with selector: {selector}")
                return element
            except TimeoutException:
                continue
        return None
    
    def _safe_clear_and_type(self, element, text: str, delay_range: Tuple[float, float]) -> bool:
        """Safely clear and type text into an element."""
        try:
            # Clear the field
            element.clear()
            time.sleep(random.uniform(0.5, 1.0))
            
            # Type text character by character for human-like behavior
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            time.sleep(random.uniform(1, 2))
            return True
            
        except Exception as e:
            logger.error(f"Error typing text: {str(e)}")
            return False
    
    def _safe_click(self, element) -> bool:
        """Safely click an element with multiple strategies."""
        try:
            # Try normal click first
            element.click()
            return True
        except ElementClickInterceptedException:
            try:
                # Try JavaScript click
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e:
                logger.error(f"JavaScript click failed: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Click failed: {str(e)}")
            return False
    
    def wait_for_jobs_to_load(self, timeout: int = 20) -> bool:
        """Wait for job listings to load on the page."""
        job_selectors = [
            ".job-search-card",
            ".jobs-search-results__list-item",
            ".job-result-card",
            ".jobs-search-results-list",
            "[data-entity-urn*='jobPosting']"
        ]
        
        for selector in job_selectors:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.debug(f"Jobs loaded with selector: {selector}")
                return True
            except TimeoutException:
                continue
        
        logger.warning("Timeout waiting for job listings to load")
        return False
    
    def extract_jobs_from_page(self) -> int:
        """Extract job data from the current page."""
        jobs_extracted = 0
        
        try:
            # Find job cards using multiple possible selectors
            job_selectors = [
                ".job-search-card",
                ".jobs-search-results__list-item",
                ".job-result-card",
                "[data-entity-urn*='jobPosting']",
                "[data-occludable-job-id]"
            ]
            
            job_cards = []
            for selector in job_selectors:
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards:
                    logger.debug(f"Found {len(job_cards)} job cards with selector: {selector}")
                    break
            
            if not job_cards:
                logger.warning("No job cards found on this page")
                return 0
            
            for i, card in enumerate(job_cards):
                try:
                    job_data = self.extract_job_data_from_card(card)
                    if job_data and self._validate_job_data(job_data):
                        self.jobs_data.append(job_data)
                        jobs_extracted += 1
                        logger.debug(f"Extracted job {i+1}: {job_data.get('title', 'N/A')}")
                    
                except Exception as e:
                    logger.error(f"Error extracting data from job card {i+1}: {str(e)}")
                    continue
            
            return jobs_extracted
            
        except Exception as e:
            logger.error(f"Error extracting jobs from page: {str(e)}")
            return 0
    
    def extract_job_data_from_card(self, job_card) -> Optional[Dict]:
        """Extract job data from a single job card element."""
        try:
            job_data = {}
            
            # Extract job title
            title_selectors = [
                "h3 a", "h3", ".job-title-link", "[data-cy='job-title'] a",
                ".job-search-card__title a", ".base-search-card__title a"
            ]
            job_data['title'] = self._extract_text_from_card(job_card, title_selectors) or "N/A"
            
            # Extract job URL
            url_selectors = ["a[href*='/jobs/view/']", "h3 a", ".job-title-link"]
            job_data['job_url'] = self._extract_url_from_card(job_card, url_selectors) or "N/A"
            
            # Extract company name
            company_selectors = [
                "h4 a", "h4", ".job-search-card__subtitle-link",
                "[data-cy='job-company-name'] a", ".base-search-card__subtitle a"
            ]
            job_data['company'] = self._extract_text_from_card(job_card, company_selectors) or "N/A"
            
            # Extract location
            location_selectors = [
                ".job-search-card__location", "[data-cy='job-location']",
                ".job-result-card__location", ".base-search-card__metadata"
            ]
            job_data['location'] = self._extract_text_from_card(job_card, location_selectors) or "N/A"
            
            # Extract posting date
            try:
                date_element = job_card.find_element(By.CSS_SELECTOR, "time")
                job_data['posted_date'] = date_element.get_attribute('datetime') or date_element.text
            except NoSuchElementException:
                job_data['posted_date'] = "N/A"
            
            # Extract job summary
            summary_selectors = [
                ".job-search-card__snippet", ".job-result-card__snippet",
                ".base-search-card__metadata", "[data-cy='job-snippet']"
            ]
            job_data['summary'] = self._extract_text_from_card(job_card, summary_selectors) or "N/A"
            
            # Add metadata
            job_data['scraped_at'] = pd.Timestamp.now().isoformat()
            job_data['source'] = 'linkedin_selenium_scraper'
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error extracting job data from card: {str(e)}")
            return None
    
    def _extract_text_from_card(self, card, selectors: List[str]) -> Optional[str]:
        """Extract text from card using multiple selector fallbacks."""
        for selector in selectors:
            try:
                element = card.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and text != "N/A":
                    return text
            except NoSuchElementException:
                continue
        return None
    
    def _extract_url_from_card(self, card, selectors: List[str]) -> Optional[str]:
        """Extract URL from card using multiple selector fallbacks."""
        for selector in selectors:
            try:
                element = card.find_element(By.CSS_SELECTOR, selector)
                href = element.get_attribute('href')
                if href:
                    return href
            except NoSuchElementException:
                continue
        return None
    
    def _validate_job_data(self, job_data: Dict) -> bool:
        """Validate job data to ensure quality."""
        required_fields = ['title', 'company']
        
        # Check for required fields
        for field in required_fields:
            if not job_data.get(field) or job_data[field] == "N/A":
                return False
        
        # Check for duplicates
        job_signature = f"{job_data['title']}_{job_data['company']}"
        for existing_job in self.jobs_data:
            existing_signature = f"{existing_job['title']}_{existing_job['company']}"
            if job_signature == existing_signature:
                return False
        
        return True
    
    def go_to_next_page(self, delay_range: Tuple[float, float]) -> bool:
        """Navigate to the next page of results."""
        try:
            # Find next button using multiple selectors
            next_selectors = [
                "button[aria-label='Next']",
                "button[aria-label*='Next']",
                ".jobs-search-results-list__pagination button:last-child",
                "button[data-cy='page-next']"
            ]
            
            next_button = self._find_element_with_fallbacks(next_selectors, timeout=5)
            
            if next_button and next_button.is_enabled():
                # Scroll to button
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                
                # Click next button
                if self._safe_click(next_button):
                    time.sleep(random.uniform(*delay_range))
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error navigating to next page: {str(e)}")
            return False
    
    def save_to_csv(self, filename: str = "linkedin_jobs_selenium.csv") -> bool:
        """Save scraped jobs to CSV file."""
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
    
    def save_to_json(self, filename: str = "linkedin_jobs_selenium.json") -> bool:
        """Save scraped jobs to JSON file."""
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
    
    def print_summary(self) -> None:
        """Print a comprehensive summary of scraped jobs."""
        if not self.jobs_data:
            print("No jobs found.")
            return
        
        try:
            df = pd.DataFrame(self.jobs_data)
            
            print(f"\n{'='*50}")
            print(f"LinkedIn Selenium Scraper Summary")
            print(f"{'='*50}")
            print(f"Total jobs found: {len(df)}")
            print(f"Unique companies: {df['company'].nunique()}")
            print(f"Unique locations: {df['location'].nunique()}")
            
            print(f"\nTop companies:")
            for company, count in df['company'].value_counts().head().items():
                print(f"  {company}: {count}")
            
            print(f"\nTop locations:")
            for location, count in df['location'].value_counts().head().items():
                print(f"  {location}: {count}")
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
    
    def close_driver(self) -> None:
        """Safely close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None


def main():
    """Main function to run the LinkedIn Selenium scraper."""
    
    print("LinkedIn Selenium Job Scraper")
    print("=" * 50)
    
    try:
        # Get user input
        while True:
            keywords = input("Enter job keywords: ").strip()
            if keywords:
                break
            print("Keywords are required.")
        
        location = input("Enter location [optional]: ").strip()
        
        while True:
            try:
                max_pages = input("Enter max pages (1-5, default 2): ").strip()
                max_pages = int(max_pages) if max_pages else 2
                if 1 <= max_pages <= 5:
                    break
                else:
                    print("Please enter 1-5.")
            except ValueError:
                print("Please enter a valid number.")
        
        headless = input("Run in headless mode? (y/n, default y): ").strip().lower()
        headless = headless != 'n'
        
        print(f"\nStarting Selenium scrape:")
        print(f"  Keywords: {keywords}")
        print(f"  Location: {location or 'Any'}")
        print(f"  Max pages: {max_pages}")
        print(f"  Headless: {headless}")
        print("-" * 50)
        
        # Initialize and run scraper
        scraper = LinkedInSeleniumScraper(headless=headless)
        
        jobs = scraper.search_jobs(
            keywords=keywords,
            location=location,
            max_pages=max_pages,
            delay_range=(3, 6)
        )
        
        # Save and display results
        if jobs:
            scraper.save_to_csv("linkedin_jobs_selenium.csv")
            scraper.save_to_json("linkedin_jobs_selenium.json")
            scraper.print_summary()
            
            print(f"\nFiles saved to 'data/' directory:")
            print(f"  - linkedin_jobs_selenium.csv")
            print(f"  - linkedin_jobs_selenium.json")
        else:
            print("\nNo jobs found.")
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main() 