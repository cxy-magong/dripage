# Chrome Manager HTTP API - 快速使用

## 启动服务器

```bash
uv run start_chrome_http.py
```

服务器将监听 `http://localhost:8889`

## 测试

### 健康检查

```bash
curl http://localhost:8889/health
```

### 启动浏览器

```bash
curl -X POST http://localhost:8889/api/browser/start \
  -H "Content-Type: application/json" \
  -d '{"name": "browser1"}'
```

### 获取状态

```bash
curl http://localhost:8889/api/browser/status
```

### 停止浏览器

```bash
curl -X POST http://localhost:8889/api/browser/stop \
  -H "Content-Type: application/json" \
  -d '{"name": "browser1"}'
```

## Python 客户端使用

```python
from services.chrome_http.client import ChromeManagerHTTPClient

client = ChromeManagerHTTPClient(host="localhost", port=8889)

# 启动浏览器
client.start_browser(name="browser1")

# 获取状态
client.get_status()

# 停止浏览器
client.stop_browser(name="browser1")

# 关闭连接
client.close()
```

## API 文档

打开浏览器访问：http://localhost:8889/docs

## 日志

查看日志：
```bash
tail -f output/log/chrome_http_server.log
```
