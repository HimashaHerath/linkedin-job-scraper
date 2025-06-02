#!/usr/bin/env python3
"""
LinkedIn Job Scraper - Main Entry Point

A comprehensive LinkedIn job scraper with both basic (requests) and advanced (Selenium) options.
"""

import sys
import argparse
import signal
from pathlib import Path
from typing import Optional

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.linkedin_scraper import LinkedInJobScraper
from scrapers.linkedin_selenium_scraper import LinkedInSeleniumScraper
from utils.logger import get_scraper_logger
from utils.data_validator import JobDataValidator
from config import get_config


class ScraperManager:
    """Manages the LinkedIn job scraping process."""
    
    def __init__(self, scraper_type: str = "basic", config_file: Optional[str] = None):
        """
        Initialize the scraper manager.
        
        Args:
            scraper_type (str): Type of scraper ('basic' or 'selenium')
            config_file (str, optional): Path to config file
        """
        self.scraper_type = scraper_type
        self.config = get_config(config_file)
        self.logger = get_scraper_logger(scraper_type)
        self.validator = JobDataValidator()
        self.scraper = None
        self.interrupted = False
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully."""
        self.interrupted = True
        self.logger.info("Interrupt signal received. Shutting down gracefully...")
        if self.scraper and hasattr(self.scraper, 'close_driver'):
            self.scraper.close_driver()
        sys.exit(0)
    
    def run_interactive(self):
        """Run the scraper in interactive mode."""
        print("🔍 LinkedIn Job Scraper")
        print("=" * 50)
        
        try:
            # Get user preferences
            scraper_choice = self._get_scraper_choice()
            if scraper_choice != self.scraper_type:
                self.scraper_type = scraper_choice
                self.logger = get_scraper_logger(scraper_choice)
            
            # Get search parameters
            search_params = self._get_search_parameters()
            
            # Initialize and run scraper
            self._initialize_scraper()
            results = self._run_scraper(search_params)
            
            # Process and save results
            if results:
                self._process_results(results)
            else:
                self._handle_no_results()
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Scraping interrupted by user.")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            print(f"❌ An error occurred: {str(e)}")
    
    def run_with_args(self, args):
        """Run the scraper with command-line arguments."""
        try:
            self.logger.info(f"Starting {self.scraper_type} scraper with arguments")
            
            # Prepare search parameters
            search_params = {
                'keywords': args.keywords,
                'location': args.location,
                'max_pages': args.max_pages,
                'delay_range': self.config.get_delay_range(self.scraper_type)
            }
            
            # Add Selenium-specific parameters
            if self.scraper_type == "selenium":
                search_params['headless'] = args.headless
            
            # Initialize and run scraper
            self._initialize_scraper(args.headless if self.scraper_type == "selenium" else None)
            results = self._run_scraper(search_params)
            
            # Process results
            if results:
                self._process_results(results)
                return True
            else:
                self._handle_no_results()
                return False
                
        except Exception as e:
            self.logger.error(f"Error running scraper: {str(e)}")
            return False
    
    def _get_scraper_choice(self) -> str:
        """Get user's scraper choice."""
        print("\nAvailable scrapers:")
        print("1. Basic Scraper (requests + BeautifulSoup) - Fast, lightweight")
        print("2. Selenium Scraper (WebDriver) - More reliable, handles JavaScript")
        
        while True:
            choice = input("\nChoose scraper (1 or 2, default 1): ").strip()
            if choice == "2":
                return "selenium"
            elif choice == "1" or choice == "":
                return "basic"
            else:
                print("Please enter 1 or 2.")
    
    def _get_search_parameters(self) -> dict:
        """Get search parameters from user input."""
        params = {}
        
        # Required: Keywords
        while True:
            keywords = input("\n📝 Enter job keywords (e.g., 'python developer'): ").strip()
            if keywords:
                params['keywords'] = keywords
                break
            print("Keywords are required. Please try again.")
        
        # Optional: Location
        location = input("📍 Enter location (e.g., 'New York, NY') [optional]: ").strip()
        params['location'] = location
        
        # Max pages
        max_pages_limit = (self.config.scraping.max_pages_selenium 
                          if self.scraper_type == "selenium" 
                          else self.config.scraping.max_pages_basic)
        
        while True:
            try:
                max_pages = input(f"📄 Enter max pages to scrape (1-{max_pages_limit}, default 3): ").strip()
                max_pages = int(max_pages) if max_pages else 3
                if 1 <= max_pages <= max_pages_limit:
                    params['max_pages'] = max_pages
                    break
                else:
                    print(f"Please enter a number between 1 and {max_pages_limit}.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Selenium-specific options
        if self.scraper_type == "selenium":
            headless = input("🖥️  Run in headless mode? (y/n, default y): ").strip().lower()
            params['headless'] = headless != 'n'
        
        params['delay_range'] = self.config.get_delay_range(self.scraper_type)
        
        return params
    
    def _initialize_scraper(self, headless: Optional[bool] = None):
        """Initialize the appropriate scraper."""
        try:
            if self.scraper_type == "selenium":
                headless = headless if headless is not None else self.config.selenium.headless
                self.scraper = LinkedInSeleniumScraper(
                    headless=headless,
                    output_dir=self.config.output.data_dir
                )
            else:
                self.scraper = LinkedInJobScraper(
                    output_dir=self.config.output.data_dir
                )
            
            self.logger.info(f"{self.scraper_type.title()} scraper initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.scraper_type} scraper: {str(e)}")
            raise
    
    def _run_scraper(self, params: dict) -> list:
        """Run the scraper with given parameters."""
        self.logger.info(f"Starting scrape: {params}")
        
        print(f"\n🚀 Starting {self.scraper_type} scrape:")
        print(f"   Keywords: {params['keywords']}")
        print(f"   Location: {params['location'] or 'Any'}")
        print(f"   Max pages: {params['max_pages']}")
        if self.scraper_type == "selenium":
            print(f"   Headless: {params.get('headless', True)}")
        print("-" * 50)
        
        # Remove headless from params as search_jobs doesn't accept it
        scraper_params = params.copy()
        if 'headless' in scraper_params:
            del scraper_params['headless']
        
        return self.scraper.search_jobs(**scraper_params)
    
    def _process_results(self, results: list):
        """Process and save scraping results."""
        print(f"\n✅ Scraping completed! Found {len(results)} jobs.")
        
        # Validate and clean data if enabled
        if self.config.scraping.validate_data:
            print("🔍 Validating and cleaning data...")
            
            cleaned_results = []
            validation_errors = []
            
            for i, job in enumerate(results):
                cleaned_job = self.validator.clean_job_data(job)
                is_valid, errors = self.validator.validate_job_data(cleaned_job)
                
                if is_valid:
                    cleaned_results.append(cleaned_job)
                else:
                    validation_errors.extend([f"Job {i+1}: {error}" for error in errors])
            
            if validation_errors:
                self.logger.warning(f"Found {len(validation_errors)} validation errors")
                for error in validation_errors[:10]:  # Show first 10 errors
                    self.logger.warning(error)
            
            # Remove duplicates if enabled
            if self.config.scraping.remove_duplicates:
                original_count = len(cleaned_results)
                cleaned_results = self.validator.remove_duplicates(cleaned_results)
                removed_count = original_count - len(cleaned_results)
                if removed_count > 0:
                    print(f"🔄 Removed {removed_count} duplicate jobs")
            
            results = cleaned_results
            print(f"✨ Data validation complete. Final count: {len(results)} jobs")
        
        # Save results
        if results:
            saved_files = []
            
            if self.config.output.save_csv:
                csv_filename = f"{self.scraper_type}_{self.config.output.csv_filename}"
                if self.scraper.save_to_csv(csv_filename):
                    saved_files.append(csv_filename)
            
            if self.config.output.save_json:
                json_filename = f"{self.scraper_type}_{self.config.output.json_filename}"
                if self.scraper.save_to_json(json_filename):
                    saved_files.append(json_filename)
            
            if saved_files:
                print(f"\n💾 Files saved to '{self.config.output.data_dir}/' directory:")
                for filename in saved_files:
                    print(f"   - {filename}")
            
            # Print summary
            self.scraper.print_summary()
        
        return results
    
    def _handle_no_results(self):
        """Handle the case when no results are found."""
        print("\n❌ No jobs found. This might be due to:")
        print("   • LinkedIn's anti-bot measures")
        print("   • Too restrictive search criteria")
        print("   • Network connectivity issues")
        print("   • Rate limiting")
        
        print("\n💡 Consider:")
        print("   • Using broader search terms")
        if self.scraper_type == "basic":
            print("   • Trying the Selenium version for better results")
        print("   • Checking your internet connection")
        print("   • Waiting a few minutes before trying again")


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="LinkedIn Job Scraper - Extract job listings from LinkedIn",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --keywords "python developer" --location "San Francisco, CA"
  %(prog)s --keywords "data scientist" --max-pages 5 --scraper selenium
  %(prog)s --keywords "software engineer" --headless false --config custom.json
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--keywords', '-k',
        required=True,
        help='Job keywords to search for (e.g., "python developer")'
    )
    
    # Optional arguments
    parser.add_argument(
        '--location', '-l',
        default='',
        help='Location to search in (e.g., "New York, NY")'
    )
    
    parser.add_argument(
        '--max-pages', '-p',
        type=int,
        default=3,
        help='Maximum number of pages to scrape (default: 3)'
    )
    
    parser.add_argument(
        '--scraper', '-s',
        choices=['basic', 'selenium'],
        default='basic',
        help='Scraper type to use (default: basic)'
    )
    
    parser.add_argument(
        '--headless',
        type=bool,
        default=True,
        help='Run Selenium in headless mode (default: True)'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode (ignore other arguments)'
    )
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Create scraper manager
        manager = ScraperManager(
            scraper_type=args.scraper,
            config_file=args.config
        )
        
        # Run in interactive or command-line mode
        if args.interactive or len(sys.argv) == 1:
            manager.run_interactive()
        else:
            success = manager.run_with_args(args)
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 