# 简单使用指南

## 启动 RPC Server

```bash
uv run chrome-rpc-server
```

## 使用交互式 Client

```bash
uv run chrome-rpc-client --host pc.lan
```

然后输入命令：

```
chrome-rpc> help
chrome-rpc> start browser1
chrome-rpc> status
chrome-rpc> stop browser1
chrome-rpc> exit
```

## 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `start <name>` | 启动浏览器 | `start browser1` |
| `stop <name>` | 停止浏览器 | `stop browser1` |
| `status` | 获取所有状态 | `status` |
| `status <name>` | 获取指定状态 | `status browser1` |
| `cdp <name>` | 获取 CDP URL | `cdp browser1` |
| `config <name>` | 加载配置 | `config browser1` |
| `help` | 显示帮助 | `help` |
| `exit` | 退出 | `exit` |

## 示例

本地启动 Server：
```bash
uv run chrome-rpc-server
```

远程连接 Client：
```bash
ssh sv-v2
cd ~/code/agent-use/dripage
uv run chrome-rpc-client --host pc.lan
```

就这么简单。
