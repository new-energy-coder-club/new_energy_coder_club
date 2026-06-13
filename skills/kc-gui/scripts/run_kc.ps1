# run_kc.ps1 - Wrapper to launch kc.exe with dependency checks and config provisioning
# Usage: powershell -ExecutionPolicy Bypass -File run_kc.ps1 [-q "task"] [other kc args...]
# Config is auto-provisioned from bundled config.toml template on first run.
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$KcArgs
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillDir = Split-Path -Parent $scriptDir

# --- Platform check ---
if ($env:OS -ne "Windows_NT") {
    Write-Host "[ERROR] kc.exe requires Windows." -ForegroundColor Red
    exit 1
}

# --- Integrity level check ---
# S-1-16-4096 = Low integrity; kc.exe needs Medium or higher to function correctly.
$tokenIntegrityLevel = ([System.Security.Principal.WindowsIdentity]::GetCurrent()).Groups |
    Where-Object { $_.Value -like "S-1-16-*" } |
    Select-Object -ExpandProperty Value -ErrorAction SilentlyContinue
if ($tokenIntegrityLevel -eq "S-1-16-4096") {
    Write-Host "[ERROR] Process is running at Low integrity level." -ForegroundColor Red
    Write-Host "[ERROR] Make sure you follow the Usage section in SKILL.md:" -ForegroundColor Red
    exit 1
}

# --- Locate kc.exe ---
$kcPath = Join-Path $skillDir "kc.exe"

if (!(Test-Path $kcPath)) {
    Write-Host "[ERROR] kc.exe not found at: $kcPath" -ForegroundColor Red
    exit 1
}

# --- VC Runtime dependency check & auto-install ---
function Test-VCRuntime {
    $sys32 = [System.Environment]::GetFolderPath("System")
    foreach ($dll in @("vcruntime140.dll", "vcruntime140_1.dll")) {
        if (!(Test-Path (Join-Path $sys32 $dll))) { return $false }
    }
    return $true
}

function Install-VCRuntime {
    Write-Host "[INFO] Installing Visual C++ Redistributable..." -ForegroundColor Yellow

    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        winget install --id Microsoft.VCRedist.2015+.x64 --silent --accept-package-agreements --accept-source-agreements 2>$null
        if ($LASTEXITCODE -eq 0 -and (Test-VCRuntime)) {
            Write-Host "[OK] VC++ Redistributable installed." -ForegroundColor Green
            return $true
        }
    }

    # Fallback: direct download
    $vcUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
    $installer = Join-Path $env:TEMP "vc_redist.x64.exe"
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $vcUrl -OutFile $installer -UseBasicParsing
        Start-Process -FilePath $installer -ArgumentList "/install", "/quiet", "/norestart" -Wait
        Remove-Item $installer -ErrorAction SilentlyContinue
        if (Test-VCRuntime) {
            Write-Host "[OK] VC++ Redistributable installed." -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "[WARN] Auto-install failed: $_" -ForegroundColor Yellow
    }
    return $false
}

if (!(Test-VCRuntime)) {
    Write-Host "[WARN] VC++ Runtime missing (vcruntime140.dll / vcruntime140_1.dll)." -ForegroundColor Yellow
    if (!(Install-VCRuntime)) {
        Write-Host "[ERROR] Could not install VC++ Redistributable." -ForegroundColor Red
        Write-Host "[ERROR] Install manually: https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Red
        exit 1
    }
}

# --- WebView2 check (needed for --gui mode) ---
function Test-WebView2 {
    $regPaths = @(
        "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-E15AB5810CD8}",
        "HKCU:\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-E15AB5810CD8}",
        "HKLM:\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-E15AB5810CD8}"
    )
    foreach ($p in $regPaths) {
        if (Test-Path $p) { return $true }
    }
    return $false
}

if ($KcArgs -match "--gui" -and !(Test-WebView2)) {
    Write-Host "[WARN] WebView2 not detected (required for GUI mode)." -ForegroundColor Yellow
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        winget install --id Microsoft.EdgeWebView2Runtime --silent --accept-package-agreements --accept-source-agreements 2>$null
    }
    if (!(Test-WebView2)) {
        Write-Host "[WARN] WebView2 auto-install failed. GUI mode may not work." -ForegroundColor Yellow
        Write-Host "[WARN] Download: https://developer.microsoft.com/en-us/microsoft-edge/webview2/" -ForegroundColor Yellow
    }
}

