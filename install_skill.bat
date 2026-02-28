@echo off
REM Dripage CLI Skill 安装/更新脚本
REM 创建目录链接到 opencode 技能目录

setlocal enabledelayedexpansion

set "SOURCE_DIR=%~dp0Skills\dripage-cli"
set "TARGET_DIR=C:\Users\%USERNAME%\.config\opencode\skills\dripage-cli"

echo ========================================
echo Dripage CLI Skill 安装/更新
echo ========================================
echo.
echo 源目录: %SOURCE_DIR%
echo 目标目录: %TARGET_DIR%
echo.

REM 检查源目录是否存在
if not exist "%SOURCE_DIR%" (
    echo [错误] 源目录不存在: %SOURCE_DIR%
    pause
    exit /b 1
)

REM 如果目标目录已存在（可能是旧文件或旧链接），先删除
if exist "%TARGET_DIR%" (
    echo [步骤 1] 删除旧的 dripage-cli 目录...
    powershell -Command "Remove-Item -Path '%TARGET_DIR%' -Recurse -Force" >nul 2>&1
    if !errorlevel! neq 0 (
        echo [错误] 删除失败，请手动删除后重试
        pause
        exit /b 1
    )
    echo [成功] 已删除旧目录
    echo.
)

REM 创建 Junction 链接
echo [步骤 2] 创建目录链接...
powershell -Command "New-Item -ItemType Junction -Path '%TARGET_DIR%' -Target '%SOURCE_DIR%'" >nul 2>&1

if !errorlevel! equ 0 (
    echo [成功] 链接创建成功！
    echo.
    echo ========================================
    echo 验证链接
    echo ========================================
    echo.

    powershell -Command "Get-Item '%TARGET_DIR%' | Select-Object LinkType, Target"
    echo.

    echo 安装完成！
    echo.
    echo 说明：
    echo - 这是 Windows Junction 链接（不需要管理员权限）
    echo - 修改源目录中的文件会自动同步到 opencode
    echo - 不需要重新安装
    echo.
) else (
    echo [错误] 链接创建失败
    echo.
    echo 可能的原因：
    echo 1. 目标路径包含特殊字符
    echo 2. 权限不足
    echo.
    pause
    exit /b 1
)

pause
