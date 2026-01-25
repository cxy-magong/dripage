#!/usr/bin/env python
"""
LangGraph Browser Agent

A LangGraph-based agent for browser automation with vision capabilities.
- Uses GLM-4.7 as the main controller agent
- Uses GLM-4.1V for vision/element detection
- Shares state across nodes for screenshots and coordinate conversion
- Implements browser control tools that can access state
"""

import os
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate
from PIL import Image
import asyncio
import operator

from utils.drission_page import create_browser
from utils.glm_coordinate_converter import GLMCoordinateConverter
from utils.logu import get_logger
from zai import ZhipuAiClient

logger = get_logger('langgraph_browser_agent')


# ============================================================================
# State Definition
# ============================================================================

class BrowserAgentState(TypedDict):
    """State for the browser agent graph

    This state is shared across all nodes in the graph.
    """
    # Agent messages - use operator.add to append messages
    messages: Annotated[List[BaseMessage], operator.add]

    # Browser state
    current_url: Optional[str]
    page_title: Optional[str]

    # Screenshot state (shared between nodes)
    screenshot_path: Optional[str]
    image_width: Optional[int]
    image_height: Optional[int]

    # Vision detection state
    vision_query: Optional[str]
    glm_coordinates: Optional[List[List[int]]]  # Coordinates from GLM-4.1V (999x999)
    converted_coordinates: Optional[List[List[int]]]  # Converted to original image size

    # Action state
    target_element: Optional[str]  # Description of element to click
    click_coordinates: Optional[List[int]]  # Final coordinates to click [x, y]

    # Status and results
    status: str  # "idle", "navigating", "analyzing", "clicking", "complete"
    error_message: Optional[str]


# ============================================================================
# Browser Control Tools
# ============================================================================

@tool
def navigate_to_url(url: str) -> str:
    """
    Navigate the browser to the specified URL

    Args:
        url: The URL to navigate to

    Returns:
        Success message with current page title
    """
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


@tool
def take_screenshot() -> str:
    """
    Take a screenshot of the current page

    Returns:
        Path to the saved screenshot file
    """
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
        logger.info(f"Screenshot saved to: {filepath}")

        return filepath
    except Exception as e:
        logger.error(f"Failed to take screenshot: {e}")
        return f"Failed to take screenshot: {str(e)}"


@tool
def click_at_coordinates(x: int, y: int) -> str:
    """
    Click at the specified coordinates on the page

    Args:
        x: X coordinate
        y: Y coordinate

    Returns:
        Success message
    """
    logger.info(f"Clicking at coordinates: ({x}, {y})")
    try:
        page = create_browser()
        tab = page.latest_tab

        # Use tab.actions to click at specific coordinates
        tab.actions.move_to((x, y))
        tab.actions.click()

        logger.info(f"Clicked at ({x}, {y})")
        return f"Successfully clicked at coordinates ({x}, {y})"
    except Exception as e:
        logger.error(f"Failed to click at ({x}, {y}): {e}")
        return f"Failed to click at ({x}, {y}): {str(e)}"


# ============================================================================
# Vision Node (GLM-4.1V)
# ============================================================================

