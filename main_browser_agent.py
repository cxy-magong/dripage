#!/usr/bin/env python
"""
Browser Agent Main Entry Point

Unified entry point for the LangGraph browser agent
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from src.browser_agent import create_browser_agent_app
from utils.logu import get_logger

logger = get_logger('browser_agent_main')


async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<user request>\"")
        print("\nExamples:")
        print('  python main.py "访问百度，搜索 14400f CPU 的价格"')
        print('  python main.py "访问 Google，搜索 LangChain"')
        print('  python main.py "访问百度，点击搜索按钮"')
        print('\nFeatures:')
        print('  - LangGraph state management')
        print('  - GLM-4.7 main agent with reflection')
        print('  - GLM-4.1V vision for element detection')
        print('  - Coordinate conversion from 999x999 to original image')
        print('  - Text input functionality')
        print('  - Modular architecture')
        sys.exit(1)

    user_request = sys.argv[1]
    logger.info("=" * 80)
    logger.info("LangGraph Browser Agent (Modular)")
    logger.info("=" * 80)
    logger.info(f"User request: {user_request}")
    logger.info("")

    # Get agent app
    app = create_browser_agent_app()

    # Initialize state
    initial_state = {
        "messages": [f"User request: {user_request}"],
        "current_url": None,
        "page_title": None,
        "screenshot_path": None,
        "image_width": None,
        "image_height": None,
        "vision_query": None,
        "glm_coordinates": None,
        "converted_coordinates": None,
        "target_element": None,
        "click_coordinates": None,
        "text_to_input": None,
        "input_box_coordinates": None,
        "status": "idle",
        "error_message": None
    }

    # Parse user request to extract URL and set vision query
    # Simple pattern matching for common scenarios
    if "访问" in user_request or "打开" in user_request:
        if "百度" in user_request:
            initial_state["current_url"] = "https://www.baidu.com"
            initial_state["vision_query"] = "找到搜索按钮并返回其坐标"

    # Run agent
    try:
        final_state = await app.ainvoke(initial_state)

        logger.info("")
        logger.info("=" * 80)
        logger.info("Agent Execution Complete")
        logger.info("=" * 80)
        logger.info(f"Final status: {final_state.get('status')}")
        logger.info(f"Current URL: {final_state.get('current_url')}")
        logger.info(f"Screenshot: {final_state.get('screenshot_path')}")

        # Check success criteria
        if final_state.get('status') == 'complete':
            current_url = final_state.get('current_url', '')
            if 'wd=' in current_url:
                logger.info("✓ Search results page detected")
                search_query = current_url.split('wd=')[1].split('&')[0]
                logger.info(f"Search query: {search_query}")
                print("\n" + "=" * 80)
                print("✅ SUCCESS!")
                print("Search results page loaded successfully")
                print("=" * 80)
            else:
                logger.info("✓ Task completed")
                print("\n" + "=" * 80)
                print("✅ SUCCESS!")
                print("Task completed successfully")
                print("=" * 80)
        else:
            error = final_state.get('error_message')
            if error:
                logger.error(f"Error: {error}")
                print("\n" + "=" * 80)
                print("❌ FAILED!")
                print(f"Error: {error}")
                print("=" * 80)
            else:
                logger.error(f"Unknown status: {final_state.get('status')}")
                print("\n" + "=" * 80)
                print("❌ FAILED!")
                print(f"Unknown error occurred")
                print("=" * 80)

        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\nInterrupted")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 80)
        print("❌ FAILED!")
        print(f"Error: {str(e)}")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
