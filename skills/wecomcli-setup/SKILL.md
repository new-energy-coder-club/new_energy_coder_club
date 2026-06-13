---
name: wecomcli-setup
description: 企业微信 CLI 安装引导与自然语言翻译技能。引导用户完成 wecom-cli 的下载安装、Skills 安装、初始化配置（扫码/手动接入），并将用户的自然语言请求翻译为对应的 wecom-cli 命令。当用户说"安装企业微信CLI"、"怎么用 wecom-cli"、"帮我配置企微机器人"、"初始化 wecom-cli"、"怎么使用企业微信命令行"、"wecom-cli 有哪些功能"、"帮我发消息给张三"、"查看我的待办"、"帮我建个会议"、"我想操作企业微信"等需要安装引导或将自然语言翻译成企微 CLI 命令的场景时使用。
metadata:
  requires:
    bins: ["node"]
  cliHelp: "wecom-cli --help"
---

# 企业微信 CLI 安装引导与自然语言翻译

> `wecom-cli` 是企业微信提供的命令行程序，让人类和 AI Agent 都能在终端中操作企业微信。

本技能分为两大部分：
1. **自动安装** — **强制**自动完成 CLI 和 Skills 的安装与初始化，无需询问用户
2. **自然语言翻译** — 将用户的自然语言请求翻译为具体的 `wecom-cli` 命令并执行

> ⚠️ **重要**：当本技能被激活时，你**必须立即自动执行**第一部分的全部检查与安装步骤，**不要询问用户是否要安装**，直接执行命令。只有在遇到无法自动解决的错误时（如 Node.js 未安装且无法自动安装）才向用户报告。

---

## 第一部分：自动安装（强制执行）

> **强制规则**：本部分的所有步骤**必须自动执行**，不要向用户询问"是否要安装"或"是否继续"。直接运行命令，只在失败时报告错误。

### 步骤 1：检查 Node.js 版本（强制）

立即执行：

```bash
node --version
```

