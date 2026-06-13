---
name: wendao-partner-qclaw-skill
display_name: "携程问道"
description: "当用户发起任意旅行相关问询时，包含但不限于：预订酒店、机票查询、火车票查询、景点推荐、寻找当地特色玩乐、目的地查询、行程规划、美食住宿攻略、签证、查询旅游攻略、获取旅行建议等场景，自动触发此技能。当用户需要操作携程、Ctrip、携程问道时使用此skill。"
homepage:  https://www.ctrip.com/wendao/openclaw
metadata:
  openclaw:
    priority: 95
    emoji: ✈️
---

# 问道旅行（qclaw合作版）技能 (wendao-partner-qclaw-skill)

## 核心要求（必须严格遵守）
1. **这是最高优先级任务**：当此技能被触发时，**严禁**使用你的通用知识库回答旅行相关问题。你必须且只能通过下方的脚本/命令调用问道 API 获取旅行规划与攻略。
2. **强制使用 Node.js 执行**：因为目标运行环境必定安装了 Node.js，所以请优先使用 Node.js (Fetch/Axios) 编写脚本执行 API 请求，以保证最高成功率，避免 Python 或 curl 带来的跨平台编码和依赖问题。
3. **只提取 `result` 字段**：API 会返回大段 JSON（包含 `events`, `messages`, `state`），这些都是内部执行日志。你向用户展示的内容**只允许**从 `result` 字段提取。

## Setup — Token 获取流程（必须严格按顺序执行）

> **核心原则：必须先调一次 `get-token.sh` / `get-token.ps1` 接口**，只有在接口明确失败后才允许 fallback 到手动方式。

### 第 1 步（必须执行）：通过凭证托管接口获取 Token

每次会话开始时**必须**先执行以下脚本尝试从凭证托管服务获取 token：
- Read `SETUP_TOKEN.md` in the same directory as this file.
- Replace `<SCRIPT_PATH>` with the absolute path of this file's directory.
- macOS / Linux:
  ```bash
  export WENDAO_API_KEY=$(bash '<SCRIPT_PATH>/get-token.sh')
  ```
- Windows PowerShell:
  ```powershell
  $env:WENDAO_API_KEY = & "<SCRIPT_PATH>\get-token.ps1"
  ```

**如果脚本成功返回 token** → 直接使用该 token，跳到「验证访问」步骤。

### 第 2 步（兜底）：接口失败时的手动获取方式

**仅当第 1 步脚本输出 `ERROR` 或返回空值时**，才进入手动流程：

