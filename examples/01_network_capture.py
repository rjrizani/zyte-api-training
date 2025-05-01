"""
Example 1: Network Capture - Infinite Scroll API Capture
Demonstrates network request capture and analysis using Zyte API.
"""

import sys
from pathlib import Path
import json
from base64 import b64decode
import requests
from typing import Dict, List, Optional
import time
import os

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT

def capture_network_requests(url: str, filter_pattern: str = "/api/", 
                           max_retries: int = 3) -> Optional[List[Dict]]:
    """
    Capture and analyze network requests during page load.
    
    Args:
        url (str): Target URL to analyze
        filter_pattern (str): Pattern to filter network requests
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        list: Processed network captures
    """
    # Define the payload for the Zyte API request
    payload = {
        "url": url,
        "browserHtml": True,
        "actions": [
            {
                "action": "scrollBottom",
            },
        ],
        "networkCapture": [
            {
                "filterType": "url",
                "httpResponseBody": True,
                "value": filter_pattern,
                "matchType": "contains",
            },
        ],
    }
    
    for attempt in range(max_retries):
        try:
            print(f"Capturing network requests (attempt {attempt + 1}/{max_retries})...")
            
            # Send the request to the Zyte API
            response = requests.post(
                ZYTE_API_ENDPOINT,
                auth=(ZYTE_API_KEY, ""),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            captures = result.get("networkCapture", [])
            
            if not captures:
                print("No network captures found. Retrying...")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return None
            
            # Process captures
            return process_captures(captures)
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
            
        except Exception as e:
            print(f"Error: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
    
    return None

def process_captures(captures: List[Dict]) -> List[Dict]:
    """
    Process network captures and extract data.
    
    Args:
        captures (list): Raw network captures
        
    Returns:
        list: Processed data from captures
    """
    processed_data = []
    
    for capture in captures:
        try:
            # Get and decode response body
            body = capture.get("httpResponseBody", "")
            if not body:
                continue
                
            decoded_text = b64decode(body).decode()
            data = json.loads(decoded_text)
            
            # Extract quotes from the response
            for quote in data.get("quotes", []):
                quote_data = {
                    "author": quote["author"]["name"],
                    "tags": quote["tags"],
                    "text": quote["text"],
                    "url": capture.get("url"),  # Include request URL
                    "method": capture.get("method"),  # Include HTTP method
                    "status": capture.get("status"),  # Include HTTP status
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                processed_data.append(quote_data)
                
        except Exception as e:
            print(f"Error processing capture: {str(e)}")
            continue
    
    return processed_data

def save_to_json(data: List[Dict], filename: str = "network_captures.json"):
    """
    Save captured data to a JSON file in the responses directory.
    """
    if not data:
        return
    os.makedirs("responses", exist_ok=True)
    if not filename.startswith("responses/"):
        filename = os.path.join("responses", filename)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'captures': data,
            'metadata': {
                'count': len(data),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }, f, indent=2, ensure_ascii=False)

def main():
    # Example usage with quotes.toscrape.com
    url = "http://quotes.toscrape.com/scroll"
    print(f"Analyzing network requests for: {url}")
    
    captures = capture_network_requests(url, "/api/quotes")
    
    if captures:
        print(f"\nFound {len(captures)} network captures")
        
        # Save to JSON
        filename = f"quotes_network_capture_{time.strftime('%Y%m%d_%H%M%S')}.json"
        save_to_json(captures, filename)
        print(f"Saved results to {filename}")
        
        # Print sample data
        print("\nSample Captured Data:")
        print("-" * 50)
        for capture in captures[:2]:  # Show first 2 captures
            print(f"\nAuthor: {capture['author']}")
            print(f"Text: {capture['text']}")
            print(f"Tags: {', '.join(capture['tags'])}")
            print(f"URL: {capture['url']}")
            print(f"Method: {capture['method']}")
            print(f"Status: {capture['status']}")
            print("-" * 30)
    else:
        print("No network captures found or error occurred")

if __name__ == "__main__":
    main() 