"""
Deployment configuration and utilities for the Job Trend Analyzer
"""

import os
import subprocess
import sys

def create_dockerfile():
    """Create Dockerfile for containerized deployment"""
    dockerfile_content = '''
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create templates directory if it doesn't exist
RUN mkdir -p templates

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "app.py"]
'''
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    print("Dockerfile created!")

def create_render_config():
    """Create render.yaml for Render deployment"""
    render_config = '''
services:
  - type: web
    name: job-trend-analyzer
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PORT
        value: 5000
'''
    
    with open('render.yaml', 'w') as f:
        f.write(render_config)
    
    print("Render configuration created!")

def create_heroku_config():
    """Create Procfile for Heroku deployment"""
    procfile_content = 'web: python app.py'
    
    with open('Procfile', 'w') as f:
        f.write(procfile_content)
    
    print("Procfile created for Heroku!")

def create_railway_config():
    """Create railway.json for Railway deployment"""
    railway_config = '''
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
'''
    
    with open('railway.json', 'w') as f:
        f.write(railway_config)
    
    print("Railway configuration created!")

def setup_environment():
    """Setup environment variables template"""
    env_template = '''
# Environment Variables Template
# Copy this to .env and fill in your values

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration (if using external database)
DATABASE_URL=sqlite:///jobs.db

# API Keys (if using external job APIs)
ADZUNA_API_ID=your_adzuna_api_id
ADZUNA_API_KEY=your_adzuna_api_key

# Scraping Configuration
SCRAPE_DELAY_MIN=1
SCRAPE_DELAY_MAX=3
MAX_PAGES_PER_SITE=5

# Security
SECRET_KEY=your_secret_key_here
'''
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    
    print("Environment template created!")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = '''
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Flask
instance/
.webassets-cache

# Scraped Data
*.csv
*.json
jobs_backup/
'''
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print(".gitignore created!")

def create_readme():
    """Create comprehensive README"""
    readme_content = '''
# Real-Time Job Trend Analyzer

A comprehensive Python-based web scraping tool that extracts live job listings from popular job portals and performs analysis to showcase trending technologies, top job roles, most hiring cities, and required skills.

## Features

- 🔍 **Web Scraping**: Extracts job data from multiple sources
- 📊 **Data Analysis**: Analyzes trends in job titles, skills, and locations
- 🌐 **Web Interface**: Clean, responsive Flask-based dashboard
- 📈 **Real-time Updates**: Scheduled data fetching and live charts
- 🔎 **Keyword Filtering**: Filter trends by specific keywords
- 💾 **Data Storage**: SQLite database for persistent storage
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd job-trend-analyzer