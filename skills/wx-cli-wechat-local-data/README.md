# WeChat Skill — 微信本地数据 CLI

> **也称作**: `wx-cli` · WeChat Local Data CLI · 微信本地数据查询工具
>
> **Skill Slug**: `wx-cli-wechat-local-data`
>
> **来源**: [aradotso/devtools-skills](https://github.com/aradotso/devtools-skills) · 原始工具: [jackwener/wx-cli](https://github.com/jackwener/wx-cli)

---

## 目录

- [概述](#概述)
- [前置条件](#前置条件)
- [安装 wx-cli](#安装-wx-cli)
- [初始化配置](#初始化配置)
- [守护进程管理](#守护进程管理)
- [环境变量](#环境变量)
- [命令速查](#命令速查)
- [AI Agent 集成](#ai-agent-集成)
- [安全与隐私](#安全与隐私)
- [故障排除](#故障排除)
- [参考链接](#参考链接)

---

## 概述

WeChat Skill 提供了一套命令行接口，可在**完全离线**的环境下查询和导出本地微信数据。底层使用 **Rust** 编写，采用**守护进程（daemon）架构**缓存解密后的数据库，实现毫秒级查询响应。

### 核心能力

| 功能 | 命令 | 说明 |
|------|------|------|
| 会话列表 | `wx sessions` | 最近联系人/群聊 |
| 未读消息 | `wx unread` | 未读会话及消息数 |
| 聊天记录 | `wx history` | 指定会话的聊天历史 |
| 全文搜索 | `wx search` | 跨所有会话关键词搜索 |
| 增量消息 | `wx new-messages` | 自上次检查以来的新消息 |
| 联系人 | `wx contacts` | 联系人列表及搜索 |
| 群成员 | `wx members` | 群成员及群昵称 |
| 朋友圈通知 | `wx sns-notifications` | 点赞/评论通知 |
| 朋友圈动态 | `wx sns-feed` | 朋友圈时间线 |
| 朋友圈搜索 | `wx sns-search` | 搜索朋友圈内容 |
| 公众号文章 | `wx biz-articles` | 订阅号文章列表 |
| 图片附件 | `wx attachments` / `wx extract` | 列出和解码图片 |
| 收藏夹 | `wx favorites` | 收藏内容查询 |
| 统计 | `wx stats` | 会话消息统计 |
| 导出 | `wx export` | 导出为文本/JSON |

### 架构特点

- **零依赖**: 单一二进制文件，无需额外运行时
- **完全本地**: 数据不离开本机，无网络请求
- **AI 友好**: 所有输出均为结构化 JSON（`{data, meta}` 包装）
- **增量查询**: `new-messages` 仅返回自上次检查后的新消息
- **数据新鲜度**: `meta.status` 指示数据是否可能过时

---

## 前置条件

### 所有平台

- **微信** 必须已安装并处于**登录状态**（运行中）
- `wx-cli` 需要从微信进程内存中提取数据库解密密钥

### 平台特定要求

| 平台 | 要求 |
|------|------|
| **macOS** | 需要对微信 App 进行 ad-hoc 签名，关闭 SIP 或授权辅助功能权限 |
| **Linux** | 需要 root 权限执行 `wx init`（读取进程内存） |
| **Windows** | 需要**管理员权限**运行 PowerShell/终端 |

### 微信版本兼容性

- 微信 **3.9.x** 及以上（Windows/macOS）
- 微信 **4.x** 及以上（Linux）
- 旧版本可能无法解密部分数据库分片

---

## 安装 wx-cli

### 方式一：npm（推荐，全平台）

```bash
npm install -g @jackwener/wx-cli
```

安装后验证：

```bash
wx --version
# 或
npx @jackwener/wx-cli --version
```

### 方式二：macOS / Linux（curl 安装脚本）

```bash
curl -fsSL https://raw.githubusercontent.com/jackwener/wx-cli/main/install.sh | bash
```

脚本会自动：
1. 检测系统架构（x86_64 / arm64）
2. 下载对应二进制文件
3. 安装到 `/usr/local/bin/wx`

### 方式三：Windows（PowerShell 安装脚本）

以**管理员身份**运行 PowerShell：

```powershell
irm https://raw.githubusercontent.com/jackwener/wx-cli/main/install.ps1 | iex
```

### 方式四：手动下载

从 [GitHub Releases](https://github.com/jackwener/wx-cli/releases) 下载对应平台的二进制文件：

| 平台 | 文件 |
|------|------|
| macOS (Apple Silicon) | `wx-cli-aarch64-apple-darwin.tar.gz` |
| macOS (Intel) | `wx-cli-x86_64-apple-darwin.tar.gz` |
| Linux (x86_64) | `wx-cli-x86_64-unknown-linux-gnu.tar.gz` |
| Linux (ARM64) | `wx-cli-aarch64-unknown-linux-gnu.tar.gz` |
| Windows (x86_64) | `wx-cli-x86_64-pc-windows-msvc.zip` |

解压后放入 PATH 中的目录即可。

---

## 初始化配置

初始化是**一次性操作**，`wx-cli` 会扫描微信进程内存提取解密密钥并缓存。

### macOS 初始化（最复杂）

#### 第一步：签名微信

macOS 要求对微信 App 进行 ad-hoc 签名才能读取其内存：

```bash
# 移除可能冲突的插件签名
codesign --remove-signature \
  "/Applications/WeChat.app/Contents/Frameworks/vlc_plugins/librtp_mpeg4_plugin.dylib" 2>/dev/null

# Ad-hoc 签名（每次微信更新后需要重新执行）
codesign --force --deep --sign - /Applications/WeChat.app
```

> ⚠️ 如果报 `signature in use`，先执行 `codesign --remove-signature` 再重试。

#### 第二步：重置 TCC 隐私记录

重新签名后需要重置 TCC（Transparency, Consent, and Control）权限：

```bash
for s in ScreenCapture Camera Microphone AppleEvents AddressBook \
         SystemPolicyDocumentsFolder SystemPolicyDownloadsFolder SystemPolicyDesktopFolder; do
  tccutil reset "$s" com.tencent.xinWeChat
done
```

#### 第三步：重启微信并初始化

```bash
# 重启微信
killall WeChat && open /Applications/WeChat.app

# 等待微信完全登录后执行
sudo wx init
```

#### 第四步：验证

```bash
wx sessions
```

如果看到最近的会话列表，说明初始化成功。

### Linux 初始化

```bash
sudo wx init
```

> 需要 root 权限以访问微信进程内存。

### Windows 初始化

以**管理员身份**运行 PowerShell 或命令提示符：

```powershell
# 确保微信已登录
wx init
```

### 重新初始化

当遇到以下情况时需要重新初始化：
- 微信版本更新后
- `meta.status` 返回 `possibly_stale`
- `meta.unknown_shards` 非空

```bash
wx init --force
```

---

## 守护进程管理

`wx-cli` 使用后台守护进程缓存解密后的数据库连接。守护进程在首次执行查询命令时**自动启动**。

### 基本命令

```bash
# 检查守护进程状态
wx status

# 输出示例:
# Daemon: running (pid: 12345)
# Cache: valid (last init: 2026-06-09 10:00:00)
# Connected sessions: 12

# 手动停止守护进程
wx stop

# 重启守护进程（执行任意查询命令即可自动重启）
wx stop && wx sessions
```

### 守护进程生命周期

```
┌──────────────┐    首次查询     ┌──────────────┐
│  守护进程关闭  │ ───────────→  │  守护进程运行  │
└──────────────┘                └──────┬───────┘
       ↑                               │
       │         wx stop               │ 空闲（缓存命中）
       │  ◄────────────────────────────  │
       │                               │
       └───────────────────────────────┘
            微信退出 / 系统关机
```

### 缓存策略

- 守护进程缓存解密后的数据库连接
- 如果数据库文件的 `mtime`（修改时间）未变，复用缓存
- 微信写入新消息后，守护进程自动检测并刷新
- 微信版本更新导致密钥变化时，缓存自动失效

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `RUST_LOG` | 日志级别 | (无，正常模式) |

### 调试模式

```bash
# 启用调试日志输出
RUST_LOG=debug wx history "张三"

# 仅输出特定模块日志
RUST_LOG=wx_cli::decrypt=debug wx init --force
```

### 微信数据路径

`wx-cli` 自动检测微信数据路径，无需手动配置：

| 平台 | 默认路径 |
|------|----------|
| **Windows** | `%USERPROFILE%\Documents\WeChat Files\` |
| **macOS** | `~/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/` |
| **Linux** | `~/.config/WeChat/` 或 `~/.wine/` |

如果微信安装在非标准路径，可通过符号链接或环境变量 `WECHAT_DATA_DIR`（部分版本支持）指向正确位置。

---

## 命令速查

> 完整命令参考请参阅 [SKILL.md](./SKILL.md)

### 消息与会话

```bash
wx sessions                        # 最近会话列表
wx unread                          # 未读会话
wx unread --filter private,group   # 仅私聊和群聊未读
wx history "联系人" -n 500         # 最近500条消息
wx history "群名" --since 2026-06-01 --until 2026-06-09
wx search "关键词" -n 200          # 全局搜索
wx new-messages                    # 增量新消息
```

### 联系人与群组

```bash
wx contacts                        # 所有联系人
wx contacts --query "李"           # 按姓名搜索
wx members "群名"                  # 群成员列表
wx members "群名" --json           # JSON格式
```

### 朋友圈

```bash
wx sns-notifications               # 点赞/评论通知
wx sns-feed -n 100                 # 朋友圈动态
wx sns-feed --user "张三"          # 特定用户动态
wx sns-search "关键词"             # 搜索朋友圈
```

### 图片与附件

```bash
wx attachments "联系人"            # 列出图片附件
wx attachments "群名" --kind image --since 2026-06-01
wx extract <attachment_id> -o ~/Desktop/photo.jpg
```

### 公众号文章

```bash
wx biz-articles                    # 最近文章
wx biz-articles --account "返朴"   # 按账号筛选
wx biz-articles --unread           # 未读文章
```

### 收藏与统计

```bash
wx favorites                       # 收藏列表
wx favorites --type image          # 按类型筛选
wx stats "群名"                    # 发言统计 Top 10
wx stats "群名" --top 30           # Top 30
```

### 导出

```bash
wx export "联系人" -o chat.txt                    # 导出为文本
wx export "群名" -o chat.json --format json        # 导出为JSON
wx export "群名" -o q2.json --format json \
  --since 2026-04-01 --until 2026-06-30           # 按时间范围
```

---

## AI Agent 集成

### Claude Code（当前环境）

WeChat Skill 已作为全局 Skill 安装，当你向 Claude Code 提出微信数据相关问题时，Skill 会自动匹配触发：

```
用户: "帮我查一下张三最近给我发了什么消息"
Claude: [自动调用 wx-cli] → wx history "张三" --json
```

**Skill 安装路径**: `C:\Users\29711\.claude\skills\wx-cli-wechat-local-data\`

**触发关键词**（自动匹配）：
- 微信本地数据
- 微信消息查询
- search my WeChat chat history
- export WeChat conversations
- find WeChat messages by keyword
- list WeChat contacts
- extract WeChat images
- etc.

### QClaw / OpenClaw

如需在 QClaw 中启用此 Skill，将 `wx-cli-wechat-local-data` 添加到对应 agent 的 `skills` 列表中：

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "skills": [
          "wx-cli-wechat-local-data"
        ]
      }
    ]
  }
}
```

### 脚本集成

#### 监控新消息并通知

```bash
#!/bin/bash
# monitor_wechat.sh — 监控微信新消息

LAST_CHECK=$(date +%s)

while true; do
  RESULT=$(wx new-messages --json 2>/dev/null)

  if [ -n "$RESULT" ]; then
    COUNT=$(echo "$RESULT" | jq '.data | length')
    if [ "$COUNT" -gt 0 ]; then
      echo "[$(date '+%H:%M:%S')] $COUNT 条新消息"
      echo "$RESULT" | jq -r '.data[] | "  [\(.sender)] \(.content)"'
    fi
  fi

  sleep 60
done
```

#### 每日聊天摘要

```bash
#!/bin/bash
# daily_summary.sh — 生成每日微信活动摘要

TODAY=$(date +%Y-%m-%d)
echo "# 微信活动摘要 — $TODAY"
echo ""

echo "## 未读消息"
wx unread --json | jq -r '.[] | "- **\(.remark)** (\(.unread_count)条)"'

echo ""
echo "## 今日活跃会话"
wx sessions --json | jq -r '.[] | select(.latest_timestamp != null) | "- \(.remark): \(.latest_msg_preview)"'

echo ""
echo "## 朋友圈动态"
wx sns-feed --since "$TODAY" --json | jq -r '.data[] | "- **\(.author)**: \(.content)"'
```

#### 备份所有聊天记录

```bash
#!/bin/bash
# backup_wechat.sh — 备份所有微信聊天记录

BACKUP_DIR="./wechat-backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

wx sessions --json | jq -r '.[].username' | while read -r username; do
  DISPLAY=$(wx sessions --json | jq -r ".[] | select(.username==\"$username\") | .remark")
  SAFE_NAME=$(echo "$DISPLAY" | sed 's/[^a-zA-Z0-9一-鿿_-]/_/g')

  echo "导出: $DISPLAY → ${SAFE_NAME}.json"
  wx export "$username" -o "${BACKUP_DIR}/${SAFE_NAME}.json" --format json 2>/dev/null
done

echo ""
echo "备份完成: $BACKUP_DIR"
echo "文件数: $(ls "$BACKUP_DIR" | wc -l)"
```

---

## 安全与隐私

### 数据完全本地

- `wx-cli` **不会发起任何网络请求**（安装和更新除外）
- 所有微信数据均在本地读取和处理
- 解密密钥仅存在于守护进程内存中，不写入磁盘

### 风险提示

| 风险 | 等级 | 说明 |
|------|------|------|
| 进程内存读取 | ⚠️ 中 | `wx init` 需要读取微信进程内存，macOS 需要 ad-hoc 签名 |
| 管理员权限 | ⚠️ 中 | Windows 需管理员权限，Linux 需 root 权限 |
| 数据库缓存 | 🟡 低 | 缓存仅存于守护进程内存中，进程结束后释放 |
| 导出文件 | 🟡 低 | 导出的聊天记录文件由用户自行保管 |

### 建议

1. **不要**在不信任的多用户环境中运行 wx-cli
2. **导出文件**包含完整的聊天内容，妥善保管
3. **定期清理**不再需要的导出文件
4. 在企业环境中使用前请确认安全合规要求

---

## 故障排除

### macOS 常见问题

#### "Operation not permitted"

```bash
# 1. 重新签名微信
codesign --force --deep --sign - /Applications/WeChat.app

# 2. 重置 TCC 权限
for s in ScreenCapture Camera Microphone AppleEvents; do
  tccutil reset "$s" com.tencent.xinWeChat
done

# 3. 重启微信并重新初始化
killall WeChat && open /Applications/WeChat.app
sudo wx init --force
```

#### "WeChat 想访问其他 App 的数据" 弹窗

这是重新签名后的已知副作用。macOS 将重签名的微信视为不同应用。点击 **"允许"** 继续。若想避免弹窗，需要使用微信官方签名。

#### codesign: signature in use

```bash
# 先移除冲突的动态库签名
codesign --remove-signature \
  "/Applications/WeChat.app/Contents/Frameworks/vlc_plugins/librtp_mpeg4_plugin.dylib"

# 再签名
codesign --force --deep --sign - /Applications/WeChat.app
```

### Windows 常见问题

#### 找不到解密密钥

```powershell
# 1. 确认微信已完全登录（不是登录界面）
# 2. 以管理员身份重新初始化
wx init --force

# 3. 检查微信是否在标准路径
dir "$env:USERPROFILE\Documents\WeChat Files"
```

#### "Access Denied" 错误

- 确保以**管理员身份**运行终端
- 关闭杀毒软件的实时内存扫描（部分杀软会阻止进程内存读取）

### Linux 常见问题

#### "Permission denied" 初始化失败

```bash
# 必须使用 root 权限
sudo wx init

# 如果仍然失败，检查 ptrace 权限
sudo sysctl kernel.yama.ptrace_scope=0
wx init --force
```

#### 图片解码不支持

Linux 上 V2 图片密钥尚未完全支持。Legacy XOR 和 V1 AES 模式可用。

### 通用问题

#### meta.unknown_shards 非空

微信创建了新的 `message_N.db` 分片：

```bash
wx init --force
```

#### 守护进程无响应

```bash
# 手动停止并重启
wx stop
wx sessions  # 任意查询命令都会重启守护进程
```

#### 查询结果为空但微信有数据

```bash
# 强制刷新所有缓存
wx init --force

# 检查守护进程状态
wx status
```

#### JSON 输出乱码（Windows）

确保终端编码为 UTF-8：

```powershell
chcp 65001
# 或在 PowerShell 中设置
[Console]::OutputEncoding = [Text.Encoding]::UTF8
```

---

## 参考链接

| 资源 | 链接 |
|------|------|
| wx-cli 源码 (GitHub) | https://github.com/jackwener/wx-cli |
| Devtools Skills 合集 | https://github.com/aradotso/devtools-skills |
| npm 包 | https://www.npmjs.com/package/@jackwener/wx-cli |
| NEC Skill 分支 | https://github.com/new-energy-coder-club/new_energy_coder_club/tree/Skill |
| SKILL.md（命令完整参考） | [./SKILL.md](./SKILL.md) |

---

## 许可证

Apache-2.0 © [ara.so](https://ara.so) & [wx-cli contributors](https://github.com/jackwener/wx-cli)
