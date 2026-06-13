---
name: imap-smtp-email
description: 通过 IMAP/SMTP 连接个人邮箱，支持完整邮件收发、抄送、附件、HTML、收件箱检索与附件下载；是当前邮件体系中唯一的个人邮箱主通道。
metadata:
  openclaw:
    emoji: "📧"
    requires:
      bins:
        - node
        - npm
---

# IMAP / SMTP Email（个人邮箱主 Skill）

## ⚠️ 强制首步（最高优先级，必读必执行）

**加载本 skill 后，无论任何情况，第一步必须立即调用 `get-token.sh` 获取凭证。** 不要检查 `.env`，不要读取任何配置文件，不要判断是否已配置——直接执行凭证获取脚本。脚本内部会自动从凭证服务拉取授权码、推断 IMAP/SMTP 服务器并写入 `.env`。

### 第 1 步：获取凭证（必须先执行）

如果用户指定了邮箱（如 `test@163.com`），从邮箱 `@` 后的域名推断 platform 参数：

| platform 参数 | 对应邮箱域名 |
|--------------|-------------|
| `163_mail` | 163.com, vip.163.com, 126.com, vip.126.com, 188.com, vip.188.com, yeah.net |
| `qq_mail` | qq.com, foxmail.com, vip.qq.com, exmail.qq.com |
| `gmail` | gmail.com |
| `outlook` | outlook.com, hotmail.com, live.com, live.cn |
| `sina_mail` | sina.com, sina.cn, vip.sina.com |
| `sohu_mail` | sohu.com |

然后调用：

- **macOS / Linux**：`bash '<SCRIPT_PATH>/get-token.sh' --platform '<平台名>'`
- **Windows**：`powershell -ExecutionPolicy Bypass -File '<SCRIPT_PATH>\get-token.ps1' -Platform '<平台名>'`

如果用户**未指定邮箱**，不传 `--platform` 参数，脚本会自动遍历所有平台找到第一个可用的：

- **macOS / Linux**：`bash '<SCRIPT_PATH>/get-token.sh'`

其中 `<SCRIPT_PATH>` 指本 skill（`imap-smtp-email`）的根目录。

脚本成功后会输出 JSON（含 `"success": true`、`"email": "xxx"`）并将凭证写入 `.env`。

### 第 2 步：执行邮件命令

凭证就绪后，通过 `resolve-account.cjs` 执行实际邮件操作：

```bash
node '<SCRIPT_PATH>/scripts/resolve-account.cjs' send \
  --account-email 'test@163.com' \
  --to 'recipient@example.com' \
  --subject 'Hello' \
  --body 'World'
```

```bash
node '<SCRIPT_PATH>/scripts/resolve-account.cjs' inbox-check \
  --account-email 'test@163.com'
```

#### 账号指定方式

支持两种方式指定使用哪个邮箱：

1. **精确邮箱地址**：`--account-email 'your@163.com'`
2. **平台别名**（用户只说了邮箱品牌时使用）：`--account-platform 'sina_mail'`

**中文别名映射表（LLM 必读）**：当用户消息中包含以下关键词但未给出精确邮箱地址时，使用 `--account-platform` 参数：

| 用户说法（关键词） | --account-platform 值 |
|-------------------|----------------------|
| 新浪邮箱、新浪、sina | `sina_mail` |
| 网易邮箱、163邮箱、163、126邮箱、netease | `163_mail` |
| QQ邮箱、QQ、foxmail、腾讯邮箱 | `qq_mail` |
| Gmail、谷歌邮箱、谷歌、google | `gmail` |
| Outlook、微软邮箱、微软、hotmail | `outlook` |
| 搜狐邮箱、搜狐、sohu | `sohu_mail` |

**示例**：用户说"用新浪邮箱帮我发个邮件"→

```bash
node '<SCRIPT_PATH>/scripts/resolve-account.cjs' send \
  --account-platform 'sina_mail' \
  --to 'recipient@example.com' \
  --subject 'Hello' \
  --body 'World'
```

> 优先级：`--account-email` > `--account-platform` > 自动选择

### 禁止事项（违反将导致任务失败）

- ❌ 禁止跳过第 1 步直接执行邮件命令
- ❌ 禁止手动读取或修改 `.env` 文件
- ❌ 禁止在获取凭证前做任何"配置检查"或"环境检查"
- ❌ 禁止告诉用户"需要先配置"或"需要授权"——凭证由脚本自动获取

---

> **定位**：这是唯一的个人邮箱主 skill。只要需求不再是"推送到我自己的邮箱做留存"，而是要像正常邮箱一样完整收发邮件，就应该走 `imap-smtp-email`。

## 1. 现在的职责

`imap-smtp-email` 负责所有**完整邮件能力**：

- 发给任意收件人
- `to` / `cc` / `bcc`
- 纯文本 / HTML
- 附件发送
- IMAP 收件、搜索、查看详情
- 下载附件
- 标记已读 / 未读
- 列出邮箱文件夹

> 当前邮件体系中，所有个人邮箱能力都统一收敛到本 skill，不再按邮箱厂商拆分入口。

## 2. 与平台公邮的边界

| 问题 | 平台公邮 | `imap-smtp-email` |
|------|----------|-------------------|
| 推送到自己的邮箱 | ✅ | ✅ |
| 发给别人 | ❌ | ✅ |
| 抄送 / 密送 | ❌ | ✅ |
| HTML | ❌ | ✅ |
| 附件 | ❌ | ✅ |
| 收件 / 搜索 / 下载附件 | ❌ | ✅ |
| 零配置 | ✅ | ❌ |

