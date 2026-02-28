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
from typing import Optional, Literal, List, Union
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
    new_tab,
    close_tab,
)

# Import network listener tools
from tools.network_listener import (
    get_url_with_response_listener,
    response_listener_stop,
    get_response_listener_data,
    clear_response_listener_data,
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
    tab_id: Optional[Union[int, str]] = None,
    formats: List[Literal["markdown", "html", "img", "mhtml"]] = ["markdown"]
) -> str:
    """Navigate to a URL or get current page, save in specified format(s).

    Args:
        url: The webpage URL to navigate to. If not provided, saves the current page.
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)
        formats: Output format(s) as list: ["markdown"], ["html"], ["img"], ["mhtml"],
                 or multiple formats: ["markdown", "html", "img"]
                 Defaults to ["markdown"]

    Returns:
        str: JSON with title, url, and file(s) - single "file" if one format,
              or "files" array if multiple formats
    """
    try:
        from tools.tab_manager import get_tab_object

        # Get specified tab object
        page, metadata = get_tab_object(tab_id)

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

        # Return JSON with title, url, file(s), and tab info
        if len(results) == 1:
            return json.dumps({
                "title": page.title,
                "url": page.url,
                "file": results[0],
                "tab": metadata
            }, ensure_ascii=False, indent=2)
        else:
            # Return with files array for multiple formats
            return json.dumps({
                "title": page.title,
                "url": page.url,
                "files": results,
                "count": len(results),
                "formats": formats,
                "tab": metadata
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        raise RuntimeError(f"Failed to get page: {e}")


# ==================== Browser Tools from tools/ directory ====================

@mcp.tool
def browser_navigate_tool(url: str, tab_id: Optional[Union[int, str]] = None) -> str:
    """Navigate browser to specified URL.

    Args:
        url: The URL to navigate to
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        Success message with page title and tab info
    """
    # Call the tool function directly
    return browser_navigate.func(url, tab_id=tab_id)


@mcp.tool
def browser_get_current_page_tool(tab_id: Optional[Union[int, str]] = None) -> str:
    """Get current page information.

    Args:
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        JSON string with page title and URL
    """
    return browser_get_current_page.func(tab_id=tab_id)


@mcp.tool
def browser_screenshot_tool(tab_id: Optional[Union[int, str]] = None, save_file: bool = False) -> str:
    """Take a screenshot of the specified tab.

    Args:
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)
        save_file: Whether to save screenshot to file (default False, returns base64 for faster use)

    Returns:
        str: File path to saved screenshot (if save_file=True) or base64 data (if save_file=False)
    """
    try:
        from tools.tab_manager import get_tab_object

        # Get specified tab object
        tab, metadata = get_tab_object(tab_id)

        if save_file:
            # Screenshot and save to file
            screenshot_data = tab.get_screenshot(as_bytes=True)

            # Generate filename with timestamp
            timestamp = generate_timestamp()
            filename = f"screenshot_{timestamp}.png"

            # Save to output directory
            filepath = OUTPUT_DIR / filename
            with open(filepath, 'wb') as f:
                f.write(screenshot_data)

            result = {
                "file": str(filepath),
                "format": "file",
                "tab": metadata
            }
        else:
            # Screenshot and return base64 (faster, no file I/O)
            screenshot_base64 = tab.get_screenshot(as_base64='png')

            result = {
                "data": screenshot_base64,
                "format": "base64",
                "tab": metadata
            }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        raise RuntimeError(f"Screenshot failed: {e}")


@mcp.tool
def browser_click_tool(x: int, y: int, tab_id: Optional[Union[int, str]] = None) -> str:
    """Click at specified coordinates on the page.

    Args:
        x: X coordinate
        y: Y coordinate
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        Success message with tab info
    """
    return browser_click.func(x, y, tab_id=tab_id)


@mcp.tool
def browser_input_tool(
    x: int, y: int, text: str, clear: bool = True,
    tab_id: Optional[Union[int, str]] = None
) -> str:
    """Click input box at coordinates and input text.

    Args:
        x: X coordinate of input box
        y: Y coordinate of input box
        text: Text to input
        clear: Whether to clear existing text first (default: True)
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        Success message with tab info
    """
    return browser_input.func(x, y, text, clear=clear, tab_id=tab_id)


@mcp.tool
def browser_press_key_tool(
    key: str, times: int = 1,
    tab_id: Optional[Union[int, str]] = None
) -> str:
    """Press keyboard keys.

    Args:
        key: Key name (e.g., 'enter', 'escape', 'space', 'tab')
        times: Number of times to press (default: 1)
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        Success message with tab info
    """
    return browser_press_key.func(key, times=times, tab_id=tab_id)


@mcp.tool
def browser_scroll_tool(
    direction: str = "down", amount: int = 500,
    tab_id: Optional[Union[int, str]] = None
) -> str:
    """Scroll the page.

    Args:
        direction: Scroll direction, 'up' or 'down' (default: 'down')
        amount: Scroll amount in pixels (default: 500)
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        Success message with tab info
    """
    return browser_scroll.func(direction=direction, amount=amount, tab_id=tab_id)


# ==================== Agent Tools from tools/ directory ====================

@mcp.tool
def vision_analyze_tool(
    query: str,
    image_path: Optional[str] = None,
    tab_id: Optional[Union[int, str]] = None
) -> str:
    """Analyze images using GLM-4V vision model.

    Args:
        query: The query/question about the image
        image_path: Path to image file (optional, uses current screenshot if not provided)
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        Vision analysis result with tab info
    """
    return vision_analyze.func(query, image_path=image_path, tab_id=tab_id)


@mcp.tool
def locate_element_tool(
    query: str,
    image_path: Optional[str] = None,
    tab_id: Optional[Union[int, str]] = None
) -> str:
    """Locate element using vision analysis and coordinate conversion.

    This tool combines vision_analyze and coordinate conversion to find
    elements on a page and return their coordinates in original image system.

    Args:
        query: Description of element to locate (e.g., "search input box", "submit button")
        image_path: Path to image file (optional, uses current screenshot if not provided)
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        JSON string with element location, converted coordinates, and analysis details

    Example:
        locate_element_tool("search input box") -> returns coordinates of search box
    """
    # Call the tool function directly with runtime=None (MCP doesn't support ToolRuntime)
    result = locate_element.func(query, image_path=image_path, tab_id=tab_id, runtime=None)
    # Handle Command object - extract update dict for serialization
    serializable_result = serialize_result(result)
    return json.dumps(serializable_result, ensure_ascii=False, indent=2)


# ==================== Tab Management Tools ====================

@mcp.tool
def browser_list_tabs_tool() -> str:
    """List all browser tabs with full information.

    Returns:
        JSON string with list of tabs including tab_id, title, url, index, is_current
    """
    from tools.tab_manager import list_all_tabs
    result = list_all_tabs()
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool
def browser_new_tab_tool(url: Optional[str] = None) -> str:
    """Open a new tab.

    Args:
        url: Optional URL to navigate to in the new tab

    Returns:
        Success message with new tab title and URL and tab info
    """
    result = new_tab(url)
    # Parse the JSON result and ensure it's properly formatted
    return result


@mcp.tool
def browser_close_tab_tool(tab_id: Union[int, str] = None) -> str:
    """Close a tab.

    Args:
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        Success message
    """
    from tools.tab_manager import close_tab_object
    result = close_tab_object(tab_id)
    return json.dumps(result, ensure_ascii=False, indent=2)


# ==================== Network Listener Tools ====================

@mcp.tool
def network_start_listener_tool(
    tab_id: Optional[Union[int, str]] = None,
    mimeType: Literal[
        "text/html", "text/css", "text/javascript", "application/javascript",
        "text/plain", "text/xml", "text/csv", "application/json",
        "application/octet-stream", "application/zip", "application/pdf",
        "multipart/form-data", "application/xml",
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "image/svg+xml", "image/x-icon",
        "audio/mpeg", "audio/ogg", "video/mp4", "video/webm", "video/ogg"
    ] = "application/json",
    url_include: str = ".",
    refresh: bool = False
) -> str:
    """Start listening to network packets (HTTP responses) on the specified tab.

    This tool enables monitoring of network responses using Chrome DevTools Protocol (CDP).
    It captures responses that match the specified mimeType and URL pattern.

    Args:
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)
        mimeType: Filter responses by MIME type (default: application/json)
                  Options include: text/html, text/css, text/javascript,
                  application/json, image/jpeg, etc.
        url_include: Filter responses by URL substring (default: "." matches all)
        refresh: Whether to refresh the page after starting listener (default: False)

    Returns:
        JSON string with listener status, tab info, and configuration

    Example:
        # Listen for all JSON responses
        network_start_listener_tool(mimeType="application/json")

        # Listen for responses containing "api" in URL
        network_start_listener_tool(url_include="api")

        # Listen for HTML responses and refresh page
        network_start_listener_tool(mimeType="text/html", refresh=True)
    """
    return get_url_with_response_listener(
        tab_id=tab_id,
        mimeType=mimeType,
        url_include=url_include,
        refresh=refresh
    )


@mcp.tool
def network_stop_listener_tool(
    tab_id: Optional[Union[int, str]] = None,
    clear_data: bool = False
) -> str:
    """Stop listening to network packets.

    Args:
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)
        clear_data: Whether to clear collected data (default: False)

    Returns:
        JSON string with stop status and tab info
    """
    return response_listener_stop(tab_id=tab_id, clear_data=clear_data)


@mcp.tool
def network_get_listener_data_tool() -> str:
    """Get all collected network packet data.

    Returns:
        JSON string with count and list of all captured network responses.
        Each response includes URL, mimeType, status, headers, and other CDP data.

    Example:
        # Get all captured responses
        network_get_listener_data_tool()

        # Returns: {"status": "success", "count": 5, "data": [...]}
    """
    return get_response_listener_data()


@mcp.tool
def network_clear_listener_data_tool() -> str:
    """Clear all collected network listener data.

    This tool removes all previously captured network responses from memory.
    Useful when you want to start fresh or free memory.

    Returns:
        JSON string with clear status

    Example:
        network_clear_listener_data_tool()
        # Returns: {"status": "success", "message": "监听数据已清空"}
    """
    return clear_response_listener_data()


if __name__ == "__main__":
    # Run MCP server with HTTP or STDIO transport
    import sys
    # Check for transport argument
    transport = "http" if len(sys.argv) > 1 and sys.argv[1] == "stdio" else "http"

    if transport == "http":
        # HTTP transport for testing
        mcp.run(transport="http", port=8101, host="127.0.0.1")
    else:
        # STDIO transport (default)
        mcp.run()
