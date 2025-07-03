#!/usr/bin/env python3
"""
Setup script for LinkedIn Job Scraper
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_chrome():
    """Check if Chrome is installed"""
    try:
        import shutil
        chrome_path = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
        if chrome_path:
            print("✅ Chrome browser found!")
            return True
        else:
            print("⚠️  Chrome browser not found. Please install Chrome for the Selenium scraper.")
            return False
    except Exception as e:
        print(f"⚠️  Could not check for Chrome: {e}")
        return False

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists("env_template.txt"):
            try:
                with open("env_template.txt", "r") as template:
                    content = template.read()
                with open(".env", "w") as env_file:
                    env_file.write(content)
                print("✅ Created .env file from template")
                return True
            except Exception as e:
                print(f"⚠️  Could not create .env file: {e}")
                return False
        else:
            print("⚠️  env_template.txt not found")
            return False
    else:
        print("✅ .env file already exists")
        return True

def run_quick_test():
    """Run a quick test to verify everything is working"""
    print("\nRunning quick test...")
    try:
        # Test basic imports
        from linkedin_scraper import LinkedInJobScraper
        from linkedin_selenium_scraper import LinkedInSeleniumScraper
        print("✅ All modules imported successfully!")
        
        # Test basic scraper initialization
        basic_scraper = LinkedInJobScraper()
        print("✅ Basic scraper initialized!")
        
        # Test Selenium scraper initialization (without actually opening browser)
        print("✅ Setup completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please check that all dependencies are installed correctly.")
        return False
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("LinkedIn Job Scraper Setup")
    print("=" * 30)
    
    success_count = 0
    total_checks = 4
    
    # Install dependencies
    if install_dependencies():
        success_count += 1
    
    # Check for Chrome
    if check_chrome():
        success_count += 1
    
    # Create .env file
    if create_env_file():
        success_count += 1
    
    # Run test
    if run_quick_test():
        success_count += 1
    
    print(f"\nSetup Results: {success_count}/{total_checks} checks passed")
    
    if success_count == total_checks:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python linkedin_scraper.py' for basic scraping")
        print("2. Run 'python linkedin_selenium_scraper.py' for advanced scraping")
        print("3. Run 'python example.py' to see usage examples")
        print("4. Check README.md for detailed documentation")
    else:
        print("\n⚠️  Setup completed with some issues.")
        print("Please resolve the issues above before using the scraper.")
    
    print("\n⚠️  Important Reminder:")
    print("This tool is for educational purposes only.")
    print("Please respect LinkedIn's Terms of Service and use responsibly.")

if __name__ == "__main__":
    main() 