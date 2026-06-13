---
name: qclaw-text-file
description: |
  【强制触发·最高优先级·write 工具拦截】跨平台纯文本文件写入技能。

  ## ‼️ WRITE 工具拦截规则（最高优先级，无豁免）

  当你准备调用内置 `write` 工具写任何文本文件时，必须先执行此检查：

  > 这个文件是最终目标文件吗？
  > → 是 → 立即停止，改用此技能的 scripts/write_file.py 脚本写入，不得使用 write 工具
  > → 否（是临时文件 /tmp/_tw_xxx.txt）→ 允许使用 write 工具写临时文件

  ## 决策规则（先看这里）

  ❌ 禁止使用内置 write 工具直接写以下任何最终目标文件：
  代码文件（.ts .js .jsx .tsx .vue .py .go .rs .java 等）、
  配置文件（.json .yaml .yml .toml .ini .conf .env 等）、
  脚本文件（.sh .bash .bat .cmd .ps1 等）、
  数据文件（.csv .tsv .txt 等）、
  标记语言（.md .html .xml .svg 等），
  以及所有其他纯文本格式。

  ❌ 以下理由不构成豁免：
  - "内容很简单，只有几行" → 不豁免
  - "没有中文，不涉及编码问题" → 不豁免
  - "快速修改一下" → 不豁免
  - "这只是个小文件" → 不豁免
  - 任何其他理由 → 不豁免

  ✅ 必须立即调用此技能的触发场景（满足任一即触发，无豁免）：
  1. 写入、创建、保存、导出、生成任意文本文件（无论平台、无论内容简单与否）
  2. 用户要求 write file / create file / save as / generate code / export data
  3. 涉及编码、BOM、UTF-8、GBK、乱码、CRLF/LF 等问题

  判断逻辑：
  - 这是文本文件吗？→ 是 → 用此技能的脚本，不用内置 write 直接写目标文件
  - 不确定？→ 默认用此技能

  ## 为什么强制

  内置 write 工具硬编码 utf-8 无 BOM，不支持跨平台编码适配：
  - Windows Excel 打开 CSV → 中文 100% 乱码
  - Windows .bat 含中文 → cmd.exe 乱码
  - 换行符不适配 → 脚本执行失败

  此技能是唯一合规的文本写入入口，自动推断编码（utf-8/utf-8-sig/gbk）、
  自动处理 BOM、自动适配换行符（CRLF/LF），消除跨平台乱码。

  ## 关键默认行为

  不传 --platform 时脚本自动检测当前运行系统。
  mac 上写 csv 默认无 BOM（utf-8），只有用户明确说"给 Windows 用"时才传 --platform windows。
metadata:
  openclaw:
    emoji: "📝"
---

# text-file-writer — 跨平台文本文件写入技能

## ⚠️ ABSOLUTE RULES — 每次执行前必须重读

