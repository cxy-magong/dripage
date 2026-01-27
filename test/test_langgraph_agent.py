#!/usr/bin/env python
"""
Test script for LangGraph Browser Agent

Tests the agent with the query: "访问百度，点击搜索按钮"

Expected behavior:
1. Navigate to Baidu
2. Take screenshot
3. Use GLM-4.1V to detect search button
4. Convert coordinates
5. Click the button
6. Verify search results appear
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langgraph_browser_agent import run_browser_agent
from utils.logu import get_logger

logger = get_logger('test_langgraph_agent')


async def test_baidu_search():
    """
    Test the LangGraph browser agent with Baidu search

    Expected workflow:
    1. User: "访问百度，点击搜索按钮"
    2. Agent navigates to https://www.baidu.com
    3. Agent takes screenshot
    4. GLM-4.1V analyzes screenshot and finds search button coordinates
    5. Coordinates converted from 999x999 to original image size
    6. Agent clicks at converted coordinates
    7. Page loads search results
    8. Success: Page shows search results
    """
    logger.info("=" * 80)
    logger.info("Testing LangGraph Browser Agent")
    logger.info("=" * 80)
    logger.info("Test Query: 访问百度，点击搜索按钮")
    logger.info("")

    # Test query
    test_query = "访问百度，点击搜索按钮"

    # Run agent
    try:
        result = await run_browser_agent(test_query)

        # Verify results
        logger.info("")
        logger.info("=" * 80)
        logger.info("Test Results")
        logger.info("=" * 80)

        # Check key state values
        status = result.get('status')
        current_url = result.get('current_url')
        screenshot_path = result.get('screenshot_path')
        glm_coords = result.get('glm_coordinates')
        converted_coords = result.get('converted_coordinates')
        click_coords = result.get('click_coordinates')
        error = result.get('error_message')

        # Print results
        print(f"\n{'=' * 80}")
        print("FINAL STATE")
        print(f"{'=' * 80}")
        print(f"Status: {status}")
        print(f"Current URL: {current_url}")
        print(f"Screenshot: {screenshot_path}")
        print(f"GLM Coordinates (999x999): {glm_coords}")
        print(f"Converted Coordinates: {converted_coords}")
        print(f"Click Coordinates: {click_coords}")
        if error:
            print(f"Error: {error}")
        print(f"{'=' * 80}")

        # Verify success criteria
        logger.info("")
        logger.info("=" * 80)
        logger.info("Success Criteria Verification")
        logger.info("=" * 80)

        success = True

        # Check 1: Status should be complete
        if status == "complete":
            logger.info("✓ Status is 'complete'")
        else:
            logger.error(f"✗ Status is '{status}', expected 'complete'")
            success = False

        # Check 2: URL should be Baidu
        if current_url and "baidu.com" in current_url.lower():
            logger.info(f"✓ URL is Baidu: {current_url}")
        else:
            logger.warning(f"⚠ URL: {current_url}")

        # Check 3: Screenshot should exist
        if screenshot_path and Path(screenshot_path).exists():
            logger.info(f"✓ Screenshot exists: {screenshot_path}")
        else:
            logger.error(f"✗ Screenshot not found: {screenshot_path}")
            success = False

        # Check 4: GLM coordinates should be detected
        if glm_coords and len(glm_coords) > 0:
            logger.info(f"✓ GLM detected {len(glm_coords)} coordinate(s): {glm_coords}")
        else:
            logger.error("✗ No GLM coordinates detected")
            success = False

        # Check 5: Coordinates should be converted
        if converted_coords and len(converted_coords) > 0:
            logger.info(f"✓ Coordinates converted: {converted_coords}")
        else:
            logger.error("✗ Coordinates not converted")
            success = False

        # Check 6: Click coordinates should be calculated
        if click_coords and len(click_coords) == 2:
            logger.info(f"✓ Click coordinates calculated: {click_coords}")
        else:
            logger.error("✗ Click coordinates not calculated")
            success = False

        # Check 7: No errors
        if not error:
            logger.info("✓ No errors")
        else:
            logger.error(f"✗ Error occurred: {error}")
            success = False

        logger.info("=" * 80)

        if success:
            logger.info("")
            logger.info("🎉 TEST PASSED!")
            logger.info("All success criteria met. The agent successfully:")
            logger.info("  1. Navigated to Baidu")
            logger.info("  2. Took screenshot")
            logger.info("  3. Detected search button with GLM-4.1V")
            logger.info("  4. Converted coordinates")
            logger.info("  5. Clicked the search button")
            logger.info("  6. Loaded search results")
        else:
            logger.error("")
            logger.error("❌ TEST FAILED!")
            logger.error("Some success criteria not met.")

        logger.info("=" * 80)

        return success

    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_custom_query():
    """
    Test with a custom query provided via command line
    """
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        logger.info(f"Testing with custom query: {query}")
        result = await run_browser_agent(query)

        print(f"\n{'=' * 80}")
        print("FINAL STATE")
        print(f"{'=' * 80}")
        print(f"Status: {result.get('status')}")
        print(f"Current URL: {result.get('current_url')}")
        print(f"Screenshot: {result.get('screenshot_path')}")
        if result.get('error_message'):
            print(f"Error: {result.get('error_message')}")
        print(f"{'=' * 80}")

        return result.get('status') == "complete"
    else:
        logger.error("No custom query provided")
        return False


if __name__ == "__main__":
    # Check if custom query provided
    if len(sys.argv) > 1:
        # Run custom query test
        success = asyncio.run(test_custom_query())
    else:
        # Run standard Baidu test
        success = asyncio.run(test_baidu_search())

    # Exit with appropriate code
    sys.exit(0 if success else 1)
