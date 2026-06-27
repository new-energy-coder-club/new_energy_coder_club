<#
.SYNOPSIS
  Kimi CLI 环境自动安装脚本 — 一键完成 PATH 配置 + Git for Windows 安装 + 环境验证

.DESCRIPTION
  在全新 Windows 系统上自动完成 Kimi CLI 运行环境搭建：
  1. 检测 kimi.exe 位置并加入用户 PATH
  2. 检测 Git Bash 是否安装，如缺失则通过 winget 自动安装
  3. 配置 KIMI_SHELL_PATH 环境变量
  4. 刷新当前会话 PATH 并验证 kimi 可运行

.PARAMETER SkipGitInstall
  跳过 Git for Windows 安装（仅做检测和提示）

.PARAMETER KimiShellPath
  自定义 bash.exe 路径（默认自动检测已知路径）

.EXAMPLE
  # 完整自动安装
  .\setup.ps1

  # 不自动安装 Git，仅检测和提示
  .\setup.ps1 -SkipGitInstall
#>

param(
  [switch]$SkipGitInstall,
  [string]$KimiShellPath = ""
)

# ============================================================
# 配置常量
# ============================================================
$KIMI_DEFAULT_DIR = "$env:USERPROFILE\.kimi-code\bin"
$KIMI_EXE_NAME = "kimi.exe"
$GIT_CHECK_PATHS = @(
  "C:\Program Files\Git\bin\bash.exe",
  "C:\Program Files\Git\usr\bin\bash.exe",
  "C:\Program Files (x86)\Git\bin\bash.exe",
  "C:\Program Files (x86)\Git\usr\bin\bash.exe",
  "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe",
  "$env:LOCALAPPDATA\Programs\Git\usr\bin\bash.exe"
)

# ============================================================
# 辅助函数
# ============================================================
function Write-Step {
  param([string]$Message)
  Write-Host "`n━━━ $Message ━━━" -ForegroundColor Cyan
}

function Write-Success {
  param([string]$Message)
  Write-Host "  ✅ $Message" -ForegroundColor Green
}

function Write-Info {
  param([string]$Message)
  Write-Host "  ℹ️  $Message" -ForegroundColor Yellow
}

function Write-Error {
  param([string]$Message)
  Write-Host "  ❌ $Message" -ForegroundColor Red
}

# ============================================================
# 主流程
# ============================================================
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║   Kimi CLI 环境自动搭建工具              ║" -ForegroundColor Magenta
Write-Host "║   kimi-env-setup (v1.0)                 ║" -ForegroundColor Magenta
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Magenta

# ---- 步骤 1: 检测并配置 kimi PATH ----
Write-Step "步骤 1/5：检测 Kimi CLI 路径"

$kimiFoundInPath = $false
$kimiPath = ""

# 1a. 在 PATH 中查找
try {
  $kimiPath = (Get-Command $KIMI_EXE_NAME -ErrorAction Stop).Source
  $kimiFoundInPath = $true
  Write-Success "已找到 $KIMI_EXE_NAME：$kimiPath"
} catch {
  Write-Info "PATH 中未找到 kimi，检查默认安装位置..."
}

# 1b. 检查默认安装目录
if (-not $kimiFoundInPath) {
  $defaultKimiExe = Join-Path $KIMI_DEFAULT_DIR $KIMI_EXE_NAME
  if (Test-Path $defaultKimiExe) {
    $kimiPath = $defaultKimiExe
    Write-Info "在默认目录找到 kimi.exe：$defaultKimiExe"

    # 添加到用户 PATH
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notlike "*$KIMI_DEFAULT_DIR*") {
      [Environment]::SetEnvironmentVariable('Path', "$userPath;$KIMI_DEFAULT_DIR", 'User')
      Write-Success "已将 $KIMI_DEFAULT_DIR 添加到用户 PATH（永久生效）"
    } else {
      Write-Info "$KIMI_DEFAULT_DIR 已在 PATH 中，跳过"
    }

    # 刷新当前会话 PATH
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' +
                [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $kimiFoundInPath = $true
  } else {
    Write-Error "未找到 kimi.exe！默认位置：$defaultKimiExe"
    Write-Info "请先安装 Kimi CLI：npm install -g kimi-cli"
  }
}

if (-not $kimiFoundInPath) {
  Write-Error "Kimi CLI 未安装，无法继续。"
  exit 1
}

# ---- 步骤 2: 检测 Git Bash ----
Write-Step "步骤 2/5：检测 Git Bash"

$gitFound = $false
$gitBashPath = ""

# 如果传入了自定义路径，优先使用
if ($KimiShellPath -ne "" -and (Test-Path $KimiShellPath)) {
  $gitFound = $true
  $gitBashPath = $KimiShellPath
  Write-Success "使用自定义 bash 路径：$gitBashPath"
}

# 检测已知 Git 安装路径
if (-not $gitFound) {
  foreach ($p in $GIT_CHECK_PATHS) {
    if (Test-Path $p) {
      $gitFound = $true
      $gitBashPath = $p
      Write-Success "找到 Git Bash：$p"
      break
    }
  }
}

