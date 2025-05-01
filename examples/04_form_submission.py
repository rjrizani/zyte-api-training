"""
Example 4: Form Submission - Quote Search Form
Demonstrates form submission and data extraction using Zyte API.
"""

import sys
from pathlib import Path
import requests
from parsel import Selector
import json
import time
from typing import Dict, List, Optional
import os

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT

def search_quotes(author: str = "Albert Einstein", tag: str = "world") -> Optional[List[Dict]]:
    """
    Search for quotes using form submission.
    
    Args:
        author (str): Author name to search for (default: Albert Einstein)
        tag (str): Tag to filter by (default: world)
        
    Returns:
        list: Collection of matching quotes
    """
    # Define the payload for the Zyte API request
    payload = {
        "url": "http://quotes.toscrape.com/search.aspx",
        "browserHtml": True,
        "actions": [
            {
                "action": "select",
                "selector": {"type": "css", "value": "#author"},
                "values": [author]
            },
            {
                "action": "waitForSelector",
                "selector": {
                    "type": "css", 
                    "value": f"[value=\"{tag}\"]", 
                    "state": "attached"
                }
            },
            {
                "action": "select",
                "selector": {"type": "css", "value": "#tag"},
                "values": [tag]
            },
            {
                "action": "click",
                "selector": {"type": "css", "value": "[type='submit']"}
            },
            {
                "action": "waitForSelector",
                "selector": {"type": "css", "value": ".quote"}
            }
        ]
    }

    try:
        print(f"Searching for quotes by {author} with tag '{tag}'...")
        
        # Send the request to the Zyte API
        response = requests.post(
            ZYTE_API_ENDPOINT,
            auth=(ZYTE_API_KEY, ""),
            json=payload,
            timeout=30
        )
        
        # Check for successful response
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            return None
            
        # Get the HTML content from the response
        html_content = response.json().get('browserHtml', '')
        
        if not html_content:
            print("No HTML content received")
            return None
        
        # Extract quotes from the response
        return extract_quotes(html_content)
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return None
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def extract_quotes(html_content: str) -> List[Dict]:
    """
    Extract quotes from HTML content using Parsel.
    
    Args:
        html_content (str): HTML content to parse
        
    Returns:
        list: Extracted quotes
    """
    quotes = []
    selector = Selector(html_content)
    
    # Find all quotes on the page
    for quote in selector.css(".quote"):
        try:
            # Extract quote data using CSS selectors
            quote_data = {
                "author": quote.css(".author::text").get(),
                "tags": quote.css(".tag::text").getall(),
                "text": quote.css(".content::text").get()[1:-1],  # Remove quotes
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            quotes.append(quote_data)
            
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
        filename = f"quotes_search_{time.strftime('%Y%m%d_%H%M%S')}.json"
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
    # Example searches with known working combinations
    searches = [
        {
            "author": "Albert Einstein",
            "tag": "world"
        },
        {
            "author": "Jane Austen",
            "tag": "love"
        },
        {
            "author": "J.K. Rowling",
            "tag": "abilities"
        }
    ]
    
    for search in searches:
        quotes = search_quotes(**search)
        
        if quotes:
            print(f"\nFound {len(quotes)} matching quotes")
            
            # Save to JSON
            filename = f"quotes_search_{search['author'].lower().replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.json"
            save_to_json(quotes, filename)
            print(f"Saved results to {filename}")
            
            # Print sample quotes
            print("\nSample Quotes:")
            print("-" * 50)
            for quote in quotes:  # Print all quotes since there might be only one
                print(f"\nAuthor: {quote['author']}")
                print(f"Text: {quote['text']}")
                print(f"Tags: {', '.join(quote['tags'])}")
                print("-" * 30)
        else:
            print(f"No quotes found for {search['author']} with tag '{search['tag']}'")
        
        time.sleep(2)  # Pause between searches

if __name__ == "__main__":
    main() 