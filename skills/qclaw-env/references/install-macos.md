# macOS 环境安装手册

面向大模型的 macOS 全链路安装指引。每个条目包含：检测 → 安装 → 验证 → 安装后操作。

---

## 全量环境快照 [首先执行]

**任何安装操作前，必须先执行此快照**，了解系统已有工具，避免重复安装。

```bash
echo "=== macOS 环境快照 ==="
echo "--- 平台 ---"
echo "macOS $(sw_vers -productVersion), $(uname -m)"

echo ""
echo "--- Xcode Command Line Tools ---"
if xcode-select -p >/dev/null 2>&1; then
  echo "已安装: $(xcode-select -p)"
  # 检测 CLT 提供的工具
  for cmd in git svn make gcc clang; do
    command -v "$cmd" >/dev/null 2>&1 && echo "  CLT 提供: $cmd"
  done
else
  echo "未安装 (安装 Homebrew 前必须先安装)"
fi

echo ""
echo "--- sudo 免密可用性 ---"
if sudo -n true 2>/dev/null; then
  echo "SUDO_OK=true — 可使用 softwareupdate / sudo installer 等非交互命令"
else
  echo "SUDO_OK=false — sudo 需要密码，非交互命令不可用，需使用 GUI 方式或用户手动操作"
fi

echo ""
echo "--- 包管理器 ---"
command -v brew >/dev/null 2>&1 && echo "brew: $(brew --version 2>&1 | head -1)" || echo "brew: 未安装"

echo ""
echo "--- 基础运行时 ---"
for cmd in node npm python3 pip3 go uv; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd: $("$cmd" --version 2>&1 | head -1)"
  else
    echo "$cmd: 未安装"
  fi
done

# python3 真实性检测（macOS 14+ 可能是 stub）
echo ""
echo "--- python3 真实性 ---"
if command -v python3 >/dev/null 2>&1; then
  python3 -c "import sys; print('真实 Python:', sys.version)" 2>/dev/null || echo "python3 是 Xcode CLT stub，非真实 Python（需通过 brew 或 .pkg 安装）"
fi

echo ""
echo "--- CLI 工具 ---"
for cmd in curl git gh jq rg ffmpeg tmux whisper memo remindctl clawhub claude codex opencode pi himalaya camsnap peekaboo songsee summarize sag oracle mcporter gifgrep blogwatcher obsidian-cli codexbar nano-pdf; do
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "$cmd: 已安装"
  else
    echo "$cmd: 未安装"
  fi
done
```

---

## 第 0 层：网络环境配置

**国内用户必读**。macOS 安装工具依赖的主要境外源（GitHub、Homebrew、npm、PyPI）在国内直连速度慢或不可达，安装前**必须先配置镜像**。

### 网络连通性检测

```bash
# 依次检测主要源是否可达（超时 3 秒）
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
  echo ""
  echo ">>> 检测到境外源不可达，必须先配置镜像再继续安装 <<<"
fi
```

**判定规则**:
- 任一源不可达 → **必须**先完成下方镜像配置
- 全部可达 → 可直接跳到第 1 层

### Homebrew 镜像（中科大源）

**重要：必须在安装 Homebrew 之前先 export 环境变量（当前会话生效），安装完成后再持久化到 ~/.zshrc。**

```bash
# 第一步：检测是否已配置
echo "HOMEBREW_BREW_GIT_REMOTE=$HOMEBREW_BREW_GIT_REMOTE"
echo "HOMEBREW_API_DOMAIN=$HOMEBREW_API_DOMAIN"
echo "HOMEBREW_BOTTLE_DOMAIN=$HOMEBREW_BOTTLE_DOMAIN"
```

```bash
# 第二步：当前会话立即生效（在安装 brew 之前执行）
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
export HOMEBREW_API_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/api"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"
```

```bash
# 第三步：持久化到 shell 配置（安装 brew 成功后执行）
grep -q 'HOMEBREW_BREW_GIT_REMOTE' ~/.zshrc 2>/dev/null || cat >> ~/.zshrc << 'EOF'
# Homebrew 镜像（中科大）
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
export HOMEBREW_API_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles/api"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.ustc.edu.cn/homebrew-bottles"
EOF
source ~/.zshrc
```

备选镜像：清华源 `https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git`

### npm 镜像

```bash
# 检测当前 registry（需 npm 已安装）
npm config get registry 2>/dev/null

# 配置国内镜像（npmmirror）
npm config set registry https://registry.npmmirror.com

# 验证
npm config get registry
# 应输出 https://registry.npmmirror.com/
```

