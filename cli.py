#!/usr/bin/env python
"""
Dripage CLI - Unified command-line interface for browser automation and packet capture.

All-in-one CLI that integrates browser management, network packet capture,
page operations, and visual analysis. Avoids repetitive parameters through
default configuration management.
"""
import os
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import click
from dotenv import load_dotenv
load_dotenv()

import sys
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from click import echo, style, secho
from cli_config import (
    ConfigManager,
    get_current_config,
    get_default_config,
    DEFAULT_CONFIG_FILE,
    SESSION_CONFIG_FILE
)
from cli_browser import (
    start_browser,
    stop_browser,
    get_browser_status,
    get_cdp_url,
    verify_cdp_connection,
    get_page_object
)
from cli_capture import (
    NetworkCapture,
    PacketFilter,
    start_global_capture,
    stop_global_capture,
    get_global_capture
)
from cli_page import (
    get_markdown,
    get_screenshot,
    analyze_vision
)
from cli_location import (
    locate_element,
    locate_and_click
)


# ==================== CLI Entry Point ====================

@click.group()
@click.version_option(version='0.2.0')
def cli():
    """Dripage CLI - Browser automation and packet capture tool.

    Unified command-line interface for controlling browsers, capturing network packets,
    and analyzing web pages.
    """
    pass


# ==================== Config Commands ====================

@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command(name='set')
@click.argument('name', required=False)
@click.option('--set-default', is_flag=True, help='Set as default configuration')
def config_set_session(name: Optional[str] = None, set_default: bool = False):
    """Set or create a session configuration.

    Examples:
        dripage config set my-session --set-default

        dripage config set dev
    """
    manager = ConfigManager()

    if name:
        if set_default:
            # Save current config as default
            current_config = manager.load_config()
            manager.save_config(current_config)
            echo(f"✓ Set current configuration as default")
            echo(f"  Browser: {current_config.browser.name} @ {current_config.browser.address}")
        else:
            # Create new session
            from cli_config import get_current_config
            session_config = get_current_config()
            manager.save_session(name, session_config)
            manager.set_current_session(name)
            echo(f"✓ Created session '{name}'")
            echo(f"  Browser: {session_config.browser.name} @ {session_config.browser.address}")
    else:
        # Show current config
        current_config = manager.load_config()
        echo("Current Configuration:")
        echo(f"  Browser: {style(fg='cyan')}{current_config.browser.name} @ {current_config.browser.address}")
        echo(f"  Vision: {style(fg='cyan')}{current_config.vision.model}")
        echo(f"  Capture: {style(fg='green' if current_config.capture.enabled else 'red')}{current_config.capture.enabled}")
        echo()
        echo(f"Config file: {DEFAULT_CONFIG_FILE}")
        echo(f"Session file: {SESSION_CONFIG_FILE}")


@config.command(name='list')
def list_sessions():
    """List all available sessions."""
    manager = ConfigManager()
    sessions = manager.list_sessions()

    if not sessions:
        echo("ℹ️  No sessions found")
        return

    echo("Available Sessions:")
    echo()
    for session in sessions:
        session_id = session.get('session_id', 'default')
        browser = session.get('browser', {})
        echo(f"  {style(fg='cyan')}{session_id}:")
        echo(f"    Browser: {browser.get('name', 'default')} @ {browser.get('address', 'N/A')}")


@config.command(name='use')
@click.argument('name')
def use_session(name: str):
    """Switch to a session configuration.

    Example:
        dripage config use dev
    """
    manager = ConfigManager()
    sessions = manager.list_sessions()
    session_ids = [s.get('session_id') for s in sessions]

    if name not in session_ids:
        echo(f"✗ Session '{name}' not found")
        echo(f"  Available sessions: {', '.join(session_ids)}")
        sys.exit(1)

    # Switch to session
    manager.set_current_session(name)
    echo(f"✓ Switched to session '{name}'")

    # Print current config
    current_config = manager.load_session(name)
    if current_config:
        echo(f"  Browser: {current_config.browser.name} @ {current_config.browser.address}")
        echo(f"  Vision: {current_config.vision.model}")
        echo(f"  Capture: {current_config.capture.enabled}")


