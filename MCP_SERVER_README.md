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

### 1. `screenshot`
Take a screenshot of the current page.

**Parameters:**
- None (captures full page)

**Returns:**
- File path to saved screenshot in `output/images/`

**Example:**
```json
{
  "name": "screenshot",
  "arguments": {}
}
```

### 2. `get`
Navigate to a URL.

**Parameters:**
- `url` (required): The webpage URL to navigate to

**Returns:**
- Success message

**Example:**
```json
{
  "name": "get",
  "arguments": {
    "url": "https://example.com"
  }
}
```

### 3. `get2markdown`
Convert a webpage URL to markdown format.

**Parameters:**
- `url` (required): The webpage URL to convert

**Returns:**
- Markdown content of webpage

**Example:**
```json
{
  "name": "get2markdown",
  "arguments": {
    "url": "https://example.com"
  }
}
```

### 4. `vision`
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
mcporter list dripage --config config/mcporter-http.json --schema
# Call a tool
npx mcporter call --config config/mcporter-http.json dripage.get url:https://example.com

# Test screenshot
npx mcporter call --config config/mcporter-http.json dripage.screenshot
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

- `ZAI_API_KEY`: Required for `vision` tool (ZhipuAI API key)

## Configuration

Server configuration is loaded from `config/mcp_config.yaml`:

```yaml
browser:
  address: "127.0.0.1:19222"

output:
  directory: "output"
  images_subdir: "images"

vision:
  model: "glm-4v-flash"
  temperature: 0.7
  max_tokens: 1024
```

## Output

Screenshots and images are saved to `output/images/` directory (configurable in `config/mcp_config.yaml`).

## Browser

The server uses DrissionPage and connects to a browser at the address specified in `config/mcp_config.yaml` (default: `127.0.0.1:19222`).

Make sure you have a Chrome browser running with debugging enabled at that address, or start it with:

```bash
# Using DrissionPage
python -c "from DrissionPage import ChromiumPage; page = ChromiumPage(addr_or_opts='127.0.0.1:19222')"
```

## Configuration Notes

- All browser addresses are now managed centrally in `config/mcp_config.yaml`
- Screenshot tool no longer accepts `element_id` parameter (always captures full page)
- All tools use the default browser address from configuration
- Vision model parameters can be customized in `config/mcp_config.yaml`