### pip 镜像（清华源）

```bash
# 配置清华 PyPI 镜像（需 pip3 已安装）
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip3 config set global.trusted-host pypi.tuna.tsinghua.edu.cn

# 验证
pip3 config get global.index-url
```

### Go 模块代理

```bash
# 配置 Go 代理（七牛云，需 go 已安装）
go env -w GOPROXY=https://goproxy.cn,direct

# 或持久化到 shell 配置
echo 'export GOPROXY=https://goproxy.cn,direct' >> ~/.zshrc
source ~/.zshrc
```

### GitHub Releases 下载加速

部分工具（sherpa-onnx-tts、gifgrep 等）需从 GitHub Releases 下载二进制文件。如直连 GitHub 下载慢：

1. **使用代理**：如果已有代理，配置 `export https_proxy=http://127.0.0.1:<端口>`
2. **手动下载**：在浏览器中使用下载工具获取文件后，手动放到目标目录
3. **使用 ghproxy 等加速服务**：将 `https://github.com/` 替换为 `https://mirror.ghproxy.com/https://github.com/`（第三方服务，可用性不保证）

---

## 第 1 层：包管理器

### sudo 可用性检测（后续多个步骤依赖）

macOS 上多个安装操作需要 `sudo` 权限（CLT 非交互安装、.pkg 安装等）。Agent 运行在非交互终端中，**无法输入密码**，因此必须先检测 `sudo` 是否免密可用。

```bash
# 检测 sudo 是否可免密执行（不会触发密码提示）
if sudo -n true 2>/dev/null; then
  echo "SUDO_OK=true  — sudo 免密可用，可使用 softwareupdate / sudo installer 等命令"
else
  echo "SUDO_OK=false — sudo 需要密码，Agent 无法使用 sudo 类命令，将使用不需要 sudo 的安装方式"
fi
```

**后续所有步骤根据 `SUDO_OK` 状态选择不同安装路径：**
- `SUDO_OK=true` → 可使用 `softwareupdate -i`、`sudo installer -pkg` 等命令
- `SUDO_OK=false` → 只能使用不需要 sudo 的方式。**当需要用户手动操作时，必须输出完整的分步指引和可复制的命令**

### 用户手动操作指引规范 [MANDATORY]

当 Agent 无法自动完成某个安装步骤（sudo 不可用、需要 GUI 操作等）时，**必须**按以下格式输出用户操作指引：

1. **说清楚为什么需要手动操作**（一句话）
2. **给出编号步骤**，每步一个动作
3. **所有终端命令必须用代码块包裹**，用户可直接复制粘贴
4. **涉及下载链接的给出完整 URL**，不要用"请访问官网"这种模糊表述
5. **说明预期结果**，让用户知道操作是否成功
6. **用户完成后告知 Agent 的方式**："完成后请回复'已安装'，我会继续后续步骤"

**示例模板**（Agent 应输出的格式）:

```
我需要你手动完成一个步骤（因为当前终端没有管理员权限）：

请打开一个新的「终端」窗口，依次复制粘贴执行以下命令：

第 1 步 — 输入密码获取管理员权限：
sudo -v

（系统会提示输入你的 Mac 登录密码，输入时屏幕不会显示任何字符，这是正常的，输入完按回车即可）

第 2 步 — 安装 Xcode 命令行工具：
sudo softwareupdate -i "Command Line Tools for Xcode-16.0" --verbose

（安装过程需要几分钟，请等待出现 "Done." 字样）

第 3 步 — 验证安装成功：
xcode-select -p

（应该输出类似 /Library/Developer/CommandLineTools 的路径）

全部完成后请回复「已安装」，我会继续后续步骤。
```

### Xcode Command Line Tools（Homebrew 前置条件）

Homebrew 依赖 Xcode CLT，**必须先安装 CLT 再安装 Homebrew**。

- 检测:
  ```bash
  xcode-select -p >/dev/null 2>&1 && echo "已安装: $(xcode-select -p)" || echo "未安装"
  ```