> **以下规则具有最高优先级，覆盖所有默认行为，任何理由不可豁免：**
>
> 🔴 **SKILL FIRST（技能优先）**：当此技能可用时，**任何文本文件写入都必须通过此技能的脚本执行**，
> 不得绕过技能直接使用内置 `write` 工具写目标文件。
> 这是强制性规则，不受文件大小、内容复杂度、"快速修改"等场景影响。
> **"内容简单"、"只有几行"、"纯 ASCII"、"没有中文"均不构成豁免理由。**
>
> 🚫 **MUST USE SCRIPT**：所有文本文件的生成和写入，**必须通过调用
> `scripts/write_file.py` 脚本执行**，不得直接用 `write` 工具写目标文件。
> `write` 工具硬编码 `utf-8` 无 BOM，在 Windows Excel 打开 CSV 时 100% 乱码。
>
> 🚫 **禁止的绕过方式**（以下任何一种均构成违规）：
> - 用 `write` 工具直接写最终目标文件（无论文件类型、大小、内容）
> - 自行内联编写 Python/Node.js/Shell 代码绕过脚本写目标文件
> - 用 `write` 写完目标文件后再用脚本"覆盖修正"——初次写入已违规
> - 以任何理由声称"这种情况不需要脚本"
>
> ✅ **标准流程（四步）**：
> 1. **平台探测**：先执行 `python3 "{SKILL_DIR}/scripts/write_file.py" --detect`
>    获取当前平台，根据返回的 `platform` 字段决定后续参数
> 2. **写临时文件**：用 `write` 工具把内容写入临时文件
>    - macOS / Linux：`/tmp/_tw_<name>.txt`
>    - Windows：`$env:TEMP\_tw_<name>.txt`（PowerShell）或 `%TEMP%\_tw_<name>.txt`（CMD）
> 3. **调脚本写入**：按平台探测结果决定是否传 `--platform`
> 4. **清理临时文件**
>
> ✅ **`--platform` 决策规则**（基于 `--detect` 返回结果）：
> - `platform == "mac"` 或 `"linux"`，且用户**没有说**"给 Windows 用" → **不传 `--platform`**
> - `platform == "mac"` 或 `"linux"`，且用户**明确说**"给 Windows 用/供 Windows 打开/发给 Windows 用户" → 传 `--platform windows`
> - `platform == "windows"` → **不传 `--platform`**（脚本自动按 Windows 规则处理）
>
> 🚫 **唯一豁免**：纯二进制文件（图片、音频、视频、zip 等）不适用本技能。

---

## 技能概述

替代 OpenClaw 内置 `write` 工具处理所有纯文本写入，提供：

| 能力 | 说明 |
|------|------|
| **BOM 自动推断** | Windows CSV/TSV/TXT 自动加 BOM；JSON/YAML/Shell 脚本等强制不加 |
| **换行符自动适配** | Windows → `\r\n`；macOS/Linux → `\n`；支持 `preserve` 保留已有风格 |
| **GBK 支持** | Windows `.bat`/`.cmd` 含中文时使用 GBK，避免 cmd.exe 乱码 |
| **跨平台目标指定** | `--platform windows` 在 macOS 上生成供 Windows 使用的文件 |
| **追加模式** | `--append` 追加到已有文件末尾，不覆盖 |
| **已有文件保留** | `--preserve` 自动保留已有文件的 BOM 状态和换行符风格 |

---

## `--platform` 使用规则（重要）

**`--platform` 表示"文件将被打开/使用的目标平台"，不是当前运行平台。**

| 情况 | 操作 |
|------|------|
| 用户在 **macOS/Linux** 上使用，文件也在本机使用 | **不传 `--platform`**（脚本自动检测当前系统） |
| 用户在 **Windows** 上使用，文件也在本机使用 | **不传 `--platform`**（脚本自动检测当前系统） |
| 用户在 **macOS** 上，但文件**发给 Windows 用户**（尤其是 CSV/Excel） | 传 `--platform windows` |
| 用户在 **Windows** 上，但文件**发给 macOS/Linux 用户** | 传 `--platform mac` |
| 用户**没有说明**文件发给谁、在哪打开 | **不传 `--platform`**（脚本自动检测，不要猜测） |

> ⚠️ **严禁在用户未明确说"给 Windows 用"时默认传 `--platform windows`。**
> 错误地传 `--platform windows` 会在 mac 上生成带 CRLF 和不必要 BOM 的文件。

---

## 命令行接口

```
python3 "{SKILL_DIR}/scripts/write_file.py" [参数]

内容来源（必须二选一）:
  --content-file <file>    从临时文件读取内容 【推荐】避免 shell 转义破坏内容
  --content <string>       直接传内容字符串（适合单行、无特殊字符的简单内容）

目标路径（必须）:
  --path <path>            目标文件路径（相对或绝对，支持 ~ 展开）

编码控制（可选，默认按文件类型 + 当前系统自动推断）:
  --encoding <enc>         强制指定编码: utf-8 | utf-8-sig | gbk | gb18030 | utf-16 | utf-16-le
  --platform <p>           目标平台: windows | mac | linux
                           【默认不传】脚本自动检测当前系统
                           【仅在跨平台场景下传】见上方"--platform 使用规则"

换行符控制（可选，默认按 --platform/当前系统自动选择）:
  --newline <nl>           crlf | lf | preserve | auto（默认 auto）
                           preserve = 保留已有文件的换行符风格

已有文件保留（可选）:
  --preserve               同时启用 --preserve-bom 和 --preserve-newline
  --preserve-bom           已有文件有 BOM 时保留，即使推断规则认为不需要
  --preserve-newline       等同于 --newline preserve

写入模式（可选）:
  --append                 追加模式，内容追加到文件末尾（不覆盖）

其他（可选）:
  --no-mkdir               禁止自动创建父目录（默认自动创建）
```

