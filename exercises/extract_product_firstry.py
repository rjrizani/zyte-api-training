import sys
from pathlib import Path
import requests
import json
import time
from bs4 import BeautifulSoup

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.config import ZYTE_API_KEY, ZYTE_API_ENDPOINT, SCROLL_PAUSE_TIME

api_response = requests.post(
    "https://api.zyte.com/v1/extract",
    auth= (ZYTE_API_KEY, ""),
   
    json={
        "url": "https://www.firstcry.com/searchresult?sale=6&searchstring=brand@@@@1@0@20@@@@@@@@@@@@@@@@&sort=bestseller&gender=boy,unisex&ref2=menu_dd_boy-fashion_bestsellers_V#sale=6&searchstring=brand@@@@1@0@20@@@@@@@@@@@@@@@@@@@@@&rating=&sort=bestseller&&vi=three&pmonths=&cgen=&skills=&measurement=&material=&curatedcollections=&Color=&Age=&gender=both,male&ser=&premium=&deliverytype=&PageNo=1&scrollPos=0&pview=&tc=97040",
        "productList": True,
        "productListOptions": {"extractFrom":"browserHtml"},
"""      
  "customAttributes": {
                            "price_details": {
                                "type": "object",
                                "properties": {
                                "regular": {
                                    "type": "number",
                                    "description": "the regular price of the product. This is, without any discount"
                                },
                                "discounted": {
                                    "type": "number",
                                    "description": "the current price of the product, with the discount"
                                },
                                "unit": {
                                    "type": "string",
                                    "description": "the currency code of the price, usually given as a 3-letter code, e.g. USD, EUR, GBP, etc."
                                }
                                }},
                            
                        },
"""
        "javascript": True,
    },
)

#save api response to json file
with open("api_response1.json", "w", encoding="utf-8") as fp:
    json.dump(api_response.json(), fp, indent=2, ensure_ascii=False)


