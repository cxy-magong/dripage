---
name: dripage-cli
description: Browser automation CLI for frontend testing, screenshot capture, and visual verification
trigger-phrases:
  - dripage
  - screenshot
  - 视觉查看
  - 视觉分析
  - 验证前端
  - frontend verification
  - browser automation
  - 页面测试
  - page test
allowed-tools: Bash(dripage:*)
---

# Dripage CLI

Browser automation via command line for testing, screenshots, and visual verification.

## Tool Restrictions (MUST OBEY)

**ONLY tools with `dripage:*` namespace are allowed.**

### Allowed Tools
- ✅ `Bash(dripage:*)` - All dripage CLI commands

### Forbidden Tools
- ❌ `Bash` (non-dripage namespace) - Generic bash commands
- ❌ `read` tool - Never use read for visual analysis
- ❌ `look_at` tool - Never use look_at for visual analysis
- ❌ Any other image viewing tools - Never use after vision analysis

**Why**: This skill provides complete browser automation capabilities through dripage CLI. Other tools are redundant and should not be used.

---

## Multi-Browser Configuration

### Browser Selection Priority

Dripage supports automatic browser selection based on configuration:

```
Priority:
1. DRIPAGE_BROWSER environment variable (highest)
2. Project-level config (.dripage/config in CWD)
3. User-level app config (~/.dripage/current_app)
4. Global default config (lowest)
```

### Usage Examples

#### Scenario 1: Project-Level Configuration (Recommended)

Each project can have its own `.dripage/config` file:

```yaml
# .dripage/config
app_id: crawler_prod
browser: browser2
output:
  directory: G:\code\crawler_prod\output
```

**Usage**:
```bash
cd /path/to/project
dripage get http://example.com  # Automatically uses browser2
```

#### Scenario 2: Environment Variable Override

For different terminal sessions:

```bash
# Terminal 1 - Use browser1
export DRIPAGE_BROWSER=browser1
dripage get http://example.com

# Terminal 2 - Use browser2 (concurrent)
export DRIPAGE_BROWSER=browser2
dripage get http://example.com
```

#### Scenario 3: View Current Configuration

```bash
dripage config show
```

**Output**:
```
Current Configuration:
  Source: project (.dripage/config)
  Browser: browser2 @ 127.0.0.1:19000
  App ID: crawler_prod
```

### Browser Management Commands

```bash
# Start browser (uses current config automatically)
dripage browser start

# Start specific browser
dripage browser start --name browser2

# Stop browser (uses current config automatically)
dripage browser stop

# View all browser status with current indicator
dripage browser status
```

**Output Example**:
```
Current browser: browser2

● default: running
● ★ browser2 [CURRENT]: running  ← Current browser
● browser1: running
```

### Concurrency Best Practices

For running multiple tasks concurrently:

```bash
# Terminal 1 - Crawler production
cd /path/to/crawler_prod
# .dripage/config: browser: browser1
dripage browser start
dripage get http://target1.com

# Terminal 2 - Scraper Amazon (concurrent)
cd /path/to/scraper_amazon
# .dripage/config: browser: browser2
dripage browser start
dripage get http://amazon.com

# Terminal 3 - Test runner (concurrent)
cd /path/to/test_runner
# .dripage/config: browser: browser3
dripage browser start
dripage get http://localhost:3000
```

**Key Points**:
- Each terminal uses its own browser
- No interference between concurrent operations
- Automatic browser selection based on config priority

---

## Trigger When
- User mentions "dripage", "screenshot", "视觉查看"
- Needs to verify frontend UI or take screenshots
- Wants to analyze page content visually
- Testing local development servers

---

## Mandatory Rules (NEVER VIOLATE)

### Rule 1: USE In-Memory Vision/Locate (DEFAULT MODE)

**CRITICAL**: `vision` and `locate` default to **in-memory mode**.

```bash
# ★ DEFAULT MODE (PREFERRED) - In-memory, no file save
dripage vision --query "描述这个页面的布局"
dripage locate --query "搜索按钮"

# ❌ DO NOT do this (redundant):
dripage screenshot
dripage vision --image output/data/screenshot_xxx.png --query "描述这个页面的布局"
```

