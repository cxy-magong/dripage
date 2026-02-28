"""
Page operations module for Dripage CLI.

Reuses existing tools from tools/ directory to provide page operations
like get markdown, screenshot, and vision analysis.
"""
import json
from pathlib import Path
from typing import Optional

from click import echo
from config.settings import get_current_config, ConfigManager
from cli.browser import get_page_object


def get_markdown(url: Optional[str] = None, save: bool = False, tab_id: Optional[str] = None) -> str:
    """
    Get page content as markdown.

    Args:
        url: Page URL to navigate to. If None, gets current page.
        save: Whether to save to file. Default False (return content only).
        tab_id: Tab ID or index to operate on. If None, uses current page.

    Returns:
        JSON string with markdown content and file path.
    """
    try:
        from markitdown import MarkItDown
        from tools import get_browser, save_browser_screenshot
        from tools.tab_manager import get_tab_object

        config = get_current_config()
        if tab_id is not None:
            # Get specific tab
            try:
                tab_id_int = int(tab_id) if tab_id.isdigit() else tab_id
                page, tab_info = get_tab_object(tab_id_int)
            except Exception as e:
                page = get_page_object()
        else:
            page = get_page_object()

        if url:
            page.get(url)
            echo(f"Navigated to: {url}")

        # Get HTML
        html_content = page.html

        # Convert to markdown
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name

        try:
            md = MarkItDown()
            result = md.convert(temp_file)
            markdown_text = result.text_content

            if save:
                # Save markdown file
                from tools.agent_tools import generate_timestamp
                timestamp = generate_timestamp()
                output_dir = Path(config.output.get('directory', 'output/data'))

                # Create page_data subdirectory if needed
                page_data_dir = output_dir / 'page_data'
                page_data_dir.mkdir(exist_ok=True)

                filename = f"page_{timestamp}.md"
                filepath = page_data_dir / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(markdown_text)

                return json.dumps({
                    "status": "success",
                    "url": page.url,
                    "title": page.title,
                    "file": str(filepath),
                    "content": markdown_text
                }, ensure_ascii=False, indent=2)
            else:
                # Just return markdown text
                return json.dumps({
                    "status": "success",
                    "url": page.url,
                    "title": page.title,
                    "content": markdown_text
                }, ensure_ascii=False, indent=2)

        finally:
            # Clean up temp file
            if 'temp_file' in locals() and Path(temp_file).exists():
                os.unlink(temp_file)

    except Exception as e:
        error_msg = f"Failed to get markdown: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


def get_screenshot(full_page: bool = True, save: bool = True) -> str:
    """
    Take a screenshot of the current page.

    Args:
        full_page: Capture full page or viewport only.
        save: Whether to save to file.

    Returns:
        JSON string with screenshot file path.
    """
    try:
        from tools import get_browser, save_browser_screenshot
        from tools.agent_tools import generate_timestamp

        config = get_current_config()
        page = get_page_object()

        # Take screenshot
        screenshot_path = save_browser_screenshot(prefix="screenshot", save=save)

        if save:
            echo(f"✓ Screenshot saved to: {screenshot_path}")

        return json.dumps({
            "status": "success",
            "file": screenshot_path,
            "full_page": full_page
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to take screenshot: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


def get_html(url: Optional[str] = None, save: bool = False, tab_id: Optional[str] = None) -> str:
    """
    Get page content as HTML.

    Args:
        url: Page URL to navigate to. If None, gets current page.
        save: Whether to save to file. Default False (return content only).
        tab_id: Tab ID or index to operate on. If None, uses current page.

    Returns:
        JSON string with HTML content and file path.
    """
    try:
        from tools.tab_manager import get_tab_object
        from tools.agent_tools import generate_timestamp

        config = get_current_config()
        if tab_id is not None:
            try:
                tab_id_int = int(tab_id) if tab_id.isdigit() else tab_id
                page, tab_info = get_tab_object(tab_id_int)
            except Exception as e:
                page = get_page_object()
        else:
            page = get_page_object()

        if url:
            page.get(url)
            echo(f"Navigated to: {url}")

        html_content = page.html

        if save:
            from tools.agent_tools import generate_timestamp
            timestamp = generate_timestamp()
            output_dir = Path(config.output.get('directory', 'output/data'))

            page_data_dir = output_dir / 'page_data'
            page_data_dir.mkdir(exist_ok=True)

            filename = f"page_{timestamp}.html"
            filepath = page_data_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            return json.dumps({
                "status": "success",
                "url": page.url,
                "title": page.title,
                "file": str(filepath),
                "content": html_content
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "status": "success",
                "url": page.url,
                "title": page.title,
                "content": html_content
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to get HTML: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


def analyze_vision(query: str, image_path: Optional[str] = None, save_file: bool = False) -> str:
    """
    Analyze page screenshot using vision model.

    Args:
        query: Question about page/image.
        image_path: Path to image file. If None, takes current page screenshot.
        save_file: Whether to save screenshot file (default False, faster with in-memory analysis).

    Returns:
        JSON string with analysis result.
    """
    try:
        from tools.agent_tools import vision_analyze, generate_timestamp
        from tools import get_browser

        config = get_current_config()
        page = get_page_object()

        # Use configured vision model
        api_key = config.vision.api_key if config.vision.api_key else None

        # Get image path or take screenshot
        if image_path:
            img_path = Path(image_path)
            # When image_path is provided, always save=False (file already exists)
            save_file = False
        else:
            # No need to save file if save_file=False (vision_analyze handles it)
            img_path = None

        # Analyze with vision model
        result_dict = json.loads(vision_analyze.func(
            query=query,
            image_path=str(img_path) if img_path else None,
            tab_id=None,
            runtime=None,
            save_file=save_file
        ))

        # Add status field for CLI compatibility
        result_dict['status'] = 'success'

        if save_file:
            echo(f"✓ Vision analysis completed (saved to {result_dict.get('image_path')})")
        else:
            echo(f"✓ Vision analysis completed (in-memory)")

        return json.dumps(result_dict, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to analyze vision: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--url', help='Test URL for markdown')
    def test_markdown(url):
        result = get_markdown(url)
        print(result)

    @click.command()
    @click.option('--query', default='What is in this image?', help='Test vision query')
    def test_vision(query):
        result = analyze_vision(query)
        print(result)

    test_markdown()
