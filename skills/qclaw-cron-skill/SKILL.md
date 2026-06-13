---
name: qclaw-cron-skill
description: |
  [MANDATORY - MUST LOAD] 凡是涉及定时/提醒/闹钟/周期执行/打卡/签到/cron/schedule/remind 等需求，以及修改/编辑/更新/暂停/恢复/删除/取消推送/改推送目标/改推送渠道等已有定时任务的操作，必须读取本 skill，严禁凭记忆猜测参数。
metadata: {"openclaw": {"emoji": "⚙️"}}
---

### cron — 定时任务

> 🚨 **[MANDATORY]** 用户提到「提醒/定时/每天X点/X分钟后/周期/重复/打卡/签到」等时，**必须创建 cron 任务**，口头承诺无效。

#### 第一步：判断「推送目标」

> 🚨 **[MANDATORY] 默认就在用户当前所处渠道提醒，禁止主动反问"推送到哪里"**。
> 用户说「提醒我 / 叫我 / 告诉我 / 让我」等**自指代**表达 → 推送目标 = **当前会话渠道**，不要追问。
> 仅当用户**显式**说"推到企微/飞书/微信群/告诉张三"等**他指代**时，才使用外部渠道。

| 当前会话 sender / channel | 推送目标 | mode |
|--------------------------|---------|------|
| `openclaw-control-ui`（本地 UI / webchat） | 本地（不投递，直接渲染回复） | **`none`** |
| `wechat-access` / `dingtalk-connector` | 当前外部渠道 | `announce` |
| `wecom` / `feishu` / `openclaw-weixin` / `qqbot` | 当前外部渠道 | `announce` |
| 本地 UI **+** 用户显式说"推送到 X" | 外部渠道 X | `announce`（**必须**先读 `~/.qclaw/channel-defaults.json`） |

#### 第二步：判断创建方式

| 场景 | 方式 |
|------|------|
| sender=`openclaw-control-ui`（本地） / channel=`wechat-access` / `dingtalk-connector` | **A：内置 `cron` 工具**, 不需要再读取channel-defaults.json（toolCall，JSON 参数） |
| channel=`wecom`/`feishu`/`openclaw-weixin`/`qqbot` | **B：`openclaw cron add` CLI**（通过 `exec`） |
| sender=`openclaw-control-ui` 但推送到外部渠道 | **B：CLI**（**必须**先读 `~/.qclaw/channel-defaults.json`） |

> 外部渠道 session 中内置 `cron` 工具被 ownerOnly 策略过滤，LLM 不可见，必须走 CLI。dingtalk-connector可以使用内置`cron`工具。

**渠道识别**：显式 `channel` 字段 → 直接使用；无 `channel` 但 `message_id` 以 `openclaw-weixin:` / `wechat-access:` 开头 → 对应渠道。

> 🚨 **[MANDATORY] 外部渠道 `to` 获取规则**：
> 当需要创建推送到外部渠道（wecom/feishu/openclaw-weixin/qqbot/dingtalk-connector/wechat-access）的定时任务时：
> 1. **当前会话有 `sender_id`** → 直接用作 `to`
> 2. **当前会话无 `sender_id`**（如本地 UI 创建推送到外部渠道）→ **必须先读 `~/.qclaw/channel-defaults.json`**，用当前 agentId + 目标 channel 查找 `to`
> 3. **channel-defaults.json 不存在 / 无对应渠道条目 / 无 `to` 值** → **严禁创建任务**，必须告知用户：「请先通过该渠道给机器人发送一条消息，系统会自动记录投递目标，之后再来创建定时任务」
>
> ⛔ **绝对禁止创建 delivery 中没有 `to` 字段的外部渠道定时任务**——这类任务会投递失败，浪费用户的期望。

#### 第三步：时间类型

- 具体时刻 / X分钟后 / 无周期词 → **一次性**（`deleteAfterRun:true` / `--delete-after-run`）
- 每天/每小时/每X分钟 → **周期任务**
- **绝对时间必须先 `date +%z` 获取时区**（`+0800`→`+08:00`），禁止硬编码

#### 第四步：时间参数速查