---

## 输出格式（JSON，stdout）

```json
// 成功
{
  "status": "ok",
  "path": "/absolute/path/to/file.csv",
  "encoding": "utf-8-sig",
  "bom": true,
  "newline": "crlf",
  "bytes": 1024,
  "bytes_written": 1024,
  "mode": "write",
  "preserved_bom": false,
  "preserved_newline": false
}

// 失败
{"status": "error", "message": "写入文件失败: Permission denied"}

// 编码错误（字符无法用指定编码表示）
{"status": "error", "message": "编码错误: 字符 '😀' (U+1F600) 无法用 gbk 编码表示。建议使用 --encoding utf-8 或 --encoding utf-8-sig"}
```

---

## 编码推断规则（`--encoding auto` 时）

**不传 `--platform` = 脚本自动检测当前系统**（mac 上运行 → 按 macOS 列处理）

### 基础编码表

| 文件后缀 | macOS / Linux（默认/不传 platform） | Windows（`--platform windows` 或当前系统是 Windows） |
|---------|:-----------------------------------:|:----------------------------------------------------:|
| `.csv` `.tsv` | utf-8（**无 BOM**） | **utf-8-sig（有 BOM ✅）** |
| `.reg` | **utf-16（有 BOM）** | **utf-16（有 BOM ✅）** |
| `.inf` | utf-8（无 BOM） | **gbk（ANSI）** |
| `.ps1` | utf-8-sig（有 BOM） | utf-8-sig（有 BOM） |
| `.bat` `.cmd` (无中文) | utf-8（无 BOM） | utf-8（无 BOM） |
| `.bat` `.cmd` (有中文) | utf-8（无 BOM） | **gbk（自动检测 ✅）** |
| `.sh` `.bash` `.zsh` `.fish` | utf-8（无 BOM） | utf-8（无 BOM） |
| `.json` `.jsonc` `.json5` | utf-8（无 BOM） | utf-8（无 BOM） |
| `.yaml` `.yml` `.toml` `.ini` `.conf` `.env` | utf-8（无 BOM） | utf-8（无 BOM） |
| `.html` `.htm` `.xml` `.svg` | utf-8（无 BOM） | utf-8（无 BOM） |
| `.md` `.markdown` `.rst` `.txt` | utf-8（无 BOM） | utf-8（无 BOM） |
| `.js` `.ts` `.jsx` `.tsx` `.vue` `.py` 等代码 | utf-8（无 BOM） | utf-8（无 BOM） |
| `.css` `.less` `.scss` `.sass` | utf-8（无 BOM） | utf-8（无 BOM） |
| `.sql` `.graphql` `.proto` | utf-8（无 BOM） | utf-8（无 BOM） |
| `.log` `.lock` | utf-8（无 BOM） | utf-8（无 BOM） |
| 无后缀文件 (Dockerfile, Makefile 等) | utf-8（无 BOM） | utf-8（无 BOM） |
| 其他 | utf-8（无 BOM） | utf-8（无 BOM） |

### 覆盖的文件类型（完整列表）

脚本已内置支持以下所有纯文本文件类型的编码推断：

**编程语言**：`.js` `.ts` `.jsx` `.tsx` `.mjs` `.cjs` `.vue` `.svelte` `.py` `.pyi` `.go` `.rs` `.c` `.cpp` `.cc` `.h` `.hpp` `.java` `.kt` `.scala` `.groovy` `.swift` `.m` `.mm` `.rb` `.erb` `.php` `.dart` `.lua` `.r` `.R` `.pl` `.pm` `.ex` `.exs` `.erl` `.hrl` `.hs` `.fs` `.clj` `.cljs` `.elm` `.v` `.sv` `.vhd`

