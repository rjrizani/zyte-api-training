import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ZYTE_API_KEY = os.getenv('ZYTE_API_KEY')
ZYTE_API_ENDPOINT = "https://api.zyte.com/v1/extract"

def basic_scraper(url):
    response = requests.post(
        ZYTE_API_ENDPOINT,
        auth=(ZYTE_API_KEY, ""),
        json= {
            "url": url,
            "browserHtml": True,
            # "httpResponseBody": True
            #"product": True,
            #"productList": True,
            #"article": True,
            #"articleList": True,
            # "actions": [
            #     {
            #         "action": "wait",
            #         "value": 10000
            #     }
            # ]
        }
    )
    return response.json()

if __name__ == "__main__":
    url = "<enter url here>"
    result = basic_scraper(url)
    print(result)