# --- Sync LLM settings from openclaw.json into config.toml ---
# On any parse error, resets config.toml to the bundled template default.
function Sync-KcConfigFromOpenClaw {
    param([string]$ConfigPath, [string]$TemplatePath)

    $openclawPath = Join-Path $env:USERPROFILE ".qclaw\openclaw.json"
    if (!(Test-Path $openclawPath)) { return }

    try {
        $ocJson = Get-Content -Path $openclawPath -Raw | ConvertFrom-Json

        # Parse primary model reference: "<provider>/<modelId>"
        $primary = $ocJson.agents.defaults.model.primary
        if ([string]::IsNullOrWhiteSpace($primary)) { throw "Missing agents.defaults.model.primary" }

        $parts = $primary -split "/", 2
        if ($parts.Count -lt 2) { throw "Invalid model reference format: $primary" }
        $providerName = $parts[0]
        $modelId = $parts[1]

        # Look up provider details
        $provider = $ocJson.models.providers.$providerName
        if ($null -eq $provider) { throw "Provider '$providerName' not found in openclaw.json" }

        $providerBaseUrl = [string]$provider.baseUrl
        $providerApiKey = [string]$provider.apiKey

        # Determine target values: QCLAW special case sets all to empty
        if ($providerApiKey -match "QCLAW") {
            $newBaseUrl = ""
            $newApiKey = ""
            $newModelName = ""
            $newMultimodalName = ""
        } else {
            $newBaseUrl = $providerBaseUrl
            $newApiKey = $providerApiKey
            $newModelName = $modelId
            $newMultimodalName = $modelId
        }

        # Read current config.toml and check existing values
        $content = Get-Content -Path $ConfigPath -Raw

        $currentBaseUrl = if ($content -match '(?m)^base_url\s*=\s*"(.*?)"') { $Matches[1] } else { "" }
        $currentApiKey = if ($content -match '(?m)^api_key\s*=\s*"(.*?)"') { $Matches[1] } else { "" }
        $currentModelName = if ($content -match '(?m)^model_name\s*=\s*"(.*?)"') { $Matches[1] } else { "" }
        $currentMultimodalName = if ($content -match '(?m)^multimodal_name\s*=\s*"(.*?)"') { $Matches[1] } else { "" }

        if ($currentBaseUrl -eq $newBaseUrl -and $currentApiKey -eq $newApiKey -and
            $currentModelName -eq $newModelName -and $currentMultimodalName -eq $newMultimodalName) {
            Write-Host "[OK] LLM config already up-to-date." -ForegroundColor Green
            return
        }

        # Update values in-place using regex replacement
        $content = $content -replace '(?m)^(model_name\s*=\s*)".*?"', "`$1`"$newModelName`""
        $content = $content -replace '(?m)^(multimodal_name\s*=\s*)".*?"', "`$1`"$newMultimodalName`""
        $content = $content -replace '(?m)^(base_url\s*=\s*)".*?"', "`$1`"$newBaseUrl`""
        $content = $content -replace '(?m)^(api_key\s*=\s*)".*?"', "`$1`"$newApiKey`""

        Set-Content -Path $ConfigPath -Value $content -NoNewline
        Write-Host "[OK] LLM config synced from openclaw.json." -ForegroundColor Green
    } catch {
        # Parse or structure error — reset config.toml to the bundled template default
        Write-Host "[WARN] Failed to parse openclaw.json: $_" -ForegroundColor Yellow
        if (Test-Path $TemplatePath) {
            Copy-Item -Path $TemplatePath -Destination $ConfigPath -Force
            Write-Host "[OK] config.toml reset to default template." -ForegroundColor Green
        } else {
            Write-Host "[WARN] Template config.toml not found, keeping existing config." -ForegroundColor Yellow
        }
    }
}

# --- Provision config.toml: only copy template if it does not exist ---
function Ensure-KcConfig {
    $kcConfigDir = Join-Path $env:LOCALAPPDATA "kc"
    $kcConfigPath = Join-Path $kcConfigDir "config.toml"
    $templatePath = Join-Path $skillDir "config.toml"

    # Only provision if config.toml does not already exist
    if (Test-Path $kcConfigPath) {
        Write-Host "[OK] config.toml already exists, skipping provisioning." -ForegroundColor Green
    } else {
        # Ensure config directory exists
        if (!(Test-Path $kcConfigDir)) {
            New-Item -ItemType Directory -Path $kcConfigDir -Force | Out-Null
        }

        # Copy the bundled template
        if (!(Test-Path $templatePath)) {
            Write-Host "[ERROR] Template config.toml not found at: $templatePath" -ForegroundColor Red
            exit 1
        }
        Copy-Item -Path $templatePath -Destination $kcConfigPath -Force

        Write-Host "[OK] config.toml created from template." -ForegroundColor Green
    }

    # Sync LLM settings from openclaw.json on every launch
    Sync-KcConfigFromOpenClaw -ConfigPath $kcConfigPath -TemplatePath $templatePath
}

Ensure-KcConfig

# --- Launch kc.exe with cleanup on Ctrl+C (supports OpenClaw exec /stop) ---
Write-Host "[OK] Launching kc.exe..." -ForegroundColor Green
$quotedArgs = ($KcArgs + @("--no-daemon", "--gui-floating")) | ForEach-Object { if ($_ -match '\s') { "`"$_`"" } else { $_ } }
$kcProcess = Start-Process -FilePath $kcPath -ArgumentList ($quotedArgs -join " ") -NoNewWindow -PassThru
try {
    $kcProcess | Wait-Process
} finally {
    if (!$kcProcess.HasExited) {
        Write-Host "`n[INFO] Stopping kc.exe (PID: $($kcProcess.Id))..." -ForegroundColor Yellow
        Stop-Process -Id $kcProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
exit $kcProcess.ExitCode
