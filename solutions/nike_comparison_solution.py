"""
Solution: Nike Product Scraping - Strategy Comparison
Comparing direct API access vs infinite scroll approaches with detailed statistics.
"""

import sys
from pathlib import Path
import json
import requests
import time
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlencode
from datetime import datetime

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT

class NikeStats:
    def __init__(self):
        self.start_time = time.time()
        self.products_found = 0
        self.total_available = 0
        self.pages_processed = 0
        self.errors = 0
        
    def get_duration(self) -> float:
        return round(time.time() - self.start_time, 2)
    
    def to_dict(self) -> Dict:
        return {
            "products_found": self.products_found,
            "total_available": self.total_available,
            "pages_processed": self.pages_processed,
            "errors": self.errors,
            "duration_seconds": self.get_duration(),
            "products_per_second": round(self.products_found / self.get_duration(), 2) if self.get_duration() > 0 else 0
        }

def get_nike_products_api(category: str, stats: NikeStats) -> List[Dict]:
    """
    Get products from Nike's API for the given category.
    """
    base_url = "https://api.nike.com/discover/product_wall/v1/marketplace/IN/language/en-GB"
    consumer_id = "d9a5bc42-4b9c-4976-858a-f159cf99c647"
    
    all_products = []
    page = 0
    products_per_page = 24
    
    while True:
        try:
            # Set up query parameters with pagination
            params = {
                "path": f"/in/w/{category}",
                "queryType": "PRODUCTS",
                "count": products_per_page,
                "anchor": page * products_per_page
            }
            
            api_url = f"{base_url}/consumerChannelId/{consumer_id}?{urlencode(params)}"
            
            headers = {
                "nike-api-caller-id": "nike:dotcom:browse:wall.client:2.0",
                "Referer": "https://www.nike.com/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            }
            
            proxies = {
                "http": f"http://{ZYTE_API_KEY}:@api.zyte.com:8011",
                "https": f"http://{ZYTE_API_KEY}:@api.zyte.com:8011"
            }
            
            print(f"Fetching page {page + 1}...")
            response = requests.get(
                api_url,
                headers=headers,
                proxies=proxies,
                timeout=30,
                verify=False
            )
            response.raise_for_status()
            
            data = response.json()
            product_groups = data.get("productGroupings", [])
            
            if page == 0:
                stats.total_available = data.get("pages", {}).get("totalResources", 0)
            
            if not product_groups:
                break
                
            for group in product_groups:
                if group.get("products"):
                    product = format_product(group["products"][0])
                    if product:
                        all_products.append(product)
                        stats.products_found += 1
            
            stats.pages_processed += 1
            
            # Check if we've reached the end
            if len(product_groups) < products_per_page:
                break
                
            page += 1
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"Error on page {page + 1}: {str(e)}")
            stats.errors += 1
            break
    
    return all_products

def get_nike_products_scroll(category: str, stats: NikeStats) -> List[Dict]:
    """
    Get products using infinite scroll strategy via Zyte API.
    """
    url = f"https://www.nike.com/in/w/{category}"
    all_products = []
    
    try:
        api_response = requests.post(
            ZYTE_API_ENDPOINT,
            auth=(ZYTE_API_KEY, ""),
            json={
                "url": url,
                "productList": True,
                "actions": [
                    {
                        "action": "scrollBottom",
                        "timeout": 30,
                        "maxScrollDelay": 2,
                        "maxScrollCount": 20,
                        "maxPageHeight": 50000
                    }
                ]
            },
            timeout=120
        )
        
        if api_response.status_code == 200:
            result = api_response.json()
            products = result.get('productList', {}).get('products', [])
            stats.products_found = len(products)
            stats.pages_processed = 1
            return products
        else:
            stats.errors += 1
            print(f"Request failed: {api_response.status_code}")
            return []
            
    except Exception as e:
        stats.errors += 1
        print(f"Error: {str(e)}")
        return []

