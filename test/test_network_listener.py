#!/usr/bin/env python
"""
Test script for network listener tools in MCP server.
"""
import asyncio
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from utils.drission_page import create_browser


async def test_network_listener():
    """Test network listener functionality."""
    print("=" * 60)
    print("Testing Network Listener Tools")
    print("=" * 60)

    # Create browser connection
    print("\n1. Connecting to browser...")
    browser = create_browser(address="127.0.0.1:19222")
    print(f"   Connected to browser: {browser}")

    # Get current tab
    print("\n2. Getting current tab...")
    tab = browser.latest_tab
    print(f"   Current tab: {tab.title} - {tab.url}")

    # Navigate to a test page
    print("\n3. Navigating to test page...")
    tab.get("https://httpbin.org/json")
    print(f"   Navigated to: {tab.url}")

    # Enable CDP Network
    print("\n4. Enabling CDP Network...")
    tab.run_cdp("Network.enable")
    print("   CDP Network enabled")

    # Set up response listener
    print("\n5. Setting up response listener...")
    captured_data = []

    def response_callback(**event):
        url = event.get("response", {}).get("url", "")
        mime_type = event.get("response", {}).get("mimeType", "")
        status = event.get("response", {}).get("status", "")

        captured_data.append({
            "url": url,
            "mimeType": mime_type,
            "status": status,
            "event": event
        })
        print(f"   Captured: {url} ({mime_type}) - Status: {status}")

    tab.driver.set_callback("Network.responseReceived", response_callback)
    print("   Response listener set up")

    # Refresh page to trigger network requests
    print("\n6. Refreshing page to trigger network requests...")
    tab.refresh()
    await asyncio.sleep(2)  # Wait for responses
    print(f"   Captured {len(captured_data)} responses")

    # Print captured data summary
    print("\n7. Captured responses summary:")
    for i, data in enumerate(captured_data[:10], 1):  # Show first 10
        print(f"   [{i}] {data['url']}")
        print(f"       Type: {data['mimeType']}, Status: {data['status']}")

    # Disable CDP Network
    print("\n8. Disabling CDP Network...")
    tab.run_cdp("Network.disable")
    print("   CDP Network disabled")

    # Test the actual network listener tools
    print("\n9. Testing network listener tools...")

    # Import the tools
    from tools.network_listener import (
        get_url_with_response_listener,
        get_response_listener_data,
        response_listener_stop,
    )

    # Start listener
    print("\n   Starting network listener...")
    result = get_url_with_response_listener(
        tab_id=None,
        mimeType="application/json",
        url_include="json",
        refresh=True
    )
    print(f"   Result: {result[:200]}...")

    # Wait for some network activity
    await asyncio.sleep(3)

    # Get captured data
    print("\n   Getting captured data...")
    data_result = get_response_listener_data()
    print(f"   Captured data: {data_result[:300]}...")

    # Stop listener
    print("\n   Stopping network listener...")
    stop_result = response_listener_stop(tab_id=None, clear_data=True)
    print(f"   Stop result: {stop_result}")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_network_listener())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
