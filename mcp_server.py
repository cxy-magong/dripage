#!/usr/bin/env python
"""
Dripage MCP Server - Browser automation and vision analysis via FastMCP.
"""
import os
import sys
import base64
import tempfile
import yaml
import json
import asyncio
from pathlib import Path
from typing import Optional, Literal, List
from datetime import datetime
from markitdown import MarkItDown

# Add project directory to path for imports
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from fastmcp import FastMCP
from langgraph.types import Command
from utils.drission_page import create_browser

# Import new tools from tools directory
from tools import (
    browser_navigate,
    browser_get_current_page,
    browser_screenshot,
    browser_click,
    browser_input,
    browser_press_key,
    browser_scroll,
    vision_analyze,
    locate_element,
    coordinate_convert_box,
    coordinate_parse_and_convert,
    coordinate_convert_from_image,
    list_tabs,
    switch_tab,
    new_tab,
    close_tab,
    get_current_tab_info,
)


# Load configuration from config directory
config_path = project_dir / 'config' / 'mcp_config.yaml'

if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
else:
    # Fallback to defaults
    config = {
        'browser': {'address': '127.0.0.1:19222'},
        'output': {'directory': 'output'},
        'vision': {'model': 'glm-4v-flash', 'temperature': 0.7, 'max_tokens': 1024}
    }

# Extract configuration
BROWSER_ADDRESS = config['browser']['address']
OUTPUT_DIR = project_dir / config['output']['directory']
DEFAULT_VISION_MODEL = config['vision']['model']
VISION_TEMPERATURE = config['vision']['temperature']
VISION_MAX_TOKENS = config['vision']['max_tokens']

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_browser() -> object:
    """Create or get a browser instance using default address."""
    return create_browser(address=BROWSER_ADDRESS)