- **安装方式 A — 非交互式 `softwareupdate` 命令（sudo 免密可用时首选）**:

  此方式**完全不需要用户手动操作 GUI 弹窗**，全程在终端内完成。

  **前置条件**: `SUDO_OK=true`（sudo 免密可用）。如果 `SUDO_OK=false`，直接跳到方式 B。

  ```bash
  # 第 1 步: 触发 CLT 安装注册
  touch /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress

  # 第 2 步: 从 softwareupdate 列表中查找 CLT 包名
  CLT_LABEL=$(softwareupdate --list 2>&1 | grep -o "Command Line Tools for Xcode-[0-9.]*" | sort -V | tail -1)

  if [ -n "$CLT_LABEL" ]; then
    echo "找到 CLT 安装包: $CLT_LABEL"
    # 第 3 步: 执行安装（sudo 免密已确认）
    sudo softwareupdate -i "$CLT_LABEL" --verbose
    echo "softwareupdate 安装完成"
  else
    echo "softwareupdate 未找到 CLT 安装包，将回退到方式 B"
  fi

  # 第 4 步: 清理标记文件
  rm -f /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress

  # 第 5 步: 验证
  if xcode-select -p >/dev/null 2>&1; then
    echo "Xcode CLT 安装成功: $(xcode-select -p)"
  else
    echo "安装未完成，需回退到方式 B"
  fi
  ```

- **安装方式 B — 用户手动操作（sudo 不可用时使用，或方式 A 失败时回退）**:

  Agent 应向用户输出以下完整操作指引（根据实际情况二选一）：

  **B-1: 推荐 — 用户在自己的终端中用 sudo 安装（全程命令行，无 GUI）**:

  Agent 先执行以下命令获取 CLT 包名，然后将包名填入指引中：
  ```bash
  touch /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress
  CLT_LABEL=$(softwareupdate --list 2>&1 | grep -o "Command Line Tools for Xcode-[0-9.]*" | sort -V | tail -1)
  rm -f /tmp/.com.apple.dt.CommandLineTools.installondemand.in-progress
  echo "CLT_LABEL=$CLT_LABEL"
  ```

  然后输出指引（将 `<CLT_LABEL>` 替换为上面获取的实际包名）：
  ```
  我需要你手动完成一个步骤（因为当前终端没有管理员权限）：

  请打开一个新的「终端」窗口（在启动台中搜索"终端"即可），依次复制粘贴执行以下命令：

  第 1 步 — 安装 Xcode 命令行工具（需要输入你的 Mac 登录密码，输入时屏幕不显示字符，输完按回车）：

  sudo softwareupdate -i "<CLT_LABEL>" --verbose

  等待安装完成（会看到 "Done." 或 "安装完成" 字样，约需 5-15 分钟）。

  第 2 步 — 验证是否安装成功：

  xcode-select -p

  如果输出了一个路径（如 /Library/Developer/CommandLineTools），说明安装成功。

  完成后请回复「已安装」，我会继续后续步骤。
  ```

  **B-2: 备选 — GUI 弹窗方式（softwareupdate 查不到包名时）**:

  ```bash
  xcode-select --install
  ```

  然后输出指引：
  ```
  系统弹出了一个安装弹窗，请按以下步骤操作：

  第 1 步 — 在弹出的窗口中，点击「安装」按钮
  第 2 步 — 等待下载和安装完成（约 1-5GB，视网速需 5-30 分钟）
  第 3 步 — 安装完成后，在终端中输入以下命令确认：

  xcode-select -p

  如果输出了一个路径（如 /Library/Developer/CommandLineTools），说明安装成功。

  完成后请回复「已安装」，我会继续后续步骤。

  如果弹窗没有出现或安装失败，请回复「失败」，我会提供其他安装方式。
  ```

- **安装方式 C — 跳过 CLT，直接让 Homebrew 安装脚本处理（备选）**:

  Homebrew 安装脚本**内置了 CLT 检测和安装逻辑**。如果 CLT 未安装，脚本会自动触发 `xcode-select --install` 弹窗。因此也可以跳过单独安装 CLT，直接运行 Homebrew 安装脚本，由脚本统一处理。

  **适用场景**: 用户既没有 sudo 免密、又不方便先单独处理 CLT 弹窗时，可以合并为一次用户交互。

- **安装方式决策流程**:
  ```
  xcode-select -p 已安装？
    → 是 → 跳过，直接安装 Homebrew
    → 否 → 检测 sudo -n true
              → sudo 可用 → 方式 A (softwareupdate，全自动)
                              → 成功？ → 继续安装 Homebrew
                              → 失败 → 方式 B (输出用户操作指引)
              → sudo 不可用 → 先获取 CLT_LABEL
                               → 获取到 → 方式 B-1 (输出 sudo softwareupdate 指引，用户在自己终端执行)
                               → 未获取到 → 方式 B-2 (xcode-select --install GUI 弹窗指引)
                               → 用户回复失败 → 方式 C (让 Homebrew 脚本处理) 或降级方案
  ```

- 说明: Xcode CLT 还会提供 `git`、`make`、`clang` 等常用工具，安装后这些工具自动可用

