import sys
from pathlib import Path
import requests
from parsel import Selector
import json
import time
from typing import Dict, List, Optional
import os
import urllib.parse
import re

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT

def search_job(job: str = "fresh", location: str = "Jakarta") -> Optional[List[Dict]]:
    """
    Search for jobs on Indeed Indonesia using Zyte API.
    
    Args:
        job (str): Job title to search for (default: "fresh")
        location (str): Location to filter by (default: "Jakarta")
        
    Returns:
        list: List of job dictionaries
    """
    # Encode parameters for URL
    encoded_job = urllib.parse.quote_plus(job)
    encoded_location = urllib.parse.quote_plus(location)
    url = f"https://id.indeed.com/jobs?q={encoded_job}&l={encoded_location}"

    # Define Zyte API payload
    payload = {
        "url": url,
        "browserHtml": True,
        "actions": [
            {
                "action": "waitForSelector",
                "selector": {
                    "type": "css", 
                    "value": ".job_seen_beacon",
                    "state": "attached"
                },
                "timeout": 10
            }
        ]
    }

    try:
        print(f"Searching for jobs: '{job}' in '{location}'...")
        
        # Send request to Zyte API
        response = requests.post(
            ZYTE_API_ENDPOINT,
            auth=(ZYTE_API_KEY, ""),
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"API request failed with status {response.status_code}")
            return None
            
        html_content = response.json().get('browserHtml', '')
        
        if not html_content:
            print("No HTML content received")
            return None
            
        return extract_jobs(html_content)
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None
    
def extract_jobs(html_content: str) -> List[Dict]:
    """
    Extract job listings with job snippet footer text
    """
    jobs = []
    selector = Selector(html_content)
    
    for job_elem in selector.css(".job_seen_beacon"):
        try:
            # Extract job title
            title = job_elem.css("h2.jobTitle span[title]::attr(title)").get()
            if not title:
                title = job_elem.css("h2.jobTitle a::attr(aria-label)").get() or "N/A"
                title = title.replace("title: ", "").strip()

            # Extract company name
            company = job_elem.css("span[data-testid='company-name']::text").get() or "N/A"
            
            # Extract location
            location = job_elem.css("div[data-testid='text-location']::text").get() or "N/A"
            
        
            
            # Extract job URL
            relative_url = job_elem.css("h2.jobTitle a::attr(href)").get()
            
            job_data = {
                "title": title.strip(),
                "company": company.strip(),
                "location": location.strip(),           
                "url": f"https://id.indeed.com{relative_url}" if relative_url else None,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            jobs.append(job_data)
        except Exception as e:
            print(f"Error extracting job: {str(e)}")
            continue
    
    return jobs
def save_to_json(jobs: List[Dict], filename: str = None):
    """
    Save job listings to JSON file in responses directory.
    """
    if not jobs:
        return
    os.makedirs("responses", exist_ok=True)
    if not filename:
        filename = f"jobs_search_{time.strftime('%Y%m%d_%H%M%S')}.json"
    if not filename.startswith("responses/"):
        filename = os.path.join("responses", filename)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'jobs': jobs,
            'metadata': {
                'count': len(jobs),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, f, indent=2, ensure_ascii=False)

def main():
    # Example job searches
    searches = [
        {"job": "fresh", "location": "Jakarta"},
        {"job": "software engineer", "location": "Bandung"},
        {"job": "data analyst", "location": "Indonesia"}
    ]
    
    for search in searches:
        jobs = search_job(**search)
        
        if jobs:
            print(f"\nFound {len(jobs)} jobs for '{search['job']}' in '{search['location']}'")
            
            # Generate filename
            filename = f"jobs_{search['job'].lower().replace(' ', '_')}_{search['location'].lower().replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.json"
            save_to_json(jobs, filename)
            print(f"Saved results to {filename}")
            
            # Print sample results
            print("\nSample Jobs:")
            print("-" * 60)
            for idx, job in enumerate(jobs[:3], 1):
                print(f"{idx}. Title: {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                print(f"   URL: {job['url']}\n")
        else:
            print(f"\nNo jobs found for '{search['job']}' in '{search['location']}'")
        
        time.sleep(3)  # Respectful crawling delay

if __name__ == "__main__":
    main()