async def vision_node(state: BrowserAgentState) -> BrowserAgentState:
    """
    Vision node using GLM-4.1V to detect elements on the page

    This node:
    1. Reads screenshot path from state
    2. Calls GLM-4.1V to analyze the image
    3. Parses coordinates from the response
    4. Updates state with GLM coordinates

    Args:
        state: Current state (contains screenshot_path and vision_query)

    Returns:
        Updated state with glm_coordinates
    """
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

        # Encode image as base64
        import base64
        with open(screenshot_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')

        # Initialize GLM-4.1V client
        client = ZhipuAiClient(api_key=os.environ.get('ZAI_API_KEY'))

        # Call GLM-4.1V-Thinking-Flash model with thinking enabled
        # Use data URL scheme for local image
        image_data_url = f"data:image/png;base64,{base64_image}"

        response = client.chat.completions.create(
            model="GLM-4.1V-Thinking-Flash",
            messages=[
                {
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data_url
                            }
                        },
                        {
                            "type": "text",
                            "text": vision_query
                        }
                    ],
                    "role": "user"
                }
            ],
            thinking={
                "type": "enabled"
            }
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

    if not vision_query:
        logger.error("No vision query in state")
        state["error_message"] = "No vision query provided"
        state["status"] = "error"
        return state

    try:
        logger.info(f"Analyzing screenshot: {screenshot_path}")
        logger.info(f"Vision query: {vision_query}")

        # Initialize GLM-4.1V client
        client = ZhipuAiClient(api_key=os.environ.get('ZAI_API_KEY'))

        # Call GLM-4.1V-Thinking-Flash model with thinking enabled
        response = client.chat.completions.create(
            model="GLM-4.1V-Thinking-Flash",
            messages=[
                {
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": screenshot_path
                            }
                        },
                        {
                            "type": "text",
                            "text": vision_query
                        }
                    ],
                    "role": "user"
                }
            ],
            thinking={
                "type": "enabled"
            }
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
# Coordinate Conversion Node
# ============================================================================

async def coordinate_conversion_node(state: BrowserAgentState) -> BrowserAgentState:
    """
    Convert GLM coordinates to original image coordinates

    This node:
    1. Reads glm_coordinates from state (999x999 space)
    2. Reads image dimensions from state
    3. Converts to original image coordinates
    4. Updates state with converted_coordinates

    Args:
        state: Current state (contains glm_coordinates and image dimensions)

    Returns:
        Updated state with converted_coordinates
    """
    logger.info("=== Coordinate Conversion Node ===")

    screenshot_path = state.get("screenshot_path")
    glm_coordinates = state.get("glm_coordinates")

    if not screenshot_path:
        logger.error("No screenshot path in state for coordinate conversion")
        state["error_message"] = "No screenshot available for coordinate conversion"
        state["status"] = "error"
        return state

    if not glm_coordinates:
        logger.error("No GLM coordinates to convert")
        state["error_message"] = "No GLM coordinates available"
        state["status"] = "error"
        return state

    try:
        # Create converter
        converter = GLMCoordinateConverter.from_image_path(screenshot_path)

        # Convert all boxes
        converted_boxes = converter.convert_boxes(glm_coordinates)

        logger.info(f"Converted {len(converted_boxes)} coordinate(s):")
        for i, (original, converted) in enumerate(zip(glm_coordinates, converted_boxes)):
            logger.info(f"  Box {i+1}: {original} -> {converted}")

        state["converted_coordinates"] = converted_boxes

        # Calculate click coordinates (center of first box)
        if converted_boxes:
            box = converted_boxes[0]
            center_x = (box[0] + box[2]) // 2
            center_y = (box[1] + box[3]) // 2
            state["click_coordinates"] = [center_x, center_y]
            logger.info(f"Click coordinates calculated: ({center_x}, {center_y})")

        state["status"] = "clicking"

    except Exception as e:
        logger.error(f"Coordinate conversion failed: {e}")
        state["error_message"] = f"Coordinate conversion failed: {str(e)}"
        state["status"] = "error"

    return state


# ============================================================================
# Main Agent Node (GLM-4.7)
# ============================================================================

# Initialize GLM-4.7 as the main controller
def get_glm_4_7_agent():
    """
    Get GLM-4.7 model configured for agent use

    Returns:
        ChatZhipuAI model instance configured for agent workflows
    """
    try:
        api_key = os.environ.get('ZAI_API_KEY')
        if not api_key:
            raise ValueError("ZAI_API_KEY environment variable not set")

        llm = ChatZhipuAI(
            model="glm-4.7",
            temperature=0.0,  # Use 0.0 for deterministic agent behavior
            streaming=True,
            max_tokens=4096,
            api_key=api_key
        )

        logger.info("GLM-4.7 agent initialized successfully")
        return llm

    except Exception as e:
        logger.error(f"Failed to initialize GLM-4.7: {e}")
        raise


