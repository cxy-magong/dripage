#!/usr/bin/env python
"""
Browser Agent Nodes

All LangGraph nodes for browser automation
- Uses GLM-4.7 as main controller agent
- Uses GLM-4.1V for vision/element detection
- Shares state across nodes for screenshots and coordinate conversion
"""

import os
import base64
import asyncio
from typing import List, Optional
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_community.chat_models import ChatZhipuAI
from langgraph.runtime import RunnableConfig

from .state import BrowserAgentState
# Import from utils directly to avoid circular imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.drission_page import create_browser
from utils.glm_coordinate_converter import GLMCoordinateConverter
from utils.logu import get_logger

logger = get_logger('browser_agent_nodes')


# Initialize GLM-4.7 model for main agent
def get_glm_4_7_agent():
    """Get GLM-4.7 model configured for agent use"""
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


async def navigate_node(state: BrowserAgentState) -> BrowserAgentState:
    """Navigate node that performs browser navigation"""
    logger.info("=== Navigate Node ===")

    url = state.get("current_url")

    if not url:
        logger.error("No URL to navigate to")
        state["error_message"] = "No URL available for navigation"
        state["status"] = "error"
        return state

    try:
        # Use the tool directly
        result = navigate_to_url(url)

        if "Failed" in result:
            state["error_message"] = result
            state["status"] = "error"
        else:
            logger.info(f"Navigation successful: {result}")
            state["messages"].append(AIMessage(content=result))
            state["status"] = "screenshot"  # After navigation, take screenshot

    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        state["error_message"] = f"Navigation failed: {str(e)}"
        state["status"] = "error"

    return state


async def screenshot_node(state: BrowserAgentState) -> BrowserAgentState:
    """Screenshot node that captures current page"""
    logger.info("=== Screenshot Node ===")

    try:
        # Create output directory
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Take screenshot using tool
        filepath = take_screenshot()

        if "Failed" in filepath:
            state["error_message"] = filepath
            state["status"] = "error"
            return state

        # Get image dimensions
        from PIL import Image
        img = Image.open(filepath)
        width, height = img.size

        logger.info(f"Screenshot captured: {filepath} ({width}x{height})")

        state["screenshot_path"] = filepath
        state["image_width"] = width
        state["image_height"] = height
        state["status"] = "ready"

    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        state["error_message"] = f"Screenshot failed: {str(e)}"
        state["status"] = "error"

    return state


async def vision_node(state: BrowserAgentState) -> BrowserAgentState:
    """
    Vision node using GLM-4.1V to detect elements on page

    This node:
    1. Reads screenshot path from state
    2. Calls GLM-4.1V to analyze image
    3. Parses coordinates from response
    4. Updates state with GLM coordinates
    5. Also extracts input box coordinates and recommended click point
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

        # Initialize GLM-4.1V client
        from zai import ZhipuAiClient
        client = ZhipuAiClient(api_key=os.environ.get('ZAI_API_KEY'))

        # Encode image as base64
        with open(screenshot_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')

        # Enhanced vision query to also get input box coordinates
        enhanced_query = f"""Please analyze the screenshot and return:
1. Bounding box coordinates of the target element (format: [[x1, y1, x2, y2]])
2. Coordinates of any text input box (format: [[x, y]])
3. Recommended click point (center of target element)

{vision_query}