@config.command(name='reset')
def reset():
    """Reset to default configuration."""
    ConfigManager().save_config(get_default_config())
    echo("✓ Reset to default configuration")


# ==================== Browser Commands ====================

@cli.group()
def browser():
    """Browser management commands."""
    pass


@browser.command(name='start')
@click.option('--name', help='Browser name from config/browsers.yaml')
@click.option('--address', help='Browser address (e.g., 127.0.0.1:19222)')
@click.option('--browser-path', help='Path to browser executable')
@click.option('--user-data-dir', help='Path to user data directory')
def browser_start(name: Optional[str], address: str, browser_path: str, user_data_dir: str):
    """Start a browser instance.

    Examples:
        dripage browser start

        dripage browser start --name browser1

        dripage browser start --address 127.0.0.1:19222
    """
    config_override = {}
    if address:
        config_override['address'] = address
    if browser_path:
        config_override['browser_path'] = browser_path
    if user_data_dir:
        config_override['user_data_dir'] = user_data_dir

    result = start_browser(name=name, config_override=config_override)

    if result['success']:
        data = result['data']
        echo(f"✓ Browser started successfully")
        echo(f"  Name: {data.get('name', 'default')}")
        echo(f"  CDP URL: {data.get('cdp_url', 'N/A')}")
        echo(f"  Address: {data.get('address', 'N/A')}")
        echo(f"  PID: {data.get('pid', 'N/A')}")
    else:
        echo(style(f"✗ {result['message']}", fg='red', bold=True))
        sys.exit(1)


@browser.command(name='stop')
@click.option('--name', help='Browser name to stop')
def browser_stop(name: Optional[str] = None):
    """Stop a browser instance.

    Examples:
        dripage browser stop

        dripage browser stop --name browser1
    """
    result = stop_browser(name=name)

    if result['success']:
        data = result.get('data', {})
        echo(f"✓ Browser stopped: {data.get('name', 'default')}")
    else:
        echo(style(f"✗ {result['message']}", fg='red', bold=True))
        sys.exit(1)


@browser.command(name='status')
@click.option('--name', help='Browser name to check. If not specified, checks all browsers')
def browser_status(name: Optional[str] = None):
    """Get browser status information.

    Examples:
        dripage browser status

        dripage browser status --name browser1
    """
    result = get_browser_status(name=name)

    if result['success']:
        data = result['data']
        echo(f"✓ Browser status retrieved")

        # Handle single browser or all browsers
        if 'browsers' in data:
            # Multiple browsers
            browsers = data['browsers']
            echo(f"  Total browsers: {data.get('total', 0)}")
            echo(f"  Running: {data.get('running', 0)}")
            echo()

            for browser_name, browser_info in browsers.items():
                status_icon = style('●', fg='green', bold=True) if browser_info.get('status') == 'running' else '○'
                status_text = style('running', fg='green') if browser_info.get('status') == 'running' else 'stopped'

                echo(f"  {status_icon} {style(browser_name, fg='cyan')}: {status_text}")
                if browser_info.get('status') == 'running':
                    echo(f"    Address: {browser_info.get('address', 'N/A')}")
                    echo(f"    CDP URL: {browser_info.get('cdp_url', 'N/A')}")
                    echo(f"    PID: {browser_info.get('pid', 'N/A')}")
                    echo(f"    Started: {browser_info.get('start_time', 'N/A')}")
        else:
            # Single browser
            browser_info = data
            status_icon = style('●', fg='green', bold=True) if browser_info.get('status') == 'running' else '○'
            status_text = style('running', fg='green') if browser_info.get('status') == 'running' else 'stopped'

            echo(f"  {status_icon} {style(browser_info.get('name', 'default'), fg='cyan')}: {status_text}")
            if browser_info.get('status') == 'running':
                echo(f"    Address: {browser_info.get('address', 'N/A')}")
                echo(f"    CDP URL: {browser_info.get('cdp_url', 'N/A')}")
                echo(f"    PID: {browser_info.get('pid', 'N/A')}")
                echo(f"    Started: {browser_info.get('start_time', 'N/A')}")
    else:
        echo(style(f"✗ {result['message']}", fg='red', bold=True))
        sys.exit(1)


