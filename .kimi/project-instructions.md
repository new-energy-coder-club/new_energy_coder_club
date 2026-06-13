# HXC ESP A Board — Kimi CLI 项目配置

> Kimi CLI 快速调用配置，用于代码生成、调试、分析等编程任务

## 环境要求

- Kimi CLI ≥ 1.9.0（已安装：`C:/Users/29711/.local/bin/kimi.exe`）
- 或 `npx kimi-cli`（无需安装）

## 快速调用

```bash
# 单次代码任务
kimi --print --final-message -w "D:/Project_env/new_energy_coder_club" -p "你的任务"

# 使用 kimi-for-coding 模型（推荐）
kimi --print --final-message -m kimi-code/kimi-for-coding -w "." -p "分析 projects/embedded/ 下的代码结构"

# 使用 kimi-k2-thinking-turbo（复杂推理）
kimi --print --final-message -m kimi/kimi-k2-thinking-turbo -w "." -p "复杂任务描述"
```

## 常用场景

### 代码审查

```bash
kimi --print --final-message -w "." -p "审查 projects/embedded/ 下 C++ 代码的内存安全和并发问题"
```

### 固件分析

```bash
kimi --print --final-message -w "." -p "分析 ESP32_platformio_temple_project 的 main.cpp，找出潜在的栈溢出和中断冲突"
```

### 文档生成

```bash
kimi --print --final-message -w "." -p "为 HXC_A_Usage_Guide.md 生成英文翻译版本"
```

### 技能辅助

```bash
kimi --print --final-message -w "." -p "根据 skills/lark-base/ 的 SKILL.md，写一段创建多维表格并添加字段的示例"
```

## 可用模型

| 模型 ID | 用途 | 特点 |
|---------|------|------|
| `kimi-code/kimi-for-coding` | 代码任务（默认） | 编程优化，速度快 |
| `kimi/kimi-k2-thinking-turbo` | 复杂推理 | 深度思考，适合架构设计 |
| `kimi/kimi-k2-turbo` | 通用任务 | 平衡速度与质量 |

## 工作目录约定

- 项目根目录：`D:/Project_env/new_energy_coder_club`
- Kimi CLI 通过 `-w` 参数指定工作目录，影响文件读写和上下文
- 会话自动关联到工作目录，支持 `--continue` 续接

## 与 Claude Code 协作

| 任务类型 | 推荐工具 | 原因 |
|----------|---------|------|
| 嵌入式 C++ 代码生成 | Kimi CLI | kimi-for-coding 专长 |
| 飞书文档/表格操作 | Claude Code (lark-* skills) | Skill 生态 |
| 项目结构分析 | 两者皆可 | 按需选择 |
| 多步骤自动化 | Claude Code | 工具调用能力 |

## 🖥️ Kimi Code IDE（桌面版）

Kimi Desktop 是 Moonshot AI 的桌面 IDE，安装在：
```
C:/Users/29711/AppData/Local/Programs/kimi-desktop/Kimi.exe
```

**项目工作区注册：** 在 Kimi Code IDE 中打开本目录后，会自动注册到 `~/.kimi/kimi.json` 的 `work_dirs` 列表中，之后 CLI 的 `--continue` 可续接 IDE 中的会话。
