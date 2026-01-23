# Dripage CLI 使用文档

Dripage CLI 是一个基于 DrissionPage 的命令行工具，提供浏览器自动化和视觉分析功能。

## 功能特性

- **get2md**: 将网页 URL 转换为 Markdown 格式
- **screenshot**: 截取当前页面或指定元素的截图
- **vision**: 使用 GLM-4V 视觉模型分析网页内容

## 安装

### 1. 安装依赖

项目使用 `uv` 管理依赖，依赖已配置在 `pyproject.toml` 中：

```bash
uv sync
```

### 2. 环境变量配置

配置智谱 AI API 密钥（用于 vision 命令）：

**Windows PowerShell:**
```powershell
$env:ZAI_API_KEY="your_api_key_here"
```

**Windows CMD:**
```cmd
set ZAI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export ZAI_API_KEY="your_api_key_here"
```

或者直接在命令中通过 `--api-key` 参数传入。

## 使用方法

### 基本命令

```bash
# 查看帮助
python dripage.py --help

# 查看子命令帮助
python dripage.py <command> --help
```

## 命令详细说明

### 1. get2md - 网页转 Markdown

将指定 URL 的网页内容转换为 Markdown 格式。

#### 语法

```bash
python dripage.py get2md <URL> [--address ADDRESS]
```

#### 参数

- `URL`: 要转换的网页地址（必需）
- `--address`: 浏览器地址，默认 `127.0.0.1:19222`（可选）

#### 示例

```bash
# 基本使用
python dripage.py get2md https://www.example.com

# 指定浏览器地址
python dripage.py get2md https://www.example.com --address 127.0.0.1:19222
```

#### 输出

Markdown 格式的网页内容会直接输出到终端。

---

### 2. screenshot - 截图

截取浏览器当前页面或指定元素的截图，保存到 `output/images/` 目录。

#### 语法

```bash
python dripage.py screenshot [--id ID] [--address ADDRESS]
```

#### 参数

- `--id`: 要截取的元素 ID（可选，不指定则截取整个页面）
- `--address`: 浏览器地址，默认 `127.0.0.1:19222`（可选）

#### 示例

```bash
# 截取整个页面
python dripage.py screenshot

# 截取指定 ID 的元素
python dripage.py screenshot --id header

# 指定浏览器地址
python dripage.py screenshot --address 127.0.0.1:19222
```

#### 输出

截图文件保存在项目根目录的 `output/images/` 下，文件名格式：
- 整页截图: `screenshot_<timestamp>.png`
- 元素截图: `screenshot_<id>_<timestamp>.png`

---

### 3. vision - 视觉分析

使用智谱 GLM-4V 视觉模型分析网页或图片内容。

#### 语法

```bash
python dripage.py vision <QUERY> [--image PATH] [--model MODEL] [--api-key KEY] [--address ADDRESS]
```

#### 参数

- `QUERY`: 对图片的查询或问题（必需）
- `--image`: 图片文件路径（可选，不指定则截取当前页面）
- `--model`: 使用的模型，可选 `glm-4v`、`glm-4v-plus`、`glm-4v-flash`（默认：`glm-4v-flash`）
- `--api-key`: 智谱 AI API 密钥（可选，默认从环境变量 `ZAI_API_KEY` 读取）
- `--address`: 浏览器地址，默认 `127.0.0.1:19222`（可选）

#### 模型说明

| 模型 | 说明 | 特点 |
|------|------|------|
| `glm-4v` | 旗舰版 | 能力最强，响应较慢 |
| `glm-4v-plus` | 增强版 | 性能和速度平衡 |
| `glm-4v-flash` | 轻量高速版 | 速度快，完全免费（推荐） |

#### 示例

```bash
# 分析当前页面
python dripage.py vision "描述这个网页的主要内容"

# 分析指定图片
python dripage.py vision "这张图里有什么" --image path/to/image.png

# 使用不同模型
python dripage.py vision "分析图片" --model glm-4v

# 指定 API 密钥
python dripage.py vision "分析页面" --api-key your_api_key
```

#### 输出

视觉分析结果会直接输出到终端。

如果未指定 `--image` 参数，会自动截取当前浏览器页面并保存为临时文件：
`output/images/temp_vision_<timestamp>.png`

## 测试

项目包含 3 个测试脚本，位于 `test/` 目录：

```bash
# 测试 get2md 命令
python test/test_get2md.py

# 测试 screenshot 命令
python test/test_screenshot.py

# 测试 vision 命令（需要配置 ZAI_API_KEY）
python test/test_vision.py
```

或使用 uv 运行：

```bash
cd test
uv run python test_get2md.py
uv run python test_screenshot.py
uv run python test_vision.py
```

## 浏览器配置

### 默认配置

- **地址**: `127.0.0.1:19222`
- **浏览器**: Chrome（通过 DrissionPage 启动）

### 启动浏览器

浏览器会在首次调用命令时自动启动。确保端口 19222 未被占用。

如需修改浏览器地址，所有命令都支持 `--address` 参数。

## 输出目录

```
dripage/
└── output/
    └── images/
        ├── screenshot_*.png        # 截图文件
        └── temp_vision_*.png     # 临时视觉分析截图
```

## 常见问题

### Q: 如何获取智谱 AI API 密钥？

A: 访问 https://open.bigmodel.cn/ 注册账号，在控制台创建 API 密钥。

### Q: 为什么截图命令失败？

A: 确保：
1. 浏览器已正确启动
2. 端口 19222 可用
3. 如果使用 `--id` 参数，确保元素存在

### Q: vision 命令提示 API key 错误？

A: 检查：
1. 环境变量 `ZAI_API_KEY` 是否正确设置
2. 或使用 `--api-key` 参数直接传入密钥
3. 确认 API 密钥格式正确：`<id>.<secret>`

### Q: 如何指定其他浏览器地址？

A: 所有命令都支持 `--address` 参数：
```bash
python dripage.py screenshot --address 127.0.0.1:9222
```

## 技术栈

- **DrissionPage**: 浏览器自动化
- **Click**: 命令行框架
- **MarkItDown**: HTML 转 Markdown
- **ZhipuAI**: GLM-4V 视觉模型 API

## 依赖项

查看 `pyproject.toml` 获取完整依赖列表：
```toml
[project]
dependencies = [
    "click>=8.3.1",
    "drissionpage>=4.1.1.2",
    "loguru>=0.7.3",
    "markitdown>=0.1.4",
    "sniffio>=1.3.1",
    "zhipuai>=2.1.5.20250825",
]
```

## 项目结构

```
dripage/
├── cli.py                   # CLI 核心实现
├── dripage.py               # CLI 入口包装脚本
├── utils/                   # 工具模块
│   ├── __init__.py
│   ├── drission_page.py    # 浏览器创建函数
│   ├── chrome_manager.py
│   ├── stageh.py
│   └── logu.py
├── output/                  # 输出目录
│   └── images/            # 截图保存位置
├── test/                   # 测试脚本
│   ├── test_get2md.py
│   ├── test_screenshot.py
│   └── test_vision.py
└── pyproject.toml          # 项目配置
```

## 许可证

项目遵循原项目许可证。

## 相关链接

- [DrissionPage 文档](https://drissionpage.cn/)
- [智谱 AI 开放平台](https://open.bigmodel.cn/)
- [Click 文档](https://click.palletsprojects.com/)
- [MarkItDown 文档](https://github.com/microsoft/markitdown)