**配置文件**：`.json` `.jsonc` `.json5` `.yaml` `.yml` `.toml` `.ini` `.cfg` `.conf` `.env` `.editorconfig` `.prettierrc` `.eslintrc` `.babelrc` `.nvmrc`

**标记语言**：`.html` `.htm` `.xhtml` `.xml` `.svg` `.md` `.markdown` `.rst`

**脚本文件**：`.sh` `.bash` `.zsh` `.fish` `.bat` `.cmd` `.ps1`

**数据/查询**：`.sql` `.graphql` `.gql` `.proto`

**其他**：`.css` `.less` `.scss` `.sass` `.styl` `.log` `.lock` `.tf` `.hcl` `.nix` `.prisma` `.plist`

**无后缀文件**：`Dockerfile` `Makefile` `Gemfile` `Rakefile` `Procfile` `Vagrantfile` `Brewfile` `Podfile` `Jenkinsfile` `CODEOWNERS` `LICENSE` `README` `CHANGELOG` 等

### 核心原则

- mac 上不传 `--platform`，`.csv` 生成**无 BOM** 的 utf-8（适合本机使用）
- 只有明确要生成"给 Windows 用户用的 CSV"时，才传 `--platform windows`
- `.ps1` 是唯一在 mac 上也加 BOM 的类型（因为它本身就是在 Windows 上执行的脚本）
- `.bat`/`.cmd` 含中文时，**Windows 平台自动切换为 GBK**，无需手动传参
- `.reg` 注册表文件**必须是 UTF-16 with BOM**，脚本自动处理
- `.inf` 安装信息文件在 Windows 上使用 GBK（ANSI 编码）

---

## 标准执行流程

### 第零步：平台探测（必须）

```bash
python3 "{SKILL_DIR}/scripts/write_file.py" --detect
```

返回示例（macOS）：
```json
{
  "platform": "mac",
  "system": "Darwin",
  "python": "3.11.0",
  "default_csv_encoding": "utf-8",
  "default_csv_bom": false,
  "needs_platform_windows_for_local_csv": false
}
```

返回示例（Windows）：
```json
{
  "platform": "windows",
  "system": "Windows",
  "python": "3.11.0",
  "default_csv_encoding": "utf-8-sig",
  "default_csv_bom": true,
  "needs_platform_windows_for_local_csv": true
}
```

**根据返回值决策 `--platform` 参数：**

| `platform` 返回值 | 用户意图 | 是否传 `--platform` |
|------------------|---------|-------------------|
| `mac` / `linux` | 本机使用（未说明） | **不传** |
| `mac` / `linux` | 明确说"给 Windows 用" | 传 `--platform windows` |
| `windows` | 任何场景 | **不传**（脚本自动按 Windows 规则） |

### 第一步：用 `write` 工具将内容写入临时文件

```
# macOS / Linux
write(path="/tmp/_tw_<目标文件名>.txt", content="<文件完整内容>")

# Windows（PowerShell）
write(path="$env:TEMP\_tw_<目标文件名>.txt", content="<文件完整内容>")
```

> 临时文件命名建议用目标文件名做后缀（如目标是 `report.csv`，临时文件用
> `/tmp/_tw_report.csv.txt`），避免并发时路径冲突。

### 第二步：调用脚本写入目标文件

```bash
# macOS / Linux
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "<目标文件路径>" \
  --content-file "/tmp/_tw_<目标文件名>.txt" \
  [--platform windows|mac|linux] \
  [--encoding utf-8-sig|gbk|...] \
  [--preserve] \
  [--append]

# Windows（PowerShell）
python3 "{SKILL_DIR}/scripts/write_file.py" `
  --path "<目标文件路径>" `
  --content-file "$env:TEMP\_tw_<目标文件名>.txt" `
  [--platform windows|mac|linux] `
  [--encoding utf-8-sig|gbk|...] `
  [--preserve] `
  [--append]
```