- Node.js >= 18 → 继续下一步
- 未安装或版本过低 → **停止并告知用户**：
  > Node.js 18 或更高版本是必需的前置依赖，请先安装后重试。
  > - macOS/Linux 推荐使用 [nvm](https://github.com/nvm-sh/nvm)：`nvm install 18 && nvm use 18`
  > - Windows 推荐使用 [nvm-windows](https://github.com/coreybutler/nvm-windows) 或直接从 [Node.js 官网](https://nodejs.org/) 下载安装

### 步骤 2：检查并安装 wecom-cli（强制）

立即执行：

```bash
wecom-cli --version
```

- 已安装 → 记录版本号，继续下一步
- 未安装（命令不存在）→ **立即自动安装，不要询问用户**：

**macOS / Linux：**

```bash
export NPM_CONFIG_PREFIX="$QCLAW_NPM_GLOBAL_PREFIX" && npm install -g @wecom/cli --force
```

**Windows：**

```powershell
$env:NPM_CONFIG_PREFIX=$env:QCLAW_NPM_GLOBAL_PREFIX; npm install -g @wecom/cli --force
```

安装完成后验证：

```bash
wecom-cli --version
```

如果安装失败（如权限问题），macOS/Linux 尝试：

```bash
export NPM_CONFIG_PREFIX="$QCLAW_NPM_GLOBAL_PREFIX" && sudo npm install -g @wecom/cli --force
```

仍然失败时才向用户报告错误。

> ⚠️ **必须**在 `npm install -g` 前设置 `NPM_CONFIG_PREFIX` 为 `QCLAW_NPM_GLOBAL_PREFIX` 的值（macOS/Linux 用 `export`，Windows 用 `$env:`）。Agent 子进程虽然注入了 `QCLAW_NPM_GLOBAL_PREFIX`（macOS: `~/Library/Application Support/QClaw/npm-global/`，Windows: `%APPDATA%/QClaw/npm-global/`），但 `NPM_CONFIG_PREFIX` 可能在 exec tool 的 shell 环境中丢失，导致 npm 使用系统默认 prefix 安装到错误位置。
> **⚠️ 禁止引导用户在外部终端手动执行 `npm install -g`**——外部终端的 npm prefix 不同，安装后 Agent 子进程仍然找不到。

### 步骤 3：检查并安装 Agent Skills（强制，不可跳过）

> ⚠️ **此步骤绝对不可跳过**，即使 CLI 已安装、凭证已存在也必须执行此检查。Skills 是 LLM 调用企微功能的前提。

首先检查 skills 是否已安装：

**macOS / Linux：**

```bash
ls ~/.agents/skills/wecomcli-contact/SKILL.md ~/.agents/skills/wecomcli-doc/SKILL.md ~/.agents/skills/wecomcli-meeting/SKILL.md ~/.agents/skills/wecomcli-msg/SKILL.md ~/.agents/skills/wecomcli-schedule/SKILL.md ~/.agents/skills/wecomcli-todo/SKILL.md 2>/dev/null | wc -l
```

**Windows：**

```powershell
@("wecomcli-contact","wecomcli-doc","wecomcli-meeting","wecomcli-msg","wecomcli-schedule","wecomcli-todo") | Where-Object { Test-Path "$env:USERPROFILE\.agents\skills\$_\SKILL.md" } | Measure-Object | Select-Object -ExpandProperty Count
```

判断逻辑：
- 结果为 **6**（6 个 SKILL.md 都存在）→ Skills 已安装，继续下一步
- 结果 **< 6**（任何一个缺失）→ 先检查 Git，再安装：

检查 Git 是否可用：

```bash
git --version
```

- Git 可用 → **立即执行安装，不要询问用户**：

```bash
npx skills add WeComTeam/wecom-cli -y -g
```

- Git 未安装 → **停止并告知用户**：
  > Git 是安装 Skills 的必要依赖（`skills add` 需要从 GitHub 拉取文件）。请先安装 Git：
  > - macOS: `xcode-select --install` 或 `brew install git`
  > - Windows: 下载 [Git for Windows](https://git-scm.com/download/win)
  > - Linux: `sudo apt install git` 或 `sudo yum install git`

安装完成后再次使用上述对应平台的检查命令验证。

验证结果为 6 则继续，否则报告安装失败。

### 步骤 4：检查凭证状态（强制）

立即检查凭证目录：

**macOS / Linux：**

```bash
ls ~/.config/wecom/bot.enc ~/.config/wecom/mcp_config.enc 2>/dev/null
```

**Windows：**

```powershell
Test-Path "$env:USERPROFILE\.config\wecom\bot.enc"; Test-Path "$env:USERPROFILE\.config\wecom\mcp_config.enc"
```

> ⚠️ 注意：凭证目录可通过环境变量 `WECOM_CLI_CONFIG_DIR` 自定义，若该变量已设置，检查该目录下的 `bot.enc` 和 `mcp_config.enc`。

判断逻辑：

| `bot.enc` | `mcp_config.enc` | 结论 | 操作 |
|-----------|-------------------|------|------|
| ✅ 存在 | ✅ 存在 | **已初始化** | 跳过步骤 5，直接验证（步骤 6） |
| ✅ 存在 | ❌ 不存在 | 配置不完整 | 执行步骤 5 |
| ❌ 不存在 | 任意 | 未初始化 | 执行步骤 5 |

### 步骤 5：初始化配置（仅凭证缺失时执行）

当步骤 4 判断需要初始化时，**立即告知用户需要执行初始化**并执行：

```bash
wecom-cli init
```

> `wecom-cli init` 是交互式命令（需要用户扫码或输入凭证），因此这一步需要用户参与。告知用户：
> - **推荐扫码接入**：终端会显示二维码，用企业微信 App 扫描即可
> - **备选手动输入**：输入 Bot ID 和 Secret（获取方式参考 [企业微信说明](https://open.work.weixin.qq.com/help2/pc/cat?doc_id=21677)）

### 步骤 6：验证安装（强制）

立即执行验证命令：

```bash
wecom-cli contact get_userlist '{}'
```

- 返回正常结果 → 安装成功，展示功能概览卡片
- 返回错误 → 凭证可能失效，提示用户重新执行 `wecom-cli init`

---

### 自动安装完整流程（AI 必须遵循）

```
技能激活
    │
    ├── 1. [自动执行] node --version
    │      ├── >= 18 → 继续
    │      └── 未安装/版本低 → 停止，告知用户安装 Node.js
    │
    ├── 2. [自动执行] wecom-cli --version
    │      ├── 已安装 → 继续
    │      └── 未安装 → [自动执行] export NPM_CONFIG_PREFIX="$QCLAW_NPM_GLOBAL_PREFIX" && npm install -g @wecom/cli --force
    │
    ├── 3. [自动执行] 检查 ~/.agents/skills/wecomcli-*/SKILL.md 是否齐全（6个）
    │      ├── 6 个都存在 → 继续
    │      └── 有缺失 → [自动执行] npx skills add WeComTeam/wecom-cli -y -g
    │
    ├── 4. [自动执行] ls ~/.config/wecom/bot.enc ~/.config/wecom/mcp_config.enc
    │      ├── 两个文件都存在 → 跳到步骤 6
    │      └── 文件缺失 → 继续步骤 5
    │
    ├── 5. [需用户参与] wecom-cli init（交互式扫码/输入凭证）
    │
    └── 6. [自动执行] wecom-cli contact get_userlist '{}'
           ├── 成功 → 展示功能概览
           └── 失败 → 提示重新 init
```

### 安装问题排查

| 问题 | 自动处理方案 |
|------|----------|
| `npm: command not found` | 停止并告知用户安装 Node.js >= 18 |
| 安装后 `wecom-cli: command not found` | 强制重装：macOS/Linux `export NPM_CONFIG_PREFIX="$QCLAW_NPM_GLOBAL_PREFIX" && npm install -g @wecom/cli --force`；Windows `$env:NPM_CONFIG_PREFIX=$env:QCLAW_NPM_GLOBAL_PREFIX; npm install -g @wecom/cli --force` |
| npm 全局安装权限不足 | macOS/Linux 尝试 `export NPM_CONFIG_PREFIX="$QCLAW_NPM_GLOBAL_PREFIX" && sudo npm install -g @wecom/cli`（Windows 通常不需要 sudo） |
| 初始化提示"凭证验证失败" | 告知用户 Bot ID/Secret 不正确或企业不满足条件（≤ 10 人） |
| 扫码超时 | 告知用户重新执行 `wecom-cli init` |

---

## 第二部分：自然语言翻译为 CLI 命令

### 翻译总则

当用户用自然语言描述企业微信操作时，按以下规则翻译为 CLI 命令：

1. **识别意图** → 判断属于哪个品类（contact/doc/meeting/msg/schedule/todo）
2. **确定方法** → 匹配具体的工具方法
3. **提取参数** → 从自然语言中提取参数值，构建 JSON
4. **执行命令** → 运行 `wecom-cli <品类> <方法> '<json参数>'`
5. **解读结果** → 将 JSON 返回值翻译为用户友好的自然语言

> ⚠️ **Windows (PowerShell) JSON 参数引号规则**：PowerShell 对引号处理与 bash 不同。
> - 简单 JSON（无嵌套双引号）：`wecom-cli contact get_userlist '{}'` 可正常工作
> - 复杂 JSON（含双引号键值）：需将外层改为双引号并转义内部双引号，例如：
>   - bash: `wecom-cli todo create_todo '{"content":"写周报"}'`
>   - PowerShell: `wecom-cli todo create_todo '{\"content\":\"写周报\"}'`

---

### 品类与方法速查表

#### 👤 通讯录（contact）

| 自然语言示例 | CLI 命令 |
|-------------|----------|
| "帮我查一下张三" | `wecom-cli contact get_userlist '{}'` → 本地筛选 |
| "公司都有谁" | `wecom-cli contact get_userlist '{}'` |
| "Sam 是谁" | `wecom-cli contact get_userlist '{}'` → 按 alias 匹配 |

> 通讯录只有 `get_userlist` 一个方法，所有人员查找都走全量获取 + 本地筛选。

---

#### ✅ 待办（todo）

| 自然语言示例 | CLI 命令 |
|-------------|----------|
| "看看我的待办" | `wecom-cli todo get_todo_list '{}'` → `get_todo_detail` |
| "我有哪些待办" | `wecom-cli todo get_todo_list '{}'` → `get_todo_detail` |
| "这个月的待办" | `wecom-cli todo get_todo_list '{"create_begin_time":"2026-04-01 00:00:00","create_end_time":"2026-04-30 23:59:59"}'` |
| "帮我建个待办：写周报" | `wecom-cli todo create_todo '{"content":"写周报"}'` |
| "创建待办提醒我明天10点开会" | `wecom-cli todo create_todo '{"content":"开会","remind_time":"2026-04-11 10:00:00"}'` |
| "把待办分派给张三" | 先查 userid → `wecom-cli todo update_todo '{"todo_id":"...","follower_list":{"followers":[{"follower_id":"zhangsan","follower_status":1}]}}'` |
| "标记待办完成" | `wecom-cli todo change_todo_user_status '{"todo_id":"...","user_status":2}'` |
| "删掉那个待办" | `wecom-cli todo delete_todo '{"todo_id":"..."}'`（需确认） |

**关键规则**：
- 查列表后**必须**查详情（`get_todo_list` → `get_todo_detail`）
- 人员 ID **必须**通过 `contact get_userlist` 转为姓名
- 分页 `has_more=true` 时**必须**告知用户

---

#### 🎥 会议（meeting）

| 自然语言示例 | CLI 命令 |
|-------------|----------|
| "帮我约个明天下午3点的会" | `wecom-cli meeting create_meeting '{"title":"会议","meeting_start_datetime":"2026-04-11 15:00","meeting_duration":3600}'` |
| "创建会议邀请张三李四" | 先查 userid → `create_meeting` 带 `invitees` |
| "这周有哪些会" | `wecom-cli meeting list_user_meetings '{"begin_datetime":"...","end_datetime":"...","limit":100}'` → 逐个 `get_meeting_info` |
| "取消明天的会" | 先查找定位 → `wecom-cli meeting cancel_meeting '{"meetingid":"..."}'` |
| "把王五加到会议里" | 先获取当前成员 → 合并 → `set_invite_meeting_members`（全量覆盖） |

**关键规则**：
- 时间格式 `YYYY-MM-DD HH:mm`
- 查详情需两步：`list_user_meetings` → `get_meeting_info`
- 更新成员是**全量覆盖**，需先获取现有成员再合并
- 创建成功后展示**会议号**（每3位加 `-` 分隔）

---

#### 💬 消息（msg）

| 自然语言示例 | CLI 命令 |
|-------------|----------|
| "最近谁给我发过消息" | `wecom-cli msg get_msg_chat_list '{"begin_time":"...","end_time":"..."}'` |
| "看看和张三的聊天记录" | 先查 chatid → `wecom-cli msg get_message '{"chat_type":1,"chatid":"zhangsan","begin_time":"...","end_time":"..."}'` |
| "给张三发消息：明天开会" | 先查 chatid → `wecom-cli msg send_message '{"chat_type":1,"chatid":"zhangsan","msgtype":"text","text":{"content":"明天开会"}}'`（需确认） |
| "看看群里发了什么图片" | 先定位群 → 拉消息 → 询问是否下载 → `get_msg_media` |

**关键规则**：
- 时间格式 `YYYY-MM-DD HH:mm:ss`，仅支持**7天内**
- chatid 通过 `get_msg_chat_list` 按名称匹配
- 提到"群"时 `chat_type=2`，否则默认 `chat_type=1`
- 发送前**必须确认**
- 非文本消息下载后**必须告知路径**并**询问是否删除**

---

#### 📅 日程（schedule）

| 自然语言示例 | CLI 命令 |
|-------------|----------|
| "今天有什么日程" | `get_schedule_list_by_range` → `get_schedule_detail` |
| "帮我建个日程：明天下午2点需求评审" | `wecom-cli schedule create_schedule '{"schedule":{"start_time":"...","end_time":"...","summary":"需求评审","reminders":{"is_remind":1,"remind_before_event_secs":900,"timezone":8}}}'` |
| "把明天的评审改到后天" | 先定位 → `update_schedule` |
| "取消今天下午的日程" | 先定位 → `cancel_schedule`（需确认） |
| "把张三加到日程里" | 先查 userid → `add_schedule_attendees` |
| "看看张三明天有没有空" | 先查 userid → `check_availability` |

**关键规则**：
- 列表查询仅支持**前后30天**
- 返回的时间是 **Unix 时间戳**，需转为可读格式
- 未指定提醒时默认提前 15 分钟（`remind_before_event_secs: 900`）

---

#### 📄 文档 / 📊 智能表格（doc）

| 自然语言示例 | CLI 命令 |
|-------------|----------|
| "帮我新建个文档叫周报" | `wecom-cli doc create_doc '{"doc_type":3,"doc_name":"周报"}'` |
| "创建一个智能表格" | `wecom-cli doc create_doc '{"doc_type":10,"doc_name":"..."}'` |
| "读取这个文档的内容" | `wecom-cli doc get_doc_content '{"docid":"...","type":2}'`（需轮询） |
| "修改文档内容为..." | 先读内容 → `edit_doc_content` 覆写 |
| "查看表格里的数据" | `smartsheet_get_sheet` → `smartsheet_get_fields` → `smartsheet_get_records` |
| "往表格里加一行" | 先查字段类型 → `smartsheet_add_records` |

**关键规则**：
- `get_doc_content` 采用**异步轮询**：首次返回 `task_id`，`task_done=false` 时需携带 `task_id` 重复调用
- `doc_type=3` 是文档，`doc_type=10` 是智能表格
- 支持 `docid` 或 `url` 两种定位方式
- 字段更新**只能改名不能改类型**

---

### 翻译执行流程

当用户用自然语言提出请求时，按以下完整流程执行：

```
用户自然语言
    │
    ├── 1. 检测 wecom-cli 是否可用
    │      ├── 未安装 → [自动执行] 第一部分安装流程（不询问用户）
    │      └── 已安装 → 检查凭证文件
    │            ├── bot.enc 和 mcp_config.enc 都存在 → 已就绪，继续
    │            │   （macOS/Linux: ~/.config/wecom/，Windows: %USERPROFILE%\.config\wecom\）
    │            └── 凭证缺失 → [自动执行] wecom-cli init
    │
    ├── 2. 识别意图 → 匹配品类和方法
    │
    ├── 3. 是否需要人员信息？
    │      └── 是 → wecom-cli contact get_userlist '{}' 查 userid
    │
    ├── 4. 是否需要定位目标（会议/日程/待办）？
    │      └── 是 → 查列表 → 匹配关键词 → 定位 ID
    │
    ├── 5. 构建 JSON 参数
    │      ├── 时间参数：相对时间（"明天"/"下周一"）→ 具体日期
    │      ├── 人员参数：姓名 → userid
    │      └── 其他参数：从上下文提取
    │
    ├── 6. 执行 CLI 命令
    │
    └── 7. 解读返回结果
           ├── errcode=0 → 翻译为友好文字展示
           ├── errcode!=0 → 展示错误信息，必要时重试（最多3次）
           └── 人员 ID → 转为姓名后展示
```

---

### 多步操作示例

#### 示例 1："帮我看看我的待办，然后给张三发消息说周报已提交"

**翻译为**：

```bash
# 第一步：查待办
wecom-cli todo get_todo_list '{}'
wecom-cli todo get_todo_detail '{"todo_id_list":["TODO_ID_1","TODO_ID_2"]}'

# 第二步：查通讯录获取张三的 userid
wecom-cli contact get_userlist '{}'

# 第三步：发消息（需用户确认后执行）
wecom-cli msg send_message '{"chat_type":1,"chatid":"zhangsan","msgtype":"text","text":{"content":"周报已提交"}}'
```

#### 示例 2："查一下我和张三明天下午都有空的时间，约个1小时的会"

**翻译为**：

```bash
# 第一步：查通讯录获取张三的 userid
wecom-cli contact get_userlist '{}'

# 第二步：查闲忙
wecom-cli schedule check_availability '{"check_user_list":["my_userid","zhangsan"],"start_time":"2026-04-11 12:00:00","end_time":"2026-04-11 18:00:00"}'

# 第三步：根据空闲时段创建会议
wecom-cli meeting create_meeting '{"title":"会议","meeting_start_datetime":"2026-04-11 14:00","meeting_duration":3600,"invitees":{"userid":["zhangsan"]}}'
```

---

## 功能概览卡片

安装成功后，向用户展示以下功能概览：

```
🎉 wecom-cli 已就绪！以下是你可以做的事情：

👤 通讯录  wecom-cli contact  — 查询成员、搜索人员
✅ 待  办  wecom-cli todo     — 创建/查看/更新/删除待办
🎥 会  议  wecom-cli meeting  — 预约/查询/取消会议
💬 消  息  wecom-cli msg      — 查看聊天记录、发送消息
📅 日  程  wecom-cli schedule — 管理日程、查询闲忙
📄 文  档  wecom-cli doc      — 创建/编辑文档和智能表格

💡 你可以直接用自然语言告诉我你想做什么，例如：
   "帮我查一下张三是谁"
   "创建一个明天下午的会议"
   "看看我最近的待办"
   "给李四发消息说项目已完成"
```

---

## 注意事项

1. **自动安装**：本技能激活后**必须自动执行**安装检查和安装步骤，不要询问用户"是否安装"。只有 Node.js 缺失和 `wecom-cli init`（交互式）需要用户参与
2. **前置条件**：使用前需确保 Node.js >= 18 已安装，企业微信账号所在企业人数 ≤ 10 人
3. **凭证安全**：Bot ID 和 Secret 经 AES-256-GCM 加密存储在凭证目录（macOS/Linux: `~/.config/wecom/`，Windows: `%USERPROFILE%\.config\wecom\`），请勿手动修改
4. **凭证检测**：执行任何操作前，先检查凭证目录下 `bot.enc` 和 `mcp_config.enc` 是否存在；两者都存在则无需 `wecom-cli init`，直接可用
5. **自定义凭证路径**：如用户设置了环境变量 `WECOM_CLI_CONFIG_DIR`，凭证文件位于该变量指定的目录下，检测时需先确认实际路径（macOS/Linux: `echo $WECOM_CLI_CONFIG_DIR`，Windows: `echo $env:WECOM_CLI_CONFIG_DIR`）
6. **重新初始化**：如需更换 Bot，重新执行 `wecom-cli init` 即可覆盖旧凭证
7. **平台支持**：macOS (x64/arm64)、Linux (x64/arm64)、Windows (x64)
8. **自然语言翻译精度**：若意图不明确，应向用户追问具体需求而非猜测执行
9. **破坏性操作**：删除待办、取消会议/日程等操作执行前**必须**向用户确认
10. **错误重试**：遇到 HTTP 错误时主动重试，最多 3 次
11. **userid 禁止暴露**：所有展示给用户的信息中，userid 必须替换为真实姓名
