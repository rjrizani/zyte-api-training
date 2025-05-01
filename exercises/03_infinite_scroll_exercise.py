"""
Exercise 3: Infinite Scroll - Nike Search Results
Scrape products from Nike's search results using infinite scroll handling.
"""

import sys
from pathlib import Path
import requests
import json
import time
from bs4 import BeautifulSoup

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT, SCROLL_PAUSE_TIME

def scrape_nike_search(query: str, max_scrolls: int = 5):
    """
    TODO: Implement this function to:
    1. Load Nike's search results page
    2. Handle infinite scroll to load more search results
    3. Capture and process product data from search
    4. Handle rate limiting and scrolling delays
    
    Args:
        query (str): Search term (e.g., 'running shoes', 'basketball')
        max_scrolls (int): Maximum number of scroll operations
        
    Returns:
        list: Collection of products from search results
    """
    url = f"https://www.nike.com/w?q={query}"
    all_products = []
    current_scroll = 0
    
    while current_scroll < max_scrolls:
        try:
            # Prepare the request payload
            payload = {
                "url": url,
                "browserHtml": True,
                "javascript": True,
                "actions": [
                    {
                        "action": "wait",
                        "value": 3000
                    },
                    {
                        "action": "scroll",
                        "target": "bottom"
                    },
                    {
                        "action": "wait",
                        "value": SCROLL_PAUSE_TIME
                    }
                ]
            }
            
            # TODO: Make the request to Zyte API
            # TODO: Extract products from the response
            # TODO: Check for new products
            # TODO: Update scroll position
            pass
            
        except Exception as e:
            print(f"Error during scroll {current_scroll + 1}: {str(e)}")
            break
    
    return all_products

def extract_search_results(html_content):
    """
    TODO: Implement this function to extract product data from search results
    
    Args:
        html_content (str): HTML content of the page
        
    Returns:
        list: Extracted products from search results
    """
    products = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # TODO: Implement product extraction
    # Hint: Look for product cards in search results
    # Extract: name, price, thumbnail, category, etc.
    
    return products

def is_new_product(product, existing_products):
    """
    TODO: Implement this function to check for duplicate products
    
    Args:
        product (dict): New product data
        existing_products (list): Previously captured products
        
    Returns:
        bool: True if product is new, False if duplicate
    """
    # Your implementation here
    pass

def main():
    # Example search query
    query = "running shoes"
    
    print(f"Searching Nike for '{query}'...")
    products = scrape_nike_search(query, max_scrolls=5)
    
    if products:
        print(f"\nFound {len(products)} products in search results:")
        print("-" * 50)
        for product in products:
            # TODO: Print product details in a formatted way
            pass
    else:
        print("No products found or error occurred")

if __name__ == "__main__":
    main()

"""
Exercise Tasks:
1. Complete the implementation of scrape_nike_search()
2. Implement extract_search_results() to process search data
3. Implement duplicate detection with is_new_product()
4. Add proper scroll timing and rate limiting
5. Handle different search result layouts

Bonus:
- Extract search filters and facets
- Track search result rankings
- Implement sorting options
- Handle 'no results found' cases
""" 