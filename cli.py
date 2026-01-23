#!/usr/bin/env python
"""
Dripage CLI - Command-line interface for browser automation and vision tasks.
"""
import os
import sys
import base64
import hashlib
from pathlib import Path
from typing import Optional

# Add project directory to path for imports
# Get the directory containing this script
project_dir = Path(__file__).resolve().parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

import click
from zhipuai import ZhipuAI
from markitdown import MarkItDown

from utils.drission_page import create_browser


# Default browser address
DEFAULT_BROWSER_ADDRESS = '127.0.0.1:19222'

# Default output directory (relative to project root)
OUTPUT_DIR = project_dir / 'output'
IMAGES_DIR = OUTPUT_DIR / 'images'

# Ensure output directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def get_browser(address: str = DEFAULT_BROWSER_ADDRESS):
    """Create or get a browser instance."""
    return create_browser(address=address)


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Dripage CLI - Browser automation and vision analysis tool."""
    pass


@cli.command()
@click.argument('url')
@click.option('--address', default=DEFAULT_BROWSER_ADDRESS, help='Browser address (default: 127.0.0.1:19222)')
def get2md(url: str, address: str):
    """Convert a webpage URL to markdown format.

    Args:
        URL: The webpage URL to convert
        --address: Browser address (default: 127.0.0.1:19222)
    """
    try:
        click.echo(f"Navigating to {url}...")
        page = get_browser(address=address)
        page.get(url)

        # Get page HTML
        html_content = page.html

        click.echo("Converting to markdown...")

        # Save HTML to temp file for markitdown
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name

        try:
            md = MarkItDown()
            result = md.convert(temp_file)
        finally:
            os.unlink(temp_file)  # Clean up temp file

        click.echo("\n" + "=" * 80)
        click.echo(result.text_content)
        click.echo("=" * 80)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--id', default=None, help='Page element ID to screenshot (optional)')
@click.option('--address', default=DEFAULT_BROWSER_ADDRESS, help='Browser address (default: 127.0.0.1:19222)')
def screenshot(id: Optional[str], address: str):
    """Take a screenshot of the current page or specific element.

    Args:
        --id: Element ID to screenshot (default: None, captures full page)
        --address: Browser address (default: 127.0.0.1:19222)
    """
    try:
        page = get_browser(address=address)

        if id:
            click.echo(f"Capturing screenshot of element with ID: {id}...")
            element = page.ele(f'#{id}')
            if not element:
                click.echo(f"Error: Element with ID '{id}' not found", err=True)
                sys.exit(1)

            # Screenshot specific element
            screenshot_data = element.get_screenshot(as_bytes=True)
            filename = f"screenshot_{id}_{int(os.path.getmtime(os.getcwd()))}.png"
        else:
            click.echo("Capturing full page screenshot...")
            # Screenshot full page
            screenshot_data = page.get_screenshot(as_bytes=True)
            filename = f"screenshot_{int(os.path.getmtime(os.getcwd()))}.png"

        # Save to output/images
        filepath = IMAGES_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(screenshot_data)

        click.echo(f"Screenshot saved to: {filepath}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--image', default=None, help='Path to image file (optional, uses current screenshot if not provided)')
@click.option('--model', default='glm-4v-flash', help='Model to use: glm-4v, glm-4v-plus, glm-4v-flash (default: glm-4v-flash)')
@click.option('--api-key', default=None, help='ZhipuAI API key (default: from ZHIPUAI_API_KEY env var)')
@click.option('--address', default=DEFAULT_BROWSER_ADDRESS, help='Browser address (default: 127.0.0.1:19222)')
def vision(query: str, image: Optional[str], model: str, api_key: Optional[str], address: str):
    """Analyze images using GLM-4V vision model.

    Args:
        QUERY: The query/question about the image
        --image: Path to image file (optional)
        --model: Vision model to use (default: glm-4v-flash)
        --api-key: ZhipuAI API key (default: from ZHIPUAI_API_KEY env var)
        --address: Browser address (default: 127.0.0.1:19222)
    """
    try:
        # Get API key
        if not api_key:
            api_key = os.environ.get('ZAI_API_KEY')
            if not api_key:
                click.echo("Error: ZAI_API_KEY not found. Set it as environment variable or use --api-key option", err=True)
                sys.exit(1)

        # Initialize client
        click.echo(f"Initializing ZhipuAI client with model: {model}...")
        client = ZhipuAI(api_key=api_key)

        # Determine image source
        if image:
            # Use provided image file
            image_path = Path(image)
            if not image_path.exists():
                click.echo(f"Error: Image file not found: {image}", err=True)
                sys.exit(1)
            click.echo(f"Using image: {image_path}")
        else:
            # Take current screenshot
            click.echo("No image provided, capturing current page...")
            page = get_browser(address=address)
            screenshot_data = page.get_screenshot(as_bytes=True)

            # Save to temporary file
            image_path = IMAGES_DIR / f"temp_vision_{int(os.path.getmtime(os.getcwd()))}.png"
            with open(image_path, 'wb') as f:
                f.write(screenshot_data)
            click.echo(f"Screenshot saved to: {image_path}")

        # Encode image to base64
        with open(image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')

        # Send to vision model
        click.echo(f"Analyzing image with query: {query}...")
        response = client.chat.completions.create(
            model=model,
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
            temperature=0.7,
            max_tokens=1024
        )

        # Print result
        click.echo("\n" + "=" * 80)
        click.echo("Vision Analysis Result:")
        click.echo("=" * 80)
        click.echo(response.choices[0].message.content)
        click.echo("=" * 80)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    cli()
