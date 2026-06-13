---
name: kimi-cli
description: 调用本地 Kimi CLI（kimi-for-coding 模型）执行编程、代码分析、代码生成等任务。当用户明确要求"用 Kimi"、"让 Kimi 处理"、"kimi 帮我"，或任务属于代码编写/调试/重构/技术分析类且适合交给 Kimi 处理时触发。
---

# Kimi CLI — 本地 Kimi 代码助手

> 调用本地已安装的 `kimi` CLI（版本 1.9.0），使用 `kimi-for-coding` 模型执行编程相关任务。

## 工具路径

```
C:/Users/29711/.local/bin/kimi.exe
```
PATH 中可直接使用 `kimi` 命令。

## 触发条件

以下任一情况触发本技能：
- 用户明确说"用 Kimi"、"让 Kimi"、"kimi 帮我"、"交给 kimi"
- 用户要求代码任务且偏好 Kimi 模型（代码生成、调试、重构、技术分析）
- 与当前上下文配合，需要将子任务委托给 Kimi 单独执行

## 调用方式

### 非交互单次输出（推荐）

```bash
kimi --print --final-message -p "你的任务描述"
```

### 指定工作目录

```bash
kimi --print --final-message -w "D:/your/project" -p "分析这个项目的主要结构"
```

### 继续上次会话

```bash
kimi --print --final-message --continue -p "继续刚才的任务"
```

### 指定模型

```bash
# 使用 kimi-for-coding（默认，适合代码任务）
kimi --print --final-message -m kimi-code/kimi-for-coding -p "任务"

# 使用 kimi-k2-thinking-turbo（适合复杂推理）
kimi --print --final-message -m kimi/kimi-k2-thinking-turbo -p "任务"
```

## 重要参数说明

| 参数 | 说明 |
|------|------|
| `--print` | 非交互模式，输出结果到 stdout |
| `--final-message` | 只输出最终回复，忽略中间步骤 |
| `-p / --prompt` | 用户指令文本 |
| `-w / --work-dir` | 设置工作目录（默认当前目录） |
| `--continue / -C` | 继续该工作目录的上一次会话 |
| `-S / --session` | 指定 session ID 恢复会话 |
| `-m / --model` | 指定模型 ID |

## 执行规则

1. **优先使用 `--print --final-message`** 获取简洁非交互输出
2. 代码任务默认使用 `kimi-code/kimi-for-coding` 模型
3. 涉及文件操作时，通过 `-w` 指定正确的工作目录
4. 执行结果直接展示给用户，必要时进行摘要整合
5. 如果任务复杂，可拆分为多步骤调用

## 示例调用

```bash
# 代码审查
kimi --print --final-message -p "审查以下代码的安全性和性能问题：$(cat main.py)"

# 生成代码
kimi --print --final-message -w "D:/myproject" -p "根据项目结构为 user.py 补充完整的 CRUD 函数"

# 调试分析
kimi --print --final-message -p "分析这个错误并给出修复方案：TypeError: 'NoneType' object is not subscriptable"
```