**Why**: 
- `vision` and `locate` automatically capture screenshots in-memory
- No file I/O operations (faster)
- No unnecessary disk writes
- Token-efficient

**When to use file save mode**:
```bash
# ONLY for debugging - Save screenshot to disk
dripage vision --query "检查布局" --save-file

# ONLY for retrospective analysis - Analyze existing image
dripage vision --query "这个页面有什么问题？" --image /path/to/image.png
```

### Rule 2: NEVER Use `read` or `look_at` After Vision/Locate

After `vision` or `locate` completes:
- ✅ **DO**: Report analysis/locate result directly to user
- ❌ **DO NOT**: Call `read`, `look_at`, or any other visual tool
- ❌ **DO NOT**: Use `dripage screenshot` after vision/locate

**Why**: 
- Vision/locate results already contain complete visual information
- `read` and `look_at` are DeepAgents general tools, not part of dripage
- They consume additional tokens without adding value
- They are redundant when vision/locate already provided analysis

**Violation Example**:
```bash
# ❌ WRONG - Redundant tool calls
dripage vision --query "Verify layout"
read output/data/vision_xxx.png  # Redundant
look_at output/data/vision_xxx.png  # Redundant

# ✅ CORRECT - Stop at vision result
dripage vision --query "Verify layout"
# Done. Report result to user.
```

### Rule 3: NEVER Combine Visual Tools

**Use single-command flow for visual analysis**:

```bash
# ❌ WRONG - Two commands, redundant
dripage screenshot
dripage vision --image output/data/screenshot_xxx.png --query "Describe page"

# ✅ CORRECT - Single command (in-memory)
dripage vision --query "Describe page"
```

### Rule 4: NEVER Use Generic Bash for Dripage Tasks

For any dripage-related operation:
- ✅ **MUST use**: `Bash(dripage:*)` namespace
- ❌ **NEVER use**: Generic `Bash` tool

**Why**: `allowed-tools` field enforces dripage namespace. Generic bash bypasses this restriction.

---

## Core Commands

### Browser & Tab
```bash
dripage browser start              # Uses current config automatically
dripage browser start --name browser1  # Specific browser
dripage browser stop               # Uses current config automatically
dripage browser status             # Shows current browser with ★ marker

dripage tab new --url <URL>
dripage tab list
dripage tab close
```

**Important**: `browser start` does NOT accept `--url`. Use `tab new` instead.

### Page Operations
```bash
dripage screenshot              # Capture screenshot (manual save)
dripage get [URL] [--tab-id ID]  # Get page content (Markdown)
dripage vision --query "问题"  # ★ In-memory analysis (PREFERRED)
dripage locate --query "搜索按钮" # ★ In-memory location (PREFERRED)
```

**Important**:
- `vision` and `locate` default to **in-memory mode** (no file save, faster)
- Use `--save-file` only for debugging
- Use `--image` only for retrospective analysis of existing images
- `get` command auto-saves long content: If content > 3000 chars, automatically saves to file and shows absolute path
- Use `--tab-id` to operate on specific tab (supports index or tab_id string)

### Element Location (In-Memory by Default)

**Use `locate` to find elements on the page using visual analysis.**

```bash
# Locate element (in-memory by default, no file save)
dripage locate --query "搜索输入框"

# Locate and click (in-memory by default)
dripage locate --query "搜索按钮" --click

# Locate in specific tab
dripage tab locate "提交按钮" --tab-id 0

# Locate and click in specific tab
dripage tab locate "保存按钮" --tab-id 0 --click
```

**Important**: 
- Default mode uses **in-memory screenshot** (no file I/O, faster)
- `locate` automatically captures, analyzes, and converts coordinates
- Use `--click` to automatically click the located element

### Vision Analysis (In-Memory by Default)

**Use `vision` for visual analysis.**

**DEFAULT MODE = IN-MEMORY (no file save, faster)**

```bash
# ★ PREFERRED: In-memory mode (default)
dripage vision --query "描述这个页面的布局"

# For debugging: Save screenshot to disk
dripage vision --query "检查布局是否正确" --save-file

# ONLY for debugging/retrospective: Analyze existing image
dripage vision --query "这个页面有什么问题？" --image /path/to/image.png
```

