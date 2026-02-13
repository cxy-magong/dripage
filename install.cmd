@echo off
REM Dripage CLI installer for Windows

chcp 65001 > nul
setlocal

set "DRIPAGE_HOME=%~dp0"
set "DRIPAGE_HOME=%DRIPAGE_HOME:~0,-1%"

REM 用户级命令目录
set "TARGET_DIR=%USERPROFILE%\.local\bin"

REM Create target directory
if not exist "%TARGET_DIR%" (
    echo Creating target directory: %TARGET_DIR%
    mkdir "%TARGET_DIR%"
)

REM 创建 Bash/Unix 包装脚本
set "WRAPPER=%TARGET_DIR%\dripage"

(
echo #!/bin/bash
echo export DRIPAGE_CLI=1
echo DRIPAGE_HOME="%DRIPAGE_HOME:\=/%"
echo "$DRIPAGE_HOME/.venv/Scripts/python.exe" "$DRIPAGE_HOME/cli.py" "$@"
) > "%WRAPPER%"

REM 创建 CMD 包装脚本
set "WRAPPER_CMD=%TARGET_DIR%\dripage.cmd"

(
echo @echo off
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
echo set "DRIPAGE_CLI=1"
echo setlocal
echo set "DRIPAGE_HOME=%DRIPAGE_HOME%"
echo "%%DRIPAGE_HOME%%\.venv\Scripts\python.exe" "%%DRIPAGE_HOME%%\cli.py" %%*
echo endlocal
) > "%WRAPPER_BAT%"

echo.
echo ========================================
echo   Installation Successful!
echo ========================================
echo.
echo Created wrapper scripts:
echo   Bash/Unix: %WRAPPER%
echo   CMD:       %WRAPPER_CMD%
echo   BAT:       %WRAPPER_BAT%
echo.
echo Verify installation:
echo   dripage --help
echo.
echo Example commands:
echo   dripage browser start --name browser1
echo   dripage browser status
echo.
echo Uninstall:
echo   del %WRAPPER%
echo   del %WRAPPER_CMD%
echo   del %WRAPPER_BAT%
echo ========================================
echo.

endlocal
