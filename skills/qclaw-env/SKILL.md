---
name: qclaw-env
description: "OpenClaw skill 全链路环境诊断与安装工具。安装任何 CLI、命令行工具、包管理器、运行时环境时必须使用此 skill。使用场景包括但不限于：(1) 安装或配置任何命令行工具或 CLI（如 gh、ffmpeg、whisper 等），(2) 安装 OpenClaw skill 所需的依赖环境（包括底层运行时 node/npm、python3/pip3、go、uv），(3) 遇到 'command not found'、'未找到命令'、'不是内部或外部命令' 等错误，(4) 用户说'帮我装 xxx'、'安装 xxx'、'配置 xxx 环境'、'setup xxx'、'install xxx'，(5) 检测系统已安装哪些工具、检查环境、环境诊断，(6) 安装包管理器（brew、scoop、winget、choco、npm、pip 等），(7) 配置 API Key、环境变量、PATH 等运行时配置，(8) 配置国内镜像源（Homebrew、npm、pip、Go proxy 等）。此 skill 为强制性入口，所有安装类操作必须遵循'先检测后安装'原则。"
metadata: {"openclaw": {"emoji": "⚙️"}}
---

# Env Doctor — OpenClaw Skill 全链路环境诊断与安装

## 强制规范 [MANDATORY]

所有 CLI、工具、运行时、包管理器的安装操作**必须**遵循以下流程，不可跳过任何步骤：

### 步骤 1：检测平台与架构

```bash
# macOS / Linux
OS="$(uname -s)"   # Darwin / Linux
ARCH="$(uname -m)" # arm64 / x86_64
echo "平台: $OS, 架构: $ARCH"
```

```powershell
# Windows (PowerShell)
$OS = "Windows"
$ARCH = if ([Environment]::Is64BitOperatingSystem) { "x64" } else { "x86" }
$WinVer = [System.Environment]::OSVersion.Version
Write-Host "平台: $OS, 架构: $ARCH, Windows 版本: $($WinVer.Major).$($WinVer.Minor).$($WinVer.Build)"
```

**平台支持说明**:
- **macOS (Darwin)** — 完整支持，参考 `install-macos.md`
- **Windows** — 完整支持，参考 `install-windows.md`
- **Linux** — 当前不提供安装手册。如检测到 Linux，告知用户此 skill 暂不支持 Linux，需自行按发行版的包管理器安装所需工具

**macOS 架构标记**：如果 `ARCH=arm64`（Apple Silicon），后续安装 Homebrew 时**必须**执行 `eval "$(/opt/homebrew/bin/brew shellenv)"`，否则所有 brew 安装的工具都无法找到。

### 步骤 2：全量环境快照

在安装任何东西之前，**先一次性探测系统已有的全部工具和版本**，避免重复安装和误判。

```bash
# macOS — 全量环境快照
echo "=== 系统环境快照 ==="
echo "--- 平台 ---"
echo "OS: $(uname -s), ARCH: $(uname -m), macOS: $(sw_vers -productVersion 2>/dev/null || echo 'N/A')"
echo ""
echo "--- Xcode CLT ---"
xcode-select -p >/dev/null 2>&1 && echo "xcode-select: 已安装 ($(xcode-select -p))" || echo "xcode-select: 未安装"
echo ""
echo "--- sudo 免密可用性 ---"
sudo -n true 2>/dev/null && echo "SUDO_OK=true" || echo "SUDO_OK=false (需使用非 sudo 安装方式)"
echo ""
echo "--- 包管理器 ---"
command -v brew >/dev/null 2>&1 && echo "brew: $(brew --version 2>&1 | head -1)" || echo "brew: 未安装"
echo ""
echo "--- 基础运行时 ---"
for cmd in node npm python3 pip3 go uv; do
  if command -v "$cmd" >/dev/null 2>&1; then
    ver="$("$cmd" --version 2>&1 | head -1)"
    echo "$cmd: $ver"
  else
    echo "$cmd: 未安装"
  fi
done
echo ""
echo "--- python3 真实性检测 ---"
python3 -c "import sys; print('python3 可用:', sys.version)" 2>/dev/null || echo "python3: 不可用或为 Xcode CLT stub"
echo ""
echo "--- CLI 工具 ---"
for cmd in curl git gh jq rg ffmpeg tmux whisper memo remindctl clawhub claude codex himalaya uv; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd: 已安装"
  else
    echo "$cmd: 未安装"
  fi
done
```

