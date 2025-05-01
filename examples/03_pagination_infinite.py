"""
Example 3: Infinite Scroll - Quote Scraper
Demonstrates infinite scroll handling using Zyte API.
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

def scrape_infinite_scroll(url: str, max_scrolls: int = 3) -> List[Dict]:
    """
    Scrape data from an infinite scroll page.
    
    Args:
        url (str): Target URL
        max_scrolls (int): Maximum number of scroll operations
        
    Returns:
        list: Collection of quotes from all scrolls
    """
    all_quotes = []
    current_scroll = 0
    
    # Initial request to get the page
    payload = {
        "url": url,
        "browserHtml": True,
        "actions": [
            {
                "action": "waitForSelector",
                "selector": {"type": "css", "value": ".quote"}
            }
        ],
        "javascript": True
    }
    
    while current_scroll < max_scrolls:
        try:
            print(f"\nPerforming scroll {current_scroll + 1}...")
            
            # Add scroll actions for subsequent requests
            if current_scroll > 0:
                payload["actions"].extend([
                    {
                        "action": "scrollTo",
                        "target": {"type": "css", "value": ".quote:last-child"}
                    },
                    {
                        "action": "wait",
                        "value": 1000  # Wait 1 second for content to load
                    }
                ])
            
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
            
            # Extract quotes
            new_quotes = extract_quotes(html_content)
            
            if not new_quotes:
                print("No new quotes found. Ending scroll.")
                break
            
            # Check for duplicates
            new_count = 0
            for quote in new_quotes:
                if not is_duplicate(quote, all_quotes):
                    all_quotes.append(quote)
                    new_count += 1
            
            print(f"Found {new_count} new quotes (Total: {len(all_quotes)})")
            
            if new_count == 0:
                print("No new content loaded. Reached end of infinite scroll.")
                break
            
            current_scroll += 1
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

def is_duplicate(quote: Dict, existing_quotes: List[Dict]) -> bool:
    """
    Check if a quote is already in the collection.
    
    Args:
        quote (dict): Quote to check
        existing_quotes (list): Existing quotes
        
    Returns:
        bool: True if quote is a duplicate
    """
    return any(
        q['text'] == quote['text'] and q['author'] == quote['author']
        for q in existing_quotes
    )

def save_to_json(quotes: List[Dict], filename: str = None):
    """
    Save quotes to a JSON file in the responses directory.
    """
    if not quotes:
        return
    os.makedirs("responses", exist_ok=True)
    if not filename:
        filename = f"quotes_infinite_scroll_{time.strftime('%Y%m%d_%H%M%S')}.json"
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
    url = "http://quotes.toscrape.com/scroll"
    print(f"Starting infinite scroll scrape for: {url}")
    
    quotes = scrape_infinite_scroll(url, max_scrolls=3)
    
    if quotes:
        print(f"\nFound {len(quotes)} total quotes")
        
        # Save to JSON
        filename = f"quotes_infinite_scroll_{time.strftime('%Y%m%d_%H%M%S')}.json"
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