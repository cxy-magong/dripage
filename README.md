# Dripage 🚀

[English](README_EN.md) | 简体中文

浏览器自动化工具，支持 CLI 命令行、MCP 服务器集成和视觉分析功能。

## 特性

- 🌐 **浏览器自动化**：通过 CLI 导航和交互网页
- 📄 **内容提取**：将网页保存为 Markdown、HTML、图片或 MHTML
- 👁️ **视觉分析**：使用 GLM-4V 视觉模型分析截图
- 🔍 **元素定位**：使用视觉和坐标查找定位元素
- 📡 **网络数据包捕获**：后台网络监控，支持过滤功能
- 🔌 **MCP 服务器**：支持 AI 代理的模型上下文协议集成

## 核心优势

与同类项目（如 Agent Browser Playwright 等浏览器框架）相比，Dripage 具有以下独特优势：

- 🖥️ **多浏览器管理**：支持通过命令行管理多个浏览器实例，灵活控制不同的浏览器会话
- 👁️ **视觉定位**：支持视觉定位网页元素，无需依赖传统的选择器
- 📋 **视觉获取 HTML**：支持通过视觉获得网页元素的 HTML 信息，便于通过 CSS 选择器定位元素
- 🎯 **人类模拟点击**：能像人类一样模拟点击操作，有效规避反爬检测

---

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone <repository-url>
cd dripage

# 安装依赖（需要 Python 3.13+）
uv sync

# 设置环境变量
cp .env.example .env
# 编辑 .env 并填入你的 API 密钥
```

### 全局安装（可选）

```bash
# Windows: 运行安装脚本
install.cmd

# Linux/Mac: 运行安装脚本
bash install.sh

# 安装后，可在任何位置直接使用 dripage 命令
dripage --help
```

### 2. 配置环境

编辑 `.env` 文件并添加所需的 API 密钥：

```bash
# 视觉分析必需
ZAI_API_KEY="your_zhipuai_api_key_here"
```

### 3. 🤖 与 AI 协作（OpenCode、Claude 等）🚀

安装好依赖和全局安装之后，就可以直接让 OpenCode 等 AI 工具帮你使用 Dripage 了！

#### 使用 OpenCode 对话

在 OpenCode 等支持 AI 对话的工具中，你可以直接要求使用 `dripage` 命令：

> "导航到 https://github.com 并截取屏幕截图"

> "找到搜索框并输入 'test'"

> "获取页面内容为 markdown"

> "分析这个页面有什么内容"

> "点击坐标 (100, 200) 处的按钮"

AI 会自动识别并执行相应的 `dripage` 命令，无需你手动输入复杂的命令行参数。

### 4. 启动浏览器

```bash
# 使用默认配置启动浏览器
uv run .\cli.py browser start

# 或使用自定义配置启动
uv run .\cli.py browser start --address 127.0.0.1:19222
```

### 5. 常用命令

```bash
# 导航到网页
uv run .\cli.py tab new --url https://example.com

# 获取页面内容为 markdown
uv run .\cli.py get

# 截取屏幕截图
uv run .\cli.py screenshot

# 使用视觉分析页面
uv run .\cli.py vision "这个页面上有什么？"

# 在坐标处点击
uv run .\cli.py click 100 200

# 列出标签页
uv run .\cli.py tab list

# 获取帮助
uv run .\cli.py --help
```

完整的 CLI 文档请参阅 [README_CLI.md](README_CLI.md)。

---

## 🖥️ 图形用户界面 (GUI) 🆕

Dripage 现在提供了可视化的浏览器管理 Dashboard，方便通过图形界面管理多个浏览器实例。

### ✨ 核心功能

- **🎨 完整中文界面**：Dashboard 风格的浏览器卡片显示
- **📡 实时状态监控**：自动刷新浏览器运行状态（每 2 秒）
- **🎯 一键操作**：启动、停止、激活浏览器窗口
- **⚙️ 配置文件管理**：
  - 复制配置文件绝对路径到剪贴板
  - 用默认编辑器打开配置文件
  - 支持相对路径和绝对路径混合配置
  - 跨平台支持（Windows/macOS/Linux）
- **🔄 自动刷新**：窗口激活时自动刷新浏览器状态
- **🛡️ 线程安全**：所有 UI 更新在主线程执行，避免崩溃

### 📸 界面预览

![Dripage GUI Dashboard](https://bk.cf.magong.site/ScreenShot_2026-02-28_164705_991.png)

### 🚀 快速使用

```bash
# 启动 GUI
python start_gui.py

