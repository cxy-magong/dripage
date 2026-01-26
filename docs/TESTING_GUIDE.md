# 浏览器多标签管理工具测试指南

## ✅ 已完成的工作

### 1. 标签管理工具实现

在 `tools/browser_tabs.py` 中实现了完整的标签管理功能：

| 工具 | 功能 | 状态 |
|------|------|------|
| `list_tabs()` | 列出所有浏览器标签 | ✅ 完成 |
| `get_current_tab_info()` | 获取当前标签信息 | ✅ 完成 |
| `new_tab(url)` | 打开新标签（可选URL） | ✅ 完成 |
| `switch_tab(index)` | 切换到指定标签 | ✅ 完成 |
| `close_tab(index)` | 关闭指定标签 | ✅ 完成 |

### 2. MCP服务器进程管理改进

在 `mcp_manager.py` 中实现了基于 psutil 的改进管理：

**改进内容：**
- ✅ 完整的日志记录（启动、停止、状态检查）
- ✅ 端口监听检查（HTTP模式下验证端口是否打开）
- ✅ 子进程追踪（自动找到实际的 uvicorn 进程 PID）
- ✅ 更准确的健康检查（同时检查进程和端口）
- ✅ 优雅的进程终止（SIGTERM → 5秒 → SIGKILL）
- ✅ 详细的错误原因报告（僵尸进程、端口未监听等）

## 🧪 测试方法

### 方法 1: 直接 Python 调用（推荐用于测试）

```bash
PYTHONPATH="G:\code\agent-use\dripage" uv run test/test_tab_comprehensive.py
```

这个测试脚本会：
1. ✅ 初始化浏览器连接
2. ✅ 列出所有标签
3. ✅ 打开新标签
4. ✅ 获取当前标签信息
5. ✅ 切换标签
6. ✅ 关闭标签
7. ✅ 批量打开多个标签
8. ✅ 返回标准化的 JSON 格式

**所有测试都已通过！** ✅

### 方法 2: 通过 MCP 服务器调用（生产环境）

**启动 MCP 服务器：**
```bash
uv run mcp_manager.py start
```

**检查服务器状态：**
```bash
uv run mcp_manager.py status
```

**问题：mcporter 只能识别 13 个工具，但 MCP 服务器实际注册了 18 个工具。**

**可用的工具（通过 mcporter）：**
- ✅ `dripage.get` - 保存页面内容
- ✅ `dripage.browser_navigate_tool` - 导航到 URL
- ✅ `dripage.browser_get_current_page_tool` - 获取当前页面
- ✅ `dripage.browser_screenshot_tool` - 截图

**mcporter 识别不到的标签管理工具：**
- ❌ `dripage.browser_list_tabs_tool` - 列出所有标签
- ❌ `dripage.browser_switch_tab_tool` - 切换标签
- ❌ `dripage.browser_new_tab_tool` - 打开新标签
- ❌ `dripage.browser_close_tab_tool` - 关闭标签
- ❌ `dripage.browser_get_current_tab_info_tool` - 获取当前标签信息

## 🔍 问题诊断

### mcporter 识别不到标签管理工具的可能原因：

1. **缓存问题**：mcporter 可能缓存了工具列表
2. **工具发现机制**：mcporter 的工具发现可能有限制
3. **版本兼容性**：mcporter 0.7.3 可能与 FastMCP 不完全兼容

### 验证工具已注册：

```bash
PYTHONPATH="G:\code\agent-use\dripage" uv run python -c "
from mcp_server import mcp
print(f'总工具数: {len(mcp._tool_manager._tools)}')
print('\\n所有工具:')
for name in sorted(mcp._tool_manager._tools.keys()):
    print(f'  - {name}')
print('\\n标签管理工具:')
for name in sorted(mcp._tool_manager._tools.keys()):
    if 'tab' in name.lower():
        print(f'  - {name}')
"
```

输出应显示 18 个工具，包括 5 个标签管理工具。

