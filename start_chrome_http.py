#!/usr/bin/env python
"""
启动 HTTP API 服务器的简单脚本
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.chrome_http.server import start_server

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="启动 Chrome Manager HTTP API")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")

    args = parser.parse_args()
    start_server(host=args.host, port=args.port)
