#!/usr/bin/env python3

import sys
import argparse
import signal
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.linkedin_scraper import LinkedInJobScraper
from utils.logger import get_scraper_logger
from utils.data_validator import JobDataValidator
from config import get_config


class ScraperManager:
    def __init__(self, config_file: Optional[str] = None):
        self.config = get_config(config_file)
        self.logger = get_scraper_logger("advanced")
        self.validator = JobDataValidator()
        self.scraper = None
        self.interrupted = False
        
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        self.interrupted = True
        self.logger.info("Interrupt signal received. Shutting down gracefully...")
        sys.exit(0)
    
    def run_interactive(self):
        print("🔍 LinkedIn Job Scraper - 2025 Edition")
        print("=" * 50)
        
        try:
            search_params = self._get_search_parameters()
            
            self._initialize_scraper()
            results = self._run_scraper(search_params)
            
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
        try:
            self.logger.info(f"Starting advanced scraper with arguments")
            
            search_params = {
                'keywords': args.keywords,
                'location': args.location,
                'max_pages': args.max_pages
            }
            
            self._initialize_scraper()
            results = self._run_scraper(search_params)
            
            if results:
                self._process_results(results)
                return True
            else:
                self._handle_no_results()
                return False
                
        except Exception as e:
            self.logger.error(f"Error running scraper: {str(e)}")
            return False
    
    def _show_scraper_info(self):
        print("\nUsing Advanced LinkedIn Scraper 2025:")
        print("• HTTPX with HTTP/2 support for superior performance")
        print("• Advanced anti-detection and behavioral simulation")
        print("• Intelligent rate limiting and session management")
        print("• AI-resistant fingerprinting techniques")
    
    def _get_search_parameters(self) -> dict:
        self._show_scraper_info()
        params = {}
        
        while True:
            keywords = input("\n📝 Enter job keywords (e.g., 'python developer'): ").strip()
            if keywords:
                params['keywords'] = keywords
                break
            print("Keywords are required. Please try again.")
        
        location = input("📍 Enter location (e.g., 'New York, NY') [optional]: ").strip()
        params['location'] = location
        
        max_pages_limit = self.config.scraping.max_pages_basic
        
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
        
        return params
    
    def _initialize_scraper(self):
        try:
            self.scraper = LinkedInJobScraper(
                output_dir=self.config.output.data_dir
            )
            
            self.logger.info("Advanced scraper initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize scraper: {str(e)}")
            raise
    
    def _run_scraper(self, params: dict) -> list:
        self.logger.info(f"Starting scrape: {params}")
        
        print(f"\n🚀 Starting advanced scrape:")
        print(f"   Keywords: {params['keywords']}")
        print(f"   Location: {params['location'] or 'Any'}")
        print(f"   Max pages: {params['max_pages']}")
        print("-" * 50)
        
        return self.scraper.search_jobs(**params)
    
    def _process_results(self, results: list):
        print(f"\n✅ Scraping completed! Found {len(results)} jobs.")
        
        print("🔍 Validating and cleaning data...")
        original_count = len(results)
        
        # Remove duplicates based on title + company
        seen = set()
        unique_results = []
        for job in results:
            signature = f"{job.get('title', '')}_{job.get('company', '')}"
            if signature not in seen:
                seen.add(signature)
                unique_results.append(job)
        
        removed_duplicates = original_count - len(unique_results)
        if removed_duplicates > 0:
            print(f"🔄 Removed {removed_duplicates} duplicate jobs")
            self.scraper.jobs_data = unique_results
        
        # Validate data
        valid_jobs = [job for job in unique_results if self.validator.is_valid_job(job)]
        invalid_count = len(unique_results) - len(valid_jobs)
        
        if invalid_count > 0:
            print(f"⚠️  Filtered out {invalid_count} invalid jobs")
            self.scraper.jobs_data = valid_jobs
        
        print(f"✨ Data validation complete. Final count: {len(valid_jobs)} jobs")
        
        # Save results
        csv_saved = self.scraper.save_to_csv()
        json_saved = self.scraper.save_to_json()
        
        if csv_saved and json_saved:
            print(f"\n💾 Files saved to '{self.config.output.data_dir}' directory:")
            print(f"   - linkedin_jobs_2025.csv")
            print(f"   - linkedin_jobs_2025.json")
        
        # Show summary
        self.scraper.print_summary()
        
        # Offer to open files
        self._offer_file_actions()
    
    def _handle_no_results(self):
        print("\n❌ No jobs found. This might be due to:")
        print("   • LinkedIn's anti-bot measures")
        print("   • Too restrictive search criteria")
        print("   • Network connectivity issues")
        print("   • Rate limiting")
        
        print("\n💡 Consider:")
        print("   • Using broader search terms")
        print("   • Checking your internet connection")
        print("   • Waiting a few minutes before trying again")
        print("   • The advanced scraper uses intelligent rate limiting")
    
    def _offer_file_actions(self):
        # Optional: Add functionality to open files or perform additional actions
        pass

def create_parser():
    parser = argparse.ArgumentParser(
        description='LinkedIn Job Scraper - Extract job listings from LinkedIn',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py -k "python developer" -l "San Francisco"
  python main.py --keywords "data scientist" --location "Remote" --max-pages 5
  python main.py -k "software engineer" -s selenium --headless false
  python main.py --interactive
        """
    )
    
    parser.add_argument('-k', '--keywords', type=str, required=False,
                        help='Job keywords to search for (required unless --interactive)')
    
    parser.add_argument('-l', '--location', type=str, default='',
                        help='Location to search in (optional)')
    
    parser.add_argument('-p', '--max-pages', type=int, default=3,
                        help='Maximum number of pages to scrape (default: 3)')
    
    
    parser.add_argument('-c', '--config', type=str,
                        help='Path to custom configuration file')
    
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Run in interactive mode')
    
    parser.add_argument('--version', action='version', version='LinkedIn Job Scraper 2025 Edition v3.0')
    
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        manager = ScraperManager(config_file=args.config)
        
        if args.interactive:
            manager.run_interactive()
        else:
            if not args.keywords:
                print("❌ Keywords are required when not in interactive mode.")
                print("Use --interactive for guided setup or provide --keywords")
                parser.print_help()
                return False
            
            success = manager.run_with_args(args)
            return success
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        return False
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 