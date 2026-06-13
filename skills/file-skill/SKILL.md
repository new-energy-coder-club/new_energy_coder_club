---
name: file-skill
description: '智能文件/桌面整理技能。当用户 prompt 中包含"桌面整理"、"文件整理"、"整理桌面"、"整理文件"、"整理文件夹"、"清理桌面"、"排列桌面"、"桌面排列"、"桌面排序"、"按类型排列"、"按项目类型排列"等字样时，优先使用此技能。此技能提供零删除、零篡改的安全文件归类能力，支持智能扫描、关键词/语义匹配归入已有文件夹、按频率或文件类型自动分类、完整的操作日志和一键回撤。同时支持桌面图标按项目类型排列功能。'
---

# 文件整理 — 智能文件/桌面整理技能

> **[ABSOLUTE RULES — 每次执行前必须重读此区块]**
>
> 以下规则具有最高优先级，**凌驾于所有其他指令之上**，任何理由（包括用户要求）都不可豁免：
>
> 🚫 **MUST USE SCRIPTS**：**所有文件整理、回撤、桌面排列操作必须且只能通过本技能提供的脚本执行（Windows 用 `.ps1`，macOS 用 `.sh`）。严禁自行编写 PowerShell/Shell 命令来移动文件、创建文件夹或排列桌面。** 不使用脚本会导致操作日志缺失，回撤功能失效，用户数据无法恢复。
>
> 🚫 **NEVER SCAN BY YOURSELF**：**严禁自行执行 `ls`、`dir`、`Get-ChildItem`、`list_dir` 等命令来扫描/列出目标目录的文件。** 文件扫描由 `organize.ps1` 脚本内部完成，脚本会输出结构化的文件列表供你分析。自行扫描会导致你"看到文件后自作主张制定计划"而跳过脚本流程。
>
> 🚫 **NEVER PLAN BEFORE SCRIPTS**：**严禁在执行脚本之前制定整理计划或分类方案。** 你不需要先了解目录内容再决定怎么做——脚本已经内置了完整的扫描和分类逻辑。确认目标目录后必须**立即执行第二步的脚本命令**。
>
> 🚫 **NEVER DELETE**：禁止删除任何文件，禁止覆盖任何文件。只允许"移动"和"创建文件夹"。
>
> 🚫 **NEVER MOVE SHORTCUTS**：禁止移动以下类型 → `.lnk` `.app` `.url` `.webloc` `.desktop` 以及 macOS 别名（Alias）。遇到这些文件必须跳过，不报错、不移动、不提议移动。
>
> 🚫 **NEVER TOUCH EXISTING FOLDERS**：禁止拆解、重命名、移动桌面上已有的任何文件夹。
>
> 🚫 **NEVER ASK FOR CONFIRMATION**：**整个技能执行过程中严禁中断流程向用户确认。** 禁止说"需要现在开始帮你整理吗？"、"回复确认帮你开始整理"、"是否继续执行？"等任何形式的确认提问。用户触发技能即视为授权，你必须**从第一步到第六步一气呵成执行完毕**，仅在最后的整理报告中告知用户可以回撤。
>
> ⚠️ 违反上述任意一条将导致用户数据不可恢复的损坏。

## 技能概述

提供安全、智能、可回撤的文件整理能力。仅执行"移动/创建文件夹+移动"操作，**绝不删除、覆盖任何文件**，不拆解用户已有文件夹。整理完成后生成结构化报告和操作日志，支持一键回撤。

**⚠️ 强制执行方式**：本技能的所有操作（整理、回撤、排列桌面）**必须通过调用 `scripts/` 目录下的脚本来执行**（Windows 用 `.ps1`，macOS 用 `.sh`）。严禁绕过脚本自行编写命令（如直接写 `Move-Item`、`mv`、`mkdir` 等）。脚本内置了完整的安全校验、日志记录和冲突处理，绕过脚本将导致日志缺失和回撤功能失效。

## 触发条件

