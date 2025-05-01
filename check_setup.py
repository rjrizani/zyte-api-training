"""
Check if all required dependencies are installed and API key is configured.
"""

import sys
import pkg_resources
import os

def check_package(package_name):
    """Check if a package is installed."""
    try:
        pkg_resources.require(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def main():
    # Required packages
    required_packages = [
        'python-dotenv',
        'requests',
        'parsel',
        'beautifulsoup4',
        'zyte-api'
    ]
    
    # Check packages
    missing_packages = []
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    if missing_packages:
        print("\n❌ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        sys.exit(1)
    else:
        print("\n✅ All required packages are installed")
    
    # Check API key
    api_key = os.getenv('ZYTE_API_KEY')
    if not api_key:
        print("\n❌ ZYTE_API_KEY not found!")
        print("Please set up your API key using one of these methods:")
        print("\n1. Create a .env file with:")
        print("ZYTE_API_KEY=your_api_key_here")
        print("\n2. Set environment variable:")
        print("export ZYTE_API_KEY=your_api_key_here")
        sys.exit(1)
    else:
        print("✅ ZYTE_API_KEY is configured")
    
    print("\n✨ Setup complete! You can now run the examples:")
    print("python test_examples.py")

if __name__ == "__main__":
    main() 