async def main_agent_node(state: BrowserAgentState) -> BrowserAgentState:
    """
    Main agent node using GLM-4.7 as controller

    This node:
    1. Analyzes user request using GLM-4.7
    2. Decides which tools/nodes to call based on analysis
    3. Orchestrates the workflow

    Args:
        state: Current state

    Returns:
        Updated state with agent decision
    """
    logger.info("=== Main Agent Node (GLM-4.7) ===")

    # Get messages from state
    messages = state.get("messages", [])
    if not messages:
        logger.error("No messages in state")
        state["error_message"] = "No messages to process"
        state["status"] = "error"
        return state

    # Get last human message
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
        # Get GLM-4.7 agent
        llm = get_glm_4_7_agent()

        # Create system prompt for agent decision-making
        system_prompt = """You are a browser automation agent. Your job is to analyze the user's request and decide what action to take.

Available actions:
1. "navigate" - Navigate to a URL. Extract the URL from the user's request.
2. "screenshot" - Take a screenshot of the current page.
3. "analyze" - Analyze the screenshot to find elements (requires screenshot_path in state).
4. "click" - Click at coordinates (requires converted_coordinates in state).
5. "complete" - Task is complete, no further action needed.

Analyze the user's request and current state to determine the next action.
Respond with only the action name in JSON format: {"action": "action_name"}

Example responses:
- "访问百度" -> {"action": "navigate"}
- "点击搜索按钮" (when screenshot exists) -> {"action": "analyze"}
- "点击搜索按钮" (when coordinates ready) -> {"action": "click"}
- Task complete -> {"action": "complete"}"""

        # Build context about current state
        state_context = f"""Current state:
- Current URL: {state.get('current_url', 'None')}
- Screenshot path: {state.get('screenshot_path', 'None')}
- Vision query: {state.get('vision_query', 'None')}
- GLM coordinates: {state.get('glm_coordinates', 'None')}
- Converted coordinates: {state.get('converted_coordinates', 'None')}
- Click coordinates: {state.get('click_coordinates', 'None')}
- Current status: {state.get('status', 'idle')}"""

        # Create messages for GLM-4.7
        agent_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User request: {last_message}\n\n{state_context}")
        ]

        # Call GLM-4.7 to decide action
        logger.info("Calling GLM-4.7 to decide next action...")
        response = await llm.ainvoke(agent_messages)

        logger.info(f"GLM-4.7 decision: {response.content}")

        # Parse action from response
        import json
        import re

        # Extract JSON from response
        json_match = re.search(r'\{[^}]+\}', response.content)
        if json_match:
            action_json = json.loads(json_match.group())
            action = action_json.get('action', '').lower()

            logger.info(f"Decided action: {action}")

            # Update state based on action
            if action == "navigate":
                state["status"] = "navigating"
                # Extract URL from request
                if "百度" in last_message:
                    state["current_url"] = "https://www.baidu.com"
                    state["vision_query"] = "找到搜索按钮并返回其坐标"
                else:
                    # Try to extract URL
                    url_match = re.search(r'https?://[^\s]+', last_message)
                    if url_match:
                        state["current_url"] = url_match.group()
                        state["vision_query"] = "找到相关元素并返回其坐标"
                    else:
                        state["error_message"] = "URL not recognized"
                        state["status"] = "error"

            elif action == "screenshot":
                state["status"] = "screenshot"

            elif action == "analyze":
                if state.get("screenshot_path"):
                    state["status"] = "analyzing"
                    state["vision_query"] = state.get("vision_query") or last_message
                else:
                    state["error_message"] = "No screenshot available for analysis"
                    state["status"] = "error"

            elif action == "click":
                if state.get("click_coordinates"):
                    state["status"] = "clicking"
                elif state.get("converted_coordinates"):
                    # Calculate click coordinates
                    converted_coords = state.get("converted_coordinates")
                    if converted_coords and len(converted_coords) > 0:
                        box = converted_coords[0]
                        center_x = (box[0] + box[2]) // 2
                        center_y = (box[1] + box[3]) // 2
                        state["click_coordinates"] = [center_x, center_y]
                        state["status"] = "clicking"
                    else:
                        state["error_message"] = "No converted coordinates available"
                        state["status"] = "error"
                else:
                    state["error_message"] = "No coordinates available for clicking"
                    state["status"] = "error"

            elif action == "complete":
                state["status"] = "complete"

            else:
                logger.warning(f"Unknown action: {action}")
                state["error_message"] = f"Unknown action: {action}"
                state["status"] = "error"

            # Add agent response to messages
            state["messages"].append(AIMessage(content=response.content))

        else:
            logger.error("Failed to parse action from GLM-4.7 response")
            state["error_message"] = "Failed to parse agent decision"
            state["status"] = "error"

    except Exception as e:
        logger.error(f"GLM-4.7 agent failed: {e}")
        import traceback
        traceback.print_exc()
        state["error_message"] = f"Agent failed: {str(e)}"
        state["status"] = "error"

    return state