```powershell
# Windows — 全量环境快照（先切 UTF-8 防乱码）
chcp 65001 >nul
Write-Host "=== 系统环境快照 ==="
Write-Host "--- 平台 ---"
$ver = [System.Environment]::OSVersion.Version
Write-Host "OS: Windows, Build: $($ver.Major).$($ver.Minor).$($ver.Build), Arch: $(if ([Environment]::Is64BitOperatingSystem) {'x64'} else {'x86'})"
Write-Host ""
Write-Host "--- Shell 环境 ---"
Write-Host "当前 Shell: $($PSVersionTable.PSVersion) (PowerShell)"
$policy = Get-ExecutionPolicy -Scope CurrentUser
Write-Host "执行策略 (CurrentUser): $policy"
Write-Host ""
Write-Host "--- 包管理器 ---"
foreach ($pm in @("scoop", "winget", "choco")) {
    $c = Get-Command $pm -ErrorAction SilentlyContinue
    if ($c) { Write-Host "$pm`: 已安装" } else { Write-Host "$pm`: 未安装" }
}
Write-Host ""
Write-Host "--- 基础运行时 ---"
foreach ($cmd in @("node", "npm", "python", "pip", "go", "uv", "curl.exe", "git")) {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($c) {
        try { $v = & $cmd --version 2>&1 | Select-Object -First 1; Write-Host "$cmd`: $v" }
        catch { Write-Host "$cmd`: 已安装 (版本获取失败)" }
    } else { Write-Host "$cmd`: 未安装" }
}
Write-Host ""
Write-Host "--- CLI 工具 ---"
foreach ($cmd in @("gh", "jq", "rg", "ffmpeg", "whisper", "clawhub", "claude", "codex", "himalaya")) {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($c) { Write-Host "$cmd`: 已安装" } else { Write-Host "$cmd`: 未安装" }
}
```

**已安装的工具直接跳过**，仅安装缺失的部分。

### 步骤 3：检测网络环境

安装工具前必须确认网络连通性。国内用户访问境外源（GitHub、npm、Homebrew、PyPI）经常超时，**必须优先配置镜像**。

```bash
# macOS — 网络检测（超时 3 秒判定可达性）
echo "=== 网络连通性检测 ==="
NEED_MIRROR=false
for url in "https://github.com" "https://raw.githubusercontent.com" "https://registry.npmjs.org" "https://pypi.org"; do
  if curl -sI --connect-timeout 3 "$url" > /dev/null 2>&1; then
    echo "可达: $url"
  else
    echo "不可达: $url"
    NEED_MIRROR=true
  fi
done
if [ "$NEED_MIRROR" = true ]; then
  echo ">>> 检测到境外源不可达，必须先配置镜像再继续安装 <<<"
fi
```

```powershell
# Windows — 网络检测（先切 UTF-8 防乱码）
chcp 65001 >nul
Write-Host "=== 网络连通性检测 ==="
@("https://github.com", "https://raw.githubusercontent.com", "https://registry.npmjs.org", "https://pypi.org") | ForEach-Object {
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        Invoke-WebRequest -Uri $_ -TimeoutSec 3 -UseBasicParsing | Out-Null
        $sw.Stop()
        if ($sw.ElapsedMilliseconds -gt 2000) {
            "慢速 ($($sw.ElapsedMilliseconds)ms): $_ — 建议配置镜像"
        } else {
            "可达 ($($sw.ElapsedMilliseconds)ms): $_"
        }
    } catch { "不可达: $_ — 必须配置镜像" }
}
```

**判定规则**:
- 任一源**不可达** → 必须先配置镜像（见平台手册「第 0 层：网络环境配置」）
- 任一源**响应超过 2 秒** → 强烈建议配置镜像
- 全部可达且速度正常 → 可直接安装

### 步骤 4：检测前置依赖链

安装任何工具前，沿依赖链**自底向上**检测，缺失的先补上：

```
第 0 层 网络环境   镜像源 / 代理（国内用户必须优先配置）
  ↓
第 1 层 包管理器   brew(macOS) / scoop(Windows)
  ↓
第 2 层 基础运行时  node+npm / python3+pip3 / go / uv
  ↓
