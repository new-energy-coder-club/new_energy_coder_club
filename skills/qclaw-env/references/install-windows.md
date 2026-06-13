# Windows 环境安装手册

面向大模型的 Windows 全链路安装指引。推荐使用 **PowerShell** 执行安装命令。

**关于管理员权限**：大部分安装命令在**普通 PowerShell** 中即可执行。推荐使用的 Scoop **无需管理员权限**；仅 Chocolatey 安装和部分 winget 操作需要管理员 PowerShell。下文会在需要管理员权限的步骤中明确标注。

---

## 全量环境快照 [首先执行]

**任何安装操作前，必须先执行此快照**，了解系统已有工具，避免重复安装。

```powershell
Write-Host "=== Windows 环境快照 ==="
Write-Host "--- 平台 ---"
$ver = [System.Environment]::OSVersion.Version
Write-Host "Windows Build: $($ver.Major).$($ver.Minor).$($ver.Build)"
Write-Host "架构: $(if ([Environment]::Is64BitOperatingSystem) {'x64'} else {'x86'})"
Write-Host "PowerShell: $($PSVersionTable.PSVersion)"
Write-Host ""

Write-Host "--- Shell 与执行策略 ---"
$policy = Get-ExecutionPolicy -Scope CurrentUser
Write-Host "执行策略 (CurrentUser): $policy"
if ($policy -eq "Restricted") {
    Write-Host "  警告: 执行策略为 Restricted，安装 Scoop 前需修改为 RemoteSigned"
}
Write-Host ""

Write-Host "--- 系统预装工具 ---"
# curl.exe (Windows 10 1803+)
$curl = Get-Command curl.exe -ErrorAction SilentlyContinue
if ($curl) { Write-Host "curl.exe: 已预装" } else { Write-Host "curl.exe: 未预装 (Windows 10 1803 以下)" }
# tar (Windows 10 1803+)
$tar = Get-Command tar -ErrorAction SilentlyContinue
if ($tar) { Write-Host "tar: 已预装" } else { Write-Host "tar: 未预装 (解压 .tar.bz2 需要 7-Zip)" }
Write-Host ""

Write-Host "--- 包管理器 ---"
foreach ($pm in @("scoop", "winget", "choco")) {
    $c = Get-Command $pm -ErrorAction SilentlyContinue
    if ($c) {
        try { $v = & $pm --version 2>&1 | Select-Object -First 1; Write-Host "$pm`: $v" }
        catch { Write-Host "$pm`: 已安装" }
    } else { Write-Host "$pm`: 未安装" }
}
Write-Host ""

Write-Host "--- 基础运行时 ---"
foreach ($cmd in @("node", "npm", "python", "pip", "go", "uv", "git")) {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($c) {
        try { $v = & $cmd --version 2>&1 | Select-Object -First 1; Write-Host "$cmd`: $v" }
        catch { Write-Host "$cmd`: 已安装 (版本获取失败)" }
    } else { Write-Host "$cmd`: 未安装" }
}
Write-Host ""

Write-Host "--- CLI 工具 ---"
foreach ($cmd in @("gh", "jq", "rg", "ffmpeg", "whisper", "clawhub", "claude", "codex", "opencode", "pi", "himalaya", "oracle", "mcporter", "gifgrep", "blogwatcher", "obsidian-cli", "nano-pdf", "songsee", "summarize", "sag")) {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($c) { Write-Host "$cmd`: 已安装" } else { Write-Host "$cmd`: 未安装" }
}
```

---

## 第 0 层：网络环境配置

**国内用户必读**。Windows 安装工具依赖的主要境外源（GitHub、npm、PyPI）在国内直连速度慢或不可达，安装前**必须先配置镜像**。

### 网络连通性检测

```powershell
# 依次检测主要源是否可达（超时 3 秒，含响应速度判定）
Write-Host "=== 网络连通性检测 ==="
$needMirror = $false
@("https://github.com", "https://raw.githubusercontent.com", "https://registry.npmjs.org", "https://pypi.org") | ForEach-Object {
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        Invoke-WebRequest -Uri $_ -TimeoutSec 3 -UseBasicParsing | Out-Null
        $sw.Stop()
        if ($sw.ElapsedMilliseconds -gt 2000) {
            "慢速 ($($sw.ElapsedMilliseconds)ms): $_ — 建议配置镜像"
            $needMirror = $true
        } else {
            "可达 ($($sw.ElapsedMilliseconds)ms): $_"
        }
    } catch {
        "不可达: $_ — 必须配置镜像"
        $needMirror = $true
    }
}
if ($needMirror) { Write-Host "`n>>> 检测到境外源不可达或慢速，必须先配置镜像再继续安装 <<<" }
```

**判定规则**:
- 任一源不可达 → **必须**先完成下方镜像配置
- 任一源响应超过 2 秒 → **强烈建议**配置镜像
- 全部可达且速度正常 → 可跳到第 1 层

### npm 镜像

```powershell
# 检测当前 registry（需 npm 已安装）
npm config get registry

