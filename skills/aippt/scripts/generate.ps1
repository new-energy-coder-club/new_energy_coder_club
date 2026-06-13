# ============================================================================
# AIPPT Generate Script (Windows PowerShell)
# Calls the GoatDee Design Agent API via Auth Gateway aippt proxy.
#
# Gateway waits for upstream SSE "started" event, extracts projectId,
# then returns JSON: { success, projectId, sessionIds, workspaceUrl, message }
# This script only needs to parse that JSON.
# ============================================================================

$ErrorActionPreference = "Stop"

# -- Force UTF-8 encoding (for output) --
chcp 65001 | Out-Null
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# -- Validate parameters --
if (-not $env:PROMPT) {
    [Console]::Error.WriteLine("[ERROR] Missing PROMPT environment variable")
    [Console]::Error.WriteLine("Usage: `$env:PROMPT='PPT description'; powershell -ExecutionPolicy Bypass -File generate.ps1")
    exit 1
}

# -- Derive Auth Gateway aippt proxy URL --
if (-not $env:QCLAW_LLM_BASE_URL) {
    [Console]::Error.WriteLine("[ERROR] QCLAW_LLM_BASE_URL is not set")
    exit 1
}

$AuthGwBase = $env:QCLAW_LLM_BASE_URL -replace '/llm$', ''
$AipptUrl = "${AuthGwBase}/aippt/agent/run"

# -- Build request body (ensure UTF-8 encoding) --
$bodyObj = @{ prompt = $env:PROMPT }
$Body = $bodyObj | ConvertTo-Json -Compress -Depth 10
$BodyBytes = [System.Text.Encoding]::UTF8.GetBytes($Body)

# -- Get API Key (via 4164 credential-hosted interface) --
$SkillDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$AipptApiKey = ""

$getTokenPath = Join-Path $SkillDir "get-token.ps1"
if (Test-Path $getTokenPath) {
    try {
        $AipptApiKey = & powershell -ExecutionPolicy Bypass -File $getTokenPath 2>$null
    } catch {
        $AipptApiKey = ""
    }
}

if (-not $AipptApiKey) {
    [Console]::Error.WriteLine("[ERROR] Failed to get AIPPT API Key. Please authorize in the integration panel first.")
    exit 1
}

Write-Host "[INFO] Generating PPT..."
Write-Host ""

# -- Call aippt proxy --
# Gateway handles SSE internally, returns JSON after receiving "started" event
$AuthToken = if ($env:QCLAW_LLM_API_KEY) { $env:QCLAW_LLM_API_KEY } else { "__QCLAW_AUTH_GATEWAY_MANAGED__" }

try {
    $response = Invoke-RestMethod -Uri $AipptUrl `
        -Method Post `
        -Headers @{
            "Content-Type"  = "application/json; charset=utf-8"
            "Authorization" = "Bearer $AuthToken"
            "X-API-Key"     = $AipptApiKey
            "X-Platform"    = "qclaw"
        } `
        -Body $BodyBytes `
        -TimeoutSec 300
} catch {
    [Console]::Error.WriteLine("[ERROR] API request failed: $_")
    exit 1
}

# -- Parse JSON response --
if (-not $response.success) {
    [Console]::Error.WriteLine("[ERROR] Generation failed:")
    $response | ConvertTo-Json -Depth 5 | ForEach-Object { [Console]::Error.WriteLine($_) }
    exit 1
}

$ProjectId    = if ($response.projectId)    { $response.projectId }    else { "" }
$WorkspaceUrl = if ($response.workspaceUrl) { $response.workspaceUrl } else { "" }
$Message      = if ($response.message)      { $response.message }      else { "" }

Write-Host "[OK] Task started, PPT is being generated in background"
Write-Host ""
Write-Host "[SUCCESS] PPT generation task submitted!"
Write-Host ""
Write-Host "Result:"

$result = @{
    projectId    = $ProjectId
    workspaceUrl = $WorkspaceUrl
    message      = $Message
}
$result | ConvertTo-Json -Depth 5

Write-Host ""
if ($WorkspaceUrl) {
    Write-Host "Edit URL: ${WorkspaceUrl}"
}