# 或使用模块启动
python -m GUI.GUI_dashboard

# 使用调试模式启动
python start_gui.py --debug

# 查看帮助
python start_gui.py --help
```

### 🎛️ 功能按钮说明

- **[启动/停止]**：控制浏览器的运行状态
- **[激活]**：将浏览器窗口置顶激活
- **[复制路径]**：复制配置文件的绝对路径到剪贴板
- **[编辑配置]**：用系统默认编辑器打开配置文件

### 📚 相关文档

- [GUI 日志系统文档](GUI/README_LOGGING.md) - 详细的日志使用指南
- [多浏览器配置指南](docs/MULTI_BROWSER_IMPLEMENTATION.md) - 浏览器配置说明

### 1. 安装

```bash
# 克隆仓库
git clone <repository-url>
cd dripage

# 安装依赖（需要 Python 3.13+）
uv sync

# 设置环境变量
cp .env.example .env
# 编辑 .env 并填入你的 API 密钥
```

### 全局安装（可选）

```bash
# Windows: 运行安装脚本
install.cmd

# Linux/Mac: 运行安装脚本
bash install.sh

# 安装后，可在任何位置直接使用 dripage 命令
dripage --help
```

### 2. 配置环境

编辑 `.env` 文件并添加所需的 API 密钥：

```bash
# 视觉分析必需
ZAI_API_KEY="your_zhipuai_api_key_here"
```

### 3. 启动浏览器

```bash
# 使用默认配置启动浏览器
uv run .\cli.py browser start

# 或使用自定义配置启动
uv run .\cli.py browser start --address 127.0.0.1:19222
```

### 4. 常用命令

```bash
# 导航到网页
uv run .\cli.py tab new --url https://example.com

# 获取页面内容为 markdown
uv run .\cli.py get

# 截取屏幕截图
uv run .\cli.py screenshot

# 使用视觉分析页面
uv run .\cli.py vision "这个页面上有什么？"

# 在坐标处点击
uv run .\cli.py click 100 200

# 列出标签页
uv run .\cli.py tab list

# 获取帮助
uv run .\cli.py --help
```

### 5. 与 AI 协作（OpenCode、Claude 等）

使用 AI 代理时，可以直接要求使用 `dripage` CLI 命令：

> "导航到 https://github.com 并截取屏幕截图"

> "找到搜索框并输入 'test'"

> "获取页面内容为 markdown"

完整的 CLI 文档请参阅 [README_CLI.md](README_CLI.md)。

---

## MCP 服务器（可选）

### 快速开始

```bash
# 启动 MCP 服务器（HTTP 模式，用于测试）
uv run mcp_server.py http

# 或启动 MCP 服务器（STDIO 模式，用于生产）
uv run mcp_server.py
```

### 配置

编辑 `config/mcp_config.yaml` 来配置浏览器和视觉设置：

```yaml
browser:
  address: "127.0.0.1:19222"

vision:
  model: "glm-4v-flash"
  temperature: 0.7
  max_tokens: 1024
```

详细的 MCP 文档请参阅 [MCP_SERVER_README.md](MCP_SERVER_README.md)。

---

## 高级配置

### 浏览器管理

```bash
# 检查浏览器状态
uv run .\cli.py browser status

# 停止浏览器
uv run .\cli.py browser stop

# 获取 CDP URL
uv run .\cli.py browser cdp
```

### 标签页管理

```bash
# 列出所有标签页
uv run .\cli.py tab list

# 创建新标签页
uv run .\cli.py tab new --url https://example.com

# 切换到标签页（按索引）
uv run .\cli.py tab switch 0

# 关闭标签页
uv run .\cli.py tab close 0
```

### 网络数据包捕获

```bash
# 开始捕获 JSON 响应
uv run .\cli.py capture start --content-type application/json

# 查询捕获的数据包
uv run .\cli.py capture query --limit 10

# 停止捕获
uv run .\cli.py capture stop
```

---

## 文档

- [README_CLI.md](README_CLI.md) - 完整的 CLI 参考
- [MCP_SERVER_README.md](MCP_SERVER_README.md) - MCP 服务器文档
- [AGENTS.md](AGENTS.md) - 项目特定的编码指南
- [example/README.md](example/README.md) - 使用示例

---

## 环境要求

- Python 3.13+
- Chrome/Chromium 浏览器
- [DrissionPage](https://github.com/g1879/DrissionPage)
- FastMCP
- MarkItDown

## 许可证

MIT