# 配置国内镜像（npmmirror）
npm config set registry https://registry.npmmirror.com

# 验证
npm config get registry
# 应输出 https://registry.npmmirror.com/
```

### pip 镜像（清华源）

```powershell
# 配置清华 PyPI 镜像（需 pip 已安装）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 验证
pip config get global.index-url
```

### Go 模块代理

```powershell
# 配置 Go 代理（七牛云，需 go 已安装）
go env -w GOPROXY=https://goproxy.cn,direct

# 或设置为持久环境变量
[System.Environment]::SetEnvironmentVariable("GOPROXY", "https://goproxy.cn,direct", "User")
```

### Scoop 代理/镜像配置

```powershell
# 如果有代理（Scoop 已安装时）
scoop config proxy 127.0.0.1:端口号

# 取消代理
scoop config rm proxy

# 将 Scoop 切换到 Gitee 源（国内加速）
scoop config SCOOP_REPO 'https://gitee.com/glsnames/scoop-installer'
```

### GitHub Releases 下载加速

部分工具（sherpa-onnx-tts、gifgrep 等）需从 GitHub Releases 下载二进制文件。如直连 GitHub 下载慢：

1. **使用代理**：如果已有代理，在 PowerShell 中设置 `$env:HTTPS_PROXY = "http://127.0.0.1:<端口>"`
2. **手动下载**：在浏览器中使用下载工具获取文件后，手动放到目标目录
3. **使用 ghproxy 等加速服务**：将 `https://github.com/` 替换为 `https://mirror.ghproxy.com/https://github.com/`（第三方服务，可用性不保证）

---

## 第 1 层：包管理器

### 包管理器选择决策树

安装前先检测已有的包管理器，**检测到什么就用什么，不要在已有包管理器的系统上安装新的包管理器**：

```
1. Get-Command scoop → 存在？ → 使用 Scoop
2. Get-Command winget → 存在？ → 使用 winget
3. Get-Command choco → 存在？ → 使用 Chocolatey
4. 全部不存在 → 安装 Scoop（首选）
5. Scoop 安装失败 → 尝试 Scoop 国内镜像
6. 国内镜像也失败 → 检测 winget 是否可用（Windows 11 预装）
7. winget 也不可用 → 使用降级方案（从官网下载 .msi 安装包）
```

### Scoop（推荐，无需管理员权限）

- 检测: `Get-Command scoop -ErrorAction SilentlyContinue`
- 前置检测（执行策略）:
  ```powershell
  $policy = Get-ExecutionPolicy -Scope CurrentUser
  if ($policy -eq "Restricted") {
      Write-Host "执行策略为 Restricted，需修改为 RemoteSigned"
      Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  } else {
      Write-Host "执行策略已满足要求: $policy"
  }
  ```
- 安装（**国内首选 — 使用 Gitee 镜像**）:
  ```powershell
  irm https://gitee.com/glsnames/scoop-installer/raw/master/bin/install.ps1 | iex
  ```
- 安装（海外/可直连）:
  ```powershell
  irm get.scoop.sh | iex
  ```
- 验证: `scoop --version`
- 安装后（添加常用 bucket）:
  ```powershell
  scoop bucket add extras
  scoop bucket add versions
  ```
- 安装失败处理:
  - 如果下载超时 → 切换到国内 Gitee 镜像安装
  - 如果 PowerShell 报执行策略错误 → 先执行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
  - 如果反复失败 → 尝试 winget 或跳转到「降级方案」

### winget（Windows 10 1709+ / Windows 11 预装）

