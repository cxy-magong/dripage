---
name: dripage-cli
description: Browser automation CLI tool - control browsers, capture pages, interact with elements, and test frontend via command line.
---

# Dripage CLI Browser Automation

Command-line interface for browser automation, page testing, and visual verification.

## When to Use

- Need to control browser from command line
- Automate web page testing
- Take screenshots for frontend verification
- Extract page content in Markdown format
- Test local development servers

---

## Core Commands

### Browser Management

```bash
dripage browser status      # Check browser status
dripage browser start        # Start browser instance
dripage browser stop         # Stop browser

# Options:
#   --name TEXT          Browser name from config/browsers.yaml
#   --address TEXT       Browser address (e.g., 127.0.0.1:19222)
#   --browser-path TEXT  Path to browser executable
#   --user-data-dir TEXT Path to user data directory
```

**Common Mistake**: `browser start` does NOT accept `--url` option

### Tab Management

```bash
dripage tab new --url http://example.com    # Open new tab with URL
dripage tab list                              # List all tabs
dripage tab close                             # Close current tab

# Options:
#   --url TEXT  URL to open
```

**Common Mistake**: Must use `--url` flag, cannot pass URL as positional argument

### Page Operations

```bash
dripage page screenshot      # Take screenshot of current page
dripage page get            # Get page content as Markdown
dripage page vision         # Analyze page with vision model

# Vision options:
#   --query TEXT          Question about the page (required)
#   --image PATH          Path to image file (optional, uses screenshot if not provided)
#   --save-file          Save screenshot to file (default: in-memory analysis, faster)
```

**Note**: `page get` requires `output/data/page_data` directory to exist

**Vision Analysis Tips**:
- Default mode uses in-memory analysis (no file I/O, faster)
- Use `--save-file` flag to save screenshot for debugging
- Example: `dripage page vision --query "Describe this page" --save-file`

### Element Interaction

```bash
dripage action click <x> <y>        # Click at coordinates
dripage action input <x> <y> <text>  # Input text at coordinates
dripage action scroll [down|up]       # Scroll page
```

### Network Packet Capture

```bash
dripage capture start    # Start background packet capture with filters
dripage capture stop     # Stop packet capture and save remaining packets
dripage capture query    # Query captured packets from files

# Start capture options:
#   --mimeType TEXT       Filter by MIME type (e.g., application/json)
#   --url-include TEXT   Filter by URL pattern
#   --save-path TEXT     Custom save path
```

### Configuration Management

```bash
dripage config list       # List all available sessions
dripage config set [name] # Set or create a session configuration
dripage config use        # Switch to a session configuration
dripage config reset      # Reset to default configuration

# Set options:
#   --set-default         Set current config as default
```

---

## Typical Workflows

### Verify Local Development Server

```bash
# 1. Check browser status
dripage browser status

# 2. Start browser if not running
dripage browser start

# 3. Open new tab and navigate to URL
dripage tab new --url http://localhost:3000

# 4. Take screenshot for verification
dripage page screenshot

# 5. (Optional) Get page content
dripage page get

# 6. (Optional) Analyze with vision model
dripage page vision --query "What's on this page?"
```

### Get Page Content

```bash
dripage tab new --url https://example.com
dripage page get
```

### Capture Network Traffic

```bash
# 1. Start browser
dripage browser start

# 2. Open target page
dripage tab new --url https://example.com

# 3. Start network capture (filter JSON responses)
dripage capture start --mimeType application/json

# 4. Interact with page to trigger network requests
# (e.g., click buttons, navigate)

# 5. Stop capture
dripage capture stop

# 6. Query captured packets
dripage capture query
```

### Vision Analysis Workflow

```bash
# Fast mode (default, no file I/O)
dripage page vision --query "Find the submit button"

# With saved screenshot for debugging
dripage page vision --query "Describe this page" --save-file

# Analyze existing image file
dripage page vision --query "What's in this image?" --image /path/to/screenshot.png
```

---

## Common Errors & Solutions

| Error Command | Correct Command | Reason |
|--------------|----------------|--------|
| `dripage browser start --url http://example.com` | `dripage browser start` + `dripage tab new --url http://example.com` | `start` doesn't support `--url` |
| `dripage tab new http://example.com` | `dripage tab new --url http://example.com` | Must use `--url` parameter |

---

## Help Commands

```bash
dripage --help              # Show all commands
dripage browser --help       # Show browser subcommand help
dripage tab --help           # Show tab subcommand help
dripage page --help          # Show page subcommand help
dripage action --help        # Show action subcommand help
```

---

## Output Paths

- **Screenshots**: `output/data/screenshot_*.png`
- **Vision Screenshots** (when --save-file): `output/data/vision_*.png`
- **Page Data**: `output/data/page_data/`
- **Network Capture**: `output/network_capture/`
- **Config Directory**: `config/`
- **Browser Config**: `config/browsers.yaml`
- **Log Directory**: `output/log/`

**Note**: Paths are relative to dripage project root directory.

---

## Quick Reference

| Task | Command |
|------|---------|
| Check status | `dripage browser status` |
| Start browser | `dripage browser start` |
| Open webpage | `dripage tab new --url <URL>` |
| Screenshot | `dripage page screenshot` |
| Get content | `dripage page get` |
| Vision analyze | `dripage page vision --query "<text>"` |
| Capture network | `dripage capture start --mimeType application/json` |
| Get help | `dripage --help` |
