# get-token.ps1 — 从凭证托管服务获取有道云笔记 API Key
#
# 用法:
#   $apiKey = & .\get-token.ps1
#   youdaonote config set apiKey $apiKey
#
# Token 由本地代理服务自动注入 JWT，无需手动传入

$ErrorActionPreference = "Stop"

$Platform  = if ($env:CREDENTIAL_PLATFORM) { $env:CREDENTIAL_PLATFORM } else { "youdaonote" }
$ProxyPort = if ($env:AUTH_GATEWAY_PORT)   { $env:AUTH_GATEWAY_PORT }   else { "19000" }
$ProxyBase = "http://localhost:${ProxyPort}"

# BUILD_ENV=test 时走测试环境，其他情况走现网
$RemoteBaseUrl = if ($env:BUILD_ENV -eq "test") { "https://jprx.sparta.html5.qq.com" } else { "https://jprx.m.qq.com" }
$RemoteUrl = "${RemoteBaseUrl}/data/4164/forward"

$body = @{ platform = $Platform } | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod -Uri "${ProxyBase}/proxy/api" `
        -Method Post `
        -Headers @{ "Remote-URL" = $RemoteUrl; "Content-Type" = "application/json" } `
        -Body $body `
        -TimeoutSec 10
} catch {
    [Console]::Error.WriteLine("ERROR: $_")
    exit 1
}

if ($response.ret -ne 0) {
    [Console]::Error.WriteLine("ERROR: ret=$($response.ret)，请先在集成面板中完成有道云笔记授权")
    exit 1
}

$accessToken = $response.data.resp.data.access_token

if (-not $accessToken -or $accessToken -eq "null") {
    [Console]::Error.WriteLine("ERROR: 未获取到 API Key，请先在集成面板中完成有道云笔记授权")
    exit 1
}

Write-Output $accessToken
