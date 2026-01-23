#!/usr/bin/env python
"""
Test get2md command
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from cli import cli

if __name__ == '__main__':
    print("Testing get2md command...")
    print("-" * 80)

    # Test with example.com
    test_url = "https://www.example.com"

    # Simulate command line args
    sys.argv = ['cli.py', 'get2md', test_url]

    try:
        cli()
        print("-" * 80)
        print("Test completed successfully!")
    except Exception as e:
        print("-" * 80)
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
