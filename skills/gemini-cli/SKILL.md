---
name: gemini-cli
description: 调用本地 Gemini CLI（gemini 命令，Google Gemini 模型）执行 AI 任务。当用户明确要求"用 Gemini"、"让 Gemini 处理"、"gemini 帮我"，或需要 Google Gemini 模型能力时触发。
---

# Gemini CLI — 本地 Google Gemini 助手

> 调用本地已安装的 `gemini` CLI（v0.36.0，`@google/gemini-cli`），使用 Google Gemini 模型执行任务。

## 工具路径

```
C:/Users/29711/AppData/Roaming/npm/gemini.cmd
```
PATH 中可直接使用 `gemini` 命令。

## 触发条件

以下任一情况触发本技能：
- 用户明确说"用 Gemini"、"让 Gemini"、"gemini 帮我"、"交给 Gemini"
- 需要 Google Gemini 模型的多模态能力（图像理解、长上下文）
- 与 Claude/Kimi 对比验证结果时

## 调用方式

### 非交互单次输出（推荐）

```bash
gemini -p "你的任务描述"
```

### 全自动模式（YOLO，跳过所有确认）

```bash
gemini -y -p "任务"
# 等价于
gemini --approval-mode yolo -p "任务"
```

### 自动接受编辑

```bash
gemini --approval-mode auto_edit -p "任务"
```

### 指定工作目录

```bash
gemini -p "分析项目" --include-directories "D:/your/project"
```

### 继续上次会话

```bash
gemini --resume latest -p "继续任务"
```

### 指定模型

```bash
gemini -m gemini-2.5-pro -p "任务"
gemini -m gemini-2.0-flash -p "任务"
```

### JSON 结构化输出

```bash
gemini -p "任务" --output-format json
```

## 重要参数说明

| 参数 | 说明 |
|------|------|
| `-p / --prompt` | 非交互模式，执行后退出 |
| `-y / --yolo` | 全自动，跳过所有操作确认 |
| `--approval-mode` | `default`/`auto_edit`/`yolo`/`plan` |
| `-m / --model` | 指定模型 ID |
| `--include-directories` | 附加工作目录 |
| `--resume latest` | 恢复最近会话 |
| `-o / --output-format` | `text`/`json`/`stream-json` |

## 执行规则

1. **默认使用 `-p` 非交互模式**获取输出
2. 自动化任务加 `-y` 跳过确认
3. 涉及文件时通过 `--include-directories` 指定���径
4. 认证已通过 `~/.gemini/settings.json` 配置（gemini-api-key 模式），无需额外登录

## 示例调用

```bash
# 通用问答
gemini -p "解释 Transformer 架构的注意力机制"

# 代码分析（全自动）
gemini -y -p "分析 D:/myproject 的代码质量" --include-directories "D:/myproject"

# 多模态（图片分析）
gemini -p "描述这张图片的内容：$(base64 image.png)"

# 与 Claude 交叉验证
gemini -p "验证以下方案是否合理：..."
```
