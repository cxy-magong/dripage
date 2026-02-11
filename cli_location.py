"""
Location module for Dripage CLI.

Provides visual element location capabilities using vision analysis
and coordinate conversion. Reuses tools from tools/agent_tools.py.
"""
import json
import sys
from pathlib import Path
from typing import Optional, Union

import sys
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from click import echo
from cli_config import get_current_config


def locate_element(
    query: str,
    image_path: Optional[str] = None,
    tab_id: Optional[Union[int, str]] = None
) -> str:
    """
    Locate element on page using vision analysis and coordinate conversion.

    This function wraps locate_element tool from tools.agent_tools
    to provide CLI-friendly interface.

    Args:
        query: Description of element to locate (e.g., "search input box", "submit button")
        image_path: Path to image file (optional, uses current screenshot if not provided)
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        JSON string with element location, converted coordinates, and analysis details.
    """
    try:
        from tools.agent_tools import locate_element
        from langgraph.types import Command

        # Call locate_element (it returns a Command object)
        result = locate_element.invoke({
            "query": query,
            "image_path": image_path,
            "tab_id": tab_id
        })

        # Extract the update dict from Command object
        if isinstance(result, Command):
            locate_result = result.update.get("locate_element_result", {})
        else:
            locate_result = result

        # Format result for CLI
        result_dict = {
            "status": "success",
            "query": query,
            "image_path": "in-memory" if not image_path else image_path,
            "tab_id": tab_id,
            **locate_result
        }

        return json.dumps(result_dict, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to locate element: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


def locate_and_click(query: str, tab_id: Optional[Union[int, str]] = None) -> str:
    """
    Locate element and click at its center coordinates.

    This is a convenience function that combines locate_element and browser_click.

    Args:
        query: Description of element to locate (e.g., "submit button")
        tab_id: Tab identifier (None=current tab, int=index, str=tab_id)

    Returns:
        JSON string with location result and click status.
    """
    try:
        from tools import browser_click

        # Step 1: Locate element
        locate_result = json.loads(locate_element(query=query, tab_id=tab_id))

        if locate_result.get("status") != "success":
            return json.dumps({
                "status": "error",
                "message": f"Failed to locate element: {locate_result.get('message')}"
            }, ensure_ascii=False, indent=2)

        # Step 2: Extract coordinates from tool_calls
        tool_calls = locate_result.get("tool_calls", [])
        if not tool_calls:
            return json.dumps({
                "status": "error",
                "message": "No coordinates found in locate result"
            }, ensure_ascii=False, indent=2)

        # Get the converted coordinates from the first tool call
        first_tool = tool_calls[0]
        result_data = first_tool.get("result", {})
        converted_coords = result_data.get("converted_coordinates", {})

        if not converted_coords:
            return json.dumps({
                "status": "error",
                "message": "No converted coordinates found"
            }, ensure_ascii=False, indent=2)

        # Get first converted box from the dict
        first_box_key = list(converted_coords.keys())[0]
        box_data = converted_coords[first_box_key]
        converted_box = box_data.get("converted_box")
        original_box = box_data.get("original_box")

        if not converted_box or len(converted_box) != 4:
            return json.dumps({
                "status": "error",
                "message": f"Invalid converted box: {converted_box}"
            }, ensure_ascii=False, indent=2)

        # Step 3: Calculate center point
        x1, y1, x2, y2 = converted_box
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        echo(f"  Located box: [{x1}, {y1}, {x2}, {y2}]")
        echo(f"  Click point: ({center_x}, {center_y})")

        # Step 4: Click at center point
        click_result = json.loads(browser_click.func(x=center_x, y=center_y, tab_id=tab_id))

        # Step 5: Return combined result
        return json.dumps({
            "status": "success" if click_result.get("status") == "success" else "error",
            "query": query,
            "located_box": [x1, y1, x2, y2],
            "click_point": {"x": center_x, "y": center_y},
            "click_result": click_result
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to locate and click: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--query', default='search button', help='Test query for locate')
    def test_locate(query):
        result = locate_element(query)
        print(result)

    @click.command()
    @click.option('--query', default='search button', help='Test query for locate and click')
    def test_locate_and_click(query):
        result = locate_and_click(query)
        print(result)

    test_locate()
