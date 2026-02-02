# Dripage 🚀

Browser automation and vision analysis via MCP (Model Context Protocol).

## Features

- 🌐 **Browser Automation**: Navigate, interact with web pages
- 📄 **Content Extraction**: Save pages as Markdown, HTML, images, or MHTML
- 👁️ **Vision Analysis**: Analyze screenshots using GLM-4V vision model
- 🔍 **Element Location**: Find and locate elements using vision + coordinates
- 📡 **Network Packet Capture**: Background packet monitoring with filtering capabilities

## Quick Start

### 1. Start MCP Server

**HTTP Mode (for testing):**
```bash
PYTHONPATH="G:\code\agent-use\dripage" uv run mcp_server.py http
```

**STDIO Mode (for production):**
```bash
PYTHONPATH="G:\code\agent-use\dripage" uv run mcp_server.py
```

### 2. Use with mcporter CLI

```bash
mcporter --config config/mcporter-http.json dripage --schema
# Save current page as markdown
mcporter call --config config/mcporter-http.json dripage.get

# Navigate and save
mcporter call --config config/mcporter-http.json dripage.get url:'https://example.com' formats:'["markdown"]'

# Save multiple formats
mcporter call --config config/mcporter-http.json dripage.get url:'https://example.com' formats:'["markdown","html","img"]'

# Network Listener - Monitor API responses
# Start listening for JSON API calls
mcporter call --config config/mcporter-http.json dripage.network_start_listener_tool mimeType:'application/json' url_include:'api'

# Get captured network data
mcporter call --config config/mcporter-http.json dripage.network_get_listener_data_tool

# Stop listening and clear data
mcporter call --config config/mcporter-http.json dripage.network_stop_listener_tool clear_data:true

# Monitor all network traffic
mcporter call --config config/mcporter-http.json dripage.network_start_listener_tool
```

### 3. Use with MCP Clients (Claude Desktop, Cursor, etc.)

Configure in your MCP client settings using `config/mcporter.json` or `config/mcporter-http.json`.

### 4. MCP Server Management

Use's MCP manager to control's server lifecycle:

```bash
# Start server (HTTP mode, port 8000)
uv run mcp_manager.py start

# Check server status
uv run mcp_manager.py status

# View recent logs
uv run mcp_manager.py logs --lines 50

# Restart server
uv run mcp_manager.py restart

# Stop server
uv run mcp_manager.py stop
```

**Custom startup:**
```bash
# Start on custom port
uv run mcp_manager.py start --port 8080

# Start STDIO mode
uv run mcp_manager.py start --transport stdio
```

**Custom startup:**
```bash
# Start on custom port
uv run mcp_manager.py start --port 8080

# Start STDIO mode
uv run mcp_manager.py start --transport stdio
```

The manager automatically handles:
- Process lifecycle (start/stop/restart)
- PID tracking and state persistence
- Log file management
- Health checks

## Configuration

Main configuration file: `config/mcp_config.yaml`

```yaml
browser:
  address: "127.0.0.1:19222"  # Browser connection address

output:
  directory: "output/data"       # Output directory

vision:
  model: "glm-4v-flash"         # Vision model
  temperature: 0.7
  max_tokens: 1024
```

For detailed configuration and MCP tools documentation, see [config/README.md](config/README.md).

## MCP Tools

### Core Tools

- `get` - Save page content in various formats
- `browser_navigate_tool` - Navigate to URL
- `browser_get_current_page_tool` - Get current page info
- `browser_screenshot_tool` - Take screenshot
- `browser_click_tool` - Click at coordinates
- `browser_input_tool` - Input text at coordinates
- `browser_press_key_tool` - Press keyboard keys
- `browser_scroll_tool` - Scroll page

### Vision & Analysis Tools

- `vision_analyze_tool` - Analyze images with GLM-4V
- `locate_element_tool` - Find elements using vision + coordinates
- `coordinate_convert_box_tool` - Convert GLM-4V coordinates
- `coordinate_parse_and_convert_tool` - Parse and convert coordinates
- `coordinate_convert_from_image_tool` - Convert based on image dimensions

### Network Monitoring Tools

- `network_start_listener_tool` - Start monitoring network responses (CDP)
- `network_get_listener_data_tool` - Get captured network data
- `network_stop_listener_tool` - Stop monitoring network responses
- `network_clear_listener_data_tool` - Clear captured network data

## Requirements

- Python 3.10+
- Chrome/Chromium browser
- [DrissionPage](https://github.com/g1879/DrissionPage)
- FastMCP
- MarkItDown

## License

MIT
