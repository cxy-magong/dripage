#!/usr/bin/env python
"""
Browser Agent State Definition

Shared state across all nodes in the LangGraph graph
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator


class BrowserAgentState(TypedDict):
    """State for browser agent graph

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

    # Text input state (for user to input text)
    text_to_input: Optional[str]
    input_box_coordinates: Optional[List[int]]  # Coordinates of input box to click

    # Status and results
    status: str  # "idle", "navigating", "analyzing", "clicking", "complete", "inputting_text", "searching"
    error_message: Optional[str]
