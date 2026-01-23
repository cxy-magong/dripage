#!/usr/bin/env python
"""
Test vision command
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from utils.drission_page import create_browser
from cli import cli

if __name__ == '__main__':
    print("Testing vision command...")
    print("-" * 80)

    # Check if API key is set
    api_key = os.environ.get('ZAI_API_KEY')
    if not api_key:
        print("✗ Error: ZAI_API_KEY environment variable not set")
        print("Please set it with: export ZAI_API_KEY=your_key")
        sys.exit(1)

    print(f"✓ API key found: {api_key[:20]}...")

    # First navigate to a page
    print()
    print("Step 1: Navigating to example.com...")
    try:
        page = create_browser()
        page.get("https://www.example.com")
        print("✓ Page loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load page: {e}")
        sys.exit(1)

    print()
    print("Step 2: Analyzing page with GLM-4V vision model...")

    # Simulate command line args
    sys.argv = ['cli.py', 'vision', '描述这个网页的主要内容', '--model', 'glm-4v-flash']

    try:
        cli()
        print("-" * 80)
        print("✓ Test completed successfully!")
    except Exception as e:
        print("-" * 80)
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
