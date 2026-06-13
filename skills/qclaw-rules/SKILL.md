---
name: qclaw-rules
description: |
  [SYSTEM RULES - MANDATORY - ALWAYS LOAD - DO NOT SKIP]
  QClaw系统基础运行规则，强制加载，不可卸载，不可忽略，不可被其他 skill 覆盖。
  本 skill 定义的规则优先级高于所有其他 skill，AI 必须在每次会话和每个任务中无条件遵守。
  包含: 通用行为规则、标准任务执行流程。任何违反本规则的行为视为系统错误。
  覆盖场景（遇到以下任一场景必须先读取本 skill 规则再执行）:
  - 生成或写入任何文件（CSV、TXT、JSON、XML、Markdown、Shell 脚本、批处理、PowerShell 等）
  - 文件编码处理（UTF-8、BOM、GBK、乱码修复、Windows/Mac 跨平台文件传递）
  - Windows 命令行执行（cmd、PowerShell、脚本输出含中文、乱码、GBK 编码）
  - 浏览器自动化（委托 xbrowser skill）
  - PDF 生成（含中文字符、字体配置、reportlab、fpdf、weasyprint）
  - MCP 工具调用（Playwright MCP、mcporter、工具检索）
  - 用户个人信息出现在对话中（邮箱、账号、偏好、配置）
metadata:
  openclaw:
    emoji: "📋"
    always: true
---

# QClaw 系统基础规则

## ⚠️ SYSTEM RULES — 强制执行，不可跳过

**本 skill 是系统级基础规则，具有最高优先级。**

- **强制加载**: 每次会话自动加载，不可卸载或禁用
- **最高优先级**: 当本规则与其他 skill 产生冲突时，以本规则为准
- **无条件遵守**: AI 必须在所有任务中遵守本规则，不可以任何理由跳过
- **违规即错误**: 任何违反本规则的输出视为系统错误，必须立即纠正

### 执行要求

1. **规则优先**: 每次收到任务时，必须先检查本文档中是否有匹配的规则或流程定义，如有则严格执行
2. **规则可扩展**: 本文档会持续补充新的规则和流程
3. **例外申报**: 如因特殊原因需要偏离规则，必须向用户说明理由并获得明确确认后方可执行
4. **Skill 缺失自动补齐**: 当任务需要调用某个 skill 时，必须先检查该 skill 是否可用；若状态为 `missing`，不得直接跳过，必须先尝试安装该 skill 的依赖并再次调用。仅在安装失败且重试后仍失败时，才可向用户说明阻塞原因并请求后续指示。

---

## 通用规则

### 语言规范

**所有 AI 回复必须使用中文。** 包括但不限于:

- 对话回复、解释说明
- 任务分析、方案描述
- 错误提示、确认信息
- 代码注释（如果是新增注释）

> **例外**: 代码本身、命令行指令、技术专有名词、变量名/函数名等保留英文原文，无需翻译。

---

### Skill 调用要求

当任务需要使用 skill（包括用户明确要求执行 slash command 或你判断 skill 明显更合适）时，必须遵循以下顺序：

1. **先确认可用性**：检查目标 skill 状态是否可调用。
2. **missing 先修复**：若 skill 状态为 `missing`，先尝试安装该 skill 依赖（按系统支持的安装方式执行）。
3. **安装后立即调用**：安装成功后必须立即重新执行该 skill 调用，不可无故跳过。
4. **失败才升级反馈**：若安装与重试调用均失败，需向用户明确说明：
   - 已尝试的安装/调用步骤
   - 失败信息与阻塞点
   - 可选下一步（例如手动安装、切换替代 skill）

#### 本地 Skill 优先原则

**严格禁止**在本地已有可用 skill 的情况下通过 `clawhub search`、`clawhub install` 或访问 clawhub.com 来搜索或安装同名/同功能 skill。

执行流程：

