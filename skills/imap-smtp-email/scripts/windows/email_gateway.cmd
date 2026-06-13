@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "RESOLVE_ACCOUNT_JS=%SCRIPT_DIR%..\resolve-account.cjs"

where node >nul 2>nul
if errorlevel 1 (
    echo {"success": false, "error_code": 2, "message": "未检测到 node，无法运行 imap-smtp-email 个人邮箱路由"}
    exit /b 1
)

node "%RESOLVE_ACCOUNT_JS%" %*
exit /b %ERRORLEVEL%