@browser.command(name='cdp')
@click.option('--name', help='Browser name to get CDP URL for. If not specified, gets default browser')
def browser_cdp(name: Optional[str] = None):
    """Get CDP WebSocket URL for browser.

    Examples:
        dripage browser cdp

        dripage browser cdp --name browser1
    """
    result = get_cdp_url(name=name)

    if result['success']:
        data = result['data']
        cdp_url = data.get('cdp_url', '')

        echo(f"✓ CDP URL retrieved")
        echo(f"  Browser: {data.get('name', 'default')}")
        if cdp_url:
            echo(f"  CDP URL: {style(cdp_url, fg='cyan')}")
        else:
            echo(f"  CDP URL: {style('Not connected', fg='yellow')}")
    else:
        echo(style(f"✗ {result['message']}", fg='red', bold=True))
        sys.exit(1)


@browser.command(name='verify')
def browser_verify():
    """Verify CDP connection by checking /json/version endpoint.

    Example:
        dripage browser verify
    """
    if verify_cdp_connection():
        echo("✓ CDP connection verified successfully")
    else:
        echo("✗ CDP connection failed")
        echo("  Make sure browser is running with CDP enabled")


# ==================== Capture Commands ====================

@cli.group()
def capture():
    """Network packet capture commands."""
    pass


@capture.command(name='start')
@click.option('--url-contains', help='Filter packets by URL containing text')
@click.option('--content-type', help='Filter by resource type (e.g., application/json)')
@click.option('--method', help='Filter by HTTP method (e.g., GET, POST)')
@click.option('--response-contains', help='Filter by response containing text')
@click.option('--status-code', type=int, help='Filter by HTTP status code')
def capture_start(url_contains: Optional[str] = None, content_type: Optional[str] = None,
                method: Optional[str] = None, response_contains: Optional[str] = None,
                status_code: Optional[int] = None):
    """Start background packet capture with filters.

    Examples:
        dripage capture start

        dripage capture start --content-type application/json --url-contains baidu

        dripage capture start --method POST
    """
    # Build filter criteria
    filter_criteria = None
    if any([url_contains, content_type, method, response_contains, status_code]):
        filter_criteria = PacketFilter(
            url_contains=url_contains,
            content_type=content_type,
            method=method,
            response_contains=response_contains,
            status_code=status_code
        )

    # Get page object
    page = get_page_object()

    # Create capture instance
    capture = NetworkCapture(page_object=page)

    # Start capture
    if capture.start_capture(filter_criteria=filter_criteria):
        filter_desc = capture._format_filter(filter_criteria)
        echo(f"✓ Packet capture started")
        echo(f"  Output dir: {capture.output_dir}")
        if filter_criteria:
            echo(f"  Filters: {filter_desc}")
        else:
            echo(f"  Filters: all (capturing all packets)")
        echo()
        echo("💡 Packets will be captured to files for filtering")
        echo("💡 Use 'dripage capture stop' to save and stop capture")
    else:
        echo("✗ Failed to start packet capture")
        sys.exit(1)


@capture.command(name='stop')
def capture_stop():
    """Stop packet capture and save remaining packets.

    Example:
        dripage capture stop
    """
    if stop_global_capture():
        echo("✓ Packet capture stopped and saved")
    else:
        echo("⚠️  No active capture to stop")


