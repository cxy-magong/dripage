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

# Add project root to sys.path FIRST
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import click
from dotenv import load_dotenv
load_dotenv()

from click import echo, style, secho
from config.settings import (
    ConfigManager,
    get_current_config,
    get_default_config,
    DEFAULT_CONFIG_FILE,
    SESSION_CONFIG_FILE
)
from cli.browser import (
    start_browser,
    stop_browser,
    get_browser_status,
    get_cdp_url,
    verify_cdp_connection,
    get_page_object,
    activate_browser
)
from cli.capture import (
    NetworkCapture,
    PacketFilter,
    start_global_capture,
    stop_global_capture,
    get_global_capture
)
from cli.page import (
    get_markdown,
    get_screenshot,
    get_html,
    analyze_vision
)
from cli.location import (
    locate_element,
    locate_and_click
)
from cli.tab import tab as tab_group


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
# TODO: Config commands temporarily disabled - may be removed in future

# @cli.group()
# def config():
#     """Configuration management commands."""
#     pass


# @config.command(name='set')
# @click.argument('name', required=False)
# @click.option('--set-default', is_flag=True, help='Set as default configuration')
# def config_set_session(name: Optional[str] = None, set_default: bool = False):
#     """Set or create a session configuration.
# 
#     Examples:
#         dripage config set my-session --set-default
# 
#         dripage config set dev
#     """
#     manager = ConfigManager()
# 
#     if name:
#         if set_default:
#             # Save current config as default
#             current_config = manager.load_config()
#             manager.save_config(current_config)
#             echo(f"✓ Set current configuration as default")
#             echo(f"  Browser: {current_config.browser.name} @ {current_config.browser.address}")
#         else:
#             # Create new session
#             from config.settings import get_current_config
#             session_config = get_current_config()
#             manager.save_session(name, session_config)
#             manager.set_current_session(name)
#             echo(f"✓ Created session '{name}'")
#             echo(f"  Browser: {session_config.browser.name} @ {session_config.browser.address}")
#     else:
#         # Show current config
#         current_config = manager.load_config()
#         echo("Current Configuration:")
#         echo(f"  Browser: {style(fg='cyan')}{current_config.browser.name} @ {current_config.browser.address}")
#         echo(f"  Vision: {style(fg='cyan')}{current_config.vision.model}")
#         echo(f"  Capture: {style(fg='green' if current_config.capture.enabled else 'red')}{current_config.capture.enabled}")
#         echo()
#         echo(f"Config file: {DEFAULT_CONFIG_FILE}")
#         echo(f"Session file: {SESSION_CONFIG_FILE}")


# @config.command(name='list')
# def list_sessions():
#     """List all available sessions."""
#     manager = ConfigManager()
#     sessions = manager.list_sessions()
# 
#     if not sessions:
#         echo("ℹ️  No sessions found")
#         return
# 
#     echo("Available Sessions:")
#     echo()
#     for session in sessions:
#         session_id = session.get('session_id', 'default')
#         browser = session.get('browser', {})
#         echo(f"  {style(fg='cyan')}{session_id}:")
#         echo(f"    Browser: {browser.get('name', 'default')} @ {browser.get('address', 'N/A')}")


# @config.command(name='use')
# @click.argument('name')
# def use_session(name: str):
#     """Switch to a session configuration.
# 
#     Example:
#         dripage config use dev
#     """
#     manager = ConfigManager()
#     sessions = manager.list_sessions()
#     session_ids = [s.get('session_id') for s in sessions]
# 
#     if name not in session_ids:
#         echo(f"✗ Session '{name}' not found")
#         echo(f"  Available sessions: {', '.join(session_ids)}")
#         sys.exit(1)
# 
#     # Switch to session
#     manager.set_current_session(name)
#     echo(f"✓ Switched to session '{name}'")
# 
#     # Print current config
#     current_config = manager.load_session(name)
#     if current_config:
#         echo(f"  Browser: {current_config.browser.name} @ {current_config.browser.address}")
#         echo(f"  Vision: {current_config.vision.model}")
#         echo(f"  Capture: {current_config.capture.enabled}")


# @config.command(name='reset')
# def reset():
#     """Reset to default configuration."""
#     ConfigManager().save_config(get_default_config())
#     echo("✓ Reset to default configuration")


# @config.command(name='show')
# def config_show():
#     """Show current configuration with source information.
# 
#     Example:
#         dripage config show
#     """
#     from config.settings import get_current_config, get_config_source
# 
#     config = get_current_config()
#     source_info = get_config_source()
# 
#     echo("Current Configuration:")
#     echo()
#     echo(f"  Source: {style(source_info['source'], fg='cyan')}")
#     echo(f"    Detail: {source_info['detail']}")
#     echo()
#     echo(f"  Browser: {style(config.browser.name, fg='cyan')} @ {config.browser.address}")
#     echo(f"    App ID: {source_info['app_id']}")
#     echo()
#     echo(f"  Working Directory:")
#     echo(f"    {source_info['cwd']}")


