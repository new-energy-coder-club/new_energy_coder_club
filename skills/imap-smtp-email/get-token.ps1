param(
    [string]$Token = "",
    [string]$Email = "",
    [string]$Platform = ""
)
# get-token.ps1 — 从凭证网关获取邮箱授权码并写入 imap-smtp-email/.env
$ErrorActionPreference = "Stop"

# ── 编码保护：强制 UTF-8 无 BOM ──
# Windows PowerShell 5.x 默认使用系统 code page（GBK/936），会导致：
#   1. Write-Output 的中文 JSON 输出变为 GBK，resolve-account.cjs JSON.parse 失败
#   2. Set-Content -Encoding UTF8 实际写 UTF-8 BOM，Node.js 读 .env 时第一个 key 带 BOM 前缀
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$SkillDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvFile  = Join-Path $SkillDir ".env"
# BUILD_ENV=test 时走测试环境，其他情况走现网
$RemoteBaseUrl = if ($env:BUILD_ENV -eq "test") { "https://jprx.sparta.html5.qq.com" } else { "https://jprx.m.qq.com" }
$ProxyPort = if ($env:AUTH_GATEWAY_PORT) { $env:AUTH_GATEWAY_PORT } else { "19000" }
$ProxyBase = "http://localhost:${ProxyPort}"
$RemoteUrl = "${RemoteBaseUrl}/data/4164/forward"
$CheckedPlatforms = @("163_mail", "qq_mail", "gmail", "outlook", "sina_mail", "sohu_mail")
$Failures = New-Object System.Collections.ArrayList

function Write-Json($success, $message, $errorCode = $null, $extra = @{}) {
    $payload = [ordered]@{
        success = [bool]$success
        message = $message
    }
    foreach ($key in $extra.Keys) {
        $payload[$key] = $extra[$key]
    }
    if ($null -ne $errorCode -and "$errorCode" -ne "") {
        $payload.error_code = [int]$errorCode
    }
    $payload | ConvertTo-Json -Depth 6 -Compress
}