- 检测: `Get-Command winget -ErrorAction SilentlyContinue`
- 安装: Windows 11 预装。Windows 10 需从 Microsoft Store 安装「应用安装程序」或从 https://github.com/microsoft/winget-cli/releases 下载
- 验证: `winget --version`
- 说明: winget 是 Windows 官方包管理器，无需第三方安装脚本，但 Windows 10 上可能不预装

### Chocolatey（备选，**需管理员 PowerShell**）

- 检测: `Get-Command choco -ErrorAction SilentlyContinue`
- 安装（**管理员 PowerShell**）:
  ```powershell
  Set-ExecutionPolicy Bypass -Scope Process -Force
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
  ```
- 验证: `choco --version`
- 注意: Chocolatey 需要管理员权限，仅在 Scoop 和 winget 都不可用时作为最后选择

---

## 第 2 层：基础运行时

**重要**: Windows 上使用 `python` 和 `pip` 命令（而非 `python3`/`pip3`）。PowerShell 中 `curl` 是 `Invoke-WebRequest` 的别名，必须使用 `curl.exe` 调用真实 curl。

### Node.js + npm

- 检测: `Get-Command node -ErrorAction SilentlyContinue`
- 安装（Scoop）: `scoop install nodejs`
- 安装（winget）: `winget install OpenJS.NodeJS.LTS`
- 安装（Chocolatey）: `choco install nodejs-lts -y`
- 安装（**降级方案 — 无包管理器时**）:
  1. 访问 https://nodejs.org/
  2. 下载 Windows .msi 安装包（LTS 版本）
  3. 运行安装程序（需用户操作，勾选 "Add to PATH"）
  4. 或用 PowerShell 下载:
     ```powershell
     # 以 Node.js 22.x LTS 为例
     Invoke-WebRequest -Uri "https://nodejs.org/dist/v22.12.0/node-v22.12.0-x64.msi" -OutFile "$env:TEMP\nodejs.msi"
     Start-Process msiexec.exe -ArgumentList "/i", "$env:TEMP\nodejs.msi", "/passive" -Wait
     Remove-Item "$env:TEMP\nodejs.msi"
     # 重新打开 PowerShell 使 PATH 生效
     ```
- 验证: `node --version; npm --version`
- 安装后（**国内网络必须立即执行，不要等到后续步骤**）:
  ```powershell
  npm config set registry https://registry.npmmirror.com
  npm config get registry  # 验证: 应输出 https://registry.npmmirror.com/
  ```
  海外/可直连用户可跳过此步。详见第 0 层 npm 镜像章节。

### Python + pip

- 检测:
  ```powershell
  # Windows 上检测 python（非 python3）
  $py = Get-Command python -ErrorAction SilentlyContinue
  if ($py) {
      # 排除 Windows Store 的 stub（路径包含 WindowsApps）
      if ($py.Source -match "WindowsApps") {
          Write-Host "python 是 Windows Store stub，需安装真实 Python"
      } else {
          $ver = python --version 2>&1
          Write-Host "python 可用: $ver"
      }
  } else {
      Write-Host "python 未安装"
  }
  ```
- 安装（Scoop）: `scoop install python`
- 安装（winget）: `winget install Python.Python.3.12`
- 安装（Chocolatey）: `choco install python -y`
- 安装（**降级方案 — 无包管理器时**）:
  1. 访问 https://mirrors.huaweicloud.com/python/3.12.8/ （华为云镜像，国内高速）
  2. 下载 `python-3.12.8-amd64.exe` 安装程序
  3. 运行安装程序（**勾选 "Add Python to PATH"**）
  4. 或用 PowerShell 下载:
     ```powershell
     # 以 Python 3.12.x 为例（华为云镜像，国内高速）
     Invoke-WebRequest -Uri "https://mirrors.huaweicloud.com/python/3.12.8/python-3.12.8-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"
     Start-Process "$env:TEMP\python-installer.exe" -ArgumentList "/passive", "InstallAllUsers=0", "PrependPath=1" -Wait
     Remove-Item "$env:TEMP\python-installer.exe"
     # 重新打开 PowerShell 使 PATH 生效
     ```
- 验证: `python --version; pip --version`
- **重要**: Windows 上使用 `python` 和 `pip`（**不是** `python3`/`pip3`）。Windows 10/11 自带的 `python3.exe` 可能是指向 Microsoft Store 的 stub，不是真实 Python。
- 安装后（**国内网络必须立即执行，不要等到后续步骤**）:
  ```powershell
  pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
  pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
  pip config get global.index-url  # 验证
  ```
  海外/可直连用户可跳过此步。详见第 0 层 pip 镜像章节。

