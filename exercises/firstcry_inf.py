import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Optional
import os
from urllib.parse import urljoin

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT

def scrape_infinite_scroll(url: str, max_scrolls: int = 3) -> List[Dict]:
    """
    Scrape product data from an infinite scroll page on FirstCry.
    
    Args:
        url (str): Target URL
        max_scrolls (int): Maximum number of scroll operations
        
    Returns:
        list: Collection of products from all scrolls
    """
    all_products = []
    current_scroll = 0
    
    # Initial request to get the page
    payload = {
        "url": url,
        "browserHtml": True,
        "actions": [
            {
                "action": "waitForSelector",
                "selector": {"type": "css", "value": ".list_block"}
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
                        "target": {"type": "css", "value": ".list_block:last-child"}
                    },
                    {
                        "action": "wait",
                        "value": 2000  # Wait 2 seconds for content to load
                    }
                ])
            
            # Make the request
            response = requests.post(
                ZYTE_API_ENDPOINT,
                auth=(ZYTE_API_KEY, ""),
                json=payload,
                timeout=40
            )
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            html_content = result.get("browserHtml", "")
            
            if not html_content:
                print("No HTML content received")
                break
            
            # Extract products
            new_products = extract_products(html_content, url)
            
            if not new_products:
                print("No new products found. Ending scroll.")
                break
            
            # Check for duplicates
            new_count = 0
            for product in new_products:
                if not is_duplicate(product, all_products):
                    all_products.append(product)
                    new_count += 1
            
            print(f"Found {new_count} new products (Total: {len(all_products)})")
            
            if new_count == 0:
                print("No new content loaded. Reached end of products.")
                break
            
            current_scroll += 1
            time.sleep(2)  # Rate limiting
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            break
            
        except Exception as e:
            print(f"Error: {str(e)}")
            break
    
    return all_products

def extract_products(html_content: str, base_url: str) -> List[Dict]:

    products = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for container in soup.select('.lft.viewtype.viewfive'):
        try:
            # Product Price
            product_price_elem = container.select_one('div.rupee.fw.lft .r1.B14_42 a')
            product_price = product_price_elem.text.strip() if product_price_elem else None
            
            # Original Price
            original_price_elem = container.select_one('span.r2.R12_42 a')
            original_price = original_price_elem.text.strip() if original_price_elem else None
            
            # Club Price
            club_price_elem = container.select_one('span.r1.B12_blue a')
            club_price = club_price_elem.text.strip() if club_price_elem else None
            
            # Product URL
            product_url_elem = container.select_one('a.prd-name')
            product_url = urljoin(base_url, product_url_elem['href']) if product_url_elem else None
            
            products.append({
                'product_price': product_price,
                'original_price': original_price,
                'club_price': club_price,
                'product_url': product_url,
                'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        except Exception as e:
            print(f"Error extracting product: {str(e)}")
            continue
    
    return products

def is_duplicate(product: Dict, existing_products: List[Dict]) -> bool:
    """
    Check if a product is already in the collection.
    
    Args:
        product (dict): Product to check
        existing_products (list): Existing products
        
    Returns:
        bool: True if product is a duplicate
    """
    return any(
        p['product_url'] == product['product_url']
        for p in existing_products
    )

def save_to_json(products: List[Dict], filename: str = None):
    """
    Save products to a JSON file in the responses directory.
    """
    if not products:
        return
    os.makedirs("responses", exist_ok=True)
    if not filename:
        filename = f"firstcry_products_infinite_{time.strftime('%Y%m%d_%H%M%S')}.json"
    if not filename.startswith("responses/"):
        filename = os.path.join("responses", filename)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'products': products,
            'metadata': {
                'count': len(products),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, f, indent=2, ensure_ascii=False)

def main():
    # FirstCry URL with parameters
    url = "https://www.firstcry.com/searchresult?sale=6&searchstring=brand@@@@1@0@20@@@@@@@@@@@@@@@@&sort=bestseller&gender=boy,unisex&ref2=menu_dd_boy-fashion_bestsellers_V#sale=6&searchstring=brand@@@@1@0@20@@@@@@@@@@@@@@@@@@@@@&rating=&sort=bestseller&&vi=three&pmonths=&cgen=&skills=&measurement=&material=&curatedcollections=&Color=&Age=&gender=both,male&ser=&premium=&deliverytype="
    
    print(f"Starting infinite scroll scrape for: {url}")
    
    products = scrape_infinite_scroll(url, max_scrolls=3)
    
    if products:
        print(f"\nFound {len(products)} total products")
        
        # Save to JSON
        filename = f"firstcry_products_infinite_{time.strftime('%Y%m%d_%H%M%S')}.json"
        save_to_json(products, filename)
        print(f"Saved results to {filename}")
        
        # Print sample products
        print("\nSample Products:")
        print("-" * 50)
        for product in products[:2]:
            print(f"\nProduct Price: {product['product_price']}")
            print(f"Original Price: {product['original_price']}")
            print(f"Club Price: {product['club_price']}")
            print(f"URL: {product['product_url']}")
            print("-" * 30)
    else:
        print("No products found or error occurred")

if __name__ == "__main__":
    main()