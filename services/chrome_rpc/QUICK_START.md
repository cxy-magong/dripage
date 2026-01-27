# 🚀 快速启动跨机器 RPC 测试

## 网络信息
- **本地 (Server):** pc.lan (192.168.2.37)
- **远程 (Client):** sv-v2.lan (100.64.0.32)
- **网络:** ✅ 已连通（ping 测试通过，延迟 1ms）

---

## 步骤 1: 启动本地 RPC Server

在 PowerShell 中运行：

```powershell
cd G:\code\agent-use\dripage\worktrees\cdp-support
.\services\chrome_rpc\start_server_background.ps1
```

**预期输出：**
```
=============================================
  Starting ChromeManager RPC Server
=============================================

Project: G:\code\agent-use\dripage\worktrees\cdp-support
Host: 0.0.0.0
Port: 9090
Log: rpc_server_20260128_050000.log

Server started!
Process ID: 12345

Waiting for server to initialize...
✅ Server is running!

You can now run remote client test:

  ssh sv-v2 "cd ~/code/agent-use/dripage && uv run services/chrome_rpc/test_remote_client.py --host sv-v2.lan --port 9090"

Monitor server log:
  Get-Content rpc_server_20260128_050000.log -Wait

Stop server:
  Stop-Process -Id 12345 -Force
```

**⚠️ 保持这个 PowerShell 窗口打开！**

---

## 步骤 2: 运行远程客户端测试

在新的 PowerShell 窗口（或 Git Bash）中运行：

```bash
ssh sv-v2 "cd ~/code/agent-use/dripage && uv run services/chrome_rpc/test_remote_client.py --host pc.lan --port 9090"
```

**预期输出：**
```
======================================================================
  Chrome Manager RPC - Remote Client Test
  Server: pc.lan:9090
======================================================================

🔌 Connecting to RPC server at pc.lan:9090...
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

... (继续测试) ...

======================================================================
  🎉 ALL REMOTE RPC TESTS PASSED! 🎉
======================================================================

✅ Successfully connected to remote server: pc.lan:9090
✅ Started and managed browsers remotely via RPC
✅ Retrieved CDP URLs from remote browser instances
```

---

## 步骤 3: 观察结果

### 在本地 Server 端：
你会看到客户端连接和每个 RPC 调用。

### 在远程 Client 端：
你会看到所有测试通过。

---

## 故障排除

### 问题: 执行策略阻止 PowerShell 脚本

**错误:** `execution of scripts is disabled on this system`

**解决:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 问题: Server 启动失败

**检查日志文件：**
```powershell
Get-Content rpc_server_*.log -Tail 50
```

### 问题: 远程连接失败

**测试连通性：**
```bash
ssh sv-v2 "ping -c 4 pc.lan"
```

**检查端口：**
```powershell
netstat -ano | findstr :9090
```

---

## 停止 Server

在启动 Server 的 PowerShell 窗口中：

```powershell
# 查看进程 ID
Get-Process python | Where-Object {$_.Path -like "*uv*"}

# 停止指定进程
Stop-Process -Id <进程ID> -Force
```

或者直接在 PowerShell 窗口按 `Ctrl+C`（如果前台运行）。

---

## 完整测试命令汇总

**终端 1 (PowerShell) - 本地 Server:**
```powershell
cd G:\code\agent-use\dripage\worktrees\cdp-support
.\services\chrome_rpc\start_server_background.ps1
```

**终端 2 (Git Bash/PowerShell) - 远程测试:**
```bash
ssh sv-v2 "cd ~/code/agent-use/dripage && uv run services/chrome_rpc/test_remote_client.py --host pc.lan --port 9090"
```

---

## 验证清单

测试完成后检查：

- [ ] 本地浏览器进程是否启动？
  ```powershell
  Get-Process chrome
  ```

- [ ] 远程测试是否显示 `ALL TESTS PASSED`？

- [ ] CDP URLs 是否返回？

- [ ] 浏览器是否正确关闭？

---

## 成功标志 🎉

```
✅ RPC Server 在本地 Windows 运行
✅ 远程 Linux 服务器连接成功
✅ 跨网络 RPC 调用正常
✅ 浏览器在本地启动（远程控制）
✅ 远程客户端获取到 CDP URL
✅ 远程客户端成功关闭本地浏览器
```