| 用户说法 | schedule（JSON） | CLI 参数 |
|---------|-----------------|----------|
| 每30分钟 | `{"kind":"every","everyMs":1800000}` | `--every 30m` |
| 每2小时 | `{"kind":"every","everyMs":7200000}` | `--every 2h` |
| 每天早上9点 | `{"kind":"cron","cron":"0 9 * * *"}` | `--cron "0 9 * * *"` |
| 每周一10点 | `{"kind":"cron","cron":"0 10 * * 1"}` | `--cron "0 10 * * 1"` |
| 工作日18点 | `{"kind":"cron","cron":"0 18 * * 1-5"}` | `--cron "0 18 * * 1-5"` |
| 今天下午3点 | `{"kind":"at","at":"2026-04-09T15:00:00+08:00"}` | `--at "..." --delete-after-run` |
| 10分钟后 | `{"kind":"at","at":"<now+10min ISO>"}` | `--at "..." --delete-after-run` |

> cron 表达式：`分 时 日 月 星期`，0=周日，1-5=周一至五。

#### 公共规则（方式 A/B 通用）

> 🚨 **[MANDATORY] message 行为约束**：`payload.message`（方式A）/ `--message`（方式B）末尾**必须**加：
> `要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出提醒文字 (4) 控制在 2-3 句话以内`

> 🚨 **[MANDATORY] agentId 必传，禁止省略，禁止默认填 `"main"`**：
> - sessionKey `agent:【agentId】:session-xxx` → 取第二段
> - 无 sessionKey 但有 cwd `/path/workspace-agent-xxx` → 取最后一段去掉 `workspace-` 前缀（即 `agent-xxx`），禁止再去 `agent-`
> - 以上均无才传 `"main"`；从**当前对话**上下文提取，禁止复用历史

> 🚨 **[MANDATORY] delivery 参数获取优先级**：
> 1. **优先从当前会话上下文** — `channel`、`sender_id`（→`to`）
> 2. **其次读 `~/.qclaw/channel-defaults.json`**（本地→外部渠道时）— 用当前 agentId + 目标 channel 查找
> 3. **无 `to` 则中止** — ⛔ **严禁创建没有 `to` 的外部渠道任务**，必须告知用户：「请先通过该渠道（如企微/飞书）给机器人发送一条消息，之后再来创建定时任务」
>
> 插件辅助处理：本地渠道/无 to 时自动注入 `bestEffort:true`（无须手写）；外部渠道自动写入 channel-defaults.json；**delivery 缺 `channel`/`to` 时插件从 sessionKey 自动补全（硬保底，仅 tool 路径）**。
> ⚠️ **插件保底 ≠ 可以不传 to**：插件的 sessionKey 补全仅适用于外部渠道 session 内（sessionKey 包含渠道信息），本地 UI 发起时 sessionKey 无渠道信息，补全不会生效；CLI 路径完全无 sessionKey 补全。

**🚨 [MANDATORY] mode 必须显式传入**（插件不再自动推断 mode，按下表选择）：

| 场景 | mode | 说明 |
|------|------|------|
| 推送到任何渠道（外部） | `"announce"` | 创建/修改推送任务必传 |
| 不推送或本地渠道（仅本地静默执行） | `"none"` | 取消推送时必传 |

> 💡 **mode 是必填项，不要省略**：
> - 想推送 → `mode:"announce"`，同时给 channel/to
> - 不想推送 → `mode:"none"`，同时**显式清空** channel/to（传空字符串）

**delivery 值速查（mode 必传）：**

| 场景 | delivery |
|------|----------|
| 本地 | `{"mode":"none"}` |
| wechat-access | `{"mode":"announce","channel":"wechat-access","to":"<sender_id>"}` |
| wecom/feishu/dingtalk | `{"mode":"announce","channel":"<渠道>","to":"<sender_id>"}` |
| openclaw-weixin | `{"mode":"announce","channel":"openclaw-weixin","to":"<openid>@im.wechat"}` |

#### 方式 A：内置 `cron` 工具模板

