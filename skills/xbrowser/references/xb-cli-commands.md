# xb 管理命令参考

所有 xb 命令返回 JSON：`{ ok, command, data?, error?, hint?, warnings? }`。

- `ok: true` — 成功，`data` 含返回数据
- `ok: false` — 失败，`error` 描述错误，`hint` 提供建议操作

浏览器操作命令（`xb run ...`）请参见 [xb-browser-commands.md](./xb-browser-commands.md)。

---

## 1. init — 环境初始化

```bash
xb init
```

初始化 xbrowser 运行环境。执行流程：

1. 检查/创建工作目录
2. 检查版本文件，处理版本不一致（升级迁移或重建）
3. 写入/更新版本文件
4. 检查底层引擎（agent-browser CLI）是否安装
5. 检查可用浏览器
6. 检查配置是否存在且完整

**返回格式：**

成功（环境就绪）：
```json
{
  "ok": true,
  "command": "init",
  "data": {
    "status": "ready",
    "env": {
      "browser": "cft",
      "headed": false,
      "cli_version": "agent-browser 0.25.3"
    }
  }
}
```

失败 — 底层引擎未安装：
```json
{
  "ok": false,
  "command": "init",
  "error": "agent-browser CLI 未安装",
  "hint": "xb setup"
}
```

失败 — 未检测到浏览器：
```json
{
  "ok": false,
  "command": "init",
  "error": "未检测到可用浏览器",
  "hint": "xb setup"
}
```

失败 — 首次使用，需要配置：
```json
{
  "ok": false,
  "command": "init",
  "error": "首次使用，需要配置",
  "hint": "xb guide config",
  "data": { "status": "needs_config" }
}
```

失败 — 配置未完成：
```json
{
  "ok": false,
  "command": "init",
  "error": "配置未完成",
  "hint": "xb guide incomplete-config",
  "data": { "status": "config_incomplete" }
}
```

失败 — 工作目录无法删除（版本不一致时重建失败）：
```json
{
  "ok": false,
  "command": "init",
  "error": "无法删除工作目录: ...",
  "hint": "请手动关闭所有浏览器后重试"
}
```

> **注意：** `init` 可能在 `warnings` 中返回清理过程的信息，如 `"已关闭 xb 启动的 chrome 进程"` 或 `"检测到版本不一致 (...), 正在重建工作目录"`。

---

## 2. config — 配置管理

```bash
xb config <show|set|reset>
```

### 2.1 config show — 查看配置

```bash
xb config show
```

成功：
```json
{
  "ok": true,
  "command": "config",
  "data": {
    "action": "show",
    "config": { "browser": "cft", "headed": false },
    "config_path": "/path/to/.xbrowser/config.json"
  }
}
```

失败 — 配置文件不存在：
```json
{
  "ok": false,
  "command": "config",
  "error": "配置文件不存在",
  "hint": "xb init"
}
```

### 2.2 config set — 修改配置

```bash
xb config set <key>=<value> [<key>=<value> ...]
```

支持的配置项：

| 配置项 | 可选值 | 默认值 |
|--------|--------|--------|
| `browser` | `cft`、`chrome`、`edge`、`qqbrowser` | `cft` |
| `headed` | `true`、`false` | `true` |

```bash
xb config set browser=chrome
xb config set headed=true
xb config set browser=edge headed=true    # 同时修改多个
```

成功：
```json
{
  "ok": true,
  "command": "config",
  "data": {
    "action": "set",
    "updated": { "browser": "chrome" },
    "config": { "browser": "chrome", "headed": false }
  }
}
```

失败 — 未知配置项：
```json
{
  "ok": false,
  "command": "config",
  "error": "未知的配置项 \"foo\"",
  "hint": "xb help config",
  "data": { "valid_keys": ["browser", "headed"] }
}
```

失败 — 缺少配置值：
```json
{
  "ok": false,
  "command": "config",
  "error": "缺少配置值",
  "hint": "xb config set browser=cft"
}
```

### 2.3 config reset — 重置配置

```bash
xb config reset
```

重置为默认配置（`browser=cft`, `headed=true`）。

成功：
```json
{
  "ok": true,
  "command": "config",
  "data": {
    "action": "reset",
    "config": { "browser": "cft", "headed": true }
  }
}
```

