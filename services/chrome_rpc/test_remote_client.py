#!/usr/bin/env python
"""
远程客户端测试脚本 - 连接到本地 RPC Server

在远程服务器 sv-v2 上运行此脚本来测试 RPC 调用。
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.chrome_rpc.client import ChromeManagerClient


def test_remote_rpc(server_host, server_port=9090):
    """Test RPC connection to remote server."""
    print("\n" + "=" * 70)
    print(f"  Chrome Manager RPC - Remote Client Test")
    print(f"  Server: {server_host}:{server_port}")
    print("=" * 70)

    try:
        # Connect to RPC server
        print(f"\n🔌 Connecting to RPC server at {server_host}:{server_port}...")
        client = ChromeManagerClient(host=server_host, port=server_port)
        print("✅ Connected to RPC server")

        # Test 1: Get status
        print("\n" + "─" * 70)
        print("Test 1: Get all browsers status")
        print("─" * 70)
        result = client.get_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if result.get("success"):
            print("✅ Test 1 PASSED: Retrieved status successfully")
        else:
            print(f"❌ Test 1 FAILED: {result.get('message')}")
            return False

        # Test 2: Start browser1
        print("\n" + "─" * 70)
        print("Test 2: Start browser1 by name")
        print("─" * 70)
        result = client.start_browser(name="browser1")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if result.get("success"):
            print("✅ Test 2 PASSED: browser1 started successfully")
        else:
            print(f"❌ Test 2 FAILED: {result.get('message')}")
            return False

        import time
        time.sleep(2)  # Wait for browser to start

        # Test 3: Start browser2
        print("\n" + "─" * 70)
        print("Test 3: Start browser2 by name")
        print("─" * 70)
        result = client.start_browser(name="browser2")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if result.get("success"):
            print("✅ Test 3 PASSED: browser2 started successfully")
        else:
            print(f"❌ Test 3 FAILED: {result.get('message')}")
            return False

        time.sleep(2)

        # Test 4: Get CDP URLs
        print("\n" + "─" * 70)
        print("Test 4: Get CDP URLs")
        print("─" * 70)

        print("\nBrowser1 CDP URL:")
        result1 = client.get_cdp_url(name="browser1")
        print(json.dumps(result1, indent=2, ensure_ascii=False))

        print("\nBrowser2 CDP URL:")
        result2 = client.get_cdp_url(name="browser2")
        print(json.dumps(result2, indent=2, ensure_ascii=False))

        if result1.get("success") and result2.get("success"):
            print("✅ Test 4 PASSED: Retrieved both CDP URLs")
        else:
            print("❌ Test 4 FAILED")
            return False

        # Test 5: Stop browsers
        print("\n" + "─" * 70)
        print("Test 5: Stop browsers")
        print("─" * 70)

        print("\nStopping browser1:")
        result = client.stop_browser(name="browser1")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        print("\nStopping browser2:")
        result = client.stop_browser(name="browser2")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        time.sleep(1)

        # Test 6: Final status
        print("\n" + "─" * 70)
        print("Test 6: Final status check")
        print("─" * 70)
        result = client.get_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))

        if result.get("success") and result.get("data", {}).get("running") == 0:
            print("✅ Test 6 PASSED: All browsers stopped")
        else:
            print("❌ Test 6 FAILED")
            return False

        # All tests passed
        print("\n" + "=" * 70)
        print("  🎉 ALL REMOTE RPC TESTS PASSED! 🎉")
        print("=" * 70)
        print(f"\n✅ Successfully connected to remote server: {server_host}:{server_port}")
        print("✅ Started and managed browsers remotely via RPC")
        print("✅ Retrieved CDP URLs from remote browser instances")
        print()

        return True

    except Exception as e:
        print(f"\n❌ Remote RPC test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        try:
            client.close()
            print("✅ Client connection closed")
        except Exception as e:
            print(f"Error closing client: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Chrome Manager RPC Remote Connection")
    parser.add_argument("--host", required=True, help="RPC server host IP address")
    parser.add_argument("--port", type=int, default=9090, help="RPC server port (default: 9090)")

    args = parser.parse_args()

    success = test_remote_rpc(args.host, args.port)
    sys.exit(0 if success else 1)
