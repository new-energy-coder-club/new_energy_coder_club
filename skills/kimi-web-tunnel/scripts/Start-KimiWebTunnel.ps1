# 一键启动 Kimi Web 远程访问（kimi web + Cloudflare Tunnel）
# 用法：右键 PowerShell 运行，或在终端执行  pwsh -File Start-KimiWebTunnel.ps1
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8

$ProjectRoot  = if ($env:KIMI_WEB_PROJECT_ROOT) { $env:KIMI_WEB_PROJECT_ROOT } else { 'D:\Project_env\SolarGlyph' }
$CfDir        = Join-Path $ProjectRoot '.devkit\cloudflared'
$Cloudflared  = Join-Path $CfDir 'cloudflared.exe'
$CfConfig     = Join-Path $CfDir 'config.yml'
$TokenFile    = Join-Path $CfDir 'kimi-web-token.txt'
$LogDir       = Join-Path $CfDir 'logs'
$Port         = 5490   # 固定专用端口，避开 /web 默认的 5494 防止抢占
$PublicHost   = 'kimi.newenergycoder.club'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (-not (Test-Path $TokenFile)) { throw "缺少 token 文件: $TokenFile" }
$Token = (Get-Content $TokenFile -Raw).Trim()
$kimiArgs = @('web','--network','--public','--no-open','--port', "$Port",
              '--auth-token', $Token,
              '--allowed-origins', "https://$PublicHost")

# --- 1. kimi web ---
$portInUse = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "[skip] kimi web 已在监听端口 $Port" -ForegroundColor Yellow
} else {
    Start-Process -FilePath 'kimi' -ArgumentList $kimiArgs `
        -WorkingDirectory $ProjectRoot -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir 'kimi-web.out.log') `
        -RedirectStandardError  (Join-Path $LogDir 'kimi-web.err.log')
    Write-Host "[ok] kimi web 已启动 (端口 $Port)" -ForegroundColor Green
}

# --- 2. cloudflared tunnel ---
$cfRunning = Get-Process -Name 'cloudflared' -ErrorAction SilentlyContinue
if ($cfRunning) {
    Write-Host "[skip] cloudflared 隧道已在运行 (PID $($cfRunning.Id -join ','))" -ForegroundColor Yellow
} else {
    Start-Process -FilePath $Cloudflared -ArgumentList @('tunnel','--config',$CfConfig,'run','kimi') `
        -WorkingDirectory $CfDir -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir 'cloudflared.out.log') `
        -RedirectStandardError  (Join-Path $LogDir 'cloudflared.err.log')
    Write-Host "[ok] cloudflared 隧道已启动" -ForegroundColor Green
}

# --- 3. 健康检查 ---
Write-Host "`n等待服务就绪..." -ForegroundColor Cyan
$ok = $false
foreach ($i in 1..12) {
    Start-Sleep -Seconds 5
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/" -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch {}
}
if ($ok) { Write-Host "[ok] 本地 kimi web 健康检查通过" -ForegroundColor Green }
else     { Write-Warning "本地健康检查未通过，请查看 $LogDir\kimi-web.err.log" }

Write-Host "`n================ 访问地址 ================" -ForegroundColor Cyan
Write-Host "公网:   https://$PublicHost/?token=$Token"
Write-Host "局域网: http://<本机IP>:$Port/?token=$Token"
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "停止服务：运行 Stop-KimiWebTunnel.ps1`n"
