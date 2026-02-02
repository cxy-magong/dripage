# Dripage CLI 🚀

Unified command-line interface for browser automation and network packet capture.

## Features

- 🌐 **Browser Management** - Start, stop, check status of browsers with CDP support
- 📊 **Packet Capture** - Background network monitoring with filtering capabilities
- 📄 **Page Operations** - Get markdown, screenshots, and vision analysis
- ⚙️ **Action Commands** - Click, input, scroll on pages
- 🗑️ **Tab Management** - List, create, close, switch tabs
- 🔧 **Configuration Management** - Default config and session profiles
- 👁️ **Vision Integration** - GLM-4V model for visual analysis

## Quick Start

### Installation

```bash
# Install dependencies
uv sync
```

### Usage

```bash
# Show all commands
dripage --help

# Configuration management
dripage config set my-session --set-default
dripage config use my-session
dripage config reset
dripage config list

# Browser management
dripage browser start --name browser1
dripage browser status
dripage browser stop
dripage browser cdp
dripage browser verify

# Packet capture
dripage capture start --content-type application/json
dripage capture stop
dripage capture query --limit 50
dripage capture query --filter ".status_code == 200"

# Page operations
dripage page get https://example.com
dripage page screenshot
dripage page vision "What's on this page?"
dripage page vision --image /path/to/screenshot.png

# Tab management
dripage tab list
dripage tab new --url https://example.com
dripage tab close 0
```

## Architecture

### Module Structure

```
dripage/
├── cli.py                    # Main CLI entry point
├── cli_config.py             # Configuration management
├── cli_browser.py            # Browser management
├── cli_capture.py            # Packet capture
├── cli_page.py              # Page operations
└── tools/                   # Reused from existing codebase
    ├── browser_tools.py       # Browser operations
    ├── agent_tools.py        # Vision analysis
    └── tab_manager.py         # Tab management
```

### Configuration

#### Default Configuration (`config/dripage_default.yaml`)

```yaml
browser:
  name: "default"
  address: "127.0.0.1:19222"
  browser_path: ""
  user_data_dir: ""
  ini_file: ""
  headless: false

vision:
  model: "glm-4v-flash"
  temperature: 0.7
  max_tokens: 1024

capture:
  enabled: false
  output_dir: "output/packets"
  filters: {}
  save_all: false

output:
  directory: "output/data"
```

#### Session Profiles (`config/dripage_session.yaml`)

Multiple session profiles allow you to switch between different browser and capture configurations without passing repetitive parameters.

```bash
# Create and use a session
dripage config use dev
dripage browser start
# Now uses dev session config
```

## Command Reference

### Config Commands

| Command | Description |
|----------|-------------|
| `dripage config set` | Set or create a session configuration |
| `dripage config use` | Switch to a session |
| `dripage config list` | List all available sessions |
| `dripage config reset` | Reset to default configuration |

### Browser Commands

| Command | Description |
|----------|-------------|
| `dripage browser start` | Start a browser instance |
| `dripage browser stop` | Stop a browser instance |
| `dripage browser status` | Get browser status information |
| `dripage browser cdp` | Get CDP WebSocket URL |

**Options:**
- `--name` - Browser name from config/browsers.yaml
- `--address` - Browser CDP address (default from config/session)
- `--browser-path` - Path to browser executable
- `--user-data-dir` - User data directory

### Capture Commands

| Command | Description |
|----------|-------------|
| `dripage capture start` | Start background packet capture |
| `dripage capture stop` | Stop capture and save packets |
| `dripage capture query` | Query captured packets from files |

**Filters:**
- `--url-contains` - Filter packets by URL containing text
- `--content-type` - Filter by resource type (e.g., application/json)
- `--method` - Filter by HTTP method (e.g., GET, POST)
- `--response-contains` - Filter by response containing text
- `--status-code` - Filter by HTTP status code

**Query Options:**
- `--limit` - Maximum packets to return (default: 100)

### Page Commands

| Command | Description |
|----------|-------------|
| `dripage page get` | Get page content as markdown |
| `dripage page screenshot` | Take screenshot of current page |
| `dripage page vision` | Analyze page with vision model |

**Page Options:**
- `--url` - Page URL to navigate to
- `--no-save` - Return content only, don't save to file

**Vision Options:**
- `--query` - Question about the page/image
- `--image` - Path to image file (if not provided, takes screenshot)

### Action Commands

| Command | Description |
|----------|-------------|
| `dripage action click` | Click at coordinates |
| `dripage action input` | Input text at coordinates |
| `dripage action scroll` | Scroll page |

**Action Options:**
- `--clear` - Clear existing text before input (default: True)
- `--text` - Text to input
- `--direction` - Scroll direction (up/down)
- `--amount` - Scroll amount in pixels

### Tab Commands

| Command | Description |
|----------|-------------|
| `dripage tab list` | List all browser tabs |
| `dripage tab new` | Open a new tab |
| `dripage tab close` | Close a tab |

**Tab Options:**
- `--url` - URL to open in new tab

## Success Criteria Verification

### 1. Browser Start/Stop with CDP Connection

```bash
# Start browser with name from config
dripage browser start --name browser1

# Verify CDP URL
curl http://127.0.0.1:19222/json/version

# Expected output includes "webSocketDebuggerUrl" field with address
```

