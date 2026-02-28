# 网络数据包监听工具使用指南

## 概述

Dripage MCP Server 现已集成网络数据包监听功能，基于 Chrome DevTools Protocol (CDP) 实现。可以监听网页的所有 HTTP 响应，包括 AJAX、Fetch、WebSocket 等各种类型的请求。

## 可用工具

### 1. `network_start_listener_tool` - 启动网络监听

启动对指定标签页的网络数据包监听功能。

**参数：**
- `tab_id` (可选): 标签页标识符（None=当前标签页, int=索引, str=tab_id）
- `mimeType` (可选): 按 MIME 类型过滤响应（默认: "application/json"）
  - 常用类型：`text/html`, `application/json`, `image/jpeg`, `text/javascript` 等
- `url_include` (可选): 按 URL 子字符串过滤（默认: "." 匹配所有）
- `refresh` (可选): 启动监听后是否刷新页面（默认: False）

**返回：**
```json
{
  "status": "success",
  "message": "开启监听成功",
  "tab": {
    "tab_id": "xxx",
    "title": "页面标题",
    "url": "https://...",
    "index": 0,
    "is_current": true
  },
  "config": {
    "mimeType": "application/json",
    "url_include": ".",
    "refresh": false
  }
}
```

**使用示例：**
```python
# 监听所有 JSON 响应
network_start_listener_tool(mimeType="application/json")

# 监听 URL 包含 "api" 的所有响应
network_start_listener_tool(url_include="api")

# 监听 HTML 响应并刷新页面
network_start_listener_tool(mimeType="text/html", refresh=True)
```

---

### 2. `network_get_listener_data_tool` - 获取监听数据

获取所有已捕获的网络数据包。

**参数：** 无

**返回：**
```json
{
  "status": "success",
  "count": 5,
  "data": [
    {
      "event_name": "Network.responseReceived",
      "event_data": {
        "requestId": "...",
        "loaderId": "...",
        "timestamp": 234033.123807,
        "type": "Document",
        "response": {
          "url": "https://...",
          "status": 200,
          "statusText": "OK",
          "mimeType": "application/json",
          "headers": {...},
          ...
        }
      }
    },
    ...
  ]
}
```

**使用示例：**
```python
# 获取所有捕获的响应
result = network_get_listener_data_tool()
```

---

### 3. `network_stop_listener_tool` - 停止监听

停止网络数据包监听功能。

**参数：**
- `tab_id` (可选): 标签页标识符
- `clear_data` (可选): 是否清空已收集的数据（默认: False）

**返回：**
```json
{
  "status": "success",
  "message": "监听网页发送的数据包关闭成功",
  "tab": {...},
  "data_cleared": true
}
```

**使用示例：**
```python
# 停止监听但不清空数据
network_stop_listener_tool()

# 停止监听并清空数据
network_stop_listener_tool(clear_data=True)
```

---

### 4. `network_clear_listener_data_tool` - 清空监听数据

清空所有已收集的网络监听数据（不停止监听）。

**参数：** 无

**返回：**
```json
{
  "status": "success",
  "message": "监听数据已清空"
}
```

**使用示例：**
```python
# 清空所有已收集的数据
network_clear_listener_data_tool()
```

---

## 完整使用流程

### 场景 1: 监听 API 响应

```python
# 1. 导航到目标网页
get(url="https://example.com")

# 2. 启动监听（监听所有 JSON 响应）
network_start_listener_tool(
    mimeType="application/json",
    url_include="api"
)

# 3. 执行触发 API 请求的操作（如点击按钮、输入表单等）
browser_click_tool(x=100, y=200)

# 4. 获取捕获的 API 响应
api_responses = network_get_listener_data_tool()
print(f"捕获到 {api_responses['count']} 个 API 响应")

# 5. 停止监听
network_stop_listener_tool(clear_data=True)
```

### 场景 2: 监听页面加载的资源

```python
# 1. 启动监听（监听所有资源类型）
network_start_listener_tool()

# 2. 刷新页面触发所有资源加载
get(url="https://example.com")

# 3. 等待页面加载完成
wait(3)

# 4. 获取所有加载的资源
resources = network_get_listener_data_tool()

# 5. 分析资源类型
for item in resources['data']:
    event = item['event_data']
    url = event['response']['url']
    mime_type = event['response']['mimeType']
    status = event['response']['status']
    print(f"{url} - {mime_type} - {status}")

# 6. 清空数据
network_clear_listener_data_tool()
```

### 场景 3: 捕获特定 API 的响应内容

```python
# 1. 导航到网页
get(url="https://example.com/data-page")

# 2. 启动监听（只监听包含特定关键字的 API）
network_start_listener_tool(
    url_include="data-api",
    refresh=True
)

# 3. 获取捕获的数据
data = network_get_listener_data_tool()

# 4. 提取响应体
for item in data['data']:
    event = item['event_data']
    url = event['response']['url']
    request_id = event['requestId']

    # 获取响应体（需要使用 CDP）
    response_body = run_cdp('Network.getResponseBody', requestId=request_id)
    print(f"URL: {url}")
    print(f"Response Body: {response_body}")
```

---

## 注意事项

1. **监听范围**：监听功能仅对启用监听后发生的网络请求有效，之前的请求不会被捕获。

2. **响应体获取**：`responseReceived` 事件只包含响应头，不包含响应体。如果需要获取响应体，需要使用 `run_cdp('Network.getResponseBody')`。

3. **多标签页**：每个标签页需要单独启动监听，监听数据是全局共享的。

4. **内存管理**：长时间运行可能会累积大量数据，建议定期使用 `clear_data=True` 或 `network_clear_listener_data_tool` 清空数据。

5. **性能影响**：启用监听会对浏览器性能有轻微影响，不需要时应及时停止监听。

---

## 技术实现

- **Chrome DevTools Protocol (CDP)**: 使用 `Network.enable`、`Network.responseReceived` 事件
- **DrissionPage**: 封装的 CDP 调用方法 `run_cdp()` 和 `driver.set_callback()`
- **数据存储**: 全局列表 `response_listener_data` 存储所有捕获的响应

---

## 测试

运行测试脚本验证功能：

```bash
# 测试基础功能
uv run test/test_network_listener.py

# 测试 MCP 集成
uv run test/test_mcp_network_listener.py
```
