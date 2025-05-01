"""
Test script to verify all examples are working correctly.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify Zyte API key is set
if not os.getenv('ZYTE_API_KEY'):
    print("Error: ZYTE_API_KEY environment variable not set!")
    print("Please create a .env file with your Zyte API key:")
    print('ZYTE_API_KEY=your_api_key_here')
    sys.exit(1)

def run_example(filename):
    """Run an example file and check its output."""
    print(f"\nTesting {filename}...")
    print("-" * 50)
    
    try:
        # Run the example
        result = os.system(f"python examples/{filename}")
        
        if result == 0:
            print(f"✅ {filename} completed successfully")
            return True
        else:
            print(f"❌ {filename} failed with exit code {result}")
            return False
            
    except Exception as e:
        print(f"❌ {filename} failed with error: {str(e)}")
        return False

def main():
    # List of examples to test
    examples = [
        "01_network_capture.py",
        "02_pagination_classic.py",
        "03_infinite_scroll.py",
        "04_form_submission.py"
    ]
    
    # Results tracking
    results = {
        "success": [],
        "failed": []
    }
    
    # Run each example
    for example in examples:
        if run_example(example):
            results["success"].append(example)
        else:
            results["failed"].append(example)
        time.sleep(2)  # Pause between examples
    
    # Print summary
    print("\nTest Results Summary")
    print("=" * 50)
    print(f"Total examples: {len(examples)}")
    print(f"Successful: {len(results['success'])}")
    print(f"Failed: {len(results['failed'])}")
    
    if results["failed"]:
        print("\nFailed examples:")
        for example in results["failed"]:
            print(f"- {example}")
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Check for output files
    print("\nChecking output files...")
    for example in results["success"]:
        base_name = example.split(".")[0]
        files = list(output_dir.glob(f"{base_name}*"))
        if files:
            print(f"\n{base_name} output files:")
            for file in files:
                print(f"- {file.name}")

if __name__ == "__main__":
    main() 