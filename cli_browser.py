"""
Browser management module for Dripage CLI.

Provides commands for starting, stopping, checking status of browsers,
and getting CDP WebSocket URLs. Reuses existing chrome_manager module.
"""
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from click import echo

import sys
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from utils.chrome_manager import ChromeManager
from utils.drission_page import create_browser
from cli_config import get_current_config, ConfigManager


# Global browser manager instance
_global_browser_manager: Optional[ChromeManager] = None
_global_page: Optional[Any] = None


def get_browser_manager() -> ChromeManager:
    """Get global browser manager instance."""
    global _global_browser_manager
    if _global_browser_manager is None:
        _global_browser_manager = ChromeManager()
    return _global_browser_manager


def get_page_object():
    """Get page object from current browser connection."""
    global _global_page

    config = get_current_config()
    address = config.browser.address

    # Reuse existing page if it's still valid
    if _global_page is not None:
        try:
            # Check if page is still alive
            if hasattr(_global_page, 'states') and _global_page.states.is_alive():
                return _global_page
        except:
            _global_page = None

    # Create new page connection
    _global_page = create_browser(address=address)
    return _global_page


def start_browser(name: Optional[str] = None, config_override: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Start a browser instance.

    Args:
        name: Browser name from config/browsers.yaml. If None, uses current config.
        config_override: Optional config overrides for testing.

    Returns:
        Dict with success status and browser info.
    """
    manager = get_browser_manager()

    # Determine browser config
    if name:
        # Load from browsers.yaml by name
        result = manager.start_browser(name=name)
    else:
        # Use current config or overrides
        if config_override:
            address = config_override.get('address', '127.0.0.1:19222')
            browser_path = config_override.get('browser_path', '')
            user_data_dir = config_override.get('user_data_dir', '')
        else:
            config = get_current_config()
            address = config.browser.address
            browser_path = config.browser.browser_path
            user_data_dir = config.browser.user_data_dir

        # Start browser with direct parameters
        result = manager.start_browser(
            name=None,
            address=address,
            user_data_dir=user_data_dir,
            browser_path=browser_path
        )

    # Clear page cache after starting new browser
    global _global_page
    _global_page = None

    return result


def stop_browser(name: Optional[str] = None) -> Dict[str, Any]:
    """
    Stop a browser instance.

    Args:
        name: Browser name to stop. If None, stops default browser.

    Returns:
        Dict with success status.
    """
    manager = get_browser_manager()
    result = manager.stop_browser(name=name)

    # Clear page cache after stopping
    global _global_page
    _global_page = None

    return result


def get_browser_status(name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get browser status information.

    Args:
        name: Browser name to check. If None, checks all browsers.

    Returns:
        Dict with browser status information.
    """
    manager = get_browser_manager()
    return manager.get_status(name)


def get_cdp_url(name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get CDP WebSocket URL for a browser.

    Args:
        name: Browser name to get CDP URL for. If None, gets default.

    Returns:
        Dict with CDP URL information.
    """
    manager = get_browser_manager()
    return manager.get_cdp_url(name)


def verify_cdp_connection() -> bool:
    """
    Verify CDP connection by checking http://<address>/json/version.

    Returns:
        True if connection is successful, False otherwise.
    """
    config = get_current_config()
    address = config.browser.address

    try:
        import requests
        response = requests.get(f"http://{address}/json/version", timeout=3)
        if response.status_code == 200:
            data = response.json()
            cdp_url = data.get('webSocketDebuggerUrl', '')
            if cdp_url:
                echo(f"✓ CDP connection verified: {cdp_url}")
                return True

        echo(f"✗ CDP connection failed: HTTP {response.status_code}")
        return False
    except requests.RequestException as e:
        echo(f"✗ CDP connection error: {e}")
        return False
    except ImportError:
        # Fallback: check using socket
        import socket
        host, port = address.split(':')
        port = int(port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            echo(f"✓ CDP port is open: {address}")
            return True
        else:
            echo(f"✗ CDP port is not open: {address}")
            return False


if __name__ == "__main__":
    # Test browser management
    import click

    @click.command()
    @click.option('--name', help='Browser name from config')
    def test_start(name):
        result = start_browser(name)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    @click.command()
    def test_stop():
        result = stop_browser()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    test_start()