function Infer-Servers($domain) {
    switch ($domain) {
        "163.com"       { $script:imapHost = "imap.163.com";          $script:smtpHost = "smtp.163.com";          $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "vip.163.com"   { $script:imapHost = "imap.vip.163.com";      $script:smtpHost = "smtp.vip.163.com";      $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "126.com"       { $script:imapHost = "imap.126.com";          $script:smtpHost = "smtp.126.com";          $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "vip.126.com"   { $script:imapHost = "imap.vip.126.com";      $script:smtpHost = "smtp.vip.126.com";      $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "188.com"       { $script:imapHost = "imap.188.com";          $script:smtpHost = "smtp.188.com";          $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "vip.188.com"   { $script:imapHost = "imap.vip.188.com";      $script:smtpHost = "smtp.vip.188.com";      $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "yeah.net"      { $script:imapHost = "imap.yeah.net";         $script:smtpHost = "smtp.yeah.net";         $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "gmail.com"     { $script:imapHost = "imap.gmail.com";        $script:smtpHost = "smtp.gmail.com";        $script:smtpPort = "587"; $script:smtpSecure = "false"; return $true }
        "outlook.com"   { $script:imapHost = "outlook.office365.com"; $script:smtpHost = "smtp-mail.outlook.com"; $script:smtpPort = "587"; $script:smtpSecure = "false"; return $true }
        "hotmail.com"   { $script:imapHost = "outlook.office365.com"; $script:smtpHost = "smtp-mail.outlook.com"; $script:smtpPort = "587"; $script:smtpSecure = "false"; return $true }
        "live.com"      { $script:imapHost = "outlook.office365.com"; $script:smtpHost = "smtp-mail.outlook.com"; $script:smtpPort = "587"; $script:smtpSecure = "false"; return $true }
        "live.cn"       { $script:imapHost = "outlook.office365.com"; $script:smtpHost = "smtp-mail.outlook.com"; $script:smtpPort = "587"; $script:smtpSecure = "false"; return $true }
        "qq.com"        { $script:imapHost = "imap.qq.com";           $script:smtpHost = "smtp.qq.com";           $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "foxmail.com"   { $script:imapHost = "imap.qq.com";           $script:smtpHost = "smtp.qq.com";           $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "vip.qq.com"    { $script:imapHost = "imap.vip.qq.com";       $script:smtpHost = "smtp.vip.qq.com";       $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "yahoo.com"     { $script:imapHost = "imap.mail.yahoo.com";   $script:smtpHost = "smtp.mail.yahoo.com";   $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "sina.com"      { $script:imapHost = "imap.sina.com";         $script:smtpHost = "smtp.sina.com";         $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "sina.cn"       { $script:imapHost = "imap.sina.com";         $script:smtpHost = "smtp.sina.com";         $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "vip.sina.com"  { $script:imapHost = "imap.vip.sina.com";     $script:smtpHost = "smtp.vip.sina.com";     $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "sohu.com"      { $script:imapHost = "imap.sohu.com";         $script:smtpHost = "smtp.sohu.com";         $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "139.com"       { $script:imapHost = "imap.139.com";          $script:smtpHost = "smtp.139.com";          $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "exmail.qq.com" { $script:imapHost = "imap.exmail.qq.com";    $script:smtpHost = "smtp.exmail.qq.com";    $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        "aliyun.com"    { $script:imapHost = "imap.aliyun.com";       $script:smtpHost = "smtp.aliyun.com";       $script:smtpPort = "465"; $script:smtpSecure = "true"; return $true }
        default { return $false }
    }
}

function Platform-FromDomain($domain) {
    switch ($domain) {
        { $_ -in @("163.com","vip.163.com","126.com","vip.126.com","188.com","vip.188.com","yeah.net") } { return "163_mail" }
        { $_ -in @("qq.com","foxmail.com","vip.qq.com","exmail.qq.com") } { return "qq_mail" }
        { $_ -eq "gmail.com" } { return "gmail" }
        { $_ -in @("outlook.com","hotmail.com","live.com","live.cn") } { return "outlook" }
        { $_ -in @("sina.com","sina.cn","vip.sina.com") } { return "sina_mail" }
        { $_ -eq "sohu.com" } { return "sohu_mail" }
        default { return "" }
    }
}

function Write-Env($emailAddr, $tokenVal, $tokenSource) {
    $homeDir = $env:USERPROFILE
    $emailDomain = ($emailAddr -split '@')[-1]
    $envContent = @"
# Provider hint
EMAIL_PROVIDER_HINT=$emailDomain

# IMAP Configuration
IMAP_HOST=$imapHost
IMAP_PORT=993
IMAP_USER=$emailAddr
IMAP_PASS=$tokenVal
IMAP_TLS=true
IMAP_REJECT_UNAUTHORIZED=true
IMAP_MAILBOX=INBOX
IMAP_CONN_TIMEOUT_MS=20000
IMAP_AUTH_TIMEOUT_MS=15000
IMAP_SOCKET_TIMEOUT_MS=30000
IMAP_CONNECTION_RETRIES=2
IMAP_RETRY_DELAY_MS=1500
IMAP_KEEPALIVE_INTERVAL_MS=10000
IMAP_IDLE_INTERVAL_MS=300000

# SMTP Configuration
SMTP_HOST=$smtpHost
SMTP_PORT=$smtpPort
SMTP_SECURE=$smtpSecure
SMTP_USER=$emailAddr
SMTP_PASS=$tokenVal
SMTP_FROM=$emailAddr
SMTP_REJECT_UNAUTHORIZED=true
SMTP_CONNECTION_TIMEOUT_MS=30000
SMTP_GREETING_TIMEOUT_MS=30000
SMTP_SOCKET_TIMEOUT_MS=60000
SMTP_DNS_TIMEOUT_MS=30000
SMTP_CONNECTION_RETRIES=2
SMTP_RETRY_DELAY_MS=1500

# File access whitelist
ALLOWED_READ_DIRS=$homeDir\Downloads,$homeDir\Documents
ALLOWED_WRITE_DIRS=$homeDir\Downloads

# Token source (used to decide whether runtime auto-refresh may overwrite this file)
TOKEN_SOURCE=$tokenSource
"@
    # 使用 .NET API 写入 UTF-8 无 BOM — Windows PowerShell 5.x 的 Set-Content -Encoding UTF8
    # 会写入 BOM (EF BB BF)，导致 Node.js 读 .env 时第一行 key 前缀带 BOM 解析失败
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($EnvFile, $envContent, $utf8NoBom)
}

function Add-Failure($platform, $errorCode, $message) {
    [void]$Failures.Add([pscustomobject]@{
        platform = $platform
        error_code = [int]$errorCode
        message = $message
    })
}

function Emit-BestFailureAndExit() {
    $selected = $Failures | Where-Object { $_.error_code -eq 21004 } | Select-Object -First 1
    if (-not $selected) {
        $selected = $Failures | Select-Object -First 1
    }
    if (-not $selected) {
        $selected = [pscustomobject]@{
            platform = ""
            error_code = 3
            message = "未从凭证服务获取到可用的个人邮箱授权信息，请先登录并接通邮箱能力，或改用 setup.sh 手动配置。"
        }
    }
    Write-Output (Write-Json $false $selected.message $selected.error_code @{ checked_platforms = $CheckedPlatforms; source = "credential_service"; platform = $selected.platform })
    exit 1
}

if ($Token -or $Email) {
    if (-not $Token -or -not $Email) {
        Write-Output (Write-Json $false "-Token 和 -Email 必须同时提供" 1 @{ mode = "manual-token" })
        exit 1
    }
    if ($Token -match '\s') {
        Write-Output (Write-Json $false "授权码不能包含空格或换行符" 1 @{ mode = "manual-token" })
        exit 1
    }
    if ($Email -notmatch '@') {
        Write-Output (Write-Json $false "邮箱地址格式无效" 1 @{ mode = "manual-token" })
        exit 1
    }
    $Email = $Email.Trim()
    $domain = ($Email -split '@')[-1]
    if (-not (Infer-Servers $domain)) {
        Write-Output (Write-Json $false "当前 get-token.ps1 不支持自动推断域名 ${domain}，请改用 setup.sh 或手工写入 .env" 1 @{ mode = "manual-token" })
        exit 1
    }
    Write-Env $Email $Token "manual_token"
    Write-Output (Write-Json $true "已写入个人邮箱凭证" $null @{ env_path = $EnvFile; mode = "manual-token" })
    exit 0
}

# ── 模式二：指定 platform 拉取凭证 ──
if ($Platform) {
    $bodyStr = @{ platform = $Platform } | ConvertTo-Json -Compress
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyStr)
    try {
        $response = Invoke-RestMethod -Uri "${ProxyBase}/proxy/api" `
            -Method Post `
            -Headers @{ "Remote-URL" = $RemoteUrl; "Content-Type" = "application/json; charset=utf-8" } `
            -Body $bodyBytes `
            -TimeoutSec 10
    } catch {
        Write-Output (Write-Json $false "请求凭证服务失败，请检查本地代理或登录态。" 999 @{ platform = $Platform; mode = "platform-specific" })
        exit 1
    }

    if ($response.ret -ne 0) {
        Write-Output (Write-Json $false "凭证服务网关返回异常，ret=$($response.ret)" 999 @{ platform = $Platform; mode = "platform-specific" })
        exit 1
    }

    $common = $response.data.resp.common
    $commonCode = if ($null -ne $common.code -and "$($common.code)" -ne "") { [int]$common.code } else { 999 }
    $commonMessage = if ($common.message) { [string]$common.message } else { "凭证服务返回失败" }
    if ($commonCode -ne 0) {
        Write-Output (Write-Json $false $commonMessage $commonCode @{ platform = $Platform; mode = "platform-specific" })
        exit 1
    }

    $accessToken = $response.data.resp.data.access_token
    $emailAddress = $response.data.resp.data.extra_data.email_address
    if (-not $accessToken -or -not $emailAddress) {
        Write-Output (Write-Json $false "凭证服务未返回可用的邮箱地址或授权码" 3 @{ platform = $Platform; mode = "platform-specific" })
        exit 1
    }

    $domain = ($emailAddress -split '@')[-1]
    if (-not (Infer-Servers $domain)) {
        Write-Output (Write-Json $false "当前 get-token.ps1 不支持自动推断域名 ${domain}，请改用 setup.sh 或手工写入 .env" 1 @{ platform = $Platform; mode = "platform-specific" })
        exit 1
    }

    Write-Env $emailAddress $accessToken "credential_service"
    Write-Output (Write-Json $true "已从凭证服务刷新个人邮箱凭证" $null @{ env_path = $EnvFile; mode = "platform-specific"; platform = $Platform; email = $emailAddress })
    exit 0
}

# ── 模式三：自动遍历所有平台 ──
foreach ($platform in $CheckedPlatforms) {
    $bodyStr = @{ platform = $platform } | ConvertTo-Json -Compress
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyStr)
    try {
        $response = Invoke-RestMethod -Uri "${ProxyBase}/proxy/api" `
            -Method Post `
            -Headers @{ "Remote-URL" = $RemoteUrl; "Content-Type" = "application/json; charset=utf-8" } `
            -Body $bodyBytes `
            -TimeoutSec 10
    } catch {
        Add-Failure $platform 999 "请求凭证服务失败，请检查本地代理或登录态。"
        continue
    }

    if ($response.ret -ne 0) {
        Add-Failure $platform 999 "凭证服务网关返回异常，ret=$($response.ret)"
        continue
    }

    $common = $response.data.resp.common
    $commonCode = if ($null -ne $common.code -and "$($common.code)" -ne "") { [int]$common.code } else { 999 }
    $commonMessage = if ($common.message) { [string]$common.message } else { "凭证服务返回失败" }
    if ($commonCode -ne 0) {
        Add-Failure $platform $commonCode $commonMessage
        continue
    }

    $accessToken = $response.data.resp.data.access_token
    $emailAddress = $response.data.resp.data.extra_data.email_address
    if (-not $accessToken -or -not $emailAddress) {
        Add-Failure $platform 3 "凭证服务未返回可用的邮箱地址或授权码"
        continue
    }

    $domain = ($emailAddress -split '@')[-1]
    $expectedPlatform = Platform-FromDomain $domain
    if ($expectedPlatform -and $expectedPlatform -ne $platform) {
        Add-Failure $platform 3 "凭证服务返回的邮箱 ${emailAddress} 与平台 ${platform} 不匹配"
        continue
    }

    if (-not (Infer-Servers $domain)) {
        Add-Failure $platform 1 "当前 get-token.ps1 不支持自动推断域名 ${domain}，请改用 setup.sh 或手工写入 .env"
        continue
    }

    Write-Env $emailAddress $accessToken "credential_service"
    Write-Output (Write-Json $true "已从凭证服务刷新个人邮箱凭证" $null @{ env_path = $EnvFile; mode = "credential-service"; platform = $platform; email = $emailAddress })
    exit 0
}

Emit-BestFailureAndExit
