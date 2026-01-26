# Dripage 🚀

Browser automation and vision analysis via MCP (Model Context Protocol).

## Features

- 🌐 **Browser Automation**: Navigate, interact with web pages
- 📄 **Content Extraction**: Save pages as Markdown, HTML, images, or MHTML
- 👁️ **Vision Analysis**: Analyze screenshots using GLM-4V vision model
- 🔍 **Element Location**: Find and locate elements using vision + coordinates

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
# Save current page as markdown
mcporter call --config config/mcporter-http.json dripage.get

# Navigate and save
mcporter call --config config/mcporter-http.json dripage.get url:'https://example.com' formats:'["markdown"]'

# Save multiple formats
mcporter call --config config/mcporter-http.json dripage.get url:'https://example.com' formats:'["markdown","html","img"]'
```

### 3. Use with MCP Clients (Claude Desktop, Cursor, etc.)

Configure in your MCP client settings using `config/mcporter.json` or `config/mcporter-http.json`.

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

## Requirements

- Python 3.10+
- Chrome/Chromium browser
- [DrissionPage](https://github.com/g1879/DrissionPage)
- FastMCP
- MarkItDown

## License

MIT
