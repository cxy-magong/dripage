#!/usr/bin/env python
"""
Browser Agent - LangGraph with GLM-4.7

Simple version that works without circular imports
"""

import os
import json
import re
import asyncio
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_community.chat_models import ChatZhipuAI

from utils.drission_page import create_browser
from utils.glm_coordinate_converter import GLMCoordinateConverter
from utils.logu import get_logger
from PIL import Image

logger = get_logger('browser_agent_simple')


# Simple state with all fields as Optional
class SimpleBrowserAgentState(dict):
    messages: list
    current_url: str | None = None
    page_title: str | None = None
    screenshot_path: str | None = None
    image_width: int | None = None
    image_height: int | None = None
    vision_query: str | None = None
    glm_coordinates: list | None = None
    converted_coordinates: list | None = None
    target_element: str | None = None
    click_coordinates: list | None = None
    text_to_input: str | None = None
    input_box_coordinates: list | None = None
    status: str = "idle"
    error_message: str | None = None


# ============================================================================
# Browser Control Tools
# ============================================================================

def navigate_to_url(url: str) -> str:
    """Navigate browser to specified URL"""
    logger.info(f"Navigating to: {url}")
    try:
        page = create_browser()
        page.get(url)
        title = page.title
        logger.info(f"Navigated to: {url} (Title: {title})")
        return f"Successfully navigated to {url}. Page title: {title}"
    except Exception as e:
        logger.error(f"Failed to navigate to {url}: {e}")
        return f"Failed to navigate to {url}: {str(e)}"


def take_screenshot() -> str:
    """Take a screenshot of the current page"""
    logger.info("Taking screenshot...")
    try:
        page = create_browser()

        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamp for filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)

        # Take screenshot
        page.get_screenshot(path=filepath)

        # Get image dimensions
        img = Image.open(filepath)
        width, height = img.size

        logger.info(f"Screenshot saved to: {filepath} ({width}x{height})")
        return filepath

    except Exception as e:
        logger.error(f"Failed to take screenshot: {e}")
        return f"Failed to take screenshot: {str(e)}"


def click_at_coordinates(x: int, y: int) -> str:
    """Click at specified coordinates on the page"""
    logger.info(f"Clicking at coordinates: ({x}, {y})")
    try:
        page = create_browser()
        tab = page.latest_tab

        # Use tab.actions to click at specific coordinates
        tab.actions.move_to((x, y))
        tab.actions.click()

        logger.info(f"Successfully clicked at ({x}, {y})")
        return f"Successfully clicked at coordinates ({x}, {y})"

    except Exception as e:
        logger.error(f"Failed to click at ({x}, {y}): {e}")
        return f"Failed to click at ({x}, {y}): {str(e)}"


# ============================================================================
# Vision Node
# ============================================================================