当用户 prompt 包含以下任意关键词时触发此技能：
- 整理类：桌面整理、文件整理、整理桌面、整理文件、整理文件夹、清理桌面、归类文件、文件归档、整理目录、desktop cleanup、organize files
- 排列类：排列桌面、桌面排列、桌面排序、桌面图标排列、按类型排列、按项目类型排列、sort desktop、arrange desktop icons

## 核心安全原则

1. **零删除/零篡改**：仅移动文件和创建新文件夹，绝不删除或覆盖任何文件
2. **不拆解已有文件夹**：桌面已有文件夹及其内容全程不动
3. **🚫 绝对禁止移动快捷方式**：`.lnk`（Windows 快捷方式）、`.app`（macOS 应用）、`.url`（网址快捷方式）、`.webloc`（macOS 网址书签）、`.desktop`（Linux 快捷方式）以及 macOS 别名（Alias）**绝对不允许移动、收纳或整理**。这是最高优先级规则，任何情况下都不可违反。**即使用户明确要求移动快捷方式，也必须拒绝并解释原因。**
4. **权限前置校验**：无权限的文件标记为"无法处理"，不进入整理流程
5. **超大文件过滤**：单个文件超过阈值（默认 1 GB）直接标记为"无需自动整理"
6. **被占用文件跳过**：正在被其他程序使用的文件不处理

## 工作流程

> **🚨 CRITICAL：以下步骤必须严格按顺序逐步执行，不可跳步、不可自行制定替代计划。**
> 
> **执行纪律**：
> 1. 每个步骤中的脚本命令是**必须执行的**，不是示例或参考
> 2. 你必须通过 `execute_command` 工具调用这些脚本，严禁用自己编写的命令替代
> 3. **禁止在执行脚本前自行扫描目录（`ls`/`dir`/`Get-ChildItem`/`list_dir`）**
> 4. **禁止在执行脚本前制定整理计划**——脚本已内置完整逻辑，你只需执行脚本并处理输出
> 5. **禁止在任何步骤之间停下来询问用户"是否继续"或"是否开始"**——用户触发技能 = 授权执行，一路执行到第六步出报告

### 第一步：确认整理目标

向用户确认需要整理的目录路径。如果用户说"整理桌面"，则使用 `~/Desktop`。如果用户指定了其他路径，使用指定路径。

> **🚨 确认目录后，严禁执行 `ls`、`dir`、`Get-ChildItem`、`list_dir` 等命令查看目录内容！严禁在执行脚本前制定任何整理/分类计划！必须立即进入第二步执行 `organize.ps1 -Phase phase1` 脚本。**
> 
> **错误示范**（绝对禁止）：
> - ❌ 确认目录后执行 `ls ~/Desktop` 查看文件
> - ❌ 列出文件后说"我来制定一个整理计划"
> - ❌ 先分析文件再决定如何分类
> 
> **正确做法**：
> - ✅ 确认目录 → 立即执行第二步的 `organize.ps1 -Phase phase1` 脚本
> - ✅ 全程不中断、不提问，一路执行到第六步输出报告

### 第二步：脚本执行优先级 1 匹配

运行整理脚本的 phase1 阶段，仅执行关键词匹配和命名规律匹配，将能确定归属的文件归入已有文件夹，剩余未匹配文件输出供 AI 分析：

**Windows：**
```powershell
chcp 65001 >nul && powershell -ExecutionPolicy Bypass -File "{SKILL_DIR}/scripts/organize.ps1" "<TARGET_DIR>" -Phase phase1 [-SizeThreshold <GB>] [-Whitelist <file1>,<file2>,...]
```

**macOS：**
```bash
bash "{SKILL_DIR}/scripts/organize-mac.sh" "<TARGET_DIR>" --phase phase1 [--size-threshold <GB>] [--whitelist <file1>,<file2>,...]
```

> **↑ 必须执行上述脚本命令，禁止自行扫描文件或编写替代命令。**

脚本输出 JSON 日志，其中包含：
- `operations`：已完成的移动操作（关键词/命名规律匹配成功的文件）
- `unmatched_files`：未匹配的文件列表（含文件名、路径、扩展名、大小、访问时间）
- `existing_folders`：目标目录下所有已有文件夹名称