**Expected Result:**
```json
{
  "webSocketDebuggerUrl": "ws://127.0.0.1:19222/devtools/browser/..."
}
```

### 2. Packet Capture with Filtering

```bash
# Start packet capture with filter
dripage capture start --content-type application/json --url-contains baidu

# Visit page (e.g., http://www.baidu.com)
# Packets will be captured to output/packets/

# Query packets with jq-like filtering
dripage capture query --limit 50 --filter ".url | contains(\"baidu\")"
```

**Expected Result:**
- Packets saved to `output/packets/packets_<timestamp>.jsonl`
- Raw packet data includes: request headers, response headers, status codes
- Filter criteria applied during capture

### 3. Page Markdown Extraction

```bash
# Get page as markdown
dripage page get https://example.com

# Expected output:
{
  "status": "success",
  "url": "https://example.com",
  "title": "Example Domain",
  "file": "output/data/page_data/page_20250203_120000.md",
  "content": "# Example Domain\n..."
}
```

### 4. Vision Analysis

```bash
# Analyze current page
dripage page vision "Describe the main content of this page"

# Expected output includes:
- Image size (width x height)
- Analysis result from GLM-4V
- Image file path
```

## Design Principles

### Code Reuse

- **tools/** modules** - All page operations reuse existing `browser_tools.py`, `agent_tools.py`, `tab_manager.py`
- **utils/chrome_manager.py** - Browser management reuses existing ChromeManager
- **utils/drission_page.py** - Browser creation reuses existing `create_browser`

### Multi-Agent Safety

The CLI uses configuration files to avoid browser conflicts:

1. **Default Config** - `config/dripage_default.yaml` for global settings
2. **Session Profiles** - `config/dripage_session.yaml` for different agent contexts

Each agent can:
- Use `dripage config use <session-name>` to switch to its own session
- Have independent browser instances with different ports
- Have separate packet capture outputs

## Packet Capture Features

### Background Capture

Packet capture runs in the background, continuously monitoring browser network traffic:

- **Filtering** - Apply filters during capture to reduce noise
- **File Storage** - Packets saved to JSONL files for easy jq filtering
- **Query API** - Search and filter captured packets

### Filter Examples

```bash
# Capture only JSON responses
dripage capture start --content-type application/json

# Capture only POST requests
dripage capture start --method POST

# Capture from specific URL
dripage capture start --url-contains baidu

# Filter by status code
dripage capture start --status-code 200

# Multiple filters
dripage capture start --content-type application/json --method POST
```

### Data Format

Each captured packet includes:
```json
{
  "timestamp": "2025-01-01T12:00:00",
  "url": "https://example.com/api/data",
  "method": "GET",
  "status_code": 200,
  "resource_type": "application/json",
  "request_headers": {"user-agent": "..."},
  "response_headers": {"content-type": "application/json"},
  "response_body": "{...}",
  "response_size": 1234
}
```

## Usage Examples

### Example 1: Automated Testing

```bash
# 1. Create session for automated testing
dripage config set test --set-default

# 2. Start browser
dripage browser start

# 3. Start packet capture
dripage capture start --content-type application/json

# 4. Navigate and test
dripage page get https://example.com

# 5. Check captured packets
dripage capture query --limit 10

# 6. Stop capture
dripage capture stop
```

### Example 2: Visual Analysis with Vision

```bash
# 1. Navigate to page
dripage page get https://www.baidu.com

# 2. Take screenshot
dripage page screenshot

# 3. Analyze with vision
dripage page vision "What is the main content of this page?"

# 4. Get detailed analysis
dripage page vision "Read all text in the image"

# 5. Switch between filters
dripage capture query --filter ".content_type | contains(\"application/json\")"
dripage capture query --filter ".method == \"GET\""
```

### Example 3: Multi-Agent Scenarios

```bash
# Agent 1: Setup and capture
dripage config use agent1 --set-default
dripage browser start
dripage capture start

# Agent 2: Work independently
dripage config use agent2
dripage browser start
# Now agent2 has its own browser context
```

## Troubleshooting

### Python Not Found Error

If you see "python: command not found", use:
```bash
# Use full path
G:/code/agent-use/dripage/python cli.py --help
```

### Module Import Errors

If you see "ModuleNotFoundError: No module named 'xxx'", try:
```bash
# Reinstall dependencies
uv sync
```

## Implementation Notes

### Code Structure

- **cli.py** - Main entry point using Click framework
- **cli_config.py** - Configuration dataclasses and manager
- **cli_browser.py** - Wraps utils/chrome_manager.py
- **cli_capture.py** - Uses DrissionPage's page.listen API
- **cli_page.py** - Reuses tools/ module functions

### Key Decisions

1. **Configuration over parameters** - Avoids repetitive --port, --browser-path arguments
2. **Session profiles** - Multiple agents can have independent browser contexts
3. **File-based packet storage** - JSONL files for efficient filtering
4. **jq-like query syntax** - Familiar to developers working with JSON data

### Success Standards

All commands return JSON output with:
- `status`: "success" or "error"
- `message`: Human-readable status message
- `data`: Command-specific data (browser info, file paths, packet counts, etc.)
