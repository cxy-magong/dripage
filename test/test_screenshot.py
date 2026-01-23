#!/usr/bin/env python
"""
Test screenshot command
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
    print("Testing screenshot command...")
    print("-" * 80)

    # First navigate to a page
    print("Step 1: Navigating to example.com...")
    try:
        page = create_browser()
        page.get("https://www.example.com")
        print("✓ Page loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load page: {e}")
        sys.exit(1)

    print()
    print("Step 2: Taking screenshot...")

    # Simulate command line args
    sys.argv = ['cli.py', 'screenshot']

    try:
        cli()
        print("-" * 80)
        print("✓ Test completed successfully!")
        print("Check output/images/ directory for the screenshot.")
    except Exception as e:
        print("-" * 80)
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