### 第三步：检查输出结果

- `status == "ok"` → 向用户展示文件路径、编码、是否含 BOM
- `status == "error"` → 说明错误原因，检查路径权限或磁盘空间

### 第四步：清理临时文件

```bash
# macOS / Linux
rm -f /tmp/_tw_<目标文件名>.txt

# Windows（PowerShell）
Remove-Item -Force "$env:TEMP\_tw_<目标文件名>.txt"

# Windows（CMD）
del "%TEMP%\_tw_<目标文件名>.txt"
```

---

## 典型场景示例

### 场景 1：用户说"写入 csv 文件"（未说明平台）

```bash
# 第零步：探测平台
python3 "{SKILL_DIR}/scripts/write_file.py" --detect
# → {"platform": "mac", ...}  当前是 mac，不传 --platform

# 第一步：写临时文件（macOS/Linux）
write(path="/tmp/_tw_poems.csv.txt", content="标题,作者,内容\n静夜思,李白,床前明月光")
# Windows：write(path="$env:TEMP\_tw_poems.csv.txt", ...)

# 第二步：脚本写入，mac 上不传 --platform → utf-8 无 BOM（本地使用）
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "~/Desktop/poems.csv" \
  --content-file "/tmp/_tw_poems.csv.txt"
# Windows：--content-file "$env:TEMP\_tw_poems.csv.txt"

# 第四步：清理（macOS/Linux）
rm -f /tmp/_tw_poems.csv.txt
# Windows：Remove-Item -Force "$env:TEMP\_tw_poems.csv.txt"
```

### 场景 2：用户明确说"给 Windows 用户用的 CSV"

```bash
# 第零步：探测平台
python3 "{SKILL_DIR}/scripts/write_file.py" --detect
# → {"platform": "mac", ...}  用户说给 Windows 用，传 --platform windows

# 第二步：脚本写入，指定 Windows 平台 → utf-8-sig + CRLF
# macOS/Linux：
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "export.csv" \
  --content-file "/tmp/_tw_export.csv.txt" \
  --platform windows
# Windows：将 --content-file 改为 "$env:TEMP\_tw_export.csv.txt"
# → 自动使用 utf-8-sig + CRLF，Excel 双击直接正确显示中文
```

### 场景 3：JSON / YAML 配置文件

```bash
# 无需任何额外参数，自动 utf-8 无 BOM（无论任何平台）
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "config.json" \
  --content-file "/tmp/_tw_config.json.txt"
# Windows：将 --content-file 改为 "$env:TEMP\_tw_config.json.txt"
```

### 场景 4：PowerShell 脚本（含中文注释）

```bash
# .ps1 自动 utf-8-sig，无需额外参数（ps1 在 Windows 执行，始终需要 BOM）
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "deploy.ps1" \
  --content-file "/tmp/_tw_deploy.ps1.txt"
# Windows：将 --content-file 改为 "$env:TEMP\_tw_deploy.ps1.txt"
```

### 场景 5：Windows 批处理脚本（含中文）

```bash
# Windows 平台：.bat 含中文时脚本自动检测并使用 GBK 编码
# 无需手动传 --encoding gbk（脚本内置非 ASCII 字符检测）
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "run.bat" \
  --content-file "/tmp/_tw_run.bat.txt"
# Windows：将 --content-file 改为 "$env:TEMP\_tw_run.bat.txt"
# → Windows 上自动检测到中文，使用 gbk 编码

# macOS/Linux 上编写 .bat 文件供 Windows 使用：
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "run.bat" \
  --content-file "/tmp/_tw_run.bat.txt" \
  --platform windows
# Windows：--content-file "$env:TEMP\_tw_run.bat.txt"
# → 自动检测到中文，使用 gbk 编码
```

### 场景 6：Shell 脚本

```bash
# .sh 自动 utf-8 无 BOM + LF，无需额外参数
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "setup.sh" \
  --content-file "/tmp/_tw_setup.sh.txt"
# Windows：将 --content-file 改为 "$env:TEMP\_tw_setup.sh.txt"
```

