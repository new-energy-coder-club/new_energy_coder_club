# 停止 Kimi Web 远程访问（kimi web + cloudflared）
$Port = 5490

# 停 kimi web（按监听端口找进程）
$conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($conns) {
    $conns | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object {
        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
        Write-Host "[ok] 已停止 kimi web (PID $_)" -ForegroundColor Green
    }
} else {
    Write-Host "[skip] 端口 $Port 无监听进程" -ForegroundColor Yellow
}

# 停 cloudflared
$cf = Get-Process -Name 'cloudflared' -ErrorAction SilentlyContinue
if ($cf) {
    $cf | Stop-Process -Force
    Write-Host "[ok] 已停止 cloudflared (PID $($cf.Id -join ','))" -ForegroundColor Green
} else {
    Write-Host "[skip] cloudflared 未运行" -ForegroundColor Yellow
}