### Go

- 检测: `Get-Command go -ErrorAction SilentlyContinue`
- 安装（Scoop）: `scoop install go`
- 安装（winget）: `winget install GoLang.Go`
- 安装（Chocolatey）: `choco install golang -y`
- 安装（**降级方案 — 无包管理器时**）:
  1. 访问 https://go.dev/dl/
  2. 下载 Windows .msi 安装包
  3. 运行安装程序
  4. 或用 PowerShell 下载:
     ```powershell
     Invoke-WebRequest -Uri "https://go.dev/dl/go1.23.4.windows-amd64.msi" -OutFile "$env:TEMP\go-installer.msi"
     Start-Process msiexec.exe -ArgumentList "/i", "$env:TEMP\go-installer.msi", "/passive" -Wait
     Remove-Item "$env:TEMP\go-installer.msi"
     # 重新打开 PowerShell 使 PATH 生效
     ```
- 验证: `go version`
- 安装后: 配置 Go 代理（见第 0 层），确保 `%GOPATH%\bin` 在 PATH 中:
  ```powershell
  $gopath = go env GOPATH
  $currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
  if ($currentPath -notmatch [regex]::Escape("$gopath\bin")) {
      [System.Environment]::SetEnvironmentVariable("PATH", "$currentPath;$gopath\bin", "User")
      Write-Host "已将 $gopath\bin 添加到 PATH，请重新打开 PowerShell"
  }
  ```

### uv

- 检测: `Get-Command uv -ErrorAction SilentlyContinue`
- 安装（首选 — 独立安装脚本）: `irm https://astral.sh/uv/install.ps1 | iex`
- 安装（Scoop）: `scoop install uv`
- 安装（winget）: `winget install astral-sh.uv`
- 验证: `uv --version`

### curl（Windows 10+ 预装）

- 检测: `Get-Command curl.exe -ErrorAction SilentlyContinue`
- 安装: Windows 10 1803+ 预装 `curl.exe`
- 注意: PowerShell 中 `curl` 是 `Invoke-WebRequest` 的别名，必须使用 `curl.exe` 调用真实 curl
- 版本检测: `curl.exe --version`

### git

- 检测: `Get-Command git -ErrorAction SilentlyContinue`
- 安装（Scoop）: `scoop install git`
- 安装（winget）: `winget install Git.Git`
- 验证: `git --version`
- 说明: Scoop 安装某些 bucket 时也需要 git，建议优先安装

---

## 降级方案汇总

当所有包管理器（Scoop/winget/Chocolatey）都不可用时，基础运行时可从官网下载安装包直接安装。**此方案不依赖任何包管理器，成功率最高。**

| 运行时 | 下载地址 | 安装方式 |
|--------|---------|---------|
| Node.js | https://nodejs.org/ | .msi 安装包，勾选 Add to PATH |
| Python | https://mirrors.huaweicloud.com/python/3.12.8/ （华为云镜像） | .exe 安装程序，勾选 Add Python to PATH |
| Go | https://go.dev/dl/ | .msi 安装包 |
| uv | N/A | `irm https://astral.sh/uv/install.ps1 \| iex`（不依赖包管理器） |
| git | https://git-scm.com/download/win | .exe 安装程序 |

**注意**:
- .msi/.exe 安装通常需要用户手动操作安装向导
- 安装后需要**重新打开 PowerShell**使 PATH 生效
- Agent 可使用 `Start-Process ... -Wait` 的 passive 模式自动化安装

---

## 第 3 层：Skill CLI 依赖

### 无需安装的 Skill

以下 skill 不需要额外安装外部工具：

- **canvas** — 内置功能
- **healthcheck** — 内置功能
- **qclaw-skill-creator** — 内置功能
- **weather** — 仅依赖 `curl.exe`（Windows 10+ 预装）
- **openai-whisper-api** — 仅依赖 `curl.exe`（Windows 10+ 预装），另需 `OPENAI_API_KEY` 环境变量
- **voice-call** — 需在 `openclaw.json` 中配置 `plugins.entries.voice-call.enabled: true`

### 不支持的 Skill（macOS 专属）

