@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "ROUTER_JS=%SCRIPT_DIR%..\router.cjs"

where node >nul 2>nul
if errorlevel 1 (
    echo {"success": false, "error_code": 2, "message": "未检测到 node，无法运行 public-skill 平台公邮路由"}
    exit /b 1
)

node "%ROUTER_JS%" %*
exit /b %ERRORLEVEL%