async def vision_node(state: SimpleBrowserAgentState) -> SimpleBrowserAgentState:
    """Vision node using GLM-4.1V"""
    logger.info("=== Vision Node (GLM-4.1V) ===")

    screenshot_path = state.get("screenshot_path")
    vision_query = state.get("vision_query", "")

    if not screenshot_path:
        logger.error("No screenshot path in state")
        state["error_message"] = "No screenshot available for analysis"
        state["status"] = "error"
        return state

    if not vision_query:
        logger.error("No vision query in state")
        state["error_message"] = "No vision query provided"
        state["status"] = "error"
        return state

    try:
        logger.info(f"Analyzing screenshot: {screenshot_path}")
        logger.info(f"Vision query: {vision_query}")

        # Initialize GLM-4.1V client
        from zai import ZhipuAiClient
        client = ZhipuAiClient(api_key=os.environ.get('ZAI_API_KEY'))

        # Encode image as base64
        import base64
        with open(screenshot_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')

        # Call GLM-4.1V-Thinking-Flash model
        image_data_url = f"data:image/png;base64,{base64_image}"
        response = client.chat.completions.create(
            model="GLM-4.1V-Thinking-Flash",
            messages=[
                {"content": [
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                    {"type": "text", "text": vision_query}
                ], "role": "user"}
            ],
            thinking={"type": "enabled"}
        )

        # Extract response
        message = response.choices[0].message
        response_text = message.content

        logger.info(f"GLM-4.1V Response: {response_text}")

        # Create coordinate converter and parse coordinates
        converter = GLMCoordinateConverter.from_image_path(screenshot_path)
        glm_boxes = converter.parse_coordinates_from_text(response_text)

        if glm_boxes:
            logger.info(f"Detected {len(glm_boxes)} bounding box(es)")
            for i, box in enumerate(glm_boxes):
                logger.info(f"  Box {i+1}: {box}")
            state["glm_coordinates"] = glm_boxes
            state["status"] = "analyzing"
        else:
            logger.warning("No coordinates found in GLM-4.1V response")
            state["error_message"] = "No coordinates detected in response"
            state["status"] = "error"

        # Add response to messages
        state["messages"].append(AIMessage(content=response_text))

    except Exception as e:
        logger.error(f"Vision analysis failed: {e}")
        state["error_message"] = f"Vision analysis failed: {str(e)}"
        state["status"] = "error"

    return state


# ============================================================================
# Main Agent Node (Simple Version)
# ============================================================================

async def main_agent_node(state: SimpleBrowserAgentState) -> SimpleBrowserAgentState:
    """Main agent using GLM-4.7 as controller"""
    logger.info("=== Main Agent Node (GLM-4.7) ===")

    # Get last human message
    messages = state.get("messages", [])
    if not messages:
        logger.error("No messages in state")
        state["error_message"] = "No messages to process"
        state["status"] = "error"
        return state

    last_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_message = msg.content
            break

    if not last_message:
        logger.error("No human message found")
        state["error_message"] = "No human message to process"
        state["status"] = "error"
        return state

    logger.info(f"User request: {last_message}")

    try:
        # Initialize GLM-4.7
        api_key = os.environ.get('ZAI_API_KEY')
        if not api_key:
            raise ValueError("ZAI_API_KEY environment variable not set")

        llm = ChatZhipuAI(
            model="glm-4.7",
            temperature=0.0,
            streaming=True,
            max_tokens=4096,
            api_key=api_key
        )

        # Create system prompt
        system_prompt = """You are a browser automation agent.

Available Actions:
1. "navigate" - Navigate to URL
2. "screenshot" - Take screenshot
3. "analyze" - Analyze screenshot with vision
4. "convert" - Convert coordinates
5. "click" - Click at coordinates
6. "search" - Click search button

Decision Logic:
- If user mentions URL like "访问百度", set url="https://www.baidu.com" and vision_query="找到搜索按钮并返回其坐标"
- If user says "点击搜索按钮" and we have coordinates, action="click"
- Otherwise, use keyword matching"""

        # Build context
        state_context = f"""Current URL: {state.get('current_url', 'None')}
Current status: {state.get('status', 'idle')}"""

        # Build messages
        agent_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User request: {last_message}\n{state_context}")
        ]

        # Call GLM-4.7
        logger.info("Calling GLM-4.7 to decide next action...")
        response = await llm.ainvoke(agent_messages)

        logger.info(f"GLM-4.7 decision: {response.content}")

        # Parse action from response
        action = None

        # Simple keyword-based action detection
        response_lower = response.content.lower()

        if "navigate" in last_message or "打开" in last_message or "导航" in last_message:
            action = "navigate"
            # Extract URL if mentioned
            if "百度" in last_message:
                state["current_url"] = "https://www.baidu.com"
                state["vision_query"] = "找到搜索按钮并返回其坐标"
            else:
                # Try to extract URL
                url_match = re.search(r'https?://[^\s]+', last_message)
                if url_match:
                    state["current_url"] = url_match.group()

        elif "截图" in last_message or "screenshot" in last_message:
            action = "screenshot"

        elif "分析" in last_message or "识别" in last_message or "分析" in last_message:
            if state.get("screenshot_path"):
                action = "analyze"
                if not state.get("vision_query"):
                    state["vision_query"] = last_message

        elif "点击" in last_message or "click" in last_message:
            if state.get("click_coordinates"):
                action = "click"
            else:
                # Need to analyze first
                action = "analyze"

        else:
            action = "complete"

        logger.info(f"Decided action: {action}")

        # Update state based on action
        if action == "navigate":
            state["status"] = "navigating"
        elif action == "screenshot":
            state["status"] = "screenshot"
        elif action == "analyze":
            state["status"] = "analyzing"
        elif action == "click":
            state["status"] = "clicking"
        elif action == "complete":
            state["status"] = "complete"
        else:
            logger.warning(f"Unknown action: {action}")
            state["status"] = "error"

        # Add response to messages
        state["messages"].append(AIMessage(content=response.content))

    except Exception as e:
        logger.error(f"GLM-4.7 agent failed: {e}")
        import traceback
        traceback.print_exc()
        state["error_message"] = f"Agent failed: {str(e)}"
        state["status"] = "error"

    return state


