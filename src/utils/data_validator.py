from typing import Dict, List, Optional, Set
import re
from urllib.parse import urlparse
import pandas as pd
from datetime import datetime, timedelta


class JobDataValidator:
    """
    Validates and cleans job data to ensure quality and consistency.
    """
    
    def __init__(self):
        self.required_fields = {'title', 'company'}
        self.optional_fields = {'location', 'posted_date', 'job_url', 'summary', 'scraped_at', 'source'}
        self.valid_domains = {'linkedin.com', 'www.linkedin.com'}
        
        # Patterns for cleaning and validation
        self.company_noise_patterns = [
            r'\s*\(.*?\)\s*$',  # Remove parenthetical info at end
            r'\s*-\s*hiring\s*now\s*$',  # Remove "- hiring now"
            r'\s*\|\s*.*$',  # Remove everything after |
        ]
        
        self.location_patterns = [
            r'^([^,]+),?\s*([A-Z]{2}).*$',  # Extract city, state
            r'^([^,]+),?\s*([A-Za-z\s]+)$',  # Extract city, country/region
        ]
    
    def is_valid_job(self, job_data: Dict) -> bool:
        """
        Simple validation method that returns True if job has basic required fields.
        
        Args:
            job_data (Dict): Job data to validate
            
        Returns:
            bool: True if job is valid, False otherwise
        """
        if not job_data.get('title'):
            return False
        
        title = str(job_data['title']).strip()
        if len(title) < 3 or not re.search(r'[a-zA-Z]', title):
            return False
        
        return True
    
    def validate_job_data(self, job_data: Dict) -> tuple[bool, List[str]]:
        """
        Validate a single job data dictionary.
        
        Args:
            job_data (Dict): Job data to validate
            
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in job_data or not job_data[field] or job_data[field] == "N/A":
                errors.append(f"Missing or empty required field: {field}")
        
        # Validate job title
        if 'title' in job_data:
            title_errors = self._validate_title(job_data['title'])
            errors.extend(title_errors)
        
        # Validate company name
        if 'company' in job_data:
            company_errors = self._validate_company(job_data['company'])
            errors.extend(company_errors)
        
        # Validate job URL
        if 'job_url' in job_data and job_data['job_url'] != "N/A":
            url_errors = self._validate_url(job_data['job_url'])
            errors.extend(url_errors)
        
        # Validate location
        if 'location' in job_data and job_data['location'] != "N/A":
            location_errors = self._validate_location(job_data['location'])
            errors.extend(location_errors)
        
        # Validate posted date
        if 'posted_date' in job_data and job_data['posted_date'] != "N/A":
            date_errors = self._validate_posted_date(job_data['posted_date'])
            errors.extend(date_errors)
        
        return len(errors) == 0, errors
    
    def _validate_title(self, title: str) -> List[str]:
        """Validate job title."""
        errors = []
        
        if not isinstance(title, str):
            errors.append("Title must be a string")
            return errors
        
        title = title.strip()
        
        if len(title) < 3:
            errors.append("Title too short (minimum 3 characters)")
        
        if len(title) > 200:
            errors.append("Title too long (maximum 200 characters)")
        
        # Check for suspicious patterns
        if re.search(r'^[^a-zA-Z]*$', title):
            errors.append("Title contains no letters")
        
        return errors
    
    def _validate_company(self, company: str) -> List[str]:
        """Validate company name."""
        errors = []
        
        if not isinstance(company, str):
            errors.append("Company must be a string")
            return errors
        
        company = company.strip()
        
        if len(company) < 2:
            errors.append("Company name too short (minimum 2 characters)")
        
        if len(company) > 150:
            errors.append("Company name too long (maximum 150 characters)")
        
        return errors
    
    def _validate_url(self, url: str) -> List[str]:
        """Validate job URL."""
        errors = []
        
        if not isinstance(url, str):
            errors.append("URL must be a string")
            return errors
        
        try:
            parsed = urlparse(url)
            
            if not parsed.scheme in ['http', 'https']:
                errors.append("URL must use HTTP or HTTPS scheme")
            
            if not parsed.netloc:
                errors.append("URL missing domain")
            
            # Check if it's a LinkedIn URL
            domain = parsed.netloc.lower()
            if not any(valid_domain in domain for valid_domain in self.valid_domains):
                errors.append(f"URL not from LinkedIn: {domain}")
            
            # Check for job ID pattern
            if '/jobs/view/' not in url:
                errors.append("URL doesn't appear to be a LinkedIn job posting")
                
        except Exception as e:
            errors.append(f"Invalid URL format: {str(e)}")
        
        return errors
    
    def _validate_location(self, location: str) -> List[str]:
        """Validate location string."""
        errors = []
        
        if not isinstance(location, str):
            errors.append("Location must be a string")
            return errors
        
        location = location.strip()
        
        if len(location) < 2:
            errors.append("Location too short (minimum 2 characters)")
        
        if len(location) > 100:
            errors.append("Location too long (maximum 100 characters)")
        
        return errors
    
    def _validate_posted_date(self, posted_date: str) -> List[str]:
        """Validate posted date."""
        errors = []
        
        if not isinstance(posted_date, str):
            errors.append("Posted date must be a string")
            return errors
        
        # Try to parse various date formats
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%fZ',
        ]
        
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(posted_date, fmt)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            # Try relative dates (e.g., "2 days ago")
            if not re.search(r'\b(day|week|month|year|hour|minute)s?\s+ago\b', posted_date.lower()):
                errors.append(f"Unable to parse posted date: {posted_date}")
        else:
            # Check if date is reasonable (not in future, not too old)
            now = datetime.now()
            if parsed_date > now:
                errors.append("Posted date is in the future")
            elif parsed_date < now - timedelta(days=365):
                errors.append("Posted date is more than a year old")
        
        return errors
    
    def clean_job_data(self, job_data: Dict) -> Dict:
        """
        Clean and normalize job data.
        
        Args:
            job_data (Dict): Raw job data
            
        Returns:
            Dict: Cleaned job data
        """
        cleaned = job_data.copy()
        
        # Clean title
        if 'title' in cleaned and cleaned['title'] != "N/A":
            cleaned['title'] = self._clean_title(cleaned['title'])
        
        # Clean company
        if 'company' in cleaned and cleaned['company'] != "N/A":
            cleaned['company'] = self._clean_company(cleaned['company'])
        
        # Clean location
        if 'location' in cleaned and cleaned['location'] != "N/A":
            cleaned['location'] = self._clean_location(cleaned['location'])
        
        # Clean summary
        if 'summary' in cleaned and cleaned['summary'] != "N/A":
            cleaned['summary'] = self._clean_summary(cleaned['summary'])
        
        # Ensure consistent URL format
        if 'job_url' in cleaned and cleaned['job_url'] != "N/A":
            cleaned['job_url'] = self._clean_url(cleaned['job_url'])
        
        return cleaned
    
    def _clean_title(self, title: str) -> str:
        """Clean job title."""
        if not isinstance(title, str):
            return "N/A"
        
        # Remove excessive whitespace
        title = re.sub(r'\s+', ' ', title.strip())
        
        # Remove common noise
        title = re.sub(r'\s*\(\s*remote\s*\)\s*$', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*-\s*remote\s*$', '', title, flags=re.IGNORECASE)
        
        return title.strip()
    
    def _clean_company(self, company: str) -> str:
        """Clean company name."""
        if not isinstance(company, str):
            return "N/A"
        
        # Remove excessive whitespace
        company = re.sub(r'\s+', ' ', company.strip())
        
        # Apply noise removal patterns
        for pattern in self.company_noise_patterns:
            company = re.sub(pattern, '', company, flags=re.IGNORECASE)
        
        return company.strip()
    
    def _clean_location(self, location: str) -> str:
        """Clean location string."""
        if not isinstance(location, str):
            return "N/A"
        
        # Remove excessive whitespace
        location = re.sub(r'\s+', ' ', location.strip())
        
        # Standardize common location formats
        for pattern in self.location_patterns:
            match = re.match(pattern, location)
            if match:
                city, region = match.groups()
                return f"{city.strip()}, {region.strip()}"
        
        return location.strip()
    
    def _clean_summary(self, summary: str) -> str:
        """Clean job summary/description."""
        if not isinstance(summary, str):
            return "N/A"
        
        # Remove excessive whitespace and newlines
        summary = re.sub(r'\s+', ' ', summary.strip())
        
        # Limit length
        if len(summary) > 500:
            summary = summary[:497] + "..."
        
        return summary.strip()
    
    def _clean_url(self, url: str) -> str:
        """Clean and normalize URL."""
        if not isinstance(url, str):
            return "N/A"
        
        url = url.strip()
        
        # Ensure HTTPS
        if url.startswith('http://'):
            url = url.replace('http://', 'https://', 1)
        
        # Remove tracking parameters
        if '?' in url:
            base_url, params = url.split('?', 1)
            # Keep only essential parameters
            essential_params = []
            for param in params.split('&'):
                if param.startswith('currentJobId=') or param.startswith('jobId='):
                    essential_params.append(param)
            if essential_params:
                url = base_url + '?' + '&'.join(essential_params)
            else:
                url = base_url
        
        return url
    
    def remove_duplicates(self, jobs_list: List[Dict]) -> List[Dict]:
        """
        Remove duplicate jobs from a list.
        
        Args:
            jobs_list (List[Dict]): List of job dictionaries
            
        Returns:
            List[Dict]: List with duplicates removed
        """
        seen_signatures = set()
        unique_jobs = []
        
        for job in jobs_list:
            # Create a signature for duplicate detection
            title = job.get('title', '').lower().strip()
            company = job.get('company', '').lower().strip()
            location = job.get('location', '').lower().strip()
            
            signature = f"{title}|{company}|{location}"
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def validate_dataframe(self, df: pd.DataFrame) -> tuple[pd.DataFrame, List[str]]:
        """
        Validate and clean a pandas DataFrame of job data.
        
        Args:
            df (pd.DataFrame): DataFrame to validate
            
        Returns:
            tuple: (cleaned_dataframe, list_of_errors)
        """
        all_errors = []
        cleaned_data = []
        
        for index, row in df.iterrows():
            job_data = row.to_dict()
            
            # Clean the data
            cleaned_job = self.clean_job_data(job_data)
            
            # Validate the cleaned data
            is_valid, errors = self.validate_job_data(cleaned_job)
            
            if is_valid:
                cleaned_data.append(cleaned_job)
            else:
                all_errors.extend([f"Row {index}: {error}" for error in errors])
        
        # Remove duplicates
        cleaned_data = self.remove_duplicates(cleaned_data)
        
        # Convert back to DataFrame
        cleaned_df = pd.DataFrame(cleaned_data) if cleaned_data else pd.DataFrame()
        
        return cleaned_df, all_errors 