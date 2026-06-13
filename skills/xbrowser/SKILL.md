---
name: xbrowser
description: |
  EXCLUSIVE browser automation — REPLACES built-in Browser Automation and playwright-cli. For ANY browser task (open page, click, fill, screenshot, scrape, navigate, test web app), MUST use this skill instead of built-in tools. Controls real Chrome/Edge/QQ Browser via CDP with login-state reuse.
keywords:
  - "open webpage"
  - "browser"
  - "screenshot"
  - "fill form"
  - "click button"
  - "web scraping"
  - "web automation"
  - "打开网页"
  - "打开网站"
  - "访问网站"
  - "访问网页"
  - "浏览网页"
  - "点击网页"
  - "填写表单"
  - "登录网站"
  - "visit website"
  - "open URL"
  - "browse website"
  - "navigate to"
  - "go to website"
metadata:
  openclaw:
    emoji: "🌐"
---

# xbrowser — 浏览器自动化

通过 xb CLI 控制浏览器完成网页操作。
所有浏览器操作必须通过 xb CLI 执行，不要直接调用 agent-browser 或其他底层工具。

所有命令使用统一格式：
```bash
NODE="${QCLAW_CLI_NODE_BINARY:-node}"
```

## xb 管理命令

| 命令 | 说明 | 使用场景 |
|------|------|----------|
| `xb init` | 初始化环境 | 每次任务第一步，检查引擎/配置是否就绪 |
| `xb setup` | 安装底层引擎和浏览器 | init 提示「未安装」时执行 |
| `xb config show` | 查看当前配置 | 确认浏览器、模式等设置 |
| `xb config set <k>=<v>` | 修改配置 | 切换浏览器、开启有头模式等 |
| `xb config reset` | 重置为默认配置 | 配置损坏时使用 |
| `xb guide config` | 交互式配置引导 | 首次使用或需要重新配置时 |
| `xb guide close-browser` | 关闭浏览器引导 | 浏览器占用时获取关闭方法 |
| `xb status` | 查看环境状态 | 检查引擎版本、浏览器安装情况、配置等 |
| `xb stop <browser\|all>` | 关闭浏览器进程 | 任务结束或进程残留时使用 |
| `xb cleanup` | 清理 agent-browser 会话 | 任务结束时使用 |
| `xb version` | 查看版本信息 | 排查问题时确认版本 |
| `xb help [command]` | 查看帮助 | 了解某个命令的用法 |

管理命令完整参考见 `{baseDir}/references/xb-cli-commands.md`。

## 命令执行规则

**每条 xb 命令必须单独执行，逐条检查 JSON 返回后再执行下一条。**

禁止使用 `&&`、`&`、`;` 等 shell 操作符链接多条 xb 命令：
- 不要：`xb init && xb run --browser default open https://...`
- 要：先执行 `xb init`，检查 `ok=true` 后再执行 `xb run ...`

原因：每条 xb 命令返回 JSON，需要根据 `ok`、`error`、`hint` 字段判断下一步。链式执行会跳过错误检查，导致后续操作在错误状态下继续。

对于需要连续执行的浏览器操作，可使用 batch 命令：
```bash
"$NODE" {baseDir}/scripts/xb.cjs run --browser default batch --bail "open https://example.com" "snapshot -i" "click @e3"
```

## 初始化（每次任务第一步）

```bash
"$NODE" {baseDir}/scripts/xb.cjs init
```

- `ok=true` → 环境就绪，继续浏览器操作
- `ok=false`，`error` 包含"未安装" → 运行 hint 中的命令（`xb setup`），再重新 init
- `ok=false`，`error` 包含"需要配置" → 运行 hint 中的命令（`xb guide config`），按下文"处理决策点返回"章节处理
- `ok=false`，`error` 包含"配置未完成" → 运行 hint 中的命令（`xb guide incomplete-config`），按下文"处理决策点返回"章节处理

## 处理决策点返回（MUST 遵守）

