# Dripage 🚀

Browser automation tool with CLI support, MCP server integration, and vision analysis capabilities.

## Features

- 🌐 **Browser Automation**: Navigate, interact with web pages via CLI
- 📄 **Content Extraction**: Save pages as Markdown, HTML, images, or MHTML
- 👁️ **Vision Analysis**: Analyze screenshots using GLM-4V vision model
- 🔍 **Element Location**: Find and locate elements using vision + coordinates
- 📡 **Network Packet Capture**: Background packet monitoring with filtering capabilities
- 🔌 **MCP Server**: Model Context Protocol integration for AI agents

## Quick Start (CLI)

### 1. Installation

```bash
# Clone repository
git clone <repository-url>
cd dripage

# Install dependencies (requires Python 3.13+)
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env and fill in your API keys
```

### 2. Configure Environment

Edit `.env` file and add required API keys:

```bash
# Required for vision analysis
ZAI_API_KEY="your_zhipuai_api_key_here"
```

### 3. Start Browser

```bash
# Start browser with default configuration
uv run .\cli.py browser start

# Or start with custom configuration
uv run .\cli.py browser start --address 127.0.0.1:19222
```

### 4. Common Commands

```bash
# Navigate to a webpage
uv run .\cli.py tab new --url https://example.com

# Get page content as markdown
uv run .\cli.py get

# Take a screenshot
uv run .\cli.py screenshot

# Analyze page with vision
uv run .\cli.py vision "What's on this page?"

# Click at coordinates
uv run .\cli.py click 100 200

# List tabs
uv run .\cli.py tab list

# Get help
uv run .\cli.py --help
```

### 5. Use with AI (OpenCode, Claude, etc.)

When working with AI agents, simply ask to use `dripage` CLI commands:

> "Navigate to https://github.com and take a screenshot"

> "Find of search box and input 'test'"

> "Get page content as markdown"

For complete CLI documentation, see [README_CLI.md](README_CLI.md).

---

## MCP Server (Optional)

### Quick Start

```bash
# Start MCP server (HTTP mode for testing)
uv run mcp_server.py http

# Or start MCP server (STDIO mode for production)
uv run mcp_server.py
```

### Configuration

Edit `config/mcp_config.yaml` to configure browser and vision settings:

```yaml
browser:
  address: "127.0.0.1:19222"

vision:
  model: "glm-4v-flash"
  temperature: 0.7
  max_tokens: 1024
```

For detailed MCP documentation, see [MCP_SERVER_README.md](MCP_SERVER_README.md).

---

## Advanced Configuration

### Browser Management

```bash
# Check browser status
uv run .\cli.py browser status

# Stop browser
uv run .\cli.py browser stop

# Get CDP URL
uv run .\cli.py browser cdp
```

### Tab Management

```bash
# List all tabs
uv run .\cli.py tab list

# Create new tab
uv run .\cli.py tab new --url https://example.com

# Switch to tab (by index)
uv run .\cli.py tab switch 0

# Close tab
uv run .\cli.py tab close 0
```

### Network Packet Capture

```bash
# Start capturing JSON responses
uv run .\cli.py capture start --content-type application/json

# Query captured packets
uv run .\cli.py capture query --limit 10

# Stop capturing
uv run .\cli.py capture stop
```

---

## Documentation

- [README_CLI.md](README_CLI.md) - Complete CLI reference
- [MCP_SERVER_README.md](MCP_SERVER_README.md) - MCP server documentation
- [AGENTS.md](AGENTS.md) - Project-specific coding guidelines
- [example/README.md](example/README.md) - Usage examples

---

## Requirements

- Python 3.13+
- Chrome/Chromium browser
- [DrissionPage](https://github.com/g1879/DrissionPage)
- FastMCP
- MarkItDown

## License

MIT