### 缺少子命令

```json
{
  "ok": false,
  "command": "config",
  "error": "缺少子命令",
  "hint": "xb help config",
  "data": { "subcommands": ["show", "set", "reset"] }
}
```

---

## 3. guide — 用户引导

```bash
xb guide <config|close-browser|incomplete-config>
```

用于引导用户完成配置或确认操作，返回面向用户的提示文案。

### 3.1 guide config — 配置引导

```bash
xb guide config [--step <0|1|2>]
```

分步引导用户完成首次配置。

| 步骤 | 说明 |
|------|------|
| `--step 0` | 欢迎介绍（默认） |
| `--step 1` | 浏览器选择（自动检测已安装的本地浏览器） |
| `--step 2` | 显示模式选择 |

所有决策点都返回 `awaits_user_input: true`，agent **必须**按 SKILL.md"处理决策点返回"章节处理：展示 `options` 给用户、等用户选择、再按 `user_choice_mapping` 执行对应命令。

**step 0（欢迎）**：
```json
{
  "ok": true,
  "command": "guide",
  "data": {
    "action": "config",
    "step": 0,
    "awaits_user_input": true,
    "message": "欢迎使用 xbrowser 浏览器自动化工具！首次使用需要简单配置。",
    "options": [
      { "value": "quick",  "label": "快速开始（推荐）", "description": "使用内置浏览器，干净环境，立即可用" },
      { "value": "custom", "label": "自定义设置",       "description": "选择默认浏览器和显示模式" }
    ],
    "recommended": "quick",
    "user_choice_mapping": {
      "quick":  "xb config reset",
      "custom": "xb guide config --step 1"
    }
  }
}
```

**step 1（浏览器选择，检测到本地浏览器时）**：
```json
{
  "ok": true,
  "command": "guide",
  "data": {
    "action": "config",
    "step": 1,
    "awaits_user_input": true,
    "message": "请选择默认使用的浏览器：",
    "options": [
      { "value": "cft",    "label": "内置浏览器 Chrome for Testing（推荐）", "description": "干净环境，无登录态" },
      { "value": "chrome", "label": "谷歌浏览器 Google Chrome",              "description": "使用本地 Chrome，可复用登录态" }
    ],
    "recommended": "cft",
    "user_choice_mapping": {
      "cft":    "xb config set browser=cft",
      "chrome": "xb config set browser=chrome"
    },
    "next_step_hint": "用户选择对应命令执行成功后，继续执行 xb guide config --step 2"
  }
}
```

**step 1（边界：未检测到本地浏览器，不构成决策点）**：
```json
{
  "ok": true,
  "command": "guide",
  "data": {
    "action": "config",
    "step": 1,
    "awaits_user_input": false,
    "auto_set": true,
    "message": "未检测到本地浏览器，将使用内置浏览器。",
    "options": [
      { "value": "cft", "label": "内置浏览器 Chrome for Testing（推荐）", "description": "干净环境，无登录态" }
    ],
    "recommended": "cft",
    "user_choice_mapping": { "cft": "xb config set browser=cft" },
    "next_step_hint": "执行完成后继续执行 xb guide config --step 2"
  }
}
```

`awaits_user_input: false` 表示无需用户决策（只有一个选项），agent 可直接按 `user_choice_mapping` 执行。

**step 2（显示模式）**：
```json
{
  "ok": true,
  "command": "guide",
  "data": {
    "action": "config",
    "step": 2,
    "awaits_user_input": true,
    "message": "请选择浏览器的默认显示模式：",
    "options": [
      { "value": "true",  "label": "有头模式：显示浏览器窗口（推荐）", "description": "可以看到自动化操作过程，方便观察和人工干预" },
      { "value": "false", "label": "无头模式：后台静默运行",          "description": "不显示窗口，速度更快，适合纯脚本场景" }
    ],
    "recommended": "true",
    "user_choice_mapping": {
      "true":  "xb config set headed=true",
      "false": "xb config set headed=false"
    },
    "note": "可随时通过 xb run --headed 覆盖默认值"
  }
}
```

失败 — 无效步骤：
```json
{
  "ok": false,
  "command": "guide",
  "error": "无效的步骤 \"5\"",
  "hint": "xb guide config --step <0|1|2>"
}
```

### 3.2 guide close-browser — 关闭浏览器引导