### Homebrew

- 检测: `command -v brew`
- 前置: Xcode CLT 已安装（见上方）
- 安装（**国内首选 — 使用中科大镜像脚本**）:
  ```bash
  # 确保已 export Homebrew 镜像环境变量（见第 0 层第二步）
  /bin/bash -c "$(curl -fsSL https://mirrors.ustc.edu.cn/misc/brew-install.sh)"
  ```
- 安装（海外/可直连）:
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- 验证: `brew --version`
- 安装后（**Apple Silicon Mac 必须执行，否则后续所有 brew 工具都找不到**）:
  ```bash
  # 检测是否为 Apple Silicon
  if [ "$(uname -m)" = "arm64" ]; then
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo "已配置 Apple Silicon Homebrew PATH"
  fi
  ```
- 安装失败处理:
  - 如果 `curl` 下载脚本超时 → 确认已配置 Homebrew 镜像环境变量，切换到中科大安装脚本
  - 如果安装过程中断 → 运行 `/bin/bash -c "$(curl -fsSL https://mirrors.ustc.edu.cn/misc/brew-install.sh)"` 重试（安装脚本支持断点续装）
  - 如果反复失败 → 跳转到下方「降级方案」，使用 .pkg 直装基础运行时

---

## 第 2 层：基础运行时

### Node.js + npm

- 检测: `command -v node && command -v npm`
- 安装（Homebrew）: `brew install node`
- 安装（**降级方案 — Homebrew 不可用时**）:
  1. **sudo 可用时** — Agent 可自动完成:
     ```bash
     # 以 Node.js 22.x LTS 为例（替换为当前 LTS 版本号）
     curl -LO "https://nodejs.org/dist/v22.12.0/node-v22.12.0.pkg"
     sudo installer -pkg node-v22.12.0.pkg -target /
     rm node-v22.12.0.pkg
     ```
  2. **sudo 不可用时** — 输出以下指引让用户操作:
     ```
     我需要你手动安装 Node.js（因为当前终端没有管理员权限）：

     请打开一个新的「终端」窗口，依次复制粘贴执行以下命令：

     第 1 步 — 下载安装包：
     curl -LO "https://nodejs.org/dist/v22.12.0/node-v22.12.0.pkg"

     第 2 步 — 安装（需要输入 Mac 登录密码，输入时不显示字符，输完按回车）：
     sudo installer -pkg node-v22.12.0.pkg -target /

     第 3 步 — 清理安装包：
     rm node-v22.12.0.pkg

     第 4 步 — 验证安装成功：
     node --version && npm --version

     如果输出了版本号（如 v22.12.0 和 10.x.x），说明安装成功。
     完成后请回复「已安装」，我会继续后续步骤。
     ```
- 验证: `node --version && npm --version`
- 安装后（**国内网络必须立即执行，不要等到后续步骤**）:
  ```bash
  npm config set registry https://registry.npmmirror.com
  npm config get registry  # 验证: 应输出 https://registry.npmmirror.com/
  ```
  海外/可直连用户可跳过此步。详见第 0 层 npm 镜像章节。

### Python3 + pip3

- 检测:
  ```bash
  # 不仅检测命令是否存在，还要验证是否为真实 Python（非 Xcode CLT stub）
  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import sys; print(sys.version)" 2>/dev/null && echo "python3 可用" || echo "python3 为 stub，需安装"
  else
    echo "python3 未安装"
  fi
  ```
- 安装（Homebrew）: `brew install python`
- 安装（**降级方案 — Homebrew 不可用时**）:
  1. **sudo 可用时** — Agent 可自动完成:
     ```bash
     # 以 Python 3.12.x 为例（华为云镜像，国内高速）
     curl -LO "https://mirrors.huaweicloud.com/python/3.12.8/python-3.12.8-macos11.pkg"
     sudo installer -pkg python-3.12.8-macos11.pkg -target /
     rm python-3.12.8-macos11.pkg
     ```
  2. **sudo 不可用时** — 输出以下指引让用户操作:
     ```
     我需要你手动安装 Python（因为当前终端没有管理员权限）：

     请打开一个新的「终端」窗口，依次复制粘贴执行以下命令：

     第 1 步 — 下载安装包（华为云镜像，国内高速）：
     curl -LO "https://mirrors.huaweicloud.com/python/3.12.8/python-3.12.8-macos11.pkg"

     第 2 步 — 安装（需要输入 Mac 登录密码，输入时不显示字符，输完按回车）：
     sudo installer -pkg python-3.12.8-macos11.pkg -target /

     第 3 步 — 清理安装包：
     rm python-3.12.8-macos11.pkg

     第 4 步 — 验证安装成功：
     python3 --version && pip3 --version

     如果输出了版本号（如 Python 3.12.8 和 pip 24.x），说明安装成功。
     完成后请回复「已安装」，我会继续后续步骤。
     ```
