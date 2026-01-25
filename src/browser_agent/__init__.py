#!/usr/bin/env python
"""Browser Agent Package - LangGraph-based browser automation with vision
"""

# Import and re-export for convenient use
from .state import BrowserAgentState
from .main import create_browser_agent_app

__all__ = ["BrowserAgentState", "create_browser_agent_app"]

__version__ = "0.1.0"
