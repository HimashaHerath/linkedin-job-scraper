"""
Advanced LinkedIn Job Harvester - 2025 Professional Edition

A sophisticated LinkedIn job scraper designed for maximum reliability and data quality.
Incorporates state-of-the-art web scraping techniques and anti-detection measures.

Key Features:
- HTTPX with HTTP/2 support for superior performance and speed
- Advanced anti-detection system with behavioral simulation
- Intelligent rate limiting and human-like interaction patterns
- AI-resistant browser fingerprinting and session management
- Multi-region and multi-language support
- Enhanced data extraction with quality assessment
- Comprehensive error handling and recovery mechanisms

Author: AI Assistant
Version: 3.0.0
Created: 2025
"""

import httpx
import asyncio
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import csv
import json
import logging
from fake_useragent import UserAgent
from urllib.parse import urlencode, quote_plus
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple, Union, Set
from pathlib import Path
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib
import platform
from collections import Counter, defaultdict
import math
import uuid

# Load environment variables
load_dotenv()

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/harvester.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class HarvestingConfiguration:
    """
    Advanced configuration for job harvesting operations.
    
    This class encapsulates all the parameters needed for optimal
    scraping performance while maintaining stealth and reliability.
    """
    # Rate limiting and timing controls
    minimum_request_delay: float = 3.0
    maximum_request_delay: float = 8.0
    human_variance_factor: float = 0.3
    
    # Session management
    max_requests_per_session: int = 75
    session_reset_threshold: int = 50
    request_timeout_seconds: int = 30
    
    # Anti-detection controls
    user_agent_rotation_frequency: int = 12
    browser_profile_rotation_frequency: int = 25
    
    # Performance settings
    concurrent_request_limit: int = 3
    max_retry_attempts: int = 3
    exponential_backoff_base: float = 2.0
    
    # Break patterns (human-like behavior)
    break_frequency_range: Tuple[int, int] = (15, 25)
    break_duration_range: Tuple[float, float] = (30.0, 90.0)
    
    # Quality control
    minimum_job_title_length: int = 3
    maximum_job_title_length: int = 200
    spam_detection_enabled: bool = True
    
    # Regional settings
    supported_languages: List[str] = field(default_factory=lambda: [
        'en-US', 'en-GB', 'en-CA', 'en-AU', 'es-ES', 'fr-FR', 'de-DE', 'it-IT'
    ])
    
    # Data extraction settings
    extract_salary_info: bool = True
    extract_company_size: bool = True
    extract_job_insights: bool = True
    extract_skills: bool = True


class HumanBehaviorSimulator:
    """
    Simulates realistic human browsing behavior patterns.
    
    This class provides methods to calculate realistic delays, determine
    break patterns, and simulate human-like interactions with web pages.
    """
    
    @staticmethod
    def calculate_realistic_reading_time(content_length: int, reading_speed_wpm: int = 200) -> float:
        """
        Calculate realistic reading time based on content length.
        
        Args:
            content_length: Number of characters in the content
            reading_speed_wpm: Average reading speed in words per minute
            
        Returns:
            Calculated reading time in seconds (capped between 2-15 seconds)
        """
        estimated_words = content_length / 5  # Average 5 characters per word
        reading_time_minutes = estimated_words / reading_speed_wpm
        reading_time_seconds = reading_time_minutes * 60
        
        # Cap between reasonable bounds for web browsing
        return max(2.0, min(15.0, reading_time_seconds))
    
    @staticmethod
    def generate_human_like_delay(base_delay: float, variance_factor: float = 0.3) -> float:
        """
        Generate human-like delay with natural variance.
        
        Human users don't click at perfectly regular intervals. This method
        adds realistic variance to delays to mimic natural behavior.
        
        Args:
            base_delay: Base delay time in seconds
            variance_factor: Percentage of variance to apply (0.0 to 1.0)
            
        Returns:
            Adjusted delay time with human-like variance
        """
        variance_range = base_delay * variance_factor
        variance = random.uniform(-variance_range, variance_range)
        return max(0.5, base_delay + variance)  # Minimum 0.5 seconds
    
    @staticmethod
    def should_take_break(requests_made: int, break_frequency_range: Tuple[int, int]) -> bool:
        """
        Determine if a break should be taken based on request count.
        
        Args:
            requests_made: Number of requests made in current session
            break_frequency_range: Tuple of (min, max) requests before break
            
        Returns:
            True if a break should be taken, False otherwise
        """
        min_freq, max_freq = break_frequency_range
        break_interval = random.randint(min_freq, max_freq)
        return requests_made > 0 and requests_made % break_interval == 0
    
    @staticmethod
    def calculate_progressive_delay(requests_made: int, base_delay: float) -> float:
        """
        Calculate progressively longer delays as session continues.
        
        This mimics human fatigue - users tend to slow down over time.
        
        Args:
            requests_made: Number of requests made in current session
            base_delay: Base delay time
            
        Returns:
            Adjusted delay time accounting for session progress
        """
        if requests_made <= 20:
            return base_delay
        elif requests_made <= 40:
            return base_delay * 1.2
        elif requests_made <= 60:
            return base_delay * 1.5
        else:
            return base_delay * 2.0


