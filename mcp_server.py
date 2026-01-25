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
from zhipuai import ZhipuAI
from utils.drission_page import create_browser


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
async def screenshot() -> str:
    """Take a screenshot of current page.

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
async def get(
    url: Optional[str] = None,
    formats: Optional[str | List[Literal["markdown", "html", "img", "mhtml"]]] = None
) -> str:
    """Navigate to a URL or get current page info, save in specified format(s).

    Args:
        url: The webpage URL to navigate to. If not provided, returns current page info.
        formats: Output format(s) - can be single format (string) or list of formats:
                 "markdown", "html", "img", "mhtml"
                 If not provided, defaults to ["markdown"]

    Returns:
        str: File path(s) to saved content (JSON array if multiple formats),
              or JSON with page title if url not provided
    """
    try:
        page = get_browser()

        # If no URL provided, return current page info
        if url is None:
            return json.dumps({
                "title": page.title,
                "url": page.url
            }, ensure_ascii=False, indent=2)

        # Navigate to URL
        page.get(url)

        # Set default format to markdown
        if formats is None:
            formats = ["markdown"]

        # Ensure formats is a list
        if isinstance(formats, str):
            formats = [formats]

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

        # Return results
        if len(results) ==1:
            return results[0]
        else:
            # Return as JSON array for multiple formats
            return json.dumps({
                "files": results,
                "count": len(results),
                "formats": formats
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        raise RuntimeError(f"Failed to get page: {e}")


async def encode_image_async(image_path: Path) -> str:
    """Async encode image to base64 using thread pool."""
    def _encode():
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    return await asyncio.to_thread(_encode)


@mcp.tool
async def vision(
    query: str,
    image_path: Optional[str] = None,
    model: Optional[str] = None
) -> str:
    """Analyze images using GLM-4V vision model.

    Args:
        query: The query/question about the image
        image_path: Path to image file (optional, uses current screenshot if not provided)
        model: Vision model to use (default: from config or glm-4v-flash)

    Returns:
        str: Vision analysis result
    """
    try:
        # Get API key
        api_key = os.environ.get('ZAI_API_KEY')
        if not api_key:
            raise ValueError("ZAI_API_KEY not found in environment variables")

        # Use provided model or default from config
        vision_model = model or DEFAULT_VISION_MODEL

        # Initialize client
        client = ZhipuAI(api_key=api_key)

        # Determine image source
        if image_path:
            # Use provided image file
            img_path = Path(image_path)
            if not img_path.exists():
                raise ValueError(f"Image file not found: {image_path}")
        else:
            # Take current screenshot
            page = get_browser()
            screenshot_data = page.get_screenshot(as_bytes=True)

            # Save to output directory
            timestamp = generate_timestamp()
            img_path = OUTPUT_DIR / f"temp_vision_{timestamp}.png"
            with open(img_path, 'wb') as f:
                f.write(screenshot_data)

        # Encode image to base64 asynchronously
        image_base64 = await encode_image_async(img_path)

        # Send to vision model
        response = client.chat.completions.create(
            model=vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": query
                        }
                    ]
                }
            ],
            temperature=VISION_TEMPERATURE,
            max_tokens=VISION_MAX_TOKENS
        )

        return response.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"Vision analysis failed: {e}")


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
