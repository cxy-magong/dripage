#!/usr/bin/env python
"""
Chrome Manager RPC Server Startup Script

Starts the ChromeManager RPC server for remote browser management.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.chrome_rpc.server import start_server


def main():
    parser = argparse.ArgumentParser(description="Chrome Manager RPC Server")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=9090, help="Server port (default: 9090)")

    args = parser.parse_args()

    start_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