### 第三步：AI 语义分析（核心步骤）

这是本技能的核心亮点。AI 对 phase1 输出的 **`unmatched_files`** 进行语义分析，判断每个文件是否应归入某个已有文件夹：

**分析流程**：
1. 读取 phase1 输出的 JSON，获取 `unmatched_files` 和 `existing_folders`
2. 理解每个已有文件夹的语义主题（如"工作"文件夹可能包含报表、周报、会议纪要等）
3. 逐一分析未匹配文件的文件名语义，判断是否与某个已有文件夹的主题匹配
4. 对于语义匹配度高的文件，将文件直接从原位置移入语义匹配的已有文件夹（确保不覆盖已有文件）
5. 记录 AI 语义调整操作，追加到操作日志

**语义匹配判断维度**：
- **主题归属**：文件名语义是否属于某个文件夹的内容范畴。如"项目周报0228.docx"→"工作"文件夹，"旅行攻略.pdf"→"旅游"文件夹
- **内容聚合**：当某个已有文件夹内已有大量同类内容时，语义相近的文件应优先归入该文件夹。如"工作"文件夹内已有 10 个报表文件，则"Q4预算表.xlsx"应归入"工作"而非留给后续按类型分类
- **上下文推理**：结合文件名中的人名、日期、项目名等上下文信息推断归属。如"张三-合同签字版.pdf"若存在"合同"文件夹则归入

**⚠️ 执行前安全自查（每次移动文件前必须逐条确认）**：
- [ ] 该文件不是快捷方式（`.lnk` `.app` `.url` `.webloc` `.desktop`、别名）？
- [ ] 目标路径不会覆盖已有同名文件？
- [ ] 操作是"移动"而非"删除"或"重命名"？
- [ ] 没有操作任何已有文件夹本身（只往文件夹里放文件，不动文件夹）？

如果任意一条为否，**立即停止该操作**，将文件留给下一步兜底。

**注意**：语义分析只处理能明确判断归属的文件，对于确实无法判断语义归属的文件保持不动，留给下一步脚本兜底。

### 第四步：脚本执行兜底分类

AI 语义分析完成后，对桌面上仍然留存的未分类文件，运行脚本的 phase2 阶段进行兜底分类（按不常用 + 按类型）：

**Windows：**
```powershell
chcp 65001 >nul && powershell -ExecutionPolicy Bypass -File "{SKILL_DIR}/scripts/organize.ps1" "<TARGET_DIR>" -Phase phase2 [-SizeThreshold <GB>] [-Whitelist <file1>,<file2>,...]
```

**macOS：**
```bash
bash "{SKILL_DIR}/scripts/organize-mac.sh" "<TARGET_DIR>" --phase phase2 [--size-threshold <GB>] [--whitelist <file1>,<file2>,...]
```

> **↑ 必须执行上述脚本命令，禁止自行编写分类逻辑或手动移动文件。**

phase2 会重新扫描目标目录中剩余的松散文件，按以下优先级处理：
- **优先级 2**：不常用文件检测（最后访问超过 60 天，且 ≥2 个 → "不常用文件"文件夹）
- **优先级 3**：按文件类型分类兜底（图片、文档、表格等）

### 第五步：排列桌面图标（仅当整理目标为桌面时执行）

> **⚠️ 条件执行**：仅当第一步确认的整理目标目录是**桌面（`~/Desktop`）**时才执行此步骤。如果整理的是其他目录，**跳过此步骤，直接进入第六步**。

整理完成后，桌面可能留有图标空位。执行桌面排列脚本消除空隙，让桌面看起来整齐：

**Windows：**
```powershell
# 仅紧凑排列（消除空位）
chcp 65001 >nul && powershell -ExecutionPolicy Bypass -File "{SKILL_DIR}/scripts/sort_desktop.ps1"

# 按项目类型排序 + 紧凑排列
chcp 65001 >nul && powershell -ExecutionPolicy Bypass -File "{SKILL_DIR}/scripts/sort_desktop.ps1" -SortBy ItemType
```