class AdvancedAntiDetectionSystem:
    """
    Comprehensive anti-detection system for web scraping.
    
    This class manages browser fingerprinting, user agent rotation,
    header management, and other techniques to avoid detection.
    """
    
    def __init__(self, config: HarvestingConfiguration):
        """
        Initialize the anti-detection system.
        
        Args:
            config: Configuration object with detection avoidance settings
        """
        self.config = config
        self.user_agent_generator = UserAgent()
        self.request_counter = 0
        self.session_fingerprint = self._generate_session_fingerprint()
        self.browser_profiles = self._create_realistic_browser_profiles()
        self.current_browser_profile = random.choice(self.browser_profiles)
        self.last_profile_rotation = 0
    
    def _create_realistic_browser_profiles(self) -> List[Dict[str, str]]:
        """
        Create realistic browser profiles for different browsers and versions.
        
        Returns:
            List of browser profile dictionaries with headers and characteristics
        """
        profiles = []
        
        # Chrome profiles (most common browser)
        chrome_versions = ['120.0.0.0', '119.0.0.0', '118.0.0.0', '117.0.0.0']
        for version in chrome_versions:
            platform_string = self._get_platform_user_agent_string()
            profiles.append({
                'browser': 'chrome',
                'version': version,
                'user_agent': f'Mozilla/5.0 ({platform_string}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept_language': random.choice(self.config.supported_languages + [
                    'en-US,en;q=0.9', 'en-GB,en;q=0.9', 'en-US,en;q=0.8,es;q=0.7'
                ]),
                'accept_encoding': 'gzip, deflate, br',
                'sec_fetch_dest': 'document',
                'sec_fetch_mode': 'navigate',
                'sec_fetch_site': 'none',
                'sec_fetch_user': '?1',
                'sec_ch_ua': f'"Not_A Brand";v="8", "Chromium";v="{version.split(".")[0]}", "Google Chrome";v="{version.split(".")[0]}"',
                'sec_ch_ua_mobile': '?0',
                'sec_ch_ua_platform': f'"{platform.system()}"',
                'upgrade_insecure_requests': '1',
                'cache_control': 'max-age=0'
            })
        
        # Firefox profiles
        firefox_versions = ['121.0', '120.0', '119.0', '118.0']
        for version in firefox_versions:
            platform_string = self._get_platform_user_agent_string()
            profiles.append({
                'browser': 'firefox',
                'version': version,
                'user_agent': f'Mozilla/5.0 ({platform_string}) Gecko/20100101 Firefox/{version}',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'accept_language': random.choice(self.config.supported_languages[:4]),  # Firefox subset
                'accept_encoding': 'gzip, deflate, br',
                'upgrade_insecure_requests': '1',
                'te': 'trailers'
            })
        
        # Edge profiles
        edge_versions = ['120.0.2210.77', '119.0.2151.72']
        for version in edge_versions:
            platform_string = self._get_platform_user_agent_string()
            profiles.append({
                'browser': 'edge',
                'version': version,
                'user_agent': f'Mozilla/5.0 ({platform_string}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/{version}',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'accept_language': 'en-US,en;q=0.9',
                'accept_encoding': 'gzip, deflate, br',
                'sec_fetch_dest': 'document',
                'sec_fetch_mode': 'navigate',
                'sec_fetch_site': 'none',
                'sec_fetch_user': '?1',
                'upgrade_insecure_requests': '1'
            })
        
        return profiles
    
    def _get_platform_user_agent_string(self) -> str:
        """
        Generate platform-specific user agent string.
        
        Returns:
            Platform-appropriate user agent string component
        """
        system = platform.system()
        if system == "Windows":
            return random.choice([
                "Windows NT 10.0; Win64; x64",
                "Windows NT 10.0; WOW64",
                "Windows NT 6.1; Win64; x64"
            ])
        elif system == "Darwin":
            return random.choice([
                "Macintosh; Intel Mac OS X 10_15_7",
                "Macintosh; Intel Mac OS X 10_14_6",
                "Macintosh; Intel Mac OS X 10_13_6"
            ])
        else:  # Linux
            return random.choice([
                "X11; Linux x86_64",
                "X11; Ubuntu; Linux x86_64"
            ])
    
    def get_stealth_headers(self) -> Dict[str, str]:
        """
        Generate stealth headers for HTTP requests.
        
        Returns:
            Dictionary of HTTP headers designed to avoid detection
        """
        self.request_counter += 1
        
        # Rotate browser profile periodically
        if (self.request_counter - self.last_profile_rotation) >= self.config.browser_profile_rotation_frequency:
            self.current_browser_profile = random.choice(self.browser_profiles)
            self.last_profile_rotation = self.request_counter
        
        # Base headers from current browser profile
        headers = dict(self.current_browser_profile)
        
        # Remove metadata fields that shouldn't be in HTTP headers
        headers.pop('browser', None)
        headers.pop('version', None)
        
        # Add dynamic headers
        headers.update({
            'dnt': '1',
            'connection': 'keep-alive',
            'pragma': 'no-cache',
        })
        
        # Add random viewport size (common screen resolutions)
        viewport_sizes = [
            '1920,1080', '1366,768', '1536,864', '1440,900', '1280,720'
        ]
        headers['viewport-width'] = random.choice(viewport_sizes).split(',')[0]
        
        return headers
    
    def _generate_session_fingerprint(self) -> str:
        """
        Generate unique session fingerprint for tracking.
        
        Returns:
            Unique session fingerprint string
        """
        components = [
            str(time.time()),
            str(uuid.uuid4()),
            platform.system(),
            str(random.randint(100000, 999999))
        ]
        fingerprint_string = ''.join(components)
        return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]
    
    def get_current_browser_info(self) -> Dict[str, str]:
        """
        Get information about the current browser profile.
        
        Returns:
            Dictionary with current browser information
        """
        return {
            'browser': self.current_browser_profile.get('browser', 'unknown'),
            'version': self.current_browser_profile.get('version', 'unknown'),
            'fingerprint': self.session_fingerprint
        }


