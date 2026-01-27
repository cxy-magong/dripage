#!/usr/bin/env python
"""
Simple test for LangGraph browser agent - just navigate and screenshot
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langgraph_browser_agent import run_browser_agent
from utils.logu import get_logger

logger = get_logger('simple_test')


async def test_navigate_and_screenshot():
    """Test basic navigate and screenshot functionality"""
    logger.info("Testing navigate and screenshot...")

    # Test query - just navigate to Baidu
    test_query = "访问百度"

    try:
        result = await run_browser_agent(test_query)

        # Print results
        print(f"\n{'=' * 80}")
        print("SIMPLE TEST RESULT")
        print(f"{'=' * 80}")
        print(f"Status: {result.get('status')}")
        print(f"Current URL: {result.get('current_url')}")
        print(f"Screenshot: {result.get('screenshot_path')}")
        print(f"Error: {result.get('error_message')}")
        print(f"{'=' * 80}")

        # Verify screenshot was created
        from utils.drission_page import create_browser
        page = create_browser()
        print(f"\nCurrent page URL: {page.url}")
        print(f"Current page title: {page.title}")

        return result.get('status') != 'error'

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_navigate_and_screenshot())
    sys.exit(0 if success else 1)
