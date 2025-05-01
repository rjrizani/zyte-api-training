import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Please run: pip install python-dotenv")
    print("Alternatively, you can set ZYTE_API_KEY environment variable directly")

# API Configuration
ZYTE_API_KEY = os.getenv('ZYTE_API_KEY')
if not ZYTE_API_KEY:
    raise ValueError(
        "ZYTE_API_KEY environment variable not set!\n"
        "Please either:\n"
        "1. Create a .env file with your API key: ZYTE_API_KEY=your_api_key_here\n"
        "2. Set the environment variable: export ZYTE_API_KEY=your_api_key_here"
    )

# API Endpoints
ZYTE_API_ENDPOINT = "https://api.zyte.com/v1/extract"

# Default request configuration
DEFAULT_CONFIG = {
    "browserHtml": True,
    "javascript": True,
    "timeout": 30000
}

# Network capture configuration
NETWORK_CAPTURE_CONFIG = {
    "filterType": "url",
    "matchType": "contains",
    "httpResponseBody": True
}

# Pagination settings
PAGINATION_TIMEOUT = 10000  # 10 seconds
SCROLL_PAUSE_TIME = 2000    # 2 seconds

# Common selectors
SELECTORS = {
    "next_button": ".next-page",
    "load_more": ".load-more",
    "search_input": "input#searchBox",
    "submit_button": "button#submitSearch"
} 