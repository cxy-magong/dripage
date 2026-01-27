#!/usr/bin/env python
"""
Integration test for Chrome Manager RPC Service

This script:
1. Starts RPC server in subprocess
2. Runs all tests
3. Stops server
4. Reports results
"""

import subprocess
import sys
import time
import json
import signal
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def start_rpc_server():
    """Start RPC server in subprocess."""
    print("\n🚀 Starting RPC server in subprocess...")

    # Start server subprocess
    process = subprocess.Popen(
        [
            sys.executable, "services/chrome_rpc/start_server.py"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=str(project_root),
        env={"PYTHONPATH": str(project_root)}
    )

    # Wait for server to start
    time.sleep(3)

    # Check if process is still running
    if process.poll() is not None:
        print("❌ Server failed to start")
        print("Output:", process.stdout.read())
        return None

    print("✅ RPC server started successfully")
    return process


def run_tests():
    """Run integration tests."""
    print("\n🧪 Running integration tests...")

    # Import test module
    from services.chrome_rpc.test_rpc import test_chrome_manager_rpc

    # Run tests
    return test_chrome_manager_rpc()


def main():
    """Main test runner."""
    print("\n" + "=" * 70)
    print("  Chrome Manager RPC Integration Test")
    print("=" * 70)

    server_process = None
    test_passed = False

    try:
        # Start server
        server_process = start_rpc_server()
        if not server_process:
            print("\n❌ Integration test FAILED: Could not start RPC server")
            return 1

        # Wait a bit more for server to be ready
        time.sleep(2)

        # Run tests
        test_passed = run_tests()

        # Report results
        if test_passed:
            print("\n✅ Integration test PASSED")
            return 0
        else:
            print("\n❌ Integration test FAILED")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        return 1

    except Exception as e:
        print(f"\n❌ Integration test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Stop server
        if server_process:
            print("\n🛑 Stopping RPC server...")
            try:
                server_process.terminate()
                server_process.wait(timeout=5)
                print("✅ RPC server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Server did not stop gracefully, forcing...")
                server_process.kill()
                print("✅ RPC server killed")
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")


if __name__ == "__main__":
    sys.exit(main())