# 检测 PATH 中的 git
if (-not $gitFound) {
  try {
    $gitPath = (Get-Command "git" -ErrorAction Stop).Source
    $gitDir = Split-Path (Split-Path $gitPath -Parent) -Parent
    $possibleBash = Join-Path $gitDir "bin\bash.exe"
    if (Test-Path $possibleBash) {
      $gitFound = $true
      $gitBashPath = $possibleBash
      Write-Success "通过 git 命令找到 Git Bash：$possibleBash"
    }
  } catch {
    Write-Info "PATH 中未找到 git 命令。"
  }
}

# ---- 步骤 3: 安装 Git for Windows（如需要） ----
Write-Step "步骤 3/5：安装 Git for Windows（如需）"

if ($gitFound) {
  Write-Success "Git Bash 已就绪：$gitBashPath"
} else {
  if ($SkipGitInstall) {
    Write-Info "已跳过 Git 安装（-SkipGitInstall 参数）"
    Write-Info "请手动安装 Git for Windows：https://gitforwindows.org/"
  } else {
    Write-Info "未找到 Git Bash，正在通过 winget 安装..."

    try {
      $wingetPath = (Get-Command "winget" -ErrorAction Stop).Source
      Write-Info "winget 路径：$wingetPath"
    } catch {
      Write-Error "未找到 winget。请手动安装 Git for Windows：https://gitforwindows.org/"
      Write-Info "安装后重新运行本脚本。"
      exit 1
    }

    Write-Host "⏳ 正在安装 Git for Windows..." -ForegroundColor Yellow
    $installResult = & $wingetPath install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements 2>&1

    if ($LASTEXITCODE -eq 0) {
      Write-Success "Git for Windows 安装成功！"

      # 重新检测 Git Bash
      Start-Sleep -Seconds 3
      foreach ($p in $GIT_CHECK_PATHS) {
        if (Test-Path $p) {
          $gitFound = $true
          $gitBashPath = $p
          Write-Success "Git Bash 已就绪：$p"
          break
        }
      }
    } else {
      Write-Error "安装失败，退出码：$LASTEXITCODE"
      Write-Info "输出内容：$installResult"
      Write-Info "请手动安装 Git for Windows：https://gitforwindows.org/"
    }
  }
}

# ---- 步骤 4: 配置 KIMI_SHELL_PATH（如需要） ----
Write-Step "步骤 4/5：配置 KIMI_SHELL_PATH 环境变量"

if ($gitFound -and $gitBashPath -ne "") {
  $currentShellPath = [Environment]::GetEnvironmentVariable('KIMI_SHELL_PATH', 'User')
  if ($currentShellPath -eq "" -or -not (Test-Path $currentShellPath)) {
    [Environment]::SetEnvironmentVariable('KIMI_SHELL_PATH', $gitBashPath, 'User')
    $env:KIMI_SHELL_PATH = $gitBashPath
    Write-Success "KIMI_SHELL_PATH 已设置为：$gitBashPath"
  } else {
    Write-Info "KIMI_SHELL_PATH 已配置：$currentShellPath（跳过）"
  }
} else {
  Write-Info "Git Bash 未安装，跳过 KIMI_SHELL_PATH 配置"
}

# ---- 步骤 5: 验证 ----
Write-Step "步骤 5/5：验证 Kimi CLI"

try {
  $kimiVersion = & $kimiPath --version 2>&1
  Write-Success "kimi 命令可正常执行"
  Write-Host "  版本信息：$kimiVersion" -ForegroundColor Gray

  # 额外测试：检查 kimi 能否正常启动
  Write-Info "尝试运行 kimi --help..."
  $helpOutput = & $kimiPath --help 2>&1 | Select-Object -First 3
  Write-Host "  $($helpOutput -join "`n  ")" -ForegroundColor Gray
  Write-Success "Kimi CLI 环境搭建完成！"
} catch {
  Write-Error "kimi 命令执行失败：$_"
  Write-Info "请检查安装后重新运行本脚本。"
  exit 1
}

# ============================================================
# 最终报告
# ============================================================
Write-Host "`n╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   ✅ 环境搭建完成！                     ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📋 安装报告" -ForegroundColor Cyan
Write-Host "  • Kimi CLI 路径    : $kimiPath" -ForegroundColor White
Write-Host "  • Git Bash 路径    : $(if ($gitBashPath) { $gitBashPath } else { '未安装' })" -ForegroundColor White
Write-Host "  • KIMI_SHELL_PATH  : $(if ($env:KIMI_SHELL_PATH) { $env:KIMI_SHELL_PATH } else { '未设置' })" -ForegroundColor White
Write-Host ""
Write-Host "💡 请打开新的 PowerShell 终端，然后运行：" -ForegroundColor Yellow
Write-Host "   kimi --version" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 参考链接" -ForegroundColor Cyan
Write-Host "  • Git for Windows  : https://gitforwindows.org/" -ForegroundColor Gray
Write-Host "  • Kimi CLI 文档    : https://kimi.moonshot.cn/" -ForegroundColor Gray