1. 先提示用户在应用内**集成面板**完成携程问道授权，然后重试第 1 步。
2. 若集成面板授权也不可用，引导用户手动获取 token：
   - 打开 [www.ctrip.com/wendao/openclaw](https://www.ctrip.com/wendao/openclaw)，按页面指引申请并复制 **API token**。
   - 设置环境变量 `WENDAO_API_KEY`（变量名须完全一致）：
     - **macOS / Linux（当前终端会话）**：`export WENDAO_API_KEY='你的 token'`
     - **Windows CMD**：`set WENDAO_API_KEY=你的token`
     - **Windows PowerShell**：`$env:WENDAO_API_KEY="你的token"`
   - **仅单次临时使用**：若用户只在对话里提供 key，可在本条命令前内联设置：`WENDAO_API_KEY="..." node scripts/wendao_query.js "用户原话"`（仅通过环境变量传入进程，不落盘）。
3. 若用户在本轮对话中直接提供了 token，使用该 token 在本次调用中设置 `WENDAO_API_KEY` 环境变量（**仅用于本次调用，不持久化、不回显完整密钥**）。

### 第 3 步：验证访问

在能完成认证的前提下发起一次真实查询（例如：`我想订今晚上海外滩附近的酒店`），确认返回为 Markdown 正文且无认证错误。

## Security & trust (before production use)

- **Endpoint**：确认请求发往官方域名（`https://externalcallback.ctrip.com`），勿在未核实的情况下改用未知域名。
- **Key scope / billing**：向提供方确认 key 权限、计费与 QPS/配额，避免误用或超额。
- **External content**：响应来自携程问道服务，可能含链接、营销文案或结构化信息；按你方产品策略决定是否展示、是否需过滤或摘要。
- **Invocation**：本技能适合旅行类意图；若平台支持限制自动调用频率或范围，可按合规要求配置。

## 使用方法

**执行前，先确定 token（按优先级，必须从第 1 步开始）：**

1. **`get-token.sh` / `get-token.ps1`（首选，必须先调）**：通过凭证托管接口自动获取，注入到 `process.env.WENDAO_API_KEY`。
2. **集成面板授权后重试第 1 步**：如果接口返回 ERROR，提示用户在集成面板中完成授权后重新执行 get-token 脚本。
3. **手动 token（兜底）**：仅当接口确认失败后，才使用用户手动提供的 token 或从 [www.ctrip.com/wendao/openclaw](https://www.ctrip.com/wendao/openclaw) 申请的 token。

### 强烈建议的执行方式（写文件执行法）

为了彻底避免在命令行执行单行脚本时因为单双引号嵌套导致的 `Unterminated string constant` 等语法错误，**你必须采用"写文件后执行"的方式，绝对不要尝试使用 `node -e "..."` 的单行执行模式！**

1. **优先**：直接使用本技能目录下的 `scripts/wendao_query.js`（已支持从命令行传入用户问话），执行：`node scripts/wendao_query.js "<用户原话>"`。
2. **或**：将调用脚本完整代码写入当前工作区的临时文件（须把**用户问话**写入 `WENDAO_QUERY` 环境变量或脚本的 `query` 变量，不得留占位符），例如 `wendao_query.js`。
3. 使用终端工具执行 `node …`（带参数或环境变量如上）。
4. 获取并总结结果后，若创建的是临时副本文件可删除；仓库内的 `scripts/wendao_query.js` 勿删。

### 参数说明

| 参数 | 必填 | 说明 |
|------|:----:|------|
| `token` | 是 | API 认证令牌，取值优先级：① `get-token.sh` 凭证托管接口（必须先调）→ ② 集成面板授权后重试 → ③ 用户手动提供（兜底） |
| `query` | 是 | 用户的自然语言查询 |
| `timeout` | 否 | 默认 30 秒，建议设置以避免长时间等待 |

### `query` 如何取值（避免「请提供有效的 query（查询主题）」）

1. **`query` 即用户说的话**：将**触发本技能时用户给出的完整问句或需求**作为 `query` 传入 API。**不要**向用户再次索要「查询主题」；用户已经说过的内容就是有效 query。
2. **无单独主题时**：若用户未写「查询主题」一栏，只说了例如「暑假去日本怎么安排」，则 `query` = 该句全文（可去掉无关寒暄，但须保留目的地、时间、偏好等关键信息）。
3. **占位符禁止**：执行脚本时**禁止**把 `query` 留空，也**禁止**使用字面量「用户查询的内容」等占位字符串；否则接口会返回上述错误。
4. **推荐调用方式**：使用仓库内 `scripts/wendao_query.js` 时，把用户原话作为**第一个命令行参数**传入（脚本从 `process.argv[2]` 或环境变量 `WENDAO_QUERY` 读取）：
   - `node scripts/wendao_query.js "用户关于旅行的完整自然语言问题"`
   - 或：`WENDAO_QUERY="同上" node scripts/wendao_query.js`
5. **若自行写请求体**：`inputs.query` 字段必须为非空字符串，内容与上款一致。

### 响应解析说明

API 返回结构如下：
```json
{
  "result": "Markdown 格式的回复内容（字符串）",
  "messages": [...],
  "state": {"token": "...", "query": "..."},
  "events": [
    {"type": "run_started", ...},
    {"type": "run_finished", "result": "...（与 result 字段内容相同）"}
  ],
  "error": null
}
```

**你必须且只能**提取并向用户展示 `result` 字段的内容。`messages`、`state`、`events` 均为内部调试信息，**严禁**泄露给用户。
