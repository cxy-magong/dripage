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
```

**Note**: `page get` requires `output/data/page_data` directory to exist

### Element Interaction

```bash
dripage action click <x> <y>        # Click at coordinates
dripage action input <x> <y> <text>  # Input text at coordinates
dripage action scroll [down|up]       # Scroll page
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
```

### Get Page Content

```bash
dripage tab new --url https://example.com
dripage page get
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

- **Screenshots**: `G:\code\agent-use\dripage\output\data\screenshot_*.png`
- **Page Data**: `G:\code\agent-use\dripage\output\data\page_data\`
- **Config Directory**: `G:\code\agent-use\dripage\config\`
- **Browser Config**: `config/browsers.yaml`

---

## Quick Reference

| Task | Command |
|------|---------|
| Check status | `dripage browser status` |
| Start browser | `dripage browser start` |
| Open webpage | `dripage tab new --url <URL>` |
| Screenshot | `dripage page screenshot` |
| Get content | `dripage page get` |
| Get help | `dripage --help` |