@capture.command(name='query')
@click.option('--limit', type=int, default=100, help='Maximum number of packets to return (default: 100)')
@click.option('--filter', help='jq-style filter query (e.g., .url, .status_code, contains("keyword"))')
def capture_query(limit: int, filter: Optional[str] = None):
    """Query captured packets from files.

    Examples:
        dripage capture query

        dripage capture query --limit 50

        dripage capture query --filter '.status_code == 200'
    """
    from cli_capture import NetworkCapture

    # Find most recent capture file
    capture = NetworkCapture()
    results = capture.query_packets(limit=limit, filter_query=filter)

    if results:
        echo(f"✓ Found {len(results)} packets")
        echo(f"  Limit: {limit}")
        if filter:
            echo(f"  Filter: {filter}")

        # Print summary
        status_codes = {}
        methods = {}
        content_types = {}

        for packet in results:
            status = packet.get('status_code')
            method = packet.get('method')
            content_type = packet.get('resource_type')

            if status:
                status_codes[status] = status_codes.get(status, 0) + 1
            if method:
                methods[method] = methods.get(method, 0) + 1
            if content_type:
                content_types[content_type] = content_types.get(content_type, 0) + 1

        echo()
        echo(f"  Status codes: {status_codes}")
        echo(f"  Methods: {methods}")
        echo(f"  Content types: {content_types}")

        # Print first few packets
        echo()
        echo(f"📦 Sample packets (first 5):")
        for i, packet in enumerate(results[:5], 1):
            packet_url = packet.get('url', 'N/A')[:60]
            packet_method = packet.get('method', 'N/A')
            packet_status = packet.get('status_code', 'N/A')

            echo(f"  [{i}] {packet_method:5} {packet_status:5} {packet_url}")
    else:
        echo("ℹ️  No packets found")
        echo("  Use 'dripage capture start' to begin capturing")


# ==================== Page Commands ====================