第 3 层 目标 CLI   gh / ffmpeg / clawhub / whisper / ...
  ↓
第 4 层 环境变量   OPENAI_API_KEY / GEMINI_API_KEY / ...
```

### 步骤 5：加载平台安装手册执行安装

根据当前平台读取对应手册：

- macOS → 阅读 `{baseDir}/references/install-macos.md`
- Windows → 阅读 `{baseDir}/references/install-windows.md`

在手册中查找目标工具的章节，按命令执行安装。

### 步骤 6：安装后验证

```bash
<工具名> --version  # 或等效验证命令
```

验证失败 → 排查错误并重试（参考手册末尾「常见问题排查」章节）。验证成功 → 告知用户安装结果。

### 需用户交互的步骤

以下操作大模型**无法完全自动化**，必须提前告知用户：

- macOS 安装 Xcode CLT: 先用 `sudo -n true` 检测 sudo 是否免密可用。**sudo 可用时**使用 `softwareupdate` 非交互安装（Agent 全自动完成）；**sudo 不可用时**输出完整操作指引让用户在自己终端执行。详见 install-macos.md 第 1 层
- macOS .pkg 降级安装: `sudo installer -pkg` 需要 sudo 免密。sudo 不可用时输出 curl + sudo installer 的分步指引让用户复制粘贴执行
- Windows 10 安装 Scoop 前可能需修改 PowerShell 执行策略
- 部分 API Key 需要用户到服务商网站注册获取

### 用户操作指引规范 [MANDATORY]

当 Agent 无法自动完成某个安装步骤时，**禁止**输出模糊的指引（如"请访问官网下载安装"）。**必须**输出小白用户可直接操作的完整指引：

1. **一句话说清原因** — 为什么需要用户操作（如"当前终端没有管理员权限"）
2. **编号步骤** — 每步只做一件事，动作明确
3. **命令用代码块包裹** — 用户可直接复制粘贴到自己的终端
4. **完整 URL / 完整命令** — 不要用"请去官网"，直接给 `curl -LO "https://..."` 等可执行命令
5. **解释密码输入行为** — 小白用户不知道 sudo 输密码时屏幕不显示字符，必须说明
6. **说明预期输出** — 让用户知道操作是否成功（如"应该输出 v22.12.0"）
7. **明确回复方式** — "完成后请回复'已安装'"

详细模板和示例见 install-macos.md 第 1 层「用户手动操作指引规范」章节。

---

## 包管理器选择决策树 [MANDATORY]

安装第 1 层包管理器时，**必须**按以下决策树选择，不可随意混用：

### macOS 决策树

```
1. command -v brew → 存在？ → 直接使用 Homebrew
2. 不存在 → 安装 Homebrew（见手册第 1 层）
3. Homebrew 安装失败（网络超时等）→ 使用降级方案：
   - 基础运行时（node/python/go）→ 从官网下载 .pkg 安装包直接安装（见手册「降级方案」章节）
   - 其他 CLI 工具 → 暂无法安装，告知用户需先解决网络问题或手动安装 Homebrew
```

### Windows 决策树

```
1. 检测已有包管理器（按优先级）：
   a. Get-Command scoop  → 存在？ → 使用 Scoop
   b. Get-Command winget → 存在？ → 使用 winget
   c. Get-Command choco  → 存在？ → 使用 Chocolatey
2. 全部不存在 → 安装 Scoop（首选，无需管理员权限）
3. Scoop 安装失败（网络超时）→ 降级方案：
   a. 尝试 Scoop 国内镜像安装（见手册第 1 层）
   b. 检测 winget 是否可用（Windows 11 预装）→ 用 winget
   c. 基础运行时（node/python/go）→ 从官网下载 .msi 安装包直接安装（见手册「降级方案」章节）
   d. 如果用户有管理员权限 → 尝试 Chocolatey
