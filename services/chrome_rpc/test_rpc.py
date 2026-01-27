#!/usr/bin/env python
"""
Chrome Manager RPC Test Script

Tests all ChromeManager RPC functionality:
1. Start two browsers by name
2. Check browser status
3. Close browsers
4. Verify final status
"""

import json
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.chrome_rpc.client import ChromeManagerClient


def print_result(title, result):
    """Print result in formatted JSON."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def test_chrome_manager_rpc():
    """Test ChromeManager RPC functionality."""
    print("\n" + "=" * 60)
    print("  Chrome Manager RPC Test Suite")
    print("=" * 60)

    # Initialize client
    print("\n🔌 Connecting to RPC server...")
    client = ChromeManagerClient(host="localhost", port=9090)
    print("✅ Connected to RPC server")

    try:
        # Test 1: Start browser1
        print("\n" + "─" * 60)
        print("Test 1: Start browser1 by name")
        print("─" * 60)
        result = client.start_browser(name="browser1")
        print_result("Start browser1 result", result)

        if result.get("success"):
            print("✅ Test 1 PASSED: browser1 started successfully")
        else:
            print(f"❌ Test 1 FAILED: {result.get('message')}")
            return False

        time.sleep(2)  # Wait for browser to fully start

        # Test 2: Start browser2
        print("\n" + "─" * 60)
        print("Test 2: Start browser2 by name")
        print("─" * 60)
        result = client.start_browser(name="browser2")
        print_result("Start browser2 result", result)

        if result.get("success"):
            print("✅ Test 2 PASSED: browser2 started successfully")
        else:
            print(f"❌ Test 2 FAILED: {result.get('message')}")
            return False

        time.sleep(2)  # Wait for browser to fully start

        # Test 3: Get status of all browsers
        print("\n" + "─" * 60)
        print("Test 3: Get status of all browsers")
        print("─" * 60)
        result = client.get_status()
        print_result("All browsers status", result)

        if result.get("success") and result.get("data", {}).get("running") == 2:
            print("✅ Test 3 PASSED: Both browsers are running")
        else:
            print(f"❌ Test 3 FAILED: Expected 2 running browsers")
            return False

        # Test 4: Get status of browser1
        print("\n" + "─" * 60)
        print("Test 4: Get status of browser1")
        print("─" * 60)
        result = client.get_status(name="browser1")
        print_result("Browser1 status", result)

        if result.get("success") and result.get("data", {}).get("status") == "running":
            print("✅ Test 4 PASSED: browser1 is running")
        else:
            print(f"❌ Test 4 FAILED")
            return False

        # Test 5: Get CDP URL of browser1
        print("\n" + "─" * 60)
        print("Test 5: Get CDP URL of browser1")
        print("─" * 60)
        result = client.get_cdp_url(name="browser1")
        print_result("Browser1 CDP URL", result)

        if result.get("success") and result.get("data", {}).get("cdp_url"):
            print(f"✅ Test 5 PASSED: CDP URL retrieved - {result['data']['cdp_url']}")
        else:
            print(f"❌ Test 5 FAILED")
            return False

        # Test 6: Get CDP URL of browser2
        print("\n" + "─" * 60)
        print("Test 6: Get CDP URL of browser2")
        print("─" * 60)
        result = client.get_cdp_url(name="browser2")
        print_result("Browser2 CDP URL", result)

        if result.get("success") and result.get("data", {}).get("cdp_url"):
            print(f"✅ Test 6 PASSED: CDP URL retrieved - {result['data']['cdp_url']}")
        else:
            print(f"❌ Test 6 FAILED")
            return False

        # Test 7: Stop browser1
        print("\n" + "─" * 60)
        print("Test 7: Stop browser1")
        print("─" * 60)
        result = client.stop_browser(name="browser1")
        print_result("Stop browser1 result", result)

        if result.get("success"):
            print("✅ Test 7 PASSED: browser1 stopped successfully")
        else:
            print(f"❌ Test 7 FAILED: {result.get('message')}")
            return False

        time.sleep(1)  # Wait for browser to stop

        # Test 8: Stop browser2
        print("\n" + "─" * 60)
        print("Test 8: Stop browser2")
        print("─" * 60)
        result = client.stop_browser(name="browser2")
        print_result("Stop browser2 result", result)

        if result.get("success"):
            print("✅ Test 8 PASSED: browser2 stopped successfully")
        else:
            print(f"❌ Test 8 FAILED: {result.get('message')}")
            return False

        time.sleep(1)  # Wait for browser to stop

        # Test 9: Final status check
        print("\n" + "─" * 60)
        print("Test 9: Final status check")
        print("─" * 60)
        result = client.get_status()
        print_result("Final browsers status", result)

        if result.get("success") and result.get("data", {}).get("running") == 0:
            print("✅ Test 9 PASSED: Both browsers stopped")
        else:
            print(f"❌ Test 9 FAILED: Expected 0 running browsers")
            return False

        # All tests passed
        print("\n" + "=" * 60)
        print("  🎉 ALL TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n✅ Summary:")
        print("   - Started two browsers by name: PASSED")
        print("   - Retrieved browser status: PASSED")
        print("   - Retrieved CDP URLs: PASSED")
        print("   - Closed browsers successfully: PASSED")
        print("   - Final status verification: PASSED")
        print()

        return True

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup: Check if any browsers are still running, then stop them
        print("\n" + "─" * 60)
        print("Cleanup: Checking for remaining browsers...")
        print("─" * 60)
        try:
            result = client.get_status()
            if result.get("success") and result.get("data", {}).get("running", 0) > 0:
                print(f"Found {result['data']['running']} running browser(s), stopping...")
                result = client.stop_browser()
                print(f"Cleanup result: {result}")
            else:
                print("No running browsers to stop.")
        except Exception as e:
            print(f"Cleanup error: {e}")

        try:
            client.close()
            print("\n✅ Client connection closed")
        except Exception as e:
            print(f"Error closing client: {e}")


if __name__ == "__main__":
    success = test_chrome_manager_rpc()
    sys.exit(0 if success else 1)