# ============================================================================
# Screenshot Node
# ============================================================================
# Navigate Node
# ============================================================================

async def navigate_node(state: BrowserAgentState) -> BrowserAgentState:
    """
    Navigate node that performs browser navigation

    Args:
        state: Current state (contains current_url)

    Returns:
        Updated state
    """
    logger.info("=== Navigate Node ===")

    url = state.get("current_url")

    if not url:
        logger.error("No URL to navigate to")
        state["error_message"] = "No URL available for navigation"
        state["status"] = "error"
        return state

    try:
        # Call the underlying function, not the tool object
        from utils.drission_page import create_browser
        page = create_browser()
        page.get(url)
        title = page.title
        result = f"Successfully navigated to {url}. Page title: {title}"

        logger.info(f"Navigation successful: {result}")
        state["messages"].append(AIMessage(content=result))
        state["page_title"] = title
        state["status"] = "screenshot"  # After navigation, take screenshot

    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        state["error_message"] = f"Navigation failed: {str(e)}"
        state["status"] = "error"

    return state


# ============================================================================
# Screenshot Node
# ============================================================================

async def screenshot_node(state: BrowserAgentState) -> BrowserAgentState:
    """
    Screenshot node that captures current page

    Args:
        state: Current state

    Returns:
        Updated state with screenshot_path and image dimensions
    """
    logger.info("=== Screenshot Node ===")

    try:
        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamp for filename
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)

        # Take screenshot directly
        from utils.drission_page import create_browser
        page = create_browser()
        page.get_screenshot(path=filepath)

        # Get image dimensions
        img = Image.open(filepath)
        width, height = img.size

        logger.info(f"Screenshot captured: {filepath} ({width}x{height})")

        state["screenshot_path"] = filepath
        state["image_width"] = width
        state["image_height"] = height
        state["current_url"] = page.url
        state["page_title"] = page.title
        state["status"] = "ready"

    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        state["error_message"] = f"Screenshot failed: {str(e)}"
        state["status"] = "error"

    return state


# ============================================================================
# Click Node
# ============================================================================

async def click_node(state: BrowserAgentState) -> BrowserAgentState:
    """
    Click node that executes click action using state coordinates

    Args:
        state: Current state (contains click_coordinates)

    Returns:
        Updated state
    """
    logger.info("=== Click Node ===")

    click_coords = state.get("click_coordinates")

    if not click_coords or len(click_coords) != 2:
        logger.error("Invalid click coordinates")
        state["error_message"] = "Invalid click coordinates"
        state["status"] = "error"
        return state

    try:
        x, y = click_coords

        # Click directly using DrissionPage
        from utils.drission_page import create_browser
        page = create_browser()
        tab = page.latest_tab

        # Move to coordinates and click
        tab.actions.move_to((x, y))
        tab.actions.click()

        logger.info(f"Successfully clicked at ({x}, {y})")
        state["status"] = "complete"
        state["messages"].append(AIMessage(content=f"Successfully clicked at ({x}, {y}). Waiting for page to load..."))

        # Wait a bit for page to load
        import time
        time.sleep(2)

        # Take another screenshot to verify
        # Create a new state for screenshot to avoid infinite recursion
        screenshot_state = state.copy()
        await screenshot_node(screenshot_state)

        # Update the current state with screenshot results
        if screenshot_state.get("screenshot_path"):
            state["screenshot_path"] = screenshot_state["screenshot_path"]
            state["image_width"] = screenshot_state["image_width"]
            state["image_height"] = screenshot_state["image_height"]
        if screenshot_state.get("current_url"):
            state["current_url"] = screenshot_state["current_url"]
        if screenshot_state.get("page_title"):
            state["page_title"] = screenshot_state["page_title"]

    except Exception as e:
        logger.error(f"Click failed: {e}")
        state["error_message"] = f"Click failed: {str(e)}"
        state["status"] = "error"

    return state