## 📝 API 说明

### 工具调用格式（mcporter）

```bash
# 成功的工具
mcporter call --config config/mcporter-http.json dripage.get url:"https://example.com"

# 需要特殊字符的工具（mcporter 可能有问题）
mcporter call --config config/mcporter-http.json "dripage.get" url:"https://example.com"
```

### 直接 HTTP 调用（绕过 mcporter）

如果 mcporter 无法识别工具，可以直接使用 HTTP API：

```bash
# 获取当前标签信息
curl -X POST http://127.0.0.1:8000/mcp/tools/browser_get_current_tab_info_tool \
  -H "Content-Type: application/json" \
  -d '{}'

# 列出所有标签
curl -X POST http://127.0.0.1:8000/mcp/tools/browser_list_tabs_tool \
  -H "Content-Type: application/json" \
  -d '{}'

# 打开新标签
curl -X POST http://127.0.0.1:8000/mcp/tools/browser_new_tab_tool \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com"}'

# 切换标签
curl -X POST http://127.0.0.1:8000/mcp/tools/browser_switch_tab_tool \
  -H "Content-Type: application/json" \
  -d '{"tab_index": 0}'
```

## 🎯 测试结果

### ✅ 完全成功的测试（直接 Python 调用）

1. **list_tabs()** - 正确列出所有标签，包括索引、标题、URL
2. **get_current_tab_info()** - 正确获取当前标签信息
3. **new_tab(url)** - 成功打开新标签并导航到指定 URL
4. **new_tab()** - 成功打开空白标签
5. **switch_tab(index)** - 成功切换到指定标签
6. **close_tab(index)** - 成功关闭指定标签
7. **close_tab()** - 成功关闭当前标签
8. **批量操作** - 成功同时打开多个标签

### ⚠️ Mcporter 调用状态

- ❌ mcporter 0.7.3 只能识别 13/18 个工具
- ❌ 所有标签管理工具（`browser_*_tab_tool`）无法通过 mcporter 调用
- ✅ 基础浏览器工具（`get`, `browser_navigate_tool` 等）可以正常工作

## 💡 建议

### 立即可用的方法：

1. **使用直接 Python 调用**
   ```bash
   PYTHONPATH="G:\code\agent-use\dripage" uv run test/test_tab_comprehensive.py
   ```

2. **在 Python 代码中直接导入工具**
   ```python
   from tools.browser_tabs import list_tabs, new_tab, switch_tab, close_tab
   ```

3. **等待 mcporter 更新或使用替代方案**
   - 当前版本的 mcporter 可能有工具发现限制
   - 考虑使用 Claude Desktop/VSCode 直接连接 MCP
   - 考虑实现自定义 MCP 客户端

### 日志位置：

- **服务器日志**: `output/log/mcp_server_YYYYMMDD_HHMMSS.log`
- **管理器日志**: `output/log/mcp_manager_debug.log`
- **工具日志**: `output/log/browser_tools.log`

查看日志来诊断问题！

## 📊 DrissionPage API 使用说明

修复中发现的问题和正确用法：

```python
# ❌ 错误 - 浏览器对象没有 to_tab()
browser.to_tab(tab_index)

# ❌ 错误 - 标签对象没有 activate()
tab = browser.get_tabs()[tab_index]
tab.activate()

# ✅ 正确 - 浏览器对象有 activate_tab()
browser.activate_tab(tab_index)

# ✅ 正确 - 关闭当前标签
browser.get_tab().close()

# ✅ 正确 - 关闭指定标签
browser.activate_tab(tab_index)
browser.get_tab().close()
```

## 总结

✅ **标签管理功能已完全实现**
✅ **进程管理已改进（psutil + 日志）**
✅ **直接 Python 调用测试全部通过**
⚠️ **mcporter 工具发现存在问题（13/18 工具）**

**推荐使用方法 1（直接 Python 调用）进行开发和测试。**