- 验证: `python3 --version && pip3 --version`
- 安装后（**国内网络必须立即执行，不要等到后续步骤**）:
  ```bash
  pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
  pip3 config set global.trusted-host pypi.tuna.tsinghua.edu.cn
  pip3 config get global.index-url  # 验证
  ```
  海外/可直连用户可跳过此步。详见第 0 层 pip 镜像章节。
- 注意: macOS 14 (Sonoma) 及更高版本不再预装 Python 3。`python3` 命令可能是一个 stub，执行后会提示安装 Xcode CLT 但不提供真实 Python。必须用 `python3 -c "import sys"` 验证真实性。

### Go

- 检测: `command -v go`
- 安装（Homebrew）: `brew install go`
- 安装（**降级方案 — Homebrew 不可用时**）:
  1. **sudo 可用时** — Agent 可自动完成:
     ```bash
     # 以 Go 1.23.x 为例（根据 ARCH 选择）
     ARCH="$(uname -m)"
     if [ "$ARCH" = "arm64" ]; then
       curl -LO "https://go.dev/dl/go1.23.4.darwin-arm64.pkg"
       sudo installer -pkg go1.23.4.darwin-arm64.pkg -target /
       rm go1.23.4.darwin-arm64.pkg
     else
       curl -LO "https://go.dev/dl/go1.23.4.darwin-amd64.pkg"
       sudo installer -pkg go1.23.4.darwin-amd64.pkg -target /
       rm go1.23.4.darwin-amd64.pkg
     fi
     ```
  2. **sudo 不可用时** — 输出以下指引让用户操作（根据 `uname -m` 结果选择对应架构版本）:

     Apple Silicon (arm64) 版本：
     ```
     我需要你手动安装 Go（因为当前终端没有管理员权限）：

     请打开一个新的「终端」窗口，依次复制粘贴执行以下命令：

     第 1 步 — 下载安装包：
     curl -LO "https://go.dev/dl/go1.23.4.darwin-arm64.pkg"

     第 2 步 — 安装（需要输入 Mac 登录密码，输入时不显示字符，输完按回车）：
     sudo installer -pkg go1.23.4.darwin-arm64.pkg -target /

     第 3 步 — 清理安装包：
     rm go1.23.4.darwin-arm64.pkg

     第 4 步 — 验证安装成功：
     go version

     如果输出了版本号（如 go version go1.23.4 darwin/arm64），说明安装成功。
     完成后请回复「已安装」，我会继续后续步骤。
     ```

     Intel (x86_64) 版本：
     ```
     （同上，将 arm64 替换为 amd64）

     curl -LO "https://go.dev/dl/go1.23.4.darwin-amd64.pkg"
     sudo installer -pkg go1.23.4.darwin-amd64.pkg -target /
     rm go1.23.4.darwin-amd64.pkg
     go version
     ```
- 验证: `go version`
- 安装后: 配置 Go 代理（见第 0 层），确保 `~/go/bin` 在 PATH 中:
  ```bash
  grep -q 'go/bin' ~/.zshrc || echo 'export PATH="$HOME/go/bin:$PATH"' >> ~/.zshrc
  source ~/.zshrc
  ```

### uv (Python 包管理器)

- 检测: `command -v uv`
- 安装（Homebrew）: `brew install uv`
- 安装（**降级方案 — Homebrew 不可用时**）:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- 验证: `uv --version`

---

## 降级方案汇总

当 Homebrew 安装失败或不可用时，基础运行时可通过官方 .pkg 安装包直接安装。**此方案不依赖任何包管理器，成功率最高。**

| 运行时 | sudo 可用时（Agent 自动） | sudo 不可用时（输出指引让用户在自己终端执行） |
|--------|------------------------|------------------------------------------|
| Node.js | `curl -LO <url> && sudo installer -pkg <file> -target /` | 输出含 curl + sudo installer 命令的分步指引 |
| Python3 | `curl -LO <url> && sudo installer -pkg <file> -target /` | 输出含 curl + sudo installer 命令的分步指引 |
| Go | `curl -LO <url> && sudo installer -pkg <file> -target /` | 输出含 curl + sudo installer 命令的分步指引 |
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | 同左（不需要 sudo） |

