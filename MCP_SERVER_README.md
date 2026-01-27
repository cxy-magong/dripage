# Dripage MCP Server

FastMCP-based server for browser automation and vision analysis.

## Installation

Dependencies are already in `pyproject.toml`:
```bash
uv add fastmcp
```

## Running the Server

### Option 1: STDIO Transport (Default)

For integration with Claude Desktop, Cursor, etc.:

```bash
uv run mcp_server.py
```

### Option 2: HTTP Transport (For Testing)

```bash
uv run mcp_server.py http
```

Server will start at `http://127.0.0.1:8000`

## Available Tools

**Recommended Workflow:**
- Use `get` to navigate to a page
- Use `locate_element_tool` to find elements (automatically handles vision analysis + coordinate conversion)
- Use `browser_click_tool`, `browser_input_tool`, etc. to interact with elements
- Use `vision_analyze_tool` for custom visual queries

### Core Tools

### 1. `get`
Navigate to a URL or get current page info, save in specified format(s). Supports concurrent processing of multiple formats.

**Parameters:**
- `url` (optional): The webpage URL to navigate to. If not provided, returns current page info (title and URL) as JSON
- `formats` (optional, default: `["markdown"]`): Output format(s) as list:
                 `["markdown"]`, `["html"]`, `["img"]`, `["mhtml"]`,
                 or multiple formats: `["markdown", "html", "img"]`

**Returns:**
- JSON array with multiple file paths for multiple formats (concurrent processing)
- Single file path (in JSON array) for single format
- JSON with page title if URL not provided

**Examples:**
```json
// Get current page info
{
  "name": "get",
  "arguments": {}
}

// Navigate and save as markdown (default format)
{
  "name": "get",
  "arguments": {
    "url": "https://example.com"
  }
}

// Navigate and save as single format
{
  "name": "get",
  "arguments": {
    "url": "https://example.com",
    "formats": ["html"]
  }
}

// Navigate and save as multiple formats (concurrent)
{
  "name": "get",
  "arguments": {
    "url": "https://example.com",
    "formats": ["markdown", "html", "img"]
  }
}

// Navigate and save as all formats (concurrent)
{
  "name": "get",
  "arguments": {
    "url": "https://example.com",
    "formats": ["markdown", "html", "img", "mhtml"]
  }
}
```

**Response Examples:**

Multiple formats (concurrent processing):
```json
{
  "name": "get",
  "arguments": {
    "url": "https://example.com",
    "formats": ["markdown", "html", "img"]
  }
}
```
**Result:**
```json
{
  "files": [
    "G:\\code\\agent-use\\dripage\\output\\page_20260125_123456.md",
    "G:\\code\\agent-use\\dripage\\output\\page_20260125_123456.html",
    "G:\\code\\agent-use\\dripage\\output\\page_20260125_123456.png"
  ],
  "count": 3,
  "formats": ["markdown", "html", "img"]
}
```

**Performance:**
- Single format: ~0.2-1.5s
- Multiple formats (concurrent): ~0.3-0.4s (all formats processed in parallel)

### 2. `locate_element_tool`
Locate element using vision analysis and coordinate conversion. This is a high-level tool that combines vision analysis with automatic coordinate conversion.

**Parameters:**
- `query` (required): Description of element to locate (e.g., "search input box", "submit button")
- `image_path` (optional): Path to image file. If not provided, captures current screenshot.

**Returns:**
- JSON with element location, converted coordinates, and analysis details

**Example:**
```json
{
  "name": "locate_element_tool",
  "arguments": {
    "query": "search input box"
  }
}
```

**Use cases:**
- Find button coordinates for clicking
- Locate input fields for text entry
- Identify element positions for any UI interaction

### 3. `vision_analyze_tool`
Analyze images using GLM-4V vision model.

**Parameters:**
- `query` (required): The query/question about the image
- `image_path` (optional): Path to image file. If not provided, captures current screenshot.

**Returns:**
- Vision analysis result text

**Example:**
```json
{
  "name": "vision_analyze_tool",
  "arguments": {
    "query": "What do you see in this image?"
  }
}
```

