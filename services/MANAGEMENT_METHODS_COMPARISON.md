# 三种浏览器管理方式总结

实现了三种不同的方式来管理 Chrome 浏览器实例。

---

## 1. 命令行管理 (CLI)

### 启动方式

直接使用 Python 模块：

```bash
python -m utils.chrome_manager start --name browser1
python -m utils.chrome_manager stop --name browser1
python -m utils.chrome_manager status --name browser1
python -m utils.chrome_manager get-cdp --name browser1
```

### 特点

✅ **优点：**
- 无需启动服务
- 直接执行
- 简单快速

❌ **缺点：**
- 仅本地使用
- 不支持远程调用
- 无自动重连

---

## 2. RPC 管理 (Pyro4)

### 启动方式

**启动 RPC Server：**
```bash
uv run chrome-rpc-server
```

**使用交互式 Client：**
```bash
uv run chrome-rpc-client --host pc.lan
```

**命令：**
```
chrome-rpc> start browser1
chrome-rpc> status
chrome-rpc> stop browser1
chrome-rpc> exit
```

### 特点

✅ **优点：**
- Python 原生 RPC
- 高性能（二进制序列化）
- 支持远程调用
- 交互式 REPL

❌ **缺点：**
- 需要客户端和服务器都是 Python
- 跨语言支持有限
- 需要单独的服务进程

---

## 3. HTTP API 管理 (REST)

### 启动方式

**启动 HTTP API Server：**
```bash
uv run chrome-http-server
```

**API 文档：**
```
http://localhost:8000/docs
```

**使用 curl：**
```bash
# 健康检查
curl http://localhost:8000/health

# 启动浏览器
curl -X POST http://localhost:8000/api/browser/start \
  -H "Content-Type: application/json" \
  -d '{"name": "browser1"}'

# 获取状态
curl http://localhost:8000/api/browser/status

# 停止浏览器
curl -X POST http://localhost:8000/api/browser/stop \
  -H "Content-Type: application/json" \
  -d '{"name": "browser1"}'
```

**使用 Python 客户端：**
```python
from services.chrome_http.client import ChromeManagerHTTPClient

client = ChromeManagerHTTPClient(host="localhost", port=8000)
client.start_browser(name="browser1")
client.stop_browser(name="browser1")
client.close()
```

### 特点

✅ **优点：**
- 跨语言支持（任何语言都可以调用）
- 标准的 RESTful API
- 自动生成 API 文档
- 易于集成到其他系统
- 使用标准 HTTP 客户端库
- 支持认证和授权（可扩展）

❌ **缺点：**
- 性能略低于 RPC（文本协议）
- 需要服务进程

---

## 对比总结

| 特性 | CLI | RPC | HTTP |
|------|-----|-----|------|
| **协议** | 直接调用 | Pyro4 | HTTP/REST |
| **远程支持** | ❌ | ✅ | ✅ |
| **跨语言** | ❌ | ❌ | ✅ |
| **性能** | 最高 | 高 | 中 |
| **API 文档** | 命令行帮助 | ❌ | ✅ (Swagger/OpenAPI) |
| **交互式** | ❌ | ✅ (REPL) | ✅ (任何 HTTP 客户端) |
| **集成难度** | 简单 | 中等 | 简单 |
| **所需进程** | 无 | 1 (Server) | 1 (Server) |
| **日志记录** | ✅ | ✅ | ✅ |

---

## 使用场景建议

### 场景 1: 本地快速操作
**推荐：** CLI

```bash
python -m utils.chrome_manager start --name browser1
```

### 场景 2: Python 应用集成
**推荐：** RPC

```python
from services.chrome_rpc.client import ChromeManagerClient
client = ChromeManagerClient(host="localhost", port=9090)
client.start_browser(name="browser1")
```

### 场景 3: 跨语言集成 / Web 应用
**推荐：** HTTP API

```bash
# JavaScript/前端
fetch('/api/browser/start', {
  method: 'POST',
  body: JSON.stringify({name: 'browser1'})
})

# Go/后端
resp, _ := http.Post("http://localhost:8000/api/browser/start", "application/json", payload)
```

### 场景 4: 远程管理 (Python)
**推荐：** RPC

```bash
# 本地
uv run chrome-rpc-server

# 远程 (sv-v2)
ssh sv-v2
cd ~/code/agent-use/dripage
uv run chrome-rpc-client --host pc.lan
```

### 场景 5: 远程管理 (任意语言)
**推荐：** HTTP API

```bash
# 本地
uv run chrome-http-server

# 远程
curl -X POST http://pc.lan:8000/api/browser/start \
  -H "Content-Type: application/json" \
  -d '{"name": "browser1"}'
```

---

## API 端点对比

| 操作 | CLI | RPC | HTTP |
|------|-----|-----|------|
| 启动浏览器 | `start --name` | `start_browser()` | `POST /api/browser/start` |
| 停止浏览器 | `stop --name` | `stop_browser()` | `POST /api/browser/stop` |
| 获取状态 | `status` | `get_status()` | `GET /api/browser/status` |
| 获取 CDP URL | `get-cdp --name` | `get_cdp_url()` | `GET /api/browser/cdp` |
| 加载配置 | - | `load_browser_config()` | `GET /api/browser/config/{name}` |
| 健康检查 | - | - | `GET /health` |

---

## 测试状态

### CLI 测试
```bash
python -m utils.chrome_manager status --name browser1
```
✅ 通过

### RPC 测试
```bash
uv run services/chrome_rpc/simple_test.py
```
✅ 所有测试通过

### HTTP API 测试
```bash
uv run python services/chrome_http/integration_test.py
```
✅ 所有测试通过（7/7）

---

## 文件结构

```
services/
├── chrome_rpc/           # RPC 服务
│   ├── server.py          # RPC 服务器
│   ├── client.py          # RPC 客户端
│   ├── interactive_client.py # 交互式 REPL 客户端
│   └── test_rpc.py       # 测试脚本
│
└── chrome_http/           # HTTP API 服务
    ├── server.py          # FastAPI 服务器
    ├── client.py          # Python HTTP 客户端
    ├── test_api.py       # 测试脚本
    └── integration_test.py # 集成测试
```

---

## Git 提交

```
f010b68 feat: 实现 ChromeManager HTTP API 服务
```

---

## 下一步

可能的扩展方向：

1. **HTTP API 增强**
   - 添加 JWT 认证
   - 添加 WebSocket 实时通知
   - 添加速率限制

2. **RPC 增强**
   - 添加 SSL/TLS 加密
   - 添加访问控制列表
   - 添加连接池优化

3. **通用增强**
   - 添加 Web UI 前端
   - 添加 Prometheus 监控
   - 添加 Docker 部署配置