### 场景 7：追加内容到已有日志文件

```bash
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "app.log" \
  --content-file "/tmp/_tw_new_lines.txt" \
  --append --preserve
# Windows：将 --content-file 改为 "$env:TEMP\_tw_new_lines.txt"
# --preserve 保留已有文件的编码和换行符风格
```

### 场景 8：更新已有 CSV（保留原有 BOM 和换行符）

```bash
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "data.csv" \
  --content-file "/tmp/_tw_data.csv.txt" \
  --preserve
# Windows：将 --content-file 改为 "$env:TEMP\_tw_data.csv.txt"
# 若原文件有 BOM，新文件保留；若原文件 CRLF，新文件保留 CRLF
```

### 场景 9：Windows 注册表文件（.reg）

```bash
# .reg 文件必须是 UTF-16 with BOM，脚本自动处理
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "settings.reg" \
  --content-file "/tmp/_tw_settings.reg.txt"
# Windows：将 --content-file 改为 "$env:TEMP\_tw_settings.reg.txt"
# → 自动使用 utf-16 编码（含 BOM），regedit 可正常导入
```

### 场景 10：Windows 安装信息文件（.inf）

```bash
# Windows 上 .inf 文件自动使用 GBK (ANSI) 编码
python3 "{SKILL_DIR}/scripts/write_file.py" \
  --path "driver.inf" \
  --content-file "$env:TEMP\_tw_driver.inf.txt" \
  --platform windows
# macOS/Linux：将 --content-file 改为 "/tmp/_tw_driver.inf.txt"
# → Windows 设备管理器可正常识别
```

---

## 常见陷阱

| 陷阱 | 说明 |
|------|------|
| **绕过 skill、直接用 `write` 工具写目标文件** | **严禁。此技能可用时，write 工具只允许写临时文件，不得写最终目标文件** |
| **"内容简单/只有几行/纯英文"就用 write 直接写** | **严禁。简单内容同样必须走脚本，规则无大小豁免** |
| **"快速改一下"就绕过脚本** | **严禁。没有"快速修改豁免"，任何目标文件写入都必须走脚本** |
| **先用 write 写目标文件，再用脚本覆盖** | **严禁。初次 write 写目标文件已违规，必须直接从临时文件走脚本** |
| 用 `write` 工具直接写 CSV | `write` 工具 utf-8 无 BOM，Windows Excel 必然乱码 |
| **在 mac 上默认传 `--platform windows`** | **用户没说"给 Windows 用"时绝不传此参数，否则 mac 本机文件会有多余 BOM 和 CRLF** |
| 忘记传 `--platform windows` | 明确要生成"给 Windows 用户的 CSV"时不传，结果是无 BOM，Windows 乱码 |
| 对所有文件无脑加 BOM | HTML/JSON/YAML/`.sh` 加 BOM 会导致解析错误或语法报错 |
| 用 GBK 写含 emoji 的文件 | GBK 无法表示 emoji，脚本会报编码错误，改用 utf-8 |
| `.reg` 文件不用 UTF-16 | Windows 注册表文件必须是 UTF-16 LE with BOM，否则 regedit 无法导入 |
| 临时文件名冲突 | 并发写多个文件时，临时文件名要包含目标文件名加以区分 |
| Python 不可用 | 脚本依赖 `python3`（Python 3.6+），若不可用提示用户安装 |

---

## 注意事项

- `{SKILL_DIR}` 在实际执行时替换为此技能的**实际安装路径**
- 脚本**零外部依赖**，仅使用 Python 标准库（`pathlib` `json` `argparse` `platform`）
- 支持 Python 3.6+，兼容 Windows / macOS / Linux
- 父目录不存在时默认自动创建（`--no-mkdir` 可禁止）
- `--content` 直接传字符串适合内容简单的场景；内容含引号、`$`、换行符等特殊字符时
  必须用 `--content-file` 方式，否则 shell 转义可能破坏内容