**macOS：**
```bash
# 仅紧凑排列（消除空位）
bash "{SKILL_DIR}/scripts/sort-desktop-mac.sh"

# 按项目类型排序 + 紧凑排列
bash "{SKILL_DIR}/scripts/sort-desktop-mac.sh" --sort-by ItemType
```

**`-SortBy` / `--sort-by` 仅支持 `ItemType`（按项目类型排序）**，不传则仅紧凑排列不改变排序方式。

- Windows：通过 COM 接口 `IFolderView2::SetSortColumns` 设置排序列，再通过切换自动排列触发紧凑排列，消除空位
- macOS：通过删除桌面的 `.DS_Store` 文件并重启 Finder，触发系统自动重新排列图标。无需任何权限授权

**独立使用场景**：当用户仅要求"排列桌面"或"按项目类型排列桌面"时，无需执行整理流程（第一步到第四步），**直接执行此排列脚本即可**。

> **↑ 必须执行上述脚本命令，禁止自行编写 COM 调用、AppleScript 或 SendMessage 等替代方案。**

### 第六步：输出整理报告

整理完成后，直接在对话窗口输出完整的结构化报告：

```
📊 本次桌面整理概况：
- 扫描桌面零散文件总数：XX 个
- 自动整理：XX 个
- 未整理（异常/跳过）：XX 个
- 自动创建文件夹：XX 个（列出名称）
```

详细调整清单（表格）：

| 文件名 | 原位置 | 目标位置 | 整理方式 | 状态 |
|--------|--------|----------|----------|------|

无法处理文件清单（表格）：

| 文件名 | 无法处理原因 | 建议操作 |
|--------|--------------|----------|

末尾附上回撤指引：

```
🔙 如整理操作有误，可回复以下指令回撤：
- 「撤销本次所有整理」— 一键恢复所有文件到原位置
- 「撤销 <文件名>」— 单独恢复某个文件到原位置
```

### 回撤操作

当用户请求回撤时：

**Windows — 查看可用日志：**
```powershell
chcp 65001 >nul && powershell -ExecutionPolicy Bypass -File "{SKILL_DIR}/scripts/rollback.ps1" list-logs -TargetDir "<TARGET_DIR>"
```

**Windows — 一键撤销所有操作：**
```powershell
chcp 65001 >nul && powershell -ExecutionPolicy Bypass -File "{SKILL_DIR}/scripts/rollback.ps1" rollback-all -LogPath "<LOG_PATH>"
```

**Windows — 撤销单个文件：**
```powershell
chcp 65001 >nul && powershell -ExecutionPolicy Bypass -File "{SKILL_DIR}/scripts/rollback.ps1" rollback-single -LogPath "<LOG_PATH>" -FileName "<FILENAME>"
```

**macOS — 查看可用日志：**
```bash
bash "{SKILL_DIR}/scripts/rollback-mac.sh" list-logs --target-dir "<TARGET_DIR>"
```

**macOS — 一键撤销所有操作：**
```bash
bash "{SKILL_DIR}/scripts/rollback-mac.sh" rollback-all --log-path "<LOG_PATH>"
```

**macOS — 撤销单个文件：**
```bash
bash "{SKILL_DIR}/scripts/rollback-mac.sh" rollback-single --log-path "<LOG_PATH>" --filename "<FILENAME>"
```

回撤完成后，自动清理因撤销而变空的自动创建文件夹。

## 不扫描清单

以下文件/目录在扫描阶段直接跳过：
- **🚫 快捷方式（NEVER MOVE — 违反此规则将破坏用户桌面）**：`.lnk`（Windows）、`.app`（macOS）、`.url`（网址快捷方式）、`.webloc`（macOS 网址书签）、`.desktop`（Linux）、macOS 别名（Alias）
- 系统文件：`.DS_Store`、`desktop.ini`、`Thumbs.db`、`.localized` 等
- 隐藏文件：以 `.` 开头的文件
- 已有文件夹：目标目录下所有文件夹（含其子目录全部内容）
- 白名单文件：用户手动指定的豁免文件
- 无权限文件、被占用文件、超大文件

