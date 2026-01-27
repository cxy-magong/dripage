#!/usr/bin/env python
"""
Browser Agent Application Factory

Creates the LangGraph app with all nodes and configuration
"""

import os
import yaml
from pathlib import Path
from langgraph.graph import StateGraph, END

from .state import BrowserAgentState
# Import nodes directly to avoid circular imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import all node functions directly to avoid circular dependency
from utils.drission_page import create_browser
from utils.glm_coordinate_converter import GLMCoordinateConverter
from utils.logu import get_logger
from langchain_community.chat_models import ChatZhipuAI
from langgraph.runtime import RunnableConfig
from langchain_core.messages import AIMessage

logger = get_logger('browser_agent_app')


def load_runtime_config():
    """Load runtime configuration from YAML files"""
    config_path = Path(__file__).parent.parent / "config" / "browser_runtime.yaml"
    mcp_tools_path = Path(__file__).parent.parent / "config" / "mcp_tools.yaml"

    # Load runtime config
    runtime_config = {}
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            runtime_config = yaml.safe_load(f)

    # Load MCP tools config
    mcp_tools_config = {}
    if mcp_tools_path.exists():
        with open(mcp_tools_path, 'r', encoding='utf-8') as f:
            mcp_tools_config = yaml.safe_load(f)

    return runtime_config, mcp_tools_config


def create_glm_4_7_agent(config: dict):
    """Get GLM-4.7 model configured for agent use with runtime config"""
    try:
        api_key = os.environ.get('ZAI_API_KEY')
        if not api_key:
            raise ValueError("ZAI_API_KEY environment variable not set")

        model_config = config.get('models', {}).get('glm_4_7', {})

        llm_kwargs = {
            "temperature": model_config.get('temperature', 0.0),
            "streaming": True,
            "max_tokens": model_config.get('max_tokens', 4096),
            "api_key": api_key
        }

        # Add reflection config if enabled
        reflection_config = model_config.get('reflection', {})
        if reflection_config.get('enabled', False):
            llm_kwargs["tools"] = [{
                "type": "web_search"
            }]

        llm = ChatZhipuAI(
            model="glm-4.7",
            **llm_kwargs
        )

        logger.info(f"GLM-4.7 agent initialized with config: {llm_kwargs}")
        return llm

    except Exception as e:
        logger.error(f"Failed to initialize GLM-4.7: {e}")
        raise


def create_browser_agent_app():
    """
    Create and configure a LangGraph browser agent application

    Returns:
        Compiled StateGraph ready for execution
    """
    logger.info("Building LangGraph browser agent...")

    # Load runtime configuration
    runtime_config, mcp_tools_config = load_runtime_config()

    # Create the graph
    workflow = StateGraph(BrowserAgentState)

    # Add all nodes (defined in nodes.py)
    from nodes import navigate_node, screenshot_node, vision_node, coordinate_conversion_node, click_node, input_text_node
    from nodes import route_after_main_agent

    workflow.add_node("main_agent", main_agent_node)
    workflow.add_node("navigate", navigate_node)
    workflow.add_node("screenshot", screenshot_node)
    workflow.add_node("vision", vision_node)
    workflow.add_node("coordinate_conversion", coordinate_conversion_node)
    workflow.add_node("click", click_node)
    workflow.add_node("input_text", input_text_node)

    # Add conditional edges from main_agent
    workflow.add_conditional_edges(
        "main_agent",
        route_after_main_agent,
        {
            "navigate": "navigate",
            "screenshot": "screenshot",
            "vision": "vision",
            "click": "click",
            "input_text": "input_text",
            END: END
        }
    )

    # Define edges for workflow chain
    # Navigate → Screenshot → Main Agent (to decide next)
    workflow.add_edge("navigate", "screenshot")
    workflow.add_edge("screenshot", "main_agent")

    # Vision → Coordinate Conversion → Click
    workflow.add_edge("vision", "coordinate_conversion")
    workflow.add_edge("coordinate_conversion", "click")

    # Input Text → Main Agent (to decide next, usually search)
    workflow.add_edge("input_text", "main_agent")

    # Click → Screenshot (to verify result)
    workflow.add_edge("click", "screenshot")

    # Set entry point
    workflow.set_entry_point("main_agent")

    # Compile the graph
    app = workflow.compile()

    logger.info("LangGraph browser agent built successfully")
    return app

