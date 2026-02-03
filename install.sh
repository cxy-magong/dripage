#!/bin/bash
# Dripage 全局命令安装脚本
# 适用于 Git Bash、WSL、Linux、macOS

set -e

DRIPAGE_HOME="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.local/bin"

# 创建目标目录
if [ ! -d "$TARGET_DIR" ]; then
    echo "创建目标目录: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

# 创建 Bash/Unix shell 包装脚本
WRAPPER="$TARGET_DIR/dripage"

cat > "$WRAPPER" << EOF
#!/bin/bash
DRIPAGE_HOME="$DRIPAGE_HOME"
"\$DRIPAGE_HOME/.venv/Scripts/python.exe" "\$DRIPAGE_HOME/cli.py" "\$@"
EOF

chmod +x "$WRAPPER"

# 创建 Windows CMD 包装脚本（用于 Windows 原生终端）
WRAPPER_CMD="$TARGET_DIR/dripage.cmd"

cat > "$WRAPPER_CMD" << EOF
@echo off
setlocal
set "DRIPAGE_HOME=$DRIPAGE_HOME"
"%DRIPAGE_HOME%\\.venv\\Scripts\\python.exe" "%DRIPAGE_HOME%\\cli.py" %%*
endlocal
EOF

# 创建 Windows BAT 包装脚本
WRAPPER_BAT="$TARGET_DIR/dripage.bat"

cat > "$WRAPPER_BAT" << EOF
@echo off
setlocal
set "DRIPAGE_HOME=$DRIPAGE_HOME"
"%DRIPAGE_HOME%\\.venv\\Scripts\\python.exe" "%DRIPAGE_HOME%\\cli.py" %%*
endlocal
EOF

echo ""
echo "========================================"
echo "  安装成功！"
echo "========================================"
echo ""
echo "已创建包装脚本："
echo "  Bash/Unix: $WRAPPER"
echo "  CMD:       $WRAPPER_CMD"
echo "  BAT:       $WRAPPER_BAT"
echo ""
echo "验证安装："
echo "  dripage --help"
echo ""
echo "示例命令："
echo "  dripage browser start --name browser1"
echo "  dripage browser status"
echo ""
echo "卸载方法："
echo "  rm $WRAPPER"
echo "  rm $WRAPPER_CMD"
echo "  rm $WRAPPER_BAT"
echo "========================================"
echo ""