```

**原则：检测到什么就用什么，不要在已有包管理器的系统上安装新的包管理器。**

---

## 跨平台工具名称差异 [重要]

以下工具在 macOS 和 Windows 上的命令名称不同，检测时需注意：

| 工具 | macOS 命令 | Windows 命令 | 说明 |
|------|-----------|-------------|------|
| Python | `python3` | `python` | Windows 上 `python3` 通常不存在 |
| pip | `pip3` | `pip` | 与 Python 命令保持一致 |
| curl | `curl` | `curl.exe` | Windows PowerShell 中 `curl` 是 `Invoke-WebRequest` 的别名 |

---

## 无需安装的 Skill

以下 skill 不依赖外部 CLI 工具，无需执行安装流程：

| Skill | 说明 |
|-------|------|
| canvas | 内置功能，在连接的 OpenClaw 节点上显示 HTML 内容 |
| healthcheck | 内置功能，主机安全加固和风险配置 |
| qclaw-skill-creator | 内置功能，创建或更新 AgentSkill |
| weather | 仅依赖 `curl`，macOS/Windows 均预装 |
| openai-whisper-api | 仅依赖 `curl`（macOS 预装 / Windows 预装 `curl.exe`），另需 `OPENAI_API_KEY` 环境变量 |
| voice-call | 需通过 `openclaw.json` 配置 `plugins.entries.voice-call.enabled: true` 启用，无需安装外部工具 |

## 特殊依赖说明

- **coding-agent**: 支持 `anyBins` 模式，安装 claude / codex / opencode / pi **任意一个**即可，无需全部安装
- **openai-whisper**: 同时依赖 `python3+pip3` **和** `ffmpeg` 两个运行时，安装时两者都需要检测和补齐
- **session-logs**: 依赖 `jq` 和 `rg`（ripgrep），两者都需要安装

---

## 基础运行时查询表

当工具需要前置运行时时，查此表确认运行时安装方式。

| 运行时 | macOS (Homebrew) | macOS (降级: .pkg 直装) | Windows (Scoop) | Windows (winget) | Windows (降级: 官网安装包) |
|--------|-----------------|------------------------|-----------------|-----------------|-------------------------|
| node+npm | `brew install node` | 从 https://nodejs.org/ 下载 .pkg | `scoop install nodejs` | `winget install OpenJS.NodeJS.LTS` | 从 https://nodejs.org/ 下载 .msi |
| python3+pip3 | `brew install python` | 从 https://mirrors.huaweicloud.com/python/3.12.8/ 下载 .pkg | `scoop install python` | `winget install Python.Python.3.12` | 从 https://mirrors.huaweicloud.com/python/3.12.8/ 下载 .exe |
| go | `brew install go` | 从 https://go.dev/dl/ 下载 .pkg | `scoop install go` | `winget install GoLang.Go` | 从 https://go.dev/dl/ 下载 .msi |
| uv | `brew install uv` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `scoop install uv` | `winget install astral-sh.uv` | `irm https://astral.sh/uv/install.ps1 \| iex` |

## 包管理器查询表

安装运行时和 CLI 的前提——包管理器本身的安装方式。

| 包管理器 | 平台 | 检测 | 安装（国内首选） | 安装（海外/直连） |
|---------|------|------|----------------|-----------------|
| Homebrew | macOS | `command -v brew` | 先安装 Xcode CLT（见手册第 1 层决策流程），再 `/bin/bash -c "$(curl -fsSL https://mirrors.ustc.edu.cn/misc/brew-install.sh)"` | 先安装 Xcode CLT（见手册第 1 层决策流程），再 `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` |
| Scoop | Windows | `Get-Command scoop` | `irm https://gitee.com/glsnames/scoop-installer/raw/master/bin/install.ps1 \| iex` | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; irm get.scoop.sh \| iex` |
| winget | Windows 11 | `Get-Command winget` | 预装；Windows 10 从 Microsoft Store 安装 "App Installer" | 同左 |

## 注意事项

- 平台标记为 `darwin` 的 skill 仅 macOS 可用（apple-notes、apple-reminders、model-usage、peekaboo、camsnap）
- `tmux` 在 Windows 上不可用（如需终端复用，可在 WSL 内安装）
- 环境变量类依赖（API Key）无法通过命令安装，需引导用户到服务商网站注册获取
- **国内用户安装前务必先配置镜像源**，否则 Homebrew/npm/pip/Go 等工具下载极易超时失败
- 安装命令的详细参数、备选方案和常见问题排查见各平台 reference 文件
- macOS 14+ (Sonoma) 不再预装 Python 3，`python3` 可能是一个 stub，需用 `python3 -c "import sys"` 验证真实性
- Windows 上 `python` 和 `pip` 是标准命令名，不要使用 `python3`/`pip3`
