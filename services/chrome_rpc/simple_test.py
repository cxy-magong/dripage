#!/usr/bin/env python
"""
Single-process test for Chrome Manager RPC Service

This test runs server and client in the same process using thread-based approach.
"""

import sys
import threading
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def run_server_in_thread():
    """Run RPC server in a separate thread."""
    from services.chrome_rpc.server import start_server
    import io
    import contextlib

    # Redirect stdout to avoid cluttering test output
    f = io.StringIO()

    with contextlib.redirect_stdout(f):
        with contextlib.redirect_stderr(f):
            # Run server in thread
            server_thread = threading.Thread(
                target=start_server,
                kwargs={"host": "localhost", "port": 9090},
                daemon=True
            )
            server_thread.start()

    # Wait for server to start
    time.sleep(3)

    return server_thread


def main():
    """Run tests."""
    print("\n" + "=" * 70)
    print("  Chrome Manager RPC Single-Process Test")
    print("=" * 70)

    print("\n🚀 Starting RPC server in thread...")
    server_thread = run_server_in_thread()
    print("✅ RPC server started on localhost:9090")

    try:
        # Run tests
        from services.chrome_rpc.test_rpc import test_chrome_manager_rpc

        print("\n🧪 Running tests...")
        test_passed = test_chrome_manager_rpc()

        if test_passed:
            print("\n✅ All tests PASSED")
            return 0
        else:
            print("\n❌ Tests FAILED")
            return 1

    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