> 🚨 调用 toolName=`cron`，**不是** `exec`，参数为 JSON 对象。
> ⚠️ 模板中的 `delivery` 默认是**本地**场景（`mode:"none"`，对应 webchat/本地 UI 自指代提醒）。
> 推送到外部渠道时按上方"delivery 值速查"替换为 `{"mode":"announce","channel":"...","to":"..."}`。

**周期任务**：
```json
{
  "action": "add",
  "job": {
    "name": "<任务名>", "agentId": "<agentId>",
    "schedule": {"kind":"every","everyMs":1800000},
    "sessionTarget": "isolated",
    "payload": {"kind":"agentTurn","message":"你是一个暖心的提醒助手。请用温暖、有趣的方式提醒用户：{内容}。要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出提醒文字 (4) 控制在 2-3 句话以内"},
    "delivery": {"mode":"none"}
  }
}
```
**一次性**：schedule→`{"kind":"at","at":"<ISO+时区>"}`，加 `"deleteAfterRun":true`

#### 方式 B：`openclaw cron add` CLI 模板

> ⚠️ 末尾的投递参数按场景选择：
> - 本地（webchat 自指代提醒） → `--no-deliver`
> - 外部渠道 → `--announce --channel <渠道> --to <sender_id>`

```bash
openclaw cron add \
  --name "<任务名>" --every 30m --session isolated --agent <agentId> \
  --message "你是一个暖心的提醒助手。请用温暖、有趣的方式提醒用户：{内容}。要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出提醒文字 (4) 控制在 2-3 句话以内" \
  --announce --channel <渠道> --to <sender_id>
```
**一次性**：`--every 30m` → `--at "<ISO+时区>" --delete-after-run`

> 🚨 命令失败最多重试一次，仍失败直接告知用户。

#### 管理命令

> 暂停/停止 ≠ 删除。"暂停/禁用"→disable，"删除"→remove。

**内置工具**：列表 `{"action":"list"}` / 暂停 `{"action":"update","jobId":"<id>","patch":{"enabled":false}}` / 恢复 `…{"enabled":true}` / 删除 `{"action":"remove","jobId":"<id>"}` / 执行 `{"action":"run","jobId":"<id>"}`

**CLI**：`openclaw cron list` / `edit <id> --enabled false/true` / `remove <id>` / `run <id>`

#### 🚨 修改任务专用规则（仅适用于 update / cron edit）

修改任务的 delivery 配置有独特的语义陷阱，必须严格遵守以下规则。

**规则 1：patch 是增量覆盖，不是整体替换**

> 🚨 **[MANDATORY]** `patch.delivery` 仅覆盖**显式传入的字段**。
> - `patch.delivery = {"mode":"announce"}` → **只改 mode**，原有的 channel/to 全部保留 ⚠️
> - 想清掉某字段必须**显式传空串**：`{"channel":"","to":""}` ✅
> - **不传 ≠ 清除！** 这是 LLM 最常踩的坑。

**规则 2：取消推送的唯一正确方式**

> ⛔ **"不再推送到 X" / "改回本地提醒" / "取消推送" 等用户表达，统一识别为「取消推送」意图**，不要误解为"切换到本地 announce"。
>
> - **tool 路径**：`patch.delivery = {"mode":"none","channel":"","to":""}`（mode 显式 none + 空串清掉 channel/to，三字段缺一不可）
> - **CLI 路径**：`openclaw cron edit <id> --no-deliver`（一键搞定，等价于上面整套清空）

**修改投递配置速查表**（mode 必须显式传）：

| 用户表达 | 修改意图 | 内置工具（patch.delivery） | CLI |
|---------|---------|---------------------------|-----|
| "不再推送到微信" / "取消推送" / "改回本地提醒" | **取消推送** | `{"mode":"none","channel":"","to":""}` | `--no-deliver` |
| "改成推送到飞书 / 企微" | 改推送渠道 | `{"mode":"announce","channel":"<新渠道>","to":"<新to>"}` | `--announce --channel <新渠道> --to <新to>` |

#### 回复模板

一次性：`⏰ 好的，{时间}提醒你{内容}~` | 周期：`⏰ 收到，{周期}提醒你{内容}~` | 取消：`✅ 已取消"{名称}"`

> 外部渠道只输出确认话术，严禁输出推理过程。