def format_product(product_data: Dict) -> Optional[Dict]:
    """
    Format raw product data into a clean structure.
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

def save_comparison_results(category: str, api_stats: Dict, scroll_stats: Dict, api_products: List[Dict], scroll_products: List[Dict]):
    """
    Save comparison results to a JSON file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nike_comparison_{category}_{timestamp}.json"
    
    # Create responses directory if it doesn't exist
    Path("responses").mkdir(exist_ok=True)
    filepath = Path("responses") / filename
    
    comparison_data = {
        "category": category,
        "timestamp": timestamp,
        "api_strategy": {
            "stats": api_stats,
            "sample_products": api_products[:3] if api_products else []
        },
        "scroll_strategy": {
            "stats": scroll_stats,
            "sample_products": scroll_products[:3] if scroll_products else []
        },
        "comparison": {
            "api_vs_scroll_difference": api_stats["products_found"] - scroll_stats["products_found"],
            "api_speed": f"{api_stats['products_per_second']} products/sec",
            "scroll_speed": f"{scroll_stats['products_per_second']} products/sec",
            "more_efficient": "API" if api_stats["products_per_second"] > scroll_stats["products_per_second"] else "Scroll"
        }
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, indent=2, ensure_ascii=False)
    
    return filename

def print_comparison(category: str, api_stats: Dict, scroll_stats: Dict):
    """
    Print a formatted comparison of both strategies.
    """
    print("\n" + "=" * 60)
    print(f"COMPARISON RESULTS FOR {category.upper()}")
    print("=" * 60)
    
    print("\n📊 API STRATEGY:")
    print(f"Total Available: {api_stats['total_available']}")
    print(f"Products Found: {api_stats['products_found']}")
    print(f"Pages Processed: {api_stats['pages_processed']}")
    print(f"Duration: {api_stats['duration_seconds']} seconds")
    print(f"Speed: {api_stats['products_per_second']} products/second")
    print(f"Errors: {api_stats['errors']}")
    
    print("\n📊 SCROLL STRATEGY:")
    print(f"Products Found: {scroll_stats['products_found']}")
    print(f"Pages Processed: {scroll_stats['pages_processed']}")
    print(f"Duration: {scroll_stats['duration_seconds']} seconds")
    print(f"Speed: {scroll_stats['products_per_second']} products/second")
    print(f"Errors: {scroll_stats['errors']}")
    
    print("\n📈 COMPARISON:")
    diff = api_stats["products_found"] - scroll_stats["products_found"]
    print(f"Difference (API - Scroll): {diff} products")
    print(f"More Products: {'API' if diff > 0 else 'Scroll'}")
    print(f"Faster Strategy: {'API' if api_stats['products_per_second'] > scroll_stats['products_per_second'] else 'Scroll'}")
    print("=" * 60 + "\n")

def main():
    categories = {
        'football': 'football-1gdj0',
        'basketball': 'basketball-3glsm',
        'running': 'running-37v7j'
    }
    
    for category_name, category_id in categories.items():
        print(f"\nProcessing {category_name} category...")
        
        # Test API strategy
        print("\nTesting API strategy...")
        api_stats = NikeStats()
        api_products = get_nike_products_api(category_id, api_stats)
        
        # Test scroll strategy
        print("\nTesting scroll strategy...")
        scroll_stats = NikeStats()
        scroll_products = get_nike_products_scroll(category_id, scroll_stats)
        
        # Save and print comparison
        filename = save_comparison_results(
            category_name,
            api_stats.to_dict(),
            scroll_stats.to_dict(),
            api_products,
            scroll_products
        )
        print(f"\nSaved detailed comparison to responses/{filename}")
        
        print_comparison(category_name, api_stats.to_dict(), scroll_stats.to_dict())
        
        # Wait between categories
        time.sleep(2)

if __name__ == "__main__":
    main() 