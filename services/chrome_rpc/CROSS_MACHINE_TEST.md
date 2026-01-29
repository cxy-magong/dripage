# 跨机器 RPC 测试指南

## 网络配置

- **本地 (Server):** `192.168.2.37:9090` (Windows)
- **远程 (Client):** `sv-v2` (Linux)

## 步骤 1: 在本地启动 RPC Server

**在本地 Windows 机器上打开新的终端窗口：**

```bash
cd "G:\code\agent-use\dripage\worktrees\cdp-support"
uv run services/chrome_rpc/start_server.py --host 0.0.0.0 --port 9090
```

**预期输出：**
```
ChromeManager RPC Server started!
RPC URI: PYRO:ChromeManager@0.0.0.0:9090
Listening on: 0.0.0.0:9090

Waiting for client connections...
Press Ctrl+C to stop the server.
```

**⚠️ 保持这个终端窗口打开，不要关闭！**

## 步骤 2: 在远程服务器运行测试

**在本地另一个终端（SSH 连接到 sv-v2）：**

```bash
ssh sv-v2 "cd ~/code/agent-use/dripage && uv run services/chrome_rpc/test_remote_client.py --host 192.168.2.37 --port 9090"
```

## 步骤 3: 验证结果

**预期测试输出：**
```
======================================================================
  Chrome Manager RPC - Remote Client Test
  Server: 192.168.2.37:9090
======================================================================

🔌 Connecting to RPC server at 192.168.2.37:9090...
✅ Connected to RPC server

----------------------------------------------------------------------
Test 1: Get all browsers status
----------------------------------------------------------------------
{
  "success": true,
  "message": "All browsers status retrieved",
  "data": { ... }
}
✅ Test 1 PASSED: Retrieved status successfully

----------------------------------------------------------------------
Test 2: Start browser1 by name
----------------------------------------------------------------------
{
  "success": true,
  "message": "Browser 'browser1' started successfully",
  "data": { ... }
}
✅ Test 2 PASSED: browser1 started successfully

...

======================================================================
  🎉 ALL REMOTE RPC TESTS PASSED! 🎉
======================================================================

✅ Successfully connected to remote server: 192.168.2.37:9090
✅ Started and managed browsers remotely via RPC
✅ Retrieved CDP URLs from remote browser instances
```

## 故障排除

### 问题 1: 连接被拒绝

**错误:** `Connection refused` 或 `CommunicationError`

**检查：**
1. 本地 Server 是否正在运行？
   ```bash
   # 检查端口 9090 是否在监听
   netstat -ano | findstr 9090
   ```

2. 防火墙是否阻止？
   - Windows 防火墙：允许端口 9090 入站连接
   - 添加防火墙规则：
     ```powershell
     New-NetFirewallRule -DisplayName "Chrome RPC" -Direction Inbound -LocalPort 9090 -Protocol TCP -Action Allow
     ```

3. 网络是否可达？
   ```bash
   # 从远程服务器 ping 本地机器
   ssh sv-v2 "ping -c 4 192.168.2.37"
   ```

### 问题 2: 浏览器启动失败

**错误:** `Failed to start browser`

**检查：**
1. 浏览器配置文件是否存在？
   ```bash
   ssh sv-v2 "cd ~/code/agent-use/dripage && ls -la config/browser/"
   ```

2. 浏览器路径是否正确？
   ```bash
   ssh sv-v2 "cd ~/code/agent-use/dripage && cat config/browser/browser1.ini | head -20"
   ```

### 问题 3: Pyro4 错误

**错误:** `module 'pyro4' not found`

**解决：**
```bash
ssh sv-v2 "cd ~/code/agent-use/dripage && uv pip show pyro4"
```

如果没有安装，安装 Pyro4：
```bash
ssh sv-v2 "cd ~/code/agent-use/dripage && uv add pyro4"
```

## 手动测试步骤

如果自动化测试失败，可以手动测试：

### 在本地 Server 终端：

1. 启动服务器（保持运行）
2. 观察客户端连接日志

### 在远程服务器终端：

```bash
# 连接到本地服务器
ssh sv-v2

# 进入项目目录
cd ~/code/agent-use/dripage

# 测试连接
uv run python -c "from services.chrome_rpc.client import ChromeManagerClient; c = ChromeManagerClient(host='192.168.2.37', port=9090); print(c.get_status()); c.close()"
```

## 网络拓扑

```
┌─────────────────────┐         网络           ┌─────────────────────┐
│   本地 Windows     │ ◄──────────────► │   远程 Linux sv-v2  │
│  192.168.2.37     │   192.168.2.x   │  (客户端)          │
│  (RPC Server)      │                 │                    │
│                   │                 │                    │
│  - Browser1       │   RPC 调用      │  - Client          │
│  - Browser2       │ ◄──────────────► │  - 测试脚本        │
└─────────────────────┘                 └─────────────────────┘

浏览器在本地 Windows 机器上运行
测试脚本在远程 Linux 机器上通过 RPC 控制
```

## 成功标志

✅ 本地 Server 显示客户端连接
✅ 远程 Client 能够调用所有方法
✅ 浏览器在本地启动（远程控制）
✅ CDP URL 返回到远程客户端
✅ 远程客户端能够关闭本地浏览器

## 清理

测试完成后：

1. **停止本地 Server：** 在 Server 终端按 `Ctrl+C`
2. **清理浏览器：** 测试脚本会自动关闭所有浏览器
3. **检查状态：**
   ```bash
   ssh sv-v2 "cd ~/code/agent-use/dripage && uv run python -m utils.chrome_manager status"
   ```