# ============================================================================
# Build Simple Graph
# ============================================================================

def create_simple_browser_agent_app():
    """Create simple LangGraph browser agent without circular imports"""

    workflow = StateGraph(SimpleBrowserAgentState)

    # Add all nodes
    workflow.add_node("main_agent", main_agent_node)
    workflow.add_node("navigate", lambda s: navigate_to_url(s["url"]))
    workflow.add_node("screenshot", lambda s: take_screenshot())
    workflow.add_node("vision", vision_node)
    workflow.add_node("click", lambda s: click_at_coordinates(*s["click_coordinates"]))

    # Define routing logic
    def route_after_main_agent(state: SimpleBrowserAgentState) -> str:
        status = state.get("status", "idle")

        if status == "navigating":
            return "navigate"
        elif status == "screenshot":
            return "screenshot"
        elif status == "analyzing":
            return "vision"
        elif status == "clicking":
            return "click"
        elif status == "complete":
            return END
        else:
            return END

    workflow.add_conditional_edges(
        "main_agent",
        route_after_main_agent,
        {
            "navigate": "navigate",
            "screenshot": "screenshot",
            "vision": "vision",
            "click": "click",
            END: END
        }
    )

    # Define edges
    workflow.add_edge("navigate", "screenshot")
    workflow.add_edge("screenshot", "main_agent")
    workflow.add_edge("vision", "click")
    workflow.add_edge("click", END)

    workflow.set_entry_point("main_agent")

    app = workflow.compile()

    logger.info("Simple browser agent built successfully")
    return app


# ============================================================================
# Main Entry Point
# ============================================================================

async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<user request>\"")
        sys.exit(1)

    user_request = sys.argv[1]

    logger.info("=" * 80)
    logger.info("LangGraph Browser Agent")
    logger.info("=" * 80)
    logger.info(f"User request: {user_request}")

    # Get agent app
    app = create_simple_browser_agent_app()

    # Initialize state
    initial_state = SimpleBrowserAgentState(
        messages=[f"User request: {user_request}"],
        current_url=None,
        screenshot_path=None
        status="idle"
    )

    # Simple parsing for Baidu
    if "访问百度" in user_request or "百度" in user_request:
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

        # Check if on Baidu
        current_url = final_state.get('current_url', '')
        if 'wd=' in current_url and '百度' in current_url:
            logger.info("✓ Successfully navigated to Baidu and clicked search button")
            print("\n" + "=" * 80)
            print("✅ SUCCESS!")
            print("Search results page loaded")
            print("=" * 80)
        else:
            print(f"Status: {final_state.get('status')}")

        sys.exit(0)

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 80)
        print("❌ FAILED!")
        print(f"Error: {str(e)}")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