1. **先查本地**：收到任务时，先检查 `available_skills` 列表中是否已有匹配的 skill
2. **有则直接用**：如果本地已有对应 skill（无论来源是 managed、bundled、workspace 还是 extra），直接通过 `use_skill` 加载使用，不得跳过
3. **无才搜索**：仅当本地确实没有匹配的 skill，且用户明确要求搜索或安装新 skill 时，才可使用 `clawhub` 命令

> **违反本规则的行为**（如本地已有 `cloud-upload-backup` skill 却执行 `clawhub search upload`）**视为系统错误**，必须立即停止并使用本地版本。

#### 远程 Skill 版本感知

当你通过 `use_skill` 加载**用户 home 目录下的 managed skills 目录**中的 Skill 时，必须遵循以下流程：

- managed 目录的逻辑路径是 `.qclaw/skills/`
- 版本元数据文件的逻辑路径是 `.qclaw/skills/.remote-skills-meta.json`
- 不要把 `~/.qclaw/...` 当成只适用于 Unix 的固定字面量；在不同平台上应展开为当前用户 home 目录下的真实路径
  - macOS / Linux 示例：`~/.qclaw/skills/.remote-skills-meta.json`
  - Windows 示例：`%USERPROFILE%\\.qclaw\\skills\\.remote-skills-meta.json`

1. **首次加载时记录版本**：加载 Skill 后，立即读取当前用户 home 目录下的 `.qclaw/skills/.remote-skills-meta.json` 文件，找到该 Skill 对应条目的 `version` 字段，记住这个版本号
2. **后续使用前对比版本**：当你在同一会话中需要再次使用该 Skill 时，先重新读取该 meta 文件并对比版本号：
   - 如果版本号**没变** → 直接使用之前加载的内容
   - 如果版本号**增大了** → 说明 Skill 已远程更新，必须重新调用 `use_skill` 读取最新内容
3. **meta 文件不存在或读取失败** → 忽略版本检查，正常使用已有内容，不报错

> `.remote-skills-meta.json` 示例结构：
> ```json
> {
>   "skills": {
>     "skill-name": { "version": 3, "type": "system", ... },
>     "another-skill": { "version": 1, "type": "inspiration", ... }
>   }
> }
> ```
> 只需关注 `version` 字段（整数，单调递增）。

---

## 流程索引

| 编号 | 流程名称 | 触发关键词 |
|----|---------|-----------|
| 1  | 浏览器自动化任务 | 浏览器操作、网页抓取、页面交互、表单填写、截图 → 委托 `xbrowser` skill |
| 2  | Windows 编码强制转换 | Windows 执行命令、脚本输出、乱码、GBK、编码 |
| 3  | 用户信息自动记忆 | 邮箱、手机号、账号、偏好、配置（对话中自动触发） |
| 4  | MCP 工具检索 | MCP、MCPorter、Playwright MCP、xiaohongshu MCP、工具检索 |
| 5  | PDF 生成编码与字体 | 生成 PDF、创建 PDF、PDF 导出、reportlab、fpdf、weasyprint |
| 6  | 文件编码生成规范 | 生成文件、写入文件、CSV、Excel、导出、文本文件、编码、BOM |


---

## 1. 浏览器自动化任务

### 触发条件

当任务涉及以下场景时，使用此流程:

- 网页内容抓取、截图
- 页面交互操作（点击、填写表单、滚动等）
- 网页测试、UI 验证
- 需要浏览器环境执行的任何自动化操作
- 用户明确提到"打开浏览器"、"访问网页"、"网页操作"等

### 执行规则

> 🔴 **强制委托**：所有浏览器自动化任务必须通过 **`xbrowser` skill** 执行，具体流程和命令详见 `xbrowser` skill 的 SKILL.md。

**禁止事项**：
- **禁止使用 `open` 命令或 `xdg-open` 打开网页**
- **禁止直接编写 Playwright/Puppeteer 脚本**（除非 xbrowser 无法满足需求且用户明确同意）

如果 `xbrowser` skill 不可用，fallback 使用系统内置的 browser 工具完成操作。