**判断口诀：**

- **只给自己做留存**：更适合平台公邮
- **像正常邮箱那样收发**：直接 `imap-smtp-email`

> 这里的关键不是"先检查平台公邮"，而是**先理解场景**：如果任务本质是结果留存，就选平台公邮；如果任务本质是完整邮件动作，就直接选本 skill。

## 3. 收敛后的能力组成

本 skill 统一承接了个人邮箱场景里仍然有效的能力与预设：

- 网易系邮箱 provider 预设
- QQ / Foxmail / 企业邮 provider 预设
- 统一的凭证自动刷新脚本（`get-token.sh` / `get-token.ps1`）

这意味着：

- `email-skill` 的个人邮箱分流目标只剩一个：`imap-smtp-email`
- 个人邮箱侧的脚本、配置和帮助信息都应围绕本 skill 维护

## 4. 支持的邮箱 Provider 预设

以下 provider 已内置到 `setup.sh` 配置向导中：

| Provider | IMAP Host | IMAP Port | SMTP Host | SMTP Port |
|----------|-----------|-----------|-----------|-----------|
| 163.com | imap.163.com | 993 | smtp.163.com | 465 |
| vip.163.com | imap.vip.163.com | 993 | smtp.vip.163.com | 465 |
| 126.com | imap.126.com | 993 | smtp.126.com | 465 |
| vip.126.com | imap.vip.126.com | 993 | smtp.vip.126.com | 465 |
| 188.com | imap.188.com | 993 | smtp.188.com | 465 |
| vip.188.com | imap.vip.188.com | 993 | smtp.vip.188.com | 465 |
| yeah.net | imap.yeah.net | 993 | smtp.yeah.net | 465 |
| gmail.com | imap.gmail.com | 993 | smtp.gmail.com | 587 |
| Outlook.com | outlook.office365.com | 993 | smtp-mail.outlook.com | 587 |
| qq.com | imap.qq.com | 993 | smtp.qq.com | 465 |
| foxmail.com | imap.qq.com | 993 | smtp.qq.com | 465 |
| yahoo.com | imap.mail.yahoo.com | 993 | smtp.mail.yahoo.com | 465 |
| sina.com | imap.sina.com | 993 | smtp.sina.com | 465 |
| sohu.com | imap.sohu.com | 993 | smtp.sohu.com | 465 |
| 139.com | imap.139.com | 993 | smtp.139.com | 465 |
| exmail.qq.com | imap.exmail.qq.com | 993 | smtp.exmail.qq.com | 465 |
| aliyun.com | imap.aliyun.com | 993 | smtp.aliyun.com | 465 |
| Custom | 自定义 | 自定义 | 自定义 | 自定义 |

> 对于 `587` 端口，`SMTP_SECURE=false`，走 STARTTLS。
> 对于 `465` 端口，`SMTP_SECURE=true`，走 SSL。

## 5. 凭证与配置（全自动）

入口脚本内部自动完成以下步骤，无需任何手动操作：

1. 调 4230 接口查询已绑定的所有个人邮箱
2. 根据 `--account-email` 参数或自动选择决定使用哪个邮箱
3. 自动刷新凭证并写入配置
4. 然后执行后续的 smtp / imap 命令

## 7. IMAP 命令

> `<SCRIPT_PATH>` 指本 skill（`imap-smtp-email`）的根目录。

### `inbox-check`

```bash
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' inbox-check \
  --account-email 'your@163.com' --limit 10 --mailbox INBOX --recent 2h
```

### `inbox-search`

```bash
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' inbox-search \
  --account-email 'your@163.com' --subject 发票 --recent 7d --limit 20
```

### `inbox-fetch`

```bash
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' inbox-fetch \
  --account-email 'your@163.com' 12345 --mailbox INBOX
```

### `inbox-download`

```bash
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' inbox-download \
  --account-email 'your@163.com' 12345 --dir "$HOME/Downloads"
```

### 其他 IMAP 命令

```bash
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' inbox-mark-read --account-email 'your@163.com' 12345
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' inbox-mark-unread --account-email 'your@163.com' 12345
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' inbox-list-mailboxes --account-email 'your@163.com'
```

## 8. SMTP 命令

### `send`

```bash
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' send \
  --account-email 'your@163.com' \
  --to partner@example.com \
  --subject "Hello" \
  --body "World"
```

### 常见示例

#### 发送 HTML 邮件

```bash
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' send \
  --account-email 'your@163.com' \
  --to recipient@example.com \
  --subject "周报" \
  --html \
  --body "<h1>Weekly Report</h1><p>详情见正文</p>"
```

#### 发送附件

```bash
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' send \
  --account-email 'your@163.com' \
  --to recipient@example.com \
  --subject "报告" \
  --body "请查收附件" \
  --attach /Users/you/Documents/report.pdf
```

#### 抄送 / 密送

```bash
bash '<SCRIPT_PATH>/scripts/unix/email_gateway.sh' send \
  --account-email 'your@163.com' \
  --to a@example.com \
  --cc b@example.com \
  --bcc c@example.com \
  --subject "项目同步" \
  --body "请查收"
```

## 9. 与其他 skill 的关系

- `email-skill`：统一入口，负责意图识别与路由分发
- `public-skill`：平台公邮，仅做"推送到自己邮箱"
- `imap-smtp-email`（本 skill）：完整个人邮箱能力

## 10. 调用规范

参见顶部「⚠️ 强制首步」段落。所有邮件操作必须且只能通过入口脚本执行。
