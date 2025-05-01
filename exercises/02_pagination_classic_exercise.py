"""
Exercise 2: Classic Pagination - Job Listings Scraper
Scrape job listings from Indeed.com using classic pagination.
"""

import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT, PAGINATION_TIMEOUT

def scrape_job_listings(search_term, location, max_pages=3):
    """
    TODO: Implement this function to:
    1. Navigate through Indeed's job listings pages
    2. Extract job details from each page
    3. Handle pagination using the "Next" button
    4. Implement proper error handling and rate limiting
    
    Args:
        search_term (str): Job search keyword
        location (str): Job location
        max_pages (int): Maximum number of pages to scrape
        
    Returns:
        list: Collection of job listings
    """
    base_url = f"https://www.indeed.com/jobs?q={search_term}&l={location}"
    all_jobs = []
    current_page = 1
    
    while current_page <= max_pages:
        try:
            # TODO: Implement pagination logic
            # TODO: Extract job listings from each page
            # TODO: Handle navigation between pages
            pass
            
        except Exception as e:
            print(f"Error on page {current_page}: {str(e)}")
            break
    
    return all_jobs

def extract_job_details(html_content):
    """
    TODO: Implement this function to extract job details from the page
    
    Args:
        html_content (str): HTML content of the page
        
    Returns:
        list: Extracted job listings
    """
    jobs = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # TODO: Implement job details extraction
    # Hint: Look for job cards/containers
    # Extract: title, company, location, salary, description
    
    return jobs

def main():
    # Example search parameters
    search_term = "python developer"
    location = "remote"
    
    print(f"Searching for {search_term} jobs in {location}...")
    jobs = scrape_job_listings(search_term, location, max_pages=3)
    
    if jobs:
        print(f"\nFound {len(jobs)} job listings:")
        print("-" * 50)
        for job in jobs:
            # TODO: Print job details in a formatted way
            pass
    else:
        print("No jobs found or error occurred")

if __name__ == "__main__":
    main()

"""
Exercise Tasks:
1. Complete the implementation of scrape_job_listings()
2. Implement extract_job_details() to process job data
3. Add proper error handling and rate limiting
4. Handle different page layouts and job card formats
5. Implement retry logic for failed requests

Bonus:
- Add filters (date posted, salary range, etc.)
- Save results to a CSV/JSON file
- Implement advanced search parameters
- Add proxy rotation support
""" 