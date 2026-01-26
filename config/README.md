# MCP Server Configuration

This directory contains configuration files for the Dripage MCP server.

## Files

### `mcp_config.yaml`
Main configuration file for the MCP server.

**Configuration options:**

```yaml
browser:
  address: "127.0.0.1:19222"  # Browser connection address

output:
  directory: "output"              # Output directory (relative to project root)
  images_subdir: "images"          # Screenshot subdirectory

vision:
  model: "glm-4v-flash"           # Default vision model
  temperature: 0.7                 # Temperature for vision API
  max_tokens: 1024                 # Max tokens for vision API
```

### `mcporter.json`
Configuration for mcporter using STDIO transport.

### `mcporter-http.json`
Configuration for mcporter using HTTP transport (for testing).

### `models_config.yaml`
Model configuration for vision and AI tools.

---

## MCP Tools

### `get` - Save Page Content

Navigate to a URL or save current page in specified format(s).

**Parameters:**
- `url` (optional): The webpage URL to navigate to. If not provided, saves the current page.
- `formats` (optional): Output format(s) as list. Default: `["markdown"]`
  - Supported formats: `"markdown"`, `"html"`, `"img"`, `"mhtml"`
  - Can specify single or multiple formats: `["markdown", "html", "img"]`

**Returns:**
JSON object containing:
- `title`: Page title
- `url`: Page URL
- `file`: File path (single format) OR
- `files`: Array of file paths (multiple formats)
- `count`: Number of files (only when multiple formats)
- `formats`: Array of formats (only when multiple formats)

**Examples:**

1. **Get current page (default markdown format)**:
```bash
mcporter call --config config/mcporter-http.json dripage.get
```
Response:
```json
{
  "title": "Page Title",
  "url": "https://example.com/",
  "file": "G:\\code\\agent-use\\dripage\\output\\data\\page_20260126_202952.md"
}
```

2. **Navigate to URL and save as markdown**:
```bash
mcporter call --config config/mcporter-http.json dripage.get url:'https://example.com' formats:'["markdown"]'
```
Response:
```json
{
  "title": "Example Domain",
  "url": "https://example.com/",
  "file": "G:\\code\\agent-use\\dripage\\output\\data\\page_20260126_203007.md"
}
```

3. **Save in multiple formats**:
```bash
mcporter call --config config/mcporter-http.json dripage.get url:'https://example.com' formats:'["markdown","html","img"]'
```
Response:
```json
{
  "title": "Example Domain",
  "url": "https://example.com/",
  "files": [
    "G:\\code\\agent-use\\dripage\\output\\data\\page_20260126_203007.md",
    "G:\\code\\agent-use\\dripage\\output\\data\\page_20260126_203007.html",
    "G:\\code\\agent-use\\dripage\\output\\data\\page_20260126_203007.png"
  ],
  "count": 3,
  "formats": ["markdown", "html", "img"]
}
```

**File Naming:**
- Pattern: `page_{timestamp}.{ext}`
- Example: `page_20260126_202952.md`
- Output directory: Configured in `mcp_config.yaml` (default: `output/data`)