**注意**:
- `sudo installer` 方式需要 `SUDO_OK=true`（sudo 免密可用）。`SUDO_OK=false` 时，Agent 必须输出完整的分步操作指引，让用户在自己的终端窗口中执行（用户终端可以输入 sudo 密码）
- 用户操作指引必须遵循上方「用户手动操作指引规范」：编号步骤 + 可复制命令 + 预期结果 + 回复方式
- .pkg 安装的工具通常安装到 `/usr/local/bin`，无需额外配置 PATH
- Go 的 .pkg 安装后需手动将 `~/go/bin` 加入 PATH

---

## 第 3 层：Skill CLI 依赖

### 无需安装的 Skill

以下 skill 不需要额外安装外部工具：

- **canvas** — 内置功能
- **healthcheck** — 内置功能
- **qclaw-skill-creator** — 内置功能
- **weather** — 仅依赖 `curl`（macOS 预装）
- **openai-whisper-api** — 仅依赖 `curl`（macOS 预装），另需 `OPENAI_API_KEY` 环境变量
- **voice-call** — 需在 `openclaw.json` 中配置 `plugins.entries.voice-call.enabled: true`

### steipete/tap 批量准备

以下 skill 的 CLI 工具来自 `steipete/tap`，先添加一次 tap：

```bash
brew tap steipete/tap
```

涉及的工具：remindctl、camsnap、gifgrep、mcporter、oracle、peekaboo、sag、songsee、summarize（共 9 个）。

### apple-notes — `memo`

- 检测: `command -v memo`
- 安装: `brew install antoniorodr/memo/memo`
- 验证: `memo --version`
- 备选: 从 https://github.com/antoniorodr/memo/releases 下载二进制文件

### apple-reminders — `remindctl`

- 检测: `command -v remindctl`
- 安装: `brew install steipete/tap/remindctl`
- 验证: `remindctl --version`

### blogwatcher — `blogwatcher`

- 前置运行时: go（安装后需先配置 Go 代理，见第 0 层）
- 检测: `command -v blogwatcher`
- 安装: `go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest`
- 验证: `blogwatcher --version`

### camsnap — `camsnap`

- 检测: `command -v camsnap`
- 安装: `brew install steipete/tap/camsnap`
- 验证: `camsnap --version`
- 注意: 依赖 macOS AVFoundation 框架，仅 macOS 可用

### clawhub — `clawhub`

- 前置运行时: node+npm（安装后需先配置 npm 镜像，见第 0 层）
- 检测: `command -v clawhub`
- 安装: `npm install -g clawhub`
- 验证: `clawhub --version`

### coding-agent — `claude` / `codex` / `opencode` / `pi`（任一）

- 前置运行时: node+npm
- 检测: `command -v claude || command -v codex || command -v opencode || command -v pi`
- 安装（**任选一个**即可，无需全部安装）:
  - Claude Code: `npm install -g @anthropic-ai/claude-code`
  - Codex: `npm install -g @openai/codex`
  - Pi: `npm install -g @mariozechner/pi-coding-agent`
  - OpenCode: 参见 https://github.com/opencode-ai/opencode
- 验证: `claude --version` / `codex --version` / `pi --version`

### gh-issues — `curl` + `git` + `gh`

- 检测: `command -v curl && command -v git && command -v gh`
- curl: macOS 预装
- git: `brew install git`（或 xcode-select 已提供）
- gh: 同下方 github skill
- 环境变量: `GH_TOKEN`（通过 `gh auth login` 自动配置）

### gifgrep — `gifgrep`

- 检测: `command -v gifgrep`
- 安装: `brew install steipete/tap/gifgrep`
- 备选: `go install github.com/steipete/gifgrep/cmd/gifgrep@latest`
- 验证: `gifgrep --version`

### github — `gh`

- 检测: `command -v gh`
- 安装: `brew install gh`
- 验证: `gh --version`
- 安装后: `gh auth login`

### himalaya — `himalaya`

- 检测: `command -v himalaya`
- 安装: `brew install himalaya`
- 验证: `himalaya --version`

### mcporter — `mcporter`

- 前置运行时: node+npm
- 检测: `command -v mcporter`
- 安装: `npm install -g mcporter`
- 备选: `brew install steipete/tap/mcporter`
- 验证: `mcporter --version`

### model-usage — `codexbar`

- 检测: `command -v codexbar`
- 安装: `brew install --cask steipete/tap/codexbar`
- 验证: `codexbar --version`

### nano-banana-pro — `uv`