```bash
xb guide close-browser --browser <chrome|edge|qqbrowser>
```

引导用户确认关闭指定浏览器，用于安全地关闭用户可能有未保存数据的浏览器。返回决策点，agent **必须**按 SKILL.md"处理决策点返回"章节处理。

成功：
```json
{
  "ok": true,
  "command": "guide",
  "data": {
    "action": "close-browser",
    "step": "close-browser",
    "awaits_user_input": true,
    "message": "检测到 谷歌浏览器 Google Chrome 正在运行。迁移浏览器数据前需要关闭浏览器，请确认：",
    "options": [
      { "value": "confirmed", "label": "我已确认手动关闭（推荐）", "description": "请先保存数据后手动关闭浏览器" },
      { "value": "force",     "label": "帮我强制关闭",             "description": "可能丢失未保存的数据" },
      { "value": "skip",      "label": "暂不关闭",                 "description": "暂停操作，稍后再试" }
    ],
    "recommended": "confirmed",
    "user_choice_mapping": {
      "confirmed": "xb stop chrome --force",
      "force":     "xb stop chrome --force",
      "skip":      null
    },
    "skip_hint": "不执行任何命令。告知用户：好的，我会等待你确认数据保存并关闭对应浏览器后再尝试自动化操作；或者你如果需要临时自动化操作，可以通过内置浏览器进行。"
  }
}
```

> `user_choice_mapping.skip` 为 `null` 表示用户选"暂不关闭"时 agent 不执行任何命令，而是按 `skip_hint` 字段告知用户即可。

失败 — 缺少参数：
```json
{
  "ok": false,
  "command": "guide",
  "error": "缺少 --browser 参数",
  "hint": "xb guide close-browser --browser <chrome|edge|qqbrowser>"
}
```

失败 — 不支持的浏览器：
```json
{
  "ok": false,
  "command": "guide",
  "error": "不支持的浏览器 \"safari\"",
  "hint": "可选值: chrome, edge, qqbrowser"
}
```

### 3.3 guide incomplete-config — 配置不完整引导

```bash
xb guide incomplete-config
```

当 `xb init` 返回 `config_incomplete` 时使用，引导用户补全缺失的配置项。返回决策点，agent **必须**按 SKILL.md"处理决策点返回"章节处理。

成功：
```json
{
  "ok": true,
  "command": "guide",
  "data": {
    "action": "incomplete-config",
    "step": "incomplete-config",
    "awaits_user_input": true,
    "message": "配置未完成，以下选项需要设置：browser（浏览器）",
    "options": [
      { "value": "reset", "label": "重置为默认设置（推荐）", "description": "使用内置浏览器 + 显示浏览器窗口" },
      { "value": "guide", "label": "重新引导设置",           "description": "重新选择浏览器和显示模式" }
    ],
    "recommended": "reset",
    "user_choice_mapping": {
      "reset": "xb config reset",
      "guide": "xb guide config --step 1"
    }
  }
}
```

### 缺少子命令

```json
{
  "ok": false,
  "command": "guide",
  "error": "缺少子命令",
  "hint": "xb help guide",
  "data": { "subcommands": ["config", "close-browser", "incomplete-config"] }
}
```

---

## 4. setup — 安装底层引擎

```bash
xb setup
```

安装/更新 agent-browser CLI 引擎和 Chrome for Testing 浏览器。幂等操作，已安装则跳过。

执行流程：

1. 确保工作目录存在
2. 检测 CLI 是否已安装及版本
3. 如需安装/更新：检测 npm 源 → 获取包信息 → 下载 → 解压 → 验证
4. 检查 Chrome for Testing，未安装则自动安装
5. 创建浏览器 profile 目录

成功：
```json
{
  "ok": true,
  "command": "setup",
  "data": {
    "cli_version": "agent-browser 0.25.3",
    "browser_installed": true,
    "install_path": "/path/to/.xbrowser"
  }
}
```

失败 — 网络问题：
```json
{
  "ok": false,
  "command": "setup",
  "error": "检测 npm 源失败: ...",
  "hint": "请检查网络连接或配置代理"
}
```

失败 — 下载失败：
```json
{
  "ok": false,
  "command": "setup",
  "error": "下载失败: ...",
  "hint": "请检查网络连接或配置代理"
}
```