def generate_timestamp() -> str:
    """Generate timestamp in format: YYYYMMDD_HHMMSS"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def serialize_result(result):
    """Serialize result to JSON, handling Command objects."""
    if isinstance(result, Command):
        return result.update
    return result


# Create MCP server instance
mcp = FastMCP(name="Dripage MCP 🚀")


async def save_markdown_async(html_content: str, timestamp: str) -> str:
    """Async save markdown using thread pool."""
    def _save():
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name

        try:
            md = MarkItDown()
            result = md.convert(temp_file)
            md_content = result.text_content

            filename = f"page_{timestamp}.md"
            filepath = OUTPUT_DIR / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)

            return str(filepath)
        finally:
            os.unlink(temp_file)

    return await asyncio.to_thread(_save)


async def save_html_async(html_content: str, timestamp: str) -> str:
    """Async save HTML using thread pool."""
    def _save():
        filename = f"page_{timestamp}.html"
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return str(filepath)

    return await asyncio.to_thread(_save)


async def save_img_async(page, timestamp: str) -> str:
    """Async save image using thread pool."""
    def _save():
        screenshot_data = page.get_screenshot(as_bytes=True)
        filename = f"page_{timestamp}.png"
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(screenshot_data)
        return str(filepath)

    return await asyncio.to_thread(_save)


async def save_mhtml_async(page, timestamp: str) -> str:
    """Async save MHTML using thread pool."""
    def _save():
        filename = f"page_{timestamp}.mhtml"
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(page.html)
        return str(filepath)

    return await asyncio.to_thread(_save)


@mcp.tool
async def get(
    url: Optional[str] = None,
    formats: List[Literal["markdown", "html", "img", "mhtml"]] = ["markdown"]
) -> str:
    """Navigate to a URL or get current page, save in specified format(s).

    Args:
        url: The webpage URL to navigate to. If not provided, saves the current page.
        formats: Output format(s) as list: ["markdown"], ["html"], ["img"], ["mhtml"],
                 or multiple formats: ["markdown", "html", "img"]
                 Defaults to ["markdown"]

    Returns:
        str: JSON with title, url, and file(s) - single "file" if one format,
              or "files" array if multiple formats
    """
    try:
        page = get_browser()

        # Navigate to URL if provided, otherwise use current page
        if url is not None:
            page.get(url)

        # Generate timestamp
        timestamp = generate_timestamp()

        # Get page HTML once
        html_content = page.html

        # Prepare async tasks for each format
        tasks = []

        for fmt in formats:
            if fmt == "markdown":
                tasks.append(save_markdown_async(html_content, timestamp))
            elif fmt == "html":
                tasks.append(save_html_async(html_content, timestamp))
            elif fmt == "img":
                tasks.append(save_img_async(page, timestamp))
            elif fmt == "mhtml":
                tasks.append(save_mhtml_async(page, timestamp))

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check for errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise RuntimeError(f"Failed to save {formats[i]}: {result}")

        # Return JSON with title, url, and file(s)
        if len(results) == 1:
            return json.dumps({
                "title": page.title,
                "url": page.url,
                "file": results[0]
            }, ensure_ascii=False, indent=2)
        else:
            # Return with files array for multiple formats
            return json.dumps({
                "title": page.title,
                "url": page.url,
                "files": results,
                "count": len(results),
                "formats": formats
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        raise RuntimeError(f"Failed to get page: {e}")


# ==================== Browser Tools from tools/ directory ====================

@mcp.tool
def browser_navigate_tool(url: str) -> str:
    """Navigate browser to specified URL.

    Args:
        url: The URL to navigate to

    Returns:
        Success message with page title
    """
    # Call the tool function directly
    return browser_navigate.func(url)


@mcp.tool
def browser_get_current_page_tool() -> str:
    """Get current page information.

    Returns:
        JSON string with page title and URL
    """
    return browser_get_current_page.func()


@mcp.tool
def browser_screenshot_tool() -> str:
    """Take a screenshot of the current page.

    Returns:
        str: File path to saved screenshot
    """
    try:
        page = get_browser()

        # Screenshot full page
        screenshot_data = page.get_screenshot(as_bytes=True)

        # Generate filename with timestamp
        timestamp = generate_timestamp()
        filename = f"screenshot_{timestamp}.png"

        # Save to output directory
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(screenshot_data)

        return str(filepath)

    except Exception as e:
        raise RuntimeError(f"Screenshot failed: {e}")


@mcp.tool
def browser_click_tool(x: int, y: int) -> str:
    """Click at specified coordinates on the page.

    Args:
        x: X coordinate
        y: Y coordinate

    Returns:
        Success message
    """
    return browser_click.func(x, y)


@mcp.tool
def browser_input_tool(x: int, y: int, text: str, clear: bool = True) -> str:
    """Click input box at coordinates and input text.

    Args:
        x: X coordinate of input box
        y: Y coordinate of input box
        text: Text to input
        clear: Whether to clear existing text first (default: True)

    Returns:
        Success message
    """
    return browser_input.func(x, y, text, clear=clear)


@mcp.tool
def browser_press_key_tool(key: str, times: int = 1) -> str:
    """Press keyboard keys.

    Args:
        key: Key name (e.g., 'enter', 'escape', 'space', 'tab')
        times: Number of times to press (default: 1)

    Returns:
        Success message
    """
    return browser_press_key.func(key, times=times)


@mcp.tool
def browser_scroll_tool(direction: str = "down", amount: int = 500) -> str:
    """Scroll the page.

    Args:
        direction: Scroll direction, 'up' or 'down' (default: 'down')
        amount: Scroll amount in pixels (default: 500)

    Returns:
        Success message
    """
    return browser_scroll.func(direction=direction, amount=amount)


# ==================== Agent Tools from tools/ directory ====================

@mcp.tool
def vision_analyze_tool(
    query: str,
    image_path: Optional[str] = None
) -> str:
    """Analyze images using GLM-4V vision model.

    Args:
        query: The query/question about the image
        image_path: Path to image file (optional, uses current screenshot if not provided)

    Returns:
        Vision analysis result
    """
    return vision_analyze.func(query, image_path=image_path)


@mcp.tool
def locate_element_tool(
    query: str,
    image_path: Optional[str] = None
) -> str:
    """Locate element using vision analysis and coordinate conversion.

    This tool combines vision_analyze and coordinate conversion to find
    elements on a page and return their coordinates in original image system.

    Args:
        query: Description of element to locate (e.g., "search input box", "submit button")
        image_path: Path to image file (optional, uses current screenshot if not provided)

    Returns:
        JSON string with element location, converted coordinates, and analysis details

    Example:
        locate_element_tool("search input box") -> returns coordinates of search box
    """
    result = locate_element.invoke({"query": query, "image_path": image_path})
    # Handle Command object - extract update dict for serialization
    serializable_result = serialize_result(result)
    return json.dumps(serializable_result, ensure_ascii=False, indent=2)


@mcp.tool
def coordinate_convert_box_tool(
    box: List[int],
    original_width: int,
    original_height: int,
) -> str:
    """Convert GLM-4V coordinates back to original image coordinate system.

    Args:
        box: Bounding box from GLM-4V [xmin, ymin, xmax, ymax]
        original_width: Original image width
        original_height: Original image height

    Returns:
        JSON string with converted coordinates
    """
    return coordinate_convert_box.func(box, original_width, original_height)


@mcp.tool
def coordinate_parse_and_convert_tool(
    text: str,
    original_width: int,
    original_height: int,
) -> str:
    """Parse coordinates from text and convert back to original image coordinate system.

    Args:
        text: Text containing coordinates (e.g., from vision model response)
        original_width: Original image width
        original_height: Original image height

    Returns:
        JSON string with converted coordinates
    """
    return coordinate_parse_and_convert.func(text, original_width, original_height)


@mcp.tool
def coordinate_convert_from_image_tool(
    text: str,
    image_path: str,
) -> str:
    """Parse coordinates from text and convert back based on image dimensions.

    Args:
        text: Text containing coordinates (e.g., from vision model response)
        image_path: Path to image file (used to get original dimensions)

    Returns:
        JSON string with converted coordinates
    """
    return coordinate_convert_from_image.func(text, image_path)


# ==================== Tab Management Tools ====================

@mcp.tool
def browser_list_tabs_tool() -> str:
    """List all browser tabs.

    Returns:
        JSON string with list of tabs including their titles and URLs
    """
    return list_tabs()


@mcp.tool
def browser_switch_tab_tool(tab_index: int) -> str:
    """Switch to a specific tab by index.

    Args:
        tab_index: The index of tab to switch to (0-based)

    Returns:
        Success message with new tab title and URL
    """
    return switch_tab(tab_index)


@mcp.tool
def browser_new_tab_tool(url: Optional[str] = None) -> str:
    """Open a new tab.

    Args:
        url: Optional URL to navigate to in the new tab

    Returns:
        Success message with new tab title and URL
    """
    return new_tab(url)


@mcp.tool
def browser_close_tab_tool(tab_index: Optional[int] = None) -> str:
    """Close a tab.

    Args:
        tab_index: Optional index of tab to close (0-based).
                   If not provided, closes the current tab.

    Returns:
        Success message
    """
    return close_tab(tab_index)


@mcp.tool
def browser_get_current_tab_info_tool() -> str:
    """Get information about the current tab.

    Returns:
        JSON string with current tab title and URL
    """
    return get_current_tab_info()


if __name__ == "__main__":
    # Run MCP server with HTTP or STDIO transport
    import sys
    # Check for transport argument
    transport = "http" if len(sys.argv) > 1 and sys.argv[1] == "http" else "stdio"

    if transport == "http":
        # HTTP transport for testing
        mcp.run(transport="http", port=8000, host="127.0.0.1")
    else:
        # STDIO transport (default)
        mcp.run()
