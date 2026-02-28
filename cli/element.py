"""
Element operations module for Dripage CLI.

Provides element operations like list, count, click, input, and get.
Uses DrissionPage native API to find and manipulate elements.
"""
import json
from pathlib import Path
from typing import Optional, Union, Dict, Any

from click import echo, style
from tools.tab_manager import get_tab_object


def _get_element_info(elem, index: int = 0) -> Dict[str, Any]:
    """
    Extract element information from DrissionPage element.

    Args:
        elem: DrissionPage element object
        index: Element index

    Returns:
        Element information dictionary
    """
    try:
        element_info = {
            "index": index,
            "tag": elem.tag.lower() if hasattr(elem, 'tag') else "",
            "id": elem.attr('id') if hasattr(elem, 'attr') else "",
            "class": elem.attr('class') if hasattr(elem, 'attr') else "",
            "text": elem.text if hasattr(elem, 'text') else ""
        }

        # Limit text length for display
        if len(element_info["text"]) > 50:
            element_info["text"] = element_info["text"][:50] + "..."

        # Get bounding box if available
        try:
            rect = elem.rect
            element_info["bbox"] = {
                "x": rect.location.x,
                "y": rect.location.y,
                "width": rect.size.width,
                "height": rect.size.height
            }
        except:
            element_info["bbox"] = None

        return element_info
    except Exception:
        return {
            "index": index,
            "tag": "",
            "id": "",
            "class": "",
            "text": "",
            "bbox": None
        }


