# Dripage CLI 全局命令

## 快速安装

### Windows / Git Bash / WSL / Linux / macOS

```bash
cd G:\code\agent-use\dripage
chmod +x install.sh
./install.sh
```

或使用 Windows CMD：
```cmd
cd G:\code\agent-use\dripage
install.cmd
```

## 使用方式

安装后，可以在任何位置直接使用 `dripage` 命令：

```bash
# 查看帮助
dripage --help

# 浏览器管理
dripage browser start --name browser1
dripage browser status
dripage browser stop

# 网络抓包
dripage capture start
dripage capture stop
dripage capture query

# 页面操作
dripage page get https://example.com
dripage page screenshot
dripage page vision "这是什么页面？"

# 元素交互
dripage action click 100 200
dripage action input 500 300 --text "hello"
dripage action scroll down 500

# 配置管理
dripage config list
dripage config set my-session
dripage config use my-session

# 标签页管理
dripage tab list
dripage tab new --url https://example.com
dripage tab close
```

## 安装位置

命令会安装到标准的用户级命令目录：
- **Windows/Linux/macOS**: `~/.local/bin/`

创建的文件：
- `~/.local/bin/dripage` - Bash/Unix shell 脚本
- `~/.local/bin/dripage.cmd` - Windows CMD 包装器
- `~/.local/bin/dripage.bat` - Windows BAT 包装器

## 原理

包装脚本会自动调用项目的虚拟环境：
```bash
~/.local/bin/dripage browser start
    ↓ 调用
G:\code\agent-use\dripage\.venv\Scripts\python.exe G:\code\agent-use\dripage\cli.py browser start
```

## 卸载

```bash
rm ~/.local/bin/dripage
rm ~/.local/bin/dripage.cmd
rm ~/.local/bin/dripage.bat
```

或 Windows CMD：
```cmd
del %USERPROFILE%\.local\bin\dripage
del %USERPROFILE%\.local\bin\dripage.cmd
del %USERPROFILE%\.local\bin\dripage.bat
```

## 注意事项

1. **代码修改即时生效**：包装脚本直接调用 `cli.py`，修改代码后无需重新安装
2. **使用项目依赖**：自动使用项目虚拟环境 `.venv` 中的依赖版本
3. **项目路径变更**：如果更改项目路径，需要重新运行安装脚本
4. **PATH 配置**：确保 `~/.local/bin` 在你的 PATH 中（大多数环境已默认包含）

## 故障排查

### 找不到 dripage 命令？

检查 PATH 是否包含 `~/.local/bin`：
```bash
echo $PATH | grep -o "[^:]*\.local/bin"
```

如果没有，添加到你的 shell 配置文件：
```bash
# ~/.bashrc 或 ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### Windows CMD 中找不到命令？

Windows CMD 需要使用 `.cmd` 或 `.bat` 后缀：
```cmd
dripage.cmd --help
```

或添加到用户 PATH：
```cmd
setx PATH "%PATH%;%USERPROFILE%\.local\bin"
```

## 目录结构

```
~/.local/bin/
├── dripage       # Bash/Unix 脚本（可执行）
├── dripage.cmd   # Windows CMD 包装器
└── dripage.bat   # Windows BAT 包装器
```

安装脚本会根据你的系统环境创建相应的包装器，确保在各种终端中都能正常工作。
