import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime
import json

class AdvancedJobScraper:
    """Advanced job scraper with multiple sources and better error handling"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_with_retry(self, url, max_retries=3):
        """Scrape with retry mechanism"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return response
                else:
                    print(f"HTTP {response.status_code} on attempt {attempt + 1}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))
        return None
    
    def extract_job_data_indeed(self, soup):
        """Extract job data from Indeed page"""
        jobs = []
        
        # Updated selectors for Indeed's current structure
        job_selectors = [
            'div[data-jk]',  # Main job container
            '.jobsearch-SerpJobCard',  # Alternative selector
            '.job_seen_beacon'  # Another alternative
        ]
        
        job_cards = []
        for selector in job_selectors:
            job_cards = soup.select(selector)
            if job_cards:
                break
        
        for card in job_cards:
            try:
                # Try multiple selectors for title
                title = None
                title_selectors = [
                    'h2.jobTitle a span',
                    '.jobTitle a',
                    'h2 a span[title]',
                    '.jobTitle'
                ]
                
                for selector in title_selectors:
                    title_elem = card.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        break
                
                # Try multiple selectors for company
                company = None
                company_selectors = [
                    '.companyName',
                    'span.companyName a',
                    'span.companyName',
                    '[data-testid="company-name"]'
                ]
                
                for selector in company_selectors:
                    company_elem = card.select_one(selector)
                    if company_elem:
                        company = company_elem.get_text(strip=True)
                        break
                
                # Try multiple selectors for location
                location = None
                location_selectors = [
                    '.companyLocation',
                    '[data-testid="job-location"]',
                    '.locationsContainer'
                ]
                
                for selector in location_selectors:
                    location_elem = card.select_one(selector)
                    if location_elem:
                        location = location_elem.get_text(strip=True)
                        break
                
                # Extract job summary/description
                summary = ""
                summary_selectors = [
                    '.summary',
                    '.job-snippet',
                    '[data-testid="job-snippet"]'
                ]
                
                for selector in summary_selectors:
                    summary_elem = card.select_one(selector)
                    if summary_elem:
                        summary = summary_elem.get_text(strip=True)
                        break
                
                if title and company:  # Only add if we have essential data
                    job = {
                        'title': title,
                        'company': company,
                        'location': location or 'Not specified',
                        'summary': summary,
                        'date_posted': datetime.now().strftime('%Y-%m-%d'),
                        'source': 'Indeed'
                    }
                    jobs.append(job)
                    
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue
        
        return jobs
    
    def scrape_jobs_api(self, keyword="software developer", location="", count=50):
        """Scrape jobs using a job API (example with a mock API)"""
        # This is a placeholder for API-based scraping
        # You would replace this with actual API calls to services like:
        # - Adzuna API
        # - Reed API
        # - GitHub Jobs API (deprecated but example)
        
        jobs = []
        
        # Mock API response structure
        mock_api_jobs = [
            {
                "title": "Senior Python Developer",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "description": "Looking for a senior Python developer with Django experience...",
                "posted_date": "2024-01-15"
            },
            # Add more mock jobs here
        ]
        
        for job_data in mock_api_jobs:
            job = {
                'title': job_data.get('title', ''),
                'company': job_data.get('company', ''),
                'location': job_data.get('location', ''),
                'summary': job_data.get('description', ''),
                'date_posted': job_data.get('posted_date', datetime.now().strftime('%Y-%m-%d')),
                'source': 'API'
            }
            jobs.append(job)
        
        return jobs
    
    def save_to_csv(self, jobs, filename='jobs.csv'):
        """Save jobs to CSV file"""
        import csv
        
        if not jobs:
            print("No jobs to save")
            return
        
        fieldnames = ['title', 'company', 'location', 'summary', 'date_posted', 'source']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for job in jobs:
                writer.writerow(job)
        
        print(f"Saved {len(jobs)} jobs to {filename}")
    
    def save_to_json(self, jobs, filename='jobs.json'):
        """Save jobs to JSON file"""
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(jobs, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(jobs)} jobs to {filename}")

# Example usage
if __name__ == "__main__":
    scraper = AdvancedJobScraper()
    
    # Generate some mock data for testing
    from app import JobScraper
    basic_scraper = JobScraper()
    jobs = basic_scraper.generate_mock_jobs(20)
    
    # Save to different formats
    scraper.save_to_csv(jobs, 'sample_jobs.csv')
    scraper.save_to_json(jobs, 'sample_jobs.json')
    
    print("Sample data files created!")