Return format:
Bounding box: [[x1,y1,x2,y2]]
Input box: [[x,y]] (if any)
Click point: [[x,y]]"""

        # Call GLM-4.1V-Thinking-Flash model with thinking enabled
        image_data_url = f"data:image/png;base64,{base64_image}"
        response = client.chat.completions.create(
            model="GLM-4.1V-Thinking-Flash",
            messages=[
                {
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_data_url}},
                        {"type": "text", "text": enhanced_query}
                    ],
                    "role": "user"
                }
            ],
            thinking={"type": "enabled"}
        )

        # Extract response
        message = response.choices[0].message
        response_text = message.content

        logger.info(f"GLM-4.1V Response: {response_text}")

        # Create coordinate converter
        converter = GLMCoordinateConverter.from_image_path(screenshot_path)

        # Parse coordinates from response
        glm_boxes = converter.parse_coordinates_from_text(response_text)

        # Extract input box coordinates (look for [[x,y]] pattern)
        import re
        input_box_matches = re.search(r'\[\[(\d+),\s*(\d+)\]\]', response_text)
        input_box_coords = None
        if input_box_matches:
            input_box_coords = [[int(input_box_matches.group(1)), int(input_box_matches.group(2))]]

        # Extract recommended click point
        click_match = re.search(r'\[?\[(\d+),\s*(\d+)\]\]', response_text)
        click_coords = None
        if click_match:
            click_coords = [int(click_match.group(1)), int(click_match.group(2))]

        if glm_boxes:
            logger.info(f"Detected {len(glm_boxes)} bounding box(es)")
            for i, box in enumerate(glm_boxes):
                logger.info(f"  Box {i+1}: {box}")

            state["glm_coordinates"] = glm_boxes

            # Store input box and click coordinates in state
            if input_box_coords:
                state["input_box_coordinates"] = input_box_coords
                logger.info(f"Input box coordinates: {input_box_coords}")
            else:
                state["input_box_coordinates"] = None

            if click_coords:
                state["click_coordinates"] = click_coords
                logger.info(f"Recommended click point: {click_coords}")
            else:
                state["click_coordinates"] = None

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


async def coordinate_conversion_node(state: BrowserAgentState) -> BrowserAgentState:
    """Convert GLM coordinates to original image coordinates"""
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

        # Calculate click coordinates if not already set
        if not state.get("click_coordinates") and converted_boxes:
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


async def click_node(state: BrowserAgentState) -> BrowserAgentState:
    """Click node that executes click action using state coordinates"""
    logger.info("=== Click Node ===")

    click_coords = state.get("click_coordinates")

    if not click_coords or len(click_coords) != 2:
        logger.error("Invalid click coordinates")
        state["error_message"] = "Invalid click coordinates"
        state["status"] = "error"
        return state

    try:
        x, y = click_coords

        # Use the tool directly
        result = click_at_coordinates(x, y)

        if "Failed" in result:
            state["error_message"] = result
            state["status"] = "error"
        else:
            logger.info("Click executed successfully")
            state["status"] = "complete"
            state["messages"].append(AIMessage(content=f"Successfully clicked at ({x}, {y}). Waiting for page to load..."))

            # Wait a bit for page to load
            import time
            time.sleep(2)

            # Take another screenshot to verify
            screenshot_result = await screenshot_node(state.copy())
            if screenshot_result.get("screenshot_path"):
                state["screenshot_path"] = screenshot_result["screenshot_path"]
                state["image_width"] = screenshot_result["image_width"]
                state["image_height"] = screenshot_result["image_height"]

    except Exception as e:
        logger.error(f"Click failed: {e}")
        state["error_message"] = f"Click failed: {str(e)}"
        state["status"] = "error"

    return state


async def click_node(state: BrowserAgentState) -> BrowserAgentState:
    """Click node that executes click action using state coordinates"""
    logger.info("=== Click Node ===")

    click_coords = state.get("click_coordinates")

    if not click_coords or len(click_coords) != 2:
        logger.error("Invalid click coordinates")
        state["error_message"] = "Invalid click coordinates"
        state["status"] = "error"
        return state

    try:
        x, y = click_coords

        # Use the tool directly
        result = click_at_coordinates(x, y)

        if "Failed" in result:
            state["error_message"] = result
            state["status"] = "error"
        else:
            logger.info("Click executed successfully")
            state["status"] = "complete"
            state["messages"].append(AIMessage(content=f"Successfully clicked at ({x}, {y}). Waiting for page to load..."))

            # Wait a bit for page to load
            import time
            time.sleep(2)

            # Take another screenshot to verify
            screenshot_result = await screenshot_node(state.copy())
            if screenshot_result.get("screenshot_path"):
                state["screenshot_path"] = screenshot_result["screenshot_path"]
                state["image_width"] = screenshot_result["image_width"]
                state["image_height"] = screenshot_result["image_height"]

    except Exception as e:
        logger.error(f"Click failed: {e}")
        state["error_message"] = f"Click failed: {str(e)}"
        state["status"] = "error"

    return state


async def input_text_node(state: BrowserAgentState) -> BrowserAgentState:
    """Input text node - clicks input box and enters text"""
    logger.info("=== Input Text Node ===")

    text_to_input = state.get("text_to_input")
    input_box_coords = state.get("input_box_coordinates")

    if not text_to_input:
        logger.error("No text to input")
        state["error_message"] = "No text provided for input"
        state["status"] = "error"
        return state

    if not input_box_coords or len(input_box_coords) != 2:
        logger.error("Invalid input box coordinates")
        state["error_message"] = "Invalid input box coordinates"
        state["status"] = "error"
        return state

    try:
        x, y = input_box_coords

        # Use the tool directly
        result = input_text_at_coordinates(x, y, text_to_input)

        if "Failed" in result:
            state["error_message"] = result
            state["status"] = "error"
        else:
            logger.info(f"Text input successful: {text_to_input}")
            state["messages"].append(AIMessage(content=result))
            state["status"] = "ready"  # After input, ready for next action

    except Exception as e:
        logger.error(f"Text input failed: {e}")
        state["error_message"] = f"Text input failed: {str(e)}"
        state["status"] = "error"

    return state


async def main_agent_node(state: BrowserAgentState) -> BrowserAgentState:
    """
    Main agent node using GLM-4.7 as controller

    This node:
    1. Analyzes user request using GLM-4.7 with reflection
    2. Decides which tools/nodes to call based on analysis
    3. Orchestrates multi-step workflows

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
        llm = create_glm_4_7_agent(config={})

        # Create system prompt with agent role and workflow guidance
        system_prompt = """You are a browser automation agent specializing in web navigation and interaction.

## Available Actions:
1. "navigate" - Navigate to a URL
2. "screenshot" - Take a screenshot of the current page
3. "analyze" - Analyze screenshot with vision to find elements and input boxes
4. "convert" - Convert coordinates from vision model space to image space
5. "click" - Click at specified coordinates
6. "input_text" - Click input box and enter text
7. "search" - Click search button after entering text
8. "complete" - Task is complete

## Workflow Patterns:
- **Pattern 1 (Simple Navigation):** navigate → screenshot → analyze → convert → click
- **Pattern 2 (Search Workflow):** navigate → screenshot → analyze → convert → input_text → search → complete
- **Pattern 3 (Multi-step):** Continue to workflow based on current state

## Decision Logic:
1. Check current status and state to determine next action
2. For "navigate" action: Extract URL from request (look for http://, https://, or site names like 百度/Google)
3. For "analyze" action: Use vision_query to describe what to find
4. For "input_text" action: Use text_to_input from state
5. For "search" action: Click search button after text input
6. Return action as JSON: {"action": "action_name", "params": {...}}
7. Use reflection to think through complex multi-step workflows
"""

        # Build context about current state
        state_context = f"""Current state:
- Current URL: {state.get('current_url', 'None')}
- Page title: {state.get('page_title', 'None')}
- Screenshot path: {state.get('screenshot_path', 'None')}
- Vision query: {state.get('vision_query', 'None')}
- GLM coordinates (999x999): {state.get('glm_coordinates', 'None')}
- Converted coordinates: {state.get('converted_coordinates', 'None')}
- Click coordinates: {state.get('click_coordinates', 'None')}
- Input box coordinates: {state.get('input_box_coordinates', 'None')}
- Text to input: {state.get('text_to_input', 'None')}
- Current status: {state.get('status', 'idle')}"""

        # Build messages for GLM-4.7
        agent_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User request: {last_message}\n\n{state_context}")
        ]

        # Call GLM-4.7 with reflection
        logger.info("Calling GLM-4.7 to decide next action...")
        response = await llm.ainvoke(agent_messages, config=RunnableConfig(recursion_limit=0))

        logger.info(f"GLM-4.7 decision: {response.content}")

        # Parse action from response
        action_json = None
        # Try to extract JSON from response
        import json
        import re
        json_match = re.search(r'\{[^}]+\}', response.content)
        if json_match:
            try:
                action_json = json.loads(json_match.group())
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract action name directly
                action_lower = response.content.lower()
                if "navigate" in action_lower:
                    action_json = {"action": "navigate"}
                elif "screenshot" in action_lower:
                    action_json = {"action": "screenshot"}
                elif "analyze" in action_lower or "vision" in action_lower:
                    action_json = {"action": "analyze"}
                elif "convert" in action_lower:
                    action_json = {"action": "convert"}
                elif "click" in action_lower:
                    action_json = {"action": "click"}
                elif "input" in action_lower or "input_text" in action_lower:
                    action_json = {"action": "input_text"}
                elif "search" in action_lower:
                    action_json = {"action": "search"}
                elif "complete" in action_lower or "done" in action_lower:
                    action_json = {"action": "complete"}
                else:
                    action_json = {"action": "complete"}

        if not action_json:
            # Default action based on keywords
            action_lower = response.content.lower()
            if "访问" in last_message or "打开" in last_message or "navigate" in last_message:
                action_json = {"action": "navigate"}
                # Extract URL if mentioned
                url_match = re.search(r'https?://[^\s]+', last_message)
                if url_match:
                    action_json["url"] = url_match.group()
                elif "百度" in last_message:
                    action_json["url"] = "https://www.baidu.com"
            elif "截图" in last_message or "screenshot" in last_message:
                action_json = {"action": "screenshot"}
            elif "分析" in last_message or "识别" in last_message:
                action_json = {"action": "analyze"}
            elif "点击" in last_message or "click" in last_message:
                # Check if we have coordinates ready
                if state.get("click_coordinates"):
                    action_json = {"action": "click"}
                else:
                    # Need to analyze first
                    action_json = {"action": "analyze"}
            elif "输入" in last_message or "input" in last_message or "type" in last_message or "输入" in last_message:
                # Extract text to input
                # Remove common prefixes
                text_to_input = last_message
                for prefix in ["输入", "type", "input text", "在输入框输入", "在输入框中输入"]:
                    text_to_input = text_to_input.replace(prefix, "").strip()

                if not text_to_input:
                    logger.error("No text found for input")
                    state["error_message"] = "No text to input"
                    state["status"] = "error"
                    return state

                action_json = {"action": "input_text", "text": text_to_input}
            elif "搜索" in last_message or "search" in last_message or "回车" in last_message or "enter" in last_message:
                action_json = {"action": "search"}
            else:
                logger.info("Unrecognized request, marking complete")
                action_json = {"action": "complete"}

        action = action_json.get("action", "")
        logger.info(f"Decided action: {action}")

        # Update state based on action
        if action == "navigate":
            state["status"] = "navigating"
            url = action_json.get("url")
            if url:
                state["current_url"] = url
                # Set vision query for after navigation
                if "百度" in last_message:
                    state["vision_query"] = "找到搜索按钮并返回其坐标"
                else:
                    state["vision_query"] = "找到相关元素并返回坐标"
            else:
                logger.error("URL not provided for navigate action")
                state["error_message"] = "URL not provided"
                state["status"] = "error"

        elif action == "screenshot":
            state["status"] = "screenshot"

        elif action == "analyze":
            if state.get("screenshot_path"):
                state["status"] = "analyzing"
                # Use existing vision query or default
                if not state.get("vision_query"):
                    state["vision_query"] = last_message or "分析页面元素并返回坐标"
            else:
                state["error_message"] = "No screenshot available for analysis"
                state["status"] = "error"

        elif action == "convert":
            if state.get("glm_coordinates"):
                state["status"] = "clicking"
            else:
                state["error_message"] = "No GLM coordinates to convert"
                state["status"] = "error"

        elif action == "click":
            if state.get("click_coordinates"):
                state["status"] = "clicking"
            else:
                state["error_message"] = "No coordinates available for clicking"
                state["status"] = "error"

        elif action == "input_text":
            text_to_input = action_json.get("text", "")
            if text_to_input and state.get("input_box_coordinates"):
                state["text_to_input"] = text_to_input
                state["status"] = "inputting_text"
            elif not text_to_input:
                logger.error("No text provided for input_text action")
                state["error_message"] = "No text provided for input"
                state["status"] = "error"
            elif not state.get("input_box_coordinates"):
                logger.error("No input box coordinates available")
                state["error_message"] = "No input box coordinates available"
                state["status"] = "error"
            else:
                state["error_message"] = "Need to analyze page first to find input box"
                state["status"] = "error"

        elif action == "search":
            state["status"] = "searching"

        elif action == "complete":
            state["status"] = "complete"

        else:
            logger.warning(f"Unknown action: {action}")
            state["error_message"] = f"Unknown action: {action}"
            state["status"] = "error"

        # Add agent response to messages
        state["messages"].append(AIMessage(content=response.content))

    except Exception as e:
        logger.error(f"GLM-4.7 agent failed: {e}")
        import traceback
        traceback.print_exc()
        state["error_message"] = f"Agent failed: {str(e)}"
        state["status"] = "error"

    return state


