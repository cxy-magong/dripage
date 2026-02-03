@echo off
REM Dripage 全局命令安装脚本（Windows）

setlocal

set "DRIPAGE_HOME=%~dp0"
set "DRIPAGE_HOME=%DRIPAGE_HOME:~0,-1%"

REM 用户级命令目录
set "TARGET_DIR=%USERPROFILE%\.local\bin"

REM 创建目标目录
if not exist "%TARGET_DIR%" (
    echo 创建目标目录: %TARGET_DIR%
    mkdir "%TARGET_DIR%"
)

REM 创建 Bash/Unix 包装脚本
set "WRAPPER=%TARGET_DIR%\dripage"

(
echo #!/bin/bash
echo REM 设置环境变量标志，表示这是 CLI 调用（禁用 console 日志）
echo export DRIPAGE_CLI=1
echo DRIPAGE_HOME="%DRIPAGE_HOME:\=/%"
echo "$DRIPAGE_HOME/.venv/Scripts/python.exe" "$DRIPAGE_HOME/cli.py" "$@"
) > "%WRAPPER%"

REM 创建 CMD 包装脚本
set "WRAPPER_CMD=%TARGET_DIR%\dripage.cmd"

(
echo @echo off
echo REM 设置环境变量标志，表示这是 CLI 调用（禁用 console 日志）
echo set "DRIPAGE_CLI=1"
echo setlocal
echo set "DRIPAGE_HOME=%DRIPAGE_HOME%"
echo "%%DRIPAGE_HOME%%\.venv\Scripts\python.exe" "%%DRIPAGE_HOME%%\cli.py" %%*
echo endlocal
) > "%WRAPPER_CMD%"

REM 创建 BAT 包装脚本
set "WRAPPER_BAT=%TARGET_DIR%\dripage.bat"

(
echo @echo off
echo REM 设置环境变量标志，表示这是 CLI 调用（禁用 console 日志）
echo set "DRIPAGE_CLI=1"
echo setlocal
echo set "DRIPAGE_HOME=%DRIPAGE_HOME%"
echo "%%DRIPAGE_HOME%%\.venv\Scripts\python.exe" "%%DRIPAGE_HOME%%\cli.py" %%*
echo endlocal
) > "%WRAPPER_BAT%"

echo.
echo ========================================
echo   安装成功！
echo ========================================
echo.
echo 已创建包装脚本：
echo   Bash/Unix: %WRAPPER%
echo   CMD:       %WRAPPER_CMD%
echo   BAT:       %WRAPPER_BAT%
echo.
echo 验证安装：
echo   dripage --help
echo.
echo 示例命令：
echo   dripage browser start --name browser1
echo   dripage browser status
echo.
echo 卸载方法：
echo   del %WRAPPER%
echo   del %WRAPPER_CMD%
echo   del %WRAPPER_BAT%
echo ========================================
echo.

endlocal