失败 — 浏览器安装失败：
```json
{
  "ok": false,
  "command": "setup",
  "error": "浏览器安装失败: ...",
  "hint": "可能原因：网络无法访问 Google CDN，请检查代理设置",
  "data": {
    "cli_version": "agent-browser 0.25.3",
    "browser_installed": false,
    "install_path": "/path/to/.xbrowser"
  }
}
```

---

## 5. stop — 关闭浏览器进程

```bash
xb stop <chrome|edge|qqbrowser|all> [--force]
```

关闭 xb 启动的本地浏览器进程。CfT（Chrome for Testing）由 agent-browser 管理，不支持通过 `stop` 关闭（请用 `xb cleanup`）。

### 不使用 --force（安全模式）

未运行时直接成功：
```json
{
  "ok": true,
  "command": "stop",
  "data": { "browser": "chrome", "running": false, "message": "Chrome 未在运行" }
}
```

运行中时返回失败，提示用引导方式关闭：
```json
{
  "ok": false,
  "command": "stop",
  "error": "Chrome 正在运行，请通过引导用户确认数据保存的方式进行关闭",
  "hint": "xb guide close-browser --browser chrome",
  "data": { "browser": "chrome", "running": true }
}
```

### 使用 --force（强制关闭）

```bash
xb stop chrome --force
```

成功：
```json
{
  "ok": true,
  "command": "stop",
  "data": {
    "browser": "chrome",
    "success": true,
    "next": "Chrome 已关闭，可以重新执行 xb run --browser chrome 继续自动化操作"
  }
}
```

失败：
```json
{
  "ok": false,
  "command": "stop",
  "error": "关闭 Chrome 失败: ...",
  "hint": "请手动关闭浏览器后重试"
}
```

### stop all — 关闭所有本地浏览器

不使用 `--force` 时，如有运行中的浏览器：
```json
{
  "ok": false,
  "command": "stop",
  "error": "以下浏览器正在运行：Chrome、Edge",
  "hint": "运行 xb stop all --force 强制关闭所有浏览器，或通过 xb guide close-browser 引导逐个关闭",
  "data": { "target": "all", "running_browsers": ["chrome", "edge"] }
}
```

使用 `--force`：
```json
{
  "ok": true,
  "command": "stop",
  "data": {
    "target": "all",
    "results": [
      { "browser": "chrome", "success": true, "error": null },
      { "browser": "edge", "success": true, "error": null },
      { "browser": "qqbrowser", "success": false, "error": "进程不存在" }
    ],
    "browsers_closed": 2
  }
}
```

没有运行中的浏览器：
```json
{
  "ok": true,
  "command": "stop",
  "data": { "target": "all", "running_browsers": [], "message": "没有正在运行的本地浏览器" }
}
```

### 错误情况

尝试关闭 CfT：
```json
{
  "ok": false,
  "command": "stop",
  "error": "CfT 由 agent-browser 管理，不需要手动关闭",
  "hint": "运行 xb cleanup 关闭 CfT 会话"
}
```

未知浏览器：
```json
{
  "ok": false,
  "command": "stop",
  "error": "未知的浏览器 \"safari\"",
  "hint": "可选值: chrome, edge, qqbrowser, all"
}
```

缺少参数：
```json
{
  "ok": false,
  "command": "stop",
  "error": "请指定要关闭的浏览器",
  "hint": "用法: xb stop <chrome|edge|qqbrowser|all> [--force]"
}
```

---

## 6. cleanup — 清理会话

```bash
xb cleanup
```

关闭所有 agent-browser 管理的会话（包括 CfT 浏览器实例）。

成功：
```json
{
  "ok": true,
  "command": "cleanup",
  "data": { "sessions_closed": 2 }
}
```

成功但有警告（部分会话关闭失败）：
```json
{
  "ok": true,
  "command": "cleanup",
  "data": { "sessions_closed": 1 },
  "warnings": ["Session cft: 进程不存在"]
}
```

> **注意：** `--force` 标志已废弃，使用时会收到警告 `"--force 已废弃，请使用 xb stop <browser> 关闭浏览器"`。要关闭本地浏览器请用 `xb stop`。

---

## 7. status — 环境状态

```bash
xb status
```

