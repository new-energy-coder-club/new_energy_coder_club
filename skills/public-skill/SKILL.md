---
name: public-skill
description: "平台公邮：用于将天气、日报、报告、提醒等内容推送到用户自己的邮箱，零配置完成消息留存"
version: "2.0"
trigger_keywords:
  - 公邮
  - 平台邮件
  - 邮件推送
  - 推送邮件
  - 日报推送
  - 天气推送
  - 报告推送
  - 提醒推送
  - 通知推送
  - 绑定邮箱
  - 邮箱绑定
  - 消息留存
  - 推送到邮箱
exclude_when:
  - 用户需要发送给第三方收件人
  - 用户需要附件、抄送、密送、HTML
  - 用户需要收件、检索、下载附件
  - 通常应通过 email-skill 统一入口调用，而非直接调用 public-skill
---

# Public Skill（平台公邮）

> **定位**：平台公邮通道，用于把内容推送到**用户自己的邮箱**。
>
> **推荐方式**：只有在明确只想操作平台公邮时，才直接使用本 skill。

## 1. 能力边界

### 支持能力

| 能力 | 状态 |
|------|------|
| 查询绑定邮箱（`query-bindmail`） | ✅ |
| 检查绑定状态（`bind-check`） | ✅ |
| 发送绑定验证码（`bind-send-code`） | ✅ |
| 完成邮箱绑定（`bind-verify`） | ✅ |
| 发送纯文本邮件到自己的邮箱 | ✅ |

### 不支持能力

| 能力 | 说明 |
|------|------|
| 发给第三方收件人（`--to`） | ❌ 仅支持发送到自己的邮箱 |
| 抄送 / 密送（`--cc` / `--bcc`） | ❌ |
| 附件（`--attach`） | ❌ |
| HTML 邮件（`--html` / `--html-file`） | ❌ 仅支持纯文本 |
| 自定义发件人（`--from`） | ❌ |
| 收件 / 检索 / 下载附件 | ❌ |

## 2. 推荐流程：自动获取绑定邮箱 → 直接发信

进入 public-skill 后，**第一步必须先调用 `query-bindmail` 命令查询用户已绑定的邮箱**，再根据结果决定后续操作。

### 步骤一：查询绑定邮箱（query-bindmail）

```bash
bash <SCRIPT_PATH>/scripts/unix/email_gateway.sh query-bindmail
```

该命令会调用 `/data/4227/forward` 接口，返回结果如下：

**成功（用户已绑定邮箱）：**
```json
{
  "success": true,
  "email": "user@qq.com",
  "message": "已检测到平台公邮绑定邮箱"
}
```

**失败（未绑定或网关异常）：**
```json
{
  "success": false,
  "error_code": 3,
  "message": "当前未检测到已绑定的平台公邮邮箱"
}
```

### 步骤二：根据结果决定后续操作

- 若 `success` 为 `true` → 拿到 `email` 字段，直接用该邮箱调用 `send` 发信
- 若 `success` 为 `false` → 引导用户走手动绑定流程（见第 3 节）

### 步骤三：发送邮件

拿到绑定邮箱后，使用 `--email` 参数传入发信：

```bash
bash <SCRIPT_PATH>/scripts/unix/email_gateway.sh send \
  --email 'user@qq.com' \
  --subject '今日日报' \
  --body '这是今天的日报内容'
```

也可以通过文件读取主题和正文：

```bash
bash <SCRIPT_PATH>/scripts/unix/email_gateway.sh send \
  --email 'user@qq.com' \
  --subject-file '/tmp/subject.txt' \
  --body-file '/tmp/report.txt'
```

### 完整流程图

```
用户请求发送邮件
       │
       ▼
  调用 query-bindmail
       │
       ▼
  返回 4227 接口结果
       │
       ├── success=true，拿到 email ──► send --email <email> ... ──► 完成 ✅
       │
       └── success=false
              │
              └── 引导用户走绑定流程（第 3 节）
```

## 3. 手动绑定流程（仅在 4227 接口无法获取绑定邮箱时使用）

当 4227 接口未返回绑定邮箱时，需要用户手动完成以下 3 步：

### 步骤一：检查绑定状态

```bash
bash <SCRIPT_PATH>/scripts/unix/email_gateway.sh bind-check \
  --email 'you@example.com'
```

### 步骤二：发送验证码

```bash
bash <SCRIPT_PATH>/scripts/unix/email_gateway.sh bind-send-code \
  --email 'you@example.com'
```

### 步骤三：校验验证码

```bash
bash <SCRIPT_PATH>/scripts/unix/email_gateway.sh bind-verify \
  --email 'you@example.com' \
  --code '123456'
```

### 绑定说明

- 必须严格按 `bind-check` → `bind-send-code` → `bind-verify` 顺序执行
- 绑定成功后，无需重复绑定
- `send` 会在发送前自动做绑定检查；若未绑定，会返回引导信息

## 4. send 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--email <email>` | 推荐 | 用户自己的邮箱地址；**推荐先通过 `query-bindmail` 获取绑定邮箱后传入**。`send` 内部也会尝试自动获取，但建议显式传入以确保明确 |
| `--subject <text>` | 二选一 | 主题文本 |
| `--subject-file <path>` | 二选一 | 从文件读取主题 |
| `--body <text>` | 二选一 | 正文文本 |
| `--body-file <path>` | 二选一 | 从文件读取正文 |
| `--content_type text` | 否 | 仅支持 `text` |

### 明确不支持的参数

以下参数传入后会直接报错，并提示改走个人邮箱通道：

- `--to`
- `--cc`
- `--bcc`
- `--attach`
- `--from`
- `--html`
- `--html-file`
- `--content_type html`

## 5. 命令列表

| 命令 | 说明 |
|------|------|
| `query-bindmail` | 查询用户已绑定的平台公邮邮箱（调用 4227 接口），**推荐在发信前先调用** |
| `bind-check` | 检查邮箱绑定状态 |
| `bind-send-code` | 发送绑定验证码 |
| `bind-verify` | 完成邮箱绑定 |
| `send` | 给自己的邮箱发送纯文本邮件 |
| `capabilities` | 查看本 skill 能力 |
| `help` | 查看帮助 |

## 6. 错误处理建议

| 错误 | 处理方式 |
|------|----------|
| 未绑定平台公邮 | 走绑定流程 |
| 传了不支持的参数 | 改用 `email-skill send --provider personal` |
| 平台额度不足 | 建议改用 `email-skill send --provider auto`，由系统回退到个人邮箱 |
| 网关通信异常 | 报告错误并稍后重试 |

## 7. 安全规则

1. **发送邮件失败后禁止自动重试**
2. **不要输出 Token、验证码、账号凭证等敏感信息**
3. **平台公邮只负责推送到自己的邮箱，不要拿它模拟通用 SMTP 发信**

## 8. 与 `email-skill` 的关系

- `email-skill` 是统一入口
- `public-skill` 是“结果推送到自己邮箱”场景下的平台公邮下游通道
- 架构上，平台公邮与个人邮箱是并行路径；通常由模型先根据场景决定是否选择 `public-skill`
- 只有在调用方使用 `email-skill --provider auto` 且参数满足公邮条件时，路由器才会自动尝试 `public-skill`
- 当平台额度不足或通道异常时，由 `email-skill` 自动回退到 `imap-smtp-email`