### 4. `browser_screenshot_tool`
Take a screenshot of current page.

**Parameters:**
- None (always captures full page)

**Returns:**
- File path to saved screenshot in `output/`

**Example:**
```json
{
  "name": "browser_screenshot_tool",
  "arguments": {}
}
```

### Browser Interaction Tools

### 5. `browser_navigate_tool`
Navigate browser to specified URL.

**Parameters:**
- `url` (required): The URL to navigate to

**Returns:**
- Success message with page title

### 6. `browser_click_tool`
Click at specified coordinates on the page.

**Parameters:**
- `x` (required): X coordinate
- `y` (required): Y coordinate

**Returns:**
- Success message

### 7. `browser_input_tool`
Click input box at coordinates and input text.

**Parameters:**
- `x` (required): X coordinate of input box
- `y` (required): Y coordinate of input box
- `text` (required): Text to input
- `clear` (optional, default: true): Whether to clear existing text first

**Returns:**
- Success message

### 8. `browser_press_key_tool`
Press keyboard keys.

**Parameters:**
- `key` (required): Key name (e.g., 'enter', 'escape', 'space', 'tab')
- `times` (optional, default: 1): Number of times to press

**Returns:**
- Success message

### 9. `browser_scroll_tool`
Scroll the page.

**Parameters:**
- `direction` (optional, default: "down"): Scroll direction, 'up' or 'down'
- `amount` (optional, default: 500): Scroll amount in pixels

**Returns:**
- Success message

### Coordinate Conversion Tools

### 10. `coordinate_convert_from_image_tool`
Parse coordinates from text and convert back based on image dimensions. Most convenient coordinate conversion tool.

**Parameters:**
- `text` (required): Text containing coordinates (e.g., from vision model response)
- `image_path` (required): Path to image file (used to get original dimensions)

**Returns:**
- JSON with converted coordinates

**Example:**
```json
{
  "name": "coordinate_convert_from_image_tool",
  "arguments": {
    "text": "The button is at [[293,244,710,327]]",
    "image_path": "output/screenshot_20260125_123456.png"
  }
}
```

### 2. `get`
Navigate to a URL or get current page info, save in specified format(s). Supports concurrent processing of multiple formats.

**Parameters:**
- `url` (optional): The webpage URL to navigate to. If not provided, returns current page info (title and URL) as JSON
- `formats` (optional): Output format(s) - can be single format (string) or list of formats:
                 "markdown", "html", "img", "mhtml"
                 If not provided, defaults to ["markdown"]

**Returns:**
- Single file path (string) for single format
- JSON array with multiple file paths for multiple formats (concurrent processing)
- JSON with page title if URL not provided

**Examples:**
```json
// Get current page info
{
  "name": "get",
  "arguments": {}
}

// Navigate and save as markdown (single format)
{
  "name": "get",
  "arguments": {
    "url": "https://example.com",
    "formats": "markdown"
  }
}

// Navigate and save as multiple formats (concurrent)
{
  "name": "get",
  "arguments": {
    "url": "https://example.com",
    "formats": ["markdown", "html", "img"]
  }
}

// Navigate and save as all formats (concurrent)
{
  "name": "get",
  "arguments": {
    "url": "https://example.com",
    "formats": ["markdown", "html", "img", "mhtml"]
  }
}
```

**Response Examples:**

Single format:
```json
{
  "name": "get",
  "arguments": {
    "url": "https://example.com",
    "formats": "markdown"
  }
}
```
**Result:**
```
G:\code\agent-use\dripage\output\page_20260125_123456.md
```

Multiple formats (concurrent processing):
```json
{
  "name": "get",
  "arguments": {
    "url": "https://example.com",
    "formats": ["markdown", "html", "img"]
  }
}
```
**Result:**
```json
{
  "files": [
    "G:\\code\\agent-use\\dripage\\output\\page_20260125_123456.md",
    "G:\\code\\agent-use\\dripage\\output\\page_20260125_123456.html",
    "G:\\code\\agent-use\\dripage\\output\\page_20260125_123456.png"
  ],
  "count": 3,
  "formats": ["markdown", "html", "img"]
}
```