- 前置运行时: uv
- 检测: `command -v uv`
- 安装: 见上方 uv 安装
- 环境变量: `GEMINI_API_KEY`（从 https://ai.google.dev/ 获取）

### nano-pdf — `nano-pdf`

- 前置运行时: uv（三层依赖链：brew → uv → nano-pdf）
- 检测: `command -v nano-pdf`
- 安装: `uv tool install nano-pdf`
- 验证: `nano-pdf --version`

### obsidian — `obsidian-cli`

- 检测: `command -v obsidian-cli`
- 安装: `brew install yakitrak/yakitrak/obsidian-cli`
- 验证: `obsidian-cli --version`
- 备选: 从 https://github.com/yakitrak/obsidian-cli/releases 下载

### openai-image-gen — `python3`

- 前置运行时: python3
- 检测: `command -v python3 && python3 -c "import sys" 2>/dev/null`
- 安装: 见上方 Python3 安装
- 环境变量: `OPENAI_API_KEY`（从 https://platform.openai.com/ 获取）

### openai-whisper — `whisper`

- 前置运行时: python3+pip3 **和** ffmpeg（两者都需要）
- 检测: `command -v whisper && command -v ffmpeg`
- 安装:
  1. 先安装 ffmpeg: `brew install ffmpeg`
  2. 再安装 whisper: `brew install openai-whisper`
- 备选: `pip3 install openai-whisper`（仍需先安装 ffmpeg）
- 验证: `whisper --help && ffmpeg -version`

### oracle — `oracle`

- 前置运行时: node+npm
- 检测: `command -v oracle`
- 安装: `npm install -g @steipete/oracle`
- 备选: `brew install steipete/tap/oracle`
- 验证: `oracle --version`

### peekaboo — `peekaboo`

- 检测: `command -v peekaboo`
- 安装: `brew install steipete/tap/peekaboo`
- 验证: `peekaboo --version`

### sag — `sag`

- 检测: `command -v sag`
- 安装: `brew install steipete/tap/sag`
- 验证: `sag --version`
- 环境变量: `ELEVENLABS_API_KEY`（从 https://elevenlabs.io 获取）

### session-logs — `jq` + `rg`

- 检测: `command -v jq && command -v rg`
- 安装: `brew install jq ripgrep`
- 验证: `jq --version && rg --version`

### sherpa-onnx-tts — 运行时 + 模型下载

- 检测: `test -d "$SHERPA_ONNX_RUNTIME_DIR" && test -d "$SHERPA_ONNX_MODEL_DIR"`
- 安装（分步执行，每步验证）:

  **步骤 1: 创建目录**
  ```bash
  mkdir -p ~/.openclaw/tools/sherpa-onnx-tts/{runtime,models}
  ls -la ~/.openclaw/tools/sherpa-onnx-tts/
  # 验证: 应看到 runtime 和 models 两个目录
  ```

  **步骤 2: 获取版本号**
  ```bash
  SHERPA_VERSION=$(curl -s https://api.github.com/repos/k2-fsa/sherpa-onnx/releases/latest | grep '"tag_name"' | head -1 | cut -d'"' -f4)
  SHERPA_VERSION=${SHERPA_VERSION:-v1.12.23}
  echo "使用版本: $SHERPA_VERSION"
  # 验证: 应输出 v1.xx.xx 格式的版本号
  ```

  **步骤 3: 下载并解压运行时**
  ```bash
  curl -L "https://github.com/k2-fsa/sherpa-onnx/releases/download/${SHERPA_VERSION}/sherpa-onnx-${SHERPA_VERSION}-osx-universal2-shared.tar.bz2" -o /tmp/sherpa-runtime.tar.bz2
  # 验证下载: 文件大小应 > 10MB
  ls -lh /tmp/sherpa-runtime.tar.bz2
  tar xjf /tmp/sherpa-runtime.tar.bz2 --strip-components=1 -C ~/.openclaw/tools/sherpa-onnx-tts/runtime
  rm /tmp/sherpa-runtime.tar.bz2
  # 验证解压: 应看到 lib/ 目录和 .dylib 文件
  ls ~/.openclaw/tools/sherpa-onnx-tts/runtime/lib/
  ```

  **步骤 4: 下载并解压模型**
  ```bash
  curl -L "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-lessac-high.tar.bz2" -o /tmp/sherpa-model.tar.bz2
  ls -lh /tmp/sherpa-model.tar.bz2
  tar xjf /tmp/sherpa-model.tar.bz2 -C ~/.openclaw/tools/sherpa-onnx-tts/models
  rm /tmp/sherpa-model.tar.bz2
  # 验证解压: 应看到模型文件
  ls ~/.openclaw/tools/sherpa-onnx-tts/models/vits-piper-en_US-lessac-high/
  ```