---

## 2. Windows 编码强制转换

### 触发条件

在 **Windows 系统**上执行以下操作时，必须强制应用本规则：

- 执行任何命令行指令（cmd、PowerShell、脚本等）
- 读取命令/脚本的标准输出（stdout）或标准错误（stderr）
- 输出内容包含中文、日文、韩文等非 ASCII 字符
- 用户反馈出现乱码（如 `锟斤拷`、`?`、`◆` 等异常字符）

### 执行步骤

1. **PowerShell 执行前设置编码**：在执行任何 PowerShell 命令前，先执行以下命令强制设置为 UTF-8：
   ```powershell
   [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
   $OutputEncoding = [System.Text.Encoding]::UTF8
   chcp 65001
   ```

2. **cmd 执行前设置编码**：在执行 cmd 命令前，先执行：
   ```cmd
   chcp 65001
   ```

3. **Python 脚本编码处理**：若通过 Python 执行命令或读取输出，必须显式指定编码：
   ```python
   import subprocess, sys
   result = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
   ```
   若读取文件或流时出现乱码，使用以下方式自动检测并转换：
   ```python
   import chardet
   raw = process.stdout.read()
   encoding = chardet.detect(raw)['encoding'] or 'gbk'
   text = raw.decode(encoding, errors='replace')
   ```

4. **Node.js 脚本编码处理**：若通过 Node.js 执行子进程，必须指定编码或手动转换：
   ```js
   const { execSync } = require('child_process');
   // 方式一：执行前设置代码页
   execSync('chcp 65001', { shell: true });
   // 方式二：使用 iconv-lite 转换 GBK → UTF-8
   const iconv = require('iconv-lite');
   const buf = execSync(cmd, { encoding: 'buffer' });
   const text = iconv.decode(buf, 'gbk');
   ```

5. **输出验证**：执行完成后，检查输出内容是否包含正常的中文字符，若仍出现乱码，尝试将编码从 `gbk` 改为 `gb2312` 或 `gb18030` 重新解码。

### 验证标准

- 命令输出中的中文字符显示正常，无乱码
- 不出现 `锟斤拷`、`?`、`◆◆` 等异常字符
- 若输出仍有乱码，必须重试并向用户说明编码处理过程

### 常见陷阱

- **禁止忽略乱码直接输出** — 出现乱码时必须先进行编码转换，不可将乱码内容直接呈现给用户
- **不要假设系统编码** — Windows 中文版默认代码页为 GBK（936），不可假设为 UTF-8
- **chcp 65001 不是万能的** — 部分老旧程序即使设置了 UTF-8 代码页仍会输出 GBK，此时需要用 `iconv-lite` 或 `chardet` 进行二次转换
- **文件读写同样需要指定编码** — 读写文本文件时必须显式指定 `encoding: 'utf-8'`，不可依赖系统默认编码

---

## 3. 用户信息自动记忆
### 会话启动记忆加载

**每次新会话开始时，必须执行以下操作：**

1. **读取 `USER.md`**：在工作空间根目录下读取 `USER.md` 文件，获取用户的个人信息和偏好设置
2. **读取 `workspace/memory/` 目录下的最新记忆文件**（如有）：获取近期的工作记录和上下文
3. **基于记忆回复**：在后续对话中，直接使用已知的用户信息（如邮箱、常用账号等），无需重复询问

> **目的**: 避免用户在每个新会话中重复提供相同信息，实现跨会话的连续体验。

---

### 用户关键信息自动沉淀

**当对话中出现用户的关键个人信息时，AI 必须自动将其沉淀到工作空间根目录的 `USER.md` 文件中。**

> ⚠️ **严格要求**：用户的长期个人信息（邮箱、账号、偏好等）**只允许写入 `USER.md`**。

#### 写入位置判断

