#!/usr/bin/env python
"""
Debug script to investigate cleanup error.
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

print("🔌 Connecting to RPC server...")
client = ChromeManagerClient(host="localhost", port=9090)

print("\n📊 Getting status before cleanup...")
result = client.get_status()
print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n🛑 Stopping all browsers (cleanup)...")
try:
    result = client.stop_browser()
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    if isinstance(result, dict):
        print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n📊 Getting status after cleanup...")
result = client.get_status()
print(json.dumps(result, indent=2, ensure_ascii=False))

client.close()
print("\n✅ Done")