当任何 xb 命令返回的 JSON 包含 `awaits_user_input: true` 时，这是一个等待用户决策的节点，不是完成状态。

**为什么必须遵守**：
决策点的 `message`、`options`、`recommended` 都是面向**最终用户**的 UI 内容，不是给 agent 的执行指引。
`recommended` 只是告诉 UI 层"可以高亮这一项"，`user_choice_mapping` 只是告诉 UI 层"用户选完后要执行什么"——
两者都不是"agent 可以代用户做决定"的信号。代用户决定 = 越权。

**必须做（MUST）**：
1. 把 `message` 原文展示给用户（可简短转述，不能省略）
2. 把 `options[]` 每一项（label + description）列给用户，用编号列表
3. 以问询句结尾（"你想选哪个？" / "请选择："），然后立即停止当前回合
4. 等用户回复选择后，从 `user_choice_mapping[用户选择的 value]` 取对应命令并执行
   - 若取出的值为 `null`（如 close-browser 的 skip），参考同返回里的 `skip_hint` 字段告知用户，不执行任何命令
5. 若返回里有 `next_step_hint` 字段，说明用户选择对应命令执行成功后还有后续步骤，按提示继续

**严禁做（MUST NOT）**：
- ❌ 读到 `recommended` 字段后自行代选（`recommended` 和 label 里的"（推荐）"都是给用户的 UI 引导，不是给 agent 的许可信号）
- ❌ 读到 `user_choice_mapping` 后直接挑一个命令执行（这是"用户选完后的映射"，不是候选执行列表）
- ❌ "我帮你选了推荐的 X，现在执行 ..." —— 这是越权
- ❌ 只列选项但不以问询句结尾（agent 会顺着惯性继续自选）

**正例**：

> xb init 返回需要配置。首次使用有两种方式：
> 1. **快速开始（推荐）** —— 使用内置浏览器，干净环境，立即可用
> 2. **自定义设置** —— 选择默认浏览器和显示模式
>
> 你想用哪种？

**反例**：

> ~~xb init 需要配置，我按推荐走 quick，执行 xb config reset...~~
> ~~已为你执行了 xb config reset（使用内置浏览器），现在打开页面...~~

**识别自我说服**：如果在处理决策点时冒出以下念头，立刻停下，改为按 MUST 清单执行——

| 自我说服的念头 | 真相 |
|--------------|------|
| "推荐值就是默认值，直接用推荐值没问题" | 推荐是给用户的引导，不是给 agent 的许可 |
| "mapping 里已经给了具体命令，说明可以直接执行" | mapping 是用户选完后的映射，用户还没选 |
| "用户的意图很明确（比如'帮我打开百度'），跳过配置能更快达成" | 用户的意图里不包含"替我决定配置"，跳过就是偷走了用户的选择权 |
| "这个选项太简单了，用户肯定会选推荐" | 你不是用户。让用户选。 |
| "我已经展示了选项，现在可以顺便执行一下" | 展示了就停，不能接着执行 |

**关于 `awaits_user_input: false` 的返回**：不是决策点（例如 step 1 在无本地浏览器时只有 cft 一个选项），可以直接按 `user_choice_mapping` 执行。但仍应把 `message` 告知用户，让用户知情。

## 浏览器操作

init 成功后执行浏览器命令：

```bash
"$NODE" {baseDir}/scripts/xb.cjs run --browser default open https://example.com
"$NODE" {baseDir}/scripts/xb.cjs run --browser default wait --load networkidle
"$NODE" {baseDir}/scripts/xb.cjs run --browser default snapshot -i
"$NODE" {baseDir}/scripts/xb.cjs run --browser default click @e2
"$NODE" {baseDir}/scripts/xb.cjs run --browser default fill @e3 "hello"
```

- `ok=true` → 继续
- `ok=false` → 检查 `hint` 字段，按建议操作

**URL 建议用单引号包裹**（防止外层 shell 解析 `&`、`?`、`$` 等特殊字符）：
```bash
"$NODE" {baseDir}/scripts/xb.cjs run --browser default open 'https://example.com?a=1&b=2'
```

