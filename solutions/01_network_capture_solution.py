"""
Solution: Nike API Direct Access
Complete implementation of Nike product data extraction using direct API access.
"""

import sys
from pathlib import Path
import json
import requests
import time
from typing import List, Dict, Optional
from urllib.parse import urlencode

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY

def get_nike_products(category: str) -> List[Dict]:
    """
    Get products from Nike's API for the given category.
    
    Args:
        category (str): Product category ID (e.g., 'football-1gdj0')
        
    Returns:
        list: Processed products data
    """
    # Configure the Nike API URL
    base_url = "https://api.nike.com/discover/product_wall/v1/marketplace/IN/language/en-GB"
    consumer_id = "d9a5bc42-4b9c-4976-858a-f159cf99c647"
    
    # Set up query parameters
    params = {
        "path": f"/in/w/{category}",
        "queryType": "PRODUCTS",
        "count": 24,  # Products per page
        "anchor": 0  # Starting index
    }
    
    # Build the full API URL
    api_url = f"{base_url}/consumerChannelId/{consumer_id}?{urlencode(params)}"
    
    # Configure headers
    headers = {
        "nike-api-caller-id": "nike:dotcom:browse:wall.client:2.0",
        "Referer": "https://www.nike.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    
    # Set up Zyte proxy configuration
    proxies = {
        "http": f"http://{ZYTE_API_KEY}:@api.zyte.com:8011",
        "https": f"http://{ZYTE_API_KEY}:@api.zyte.com:8011"
    }
    
    try:
        print(f"Fetching data from Nike API...")
        response = requests.get(
            api_url,
            headers=headers,
            proxies=proxies,
            timeout=30,
            verify=False
        )
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Extract products
        product_groups = data.get("productGroupings", [])
        total_products = data.get("pages", {}).get("totalResources", 0)
        print(f"Total available products: {total_products}")
        
        # Process each product
        products = []
        for group in product_groups:
            if group.get("products"):
                product = format_product(group["products"][0])  # Get first product variant
                if product:
                    products.append(product)
        
        return products
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {str(e)}")
        return []
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return []

def format_product(product_data: Dict) -> Optional[Dict]:
    """
    Format raw product data into a clean structure.
    
    Args:
        product_data (dict): Raw product data from API
        
    Returns:
        dict: Formatted product information
    """
    try:
        return {
            "title": product_data.get("copy", {}).get("title"),
            "subtitle": product_data.get("copy", {}).get("subTitle"),
            "price": product_data.get("prices", {}).get("currentPrice"),
            "currency": product_data.get("prices", {}).get("currency"),
            "image_url": product_data.get("colorwayImages", {}).get("portraitURL"),
            "product_url": product_data.get("pdpUrl", {}).get("url"),
            "colorway": product_data.get("colorDescription"),
            "style_code": product_data.get("styleCode"),
            "available": product_data.get("availability", {}).get("available", False),
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Error formatting product: {str(e)}")
        return None

def save_to_json(products: List[Dict], filename: str = "nike_products.json"):
    """
    Save products to a JSON file in the responses directory.
    
    Args:
        products (list): List of product dictionaries
        filename (str): Output filename
    """
    if not products:
        return
        
    # Create responses directory if it doesn't exist
    Path("responses").mkdir(exist_ok=True)
    
    # Save file in responses directory
    filepath = Path("responses") / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump({
            'products': products,
            'metadata': {
                'count': len(products),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Saved results to responses/{filename}")

def main():
    # Nike category URLs
    categories = {
        'football': 'football-1gdj0',
        'basketball': 'basketball-3glsm',
        'running': 'running-37v7j'
    }
    
    for category_name, category_id in categories.items():
        print(f"\nProcessing {category_name} category...")
        products = get_nike_products(category_id)
        
        if products:
            print(f"\nFound {len(products)} products:")
            print("-" * 50)
            
            # Show first 3 products as sample
            for product in products[:3]:
                print(f"\n🛒 {product['title']}")
                if product['subtitle']:
                    print(f"📝 {product['subtitle']}")
                print(f"💰 Price: {product['price']} {product['currency']}")
                print(f"🎨 Colorway: {product['colorway']}")
                print(f"📦 Available: {'Yes' if product['available'] else 'No'}")
                print(f"🔗 URL: {product['product_url']}")
                print("-" * 30)
            
            # Save to JSON
            filename = f"nike_{category_name}_{time.strftime('%Y%m%d_%H%M%S')}.json"
            save_to_json(products, filename)
        else:
            print(f"No products found for {category_name}")
        
        # Wait between categories to avoid rate limiting
        time.sleep(2)

if __name__ == "__main__":
    main() 