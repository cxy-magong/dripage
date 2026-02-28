"""
Tab management module for Dripage CLI.

Provides commands for managing browser tabs (list, new, close, locate).
"""
import json
from typing import Optional

import click
from click import echo, style

from cli.location import (
    locate_element,
    locate_and_click
)


# ==================== Tab Commands ====================

@click.group()
def tab():
    """Tab management commands."""
    pass


@click.command(name='list')
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


@click.command(name='new')
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


@click.command(name='close')
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


@click.command(name='locate')
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


# Add commands to tab group
tab.add_command(tab_list)
tab.add_command(tab_new)
tab.add_command(tab_close)
tab.add_command(tab_locate)
