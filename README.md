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

## 快速开始 (CLI)

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
