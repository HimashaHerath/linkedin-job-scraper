"""
Enhanced configuration module for LinkedIn Job Scraper
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json


@dataclass
class ScrapingConfig:
    """Configuration for scraping behavior."""
    # Rate limiting
    delay_min: float = 2.0
    delay_max: float = 5.0
    selenium_delay_min: float = 3.0
    selenium_delay_max: float = 6.0
    
    # Request settings
    max_retries: int = 3
    timeout: int = 30
    
    # Page limits
    max_pages_basic: int = 10
    max_pages_selenium: int = 5
    
    # Data quality
    min_title_length: int = 3
    max_title_length: int = 200
    min_company_length: int = 2
    max_company_length: int = 150
    
    # Output settings
    remove_duplicates: bool = True
    validate_data: bool = True


@dataclass
class LinkedInConfig:
    """LinkedIn-specific configuration."""
    base_url: str = "https://www.linkedin.com"
    jobs_search_url: str = "https://www.linkedin.com/jobs/search"
    
    # CSS Selectors (with fallbacks)
    job_card_selectors: List[str] = field(default_factory=lambda: [
        'div.job-search-card',
        'div.base-card',
        'li.job-result-card',
        'div.jobs-search-results__list-item',
        'div[data-entity-urn*="jobPosting"]',
        'li[data-occludable-job-id]'
    ])
    
    title_selectors: List[str] = field(default_factory=lambda: [
        'h3 a', 'h3', '.job-title-link', 'a[data-cy="job-title"]',
        '.job-search-card__title a', '.base-search-card__title a'
    ])
    
    company_selectors: List[str] = field(default_factory=lambda: [
        'h4 a', 'h4', '.job-search-card__subtitle-link',
        'a[data-cy="job-company-name"]', '.base-search-card__subtitle a'
    ])
    
    location_selectors: List[str] = field(default_factory=lambda: [
        '.job-search-card__location', '[data-cy="job-location"]',
        '.job-result-card__location', '.base-search-card__metadata'
    ])
    
    url_selectors: List[str] = field(default_factory=lambda: [
        'a[href*="/jobs/view/"]', 'h3 a', '.job-title-link'
    ])
    
    summary_selectors: List[str] = field(default_factory=lambda: [
        '.job-search-card__snippet', '.job-result-card__snippet',
        '.base-search-card__metadata', 'p[data-cy="job-snippet"]'
    ])
    
    # Search form selectors
    keywords_search_selectors: List[str] = field(default_factory=lambda: [
        "input[aria-label*='Search job titles']",
        "input[aria-label*='Search jobs']",
        "input[placeholder*='Search job titles']",
        ".jobs-search-box__text-input[aria-label*='Search']"
    ])
    
    location_search_selectors: List[str] = field(default_factory=lambda: [
        "input[aria-label*='Search job locations']",
        "input[aria-label*='Search locations']",
        "input[placeholder*='Search job locations']",
        ".jobs-search-box__text-input[aria-label*='Location']"
    ])
    
    search_button_selectors: List[str] = field(default_factory=lambda: [
        "button[aria-label='Search']",
        "button[aria-label*='Search']",
        ".jobs-search-box__submit-button",
        "button[type='submit']"
    ])
    
    # Pagination selectors
    next_button_selectors: List[str] = field(default_factory=lambda: [
        "button[aria-label='Next']",
        "button[aria-label*='Next']",
        ".jobs-search-results-list__pagination button:last-child",
        "button[data-cy='page-next']"
    ])


@dataclass
class SeleniumConfig:
    """Selenium WebDriver configuration."""
    # Browser options
    headless: bool = True
    window_width: int = 1920
    window_height: int = 1080
    
    # Anti-detection options
    disable_images: bool = True
    disable_javascript: bool = False  # LinkedIn needs JS
    disable_extensions: bool = True
    disable_plugins: bool = True
    
    # Performance options
    page_load_timeout: int = 30
    implicit_wait: int = 10
    explicit_wait_timeout: int = 20
    
    # Chrome-specific options
    no_sandbox: bool = True
    disable_dev_shm: bool = True
    disable_gpu: bool = True
    
    # User agent rotation
    rotate_user_agent: bool = True


@dataclass
class OutputConfig:
    """Output and file configuration."""
    # Directories
    data_dir: str = "data"
    logs_dir: str = "logs"
    
    # File formats
    save_csv: bool = True
    save_json: bool = True
    csv_filename: str = "linkedin_jobs.csv"
    json_filename: str = "linkedin_jobs.json"
    
    # CSV options
    csv_encoding: str = "utf-8"
    csv_index: bool = False
    
    # JSON options
    json_indent: int = 2
    json_ensure_ascii: bool = False
    
    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    log_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5


@dataclass
class FilterConfig:
    """Job filtering configuration."""
    # LinkedIn filter codes
    experience_levels: Dict[str, str] = field(default_factory=lambda: {
        "internship": "1",
        "entry_level": "2",
        "associate": "3",
        "mid_senior": "4",
        "director": "5",
        "executive": "6"
    })
    
    job_types: Dict[str, str] = field(default_factory=lambda: {
        "full_time": "F",
        "part_time": "P",
        "contract": "C",
        "temporary": "T",
        "volunteer": "V",
        "internship": "I",
        "other": "O"
    })
    
    date_posted: Dict[str, str] = field(default_factory=lambda: {
        "any_time": "",
        "past_24_hours": "r86400",
        "past_week": "r604800",
        "past_month": "r2592000"
    })
    
    # Remote work options
    remote_options: Dict[str, str] = field(default_factory=lambda: {
        "on_site": "1",
        "remote": "2",
        "hybrid": "3"
    })


class Config:
    """Main configuration class that combines all config sections."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file (str, optional): Path to custom config file
        """
        self.scraping = ScrapingConfig()
        self.linkedin = LinkedInConfig()
        self.selenium = SeleniumConfig()
        self.output = OutputConfig()
        self.filters = FilterConfig()
        
        # Load custom configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
        
        # Load from environment variables
        self.load_from_env()
        
        # Ensure output directories exist
        self._create_directories()
    
    def load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Update configuration sections
            for section_name, section_data in config_data.items():
                if hasattr(self, section_name):
                    section = getattr(self, section_name)
                    for key, value in section_data.items():
                        if hasattr(section, key):
                            setattr(section, key, value)
                            
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Scraping settings
        self.scraping.delay_min = float(os.getenv('SCRAPER_DELAY_MIN', self.scraping.delay_min))
        self.scraping.delay_max = float(os.getenv('SCRAPER_DELAY_MAX', self.scraping.delay_max))
        self.scraping.max_retries = int(os.getenv('SCRAPER_MAX_RETRIES', self.scraping.max_retries))
        self.scraping.timeout = int(os.getenv('SCRAPER_TIMEOUT', self.scraping.timeout))
        
        # Selenium settings
        self.selenium.headless = os.getenv('SELENIUM_HEADLESS', 'true').lower() == 'true'
        self.selenium.window_width = int(os.getenv('SELENIUM_WIDTH', self.selenium.window_width))
        self.selenium.window_height = int(os.getenv('SELENIUM_HEIGHT', self.selenium.window_height))
        
        # Output settings
        self.output.data_dir = os.getenv('DATA_DIR', self.output.data_dir)
        self.output.logs_dir = os.getenv('LOGS_DIR', self.output.logs_dir)
        self.output.log_level = os.getenv('LOG_LEVEL', self.output.log_level)
    
    def _create_directories(self) -> None:
        """Create necessary directories."""
        Path(self.output.data_dir).mkdir(exist_ok=True)
        Path(self.output.logs_dir).mkdir(exist_ok=True)
    
    def get_delay_range(self, scraper_type: str = "basic") -> tuple:
        """Get delay range for specified scraper type."""
        if scraper_type == "selenium":
            return (self.scraping.selenium_delay_min, self.scraping.selenium_delay_max)
        else:
            return (self.scraping.delay_min, self.scraping.delay_max)
    
    def get_user_agent_list(self) -> List[str]:
        """Get list of user agents for rotation."""
        return [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
        ]
    
    def get_chrome_options(self) -> List[str]:
        """Get Chrome options for Selenium."""
        options = []
        
        if self.selenium.headless:
            options.append("--headless=new")
        
        options.extend([
            f"--window-size={self.selenium.window_width},{self.selenium.window_height}",
            "--start-maximized"
        ])
        
        if self.selenium.no_sandbox:
            options.append("--no-sandbox")
        
        if self.selenium.disable_dev_shm:
            options.append("--disable-dev-shm-usage")
        
        if self.selenium.disable_gpu:
            options.append("--disable-gpu")
        
        if self.selenium.disable_images:
            options.append("--disable-images")
        
        if self.selenium.disable_extensions:
            options.append("--disable-extensions")
        
        if self.selenium.disable_plugins:
            options.append("--disable-plugins")
        
        # Anti-detection options
        options.extend([
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--disable-default-apps",
            "--disable-features=TranslateUI",
            "--disable-ipc-flooding-protection",
            "--memory-pressure-off",
            "--max_old_space_size=4096"
        ])
        
        return options
    
    def get_chrome_prefs(self) -> Dict[str, Any]:
        """Get Chrome preferences for Selenium."""
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "media_stream": 2,
            }
        }
        
        if self.selenium.disable_images:
            prefs["profile.managed_default_content_settings"] = {"images": 2}
        
        return prefs
    
    def save_to_file(self, config_file: str) -> None:
        """Save current configuration to JSON file."""
        config_data = {
            "scraping": {
                "delay_min": self.scraping.delay_min,
                "delay_max": self.scraping.delay_max,
                "selenium_delay_min": self.scraping.selenium_delay_min,
                "selenium_delay_max": self.scraping.selenium_delay_max,
                "max_retries": self.scraping.max_retries,
                "timeout": self.scraping.timeout,
                "max_pages_basic": self.scraping.max_pages_basic,
                "max_pages_selenium": self.scraping.max_pages_selenium,
                "remove_duplicates": self.scraping.remove_duplicates,
                "validate_data": self.scraping.validate_data
            },
            "selenium": {
                "headless": self.selenium.headless,
                "window_width": self.selenium.window_width,
                "window_height": self.selenium.window_height,
                "disable_images": self.selenium.disable_images,
                "page_load_timeout": self.selenium.page_load_timeout,
                "implicit_wait": self.selenium.implicit_wait
            },
            "output": {
                "data_dir": self.output.data_dir,
                "logs_dir": self.output.logs_dir,
                "save_csv": self.output.save_csv,
                "save_json": self.output.save_json,
                "csv_filename": self.output.csv_filename,
                "json_filename": self.output.json_filename,
                "log_level": self.output.log_level,
                "log_to_file": self.output.log_to_file,
                "log_to_console": self.output.log_to_console
            }
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")


# Default configuration instance
default_config = Config()


def get_config(config_file: Optional[str] = None) -> Config:
    """
    Get configuration instance.
    
    Args:
        config_file (str, optional): Path to custom config file
        
    Returns:
        Config: Configuration instance
    """
    if config_file:
        return Config(config_file)
    return default_config 