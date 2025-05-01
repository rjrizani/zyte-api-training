"""
Exercise 4: Form Submission - Quote Search Form
Handle form submission and data extraction using Zyte API.
"""

import sys
from pathlib import Path
import requests
from parsel import Selector
from typing import Dict, List, Optional
import json
import time

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT

class FormSubmissionError(Exception):
    pass

def submit_search_form(author: str, tag: str, max_retries: int = 3) -> Optional[List[Dict]]:
    """
    Submit the search form and extract quote data.
    
    Args:
        author (str): Author name to search for
        tag (str): Tag to filter by
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        list: Collection of quotes matching the search criteria
    """
    # Define the payload for the Zyte API request
    payload = {
        "url": "http://quotes.toscrape.com/search.aspx",
        "browserHtml": True,
        "actions": [
            {
                "action": "select",
                "selector": {"type": "css", "value": "#author"},
                "values": [author],
            },
            {
                "action": "waitForSelector",
                "selector": {
                    "type": "css", 
                    "value": f"[value=\"{tag}\"]", 
                    "state": "attached"
                },
            },
            {
                "action": "select",
                "selector": {"type": "css", "value": "#tag"},
                "values": [tag],
            },
            {
                "action": "click",
                "selector": {"type": "css", "value": "[type='submit']"},
            },
            {
                "action": "waitForSelector",
                "selector": {"type": "css", "value": ".quote"},
            },
        ],
    }
    
    for attempt in range(max_retries):
        try:
            # Send the request to the Zyte API
            response = requests.post(
                ZYTE_API_ENDPOINT,
                auth=(ZYTE_API_KEY, ""),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Get the HTML content from the response
            result = response.json()
            html_content = result.get('browserHtml', '')
            
            if not html_content:
                raise FormSubmissionError("No HTML content received")
            
            # Extract quotes from the response
            quotes = extract_quotes(html_content)
            
            if not quotes:
                print("No quotes found matching the criteria.")
            
            return quotes
            
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return None
            
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
    
    return None

def extract_quotes(html_content: str) -> List[Dict]:
    """
    Extract quote data from the HTML response.
    
    Args:
        html_content (str): HTML content to parse
        
    Returns:
        list: Extracted quotes
    """
    quotes = []
    selector = Selector(html_content)
    
    for quote in selector.css(".quote"):
        try:
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

def save_to_json(quotes: List[Dict], filename: str = "quotes.json"):
    """
    Save quotes to a JSON file.
    
    Args:
        quotes (list): List of quote dictionaries
        filename (str): Output filename
    """
    if not quotes:
        return
        
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'quotes': quotes,
            'metadata': {
                'count': len(quotes),
                'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, f, indent=2, ensure_ascii=False)

def main():
    # Example search parameters
    search_params = [
        {"author": "Albert Einstein", "tag": "world"},
        {"author": "Oscar Wilde", "tag": "humor"}
    ]
    
    for params in search_params:
        print(f"\nSearching for quotes by {params['author']} with tag '{params['tag']}'...")
        quotes = submit_search_form(**params)
        
        if quotes:
            print(f"\nFound {len(quotes)} matching quotes:")
            print("-" * 50)
            
            # Save to JSON
            filename = f"quotes_{params['author'].lower().replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.json"
            save_to_json(quotes, filename)
            print(f"Saved results to {filename}")
            
            # Print sample quotes
            for quote in quotes:
                print(f"\nAuthor: {quote['author']}")
                print(f"Text: {quote['text']}")
                print(f"Tags: {', '.join(quote['tags'])}")
                print("-" * 30)
        else:
            print("No quotes found or error occurred")
        
        time.sleep(2)  # Pause between searches

if __name__ == "__main__":
    main()

"""
Exercise Tasks:
1. Add support for multiple form fields
2. Implement validation for form inputs
3. Add error handling for invalid selections
4. Support different form submission methods (GET/POST)
5. Add pagination support for results

Bonus:
- Handle dynamic form fields
- Implement advanced search filters
- Add data export to different formats
- Support multiple search criteria
""" 