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
allowed-tools:
  - Bash(dripage:*)
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

## Trigger When
- User mentions "dripage", "screenshot", "视觉查看"
- Needs to verify frontend UI or take screenshots
- Wants to analyze page content visually
- Testing local development servers

---

## Mandatory Rules (NEVER VIOLATE)

### Rule 1: NEVER Use `read` or `look_at` for Image Files

When analyzing screenshots or visual content:
- ✅ **MUST use**: `dripage vision --query "<question>"`
- ❌ **NEVER use**: `read <screenshot-path>`
- ❌ **NEVER use**: `look_at <image-path>`

**Reason**: `vision` already provides structured visual analysis. Using `read` or `look_at` is redundant and wastes tokens.

**Violation Example**:
```bash
# ❌ WRONG - Do NOT do this
dripage vision --query "Analyze page"
read output/data/screenshot_xxx.png

# ✅ CORRECT - This is the ONLY step needed
dripage vision --query "Analyze page"
```

### Rule 2: MUST Use Single-Command Flow for Visual Analysis

For visual verification:
- ✅ **MUST use**: `dripage vision --query "<question>"` (single command)
- ❌ **NEVER**: `dripage screenshot` + `dripage vision --image <path>` (two commands)

**Reason**: Default mode of `vision` automatically captures and analyzes. Separate screenshot command is redundant and creates unnecessary file I/O.

**Violation Example**:
```bash
# ❌ WRONG - Do NOT do this
dripage screenshot
dripage vision --image output/data/screenshot_xxx.png --query "Describe page"

# ✅ CORRECT - Single command
dripage vision --query "Describe page"
```

### Rule 3: NEVER Combine Visual Tools

Once `vision` is complete:
- ✅ **DO**: Report analysis result directly to user
- ❌ **DO NOT**: Call `read`, `look_at`, or any other visual tool
- ❌ **DO NOT**: Use `dripage screenshot` after vision

**Reason**: Vision result already contains complete visual information. Additional tools provide no value and consume unnecessary tokens.

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

### Rule 4: NEVER Use Generic Bash for Dripage Tasks

For any dripage-related operation:
- ✅ **MUST use**: `Bash(dripage:*)` namespace
- ❌ **NEVER use**: Generic `Bash` tool

**Why**: `allowed-tools` field enforces dripage namespace. Generic bash bypasses this restriction.

---

## Core Commands

### Browser & Tab
```bash
dripage browser start
dripage browser stop
dripage browser status

dripage tab new --url <URL>
dripage tab list
dripage tab close
```

**Important**: `browser start` does NOT accept `--url`. Use `tab new` instead.

### Page Operations
```bash
dripage screenshot              # Capture screenshot
dripage get [URL]             # Get page content (Markdown)
dripage vision --query "问题"  # ★ Analyze with vision model
```

### Vision Analysis (Priority)
**Use `vision` for visual analysis instead of reading images directly.**

```bash
# Fast mode (default, in-memory) - PREFERRED
dripage vision --query "描述这个页面的布局"

# With saved screenshot for debugging
dripage vision --query "检查布局是否正确" --save-file

# Analyze existing image (ONLY for debugging/retrospective analysis)
dripage vision --query "这个页面有什么问题？" --image /path/to/image.png
```

**STOP HERE**: After `vision`, do NOT call any other visual tools.

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

## Recommended Workflow: Verify Frontend

```bash
# 1. Start browser
dripage browser status
dripage browser start

# 2. Open page
dripage tab new --url http://localhost:3000

# 3. ★ Analyze visually (SINGLE command, STOP here)
dripage vision --query "验证页面布局和内容"

# ❌ DO NOT proceed with any of these:
# - read output/data/screenshot_xxx.png
# - look_at output/data/vision_xxx.png
# - dripage screenshot
# - Any other visual tool

# ✅ INSTEAD: Report vision analysis result to user
```

---

## Common Errors

| Wrong | Right | Why |
|-------|-------|-----|
| `dripage browser start --url http://...` | `dripage browser start` + `dripage tab new --url http://...` | `start` doesn't support `--url` |
| `dripage tab new http://...` | `dripage tab new --url http://...` | Must use `--url` flag |
| `read screenshot.png` | `dripage vision --query "问题"` | Use vision analysis, not read tool |
| `dripage screenshot` + `dripage vision --image screenshot.png` | `dripage vision --query "问题"` | Vision automatically captures, redundant screenshot |
| `look_at screenshot.png` | `dripage vision --query "问题"` | Vision already analyzed, look_at is redundant |

---

## Quick Reference

| Task | Command |
|------|---------|
| Start browser | `dripage browser start` |
| Open page | `dripage tab new --url <URL>` |
| Screenshot | `dripage screenshot` |
| Vision analyze | `dripage vision --query "<问题>"` |
| Get content | `dripage get [URL]` |
| Help | `dripage --help` |

---

## Output Paths

- **Screenshots**: `output/data/screenshot_*.png`
- **Vision screenshots** (with `--save-file`): `output/data/vision_*.png`
- **Page data**: `output/data/page_data/`
- **Network capture**: `output/network_capture/`