# @config.command(name='set-user')
# @click.option('--app', help='App ID (e.g., crawler_prod)')
# @click.option('--browser', help='Browser name (e.g., browser1)')
# def config_set_user(app: Optional[str], browser: Optional[str]):
#     """Set user-level app configuration.
# 
#     This configuration is stored in ~/.dripage/current_app and will be used
#     when no project config or environment variable is set.
# 
#     Examples:
#         dripage config set-user --app crawler_prod --browser browser1
# 
#         dripage config set-user --browser browser2
#     """
#     if not browser:
#         echo(style("✗ --browser is required", fg='red'))
#         sys.exit(1)
# 
#     import yaml
# 
#     home = Path.home()
#     config_path = home / '.dripage'
#     current_app_path = config_path / 'current_app'
# 
#     config_path.mkdir(parents=True, exist_ok=True)
# 
#     data = {
#         'app_id': app or browser,
#         'browser': browser,
#         'timestamp': datetime.now().isoformat()
#     }
# 
#     with open(current_app_path, 'w', encoding='utf-8') as f:
#         yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
# 
#     echo(f"✓ User app configuration saved")
#     echo(f"  App ID: {data['app_id']}")
#     echo(f"  Browser: {data['browser']}")
#     echo(f"  Config file: {current_app_path}")
#     echo()
#     echo("ℹ️  This configuration will be used when:")
#     echo("    - No .dripage/config in current directory")
#     echo("    - No DRIPAGE_BROWSER environment variable set")


# @config.command(name='clear-user')
# def config_clear_user():
#     """Clear user-level app configuration.
# 
#     Example:
#         dripage config clear-user
#     """
#     home = Path.home()
#     current_app_path = home / '.dripage' / 'current_app'
# 
#     if current_app_path.exists():
#         current_app_path.unlink()
#         echo("✓ User app configuration cleared")
#         echo(f"  Removed: {current_app_path}")
#     else:
#         echo("ℹ️  No user app configuration found")


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
    # If name not specified, use current config
    if name is None:
        from config.settings import get_current_config
        config = get_current_config()
        name = config.browser.name

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
    # If name not specified, use current config
    if name is None:
        from config.settings import get_current_config
        config = get_current_config()
        name = config.browser.name

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
    from config.settings import get_current_config

    result = get_browser_status(name=name)

    if result['success']:
        data = result['data']
        echo(f"✓ Browser status retrieved")

        # Get current browser from config
        current_config = get_current_config()
        current_browser = current_config.browser.name

        # Handle single browser or all browsers
        if 'browsers' in data:
            # Multiple browsers
            browsers = data['browsers']
            echo(f"  Total browsers: {data.get('total', 0)}")
            echo(f"  Running: {data.get('running', 0)}")
            echo()
            echo(f"  Current browser: {style(current_browser, fg='yellow', bold=True)}")
            echo()

            for browser_name, browser_info in browsers.items():
                status_icon = style('●', fg='green', bold=True) if browser_info.get('status') == 'running' else '○'
                status_text = style('running', fg='green') if browser_info.get('status') == 'running' else 'stopped'

                # Mark current browser with ★
                browser_label = browser_name
                if browser_name == current_browser:
                    browser_label = f"{style('★', fg='yellow', bold=True)} {style(browser_name, fg='yellow', bold=True)} {style('[CURRENT]', fg='yellow')}"

                echo(f"  {status_icon} {browser_label}: {status_text}")
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