**STOP HERE**: After `vision` or `locate`, do NOT call any other visual tools.

### Interaction & Network
```bash
dripage action click <x> <y>
dripage action input <x> <y> <text>
dripage action scroll [down|up]

dripage capture start --mimeType application/json
dripage capture stop
dripage capture query
```

---

## Recommended Workflow: Multi-Browser Concurrency

### Example: 3 Concurrent Tasks with Different Browsers

```bash
# Terminal 1 - Crawler Production (browser1)
cd /path/to/crawler_prod
# .dripage/config: browser: browser1

dripage browser start          # Starts browser1
dripage tab new --url http://target1.com
dripage vision --query "分析页面结构"
dripage locate --query "数据提取按钮" --click

# Terminal 2 - Scraper Amazon (browser2) - CONCURRENT
cd /path/to/scraper_amazon
# .dripage/config: browser: browser2

dripage browser start          # Starts browser2
dripage tab new --url http://amazon.com
dripage vision --query "检查价格显示"
dripage locate --query "购买按钮" --click

# Terminal 3 - Test Runner (browser3) - CONCURRENT
cd /path/to/test_runner
# .dripage/config: browser: browser3

dripage browser start          # Starts browser3
dripage tab new --url http://localhost:3000
dripage vision --query "验证测试结果"
```

**Key Points**:
- Each terminal operates independently
- No interference between browsers
- Automatic browser selection from config
- All operations use in-memory mode by default

---

## Recommended Workflow: Verify Frontend (Single Browser)

```bash
# 1. Check current configuration
dripage config show
# Output: Current browser: browser2

# 2. Start browser (auto-uses browser2)
dripage browser start

# 3. Open page
dripage tab new --url http://localhost:3000

# 4. ★ Analyze visually (IN-MEMORY, single command)
dripage vision --query "验证页面布局和内容"

# OR locate elements (IN-MEMORY)
dripage locate --query "搜索输入框"

# OR locate and click (IN-MEMORY)
dripage locate --query "搜索按钮" --click

# ❌ DO NOT proceed with any of these:
# - read output/data/screenshot_xxx.png
# - look_at output/data/vision_xxx.png
# - dripage screenshot (vision already captured in-memory)
# - Any other visual tool

# ✅ INSTEAD: Report analysis result directly to user
```

---

## Common Errors

| Wrong | Right | Why |
|-------|-------|-----|
| `dripage browser start --url http://...` | `dripage browser start` + `dripage tab new --url http://...` | `start` doesn't support `--url` |
| `dripage tab new http://...` | `dripage tab new --url http://...` | Must use `--url` flag |
| `dripage screenshot` + `dripage vision --image screenshot.png` | `dripage vision --query "问题"` | Vision automatically captures in-memory, redundant |
| `dripage screenshot` + `dripage locate --query "按钮"` | `dripage locate --query "按钮"` | Locate uses in-memory screenshot by default |
| `read screenshot.png` | `dripage vision --query "问题"` | Vision already analyzed, read is redundant |
| `look_at screenshot.png` | `dripage vision --query "问题"` | Vision already analyzed, look_at is redundant |

---

## Quick Reference

| Task | Command |
|------|---------|
| Show current config | `dripage config show` |
| Start browser (auto) | `dripage browser start` |
| Start browser (specific) | `dripage browser start --name browser2` |
| View status | `dripage browser status` |
| Open page | `dripage tab new --url <URL>` |
| Vision analyze (in-memory) | `dripage vision --query "<问题>"` |
| Locate element (in-memory) | `dripage locate --query "<元素描述>"` |
| Locate and click | `dripage locate --query "<元素描述>" --click` |
| Get content | `dripage get [URL]` |
| Help | `dripage --help` |

---

## Output Paths

- **Screenshots** (manual): `output/data/screenshot_*.png`
- **Vision screenshots** (with `--save-file`): `output/data/vision_*.png`
- **Page data**: `output/data/page_data/`
- **Network capture**: `output/network_capture/`

**Note**: Vision and locate operations are in-memory by default and do not create files unless `--save-file` is used.
