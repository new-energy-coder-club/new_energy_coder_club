---
name: aicodewith
description: 管理 AiCodeWith（api.with7.cn）模型配置。支持同步最新模型列表到 OpenClaw、查询可用模型、切换默认模型。当用户说"更新 ACW 模型"、"同步 AiCodeWith 模型"、"查看 with7 模型"、"切换默认模型到 xxx" 时触发。
metadata: {"openclaw": {"emoji": "🤖"}}
---

# AiCodeWith 模型管理 Skill

管理 `api.with7.cn` 的模型配置，自动同步到 `~/.qclaw/openclaw.json`。

## 配置文件

`scripts/config.json` 存储 API 信息（迁移时只需复制此文件）：

```json
{
  "base_url": "https://api.with7.cn/v1",
  "api_key": "sk-acw-YOUR_API_KEY_HERE",
  "provider_name": "aicodewith",
  "openclaw_config": "~/.qclaw/openclaw.json"
}
```

## 可用命令

### 1. 查看当前可用模型

```bash
python3 skills/aicodewith/scripts/list_models.py
python3 skills/aicodewith/scripts/list_models.py --json
python3 skills/aicodewith/scripts/list_models.py --filter claude
```

### 2. 同步最新模型到 OpenClaw（核心功能）

```bash
python3 skills/aicodewith/scripts/sync_models.py
python3 skills/aicodewith/scripts/sync_models.py --dry-run   # 预览变更，不写入
```

### 3. 切换默认模型

```bash
python3 skills/aicodewith/scripts/set_default.py aicodewith/claude-sonnet-4-6
python3 skills/aicodewith/scripts/set_default.py aicodewith/deepseek-v3.2
```

## 推理模型标识

以下模型自动标记 `"reasoning": true`（下划线前缀匹配）：

- `deepseek-r1*`、`kimi-k2-thinking*`
- `qwen3*-thinking*`、`qwq-*`

## 迁移说明

迁移到新机器时只需：
1. 复制 `~/.qclaw/skills/aicodewith/` 目录
2. 编辑 `scripts/config.json` 更新 API Key（如需）
3. 运行 `sync_models.py` 重新写入配置
