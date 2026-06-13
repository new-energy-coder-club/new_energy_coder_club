---
name: aippt
description: "当用户明确要求使用 AI 智能设计生成 PPT 演示文稿时使用本技能（智绘高迪/AIPPT）。本技能调用远程 Design Agent API，根据文字描述自动生成专业 PPT 演示文稿，支持指定模板和自定义模型。当用户说'AI生成PPT'、'智绘PPT'、'自动生成演示文稿'、'帮我做个PPT'时触发。注意：本技能仅用于生成全新的 PPT，不用于读取、解析或编辑已有的 .pptx 文件——编辑已有文件请使用 pptx 技能。"
---

# AIPPT Skill — AI 智能 PPT 生成

通过智绘高迪 Design Agent API，根据用户的文字描述自动生成专业 PPT。

## 使用方式

> **Windows 用户**：所有 `bash` 命令请替换为对应的 `powershell -ExecutionPolicy Bypass -File` 版本，详见下方双版本示例。
> Windows 下使用 `python` 而非 `python3`。

### ⚠️ 调用前必须输出提示（MANDATORY）

**在执行脚本之前**，必须先向用户输出以下温馨提示：

```markdown
> 💡 **温馨提示**
> PPT 后台生成过程会持续消耗积分；如需终止任务，请点击下方链接进入智绘高迪平台操作。每张PPT平均消耗约0.5积分。
```

### 生成 PPT

**macOS / Linux：**

```bash
# 用法 — 只需 prompt
PROMPT="制作一个关于人工智能发展趋势的商业演示" bash __SKILL_DIR__/scripts/generate.sh
```

**Windows (PowerShell)：**

```powershell
# 用法 — 只需 prompt
$env:PROMPT="制作一个关于人工智能发展趋势的商业演示"; chcp 65001 >nul; powershell -ExecutionPolicy Bypass -File "__SKILL_DIR__/scripts/generate.ps1"
```

### 参数说明

| 环境变量 | 必填 | 说明 |
|----------|------|------|
| `PROMPT` | ✅ | PPT 内容描述，越详细越好 |

### 输出格式

脚本调用 Gateway 代理，Gateway 等待智绘 API 返回 `started` 事件后立即返回 JSON 结果：

```
📝 开始生成 PPT...
🚀 任务已启动，PPT 正在后台生成中

✅ PPT 生成任务已提交！

结果：
{
  "projectId": "69def187a7e1519b00d4708e",
  "workspaceUrl": "https://goatdee.qq.com/ppt/69def187a7e1519b00d4708e",
  "message": "PPT 任务已启动，正在后台生成中。你可以通过以下链接查看和编辑：..."
}

📊 编辑地址: https://goatdee.qq.com/ppt/69def187a7e1519b00d4708e
```

### 结果展示

将生成结果以 Markdown 格式展示给用户：

```markdown
✅ **PPT 生成任务已提交！**

PPT 正在后台生成中，预计需要 5-15 分钟。

📊 **在线编辑地址**: [点击打开智绘高迪](https://goatdee.qq.com/ppt/{projectId})

你可以点击链接查看生成进度，完成后直接在编辑器中修改。如需终止任务，也请在该页面中操作。
```

## 工作原理

1. Skill 脚本发送 POST 请求到 Auth Gateway 的 `/proxy/aippt/agent/run`
2. Gateway 注入模型凭证，转发到智绘高迪 Design Agent API（SSE 协议）
3. Gateway 等待上游返回 `started` 事件，提取 `projectId` 拼接编辑地址
4. Gateway 立即返回 JSON 结果给脚本，**不等待 PPT 生成完成**
5. PPT 在后台异步生成，用户通过编辑地址查看进度和结果

## ⚠️ 编码要求（MANDATORY）

**所有传递给接口的数据必须确保是 UTF-8 编码。** 这是强制要求，违反将导致服务端收到乱码。

- `PROMPT` 环境变量中的中文内容必须是 UTF-8 编码
- Windows 下必须在脚本执行前通过 `chcp 65001` 切换控制台代码页为 UTF-8
- HTTP 请求 body 必须以 UTF-8 编码发送，Content-Type 必须声明 `charset=utf-8`
- **禁止**使用系统默认编码（如 GBK/GB2312）传递任何包含非 ASCII 字符的数据

## ⚠️ 关于页数的严格规则（MANDATORY）

**除非用户在描述中明确指定了页数（如"生成10页PPT"、"做一个5页的演示"），否则绝对不要在 PROMPT 中自行添加、编造或暗示任何页数相关的内容。**

- ❌ 错误做法：用户说"帮我做个关于AI的PPT"，你在 PROMPT 里写"生成一个15页的AI主题PPT"
- ✅ 正确做法：用户说"帮我做个关于AI的PPT"，PROMPT 直接写"制作一个关于AI的演示文稿"，不提及页数
- ✅ 正确做法：用户说"帮我做一个8页的AI PPT"，PROMPT 写"制作一个8页的关于AI的演示文稿"

页数由智绘高迪平台根据内容自动决定，不需要你来指定。擅自添加页数要求可能导致生成效果不符合预期。

## 注意事项

1. 该 skill 调用远程 API，需要网络连接
2. Gateway 只等待 `started` 事件（通常几秒），不会因 PPT 生成耗时而超时
3. PPT 生成过程在后台进行，可能需要 5-15 分钟
4. 如果用户需要**编辑已有的 .pptx 文件**，请使用 `pptx` skill 而非本 skill
5. 如果 API 返回错误，检查网络连接并提示用户稍后重试

## 依赖

| 依赖 | macOS / Linux | Windows |
|------|--------------|---------|
| HTTP 请求 | `curl`（系统自带） | PowerShell `Invoke-RestMethod`（内置） |
| JSON 解析 | `python3`（系统自带） | PowerShell `ConvertFrom-Json`（内置） |