- 安装后: 在 `~/.openclaw/openclaw.json` 中配置:
  ```json5
  { skills: { entries: { "sherpa-onnx-tts": { env: {
    SHERPA_ONNX_RUNTIME_DIR: "~/.openclaw/tools/sherpa-onnx-tts/runtime",
    SHERPA_ONNX_MODEL_DIR: "~/.openclaw/tools/sherpa-onnx-tts/models/vits-piper-en_US-lessac-high"
  }}}}}
  ```
- 注意: 如果 GitHub 下载慢，参考第 0 层「GitHub Releases 下载加速」

### songsee — `songsee`

- 检测: `command -v songsee`
- 安装: `brew install steipete/tap/songsee`
- 验证: `songsee --version`

### summarize — `summarize`

- 检测: `command -v summarize`
- 安装: `brew install steipete/tap/summarize`
- 验证: `summarize --version`

### tmux — `tmux`

- 检测: `command -v tmux`
- 安装: `brew install tmux`
- 验证: `tmux -V`

### video-frames — `ffmpeg`

- 检测: `command -v ffmpeg`
- 安装: `brew install ffmpeg`
- 验证: `ffmpeg -version`

---

## 第 4 层：环境变量配置

API Key 无法通过命令安装，需引导用户到服务商注册获取。

| 环境变量 | 获取地址 | 相关 skill |
|---------|---------|-----------|
| OPENAI_API_KEY | https://platform.openai.com/ | openai-image-gen, openai-whisper-api |
| GEMINI_API_KEY | https://ai.google.dev/ | nano-banana-pro |
| ELEVENLABS_API_KEY | https://elevenlabs.io | sag |
| GH_TOKEN | 通过 `gh auth login` 自动配置 | gh-issues |

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

### 设置方法（备选：shell 环境变量）

临时（当前会话）:

```bash
export OPENAI_API_KEY="sk-..."
```

持久化（写入 shell 配置）:

```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
source ~/.zshrc
```

---

## 常见问题排查

### 网络超时 / 下载失败

**现象**: `brew install` 卡住、`npm install -g` 超时、`pip3 install` 报连接错误

**排查**:
1. 确认是否已配置镜像源（第 0 层）
2. 检查当前镜像配置:
   ```bash
   echo $HOMEBREW_BOTTLE_DOMAIN    # Homebrew
   npm config get registry          # npm
   pip3 config get global.index-url # pip
   go env GOPROXY                   # Go
   ```
3. 如果已配置镜像仍然失败，检查是否有代理冲突: `echo $https_proxy $http_proxy`

### `command not found`（安装后找不到命令）

**排查**:
1. 重新打开终端（新 shell 会话才能加载新的 PATH）
2. 检查工具是否确实安装成功:
   ```bash
   # Homebrew 安装的工具
   brew list | grep <工具名>
   # npm 全局安装的工具
   npm list -g | grep <工具名>
   # Go 安装的工具
   ls ~/go/bin/
   # uv 安装的工具
   uv tool list
   ```
3. 手动检查 PATH:
   ```bash
   echo $PATH | tr ':' '\n' | grep -E '(brew|npm|go|uv)'
   ```
4. Apple Silicon Mac 常见问题：Homebrew 安装在 `/opt/homebrew/bin`，确认已执行:
   ```bash
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```

### 权限拒绝

**现象**: `Permission denied`、`EACCES`

**排查**:
1. Homebrew 权限修复: `sudo chown -R $(whoami) $(brew --prefix)/*`
2. npm 全局安装权限问题: `sudo chown -R $(whoami) $(npm config get prefix)/{lib/node_modules,bin,share}`
3. 避免使用 `sudo npm install -g`，改用 npm 配置 prefix 或使用 nvm

### Homebrew 安装异常

**排查**:
1. 运行诊断: `brew doctor`
2. 更新 Homebrew: `brew update`
3. 清理缓存: `brew cleanup`
4. 重置 Homebrew: `brew update-reset`

### 安装失败后的清理

如果安装过程中断导致残留文件，按以下方式清理后重试:

```bash
# Homebrew 安装残留清理
rm -rf /opt/homebrew  # Apple Silicon
rm -rf /usr/local/Homebrew  # Intel Mac
rm -rf ~/.cache/Homebrew

# npm 全局包残留清理
npm cache clean --force

# pip 缓存清理
pip3 cache purge

# Go 模块缓存清理
go clean -modcache
```
