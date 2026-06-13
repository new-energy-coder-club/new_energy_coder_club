# get-token.ps1 — Fetch Tencent Meeting access_token from credential gateway
#
# Usage:
#   $env:TENCENT_MEETING_TOKEN = & .\get-token.ps1
#
# Token is auto-injected via local proxy service (JWT), no manual input needed

$ErrorActionPreference = "Stop"

# -- Remote API base URL (BUILD_ENV=test uses test env, otherwise production) --

$RemoteBaseUrl = if ($env:BUILD_ENV -eq "test") { "https://jprx.sparta.html5.qq.com" } else { "https://jprx.m.qq.com" }

# -- Proxy port and request URL --

$Platform  = if ($env:CREDENTIAL_PLATFORM) { $env:CREDENTIAL_PLATFORM } else { "tencent_meeting" }
$ProxyPort = if ($env:AUTH_GATEWAY_PORT)   { $env:AUTH_GATEWAY_PORT }   else { "19000" }
$ProxyBase = "http://localhost:${ProxyPort}"
$RemoteUrl = "${RemoteBaseUrl}/data/4164/forward"

$body = @{ platform = $Platform } | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod -Uri "${ProxyBase}/proxy/api" `
        -Method Post `
        -Headers @{ "Remote-URL" = $RemoteUrl; "Content-Type" = "application/json" } `
        -Body $body `
        -TimeoutSec 10
} catch {
    [Console]::Error.WriteLine("ERROR: Gateway request failed: $_. Please authorize Tencent Meeting in the integration panel first.")
    exit 1
}

if ($response.ret -ne 0) {
    [Console]::Error.WriteLine("ERROR: Gateway returned error (ret=$($response.ret)). Please authorize Tencent Meeting in the integration panel first.")
    exit 1
}

$accessToken = $response.data.resp.data.access_token

if (-not $accessToken -or $accessToken -eq "null") {
    [Console]::Error.WriteLine("ERROR: access_token not found. Please authorize Tencent Meeting in the integration panel first.")
    exit 1
}

Write-Host -NoNewline $accessToken