以下 skill 依赖 macOS 原生 API，**Windows 不支持**：
- apple-notes (memo) — 依赖 macOS Apple Notes API
- apple-reminders (remindctl) — 依赖 macOS Reminders API
- model-usage (codexbar) — 依赖 macOS 桌面环境
- peekaboo — 依赖 macOS Accessibility API
- camsnap — 依赖 macOS AVFoundation 框架

### 不支持的 Skill（不适用于 Windows）

- tmux — 无原生 Windows 版本。如需终端复用，可在 WSL 内安装

---

### blogwatcher — `blogwatcher`

- 前置运行时: go（安装后需先配置 Go 代理，见第 0 层）
- 检测: `Get-Command blogwatcher -ErrorAction SilentlyContinue`
- 安装: `go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest`
- 验证: `blogwatcher --version`
- 注意: 确保 `%GOPATH%\bin` 在 PATH 中

### clawhub — `clawhub`

- 前置运行时: node+npm（安装后需先配置 npm 镜像，见第 0 层）
- 检测: `Get-Command clawhub -ErrorAction SilentlyContinue`
- 安装: `npm install -g clawhub`
- 验证: `clawhub --version`

### coding-agent — `claude` / `codex` / `opencode` / `pi`（任一）

- 前置运行时: node+npm
- 检测: `Get-Command claude -ErrorAction SilentlyContinue` （或 codex/opencode/pi）
- 安装（**任选一个**即可，无需全部安装）:
  - Claude Code: `npm install -g @anthropic-ai/claude-code`
  - Codex: `npm install -g @openai/codex`
  - Pi: `npm install -g @mariozechner/pi-coding-agent`
  - OpenCode: 参见 https://github.com/opencode-ai/opencode
- 验证: `claude --version` / `codex --version` / `pi --version`

### gh-issues — `curl.exe` + `git` + `gh`

- 检测: `Get-Command curl.exe -ErrorAction SilentlyContinue; Get-Command git -ErrorAction SilentlyContinue; Get-Command gh -ErrorAction SilentlyContinue`
- curl.exe: Windows 10+ 预装
- git: 见上方安装
- gh: 同下方 github skill
- 环境变量: `GH_TOKEN`（通过 `gh auth login` 配置）

### gifgrep — `gifgrep`

- 检测: `Get-Command gifgrep -ErrorAction SilentlyContinue`
- 安装: `go install github.com/steipete/gifgrep/cmd/gifgrep@latest`（需 Go）
- 备选: 从 https://github.com/steipete/gifgrep/releases 下载 Windows 二进制
- 验证: `gifgrep --version`

### github — `gh`

- 检测: `Get-Command gh -ErrorAction SilentlyContinue`
- 安装（Scoop）: `scoop install gh`
- 安装（winget）: `winget install GitHub.cli`
- 安装（Chocolatey）: `choco install gh -y`
- 验证: `gh --version`
- 安装后: `gh auth login`

### himalaya — `himalaya`

- 检测: `Get-Command himalaya -ErrorAction SilentlyContinue`
- 安装（Scoop）: `scoop install himalaya`
- 安装（winget）: `winget install pimalaya.himalaya`
- 备选: 从 https://github.com/pimalaya/himalaya/releases 下载 Windows 二进制
- 验证: `himalaya --version`

### mcporter — `mcporter`

- 前置运行时: node+npm
- 检测: `Get-Command mcporter -ErrorAction SilentlyContinue`
- 安装: `npm install -g mcporter`
- 验证: `mcporter --version`

### nano-banana-pro — `uv`

- 前置运行时: uv
- 检测: `Get-Command uv -ErrorAction SilentlyContinue`
- 安装: 见上方 uv 安装
- 环境变量: `GEMINI_API_KEY`（从 https://ai.google.dev/ 获取）

### nano-pdf — `nano-pdf`

- 前置运行时: uv（依赖链：scoop → uv → nano-pdf）
- 检测: `Get-Command nano-pdf -ErrorAction SilentlyContinue`
- 安装: `uv tool install nano-pdf`
- 验证: `nano-pdf --version`

### obsidian — `obsidian-cli`

- 检测: `Get-Command obsidian-cli -ErrorAction SilentlyContinue`
- 安装: 从 https://github.com/yakitrak/obsidian-cli/releases 下载 Windows 二进制
- 验证: `obsidian-cli --version`
- 注意: 下载后将可执行文件放入 PATH 目录中