def route_after_main_agent(state: BrowserAgentState) -> str:
    """Route after main agent based on status"""
    status = state.get("status", "idle")
    logger.info(f"Routing decision based on status: {status}")

    # Navigate
    if status == "navigating":  # Fixed typo
        return "navigate"
    # Screenshot
    elif status == "screenshot":
        return "screenshot"
    # Analyze with vision
    elif status == "analyzing":
        return "vision"
    # Convert coordinates
    elif status == "clicking":
        return "click"
    # Input text
    elif status == "inputting_text":
        return "input_text"
    # Search (after text input)
    elif status == "searching":
        return "click"  # Click search button
    # Complete
    elif status == "complete":
        return END
    # Error
    elif status == "error":
        return END
    else:
        logger.warning(f"Unknown status in routing: {status}")
        return END


async def main_agent_node(state: BrowserAgentState) -> BrowserAgentState:
    """
    Main agent node using GLM-4.7 as controller

    This node:
    1. Analyzes user request using GLM-4.7 with reflection
    2. Decides which tools/nodes to call based on analysis
    3. Orchestrates multi-step workflows

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
        llm = create_glm_4_7_agent(config={})

        # Create system prompt with agent role and workflow guidance
        system_prompt = """You are a browser automation agent specializing in web navigation and interaction.