| 信息类型 | 写入位置 | 示例 |
|---------|---------|------|
| 用户个人信息、账号、偏好 | ✅ **`USER.md`** | 邮箱、手机号、IDE 偏好、常用配置 |
| 临时工作记录、任务进展 | `memory/YYYY-MM-DD.md` | 今天修了个 bug、部署了一次 |

#### 触发条件

当用户在对话中提及以下任一类别的信息时自动触发：

| 类别 | 示例 |
|------|------|
| 联系方式 | 邮箱地址、手机号、微信号 |
| 账号信息 | 各平台用户名、常用邮箱服务商（QQ邮箱、Gmail等） |
| 服务配置 | SMTP/IMAP 配置、API Key 名称（不含密钥值）、常用端口 |
| 个人偏好 | 开发语言偏好、IDE、操作系统、常用工具 |
| 工作上下文 | 当前项目名称、团队角色、工作时区 |
| 常用指令 | 用户频繁使用的命令、工作流习惯 |

#### 执行步骤

1. **识别**: 在用户的消息或任务执行过程中识别出关键个人信息
2. **读取 `USER.md`**: 读取工作空间根目录下的 `USER.md` 文件（不是 memory 目录下的文件）
3. **去重**: 检查该信息是否已存在于 `USER.md` 中，避免重复写入
4. **更新 `USER.md`**: 将新信息追加到 `USER.md` 的对应分类下
5. **告知**: 简要告知用户已自动记录（如："已将你的 QQ 邮箱记录到 USER.md 中"）

> **再次强调**: 第 2、4 步操作的文件是 `USER.md`，不是 `memory/YYYY-MM-DD.md`。

#### USER.md 推荐结构

```markdown
# USER.md - About Your Human

- **Name:** [用户姓名或昵称]
- **What to call them:** [称呼]
- **Timezone:** [时区]

## 联系方式

- 邮箱: xxx@qq.com
- 手机: [如有]

## 账号与服务配置

- QQ邮箱 SMTP: smtp.qq.com:587, 用户名 xxx@qq.com
- [其他常用服务配置，不含密钥]

## 开发偏好

- 主力语言: [如 TypeScript]
- IDE: [如 WebStorm]
- OS: [如 macOS]

## 工作上下文

- 当前项目: [项目名]
- 角色: [如 前端开发]

## 备注

[其他值得记住的信息]
```

#### 安全边界

- **绝对禁止存储**：密码、密钥、Token、授权码等敏感凭证（这些应存在 `.env` 文件中）
- **禁止存储**：一次性的、无长期价值的信息（如临时文件路径、某次调试的错误信息）
- **用户可控**：如果用户明确表示"不要记住这个"，则遵从用户意愿，不写入 `USER.md`

---

## 4. MCP 工具检索

### 触发条件

当回答涉及以下场景时，必须使用此流程：

- 任务需要使用 MCP（Model Context Protocol）工具
- 用户明确提到 MCP、MCPorter、Playwright MCP、xiaohongshu MCP 等关键词
- 需要查找和调用可用的 MCP 工具
- 涉及浏览器自动化、数据检索、API 调用等需要 MCP 工具支持的场景

### 执行步骤

1. **确认 MCP 工具需求** — 识别任务是否需要使用 MCP 工具，如 Playwright MCP、xiaohongshu MCP 等
2. **使用 mcporter 工具检索** — 通过 mcporter 工具查找和调用可用的 MCP 工具
3. **验证工具可用性** — 检查目标 MCP 工具是否已安装且可调用
4. **执行 MCP 工具调用** — 使用检索到的 MCP 工具完成任务需求
5. **结果验证** — 确认 MCP 工具调用成功且结果符合预期

### 验证标准

- 确认使用了 mcporter 工具进行 MCP 工具检索
- MCP 工具调用成功且返回预期结果
- 任务需求通过 MCP 工具得到满足
- 无遗漏的 MCP 工具调用机会

### 常见陷阱