class EnhancedLinkedInJobHarvester:
    """
    Professional LinkedIn Job Harvester - 2025 Edition
    
    A sophisticated job scraping system designed for maximum reliability,
    data quality, and stealth operation. Supports multiple regions,
    languages, and job types with advanced anti-detection capabilities.
    """
    
    # Enhanced CSS selectors with comprehensive fallbacks
    ADVANCED_SELECTORS = {
        'job_cards': [
            'div.job-search-card',
            'div.base-card',
            'li.result-card',
            'div.jobs-search-results__list-item',
            'div[data-entity-urn*="jobPosting"]',
            'li[data-occludable-job-id]',
            'div.scaffold-layout__list-item',
            'article.job-card',
            '.job-result-card',
            '[data-job-id]'
        ],
        'job_title': [
            'h3.base-search-card__title a',
            'h3.job-search-card__title a',
            'h3 a[data-cy="job-title"]',
            '.job-title-link',
            'a[data-cy="job-title"]',
            '.base-search-card__title',
            '.result-card__title a',
            'h2.job-title a',
            '.job-card__title a',
            'h3 > a'
        ],
        'company_name': [
            'h4.base-search-card__subtitle a',
            'h4.job-search-card__subtitle-link',
            'h4 a[data-cy="job-company-name"]',
            '.job-search-card__subtitle-link',
            'a[data-cy="job-company-name"]',
            '.result-card__subtitle',
            '.company-name-link',
            'h4 > a',
            '.job-card__company-name a'
        ],
        'job_location': [
            '.job-search-card__location',
            '[data-cy="job-location"]',
            '.result-card__location',
            '.base-search-card__metadata',
            '.job-location',
            '.location-text',
            'span.job-search-card__location'
        ],
        'posting_date': [
            'time[datetime]',
            '.job-search-card__listdate',
            '.job-result-card__listdate',
            '.posted-time-ago',
            '[data-cy="posting-date"]'
        ],
        'salary_info': [
            '.job-search-card__salary-info',
            '.salary-snippet',
            '.job-insight[data-test-id*="salary"]',
            '.compensation-text',
            '[data-test-id="job-salary"]'
        ],
        'job_insights': [
            'li.job-search-card__job-insight',
            '.job-insights-container li',
            '.job-criteria li',
            '.job-benefits li',
            '[data-cy="job-insight"]'
        ],
        'applicant_count': [
            '.job-search-card__subtitle-wrapper',
            '.applicant-count',
            '.num-applicants',
            '[data-cy="applicant-count"]'
        ]
    }
    
    # Regional LinkedIn domains and configurations
    REGIONAL_DOMAINS = {
        'US': 'www.linkedin.com',
        'UK': 'uk.linkedin.com',
        'CA': 'ca.linkedin.com',
        'AU': 'au.linkedin.com',
        'DE': 'de.linkedin.com',
        'FR': 'fr.linkedin.com',
        'ES': 'es.linkedin.com',
        'IT': 'it.linkedin.com',
        'IN': 'in.linkedin.com',
        'BR': 'br.linkedin.com',
        'JP': 'jp.linkedin.com',
        'SG': 'sg.linkedin.com'
    }
    
    def __init__(self, output_directory: str = "harvested_data", 
                 config: Optional[HarvestingConfiguration] = None,
                 region: str = "US"):
        """
        Initialize the LinkedIn Job Harvester.
        
        Args:
            output_directory: Directory path for saving harvested data
            config: Configuration object for harvesting parameters
            region: Regional code for LinkedIn domain (US, UK, CA, etc.)
        """
        self.config = config or HarvestingConfiguration()
        self.behavior_simulator = HumanBehaviorSimulator()
        self.anti_detection_system = AdvancedAntiDetectionSystem(self.config)
        
        # Set up regional configuration
        self.region = region.upper()
        self.base_domain = self.REGIONAL_DOMAINS.get(self.region, self.REGIONAL_DOMAINS['US'])
        self.base_url = f"https://{self.base_domain}"
        
        # Data storage
        self.harvested_jobs_data = []
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Session management
        self.http_client = None
        self.requests_made_in_session = 0
        self.session_start_timestamp = time.time()
        self.last_request_timestamp = 0
        
        # Quality tracking
        self.extraction_statistics = defaultdict(int)
        self.quality_metrics = defaultdict(list)
        
        logger.info(f"LinkedIn Job Harvester initialized for region {self.region}")
        logger.info(f"Using domain: {self.base_domain}")
    
    async def __aenter__(self):
        """Async context manager entry point."""
        await self._initialize_http_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit point."""
        await self._cleanup_http_client()
    
    async def _initialize_http_client(self):
        """
        Initialize HTTPX client with optimal performance settings.
        
        Sets up HTTP/2 support, connection pooling, timeouts, and headers.
        """
        # Configure connection limits for optimal performance
        connection_limits = httpx.Limits(
            max_keepalive_connections=15,
            max_connections=25,
            keepalive_expiry=45.0
        )
        
        # Configure timeouts
        timeout_config = httpx.Timeout(
            timeout=self.config.request_timeout_seconds,
            connect=10.0,
            read=25.0,
            write=5.0,
            pool=10.0
        )
        
        # Initialize client with advanced features
        self.http_client = httpx.AsyncClient(
            limits=connection_limits,
            timeout=timeout_config,
            http2=True,  # Enable HTTP/2 for better performance
            follow_redirects=True,
            headers=self.anti_detection_system.get_stealth_headers(),
            verify=True  # Enable SSL verification for security
        )
        
        logger.info("HTTP client initialized with HTTP/2 support and advanced features")
    
    async def _cleanup_http_client(self):
        """Clean up HTTP client resources."""
        if self.http_client:
            await self.http_client.aclose()
            logger.info("HTTP client cleaned up")
    
    async def harvest_jobs(self, 
                          search_keywords: str = "",
                          target_location: str = "",
                          maximum_pages: int = 5,
                          **additional_filters) -> List[Dict]:
        """
        Harvest job listings from LinkedIn with advanced filtering and extraction.
        
        Args:
            search_keywords: Job title or keywords to search for
            target_location: Geographic location for job search
            maximum_pages: Maximum number of result pages to process
            **additional_filters: Additional search filters (experience_level, job_type, etc.)
            
        Returns:
            List of dictionaries containing harvested job data
        """
        if not search_keywords.strip():
            logger.warning("No search keywords provided - performing broad search")
        
        logger.info(f"Starting job harvest: '{search_keywords}' in '{target_location}'")
        logger.info(f"Target pages: {maximum_pages}, Region: {self.region}")
        
        # Build optimized search parameters
        search_parameters = self._construct_search_parameters(
            search_keywords, target_location, **additional_filters
        )
        
        # Initialize counters
        successful_pages = 0
        failed_pages = 0
        
        # Process pages sequentially with intelligent pacing
        for page_number in range(maximum_pages):
            try:
                # Check session health and reset if needed
                if self.requests_made_in_session >= self.config.max_requests_per_session:
                    await self._reset_session_completely()
                
                # Implement human-like break patterns
                if self.behavior_simulator.should_take_break(
                    self.requests_made_in_session, 
                    self.config.break_frequency_range
                ):
                    await self._take_human_like_break()
                
                # Configure pagination
                search_parameters['start'] = page_number * 25
                search_url = self._build_search_url(search_parameters)
                
                logger.info(f"Processing page {page_number + 1}/{maximum_pages}")
                
                # Execute request with intelligent retry logic
                page_success = await self._execute_intelligent_request(search_url)
                
                if page_success:
                    successful_pages += 1
                    logger.info(f"Successfully processed page {page_number + 1}")
                else:
                    failed_pages += 1
                    logger.warning(f"Failed to process page {page_number + 1}")
                    
                    # Implement adaptive failure handling
                    if failed_pages >= 2:
                        logger.error("Multiple failures detected - implementing recovery strategy")
                        await self._implement_recovery_strategy()
                        
                    if failed_pages >= 3:
                        logger.error("Too many failures - terminating harvest")
                        break
                
            except Exception as e:
                failed_pages += 1
                logger.error(f"Unexpected error processing page {page_number + 1}: {str(e)}")
                
                if failed_pages >= 3:
                    logger.error("Critical failure threshold reached - stopping harvest")
                    break
        
        # Log final results
        total_jobs = len(self.harvested_jobs_data)
        logger.info(f"Harvest completed: {successful_pages} successful pages, "
                   f"{failed_pages} failed pages, {total_jobs} jobs harvested")
        
        return self.harvested_jobs_data
    
    def _construct_search_parameters(self, keywords: str, location: str, **filters) -> Dict:
        """
        Construct optimized search parameters for LinkedIn job search.
        
        Args:
            keywords: Job search keywords
            location: Target location
            **filters: Additional search filters
            
        Returns:
            Dictionary of search parameters
        """
        # Base parameters
        parameters = {
            'keywords': keywords.strip(),
            'location': location.strip(),
            'sortBy': 'R',  # Sort by relevance
            'f_TPR': filters.get('date_posted', ''),  # Time period
            'f_E': filters.get('experience_level', ''),  # Experience level
            'f_JT': filters.get('job_type', ''),  # Job type
            'f_SB2': filters.get('salary_min', ''),  # Salary minimum
            'f_C': filters.get('company', ''),  # Company filter
            'f_I': filters.get('industry', ''),  # Industry filter
            'f_CF': filters.get('company_size', ''),  # Company size
            'f_WT': filters.get('work_type', ''),  # Remote/on-site
        }
        
        # Remove empty parameters to clean up the URL
        return {key: value for key, value in parameters.items() if value}
    
    def _build_search_url(self, parameters: Dict) -> str:
        """
        Build complete search URL with parameters.
        
        Args:
            parameters: Dictionary of search parameters
            
        Returns:
            Complete LinkedIn job search URL
        """
        encoded_params = urlencode(parameters, quote_via=quote_plus)
        return f"{self.base_url}/jobs/search?{encoded_params}"
    
    async def _execute_intelligent_request(self, url: str) -> bool:
        """
        Execute HTTP request with intelligent retry logic and error handling.
        
        Args:
            url: Target URL for the request
            
        Returns:
            True if request was successful, False otherwise
        """
        if not self.http_client:
            await self._initialize_http_client()
        
        for attempt in range(self.config.max_retry_attempts):
            try:
                # Apply intelligent delay before request
                await self._apply_intelligent_delay()
                
                # Rotate headers periodically for stealth
                if (self.requests_made_in_session % 
                    self.config.user_agent_rotation_frequency == 0):
                    self.http_client.headers.update(
                        self.anti_detection_system.get_stealth_headers()
                    )
                
                # Execute the HTTP request
                response = await self.http_client.get(url)
                self.requests_made_in_session += 1
                
                # Handle different response status codes
                if response.status_code == 200:
                    await self._extract_jobs_from_html(response.text)
                    return True
                    
                elif response.status_code == 429:
                    # Rate limited - implement intelligent backoff
                    retry_after = int(response.headers.get('retry-after', 60))
                    backoff_time = retry_after + random.randint(15, 45)
                    logger.warning(f"Rate limited - waiting {backoff_time} seconds")
                    await asyncio.sleep(backoff_time)
                    
                elif response.status_code == 403:
                    logger.error("Access forbidden - implementing recovery strategy")
                    await self._implement_recovery_strategy()
                    return False
                    
                elif response.status_code in [404, 410]:
                    logger.warning(f"Resource not found (HTTP {response.status_code})")
                    return False
                    
                else:
                    logger.warning(f"HTTP {response.status_code} on attempt {attempt + 1}")
                    await asyncio.sleep(
                        self.config.exponential_backoff_base ** attempt
                    )
                    
            except httpx.TimeoutException:
                logger.warning(f"Request timeout on attempt {attempt + 1}")
                await asyncio.sleep(self.config.exponential_backoff_base ** attempt)
                
            except httpx.ConnectError:
                logger.warning(f"Connection error on attempt {attempt + 1}")
                await asyncio.sleep(self.config.exponential_backoff_base ** attempt)
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                await asyncio.sleep(self.config.exponential_backoff_base ** attempt)
        
        self.extraction_statistics['failed_requests'] += 1
        return False
    
    async def _apply_intelligent_delay(self):
        """
        Apply intelligent delays that mimic human behavior patterns.
        """
        current_time = time.time()
        
        # Ensure minimum interval between requests
        if self.last_request_timestamp > 0:
            time_since_last = current_time - self.last_request_timestamp
            min_interval = self.config.minimum_request_delay
            
            if time_since_last < min_interval:
                additional_wait = min_interval - time_since_last
                await asyncio.sleep(additional_wait)
        
        # Calculate base delay with human-like variance
        base_delay = random.uniform(
            self.config.minimum_request_delay,
            self.config.maximum_request_delay
        )
        
        # Apply human variance
        human_delay = self.behavior_simulator.generate_human_like_delay(
            base_delay, self.config.human_variance_factor
        )
        
        # Apply progressive delay based on session progress
        progressive_delay = self.behavior_simulator.calculate_progressive_delay(
            self.requests_made_in_session, human_delay
        )
        
        logger.debug(f"Applying intelligent delay: {progressive_delay:.2f} seconds")
        await asyncio.sleep(progressive_delay)
        
        self.last_request_timestamp = time.time()
    
    async def _take_human_like_break(self):
        """Take a human-like break between batches of requests."""
        break_duration = random.uniform(*self.config.break_duration_range)
        logger.info(f"Taking human-like break for {break_duration:.1f} seconds")
        await asyncio.sleep(break_duration)
    
    async def _implement_recovery_strategy(self):
        """
        Implement comprehensive recovery strategy for detection/blocking.
        """
        logger.info("Implementing comprehensive recovery strategy")
        
        # Complete session reset
        await self._reset_session_completely()
        
        # Extended cooling-off period
        cooldown_duration = random.uniform(180, 420)  # 3-7 minutes
        logger.info(f"Extended cooldown period: {cooldown_duration:.1f} seconds")
        await asyncio.sleep(cooldown_duration)
        
        # Reset request counter
        self.requests_made_in_session = 0
    
    async def _reset_session_completely(self):
        """
        Completely reset the session with new fingerprint and headers.
        """
        logger.info("Performing complete session reset")
        
        # Close existing client
        if self.http_client:
            await self.http_client.aclose()
        
        # Generate new anti-detection profile
        self.anti_detection_system = AdvancedAntiDetectionSystem(self.config)
        
        # Reinitialize HTTP client
        await self._initialize_http_client()
        
        # Reset session tracking
        self.requests_made_in_session = 0
        self.session_start_timestamp = time.time()
    
    async def _extract_jobs_from_html(self, html_content: str):
        """
        Extract job information from HTML content using advanced techniques.
        
        Args:
            html_content: Raw HTML content from LinkedIn job search page
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find job cards using multiple selector strategies
        job_cards = self._find_job_cards_with_fallbacks(soup)
        
        if not job_cards:
            logger.warning("No job cards found in HTML content")
            self.extraction_statistics['pages_with_no_jobs'] += 1
            return
        
        # Simulate realistic content reading time
        content_length = len(html_content)
        reading_time = self.behavior_simulator.calculate_realistic_reading_time(content_length)
        await asyncio.sleep(reading_time)
        
        # Extract data from each job card
        successful_extractions = 0
        failed_extractions = 0
        
        for job_card in job_cards:
            try:
                job_data = self._extract_comprehensive_job_data(job_card)
                if job_data and self._validate_job_data_quality(job_data):
                    self.harvested_jobs_data.append(job_data)
                    successful_extractions += 1
                    self.quality_metrics['extraction_quality'].append(
                        job_data.get('data_quality_score', 0)
                    )
                else:
                    failed_extractions += 1
            except Exception as e:
                failed_extractions += 1
                logger.debug(f"Error extracting job data: {str(e)}")
        
        # Update statistics
        self.extraction_statistics['successful_extractions'] += successful_extractions
        self.extraction_statistics['failed_extractions'] += failed_extractions
        
        logger.info(f"Extracted {successful_extractions} jobs, {failed_extractions} failed")
    
    def _find_job_cards_with_fallbacks(self, soup: BeautifulSoup) -> List:
        """
        Find job cards using multiple selector fallbacks.
        
        Args:
            soup: BeautifulSoup object of the page content
            
        Returns:
            List of job card elements
        """
        for selector in self.ADVANCED_SELECTORS['job_cards']:
            job_cards = soup.select(selector)
            if job_cards:
                logger.debug(f"Found {len(job_cards)} job cards using selector: {selector}")
                return job_cards
        
        logger.warning("No job cards found with any selector")
        return []
    
    def _extract_comprehensive_job_data(self, job_card) -> Optional[Dict]:
        """
        Extract comprehensive job data from a job card element.
        
        Args:
            job_card: BeautifulSoup element representing a job card
            
        Returns:
            Dictionary containing extracted job data or None if extraction fails
        """
        job_data = {}
        
        # Extract core job information
        job_data['title'] = self._extract_with_selector_fallbacks(
            job_card, self.ADVANCED_SELECTORS['job_title']
        )
        job_data['company'] = self._extract_with_selector_fallbacks(
            job_card, self.ADVANCED_SELECTORS['company_name']
        )
        job_data['location'] = self._extract_with_selector_fallbacks(
            job_card, self.ADVANCED_SELECTORS['job_location']
        )
        
        # Extract job URL with enhanced logic
        job_data['job_url'] = self._extract_job_url_enhanced(job_card)
        
        # Extract additional metadata
        job_data.update(self._extract_enhanced_metadata(job_card))
        
        # Add extraction metadata
        job_data.update({
            'harvested_at': datetime.now().isoformat(),
            'harvester_version': '3.0.0',
            'data_source_region': self.region,
            'extraction_method': 'advanced_fallback',
            'data_quality_score': self._calculate_data_quality_score(job_data)
        })
        
        return job_data if job_data.get('title') else None
    
    def _extract_with_selector_fallbacks(self, element, selectors: List[str]) -> Optional[str]:
        """
        Extract text using multiple CSS selector fallbacks.
        
        Args:
            element: BeautifulSoup element to search within
            selectors: List of CSS selectors to try
            
        Returns:
            Extracted and cleaned text or None if nothing found
        """
        for selector in selectors:
            try:
                found_element = element.select_one(selector)
                if found_element:
                    text = found_element.get_text(strip=True)
                    if text and len(text) >= 2:
                        return self._clean_extracted_text(text)
            except Exception:
                continue
        return None
    
    def _extract_job_url_enhanced(self, element) -> Optional[str]:
        """
        Extract job URL using enhanced logic and fallbacks.
        
        Args:
            element: BeautifulSoup element to search within
            
        Returns:
            Complete job URL or None if not found
        """
        url_selectors = [
            'a[href*="/jobs/view/"]',
            'h3 a[href]',
            '.job-title-link[href]',
            'a[data-entity-urn*="jobPosting"]',
            'a[href*="linkedin.com/jobs"]',
            '[data-job-id] a'
        ]
        
        for selector in url_selectors:
            try:
                link_element = element.select_one(selector)
                if link_element and link_element.get('href'):
                    href = link_element.get('href')
                    
                    # Handle relative URLs
                    if href.startswith('/'):
                        return f"{self.base_url}{href}"
                    elif href.startswith('http'):
                        return href
                    
            except Exception:
                continue
        
        return None
    
    def _extract_enhanced_metadata(self, element) -> Dict:
        """
        Extract enhanced metadata from job card.
        
        Args:
            element: BeautifulSoup element to extract from
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        
        # Extract posting date
        posting_date = self._extract_with_selector_fallbacks(
            element, self.ADVANCED_SELECTORS['posting_date']
        )
        if posting_date:
            # Try to extract datetime attribute first
            time_elem = element.find('time')
            if time_elem and time_elem.get('datetime'):
                metadata['posted_date'] = time_elem.get('datetime')
            else:
                metadata['posted_date'] = posting_date
        
        # Extract salary information
        if self.config.extract_salary_info:
            salary = self._extract_with_selector_fallbacks(
                element, self.ADVANCED_SELECTORS['salary_info']
            )
            if salary:
                metadata['salary_info'] = salary
        
        # Extract job insights
        if self.config.extract_job_insights:
            insights_elements = element.select('li.job-search-card__job-insight')
            if insights_elements:
                insights = [insight.get_text(strip=True) for insight in insights_elements]
                metadata['job_insights'] = [insight for insight in insights if insight]
        
        # Extract applicant count
        applicant_info = self._extract_with_selector_fallbacks(
            element, self.ADVANCED_SELECTORS['applicant_count']
        )
        if applicant_info and 'applicant' in applicant_info.lower():
            metadata['applicant_count'] = applicant_info
        
        return metadata
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common LinkedIn artifacts
        cleaned = re.sub(r'\b(new|hiring|actively recruiting)\s*$', '', cleaned, flags=re.IGNORECASE)
        
        # Remove emoji and special characters if needed
        if len(cleaned) > self.config.maximum_job_title_length:
            cleaned = cleaned[:self.config.maximum_job_title_length].strip()
        
        return cleaned
    
    def _validate_job_data_quality(self, job_data: Dict) -> bool:
        """
        Validate job data quality using comprehensive checks.
        
        Args:
            job_data: Dictionary containing job data
            
        Returns:
            True if data meets quality standards, False otherwise
        """
        # Basic validation
        if not job_data.get('title'):
            return False
        
        title = job_data['title'].strip()
        if (len(title) < self.config.minimum_job_title_length or 
            len(title) > self.config.maximum_job_title_length):
            return False
        
        # Spam detection
        if self.config.spam_detection_enabled:
            spam_indicators = [
                '🚀', '💰', '🔥', '💯', 'URGENT', 'IMMEDIATE', 'HURRY',
                'MAKE MONEY FAST', 'WORK FROM HOME GUARANTEED'
            ]
            title_upper = title.upper()
            if any(indicator in title_upper for indicator in spam_indicators):
                return False
        
        # Validate company name
        if job_data.get('company'):
            company = job_data['company'].strip()
            if len(company) < 2 or not re.search(r'[a-zA-Z]', company):
                job_data['company'] = None
        
        # Validate location
        if job_data.get('location'):
            location = job_data['location'].strip()
            if len(location) < 2 or not re.search(r'[a-zA-Z]', location):
                job_data['location'] = None
        
        return True
    
    def _calculate_data_quality_score(self, job_data: Dict) -> float:
        """
        Calculate a quality score for extracted job data.
        
        Args:
            job_data: Dictionary containing job data
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        total_fields = 6  # title, company, location, url, date, insights
        filled_fields = 0
        
        # Core fields
        if job_data.get('title'): filled_fields += 1
        if job_data.get('company'): filled_fields += 1
        if job_data.get('location'): filled_fields += 1
        if job_data.get('job_url'): filled_fields += 1
        if job_data.get('posted_date'): filled_fields += 1
        if job_data.get('job_insights'): filled_fields += 1
        
        base_score = filled_fields / total_fields
        
        # Bonus points for additional metadata
        bonus = 0.0
        if job_data.get('salary_info'): bonus += 0.1
        if job_data.get('applicant_count'): bonus += 0.05
        
        return min(1.0, base_score + bonus)
    
    def save_harvested_data_to_csv(self, filename: str = "linkedin_jobs_harvested.csv") -> bool:
        """
        Save harvested jobs to CSV file with comprehensive metadata.
        
        Args:
            filename: Name of the output CSV file
            
        Returns:
            True if save was successful, False otherwise
        """
        if not self.harvested_jobs_data:
            logger.warning("No harvested data to save")
            return False
        
        try:
            file_path = self.output_directory / filename
            
            # Define comprehensive fieldnames
            fieldnames = [
                'title', 'company', 'location', 'posted_date', 'job_url',
                'salary_info', 'applicant_count', 'job_insights',
                'harvested_at', 'harvester_version', 'data_source_region',
                'extraction_method', 'data_quality_score'
            ]
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for job in self.harvested_jobs_data:
                    # Handle list fields
                    job_copy = job.copy()
                    if isinstance(job_copy.get('job_insights'), list):
                        job_copy['job_insights'] = '; '.join(job_copy['job_insights'])
                    
                    # Filter to fieldnames only
                    filtered_job = {k: v for k, v in job_copy.items() if k in fieldnames}
                    writer.writerow(filtered_job)
            
            logger.info(f"Saved {len(self.harvested_jobs_data)} jobs to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving CSV: {str(e)}")
            return False
    
    def save_harvested_data_to_json(self, filename: str = "linkedin_jobs_harvested.json") -> bool:
        """
        Save harvested jobs to JSON file with comprehensive metadata.
        
        Args:
            filename: Name of the output JSON file
            
        Returns:
            True if save was successful, False otherwise
        """
        if not self.harvested_jobs_data:
            logger.warning("No harvested data to save")
            return False
        
        try:
            file_path = self.output_directory / filename
            
            # Create comprehensive output structure
            output_data = {
                'harvest_metadata': {
                    'harvester_version': '3.0.0',
                    'total_jobs_harvested': len(self.harvested_jobs_data),
                    'harvest_completed_at': datetime.now().isoformat(),
                    'target_region': self.region,
                    'domain_used': self.base_domain,
                    'extraction_statistics': dict(self.extraction_statistics),
                    'quality_summary': self._generate_quality_summary()
                },
                'harvested_jobs': self.harvested_jobs_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(self.harvested_jobs_data)} jobs to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving JSON: {str(e)}")
            return False
    
    def _generate_quality_summary(self) -> Dict:
        """
        Generate comprehensive quality summary of harvested data.
        
        Returns:
            Dictionary with quality metrics and statistics
        """
        if not self.harvested_jobs_data:
            return {}
        
        total_jobs = len(self.harvested_jobs_data)
        quality_scores = [job.get('data_quality_score', 0) for job in self.harvested_jobs_data]
        
        return {
            'average_quality_score': sum(quality_scores) / len(quality_scores),
            'high_quality_jobs': sum(1 for score in quality_scores if score >= 0.8),
            'medium_quality_jobs': sum(1 for score in quality_scores if 0.5 <= score < 0.8),
            'low_quality_jobs': sum(1 for score in quality_scores if score < 0.5),
            'completion_rates': {
                'title': sum(1 for job in self.harvested_jobs_data if job.get('title')) / total_jobs,
                'company': sum(1 for job in self.harvested_jobs_data if job.get('company')) / total_jobs,
                'location': sum(1 for job in self.harvested_jobs_data if job.get('location')) / total_jobs,
                'job_url': sum(1 for job in self.harvested_jobs_data if job.get('job_url')) / total_jobs,
                'salary_info': sum(1 for job in self.harvested_jobs_data if job.get('salary_info')) / total_jobs,
            }
        }
    
    def display_comprehensive_summary(self):
        """Display comprehensive summary of harvesting operation."""
        if not self.harvested_jobs_data:
            print("No harvested data available for summary")
            return
        
        total_jobs = len(self.harvested_jobs_data)
        quality_summary = self._generate_quality_summary()
        
        print("=" * 80)
        print("LinkedIn Job Harvester - Comprehensive Summary")
        print("=" * 80)
        
        print(f"Total jobs harvested: {total_jobs}")
        print(f"Target region: {self.region}")
        print(f"Average quality score: {quality_summary.get('average_quality_score', 0):.3f}")
        
        # Quality distribution
        print(f"\nQuality Distribution:")
        print(f"  High quality (≥0.8): {quality_summary.get('high_quality_jobs', 0)} "
              f"({quality_summary.get('high_quality_jobs', 0)/total_jobs*100:.1f}%)")
        print(f"  Medium quality (0.5-0.8): {quality_summary.get('medium_quality_jobs', 0)} "
              f"({quality_summary.get('medium_quality_jobs', 0)/total_jobs*100:.1f}%)")
        print(f"  Low quality (<0.5): {quality_summary.get('low_quality_jobs', 0)} "
              f"({quality_summary.get('low_quality_jobs', 0)/total_jobs*100:.1f}%)")
        
        # Field completion rates
        print(f"\nField Completion Rates:")
        completion_rates = quality_summary.get('completion_rates', {})
        for field, rate in completion_rates.items():
            print(f"  {field.title()}: {rate*100:.1f}%")
        
        # Top companies and locations
        companies = [job.get('company') for job in self.harvested_jobs_data if job.get('company')]
        if companies:
            print(f"\nTop 5 Companies:")
            for company, count in Counter(companies).most_common(5):
                print(f"  {company}: {count}")
        
        locations = [job.get('location') for job in self.harvested_jobs_data if job.get('location')]
        if locations:
            print(f"\nTop 5 Locations:")
            for location, count in Counter(locations).most_common(5):
                print(f"  {location}: {count}")
        
        # Extraction statistics
        if self.extraction_statistics:
            print(f"\nExtraction Statistics:")
            for stat, value in self.extraction_statistics.items():
                print(f"  {stat.replace('_', ' ').title()}: {value}")
        
        print("\n" + "=" * 80)


