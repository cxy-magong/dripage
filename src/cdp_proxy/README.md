# CDP Proxy - Chrome DevTools Protocol Proxy

为外部访问本地Chrome DevTools Protocol (CDP)端口提供HTTP/WebSocket代理。

## 功能

- ✅ HTTP代理（用于CDP HTTP端点，如 `/json/version`）
- ✅ WebSocket代理（用于CDP WebSocket连接）
- ✅ 透明转发所有headers、cookies、查询参数
- ✅ 支持非标准端口
- ✅ 健康检查端点
- ✅ 配置灵活（命令行参数或环境变量）

## 安装

```bash
uv add fastapi-proxy-lib[standard]
```

## 使用

### 1. 启动代理服务器

#### 使用Python模块命令
```bash
# 默认配置（CDP端口19222，代理端口8080）
uv run python -m cdp_proxy.start_proxy

# 自定义配置
uv run python -m cdp_proxy.start_proxy --cdp-port 19222 --proxy-port 8080 --host 0.0.0.0

# 启用调试日志
uv run python -m cdp_proxy.start_proxy --log-level debug
```

#### 直接运行脚本
```bash
uv run src/cdp_proxy/server.py
```

### 2. 测试代理服务器

```bash
# 测试默认代理（localhost:8080）
uv run python -m cdp_proxy.test_proxy

# 测试指定代理
uv run python -m cdp_proxy.test_proxy --url http://localhost:8080

# 测试远程代理
uv run python -m cdp_proxy.test_proxy --url http://192.168.1.100:8080
```

### 3. 从外部连接CDP

启动Chrome并确保它监听CDP端口：
```bash
# 启动Chrome（使用DrissionPage）
uv run python -m utils.chrome_manager start
```

然后从外部机器连接到代理：

#### WebSocket连接（推荐用于Playwright、Puppeteer等）
```javascript
// JavaScript/TypeScript客户端示例
const ws = new WebSocket('ws://your-server-ip:8080/ws/devtools/browser/session-id');

ws.onopen = () => {
  console.log('CDP连接成功');

  // 发送CDP命令
  ws.send(JSON.stringify({
    id: 1,
    method: "Page.navigate",
    params: { url: "https://example.com" }
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('收到CDP响应:', message);
};
```

#### HTTP连接（用于CDP端点信息）
```bash
# 获取Chrome版本信息
curl http://your-server-ip:8080/json/version

# 获取CDP目标列表
curl http://your-server-ip:8080/json
```

## 配置选项

### 命令行参数

| 参数 | 默认值 | 说明 |
|------|---------|------|
| `--cdp-port` | 19222 | Chrome CDP调试端口 |
| `--proxy-port` | 8080 | 代理服务器端口 |
| `--host` | 0.0.0.0 | 监听地址（0.0.0.0允许外部访问） |
| `--log-level` | info | 日志级别（debug/info/warning/error） |
| `--keepalive-interval` | 20 | WebSocket ping间隔（秒） |
| `--keepalive-timeout` | 20 | WebSocket ping超时（秒） |

### 环境变量

| 变量 | 默认值 | 说明 |
|------|---------|------|
| `CDP_PORT` | 19222 | Chrome CDP调试端口 |
| `PROXY_PORT` | 8080 | 代理服务器端口 |
| `PROXY_HOST` | 0.0.0.0 | 监听地址 |
| `LOG_LEVEL` | info | 日志级别 |
| `KEEPALIVE_INTERVAL` | 20 | WebSocket ping间隔（秒） |
| `KEEPALIVE_TIMEOUT` | 20 | WebSocket ping超时（秒） |

## 防火墙配置

确保代理端口开放：

### Linux (Ubuntu/Debian)
```bash
# 允许8080端口
sudo ufw allow 8080/tcp

# 检查防火墙状态
sudo ufw status

# 或者使用iptables
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

### Windows
```powershell
# 在管理员PowerShell中运行
New-NetFirewallRule -DisplayName "CDP Proxy" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

### 检查端口监听
```bash
# Linux/Mac
netstat -tuln | grep 8080
# 或
ss -tuln | grep 8080

# Windows (PowerShell)
netstat -an | findstr 8080
```

## 测试验证

成功标准：通过代理访问到CDP

运行测试脚本会验证：
1. ✅ 健康检查端点
2. ✅ HTTP端点（/json/version）
3. ✅ CDP发现（/json）
4. ✅ WebSocket连接（/ws/devtools/browser/...）

如果所有测试通过，会看到：
```
🎉 成功！代理可以访问CDP

📡 您现在可以连接到:
   ws://your-ip:8080/ws/devtools/browser/...
```

## 工作流程

```
┌─────────────────────────────────────────────────────────┐
│          外部CDP客户端                     │
│   (Playwright, Puppeteer等)              │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│         CDP代理服务器 (8080)              │
│   - HTTP代理: / → localhost:19222/       │
│   - WebSocket代理: /ws/ → ws://...        │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│         Chrome浏览器 (19222)                │
│   - CDP WebSocket端点                   │
│   - DrissionPage控制                       │
└─────────────────────────────────────────────────────────┘
```

## 故障排查

### 代理启动失败
1. 检查端口8080是否被占用：
   ```bash
   netstat -tuln | grep 8080
   ```
2. 尝试使用其他端口：
   ```bash
   uv run python -m cdp_proxy.start_proxy --proxy-port 8081
   ```

### 无法连接到CDP
1. 确认Chrome浏览器已启动：
   ```bash
   uv run python -m utils.chrome_manager status
   ```
2. 检查Chrome监听CDP端口：
   ```bash
   netstat -tuln | grep 19222
   ```
3. 查看代理服务器日志
4. 确认防火墙规则

### 测试失败
1. 确认代理服务器运行
2. 确认CDP端口正确
3. 使用 `--log-level debug` 查看详细日志
4. 手动测试端点：
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8080/json/version
   ```

## 架构说明

本代理使用 `fastapi-proxy-lib` 实现：
- **HTTP代理**: 使用 `httpx` 库
- **WebSocket代理**: 使用 `httpx-ws` 库
- **Web框架**: FastAPI + Uvicorn
- **优势**: 生产就绪、类型安全、95%+测试覆盖率

## 许可证

MIT License