@browser.command(name='activate')
@click.option('--name', help='Browser name to activate. If not specified, activates current browser')
def browser_activate(name: Optional[str] = None):
    """Activate browser window (bring to foreground).

    This command brings the browser window to the foreground on Windows.
    Useful for identifying which window corresponds to which browser instance.

    Examples:
        dripage browser activate              # Activate current browser

        dripage browser activate --name browser1

        dripage browser activate --name worker_9321
    """
    result = activate_browser(name=name)

    if result['success']:
        echo()
        echo(f"✓ Browser window activated successfully")
        if result.get('window_title'):
            echo(f"  Window: {result['window_title']}")
        echo(f"  PID: {result['pid']}")
    else:
        echo(style(f"✗ {result.get('error', 'Failed to activate window')}", fg='red', bold=True))
        sys.exit(1)


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
    from .capture import NetworkCapture

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
@click.option('--format', type=click.Choice(['markdown', 'html', 'screenshot']), default='markdown', help='Output format')
@click.option('--tab-id', help='Tab ID or index to operate on (default: current page)')
def page_get(url: Optional[str] = None, save: bool = False, format: str = 'markdown', tab_id: Optional[str] = None):
    """Get page content in various formats.

    Supports markdown, html, and screenshot formats.

    Examples:
        dripage get http://localhost:3000/sign-up

        dripage get --format screenshot

        dripage get --format html --save

        dripage get --tab-id 0
    """
    if format == 'screenshot':
        result = get_screenshot(full_page=True, save=True)
        data = json.loads(result)
        if data.get('status') == 'success':
            filepath = Path(data.get('file', 'N/A')).resolve()
            echo(f"✓ Screenshot saved to: {filepath}")
        else:
            echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))
        return

    elif format == 'html':
        result = get_html(url=url, save=save, tab_id=tab_id)
    else:
        result = get_markdown(url=url, save=save, tab_id=tab_id)

    data = json.loads(result)
    if data.get('status') == 'success':
        echo(f"✓ Page retrieved successfully")
        echo(f"  URL: {data.get('url', 'N/A')}")
        echo(f"  Title: {data.get('title', 'N/A')}")
        echo(f"  Format: {format}")

        content = data.get('content', '')

        if format == 'screenshot':
            filepath = Path(data.get('file', 'N/A')).resolve()
            echo(f"✓ Saved to: {filepath}")
            return

        if len(content) > 3000:
            echo()
            echo(content[:3000])
            echo()
            echo(f"⚠️  Content truncated ({len(content)} chars > 3000 limit)")

            if 'file' not in data:
                if format == 'markdown':
                    save_result = get_markdown(url=None if url else None, save=True, tab_id=tab_id)
                else:
                    save_result = get_html(url=None if url else None, save=True, tab_id=tab_id)
                save_data = json.loads(save_result)
                if save_data.get('status') == 'success' and 'file' in save_data:
                    filepath = Path(save_data.get('file', 'N/A')).resolve()
                    echo(f"   Full content saved to: {filepath}")
                else:
                    echo(f"   Failed to save content automatically")
            else:
                filepath = Path(data.get('file', 'N/A')).resolve()
                echo(f"   Full content saved to: {filepath}")
        else:
            echo()
            echo(content)

        if save and 'file' in data:
            filepath = Path(data.get('file', 'N/A')).resolve()
            echo(f"✓ Saved to: {filepath}")
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

                    # Display element info if available
                    element_info = data.get('element_info')
                    if element_info:
                        echo()
                        echo(f"  Element information:")
                        echo(f"    Tag: {element_info.get('tagName', 'N/A')}")
                        if element_info.get('id'):
                            echo(f"    ID: {element_info.get('id')}")
                        if element_info.get('className'):
                            echo(f"    Class: {element_info.get('className')}")
                        if element_info.get('name'):
                            echo(f"    Name: {element_info.get('name')}")
                        if element_info.get('type'):
                            echo(f"    Type: {element_info.get('type')}")
                        if element_info.get('placeholder'):
                            echo(f"    Placeholder: {element_info.get('placeholder')}")
                        if element_info.get('xpath'):
                            echo(f"    XPath: {element_info.get('xpath')}")

                        # Display text content (use truncated version if available)
                        if element_info.get('textContent_display'):
                            text_display = element_info.get('textContent_display', '')
                            echo(f"    Text: {text_display}...")
                            if element_info.get('textContent_truncated'):
                                text_file = element_info.get('textContent_file')
                                echo(f"          ⚠️  Full text saved to: {text_file}")
                        elif element_info.get('textContent'):
                            text = element_info.get('textContent', '')[:50]
                            echo(f"    Text: {text}...")

                        # Display HTML (use truncated version if available)
                        if element_info.get('outerHTML_display'):
                            html_display = element_info.get('outerHTML_display', '')
                            echo(f"    HTML: {html_display}...")
                            if element_info.get('outerHTML_truncated'):
                                html_file = element_info.get('outerHTML_file')
                                echo(f"          ⚠️  Full HTML saved to: {html_file}")
                        elif element_info.get('outerHTML'):
                            html = element_info.get('outerHTML', '')[:200]
                            echo(f"    HTML: {html}...")

                        if element_info.get('attributes'):
                            echo(f"    Attributes: {len(element_info.get('attributes'))} found")
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
def action_click(x: int, y: int):
    """Click at coordinates on the page.

    Examples:
        dripage action click 100 200

        dripage action click 395 76
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
        dripage action scroll --direction down --amount 500

        dripage action scroll --direction up --amount 300
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
cli.add_command(tab_group)


# ==================== Main Entry Point ====================

if __name__ == '__main__':
    cli()
