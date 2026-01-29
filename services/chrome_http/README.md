# Chrome Manager HTTP API

基于 FastAPI 的 RESTful API 服务来管理 Chrome 浏览器实例。

## ⚠️ 端口问题

**Windows 上端口 8000/8001 可能被占用。**

如果遇到绑定错误：
```
ERROR: [Errno 13] error while attempting to bind on address ('0.0.0.0', 8000):
[winerror 10013] 以一种访问权限不允许的方式做了一个访问套接字的尝试。
```

**解决方案：** 使用不同的端口，例如 8888

```bash
uv run python services/chrome_http/server.py --port 8888
```

---

## 快速开始

### 启动 HTTP API Server

```bash
# 默认端口 8000（可能失败）
uv run python services/chrome_http/server.py

# 使用端口 8888（推荐）
uv run python services/chrome_http/server.py --port 8888
```

服务器将监听 `http://0.0.0.0:<port>`

### 访问 API 文档

打开浏览器访问：
```
http://localhost:<port>/docs
```

## API 端点

### 1. 健康检查

```
GET /health
```

响应：
```json
{
  "status": "ok",
  "service": "chrome-manager-api"
}
```

### 2. 启动浏览器

```
POST /api/browser/start
Content-Type: application/json

{
  "name": "browser1",
  "address": "127.0.0.1:19222",
  "user_data_dir": "",
  "browser_path": ""
}
```

响应：
```json
{
  "success": true,
  "message": "Browser 'browser1' started successfully",
  "data": {
    "name": "browser1",
    "cdp_url": "ws://127.0.0.1:19222/devtools/browser/...",
    "address": "127.0.0.1:19222",
    "pid": 12345
  }
}
```

### 3. 停止浏览器

```
POST /api/browser/stop
Content-Type: application/json

{
  "name": "browser1"
}
```

响应：
```json
{
  "success": true,
  "message": "Browser 'browser1' stopped successfully",
  "data": {
    "name": "browser1"
  }
}
```

### 4. 获取浏览器状态

获取所有浏览器：
```
GET /api/browser/status
```

获取特定浏览器：
```
GET /api/browser/status?name=browser1
```

响应：
```json
{
  "success": true,
  "message": "All browsers status retrieved",
  "data": {
    "browsers": {
      "browser1": {
        "status": "running",
        "cdp_url": "ws://...",
        "address": "127.0.0.1:19222",
        "pid": 12345
      }
    },
    "total": 1,
    "running": 1
  }
}
```

### 5. 获取 CDP URL

获取默认浏览器：
```
GET /api/browser/cdp
```

获取特定浏览器：
```
GET /api/browser/cdp?name=browser1
```

响应：
```json
{
  "success": true,
  "message": "CDP URL retrieved for 'browser1'",
  "data": {
    "name": "browser1",
    "cdp_url": "ws://127.0.0.1:19222/devtools/browser/..."
  }
}
```

### 6. 加载浏览器配置

```
GET /api/browser/config/{name}
```

响应：
```json
{
  "success": true,
  "data": {
    "name": "browser1",
    "ini_file": "...",
    "description": "..."
  }
}
```

## 使用 Python 客户端

```python
from services.chrome_http.client import ChromeManagerHTTPClient

# 创建客户端
client = ChromeManagerHTTPClient(host="localhost", port=8000)

# 启动浏览器
result = client.start_browser(name="browser1")
print(result)

# 获取状态
result = client.get_status()
print(result)

# 获取 CDP URL
result = client.get_cdp_url(name="browser1")
print(result)

# 停止浏览器
result = client.stop_browser(name="browser1")
print(result)

# 关闭客户端
client.close()
```

## 使用 curl 测试

### 健康检查
```bash
curl http://localhost:8000/health
```

### 启动浏览器
```bash
curl -X POST http://localhost:8000/api/browser/start \
  -H "Content-Type: application/json" \
  -d '{"name": "browser1"}'
```

### 获取状态
```bash
curl http://localhost:8000/api/browser/status
```

### 获取 CDP URL
```bash
curl http://localhost:8000/api/browser/cdp?name=browser1
```

### 停止浏览器
```bash
curl -X POST http://localhost:8000/api/browser/stop \
  -H "Content-Type: application/json" \
  -d '{"name": "browser1"}'
```

## 运行完整测试

```bash
uv run python services/chrome_http/test_api.py
```

## 对比三种管理方式

| 方式 | 协议 | 命令 | 优点 |
|------|--------|------|------|
| **命令行** | CLI | `python -m utils.chrome_manager` | 直接、无需服务 |
| **RPC** | Pyro4 | `uv run chrome-rpc-server` | 高性能、Python 原生 |
| **HTTP** | REST | `uv run chrome-http-server` | 跨语言、易集成、有文档 |

## 日志

所有 API 操作日志记录在 `output/log/chrome_http_server.log`

查看日志：
```bash
tail -f output/log/chrome_http_server.log
```