## Available Actions:
1. "navigate" - Navigate to a URL
2. "screenshot" - Take a screenshot of the current page
3. "analyze" - Analyze screenshot with vision to find elements and input boxes
4. "convert" - Convert coordinates from vision model space to image space
5. "click" - Click at specified coordinates
6. "input_text" - Click input box and enter text
7. "search" - Click search button after entering text
8. "complete" - Task is complete

## Workflow Patterns:
- **Pattern 1 (Simple Navigation):** navigate → screenshot → analyze → convert → click
- **Pattern 2 (Search Workflow):** navigate → screenshot → analyze → convert → input_text → search → complete
- **Pattern 3 (Multi-step):** Continue the workflow based on current state

## Decision Logic:
1. Check current status and state to determine next action
2. For "navigate" action: Extract URL from request (look for http://, https://, or site names like 百度/Google)
3. For "analyze" action: Use the vision_query to describe what to find
4. For "input_text" action: Use text_to_input from state
5. For "search" action: Click search button after text input
6. Return action as JSON: {"action": "action_name", "params": {...}}
7. Use reflection to think through complex multi-step workflows
"""

        # Build context about current state
        state_context = f"""Current state:
- Current URL: {state.get('current_url', 'None')}
- Page title: {state.get('page_title', 'None')}
- Screenshot path: {state.get('screenshot_path', 'None')}
- Vision query: {state.get('vision_query', 'None')}
- GLM coordinates (999x999): {state.get('glm_coordinates', 'None')}
- Converted coordinates: {state.get('converted_coordinates', 'None')}
- Click coordinates: {state.get('click_coordinates', 'None')}
- Input box coordinates: {state.get('input_box_coordinates', 'None')}
- Text to input: {state.get('text_to_input', 'None')}
- Current status: {state.get('status', 'idle')}"""

        # Build messages for GLM-4.7
        agent_messages = [
            AIMessage(content=f"Current state:\\n{state_context}"),
            HumanMessage(content=f"User request: {last_message}")
        ]

        # Call GLM-4.7 with reflection
        logger.info("Calling GLM-4.7 to decide next action...")
        response = await llm.ainvoke(agent_messages, config=RunnableConfig(recursion_limit=0))

        logger.info(f"GLM-4.7 decision: {response.content}")

        # Parse action from response
        action_json = None
        # Try to extract JSON from response
        import json
        import re
        json_match = re.search(r'\{[^}]+\}', response.content)
        if json_match:
            try:
                action_json = json.loads(json_match.group())
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract action name directly
                action_lower = response.content.lower()
                if "navigate" in action_lower:
                    action_json = {"action": "navigate"}
                elif "screenshot" in action_lower:
                    action_json = {"action": "screenshot"}
                elif "analyze" in action_lower or "vision" in action_lower:
                    action_json = {"action": "analyze"}
                elif "convert" in action_lower:
                    action_json = {"action": "convert"}
                elif "click" in action_lower:
                    action_json = {"action": "click"}
                elif "input" in action_lower or "input_text" in action_lower:
                    action_json = {"action": "input_text"}
                elif "search" in action_lower:
                    action_json = {"action": "search"}
                elif "complete" in action_lower or "done" in action_lower:
                    action_json = {"action": "complete"}
                else:
                    action_json = {"action": "complete"}

        if not action_json:
            # Default action based on keywords
            action_lower = response.content.lower()
            if "访问" in last_message or "打开" in last_message or "navigate" in last_message:
                action_json = {"action": "navigate"}
                # Extract URL if mentioned
                url_match = re.search(r'https?://[^\s]+', last_message)
                if url_match:
                    action_json["url"] = url_match.group()
                elif "百度" in last_message:
                    action_json["url"] = "https://www.baidu.com"
            elif "截图" in last_message or "screenshot" in last_message:
                action_json = {"action": "screenshot"}
            elif "分析" in last_message or "识别" in last_message:
                action_json = {"action": "analyze"}
            elif "点击" in last_message or "click" in last_message:
                # Check if we have coordinates ready
                if state.get("click_coordinates"):
                    action_json = {"action": "click"}
                else:
                    # Need to analyze first
                    action_json = {"action": "analyze"}
            elif "输入" in last_message or "input" in last_message or "type" in last_message or "输入" in last_message:
                # Extract text to input
                # Remove common prefixes
                text_to_input = last_message
                for prefix in ["输入", "type", "input text", "在输入框输入", "在输入框中输入"]:
                    text_to_input = text_to_input.replace(prefix, "").strip()

                if not text_to_input:
                    logger.error("No text found for input")
                    state["error_message"] = "No text to input"
                    state["status"] = "error"
                    return state

                action_json = {"action": "input_text", "text": text_to_input}
            elif "搜索" in last_message or "search" in last_message or "回车" in last_message or "enter" in last_message:
                action_json = {"action": "search"}
            else:
                logger.info("Unrecognized request, marking complete")
                action_json = {"action": "complete"}

        action = action_json.get("action", "")
        logger.info(f"Decided action: {action}")

        # Update state based on action
        if action == "navigate":
            state["status"] = "navigating"
            url = action_json.get("url")
            if url:
                state["current_url"] = url
                # Set vision query for after navigation
                if "百度" in last_message:
                    state["vision_query"] = "找到搜索按钮并返回其坐标"
                else:
                    state["vision_query"] = "找到相关元素并返回坐标"
            else:
                logger.error("URL not provided for navigate action")
                state["error_message"] = "URL not provided"
                state["status"] = "error"

        elif action == "screenshot":
            state["status"] = "screenshot"

        elif action == "analyze":
            if state.get("screenshot_path"):
                state["status"] = "analyzing"
                # Use existing vision query or default
                if not state.get("vision_query"):
                    state["vision_query"] = last_message or "分析页面元素并返回坐标"
            else:
                state["error_message"] = "No screenshot available for analysis"
                state["status"] = "error"

        elif action == "convert":
            if state.get("glm_coordinates"):
                state["status"] = "clicking"
            else:
                state["error_message"] = "No GLM coordinates to convert"
                state["status"] = "error"

        elif action == "click":
            if state.get("click_coordinates"):
                state["status"] = "clicking"
            else:
                state["error_message"] = "No coordinates available for clicking"
                state["status"] = "error"

        elif action == "input_text":
            text_to_input = action_json.get("text", "")
            if text_to_input and state.get("input_box_coordinates"):
                state["text_to_input"] = text_to_input
                state["status"] = "inputting_text"
            elif not text_to_input:
                logger.error("No text provided for input_text action")
                state["error_message"] = "No text provided for input"
                state["status"] = "error"
            elif not state.get("input_box_coordinates"):
                state["error_message"] = "No input box coordinates available"
                state["status"] = "error"
            else:
                state["error_message"] = "Need to analyze page first to find input box"
                state["status"] = "error"

        elif action == "search":
            state["status"] = "searching"

        elif action == "complete":
            state["status"] = "complete"

        else:
            logger.warning(f"Unknown action: {action}")
            state["error_message"] = f"Unknown action: {action}"
            state["status"] = "error"

        # Add agent response to messages
        state["messages"].append(AIMessage(content=response.content))

    except Exception as e:
        logger.error(f"GLM-4.7 agent failed: {e}")
        import traceback
        traceback.print_exc()
        state["error_message"] = f"Agent failed: {str(e)}"
        state["status"] = "error"

    return state


def route_after_main_agent(state: BrowserAgentState) -> str:
    """Route after main agent based on status"""
    status = state.get("status", "idle")
    logger.info(f"Routing decision based on status: {status}")

    # Navigate
    if status == "navigating":  # Fixed typo
        return "navigate"
    # Screenshot
    elif status == "screenshot":
        return "screenshot"
    # Analyze with vision
    elif status == "analyzing":
        return "vision"
    # Convert coordinates
    elif status == "clicking":
        return "click"
    # Input text
    elif status == "inputting_text":
        return "input_text"
    # Search (after text input)
    elif status == "searching":
        return "click"  # Click search button
    # Complete
    elif status == "complete":
        return END
    # Error
    elif status == "error":
        return END
    else:
        logger.warning(f"Unknown status in routing: {status}")
        return END
