import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
from datetime import datetime, timedelta
import threading
from collections import Counter
import re
from flask import Flask, render_template, jsonify, request
import plotly.graph_objs as go
import plotly.utils
from urllib.parse import quote_plus
import schedule

app = Flask(__name__)

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def scrape_indeed(self, keyword="software developer", location="", max_pages=3):
        """Scrape job listings from Indeed"""
        jobs = []
        base_url = "https://www.indeed.com/jobs"
        
        for page in range(max_pages):
            params = {
                'q': keyword,
                'l': location,
                'start': page * 10
            }
            
            try:
                response = self.session.get(base_url, params=params, timeout=10)
                if response.status_code != 200:
                    print(f"Failed to fetch page {page + 1}")
                    continue
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        title = title_elem.get_text(strip=True) if title_elem else "N/A"
                        
                        company_elem = card.find('span', class_='companyName')
                        company = company_elem.get_text(strip=True) if company_elem else "N/A"
                        
                        location_elem = card.find('div', class_='companyLocation')
                        job_location = location_elem.get_text(strip=True) if location_elem else "N/A"
                        
                        summary_elem = card.find('div', class_='summary')
                        summary = summary_elem.get_text(strip=True) if summary_elem else ""
                        
                        # Extract skills from job description
                        skills = self.extract_skills(title + " " + summary)
                        
                        job = {
                            'title': title,
                            'company': company,
                            'location': job_location,
                            'skills': ', '.join(skills),
                            'date_posted': datetime.now().strftime('%Y-%m-%d'),
                            'source': 'Indeed'
                        }
                        jobs.append(job)
                        
                    except Exception as e:
                        print(f"Error parsing job card: {e}")
                        continue
                
                # Be polite - add delay between requests
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"Error scraping page {page + 1}: {e}")
                continue
                
        return jobs
    
    def generate_mock_jobs(self, count=50):
        """Generate mock job data for demonstration"""
        job_titles = [
            "Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer",
            "Frontend Developer", "Backend Developer", "Full Stack Developer", "Data Analyst",
            "Machine Learning Engineer", "Cloud Architect", "Cybersecurity Analyst",
            "Mobile Developer", "QA Engineer", "UX Designer", "Technical Writer"
        ]
        
        companies = [
            "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Spotify",
            "Uber", "Airbnb", "Tesla", "Stripe", "Shopify", "Zoom", "Slack", "Adobe"
        ]
        
        cities = [
            "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
            "Boston, MA", "Los Angeles, CA", "Chicago, IL", "Denver, CO",
            "Atlanta, GA", "Miami, FL", "Portland, OR", "San Diego, CA"
        ]
        
        skills_pool = [
            "Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes",
            "SQL", "MongoDB", "PostgreSQL", "Git", "Linux", "Java", "C++", "Go",
            "TypeScript", "Vue.js", "Angular", "Django", "Flask", "TensorFlow",
            "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Tableau", "Power BI"
        ]
        
        jobs = []
        for i in range(count):
            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            date_posted = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            # Random skills (2-6 skills per job)
            num_skills = random.randint(2, 6)
            job_skills = random.sample(skills_pool, num_skills)
            
            job = {
                'title': random.choice(job_titles),
                'company': random.choice(companies),
                'location': random.choice(cities),
                'skills': ', '.join(job_skills),
                'date_posted': date_posted,
                'source': 'Mock Data'
            }
            jobs.append(job)
            
        return jobs
    
    def extract_skills(self, text):
        """Extract technical skills from job description"""
        skills_keywords = [
            'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker',
            'kubernetes', 'sql', 'mongodb', 'postgresql', 'git', 'linux',
            'typescript', 'vue.js', 'angular', 'django', 'flask', 'tensorflow',
            'pytorch', 'pandas', 'numpy', 'scikit-learn', 'tableau', 'power bi',
            'c++', 'go', 'rust', 'scala', 'r', 'matlab', 'spark', 'hadoop',
            'elasticsearch', 'redis', 'nginx', 'apache', 'jenkins', 'gitlab'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
                
        return found_skills

class JobDatabase:
    def __init__(self, db_path='jobs.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                skills TEXT,
                date_posted DATE NOT NULL,
                source TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_jobs(self, jobs):
        """Insert job listings into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for job in jobs:
            cursor.execute('''
                INSERT INTO jobs (title, company, location, skills, date_posted, source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (job['title'], job['company'], job['location'], 
                  job['skills'], job['date_posted'], job['source']))
        
        conn.commit()
        conn.close()
        print(f"Inserted {len(jobs)} jobs into database")
    
    def get_all_jobs(self):
        """Retrieve all jobs from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC')
        jobs = cursor.fetchall()
        
        conn.close()
        return jobs
    
    def get_jobs_by_keyword(self, keyword):
        """Get jobs filtered by keyword"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM jobs 
            WHERE title LIKE ? OR skills LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%'))
        
        jobs = cursor.fetchall()
        conn.close()
        return jobs
    
    def clear_old_data(self):
        """Clear old job data (older than 30 days)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('DELETE FROM jobs WHERE date_posted < ?', (thirty_days_ago,))
        
        conn.commit()
        conn.close()

class JobAnalyzer:
    def __init__(self, db):
        self.db = db
    
    def get_top_job_titles(self, limit=5, keyword=None):
        """Get top job titles"""
        if keyword:
            jobs = self.db.get_jobs_by_keyword(keyword)
        else:
            jobs = self.db.get_all_jobs()
        
        titles = [job[1] for job in jobs]  # job[1] is title
        title_counts = Counter(titles)
        return title_counts.most_common(limit)
    
    def get_top_skills(self, limit=10, keyword=None):
        """Get most frequent skills"""
        if keyword:
            jobs = self.db.get_jobs_by_keyword(keyword)
        else:
            jobs = self.db.get_all_jobs()
        
        all_skills = []
        for job in jobs:
            skills = job[4]  # job[4] is skills
            if skills:
                skill_list = [skill.strip() for skill in skills.split(',')]
                all_skills.extend(skill_list)
        
        skill_counts = Counter(all_skills)
        return skill_counts.most_common(limit)
    
    def get_top_cities(self, limit=5, keyword=None):
        """Get cities with most job openings"""
        if keyword:
            jobs = self.db.get_jobs_by_keyword(keyword)
        else:
            jobs = self.db.get_all_jobs()
        
        locations = [job[3] for job in jobs]  # job[3] is location
        location_counts = Counter(locations)
        return location_counts.most_common(limit)
    
    def get_posting_trends(self, keyword=None):
        """Get job posting trends over time"""
        if keyword:
            jobs = self.db.get_jobs_by_keyword(keyword)
        else:
            jobs = self.db.get_all_jobs()
        
        dates = [job[5] for job in jobs]  # job[5] is date_posted
        date_counts = Counter(dates)
        
        # Sort by date
        sorted_dates = sorted(date_counts.items())
        return sorted_dates

# Initialize components
scraper = JobScraper()
db = JobDatabase()
analyzer = JobAnalyzer(db)

def scrape_and_store_jobs():
    """Function to scrape and store jobs"""
    print("Starting job scraping...")
    
    # For demonstration, we'll use mock data
    # In production, you would use real scraping
    jobs = scraper.generate_mock_jobs(50)
    
    # Uncomment below for real Indeed scraping (be careful with rate limits)
    # jobs.extend(scraper.scrape_indeed("software engineer", "", 2))
    
    if jobs:
        db.insert_jobs(jobs)
        print(f"Successfully scraped and stored {len(jobs)} jobs")
    else:
        print("No jobs found")

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard')
def dashboard_data():
    keyword = request.args.get('keyword', '')
    
    top_titles = analyzer.get_top_job_titles(5, keyword if keyword else None)
    top_skills = analyzer.get_top_skills(10, keyword if keyword else None)
    top_cities = analyzer.get_top_cities(5, keyword if keyword else None)
    trends = analyzer.get_posting_trends(keyword if keyword else None)
    
    return jsonify({
        'top_titles': top_titles,
        'top_skills': top_skills,
        'top_cities': top_cities,
        'trends': trends
    })

@app.route('/api/scrape')
def trigger_scrape():
    """Manually trigger job scraping"""
    try:
        scrape_and_store_jobs()
        return jsonify({'status': 'success', 'message': 'Jobs scraped successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stats')
def get_stats():
    """Get basic statistics"""
    jobs = db.get_all_jobs()
    total_jobs = len(jobs)
    
    # Get unique companies and locations
    companies = set(job[2] for job in jobs)
    locations = set(job[3] for job in jobs)
    
    return jsonify({
        'total_jobs': total_jobs,
        'total_companies': len(companies),
        'total_locations': len(locations)
    })

# Scheduled scraping (runs every 30 minutes)
def schedule_scraping():
    schedule.every(30).minutes.do(scrape_and_store_jobs)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    # Initial data load
    print("Loading initial job data...")
    scrape_and_store_jobs()
    
    # Start background scheduler
    scheduler_thread = threading.Thread(target=schedule_scraping, daemon=True)
    scheduler_thread.start()
    
    print("Starting Flask application...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)