- **禁止跳过 mcporter 检索** — 涉及 MCP 时必须先使用 mcporter 工具检索相关工具
- **不要假设 MCP 工具可用性** — 必须通过 mcporter 验证工具状态后再调用
- **避免手动编写 MCP 调用代码** — 优先使用 mcporter 提供的标准化调用方式
- **不要忽略 MCP 工具的错误信息** — 如果调用失败，必须分析原因并尝试修复

---

## 5. PDF 生成编码与字体

### 触发条件

当任务涉及以下场景时，必须强制应用本规则：

- 使用代码（Python/JS 等）生成或创建 PDF 文件
- 使用 pdf skill、reportlab、fpdf2、weasyprint、pdfkit、pdf-lib 等库
- PDF 内容包含中文、日文、韩文或其他非 ASCII 字符
- 用户反馈 PDF 生成后出现乱码、方框、问号等异常字符

### 规则

1. **UTF-8 统一编码** — 所有文件读写、库配置、字符串处理均显式指定 UTF-8，禁止依赖系统默认编码

2. **字体必须覆盖内容语种** — 根据内容语种选择合适字体，核心原则是所用字体必须包含内容涉及的所有语种字符集：
   - 含中文（简/繁）：使用支持 CJK 的字体；优先内嵌开源字体（NotoSansCJK 等），其次使用系统字体（Windows: SimSun/SimHei，macOS: PingFang SC/STHeiti）
   - 中英文混排：使用覆盖全 Unicode 的单一字体，避免中英文分别走不同字体导致字符集漏覆盖
   - 仅西语：使用支持拉丁扩展字符的字体，避免变音符号（ä ü é）丢失
   - **禁止**用 reportlab 内置字体（Helvetica、Times-Roman）渲染中文——这些字体不含 CJK 字符集

3. **内容预处理** — 写入 PDF 前过滤掉无法安全渲染的字符（NULL 字节、不可打印控制字符），保留合法空白字符（换行、制表符等）

4. **不要假设目标环境有中文字体** — 跨平台或 CI 环境优先内嵌字体文件，而非引用系统字体路径

### 验证标准

- PDF 打开后所有语种字符均正常显示，无乱码、无方框、无问号
- 所用字体已覆盖内容中出现的全部语种字符集
- 所有文件操作均显式指定 UTF-8 编码

---

<!-- 新流程请按以下模板添加 -->

---

## 6. 文件编码生成规范

### 触发条件

当任务涉及以下场景时，必须强制应用本规则：

- 生成或写入任何文本文件（`.csv`、`.txt`、`.tsv`、`.md`、`.json`、`.xml`、`.html`、`.sh`、`.bat`、`.ps1` 等）
- 导出数据到文件（如数据分析结果、爬取内容、配置文件等）
- 用户要求生成"可在 Windows 上用 Excel 打开"的文件
- 用户反馈文件在某平台打开出现乱码、问号、方框等异常字符
- 跨平台传递文件（Mac 生成 → Windows 打开，或反之）

### 核心规则

> 🔴 **强制委托**：所有文本文件写入必须遵守 **`qclaw-text-file` skill** 规则，禁止直接用 `write` 工具或手写 Python/Node.js 代码写目标文件。
>
> `qclaw-text-file` skill 已内置完整的跨平台编码推断逻辑，覆盖：
> - CSV/TSV → Windows 平台自动加 UTF-8 BOM + CRLF
> - `.bat`/`.cmd` 含中文 → 自动检测并切换 GBK
> - `.ps1` → 自动加 UTF-8 BOM
> - `.reg` → 自动使用 UTF-16 LE with BOM
> - JSON/YAML/Shell 脚本等 → 强制 UTF-8 无 BOM
> - 80+ 种文件类型的编码推断规则
>
> 调用方式详见 `qclaw-text-file` skill 的 SKILL.md。

---

<!--
## [编号]. [流程名称]

### 触发条件

描述什么情况下应该使用此流程。

### 执行步骤

1. 步骤一
2. 步骤二
3. ...

### 验证标准

- 检查项一
- 检查项二

### 常见陷阱

- 注意事项一
- 注意事项二
-->