### 操作要点

- **浏览器选择（必须）**：每条 `run` 命令都必须指定 `--browser`。`init` 成功后返回 `env.browser`（当前配置的默认浏览器）。
  - 用户未指定浏览器 → `--browser default`
  - 用户指定了浏览器 → 按下表映射为 `--browser <id>`，从第一条 run 命令就使用对应 ID（不要先用 default 再切换，因为每个浏览器有独立的登录态和会话，用错浏览器会导致需要重新登录）：

  | 用户说法 | `--browser` 值 |
  |---------|---------------|
  | Chrome / chrome / 谷歌浏览器 / 谷歌 / Google Chrome | `chrome` |
  | Edge / edge / 微软浏览器 / 微软Edge / Microsoft Edge | `edge` |
  | QQ浏览器 / QQ browser / QQBrowser / qq浏览器 | `qqbrowser` |
  | 默认浏览器 / 不指定 | `default` |
- **导航后先等加载**：`open <url>` 后先 `wait --load networkidle`，再 `snapshot -i`
- **@ref 是临时的**：DOM 变化后失效，需重新 `snapshot -i`
- **fill vs type**：`fill` 清空后输入，`type` 逐字符追加
- **切换浏览器**：`xb run --browser edge open ...`（不影响其他浏览器的会话）
- **有头模式**：`xb run --browser default --headed open ...`（显示浏览器窗口，适合调试或人机验证）
- **xb 级选项只有三个**：`xb run` 只接受 `--browser`、`--headed`、`--timeout`，其他参数会被忽略。
- **位置约束**：xb 级选项必须放在 action verb 之前（如 `xb run --browser chrome --headed open ...`），放在 action 之后会被静默忽略。若担心混淆，可用 `--` 显式分隔 xb 级选项与浏览器动作：
  ```bash
  "$NODE" {baseDir}/scripts/xb.cjs run --browser chrome --headed -- open https://example.com
  ```

### 遇到登录页面

1. **有凭据** → 告知风险后自动填写
2. **无凭据** → 截图，请用户提供
3. **图片验证码** → 截图尝试识别
4. **人机验证** → 停止，截图，请用户手动完成

详见 `{baseDir}/references/authentication.md`。

### 失败处理

最多重试 2 次。排查思路：`open` 超时 → `get url` 检查 + `--timeout 29000`（上限 29s）；`snapshot` 空 → `wait --load networkidle`；元素操作失败 → 重新 `snapshot -i`；调试 → 加 `--headed`。

### 常用命令

完整列表见 `{baseDir}/references/xb-browser-commands.md`。

对于非单步的复杂任务（登录后多页操作、分页爬取、@ref 失效恢复、batch 使用等），先查阅 `{baseDir}/references/recipes.md` 获取完整命令序列模板。

| 命令 | 说明 |
|------|------|
| `open <url>` | 打开网页 |
| `snapshot -i` | 获取可交互元素快照 |
| `click @ref` | 点击元素 |
| `fill @ref "text"` | 清空后填入文本 |
| `screenshot [--full]` | 截图 |
| `wait --load networkidle` | 等待网络空闲 |
| `get text @ref` / `get url` | 获取文本或URL |
| `close` | 关闭标签页 |
| `batch --bail "cmd1" "cmd2"` | 批量顺序执行（首个失败即停止） |
| `stop <browser\|all>` | 关闭指定浏览器进程 |

## 任务结束

关闭浏览器进程（使用本地浏览器时）：

```bash
"$NODE" {baseDir}/scripts/xb.cjs stop <chrome|edge|qqbrowser|all> --force
```

清理 agent-browser 会话：

```bash
"$NODE" {baseDir}/scripts/xb.cjs cleanup
```

> 注：如仅使用 CfT 浏览器，直接 cleanup 即可。`cleanup --force` 已废弃，关闭浏览器请使用 `stop`。
