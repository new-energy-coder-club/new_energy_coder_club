# get-token.ps1 — 获取 IMA OpenAPI 凭证（Client ID + API Key）
#
# 用法:
#   $creds = & "<SCRIPT_PATH>\get-token.ps1" | ConvertFrom-Json
#   # 返回 JSON: {"client_id":"...","api_key":"..."}
#
# 支持两种凭证来源（按优先级）：
#   1. 本地代理服务（平台托管模式，AUTH_GATEWAY_PORT 环境变量存在时启用）
#   2. 环境变量 / 配置文件（本地模式）

$ErrorActionPreference = "Stop"

# ── 模式 1：本地代理服务（平台托管） ──────────────────────────────────────────

if ($env:AUTH_GATEWAY_PORT) {
    $ProxyPort = $env:AUTH_GATEWAY_PORT
    $ProxyBase = "http://localhost:${ProxyPort}"

    # BUILD_ENV=test 时走测试环境，其他情况走现网
    $RemoteBase = if ($env:BUILD_ENV -eq "test") { "https://jprx.sparta.html5.qq.com" } else { "https://jprx.m.qq.com" }

    $Platform = if ($env:CREDENTIAL_PLATFORM) { $env:CREDENTIAL_PLATFORM } else { "ima" }
    $body = @{ platform = $Platform } | ConvertTo-Json -Compress
    $RemoteUrl = "${RemoteBase}/data/4164/forward"

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
        [Console]::Error.WriteLine("ERROR: ret=$($response.ret)")
        exit 1
    }

    # access_token → api_key, extra_data.client_id → client_id
    $apiKey = $response.data.resp.data.access_token
    $clientId = $response.data.resp.data.extra_data.client_id

    if (-not $clientId -or $clientId -eq "null" -or -not $apiKey -or $apiKey -eq "null") {
        [Console]::Error.WriteLine("ERROR: 未获取到 IMA 凭证，请先在集成面板中完成 IMA 授权")
        exit 1
    }

    Write-Output (@{ client_id = $clientId; api_key = $apiKey } | ConvertTo-Json -Compress)
    exit 0
}

# ── 模式 2：环境变量 / 配置文件（本地模式） ──────────────────────────────────

$ImaClientId = $env:IMA_OPENAPI_CLIENTID
$ImaApiKey = $env:IMA_OPENAPI_APIKEY

if (-not $ImaClientId) {
    $configPath = Join-Path $HOME ".config/ima/client_id"
    if (Test-Path $configPath) { $ImaClientId = (Get-Content $configPath -Raw).Trim() }
}

if (-not $ImaApiKey) {
    $configPath = Join-Path $HOME ".config/ima/api_key"
    if (Test-Path $configPath) { $ImaApiKey = (Get-Content $configPath -Raw).Trim() }
}

if (-not $ImaClientId -or -not $ImaApiKey) {
    [Console]::Error.WriteLine("ERROR: 缺少 IMA 凭证。请配置环境变量 IMA_OPENAPI_CLIENTID + IMA_OPENAPI_APIKEY 或写入 ~/.config/ima/")
    exit 1
}

Write-Output (@{ client_id = $ImaClientId; api_key = $ImaApiKey } | ConvertTo-Json -Compress)