**Performance:**
- Single format: ~0.2-1.5s
- Multiple formats (concurrent): ~0.3-0.4s (all formats processed in parallel)

### 3. `vision`
Analyze images using GLM-4V vision model.

**Parameters:**
- `query` (required): The query/question about the image
- `image_path` (optional): Path to image file. If not provided, captures current screenshot.
- `model` (optional): Vision model to use (default: from config or "glm-4v-flash")

**Returns:**
- Vision analysis result

**Example:**
```json
{
  "name": "vision",
  "arguments": {
    "query": "What do you see in this image?"
  }
}
```

## Testing with mcporter

### Install mcporter
```bash
npm install -g mcporter
# or use npx: npx mcporter
```

### Configure mcporter
Use the provided config file:

```bash
# HTTP transport (for testing)
npx mcporter list --config config/mcporter-http.json

# STDIO transport (for integration)
npx mcporter list --config config/mcporter.json
```

### Test Tools
```bash
# List all tools
npx mcporter list --config config/mcporter-http.json
mcporter list --config config/mcporter-http.json
mcporter list dripage --config config/mcporter-http.json --schema

# Get current page info
npx mcporter call --config config/mcporter-http.json dripage.get

# Navigate and save as markdown (default)
npx mcporter call --config config/mcporter-http.json dripage.get url:https://example.com

# Navigate and save as multiple formats (concurrent)
npx mcporter call --config config/mcporter-http.json dripage.get url:https://example.com formats:'["markdown", "html", "img"]'

# Navigate and save as all formats (concurrent)
npx mcporter call --config config/mcporter-http.json dripage.get url:https://example.com formats:'["markdown", "html", "img", "mhtml"]'

# Test screenshot
npx mcporter call --config config/mcporter-http.json dripage.browser_screenshot_tool

# Test locate element
npx mcporter call --config config/mcporter-http.json dripage.locate_element_tool query:"search input box"

# Test vision analysis
npx mcporter call --config config/mcporter-http.json dripage.vision_analyze_tool query:"What do you see?"

# Test browser navigation
npx mcporter call --config config/mcporter-http.json dripage.browser_navigate_tool url:https://example.com
```

## Claude Desktop Integration

Add to Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "dripage": {
      "command": "uv",
      "args": ["run", "mcp_server.py"],
      "cwd": "G:\\code\\agent-use\\dripage",
      "env": {
        "PYTHONPATH": "G:\\code\\agent-use\\dripage"
      }
    }
  }
}
```

## Environment Variables

- `ZAI_API_KEY`: Required for `vision_analyze_tool` and `locate_element_tool` (ZhipuAI API key)

## Configuration

Server configuration is loaded from `config/mcp_config.yaml`:

```yaml
browser:
  address: "127.0.0.1:19222"

output:
  directory: "output"

vision:
  model: "glm-4v-flash"
  temperature: 0.7
  max_tokens: 1024
```

## Output

All files (screenshots, HTML, Markdown, images, MHTML) are saved to `output/` directory (configurable in `config/mcp_config.yaml`).

**File naming format:** `{type}_YYYYMMDD_HHMMSS.{ext}`

Examples:
- `screenshot_20260125_123456.png`
- `page_20260125_123456.md`
- `page_20260125_123456.html`
- `page_20260125_123456.png`
- `page_20260125_123456.mhtml`

## Browser

The server uses DrissionPage and connects to a browser at the address specified in `config/mcp_config.yaml` (default: `127.0.0.1:19222`).

Make sure you have a Chrome browser running with debugging enabled at that address, or start it with:

```bash
# Using DrissionPage
python -c "from DrissionPage import ChromiumPage; page = ChromiumPage(addr_or_opts='127.0.0.1:19222')"
```

## Configuration Notes

- All browser addresses are now managed centrally in `config/mcp_config.yaml`
- `browser_screenshot_tool` always captures full page
- `get` tool's `formats` parameter must be a list (e.g., `["markdown"]`, not `"markdown"`)
- All tools use the default browser address from configuration
- Vision model parameters can be customized in `config/mcp_config.yaml`