# Backward compatibility wrapper
class LinkedInJobScraper:
    """
    Backward compatibility wrapper for the enhanced job harvester.
    
    This class maintains the same interface as the previous scraper
    while using the new enhanced harvesting system underneath.
    """
    
    def __init__(self, output_dir: str = "data"):
        """
        Initialize the LinkedIn job scraper with backward compatibility.
        
        Args:
            output_dir: Directory for saving output files
        """
        self.output_dir = output_dir
        self.jobs_data = []
        self.harvester = None
    
    def search_jobs(self, keywords: str = "", location: str = "", max_pages: int = 5, 
                   delay_range: Tuple[float, float] = (3, 8), **kwargs) -> List[Dict]:
        """
        Search for jobs using the enhanced harvester (backward compatible).
        
        Args:
            keywords: Job search keywords
            location: Target location
            max_pages: Maximum pages to scrape
            delay_range: Delay range (maintained for compatibility)
            **kwargs: Additional search parameters
            
        Returns:
            List of job data dictionaries
        """
        return asyncio.run(self._async_search(keywords, location, max_pages, **kwargs))
    
    async def _async_search(self, keywords: str, location: str, max_pages: int, **kwargs) -> List[Dict]:
        """
        Async implementation of job search.
        
        Args:
            keywords: Job search keywords
            location: Target location
            max_pages: Maximum pages to scrape
            **kwargs: Additional search parameters
            
        Returns:
            List of job data dictionaries
        """
        # Create enhanced configuration
        config = HarvestingConfiguration(
            minimum_request_delay=3.0,
            maximum_request_delay=8.0,
            max_requests_per_session=75
        )
        
        # Use enhanced harvester
        async with EnhancedLinkedInJobHarvester(self.output_dir, config) as harvester:
            jobs = await harvester.harvest_jobs(keywords, location, max_pages, **kwargs)
            self.jobs_data = jobs
            self.harvester = harvester
            return jobs
    
    def save_to_csv(self, filename: str = "linkedin_jobs_2025.csv") -> bool:
        """Save jobs to CSV file."""
        if not self.jobs_data:
            return False
        
        harvester = EnhancedLinkedInJobHarvester(self.output_dir)
        harvester.harvested_jobs_data = self.jobs_data
        return harvester.save_harvested_data_to_csv(filename)
    
    def save_to_json(self, filename: str = "linkedin_jobs_2025.json") -> bool:
        """Save jobs to JSON file."""
        if not self.jobs_data:
            return False
        
        harvester = EnhancedLinkedInJobHarvester(self.output_dir)
        harvester.harvested_jobs_data = self.jobs_data
        return harvester.save_harvested_data_to_json(filename)
    
    def print_summary(self):
        """Print job harvesting summary."""
        if not self.jobs_data:
            print("No job data available")
            return
        
        harvester = EnhancedLinkedInJobHarvester(self.output_dir)
        harvester.harvested_jobs_data = self.jobs_data
        harvester.display_comprehensive_summary()


