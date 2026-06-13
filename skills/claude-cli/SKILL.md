---
name: claude-cli
description: 调用本地 Claude Code CLI（claude 命令）执行通用 AI 任务、文件操作、代码分析等。当用户明确要求"用 Claude"、"让 Claude 处理"、"claude 帮我"，或需要利用 Claude 的工具调用能力（文件读写、搜索、执行命令）完成复杂自动化任务时触发。
---

# Claude CLI — 本地 Claude Code 助手

> 调用本地已安装的 `claude` CLI（Claude Code v2.1.90），支持工具调用、文件操作、搜索等能力。

## 工具路径

```
C:/Users/29711/AppData/Roaming/npm/claude.cmd
```
PATH 中可直接使用 `claude` 命令。

## 触发条件

以下任一情况触发本技能：
- 用户明确说"用 Claude"、"让 Claude"、"claude 帮我"、"交给 claude"
- 任务需要工具调用能力（文件读写、执行命令、搜索代码库）
- 需要委托 Claude 完成复杂多步骤自动化任务
- 需要与本地文件系统深度交互的任务

## 调用方式

### 非交互单次输出（推荐）

```bash
claude -p "你的任务描述"
```

### 指定工作目录

```bash
claude -p "分析项目结构" --add-dir "D:/your/project"
```

### 允许自动执行（危险操作需确认）

```bash
claude -p "任务" --permission-mode acceptEdits
```

### 流式 JSON 输出（结构化）

```bash
claude -p "任务" --output-format json
```

### 使用特定配置

```bash
claude -p "任务" --settings "C:/path/to/settings.json"
```

## 重要参数说明

| 参数 | 说明 |
|------|------|
| `-p / --print` | 非交互模式，输出结果后退出 |
| `--add-dir <path>` | 添加工作目录（可重复使用） |
| `--permission-mode` | 权限模式：`default`/`acceptEdits`/`dontAsk`/`auto` |
| `--output-format` | 输出格式：`text`（默认）/`json`/`stream-json` |
| `--append-system-prompt` | 附加系统提示 |
| `--max-budget-usd` | 最大 API 预算（USD） |
| `--model` | 指定模型（如 `claude-sonnet-4-6`） |

## 执行规则

1. **默认使用 `-p` 非交互模式**，适合管道和自动化
2. 文件操作任务通过 `--add-dir` 指定工作目录
3. 自动化批量任务建议使用 `--permission-mode acceptEdits`
4. 输出结果直接展示给用户，必要时整合摘要
5. 复杂任务可分步执行，利用 `--append-system-prompt` 注入上下文

## 当前配置信息

- **API Base URL**：`https://api.with7.cn`（自定义代理）
- **默认模型**：`claude-sonnet-4-6`
- **Skills 目录**：`C:/Users/29711/.claude/skills/`

## 示例调用

```bash
# 代码解释
claude -p "解释这段 Python 代码的逻辑"

# 文件分析（在项目目录下）
claude -p "找出所有未使用的导入" --add-dir "D:/myproject"

# 自动修复（允许编辑文件）
claude -p "修复所有 ESLint 错误" --permission-mode acceptEdits --add-dir "D:/myproject"

# 复杂研究任务
claude -p "分析 D:/myproject 的架构，生成 README.md" --permission-mode acceptEdits

# 结构化 JSON 输出
claude -p "列出项目中所有 API 接口" --output-format json
```

## 注意事项

- `--permission-mode acceptEdits` 会自动接受文件编辑，使用前确认用户已授权
- `--permission-mode dontAsk` 跳过所有权限确认，仅在完全信任的环境使用
- Claude Code 的 API Key 已通过 settings.json 配置，无需额外认证