# ============================================================================
# Build the Graph
# ============================================================================

def build_browser_agent_graph() -> StateGraph:
    """
    Build the LangGraph browser agent graph

    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Building LangGraph browser agent...")

    # Create the graph
    workflow = StateGraph(BrowserAgentState)

    # Add nodes
    workflow.add_node("main_agent", main_agent_node)
    workflow.add_node("navigate", navigate_node)
    workflow.add_node("screenshot", screenshot_node)
    workflow.add_node("vision", vision_node)
    workflow.add_node("coordinate_conversion", coordinate_conversion_node)
    workflow.add_node("click", click_node)

    # Define edges (routing logic)
    workflow.set_entry_point("main_agent")

    # From main_agent, decide next step based on status
    def route_after_main_agent(state: BrowserAgentState) -> str:
        status = state.get("status", "idle")
        logger.info(f"Routing decision based on status: {status}")

        if status == "navigating":  # Fixed typo from "navigating"
            return "navigate"
        elif status == "screenshot":
            return "screenshot"
        elif status == "analyzing":
            return "vision"
        elif status == "clicking":
            return "click"
        elif status == "complete":
            return END
        elif status == "error":
            return END
        else:
            logger.warning(f"Unknown status in routing: {status}")
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

    # After navigate, go to screenshot (navigate_node sets status to "screenshot")
    workflow.add_edge("navigate", "screenshot")

    # After screenshot, always go back to main_agent to let it decide next action
    workflow.add_edge("screenshot", "main_agent")

    # After vision, go to coordinate conversion
    workflow.add_edge("vision", "coordinate_conversion")

    # After coordinate conversion, go to click
    workflow.add_edge("coordinate_conversion", "click")

    # After click, end
    workflow.add_edge("click", END)

    # Compile the graph
    app = workflow.compile()

    logger.info("LangGraph browser agent built successfully")
    return app


# ============================================================================
# Run the Agent
# ============================================================================

async def run_browser_agent(user_request: str) -> BrowserAgentState:
    """
    Run the browser agent with a user request

    Args:
        user_request: The user's request in natural language

    Returns:
        Final state after execution
    """
    logger.info("=" * 80)
    logger.info("Running LangGraph Browser Agent")
    logger.info("=" * 80)
    logger.info(f"User request: {user_request}")
    logger.info("")

    # Build the graph
    app = build_browser_agent_graph()

    # Initialize state
    initial_state: BrowserAgentState = {
        "messages": [HumanMessage(content=user_request)],
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
        "status": "idle",
        "error_message": None
    }

    # Run the graph
    try:
        final_state = await app.ainvoke(initial_state)

        logger.info("")
        logger.info("=" * 80)
        logger.info("Agent Execution Complete")
        logger.info("=" * 80)
        logger.info(f"Final status: {final_state.get('status')}")
        if final_state.get('error_message'):
            logger.error(f"Error: {final_state.get('error_message')}")
        logger.info("=" * 80)

        return final_state

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys

    # Example usage
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = "访问百度，点击搜索按钮"

    # Run the agent
    result = asyncio.run(run_browser_agent(user_request))

    # Print results
    print("\n" + "=" * 80)
    print("RESULT")
    print("=" * 80)
    print(f"Status: {result.get('status')}")
    print(f"Final URL: {result.get('current_url')}")
    print(f"Screenshot: {result.get('screenshot_path')}")
    if result.get('error_message'):
        print(f"Error: {result.get('error_message')}")
    print("=" * 80)
