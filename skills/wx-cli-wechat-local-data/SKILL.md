---
name: WeChat Skill (wx-cli-wechat-local-data)
description: 微信本地数据查询与导出 — WeChat local data CLI (messages, contacts, moments, favorites, images) with daemon architecture. Query and export from the command line without network calls.
triggers:
  - WeChat Skill
  - 微信本地数据
  - 微信消息查询
  - how do I query my local WeChat messages
  - search my WeChat chat history
  - export WeChat conversations
  - get unread WeChat messages from CLI
  - access WeChat data locally
  - find WeChat messages by keyword
  - list WeChat contacts and groups
  - extract WeChat images and attachments
---

# WeChat Skill — 微信本地数据 CLI

> Skill by [ara.so](https://ara.so) — Devtools Skills collection.
> 
> 也称作 `wx-cli` / WeChat Local Data CLI / 微信本地数据查询工具
>
> 📖 详细配置指南请参阅 [README.md](./README.md)

Query and export local WeChat data (messages, contacts, moments, favorites, public account articles) from the command line. Built in Rust with a daemon architecture that caches decrypted databases for millisecond-level responses.

## What it does

`wx-cli` provides a command-line interface to your local WeChat data without network calls. It:

- Scans WeChat's memory to extract database encryption keys
- Maintains a background daemon that caches decrypted databases (reuses cache if mtime unchanged)
- Queries messages, contacts, groups, moments (SNS), favorites, and public account articles
- Extracts and decodes image attachments (.dat files)
- Returns structured JSON with metadata about data freshness

**Key features:**

- Zero-dependency single binary
- Fully local (no data leaves your machine)
- AI-friendly JSON output with `meta` wrapper for freshness/source info
- Supports incremental queries (`new-messages` returns only messages since last check)

## Installation

**npm (recommended, cross-platform):**

```bash
npm install -g @jackwener/wx-cli
```

**macOS / Linux (curl):**

```bash
curl -fsSL https://raw.githubusercontent.com/jackwener/wx-cli/main/install.sh | bash
```

**Windows (PowerShell as Administrator):**

```powershell
irm https://raw.githubusercontent.com/jackwener/wx-cli/main/install.ps1 | iex
```

## Initial Setup

Keep WeChat running, then initialize (one-time):

### macOS

Ad-hoc signing is required to scan WeChat's memory:

```bash
# 1. Sign WeChat (once per WeChat update)
codesign --force --deep --sign - /Applications/WeChat.app

# 2. Reset TCC privacy records (required after re-signing)
for s in ScreenCapture Camera Microphone AppleEvents AddressBook \
         SystemPolicyDocumentsFolder SystemPolicyDownloadsFolder SystemPolicyDesktopFolder; do
  tccutil reset "$s" com.tencent.xinWeChat
done

# 3. Restart WeChat and wait for full login
killall WeChat && open /Applications/WeChat.app

# 4. Initialize wx-cli
sudo wx init
```

If `codesign` reports `signature in use`:

```bash
codesign --remove-signature "/Applications/WeChat.app/Contents/Frameworks/vlc_plugins/librtp_mpeg4_plugin.dylib"
codesign --force --deep --sign - /Applications/WeChat.app
```

### Linux

```bash
sudo wx init
```

### Windows

Run PowerShell as Administrator:

```powershell
wx init
```

**Verify installation:**

```bash
wx sessions
```

If you see recent sessions, setup is complete. The daemon starts automatically on first command.

## Core Commands

### Messages & Sessions

```bash
# Recent sessions (conversations)
wx sessions

# Unread sessions only
wx unread

# Filter unread (exclude official accounts and folded entries)
wx unread --filter private,group

# New messages since last check (incremental)
wx new-messages

# Chat history with a contact/group
wx history "张三"
wx history "张三" -n 2000                    # More messages
wx history "AI群" --since 2026-04-01 --until 2026-04-15

# Search across all messages
wx search "关键词"
wx search "关键词" -n 500                     # More results
wx search "会议" --in "工作群" --since 2026-01-01
```

**JSON output structure:**

```rust
// history, search, sessions, new-messages, stats, attachments
{
  "data": [...],
  "meta": {
    "status": "ok" | "possibly_stale" | "windowed",
    "unknown_shards": ["message_3.db"],  // If non-empty, run `wx init --force`
    "chat_latest_timestamp": "2026-05-16T12:34:56+08:00",
    "chat_latest_db": "message_2.db",
    "session_last_timestamp": "2026-05-16T14:20:00+08:00"
  }
}
```

**Message fields:**

```json
{
  "time": "2026-05-16 10:23:45",
  "timestamp": 1715832225,
  "sender": "张三",
  "content": "消息内容",
  "type": "text",
  "chat_type": "private",
  "is_self": false
}
```

- `chat_type`: `private` | `group` | `official_account` | `folded`
- `type`: `text` | `image` | `video` | `file` | `link` | `voice` | `system` | etc.

**Quoted messages:** History/search output shows quoted replies with original context:

```text
[引用] 当前回复
  ↳ 发送者: 被引用内容
```

### Contacts & Groups

```bash
# List contacts
wx contacts
wx contacts --query "李"       # Search by name

# List group members (prioritizes group nicknames)
wx members "AI交流群"
wx members "AI交流群" --json   # JSON with username/display/group_nickname/is_owner
```

**Member JSON structure:**

```json
{
  "username": "wxid_abc123",
  "display": "李四 (群昵称)",
  "contact_display": "李四",
  "group_nickname": "群昵称",
  "is_owner": false
}
```

### Moments (SNS)

Three separate commands for notifications vs. posts:

```bash
# Like/comment notifications (unread by default)
wx sns-notifications
wx sns-notifications --include-read -n 100

# Moments timeline (your feed)
wx sns-feed
wx sns-feed --user "张三" -n 100
wx sns-feed --since 2026-04-01

# Search moments content
wx sns-search "关键词"
wx sns-search "婚礼" --user "李四" --since 2023-01-01
```

**sns-notifications output:**

```json
{
  "type": "like" | "comment",
  "from_nickname": "张三",
  "content": "评论内容",
  "feed_preview": "原帖正文片段",
  "feed_author": "李四",
  "timestamp": 1715832225
}
```

**sns-feed / sns-search output:**

```json
{
  "author": "张三",
  "content": "朋友圈正文",
  "media": [
    {
      "url": "...",
      "thumb": "...",
      "key": "...",
      "token": "...",
      "md5": "...",
      "enc_idx": 0,
      "size": 123456
    }
  ],
  "media_count": 1,
  "location": "北京",
  "timestamp": 1715832225
}
```

### Public Account Articles

Official/subscription account articles are stored separately:

```bash
# Recent articles
wx biz-articles
wx biz-articles -n 200

# Filter by account name
wx biz-articles --account "返朴"

# Time range
wx biz-articles --since 2026-05-01 --until 2026-05-10

# Unread only (1 latest per account)
wx biz-articles --unread

# Extract URLs
wx biz-articles --json | jq '.[].url'
```

**Output fields:**

```json
{
  "account": "返朴",
  "account_username": "gh_abc123",
  "title": "文章标题",
  "url": "https://mp.weixin.qq.com/...",
  "digest": "摘要",
  "cover_url": "...",
  "time": "2026-05-16 10:00:00",
  "timestamp": 1715832000,
  "recv_time_str": "2026-05-16 10:01:23"
}
```

### Attachments (Images)

Image attachments are stored as `.dat` files that require decryption:

```bash
# 1. List image attachments in a conversation
wx attachments "张三"
wx attachments "AI群" --kind image -n 100
wx attachments "AI群" --since 2026-04-01 --until 2026-04-15

# 2. Extract a specific attachment by ID
wx extract <attachment_id> -o ~/Desktop/photo.jpg
wx extract <attachment_id> -o /tmp/x.jpg --overwrite
```

**attachments output:**

```json
{
  "attachment_id": "opaque-id-123",
  "kind": "image",
  "type": 3,
  "local_id": 456,
  "timestamp": 1715832225,
  "time": "2026-05-16 10:23:45",
  "sender": "张三"
}
```

**extract output:**

```json
{
  "md5": "abc123...",
  "dat_path": "/.../msg/attach/.../abc.dat",
  "dat_size": 123456,
  "output": "~/Desktop/photo.jpg",
  "output_size": 120000,
  "format": "jpg",
  "decoder": "v2"
}
```

Supported decoders:
- `legacy_xor`: Early single-byte XOR (no magic header)
- `v1_aes`: Fixed AES-128-ECB with hardcoded key
- `v2`: AES + XOR with platform-derived keys

### Favorites & Statistics

```bash
# All favorites
wx favorites
wx favorites --type image      # Filter by type: text/image/article/card/video
wx favorites --since 2026-01-01

# Conversation statistics
wx stats "AI群"                # Message counts by sender (top 10)
wx stats "AI群" --top 20       # More senders
```

### Export

```bash
# Export to text file
wx export "张三" -o chat.txt

# Export to JSON
wx export "AI群" -o chat.json --format json
wx export "AI群" -o chat.json --format json --since 2026-04-01
```

## Configuration

### Daemon Management

The daemon starts automatically on first command. Manual control:

```bash
# Check daemon status
wx status

# Stop daemon
wx stop

# Restart daemon
wx stop && wx sessions  # Any query command restarts it

# Force re-initialize (re-scan WeChat memory)
wx init --force
```

### Environment Variables

wx-cli reads configuration from standard WeChat data paths. No env vars required for normal operation.

**Logging:**

```bash
# Enable debug logging (not typically needed)
RUST_LOG=debug wx history "张三"
```

## Common Patterns

### Monitor new messages in a script

```bash
#!/bin/bash
while true; do
  wx new-messages --json | jq -r '.data[] | "\(.time) \(.sender): \(.content)"'
  sleep 60
done
```

### Export all conversations since date

```bash
for session in $(wx sessions --json | jq -r '.[].username'); do
  wx export "$session" -o "backup/${session}.json" --format json --since 2026-01-01
done
```

### Search for keywords and extract context

```bash
wx search "项目" --json | jq -r '.data[] | "\(.time) [\(.sender)] \(.content)"'
```

### Get unread count per conversation

```bash
wx unread --json | jq '.[] | "\(.unread_count)\t\(.remark)"'
```

### Extract all images from a date range

```bash
# 1. Get attachment IDs
wx attachments "旅行群" --since 2026-05-01 --json | jq -r '.data[].attachment_id' > ids.txt

# 2. Extract each
mkdir -p images
while read id; do
  wx extract "$id" -o "images/${id}.jpg" 2>/dev/null
done < ids.txt
```

### Check data freshness in automation

```bash
result=$(wx history "张三" --json)
status=$(echo "$result" | jq -r '.meta.status')

if [ "$status" != "ok" ]; then
  echo "Warning: Data may be stale. Unknown shards:"
  echo "$result" | jq '.meta.unknown_shards'
  echo "Run: wx init --force"
fi
```

## Troubleshooting

### macOS: "Operation not permitted"

```bash
# Re-sign WeChat
codesign --force --deep --sign - /Applications/WeChat.app

# Reset TCC and reinitialize
for s in ScreenCapture Camera Microphone AppleEvents; do
  tccutil reset "$s" com.tencent.xinWeChat
done
killall WeChat && open /Applications/WeChat.app
sudo wx init --force
```

### macOS: "WeChat 想访问其他 App 的数据" popups

This is a known side effect of re-signing. The popup occurs because macOS treats the re-signed WeChat as a different app accessing its old container. Click "Allow" to proceed. To avoid popups, you'd need to use official WeChat signature (which requires SSH-free local Terminal with Developer Tools TCC access).

### Windows: No decryption keys found

```bash
# Make sure WeChat is fully logged in
# Run as Administrator
wx init --force
```

### "unknown_shards" in meta output

WeChat may have created new `message_N.db` shards since initialization:

```bash
wx init --force
```

### Daemon not responding

```bash
wx stop
wx sessions  # Restarts daemon
```

### Empty results but WeChat has data

```bash
# Force refresh all caches
wx init --force

# Check daemon status
wx status
```

### Image extraction fails with "unsupported decoder"

On Linux, V2 image keys are not yet supported. Legacy XOR and V1 AES work. On macOS/Windows, ensure WeChat is running during `wx init`.

## Advanced Usage

### Custom limit for large queries

```bash
# Default limits are conservative to avoid overwhelming output
wx history "张三" -n 10000
wx search "keyword" -n 5000
wx sns-feed -n 500
```

### Filter messages by type

```bash
# Links, files, merged chat records, quoted messages
wx history "AI群" --type link --json

# Images only
wx history "AI群" --type image --json
```

### Include metadata in all outputs

```bash
# Human-readable warnings go to stderr
wx history "张三" 2>&1 | grep "WARNING"

# Machine-readable meta in JSON stdout
wx history "张三" --json | jq '.meta'

# Extended meta with per-shard details
wx history "张三" --with-meta --json | jq '.meta.per_shard_latest'
```

### Export with custom time windows

```bash
wx export "项目群" -o q1-2026.json --format json \
  --since 2026-01-01 --until 2026-03-31
```

## Integration with AI Agents

wx-cli is designed for AI agent consumption:

1. **Install via skills:**
   ```bash
   npx skills add jackwener/wx-cli
   ```

2. **Structured output:** All query commands return JSON with `{data, meta}` wrapper
3. **Freshness indicators:** `meta.status` tells agents if data may be stale
4. **Incremental queries:** `new-messages` returns only messages since last check
5. **Error handling:** Non-zero exit codes + stderr for errors; JSON always valid on stdout

Example agent prompt:

> "Check my WeChat for any messages from 李四 in the last week mentioning '合同'"

Agent execution:

```bash
wx search "合同" --in "李四" --since $(date -d '7 days ago' +%Y-%m-%d) --json
```

## Documentation

- GitHub: https://github.com/jackwener/wx-cli
- Installation: See `install.sh` / `install.ps1` in repo
- macOS Permission Guide: `docs/macos-permission-guide.md`

## License

Apache-2.0