检查完整的环境状态，包括 CLI 引擎、浏览器、配置和 profile。

成功：
```json
{
  "ok": true,
  "command": "status",
  "data": {
    "cli": {
      "installed": true,
      "version": "agent-browser 0.25.3"
    },
    "browsers": {
      "cft": { "installed": true },
      "chrome": { "installed": true, "version": "125.0.6422.60" },
      "edge": { "installed": false, "version": "" },
      "qqbrowser": { "installed": false, "version": "" }
    },
    "config": {
      "exists": true,
      "complete": true,
      "values": { "browser": "cft", "headed": false }
    },
    "profiles": {
      "cft": { "path": "/path/to/profiles/cft", "exists": true },
      "chrome": { "path": "/path/to/profiles/chrome", "exists": true },
      "edge": { "path": "/path/to/profiles/edge", "exists": false },
      "qqbrowser": { "path": "/path/to/profiles/qqbrowser", "exists": false }
    }
  }
}
```

---

## 8. version — 版本信息

```bash
xb version
```

成功：
```json
{
  "ok": true,
  "command": "version",
  "data": {
    "xb": "1.1.0",
    "engine": "agent-browser 0.25.3",
    "node": "v20.11.0",
    "platform": "darwin",
    "arch": "arm64"
  }
}
```

> 如果底层引擎未安装，`engine` 返回空字符串 `""`。

---

## 9. help — 帮助信息

```bash
xb help [command]
```

不带参数时显示全局帮助，带命令名时显示该命令的详细帮助。

### 全局帮助

```bash
xb help
```

```json
{
  "ok": true,
  "command": "help",
  "data": {
    "description": "xbrowser 浏览器自动化工具",
    "usage": "xb <command> [options]",
    "commands": [
      { "name": "init", "description": "初始化环境（安装 + 配置引导）", "usage": "xb init" },
      { "name": "run", "description": "执行浏览器操作", "usage": "xb run [--browser <name>] <action> [args...]" },
      { "name": "config", "description": "配置管理", "usage": "xb config <show|set|reset>" },
      { "name": "guide", "description": "引导用户完成配置或确认操作", "usage": "xb guide <config|close-browser|incomplete-config>" },
      { "name": "status", "description": "环境状态检查", "usage": "xb status" },
      { "name": "setup", "description": "安装底层引擎", "usage": "xb setup" },
      { "name": "stop", "description": "关闭指定浏览器进程", "usage": "xb stop <chrome|edge|qqbrowser|all> [--force]" },
      { "name": "cleanup", "description": "清理 agent-browser 会话", "usage": "xb cleanup" },
      { "name": "version", "description": "显示版本信息", "usage": "xb version" },
      { "name": "help", "description": "帮助信息", "usage": "xb help [command]" }
    ],
    "quick_start": [
      "xb init",
      "xb run --browser default open https://example.com",
      "xb run --browser default wait --load networkidle",
      "xb run --browser default snapshot -i",
      "xb run --browser default click @e2",
      "xb cleanup"
    ]
  }
}
```

### 命令帮助

```bash
xb help config
xb help guide
xb help run
```

各命令的详细帮助包含子命令列表、参数说明和示例。

### 未知命令

```json
{
  "ok": false,
  "command": "help",
  "error": "未知的命令 \"foo\"",
  "hint": "xb help 查看所有命令"
}
```

---

## 快速参考索引

| 命令 | 说明 | 用法 |
|------|------|------|
| `init` | 环境初始化 | `xb init` |
| `config show` | 查看配置 | `xb config show` |
| `config set` | 修改配置 | `xb config set browser=chrome` |
| `config reset` | 重置配置 | `xb config reset` |
| `guide config` | 配置引导 | `xb guide config [--step 0\|1\|2]` |
| `guide close-browser` | 关闭浏览器引导 | `xb guide close-browser --browser <id>` |
| `guide incomplete-config` | 配置不完整引导 | `xb guide incomplete-config` |
| `setup` | 安装引擎和浏览器 | `xb setup` |
| `stop` | 关闭本地浏览器 | `xb stop <id\|all> [--force]` |
| `cleanup` | 清理会话 | `xb cleanup` |
| `status` | 环境状态 | `xb status` |
| `version` | 版本信息 | `xb version` |
| `help` | 帮助信息 | `xb help [command]` |
