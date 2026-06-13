@echo off
setlocal enabledelayedexpansion

REM QClaw OpenClaw CLI wrapper (Windows)
REM
REM 从 ~/.qclaw/qclaw.json 读取运行时路径，通过独立 Node.js 二进制执行 openclaw 命令。
REM
REM 用法:
REM   scripts\openclaw-win.cmd <command> [args...]
REM   scripts\openclaw-win.cmd config get gateway.port
REM   scripts\openclaw-win.cmd cron list
REM   scripts\openclaw-win.cmd skills list

set "META_FILE=%USERPROFILE%\.qclaw\qclaw.json"

REM ============================================================
REM 读取 QClaw 元信息
REM ============================================================

if not exist "%META_FILE%" (
  echo [qclaw-cli] 错误: 元信息文件不存在: %META_FILE%
  echo [qclaw-cli] 请先启动 QClaw 桌面应用
  exit /b 1
)

REM 使用 PowerShell 解析 JSON
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-Content '%META_FILE%' -Raw | ConvertFrom-Json).cli.nodeBinary"`) do set "NODE_BINARY=%%i"
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-Content '%META_FILE%' -Raw | ConvertFrom-Json).cli.openclawMjs"`) do set "OPENCLAW_MJS=%%i"
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-Content '%META_FILE%' -Raw | ConvertFrom-Json).stateDir"`) do set "STATE_DIR=%%i"
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "(Get-Content '%META_FILE%' -Raw | ConvertFrom-Json).configPath"`) do set "CONFIG_PATH=%%i"

REM 验证路径有效性
if not exist "%NODE_BINARY%" (
  echo [qclaw-cli] 错误: Node 二进制不存在: %NODE_BINARY%
  echo [qclaw-cli] 请重启 QClaw 应用以更新元信息
  exit /b 1
)

if not exist "%OPENCLAW_MJS%" (
  echo [qclaw-cli] 错误: openclaw.mjs 不存在: %OPENCLAW_MJS%
  echo [qclaw-cli] 请重启 QClaw 应用以更新元信息
  exit /b 1
)

REM ============================================================
REM 环境变量注入
REM ============================================================

set "NODE_OPTIONS=--no-warnings"
set "OPENCLAW_NIX_MODE=1"
set "OPENCLAW_STATE_DIR=%STATE_DIR%"
set "OPENCLAW_CONFIG_PATH=%CONFIG_PATH%"

REM ============================================================
REM 执行 openclaw CLI
REM ============================================================

"%NODE_BINARY%" "%OPENCLAW_MJS%" %*