### openai-image-gen — `python`

- 前置运行时: python
- 检测:
  ```powershell
  $py = Get-Command python -ErrorAction SilentlyContinue
  if ($py -and $py.Source -notmatch "WindowsApps") { "python 可用" } else { "python 未安装或为 Store stub" }
  ```
- 安装: 见上方 Python 安装
- 环境变量: `OPENAI_API_KEY`（从 https://platform.openai.com/ 获取）

### openai-whisper — `whisper`

- 前置运行时: python+pip **和** ffmpeg（两者都需要）
- 检测: `Get-Command whisper -ErrorAction SilentlyContinue; Get-Command ffmpeg -ErrorAction SilentlyContinue`
- 安装:
  1. 先安装 ffmpeg:
     - Scoop: `scoop install ffmpeg`
     - winget: `winget install Gyan.FFmpeg`
     - Chocolatey: `choco install ffmpeg -y`
  2. 再安装 whisper: `pip install openai-whisper`
- 验证: `whisper --help; ffmpeg -version`

### oracle — `oracle`

- 前置运行时: node+npm
- 检测: `Get-Command oracle -ErrorAction SilentlyContinue`
- 安装: `npm install -g @steipete/oracle`
- 验证: `oracle --version`

### sag — `sag`

- 检测: `Get-Command sag -ErrorAction SilentlyContinue`
- 安装: 从 https://github.com/steipete/sag/releases 下载 Windows 二进制
- 验证: `sag --version`
- 环境变量: `ELEVENLABS_API_KEY`（从 https://elevenlabs.io 获取）

### session-logs — `jq` + `rg`

- 检测: `Get-Command jq -ErrorAction SilentlyContinue; Get-Command rg -ErrorAction SilentlyContinue`
- 安装（Scoop）: `scoop install jq ripgrep`
- 安装（winget）: `winget install jqlang.jq; winget install BurntSushi.ripgrep.MSVC`
- 安装（Chocolatey）: `choco install jq ripgrep -y`
- 验证: `jq --version; rg --version`

### sherpa-onnx-tts — 运行时 + 模型下载

- 检测: `Test-Path $env:SHERPA_ONNX_RUNTIME_DIR; Test-Path $env:SHERPA_ONNX_MODEL_DIR`
- 前置检测:
  ```powershell
  # 检测 tar 和 7-Zip 可用性（解压 .tar.bz2 需要其中之一）
  $hasTar = Get-Command tar -ErrorAction SilentlyContinue
  $has7z = Get-Command 7z -ErrorAction SilentlyContinue
  if (-not $hasTar -and -not $has7z) {
      Write-Host "需要先安装 7-Zip 用于解压: scoop install 7zip"
  }
  ```
