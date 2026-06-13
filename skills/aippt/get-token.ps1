# get-token.ps1 - Get aippt access_token from credential-hosted service (Windows)
#
# Usage:
#   $env:AIPPT_API_KEY = & .\get-token.ps1
#
# Token is auto-injected by local proxy service via JWT, no manual input needed

$ErrorActionPreference = "Stop"

# -- Remote API base URL (BUILD_ENV=test uses test env, otherwise production) --

$RemoteBaseUrl = if ($env:BUILD_ENV -eq "test") { "https://jprx.sparta.html5.qq.com" } else { "https://jprx.m.qq.com" }

# -- Proxy port and request URL --

$Platform  = if ($env:CREDENTIAL_PLATFORM) { $env:CREDENTIAL_PLATFORM } else { "aippt" }
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
    [Console]::Error.WriteLine("ERROR: Gateway request failed: $_. Please authorize AIPPT in the integration panel first.")
    exit 1
}

if ($response.ret -ne 0) {
    [Console]::Error.WriteLine("ERROR: Gateway returned error (ret=$($response.ret)). Please authorize AIPPT in the integration panel first.")
    exit 1
}

$accessToken = $response.data.resp.data.access_token

if (-not $accessToken -or $accessToken -eq "null") {
    [Console]::Error.WriteLine("ERROR: Failed to get access_token. Please authorize AIPPT in the integration panel first.")
    exit 1
}

Write-Host -NoNewline $accessToken
