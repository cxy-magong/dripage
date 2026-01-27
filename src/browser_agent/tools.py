#!/usr/bin/env python
"""
Browser Control Tools

Tools for browser automation using DrissionPage
"""

import os
from typing import Optional
from datetime import datetime
from langchain_core.tools import tool
from PIL import Image

from utils.drission_page import create_browser
from utils.logu import get_logger

logger = get_logger('browser_tools')


@tool
def navigate_to_url(url: str) -> str:
    """
    Navigate browser to specified URL

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
        Path to saved screenshot file
    """
    logger.info("Taking screenshot...")
    try:
        page = create_browser()

        # Create output directory if it doesn't exist
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamp for filename
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


@tool
def click_at_coordinates(x: int, y: int) -> str:
    """
    Click at specified coordinates on the page

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

        logger.info(f"Successfully clicked at ({x}, {y})")
        return f"Successfully clicked at coordinates ({x}, {y})"

    except Exception as e:
        logger.error(f"Failed to click at ({x}, {y}): {e}")
        return f"Failed to click at ({x}, {y}): {str(e)}"


@tool
def input_text_at_coordinates(x: int, y: int, text: str) -> str:
    """
    Click input box at coordinates and enter text

    Args:
        x: X coordinate of input box
        y: Y coordinate of input box
        text: Text to input

    Returns:
        Success message
    """
    logger.info(f"Inputting text '{text}' at coordinates: ({x}, {y})")
    try:
        page = create_browser()
        tab = page.latest_tab

        # Click to focus on input box
        tab.actions.move_to((x, y))
        tab.actions.click()

        # Clear existing text and input new text
        import time
        time.sleep(0.5)

        # Find input element and send keys
        # Use DrissionPage's input method
        tab.actions.move_to((x, y))
        tab.actions.click()
        time.sleep(0.5)

        # Type the text
        # Clear existing text (Ctrl+A, Delete) then type new
        tab.actions.key_down('ctrl')
        tab.actions.key_press('a')
        time.sleep(0.2)
        tab.actions.key_press('delete')
        tab.actions.input(text)

        logger.info(f"Successfully inputted text: {text}")
        return f"Successfully inputted '{text}' at coordinates ({x}, {y})"

    except Exception as e:
        logger.error(f"Failed to input text at ({x}, {y}): {e}")
        return f"Failed to input text: {str(e)}"