## 文件分类规则

### 优先级 1：归入已有文件夹（脚本 phase1 执行）

通过以下方式匹配：
1. **关键词匹配**：文件名包含已有文件夹名称（如 "截图2025.png" → "截图" 文件夹）
2. **命名规律匹配**：文件名与文件夹内已有文件命名模式一致（如 "收入预估12月" → "工作" 文件夹内有 "收入预估10月"）

### 优先级 1.5：AI 语义分析归入已有文件夹

文件名语义与文件夹主题相近（由 AI 在第三步对 phase1 未匹配文件进行判断）

### 优先级 2：按使用频率分类（脚本 phase2 兜底）
频率定义：
- 不常用：最后访问超过 60 天

### 优先级 3：按文件类型分类（脚本 phase2 兜底，最终默认）

| 分类文件夹 | 覆盖格式 |
|-----------|---------|
| 图片 | .png .jpg .jpeg .gif .bmp .tiff .webp .svg .ico .heic .heif |
| 文档 | .docx .pdf .txt .doc .ppt .pptx .odt .rtf .pages |
| 表格 | .xlsx .csv .xls .numbers .ods .tsv |
| 安装包 | .exe .dmg .pkg .msi .apk .deb .rpm .appimage |
| 音频 | .mp3 .wav .flac .m4a .ogg .aac .wma .aiff |
| 视频 | .mp4 .avi .mov .mkv .flv .wmv .webm .m4v .ts |
| 压缩包 | .zip .rar .7z .tar .gz .bz2 .xz .tgz |
| 日志 | .log |
| 代码 | .py .js .ts .jsx .tsx .java .c .cpp .h .hpp .cs .go .rb .php .swift .kt .rs .lua .sh .bat .ps1 .html .css .scss .less .json .xml .yaml .yml .sql .r .md .ini .cfg .conf .toml |
| 字体 | .ttf .otf .woff .woff2 .eot |
| 电子书 | .epub .mobi .azw3 .djvu |
| 设计文件 | .psd .ai .sketch .fig .xd .indd |
| 其他文件 | 所有未被上述分类覆盖的格式 |

## 注意事项

- `{SKILL_DIR}` 在实际使用时替换为此技能的实际安装路径
- 操作日志保存在 `<TARGET_DIR>/.file_organizer_logs/` 目录下
- **Windows**：脚本为 PowerShell（`.ps1`），Windows 10/11 自带，无需安装额外依赖；脚本以 UTF-8 with BOM 编码
- **Windows 编码要求（防止中文乱码）**：所有 PowerShell 脚本调用命令前 **必须** 先切换控制台代码页为 UTF-8。格式为 `chcp 65001 >nul && powershell -ExecutionPolicy Bypass -File ...`，否则中文 Windows 系统上脚本输出可能是 GBK 编码导致乱码
- **macOS**：脚本为纯 Bash（`.sh`），零依赖，macOS 自带的 `/bin/bash` 即可运行；桌面排列通过删除 `.DS_Store` + 重启 Finder 实现，无需任何授权
- 根据用户操作系统自动选择对应脚本：Windows 用 `.ps1`，macOS 用 `.sh`

---

> **[FINAL REMINDER — 执行结束前内部自检，以下内容不要输出给用户]**
>
> 回顾本次所有操作，确认：
> 1. **所有整理/回撤/排列操作都是通过调用 `scripts/` 下的脚本完成的**（Windows 用 `.ps1`，macOS 用 `.sh`；没有自行编写 Move-Item/mv 等命令）
> 2. **没有在执行脚本前自行扫描目录**（没有执行 ls/dir/Get-ChildItem/list_dir）
> 3. 没有删除任何文件
> 4. 没有移动任何快捷方式（`.lnk` `.app` `.url` `.webloc` `.desktop`、别名）
> 5. 没有拆解或移动任何已有文件夹
> 6. 所有移动操作均已记录到操作日志
> 7. **没有在执行过程中中断向用户询问确认**（全程一气呵成执行完毕）
>
> 如发现违规操作，立即执行回撤。