- 安装（分步执行，每步验证）:

  **步骤 1: 创建目录**
  ```powershell
  $toolDir = "$env:USERPROFILE\.openclaw\tools\sherpa-onnx-tts"
  New-Item -ItemType Directory -Force -Path "$toolDir\runtime", "$toolDir\models"
  Get-ChildItem $toolDir
  # 验证: 应看到 runtime 和 models 两个目录
  ```

  **步骤 2: 获取版本号**
  ```powershell
  try {
      $release = Invoke-RestMethod -Uri "https://api.github.com/repos/k2-fsa/sherpa-onnx/releases/latest" -TimeoutSec 10
      $SHERPA_VERSION = $release.tag_name
  } catch {
      $SHERPA_VERSION = "v1.12.23"
  }
  Write-Host "使用版本: $SHERPA_VERSION"
  # 验证: 应输出 v1.xx.xx 格式的版本号
  ```

  **步骤 3: 下载运行时**
  ```powershell
  $runtimeUrl = "https://github.com/k2-fsa/sherpa-onnx/releases/download/$SHERPA_VERSION/sherpa-onnx-$SHERPA_VERSION-win-x64-shared.tar.bz2"
  Invoke-WebRequest -Uri $runtimeUrl -OutFile "$toolDir\runtime.tar.bz2"
  # 验证下载: 文件大小应 > 10MB
  (Get-Item "$toolDir\runtime.tar.bz2").Length / 1MB
  ```

  **步骤 4: 解压运行时（根据可用工具选择）**
  ```powershell
  # 方式 A: 使用 tar（Windows 10 1803+）
  if (Get-Command tar -ErrorAction SilentlyContinue) {
      tar -xjf "$toolDir\runtime.tar.bz2" --strip-components=1 -C "$toolDir\runtime"
  }
  # 方式 B: 使用 7-Zip
  elseif (Get-Command 7z -ErrorAction SilentlyContinue) {
      7z x "$toolDir\runtime.tar.bz2" -o"$toolDir" -y
      7z x "$toolDir\runtime.tar" -o"$toolDir\runtime" -y
      Remove-Item "$toolDir\runtime.tar"
  }
  else {
      Write-Host "错误: 需要 tar 或 7-Zip 来解压。请先安装: scoop install 7zip"
  }
  Remove-Item "$toolDir\runtime.tar.bz2" -ErrorAction SilentlyContinue
  # 验证: 应看到 lib/ 目录和 .dll 文件
  Get-ChildItem "$toolDir\runtime\lib\" -ErrorAction SilentlyContinue
  ```

  **步骤 5: 下载并解压模型（同上方式选择）**
  ```powershell
  Invoke-WebRequest -Uri "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-lessac-high.tar.bz2" -OutFile "$toolDir\models.tar.bz2"
  if (Get-Command tar -ErrorAction SilentlyContinue) {
      tar -xjf "$toolDir\models.tar.bz2" -C "$toolDir\models"
  } elseif (Get-Command 7z -ErrorAction SilentlyContinue) {
      7z x "$toolDir\models.tar.bz2" -o"$toolDir" -y
      7z x "$toolDir\models.tar" -o"$toolDir\models" -y
      Remove-Item "$toolDir\models.tar"
  }
  Remove-Item "$toolDir\models.tar.bz2" -ErrorAction SilentlyContinue
  # 验证: 应看到模型文件
  Get-ChildItem "$toolDir\models\vits-piper-en_US-lessac-high\" -ErrorAction SilentlyContinue
  ```

- 安装后: 在 `~/.openclaw/openclaw.json` 中配置:
  ```json5
  { skills: { entries: { "sherpa-onnx-tts": { env: {
    SHERPA_ONNX_RUNTIME_DIR: "%USERPROFILE%\\.openclaw\\tools\\sherpa-onnx-tts\\runtime",
    SHERPA_ONNX_MODEL_DIR: "%USERPROFILE%\\.openclaw\\tools\\sherpa-onnx-tts\\models\\vits-piper-en_US-lessac-high"
  }}}}}
  ```
- 注意: 如果 GitHub 下载慢，参考第 0 层「GitHub Releases 下载加速」

### songsee — `songsee`

- 检测: `Get-Command songsee -ErrorAction SilentlyContinue`
- 安装: 从 https://github.com/steipete/songsee/releases 下载 Windows 二进制
- 验证: `songsee --version`
- 注意: 下载后将可执行文件放入 PATH 目录（如 `$env:USERPROFILE\scoop\shims`）

### summarize — `summarize`

- 检测: `Get-Command summarize -ErrorAction SilentlyContinue`
- 安装: 从 https://github.com/steipete/summarize/releases 下载 Windows 二进制
- 验证: `summarize --version`

### video-frames — `ffmpeg`

- 检测: `Get-Command ffmpeg -ErrorAction SilentlyContinue`
- 安装（Scoop）: `scoop install ffmpeg`
- 安装（winget）: `winget install Gyan.FFmpeg`
- 安装（Chocolatey）: `choco install ffmpeg -y`
- 验证: `ffmpeg -version`

---

## 第 4 层：环境变量配置

API Key 无法通过命令安装，需引导用户到服务商注册获取。

| 环境变量 | 获取地址 | 相关 skill |
|---------|---------|-----------|
| OPENAI_API_KEY | https://platform.openai.com/ | openai-image-gen, openai-whisper-api |
| GEMINI_API_KEY | https://ai.google.dev/ | nano-banana-pro |
| ELEVENLABS_API_KEY | https://elevenlabs.io | sag |
| GH_TOKEN | 通过 `gh auth login` 配置 | gh-issues |

### 设置方法（推荐：openclaw.json skill env 配置）

在 `~/.openclaw/openclaw.json` 中为对应 skill 设置环境变量，**此方式仅对 OpenClaw 生效，不会污染全局环境**：

