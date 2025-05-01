"""
Example 2: Classic Pagination - Quote Scraper
Demonstrates classic pagination handling with Next button navigation.
"""

import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Optional
import os

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT

def scrape_with_pagination(url: str, max_pages: int = 3) -> List[Dict]:
    """
    Scrape data using classic pagination with Next button.
    
    Args:
        url (str): Starting URL
        max_pages (int): Maximum number of pages to scrape
        
    Returns:
        list: Collection of quotes from all pages
    """
    all_quotes = []
    current_page = 1
    current_url = url
    
    while current_page <= max_pages:
        print(f"\nScraping page {current_page}...")
        
        # Prepare the request payload
        payload = {
            "url": current_url,
            "browserHtml": True,
            "actions": [
                {
                    "action": "waitForSelector",
                    "selector": {"type": "css", "value": ".quote"}
                }
            ]
        }
        
        try:
            # Make the request
            response = requests.post(
                ZYTE_API_ENDPOINT,
                auth=(ZYTE_API_KEY, ""),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            html_content = result.get("browserHtml", "")
            
            if not html_content:
                print("No HTML content received")
                break
            
            # Extract quotes from the page
            new_quotes = extract_quotes(html_content)
            
            if not new_quotes:
                print("No quotes found on this page")
                break
            
            all_quotes.extend(new_quotes)
            print(f"Found {len(new_quotes)} quotes on page {current_page}")
            
            # Check for next page
            soup = BeautifulSoup(html_content, 'html.parser')
            next_link = soup.select_one('li.next a')
            
            if not next_link:
                print("No next page link found. Reached last page.")
                break
            
            # Update URL for next page
            next_url = next_link.get('href')
            if next_url:
                if next_url.startswith('/'):
                    # Handle relative URLs
                    current_url = f"http://quotes.toscrape.com{next_url}"
                else:
                    current_url = next_url
            else:
                print("Invalid next page URL")
                break
            
            current_page += 1
            time.sleep(2)  # Rate limiting
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            break
            
        except Exception as e:
            print(f"Error: {str(e)}")
            break
    
    return all_quotes

def extract_quotes(html_content: str) -> List[Dict]:
    """
    Extract quotes from the page.
    
    Args:
        html_content (str): HTML content to parse
        
    Returns:
        list: Extracted quotes
    """
    quotes = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for quote_div in soup.select('.quote'):
        try:
            # Extract quote data
            text = quote_div.select_one('.text').get_text(strip=True)
            author = quote_div.select_one('.author').get_text(strip=True)
            tags = [tag.get_text(strip=True) for tag in quote_div.select('.tags .tag')]
            
            quotes.append({
                'text': text[1:-1],  # Remove surrounding quotes
                'author': author,
                'tags': tags,
                'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        except Exception as e:
            print(f"Error extracting quote: {str(e)}")
            continue
    
    return quotes

def save_to_json(quotes: List[Dict], filename: str = None):
    """
    Save quotes to a JSON file in the responses directory.
    """
    if not quotes:
        return
    os.makedirs("responses", exist_ok=True)
    if not filename:
        filename = f"quotes_pagination_{time.strftime('%Y%m%d_%H%M%S')}.json"
    if not filename.startswith("responses/"):
        filename = os.path.join("responses", filename)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'quotes': quotes,
            'metadata': {
                'count': len(quotes),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, f, indent=2, ensure_ascii=False)

def main():
    # Example usage
    url = "http://quotes.toscrape.com/page/1/"
    print(f"Starting pagination scrape from: {url}")
    
    quotes = scrape_with_pagination(url, max_pages=3)
    
    if quotes:
        print(f"\nFound {len(quotes)} total quotes")
        
        # Save to JSON
        filename = f"quotes_pagination_{time.strftime('%Y%m%d_%H%M%S')}.json"
        save_to_json(quotes, filename)
        print(f"Saved results to {filename}")
        
        # Print sample quotes
        print("\nSample Quotes:")
        print("-" * 50)
        for quote in quotes[:2]:  # Show first 2 quotes
            print(f"\nText: {quote['text']}")
            print(f"Author: {quote['author']}")
            print(f"Tags: {', '.join(quote['tags'])}")
            print("-" * 30)
    else:
        print("No quotes found or error occurred")

if __name__ == "__main__":
    main() 