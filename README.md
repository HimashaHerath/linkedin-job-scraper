# LinkedIn Job Scraper

A comprehensive Python-based LinkedIn job scraper that can extract job listings using two different approaches: requests/BeautifulSoup for basic scraping and Selenium for more robust scraping with JavaScript support.

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## ⚠️ Important Legal Notice

**Please read this carefully before using this scraper:**

1. **Respect LinkedIn's Terms of Service**: This scraper is for educational purposes only. LinkedIn's Terms of Service prohibit automated scraping of their platform.

2. **Use Responsibly**: Always implement proper rate limiting and respect the website's resources. Excessive scraping can impact server performance and may result in IP blocking.

3. **Consider Alternatives**: LinkedIn offers an official API for legitimate business use cases. Consider using the LinkedIn API instead: https://developer.linkedin.com/

4. **Legal Compliance**: Ensure your use of this scraper complies with applicable laws and regulations in your jurisdiction, including data protection laws like GDPR.

## 🚀 Features

- **Two Scraping Methods**: 
  - ✅ Basic HTTP requests with BeautifulSoup (Recommended - Working)
  - ⚠️ Advanced Selenium WebDriver for JavaScript-heavy pages (Limited due to anti-bot measures)
- **Comprehensive Data Extraction**: Job title, company, location, posting date, job URL, and summary
- **Rate Limiting**: Built-in delays to avoid overwhelming the server
- **Anti-Detection Measures**: Random user agents, headers, and delays
- **Multiple Output Formats**: Save results as CSV or JSON
- **Data Validation**: Built-in validation and cleaning of scraped data
- **Error Handling**: Robust error handling and retry mechanisms
- **Configurable**: Easy-to-modify configuration file
- **Command Line Interface**: Easy-to-use CLI with multiple options
- **Interactive Mode**: User-friendly interactive prompts

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- Chrome browser (for Selenium scraper - optional)

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd linkedin-job-scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment (optional):**
   ```bash
   cp env_template.txt .env
   # Edit .env file with your preferences
   ```

### Chrome WebDriver (Optional - for Selenium)

The Selenium scraper uses `webdriver-manager` to automatically download and manage ChromeDriver, so no manual installation is required. However, note that LinkedIn's anti-bot measures make the basic scraper more reliable.

## 🛠️ Usage

### Quick Start

**Basic scraper (Recommended):**
```bash
python main.py -k "python developer" -l "San Francisco, CA" -p 3
```

**With more options:**
```bash
python main.py --keywords "data scientist" --location "New York, NY" --max-pages 5 --scraper basic
```

### Command Line Options

```bash
python main.py --help
```

Available options:
- `-k, --keywords`: Job keywords to search for (required)
- `-l, --location`: Location to search in (optional)
- `-p, --max-pages`: Maximum number of pages to scrape (default: 3)
- `-s, --scraper`: Scraper type (`basic` or `selenium`, default: `basic`)
- `--headless`: Run Selenium in headless mode (default: true)
- `-c, --config`: Path to custom configuration file
- `-i, --interactive`: Run in interactive mode

### Interactive Mode

For a guided experience:
```bash
python main.py --interactive
```

### Programmatic Usage

```python
from src.scrapers.linkedin_scraper import LinkedInJobScraper

# Initialize scraper
scraper = LinkedInJobScraper()

# Search for jobs
jobs = scraper.search_jobs(
    keywords="python developer",
    location="San Francisco, CA",
    max_pages=5
)

# Save results
scraper.save_to_csv("my_jobs.csv")
scraper.save_to_json("my_jobs.json")
```

## 📊 Output Formats

### CSV Output
- Easy to open in Excel or Google Sheets
- Columns: title, company, location, posted_date, job_url, summary, scraped_at

### JSON Output
- Structured data format
- Includes all extracted information
- Easy to process programmatically

### Sample Output

```json
{
  "title": "Senior Python Developer",
  "company": "Tech Company Inc.",
  "location": "San Francisco, CA",
  "posted_date": "2024-01-15",
  "job_url": "https://www.linkedin.com/jobs/view/123456789",
  "summary": "We are looking for an experienced Python developer...",
  "scraped_at": "2024-01-16T10:30:00"
}
```

## ⚙️ Configuration

The scraper uses a comprehensive configuration system. Modify `src/config.py` to customize:

- **Search parameters**: Default keywords, location, max pages
- **Timing**: Delay ranges between requests
- **Output**: Default filenames and formats
- **Selenium**: Headless mode, window size
- **CSS Selectors**: Update if LinkedIn changes their HTML structure

## 🔧 Project Structure

```
linkedin-job-scraper/
├── main.py                 # Main entry point
├── src/
│   ├── config.py          # Configuration management
│   ├── scrapers/          # Scraper implementations
│   └── utils/             # Utility functions
├── data/                  # Output directory
├── logs/                  # Log files
├── tests/                 # Test suite
├── docs/                  # Documentation
├── drivers/               # WebDriver files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚨 Current Status & Troubleshooting

### Known Issues

1. **Selenium Scraper Limitations**: 
   - LinkedIn has implemented strong anti-bot measures
   - The basic scraper is currently more reliable
   - Selenium scraper may fail due to CAPTCHA or detection

2. **Basic Scraper Status**: ✅ Working reliably

### Common Issues

1. **No jobs found**: 
   - LinkedIn may be blocking requests
   - Use the basic scraper instead of Selenium
   - Try broader search terms
   - Check your internet connection

2. **Rate limiting**:
   - Increase delay ranges in config
   - Reduce the number of pages scraped
   - Take breaks between scraping sessions

3. **Data validation warnings**:
   - Some job listings may have incomplete data
   - The scraper automatically filters out invalid entries

### Debug Mode

For debugging, you can:
1. Check log files in the `logs/` directory
2. Run with verbose output
3. Use interactive mode for step-by-step execution

## 📈 Best Practices

1. **Start Small**: Begin with 1-2 pages to test
2. **Use Basic Scraper**: Currently more reliable than Selenium
3. **Monitor Usage**: Be aware of how much you're scraping
4. **Respect Rate Limits**: Don't overwhelm the servers
5. **Regular Breaks**: Take breaks between scraping sessions
6. **Keep Updated**: LinkedIn may change their structure

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Test the scraper manually:
```bash
# Quick test with basic scraper
python main.py -k "software engineer" -l "Remote" -p 1

# Interactive test
python main.py --interactive
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Clone the repo
git clone <repository-url>
cd linkedin-job-scraper

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Test the scraper
python main.py -k "test job" -p 1
```

## 📝 Recent Updates

- ✅ **Working Status**: Basic scraper tested and functional
- 🔧 **Improved CLI**: Enhanced command-line interface with better options
- 📊 **Data Validation**: Added comprehensive data validation and cleaning
- 🗂️ **Better Structure**: Organized code into proper modules
- 📋 **Enhanced Logging**: Detailed logging for debugging and monitoring
- 🎯 **Rate Limiting**: Improved rate limiting to avoid detection

## 🔗 Resources

- [LinkedIn Developer API](https://developer.linkedin.com/) (Official Alternative)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Web Scraping Ethics](https://blog.apify.com/is-web-scraping-legal/)

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Look at log files in the `logs/` directory
3. Ensure all dependencies are installed correctly
4. Try the basic scraper if Selenium fails
5. Open an issue on GitHub with detailed error information

## 📄 License

This project is for educational purposes only. Please ensure compliance with all applicable laws and terms of service before use.

---

**Note**: This scraper is primarily educational. For production use cases, consider LinkedIn's official API or other legitimate job search APIs. 