```json5
{
  skills: {
    entries: {
      "openai-image-gen": {
        env: { OPENAI_API_KEY: "sk-..." }
      },
      "nano-banana-pro": {
        env: { GEMINI_API_KEY: "..." }
      }
    }
  }
}
```

### 设置方法（备选：系统环境变量）

当前会话:

```powershell
$env:OPENAI_API_KEY = "sk-..."
```

持久化（用户级）:

```powershell
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

持久化（通过 GUI）:
1. 搜索「环境变量」->「编辑系统环境变量」
2. 点击「环境变量」-> 用户变量 ->「新建」
3. 输入变量名和值

---

## 附录：PATH 配置

Windows 上部分工具安装后需要确保其目录在 PATH 中。常见路径:

| 工具 | 默认安装路径 |
|------|------------|
| Go (GOPATH/bin) | `%USERPROFILE%\go\bin` |
| npm global | `%APPDATA%\npm` |
| Scoop | `%USERPROFILE%\scoop\shims` |
| uv tools | `%USERPROFILE%\.local\bin` |
| pip scripts | `%USERPROFILE%\AppData\Local\Programs\Python\Python3xx\Scripts` |

添加 PATH（PowerShell，持久化）:

```powershell
$currentPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
[System.Environment]::SetEnvironmentVariable("PATH", "$currentPath;C:\your\new\path", "User")
```

**重要**: 修改 PATH 后需重新打开终端窗口才能生效。

---

## 常见问题排查

### 网络超时 / 下载失败

**现象**: `npm install -g` 超时、`pip install` 报连接错误、Scoop 安装卡住

**排查**:
1. 确认是否已配置镜像源（第 0 层）
2. 检查当前镜像配置:
   ```powershell
   npm config get registry          # npm
   pip config get global.index-url  # pip
   go env GOPROXY                   # Go
   scoop config proxy               # Scoop
   ```
3. 如果已配置镜像仍然失败，检查是否有代理冲突: `$env:HTTPS_PROXY`

### PowerShell 执行策略报错

**现象**: `cannot be loaded because running scripts is disabled on this system`

**修复**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### `command not found` / 命令无法识别

**排查**:
1. 重新打开 PowerShell 窗口（新会话才能加载新的 PATH）
2. 检查工具是否确实安装成功:
   ```powershell
   # Scoop 安装的工具
   scoop list
   # npm 全局安装的工具
   npm list -g --depth=0
   # Go 安装的工具
   Get-ChildItem "$env:GOPATH\bin" -ErrorAction SilentlyContinue
   # uv 安装的工具
   uv tool list
   ```
3. 手动检查 PATH:
   ```powershell
   $env:PATH -split ';' | Where-Object { $_ -match '(scoop|npm|go|uv|python)' }
   ```

### `tar` 解压 `.tar.bz2` 失败

**现象**: sherpa-onnx-tts 安装时 tar 解压报错

**修复**:
1. 确认 Windows 版本 >= 10 1803（内置 tar）
2. 注意: Windows 内置 tar 对 `.tar.bz2` 的支持可能不完整（依赖 bzip2）
3. 推荐改用 7-Zip:
   ```powershell
   scoop install 7zip    # 如果 scoop 可用
   # 或从 https://www.7-zip.org/ 下载安装
   7z x runtime.tar.bz2
   7z x runtime.tar -oruntime
   ```

### winget 找不到

**现象**: `winget : The term 'winget' is not recognized`

**排查**:
1. 确认 Windows 版本: Windows 10 需 1709+ 且安装了「应用安装程序」
2. 从 Microsoft Store 搜索安装「应用安装程序」
3. 或从 https://github.com/microsoft/winget-cli/releases 手动下载安装
4. Windows 11 通常已预装，重新打开终端试试

### python 指向 Windows Store stub

**现象**: 执行 `python` 弹出 Microsoft Store 页面

**排查**:
1. 检查 python 路径:
   ```powershell
   (Get-Command python).Source
   # 如果路径包含 WindowsApps，说明是 Store stub
   ```
2. 修复: 安装真实 Python（见第 2 层），或在「管理应用执行别名」中关闭 python.exe 别名:
   - 设置 → 应用 → 应用执行别名 → 关闭 python.exe 和 python3.exe

### 安装失败后的清理

```powershell
# Scoop 清理
scoop cache rm *

# npm 缓存清理
npm cache clean --force

# pip 缓存清理
pip cache purge

# Go 模块缓存清理
go clean -modcache
```
