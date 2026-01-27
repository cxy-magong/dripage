# Chrome Manager RPC Service

Remote procedure call (RPC) service for ChromeManager using Pyro4.

## Features

- ✅ Remote browser management via RPC
- ✅ All ChromeManager methods exposed
- ✅ Multi-browser support (start, stop, status, CDP URL)
- ✅ Minimal code implementation
- ✅ Cross-platform compatible

## Project Structure

```
services/chrome_rpc/
├── __init__.py          # Package initialization
├── server.py            # RPC server implementation
├── client.py            # RPC client implementation
├── start_server.py      # Server startup script
├── test_rpc.py          # Test script
└── README.md            # This file
```

## Installation

Pyro4 is already added to project dependencies:
```bash
uv add pyro4
```

## Usage

### 1. Start RPC Server

**Terminal 1 - Start the server:**
```bash
cd "G:\code\agent-use\dripage\worktrees\cdp-support"
PYTHONPATH="G:\code\agent-use\dripage\worktrees\cdp-support" uv run services/chrome_rpc/start_server.py
```

**Custom host/port:**
```bash
uv run services/chrome_rpc/start_server.py --host 0.0.0.0 --port 9090
```

Server output:
```
ChromeManager RPC Server started!
RPC URI: PYRO:ChromeManager@0.0.0.0:9090
Listening on: 0.0.0.0:9090

Waiting for client connections...
Press Ctrl+C to stop the server.
```

### 2. Run Tests

**Terminal 2 - Run tests:**
```bash
cd "G:\code\agent-use\dripage\worktrees\cdp-support"
PYTHONPATH="G:\code\agent-use\dripage\worktrees\cdp-support" uv run services/chrome_rpc/test_rpc.py
```

Expected output:
```
============================================================
  Chrome Manager RPC Test Suite
============================================================

🔌 Connecting to RPC server...
✅ Connected to RPC server

------------------------------------------------------------
Test 1: Start browser1 by name
------------------------------------------------------------
✅ Test 1 PASSED: browser1 started successfully

...

============================================================
  🎉 ALL TESTS PASSED! 🎉
============================================================

✅ Summary:
   - Started two browsers by name: PASSED
   - Retrieved browser status: PASSED
   - Retrieved CDP URLs: PASSED
   - Closed browsers successfully: PASSED
   - Final status verification: PASSED
```

### 3. Use RPC Client in Your Code

```python
from services.chrome_rpc.client import ChromeManagerClient
import json

# Create client
client = ChromeManagerClient(host="localhost", port=9090)

# Start browser by name
result = client.start_browser(name="browser1")
print(json.dumps(result, indent=2))

# Get status
result = client.get_status()
print(json.dumps(result, indent=2))

# Get CDP URL
result = client.get_cdp_url(name="browser1")
cdp_url = result["data"]["cdp_url"]
print(f"CDP URL: {cdp_url}")

# Stop browser
result = client.stop_browser(name="browser1")
print(json.dumps(result, indent=2))

# Close connection
client.close()
```

### 4. Convenience Function

```python
from services.chrome_rpc.client import get_client

# Quick client creation
client = get_client(host="localhost", port=9090)

# Use ChromeManager methods
result = client.get_status()

# Don't forget to close
client.close()
```

## API Reference

### ChromeManagerClient

All methods mirror `utils.chrome_manager.ChromeManager`:

#### `start_browser(name=None, address="127.0.0.1:19222", user_data_dir="", browser_path="")`
Start a browser instance.

**Parameters:**
- `name` (str, optional): Browser name from `config/browsers.yaml`
- `address` (str): Browser CDP address
- `user_data_dir` (str): User data directory
- `browser_path` (str): Browser executable path

**Returns:** Dict with success status and data

#### `stop_browser(name=None)`
Stop a browser instance.

**Parameters:**
- `name` (str, optional): Browser name to stop

**Returns:** Dict with success status and data

#### `get_status(name=None)`
Get browser status.

**Parameters:**
- `name` (str, optional): Browser name (if None, returns all browsers)

**Returns:** Dict with browser status information

#### `get_cdp_url(name=None)`
Get CDP WebSocket URL for a browser.

**Parameters:**
- `name` (str, optional): Browser name

**Returns:** Dict with CDP URL

#### `load_browser_config(name)`
Load browser configuration by name.

**Parameters:**
- `name` (str): Browser name from `config/browsers.yaml`

**Returns:** Dictionary with browser configuration or None

#### `close()`
Close the RPC proxy connection.

## Server Configuration

### Default Settings
- **Host:** `0.0.0.0` (all interfaces)
- **Port:** `9090`
- **URI:** `PYRO:ChromeManager@0.0.0.0:9090`

### Custom Configuration

Edit `services/chrome_rpc/start_server.py` or use command-line arguments:
```bash
uv run services/chrome_rpc/start_server.py --host 0.0.0.0 --port 9090
```

## Success Criteria

✅ Enable remote procedure call service
✅ Client can call all ChromeManager methods
✅ Start two browsers by name successfully
✅ Close browsers successfully
✅ Check browser status successfully

## Troubleshooting

### Connection Refused
Ensure the RPC server is running:
```bash
# Check if port 9090 is in use
netstat -ano | findstr 9090  # Windows
lsof -i :9090               # Linux/Mac
```

### Pyro4 Errors
Make sure Pyro4 is installed:
```bash
uv pip show pyro4
```

### Browser Not Starting
Check browser configuration in `config/browsers.yaml`:
```bash
uv run python -m utils.chrome_manager status --name browser1
```

## Implementation Details

### Minimal Code Approach

This implementation follows the minimal code principle:

1. **Server (`server.py`):** Simple wrapper around ChromeManager with Pyro4 exposure
2. **Client (`client.py`):** Proxy that forwards all method calls to the RPC server
3. **No additional logic:** Direct method forwarding, no extra abstractions

### Why Pyro4?

- **Simple:** Easy to use, minimal configuration
- **Python-native:** Built for Python RPC
- **Lightweight:** Small footprint, fast startup
- **Cross-platform:** Works on Windows, Linux, and macOS

## License

MIT