@cli.command(name='get')
@click.argument('url', required=False)
@click.option('--save', is_flag=True, help='Save to file')
@click.option('--tab-id', help='Tab ID or index to operate on (default: current page)')
def page_get(url: Optional[str] = None, save: bool = False, tab_id: Optional[str] = None):
    """Get page content as markdown.

    Examples:
        dripage get http://localhost:3000/sign-up

        dripage get

        dripage get --save

        dripage get --tab-id 0
    """
    result = get_markdown(url=url, save=save, tab_id=tab_id)

    data = json.loads(result)
    if data.get('status') == 'success':
        echo(f"✓ Page retrieved successfully")
        echo(f"  URL: {data.get('url', 'N/A')}")
        echo(f"  Title: {data.get('title', 'N/A')}")

        # Get content
        content = data.get('content', '')

        # Show content with truncation
        if len(content) > 3000:
            # Show first 3000 chars
            echo()
            echo(content[:3000])
            echo()
            echo(f"⚠️  Content truncated ({len(content)} chars > 3000 limit)")

            # Auto-save if not already saved
            if 'file' not in data:
                # Re-fetch with save=True to auto-save long content
                save_result = get_markdown(url=None if url else None, save=True, tab_id=tab_id)
                save_data = json.loads(save_result)
                if save_data.get('status') == 'success' and 'file' in save_data:
                    filepath = Path(save_data.get('file', 'N/A')).resolve()
                    echo(f"   Full content saved to: {filepath}")
                else:
                    echo(f"   Failed to save content automatically")
            else:
                # Already saved, show absolute path
                filepath = Path(data.get('file', 'N/A')).resolve()
                echo(f"   Full content saved to: {filepath}")
        else:
            # Show full content
            echo()
            echo(content)

        # Show saved path if explicitly requested
        if save and 'file' in data:
            # Get absolute path
            filepath = Path(data.get('file', 'N/A')).resolve()
            echo(f"✓ Saved to: {filepath}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@cli.command(name='screenshot')
def page_screenshot():
    """Take a screenshot of current page.

    Example:
        dripage screenshot
    """
    result = get_screenshot(full_page=True, save=True)

    data = json.loads(result)
    if data.get('status') == 'success':
        echo(f"✓ Screenshot taken successfully")
        echo(f"  Saved to: {data.get('file', 'N/A')}")
        echo(f"  Full page: {data.get('full_page', True)}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@cli.command(name='vision')
@click.option('--query', required=True, help='Question about the page')
@click.option('--image', help='Path to image file. If not specified, takes screenshot')
@click.option('--save-file', is_flag=True, help='Save screenshot to file (default: in-memory analysis, faster)')
def page_vision(query: str, image: Optional[str] = None, save_file: bool = False):
    """Analyze page screenshot with vision model.

    Examples:
        dripage vision "What's the main heading?"

        dripage vision --image /path/to/screenshot.png "Describe this image"

        dripage vision --save-file "Save screenshot and analyze"
    """
    result = analyze_vision(query=query, image_path=image, save_file=save_file)

    data = json.loads(result)
    if data.get('status') == 'success':
        echo(f"✓ Vision analysis completed")
        if 'image_size' in data:
            size = data['image_size']
            echo(f"  Image size: {size.get('width', 'N/A')}x{size.get('height', 'N/A')}")
        if 'image_path' in data and data.get('image_path') != 'in-memory':
            echo(f"  Source image: {data.get('image_path', 'N/A')}")

        # Show analysis
        if 'analysis' in data:
            echo(f"  Analysis: {data.get('analysis', 'N/A')}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


# ==================== Location Commands ====================

@cli.command(name='locate')
@click.option('--query', required=True, help='Description of element to locate (e.g., "search input box", "submit button")')
@click.option('--image', help='Path to image file. If not specified, takes screenshot of current page')
@click.option('--click', is_flag=True, help='Click at the located element\'s center after locating')
def page_locate(query: str, image: Optional[str] = None, click: bool = False):
    """Locate element on page using vision analysis (uses latest tab).

    Examples:
        dripage locate --query "search button"

        dripage locate --query "submit button" --click

        dripage locate --query "login input" --image /path/to/screenshot.png
    """
    if click:
        result = locate_and_click(query=query, tab_id=None)
    else:
        result = locate_element(query=query, image_path=image, tab_id=None)

    data = json.loads(result)
    if data.get('status') == 'success':
        if click:
            located_box = data.get('located_box', [])
            click_point = data.get('click_point', {})
            echo(f"✓ Located and clicked element")
            echo(f"  Query: {query}")
            echo(f"  Box: {located_box}")
            echo(f"  Clicked at: ({click_point.get('x', 'N/A')}, {click_point.get('y', 'N/A')})")
        else:
            tool_calls = data.get('tool_calls', [])
            if tool_calls:
                first_tool = tool_calls[0]
                result_data = first_tool.get('result', {})
                converted_coords = result_data.get('converted_coordinates', {})
                # Get first converted box from the dict
                if converted_coords:
                    first_box_key = list(converted_coords.keys())[0]
                    box_data = converted_coords[first_box_key]
                    converted_box = box_data.get('converted_box', [])
                    original_box = box_data.get('original_box', [])
                    echo(f"✓ Element located")
                    echo(f"  Query: {query}")
                    echo(f"  Original box (GLM): {original_box}")
                    echo(f"  Converted box: {converted_box}")
                else:
                    echo(f"✓ Vision analysis completed")
                    echo(f"  Query: {query}")
                    vision_result = data.get('vision_result', '')
                    if isinstance(vision_result, str):
                        echo(f"  Analysis: {vision_result[:200]}...")
                    else:
                        echo(f"  Analysis: {str(vision_result)[:200]}...")
            else:
                echo(f"✓ Vision analysis completed")
                echo(f"  Query: {query}")
                vision_result = data.get('vision_result', '')
                if isinstance(vision_result, str):
                    echo(f"  Analysis: {vision_result[:200]}...")
                else:
                    echo(f"  Analysis: {str(vision_result)[:200]}...")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


# ==================== Action Commands ====================

@cli.group()
def action():
    """Element interaction commands (click, input, scroll)."""
    pass


@action.command(name='click')
@click.argument('x', type=int, required=True)
@click.argument('y', type=int, required=True)
@click.option('--clear', is_flag=True, default=True, help='Clear existing text before input (default: True)')
@click.option('--text', required=True, help='Text to input')
def action_click(x: int, y: int, clear: bool, text: str):
    """Click at coordinates on the page.

    Examples:
        dripage action click 100 200 --text "search"

        dripage action click 395 76 --clear --text "username"
    """
    from tools import browser_click

    result = browser_click.func(x=x, y=y, tab_id=None)

    data = json.loads(result)
    if data.get('status') == 'success':
        echo(f"✓ Clicked at coordinates ({x}, {y})")
        if 'tab' in data:
            tab_info = data['tab']
            echo(f"  Tab: {tab_info.get('title', 'N/A')}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@action.command(name='input')
@click.argument('x', type=int, required=True)
@click.argument('y', type=int, required=True)
@click.option('--clear', is_flag=True, default=True, help='Clear existing text before input (default: True)')
@click.option('--text', required=True, help='Text to input')
def action_input(x: int, y: int, clear: bool, text: str):
    """Input text at coordinates on the page.

    Examples:
        dripage action input 395 76 --clear --text "hello world"

        dripage action input 500 300 --no-clear --text "test"
    """
    from tools import browser_input

    result = browser_input.func(x=x, y=y, text=text, clear=clear, tab_id=None)

    data = json.loads(result)
    if data.get('status') == 'success':
        echo(f"✓ Input text: {text[:50]}...")
        if 'tab' in data:
            tab_info = data['tab']
            echo(f"  Tab: {tab_info.get('title', 'N/A')}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@action.command(name='scroll')
@click.option('--direction', type=click.Choice(['up', 'down']), default='down', help='Scroll direction')
@click.option('--amount', type=int, default=500, help='Scroll amount in pixels')
def action_scroll(direction: str, amount: int):
    """Scroll the page.

    Examples:
        dripage action scroll down 500

        dripage action scroll up 300
    """
    from tools import browser_scroll

    result = browser_scroll.func(direction=direction, amount=amount, tab_id=None)

    data = json.loads(result)
    if data.get('status') == 'success':
        echo(f"✓ Scrolled {direction} {amount}px")
        if 'tab' in data:
            tab_info = data['tab']
            echo(f"  Tab: {tab_info.get('title', 'N/A')}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


# ==================== Tab Commands ====================

@cli.group()
def tab():
    """Tab management commands."""
    pass


@tab.command(name='list')
def tab_list():
    """List all browser tabs.

    Example:
        dripage tab list
    """
    from tools import list_tabs

    result = list_tabs()
    data = json.loads(result)

    if 'tabs' in data:
        tabs = data['tabs']
        echo(f"✓ Found {len(tabs)} tabs")
        echo()
        for i, tab in enumerate(tabs, 1):
            tab_id = tab.get('tab_id', 'N/A')
            tab_title = tab.get('title', 'N/A')
            tab_url = tab.get('url', 'N/A')
            current = ' [current]' if tab.get('is_current', False) else ''

            echo(f"  [{i}] {style(current, fg='green')} {tab_id}: {tab_title}")
            if tab_url:
                echo(f"      URL: {tab_url[:60]}...")
    else:
        echo("ℹ️  No tabs found")


@tab.command(name='new')
@click.option('--url', help='URL to open in new tab')
def tab_new(url: Optional[str] = None):
    """Open a new tab.

    Example:
        dripage tab new --url https://example.com
    """
    from tools import new_tab

    result = new_tab(url=url)
    data = json.loads(result)

    if data.get('status') == 'success':
        tab = data.get('tab', {})
        echo(f"✓ New tab opened")
        echo(f"  Tab ID: {tab.get('tab_id', 'N/A')}")
        echo(f"  Title: {tab.get('title', 'N/A')}")
        if tab.get('url'):
            echo(f"  URL: {tab.get('url', 'N/A')}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@tab.command(name='close')
@click.argument('tab_id', required=False)
def tab_close(tab_id: Optional[str] = None):
    """Close a tab.

    Examples:
        dripage tab close

        dripage tab close 0
    """
    from tools import close_tab

    result = close_tab(tab_id=tab_id)
    data = json.loads(result)

    if data.get('status') == 'success':
        tab = data.get('tab', {})
        echo(f"✓ Tab closed")
        echo(f"  Tab ID: {tab.get('tab_id', 'N/A')}")
        echo(f"  Title: {tab.get('title', 'N/A')}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@tab.command(name='locate')
@click.argument('query', required=True)
@click.option('--tab-id', help='Tab ID or index to locate element in (default: latest tab)')
@click.option('--image', help='Path to image file. If not specified, takes screenshot of specified tab')
@click.option('--click', is_flag=True, help='Click at the located element\'s center after locating')
def tab_locate(query: str, tab_id: Optional[str] = None, image: Optional[str] = None, click: bool = False):
    """Locate element on specific tab using vision analysis.

    Examples:
        dripage tab locate "search button"

        dripage tab locate "submit button" --tab-id 0 --click

        dripage tab locate "login input" --tab-id "E3B0C442" --image /path/to/screenshot.png
    """
    # Convert tab_id to int or str as needed
    target_tab_id = None
    if tab_id:
        try:
            target_tab_id = int(tab_id)
        except ValueError:
            target_tab_id = tab_id

    if click:
        result = locate_and_click(query=query, tab_id=target_tab_id)
    else:
        result = locate_element(query=query, image_path=image, tab_id=target_tab_id)

    data = json.loads(result)
    if data.get('status') == 'success':
        if click:
            click_result = data.get('click_result', {})
            if click_result.get('status') == 'success':
                located_box = data.get('located_box', [])
                click_point = data.get('click_point', {})
                echo(f"✓ Located and clicked element")
                echo(f"  Query: {query}")
                echo(f"  Tab ID: {target_tab_id or 'latest'}")
                echo(f"  Box: {located_box}")
                echo(f"  Clicked at: ({click_point.get('x', 'N/A')}, {click_point.get('y', 'N/A')})")
            else:
                echo(style(f"✗ Click failed: {click_result.get('message', 'Unknown error')}", fg='red', bold=True))
        else:
            tool_calls = data.get('tool_calls', [])
            if tool_calls:
                first_tool = tool_calls[0]
                result_data = first_tool.get('result', {})
                converted_coords = result_data.get('converted_coordinates', {})
                # Get first converted box from the dict
                if converted_coords:
                    first_box_key = list(converted_coords.keys())[0]
                    box_data = converted_coords[first_box_key]
                    converted_box = box_data.get('converted_box', [])
                    original_box = box_data.get('original_box', [])
                    echo(f"✓ Element located")
                    echo(f"  Query: {query}")
                    echo(f"  Tab ID: {target_tab_id or 'latest'}")
                    echo(f"  Original box (GLM): {original_box}")
                    echo(f"  Converted box: {converted_box}")
                else:
                    echo(f"✓ Vision analysis completed")
                    echo(f"  Query: {query}")
                    echo(f"  Tab ID: {target_tab_id or 'latest'}")
                    vision_result = data.get('vision_result', '')
                    if isinstance(vision_result, str):
                        echo(f"  Analysis: {vision_result[:200]}...")
                    else:
                        echo(f"  Analysis: {str(vision_result)[:200]}...")
            else:
                echo(f"✓ Vision analysis completed")
                echo(f"  Query: {query}")
                echo(f"  Tab ID: {target_tab_id or 'latest'}")
                vision_result = data.get('vision_result', '')
                if isinstance(vision_result, str):
                    echo(f"  Analysis: {vision_result[:200]}...")
                else:
                    echo(f"  Analysis: {str(vision_result)[:200]}...")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


# ==================== Main Entry Point ====================

if __name__ == '__main__':
    cli()