if __name__ == "__main__":
    async def test_enhanced_harvester():
        """Test the enhanced job harvester with multiple scenarios."""
        print("Testing Enhanced LinkedIn Job Harvester")
        
        # Test configuration
        config = HarvestingConfiguration(minimum_request_delay=2.0, maximum_request_delay=5.0)
        
        # Test with different regions and job types
        test_scenarios = [
            {"keywords": "software engineer", "location": "San Francisco", "region": "US"},
            {"keywords": "data scientist", "location": "London", "region": "UK"},
            {"keywords": "product manager", "location": "Toronto", "region": "CA"},
        ]
        
        for scenario in test_scenarios:
            print(f"\nTesting: {scenario}")
            
            async with EnhancedLinkedInJobHarvester(
                "test_output", config, scenario["region"]
            ) as harvester:
                jobs = await harvester.harvest_jobs(
                    scenario["keywords"], 
                    scenario["location"], 
                    max_pages=1
                )
                
                if jobs:
                    harvester.save_harvested_data_to_csv(
                        f"test_{scenario['region'].lower()}_jobs.csv"
                    )
                    harvester.save_harvested_data_to_json(
                        f"test_{scenario['region'].lower()}_jobs.json"
                    )
                    harvester.display_comprehensive_summary()
                else:
                    print("No jobs found")
    
    # Run the test
    asyncio.run(test_enhanced_harvester())