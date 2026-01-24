#!/usr/bin/env python
"""
Dripage MCP Server - Browser automation and vision analysis via FastMCP.
"""
import os
import sys
import base64
import tempfile
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add project directory to path for imports
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from fastmcp import FastMCP
from zhipuai import ZhipuAI
from markitdown import MarkItDown

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
        'output': {'directory': 'output', 'images_subdir': 'images'},
        'vision': {'model': 'glm-4v-flash', 'temperature': 0.7, 'max_tokens': 1024}
    }

# Extract configuration
BROWSER_ADDRESS = config['browser']['address']
OUTPUT_DIR = project_dir / config['output']['directory']
IMAGES_DIR = OUTPUT_DIR / config['output']['images_subdir']
DEFAULT_VISION_MODEL = config['vision']['model']
VISION_TEMPERATURE = config['vision']['temperature']
VISION_MAX_TOKENS = config['vision']['max_tokens']

# Ensure output directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def get_browser() -> object:
    """Create or get a browser instance using default address."""
    return create_browser(address=BROWSER_ADDRESS)


# Create MCP server instance
mcp = FastMCP(name="Dripage MCP 🚀")


@mcp.tool
def screenshot() -> str:
    """Take a screenshot of the current page.

    Returns:
        str: File path to the saved screenshot
    """
    try:
        page = get_browser()

        # Screenshot full page
        screenshot_data = page.get_screenshot(as_bytes=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"

        # Save to output/images
        filepath = IMAGES_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(screenshot_data)

        return str(filepath)

    except Exception as e:
        raise RuntimeError(f"Screenshot failed: {e}")


@mcp.tool
def get(url: str) -> str:
    """Navigate to a URL.

    Args:
        url: The webpage URL to navigate to

    Returns:
        str: Success message
    """
    try:
        page = get_browser()
        page.get(url)
        return f"Successfully navigated to {url}"
    except Exception as e:
        raise RuntimeError(f"Failed to navigate to {url}: {e}")


@mcp.tool
def get2markdown(url: str) -> str:
    """Convert a webpage URL to markdown format.

    Args:
        url: The webpage URL to convert

    Returns:
        str: Markdown content of the webpage
    """
    try:
        page = get_browser()
        page.get(url)

        # Get page HTML
        html_content = page.html

        # Save HTML to temp file for markitdown
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name

        try:
            md = MarkItDown()
            result = md.convert(temp_file)
            return result.text_content
        finally:
            os.unlink(temp_file)  # Clean up temp file

    except Exception as e:
        raise RuntimeError(f"Failed to convert {url} to markdown: {e}")


@mcp.tool
def vision(
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

            # Save to temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = IMAGES_DIR / f"temp_vision_{timestamp}.png"
            with open(img_path, 'wb') as f:
                f.write(screenshot_data)

        # Encode image to base64
        with open(img_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')

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