def ele_list(selector: str = "*", attribute: Optional[str] = None, tab_id: Optional[Union[int, str]] = None) -> str:
    """
    List elements matching the criteria.

    Args:
        selector: CSS selector or XPath (default: "*" for all tags)
        attribute: Attribute filter (e.g., "id=value", "class=classname") - only used if selector is a tag name
        tab_id: Tab ID or index to operate on (default: current page)

    Returns:
        JSON string with list of matching elements
    """
    try:
        page, metadata = get_tab_object(tab_id)

        # Build selector using DrissionPage syntax
        # If attribute is provided and selector looks like a simple tag name, use DrissionPage attribute syntax
        if attribute and not selector.startswith('//') and not selector.startswith('/') and not selector.startswith('#') and not selector.startswith('.'):
            # Parse attribute filter
            parts = attribute.split('=', 1)
            attr_name = parts[0]
            attr_value = parts[1] if len(parts) > 1 else ""
            # DrissionPage supports attribute selector: tag@attr=value
            if selector != '*':
                final_selector = f'{selector}@{attr_name}={attr_value}'
            else:
                final_selector = f'@{attr_name}={attr_value}'
        else:
            final_selector = selector

        # Use DrissionPage's eles() to get all matching elements
        # DrissionPage supports both CSS selectors and XPath
        elements = page.eles(final_selector)

        if not elements:
            return json.dumps({
                "status": "success",
                "count": 0,
                "selector": final_selector,
                "elements": []
            }, ensure_ascii=False, indent=2)

        # Build element list
        element_list = []
        for i, elem in enumerate(elements):
            elem_info = _get_element_info(elem, index=i)
            element_list.append(elem_info)

        return json.dumps({
            "status": "success",
            "count": len(element_list),
            "selector": final_selector,
            "elements": element_list
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to list elements: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


def ele_count(selector: str = "*", attribute: Optional[str] = None, tab_id: Optional[Union[int, str]] = None) -> str:
    """
    Count elements matching the criteria.

    Args:
        selector: CSS selector or XPath (default: "*" for all tags)
        attribute: Attribute filter (e.g., "id=value", "class=classname") - only used if selector is a tag name
        tab_id: Tab ID or index to operate on (default: current page)

    Returns:
        JSON string with count of matching elements
    """
    try:
        page, metadata = get_tab_object(tab_id)

        # Build selector using DrissionPage syntax
        # If attribute is provided and selector looks like a simple tag name, use DrissionPage attribute syntax
        if attribute and not selector.startswith('//') and not selector.startswith('/') and not selector.startswith('#') and not selector.startswith('.'):
            # Parse attribute filter
            parts = attribute.split('=', 1)
            attr_name = parts[0]
            attr_value = parts[1] if len(parts) > 1 else ""
            if selector != '*':
                final_selector = f'{selector}@{attr_name}={attr_value}'
            else:
                final_selector = f'@{attr_name}={attr_value}'
        else:
            final_selector = selector

        # Use DrissionPage's eles() to get all matching elements
        # DrissionPage supports both CSS selectors and XPath
        elements = page.eles(final_selector)
        count = len(elements)

        return json.dumps({
            "status": "success",
            "count": count,
            "selector": final_selector
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to count elements: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


def ele_click(selector: str, index: int = 0, tab_id: Optional[Union[int, str]] = None) -> str:
    """
    Click an element by CSS selector or XPath.

    Args:
        selector: CSS selector or XPath
        index: Index of matching element (default: 0 for first match)
        tab_id: Tab ID or index to operate on (default: current page)

    Returns:
        JSON string with click result
    """
    try:
        page, metadata = get_tab_object(tab_id) 

        # Use DrissionPage's eles() to get all elements, then get by index
        elements = page.eles(selector)
        if index >= len(elements):
            return json.dumps({
                "status": "error",
                "message": f"Element not found: selector='{selector}', index={index} (only {len(elements)} elements found)"
            }, ensure_ascii=False, indent=2)
        
        elem = elements[index]

        if not elem:
            return json.dumps({
                "status": "error",
                "message": f"Element not found: selector='{selector}', index={index}"
            }, ensure_ascii=False, indent=2)

        # Click using DrissionPage methods
        # Use page.click.at() to click at element position
        page.click.at(elem)

        return json.dumps({
            "status": "success",
            "selector": selector,
            "index": index,
            "tab": metadata
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to click element: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


def ele_input(selector: str, text: str, index: int = 0, clear: bool = True, tab_id: Optional[Union[int, str]] = None) -> str:
    """
    Input text into an element by CSS selector or XPath.

    Args:
        selector: CSS selector or XPath
        text: Text to input
        index: Index of matching element (default: 0 for first match)
        clear: Clear existing text before input (default: True)
        tab_id: Tab ID or index to operate on (default: current page)

    Returns:
        JSON string with input result
    """
    try:
        page, metadata = get_tab_object(tab_id) 

        # Use DrissionPage's eles() to get all elements, then get by index
        elements = page.eles(selector)
        if index >= len(elements):
            return json.dumps({
                "status": "error",
                "message": f"Element not found: selector='{selector}', index={index} (only {len(elements)} elements found)"
            }, ensure_ascii=False, indent=2)
        
        elem = elements[index]

        if not elem:
            return json.dumps({
                "status": "error",
                "message": f"Element not found: selector='{selector}', index={index}"
            }, ensure_ascii=False, indent=2)

        # Input directly using DrissionPage's input() method
        if clear:
            elem.clear()
        elem.input(text)

        return json.dumps({
            "status": "success",
            "selector": selector,
            "index": index,
            "text": text,
            "tab": metadata
        }, ensure_ascii=False, indent=2)

        # Add element info to result
        if result.get("status") == "success":
            elem_info = _get_element_info(elem, index)
            result["element"] = elem_info

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to input text: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


def ele_get(selector: str, index: int = 0, properties: Optional[list] = None, tab_id: Optional[Union[int, str]] = None) -> str:
    """
    Get properties of an element by CSS selector or XPath.

    Args:
        selector: CSS selector or XPath
        index: Index of matching element (default: 0 for first match)
        properties: List of properties to get (default: ['tagName', 'id', 'className', 'textContent'])
        tab_id: Tab ID or index to operate on (default: current page)

    Returns:
        JSON string with element properties
    """
    try:
        page, metadata = get_tab_object(tab_id) 

        # Default properties to get
        if properties is None:
            properties = ['tagName', 'id', 'className', 'textContent']

        # Use DrissionPage's eles() to get all elements, then get by index
        elements = page.eles(selector)
        if index >= len(elements):
            return json.dumps({
                "status": "error",
                "message": f"Element not found: selector='{selector}', index={index} (only {len(elements)} elements found)"
            }, ensure_ascii=False, indent=2)
        
        elem = elements[index]

        if not elem:
            return json.dumps({
                "status": "error",
                "message": f"Element not found: selector='{selector}', index={index}"
            }, ensure_ascii=False, indent=2)

        # Extract properties
        element_data = {}

        for prop in properties:
            try:
                if prop == 'innerHTML':
                    element_data['innerHTML'] = elem.html() if hasattr(elem, 'html') else ""
                elif prop == 'outerHTML':
                    element_data['outerHTML'] = elem.html() if hasattr(elem, 'html') else ""
                elif prop == 'textContent':
                    element_data['textContent'] = elem.text if hasattr(elem, 'text') else ""
                elif prop == 'tagName':
                    element_data['tagName'] = elem.tag if hasattr(elem, 'tag') else ""
                elif prop == 'id':
                    element_data['id'] = elem.attr('id') if hasattr(elem, 'attr') else ""
                elif prop == 'className':
                    element_data['className'] = elem.attr('class') if hasattr(elem, 'attr') else ""
                elif prop == 'value':
                    element_data['value'] = elem.attr('value') if hasattr(elem, 'attr') else ""
                elif prop == 'href':
                    element_data['href'] = elem.attr('href') if hasattr(elem, 'attr') else ""
                elif prop == 'src':
                    element_data['src'] = elem.attr('src') if hasattr(elem, 'attr') else ""
                else:
                    # Try to get any attribute
                    element_data[prop] = elem.attr(prop) if hasattr(elem, 'attr') else ""
            except:
                element_data[prop] = ""

        # Limit content length
        if 'innerHTML' in element_data and element_data['innerHTML']:
            element_data['innerHTML'] = element_data['innerHTML'][:500]
        if 'outerHTML' in element_data and element_data['outerHTML']:
            element_data['outerHTML'] = element_data['outerHTML'][:500]
        if 'textContent' in element_data and element_data['textContent']:
            element_data['textContent'] = element_data['textContent'][:200]

        # Get bounding box
        try:
            rect = elem.rect
            element_data['bbox'] = {
                "x": rect.location.x,
                "y": rect.location.y,
                "width": rect.size.width,
                "height": rect.size.height
            }
        except:
            element_data['bbox'] = None

        return json.dumps({
            "status": "success",
            "selector": selector,
            "index": index,
            "element": element_data
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        error_msg = f"Failed to get element: {str(e)}"
        echo(f"✗ {error_msg}")
        return json.dumps({"status": "error", "message": error_msg}, ensure_ascii=False, indent=2)


# ==================== CLI Commands ====================

import click


@click.group()
def ele():
    """Element operations commands."""
    pass


@ele.command(name='list')
@click.option('--selector', default='*', help='CSS selector or XPath (default: *)')
@click.option('--attribute', help='Attribute filter (e.g., "id=value", "class=classname") - only used with simple tag selectors')
@click.option('--tab-id', help='Tab ID or index to operate on (default: current page)')
@click.option('--json', 'output_json', is_flag=True, help='Output raw JSON')
def cli_ele_list(selector: str, attribute: Optional[str], tab_id: Optional[str], output_json: bool):
    """List elements matching the criteria.

    Examples:
        dripage ele list --selector '//li'

        dripage ele list --selector '//div[contains(text(), "item")]'

        dripage ele list --selector '.list-item'

        dripage ele list --selector 'input' --attribute type=text

        dripage ele list --selector '//ul[@class="menu"]/li'
    """
    result = ele_list(selector=selector, attribute=attribute, tab_id=tab_id)

    if output_json:
        echo(result)
        return

    data = json.loads(result)

    if data.get('status') == 'success':
        count = data.get('count', 0)
        elements = data.get('elements', [])

        echo(f"✓ Found {count} element(s)")

        if elements:
            echo()
            for elem in elements:
                index = elem.get('index', 0)
                tag_name = elem.get('tag', '')
                elem_id = elem.get('id', '')
                elem_class = elem.get('class', '')
                text = elem.get('text', '')

                # Build display string
                parts = [f"[{index}] {tag_name}"]
                if elem_id:
                    parts.append(f"id={elem_id}")
                if elem_class:
                    parts.append(f"class={elem_class[:50]}")
                if text:
                    parts.append(f'"{text}"')

                echo('  '.join(parts))
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@ele.command(name='count')
@click.option('--selector', default='*', help='CSS selector or XPath (default: *)')
@click.option('--attribute', help='Attribute filter (e.g., "id=value", "class=classname") - only used with simple tag selectors')
@click.option('--tab-id', help='Tab ID or index to operate on (default: current page)')
@click.option('--json', 'output_json', is_flag=True, help='Output raw JSON')
def cli_ele_count(selector: str, attribute: Optional[str], tab_id: Optional[str], output_json: bool):
    """Count elements matching the criteria.

    Examples:
        dripage ele count --selector '//li'

        dripage ele count --selector '//div[contains(text(), "item")]'

        dripage ele count --selector '.list-item'

        dripage ele count --selector 'input' --attribute type=text

        dripage ele count --selector '//a[@href]'
    """
    result = ele_count(selector=selector, attribute=attribute, tab_id=tab_id)

    if output_json:
        echo(result)
        return

    data = json.loads(result)

    if data.get('status') == 'success':
        count = data.get('count', 0)
        selector = data.get('selector', '')
        echo(f"✓ Found {count} element(s) matching: {selector}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@ele.command(name='click')
@click.argument('selector')
@click.option('--index', default=0, help='Index of matching element (default: 0)')
@click.option('--tab-id', help='Tab ID or index to operate on (default: current page)')
@click.option('--json', 'output_json', is_flag=True, help='Output raw JSON')
def cli_ele_click(selector: str, index: int, tab_id: Optional[str], output_json: bool):
    """Click an element by CSS selector or XPath.

    Examples:
        dripage ele click '#submit-button'

        dripage ele click '//button[@type="submit"]'

        dripage ele click '.nav-item' --index 2
    """
    result = ele_click(selector=selector, index=index, tab_id=tab_id)

    if output_json:
        echo(result)
        return

    data = json.loads(result)

    if data.get('status') == 'success':
        message = data.get('message', '')
        echo(f"✓ {message}")

        if 'element' in data:
            elem = data['element']
            echo(f"  Tag: {elem.get('tag', '')}")
            if elem.get('id'):
                echo(f"  ID: {elem.get('id', '')}")
            if elem.get('text'):
                echo(f"  Text: {elem.get('text', '')}")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@ele.command(name='input')
@click.argument('selector')
@click.argument('text')
@click.option('--index', default=0, help='Index of matching element (default: 0)')
@click.option('--clear/--no-clear', default=True, help='Clear existing text before input (default: True)')
@click.option('--tab-id', help='Tab ID or index to operate on (default: current page)')
@click.option('--json', 'output_json', is_flag=True, help='Output raw JSON')
def cli_ele_input(selector: str, text: str, index: int, clear: bool, tab_id: Optional[str], output_json: bool):
    """Input text into an element by CSS selector or XPath.

    Examples:
        dripage ele input '#search-box' 'hello world'

        dripage ele input '//input[@name="q"]' 'test'

        dripage ele input '.username-input' 'admin' --clear
    """
    result = ele_input(selector=selector, text=text, index=index, clear=clear, tab_id=tab_id)

    if output_json:
        echo(result)
        return

    data = json.loads(result)

    if data.get('status') == 'success':
        message = data.get('message', '')
        echo(f"✓ {message}")

        if 'element' in data:
            elem = data['element']
            echo(f"  Tag: {elem.get('tag', '')}")
            if elem.get('id'):
                echo(f"  ID: {elem.get('id', '')}")
            echo(f"  Text input: '{text}'")
    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))


@ele.command(name='get')
@click.argument('selector')
@click.option('--index', default=0, help='Index of matching element (default: 0)')
@click.option('--properties', help='Comma-separated properties to get (default: tagName,id,className,textContent)')
@click.option('--tab-id', help='Tab ID or index to operate on (default: current page)')
@click.option('--json', 'output_json', is_flag=True, help='Output raw JSON')
def cli_ele_get(selector: str, index: int, properties: Optional[str], tab_id: Optional[str], output_json: bool):
    """Get properties of an element by CSS selector or XPath.

    Examples:
        dripage ele get '#submit-button'

        dripage ele get '//button[@type="submit"]'

        dripage ele get '.nav-item' --properties tagName,href,text
    """
    # Parse properties if provided
    prop_list = None
    if properties:
        prop_list = [p.strip() for p in properties.split(',')]

    result = ele_get(selector=selector, index=index, properties=prop_list, tab_id=tab_id)

    if output_json:
        echo(result)
        return

    data = json.loads(result)

    if data.get('status') == 'success':
        element = data.get('element', {})
        echo(f"✓ Element found: {selector} (index={index})")
        echo()

        # Display key properties
        if 'tagName' in element and element['tagName']:
            echo(f"  Tag: {element['tagName']}")

        if 'id' in element and element['id']:
            echo(f"  ID: {element['id']}")

        if 'className' in element and element['className']:
            echo(f"  Class: {element['className']}")

        if 'textContent' in element and element['textContent']:
            text = element['textContent']
            if len(text) > 100:
                text = text[:100] + "..."
            echo(f"  Text: {text}")

        if 'value' in element and element['value']:
            echo(f"  Value: {element['value']}")

        if 'href' in element and element['href']:
            echo(f"  Href: {element['href']}")

        if 'src' in element and element['src']:
            echo(f"  Src: {element['src']}")

        if 'bbox' in element and element['bbox']:
            bbox = element['bbox']
            echo(f"  Position: x={bbox['x']}, y={bbox['y']}")
            echo(f"  Size: width={bbox['width']}, height={bbox['height']}")

        # Display other properties
        for key, value in element.items():
            if key not in ['tagName', 'id', 'className', 'textContent', 'value', 'href', 'src', 'bbox', 'innerHTML', 'outerHTML']:
                if value:
                    echo(f"  {key}: {value}")

    else:
        echo(style(f"✗ {data.get('message', 'Unknown error')}", fg='red', bold=True))
