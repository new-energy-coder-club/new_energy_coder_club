# File Organizer 脚本功能详解

本项目包含 3 个核心 PowerShell 脚本（Windows）和 3 个对应的纯 Bash 脚本（macOS），功能完全一致。

---

## 1. `organize.ps1` — 文件整理脚本

### 基本信息
- **用途**：扫描目标目录中的零散文件，按规则自动归类到文件夹中
- **核心策略**：**零删除、零覆盖** — 只移动文件和创建文件夹，绝不删除或覆盖任何文件

### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `TargetDir` | string | 是 | — | 要整理的目标目录路径 |
| `-Phase` | string | 否 | `all` | 执行阶段：`phase1`、`phase2`、`all` |
| `-SizeThreshold` | double | 否 | `1` | 超大文件阈值（GB），超过此大小的文件跳过 |
| `-Whitelist` | string[] | 否 | `@()` | 白名单文件列表，这些文件不会被整理 |
| `-DryRun` | switch | 否 | — | 预览模式，不实际执行移动操作 |

### 执行流程

#### Phase 1：关键词匹配 + 命名规律匹配

```
扫描文件 → 过滤跳过项 → 关键词匹配已有文件夹 → 命名规律匹配已有文件夹 → 输出未匹配文件列表
```

**详细步骤**：

1. **扫描候选文件**（`Invoke-ScanCandidates` 函数）
   - 遍历目标目录下所有**一级文件**（不递归子目录）
   - 依次检查并**跳过**以下文件：
     - **白名单文件**：用户通过 `-Whitelist` 指定的文件 → 记录到 `skipped`
     - **快捷方式**：`.lnk` `.app` `.url` `.webloc` `.desktop` → 记录到 `skipped`
     - **系统文件**：`desktop.ini`、`.DS_Store`、`Thumbs.db`、以 `.` 开头的隐藏文件等 → 记录到 `skipped`
     - **超大文件**：文件大小超过 `SizeThreshold` GB → 记录到 `errors`，建议手动处理
     - **被占用文件**：尝试以独占方式打开文件，失败则说明被其他程序占用 → 记录到 `errors`
   - 通过检查的文件进入候选列表，记录：文件名、路径、扩展名、文件大小、最后访问时间、最后修改时间

2. **关键词匹配已有文件夹**（`Invoke-MatchExistingFolders` 函数）
   - 获取目标目录下所有已有文件夹（不含以 `.` 开头的隐藏文件夹）
   - 对每个候选文件，检查文件名（不含扩展名）是否**包含**某个文件夹名称
   - 匹配规则：文件夹名至少 2 个字符，文件名中包含文件夹名即算匹配
   - 示例：`截图2025.png` → 文件名包含"截图" → 移入"截图"文件夹

3. **命名规律匹配**（`Test-NamingPatternMatch` 函数）
   - 对关键词未匹配的文件，检查文件名是否与某文件夹内已有文件的命名模式一致
   - 匹配逻辑：与文件夹内的文件名比较**公共前缀**，如果公共前缀 ≥ 3 个字符，且有 ≥ 2 个文件匹配，则认为属于该文件夹
   - 示例：文件夹"工作"内有"收入预估10月"和"收入预估11月" → "收入预估12月"与两者公共前缀均为"收入预估"（4字符，≥3） → 匹配成功

4. **输出结果**（仅 phase1）
   - 已匹配文件直接移动（或 dry_run 标记）
   - 未匹配文件输出到 `unmatched_files` 字段，供 AI 进行第三步语义分析
   - 同时输出 `existing_folders` 列表

#### Phase 2：兜底分类（不常用文件 + 按文件类型）

```
重新扫描剩余文件 → 不常用文件归类 → 按扩展名分类
```

**详细步骤**：

1. **不常用文件检测**（`Invoke-FallbackClassify` 函数）
   - 检查每个文件的最后访问时间（`atime`）
   - 如果距今超过 **60 天** 未访问，标记为"不常用"
   - 当不常用文件 ≥ 2 个时，创建"不常用文件"文件夹并移入
   - 如果不常用文件只有 1 个，则不单独建文件夹，交给下一步按类型分类

2. **按文件类型分类**
   - 根据文件扩展名匹配到预定义的分类文件夹：

     | 文件夹 | 扩展名 |
     |--------|--------|
     | 图片 | .png .jpg .jpeg .gif .bmp .tiff .webp .svg .ico .heic .heif |
     | 文档 | .docx .pdf .txt .doc .md .ppt .pptx .odt .rtf .pages |
     | 表格 | .xlsx .csv .xls .numbers .ods .tsv |
     | 安装包 | .exe .dmg .pkg .msi .apk .deb .rpm .appimage |
     | 音频 | .mp3 .wav .flac .m4a .ogg .aac .wma .aiff |
     | 视频 | .mp4 .avi .mov .mkv .flv .wmv .webm .m4v .ts |
     | 压缩包 | .zip .rar .7z .tar .gz .bz2 .xz .tgz |
     | 其他文件 | 以上都不匹配的扩展名 |

### 安全移动机制（`Invoke-SafeMove` 函数）

每次移动文件时：
1. 目标文件夹不存在则自动创建
2. **同名文件冲突处理**：如果目标位置已有同名文件，自动添加 `_1`、`_2` 等后缀，**绝不覆盖**
3. DryRun 模式下只计算目标路径，不实际移动

### 日志输出

脚本执行完毕后输出 JSON 格式日志（同时保存到 `<目标目录>/.file_organizer_logs/organize_<时间戳>.json`）：

```json
{
  "timestamp": "2026-03-06T10:30:00",
  "target_dir": "C:\\Users\\xxx\\Desktop",
  "phase": "phase1",
  "operations": [
    {
      "file": "截图2025.png",
      "original_path": "C:\\Users\\xxx\\Desktop\\截图2025.png",
      "destination_path": "C:\\Users\\xxx\\Desktop\\截图\\截图2025.png",
      "destination_folder": "截图",
      "method": "关键词匹配已有文件夹",
      "confidence": "high",
      "status": "done"
    }
  ],
  "unmatched_files": [ ... ],  // 仅 phase1
  "existing_folders": [ ... ], // 仅 phase1
  "skipped": [ ... ],
  "errors": [ ... ],
  "created_folders": [ ... ],
  "summary": {
    "total_scanned": 25,
    "auto_organized": 10,
    "skipped_count": 8,
    "error_count": 2,
    "created_folder_count": 3
  }
}
```

---

## 2. `rollback.ps1` — 回撤脚本

### 基本信息
- **用途**：读取 organize.ps1 生成的操作日志，将文件移回原位置，并清理空文件夹
- **三个子命令**：`list-logs`、`rollback-all`、`rollback-single`

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `Command` | string | 是 | 子命令：`rollback-all` / `rollback-single` / `list-logs` |
| `-LogPath` | string | rollback 时必填 | 操作日志 JSON 文件路径 |
| `-FileName` | string | rollback-single 时必填 | 要回撤的文件名 |
| `-TargetDir` | string | list-logs 时必填 | 当初整理的目标目录 |
| `-DryRun` | switch | 否 | 预览模式 |

### 子命令详解

#### `list-logs`：列出可用日志

```powershell
rollback.ps1 list-logs -TargetDir "C:\Users\xxx\Desktop"
```

- 扫描 `<目标目录>/.file_organizer_logs/` 下所有 `organize_*.json` 文件
- 按时间倒序排列
- 输出每个日志的：文件名、路径、时间戳、操作数量、是否为 dry_run

#### `rollback-all`：一键撤销所有操作

```powershell
rollback.ps1 rollback-all -LogPath "C:\...\organize_20260306_103000.json"
```

执行流程：
1. 读取日志中的 `operations` 数组
2. **倒序遍历**（后移动的先恢复，避免依赖冲突）
3. 对每个操作：
   - 检查目标文件是否存在（不存在 → 报错跳过）
   - 检查原位置是否已有同名文件（有 → 报错跳过，防止覆盖）
   - 将文件从目标路径移回原路径
4. **清理空文件夹**：
   - 遍历日志中的 `created_folders`（整理时自动创建的文件夹）
   - 检查文件夹内是否还有"用户文件"（排除 `desktop.ini`、`Thumbs.db`、`.DS_Store` 等系统文件）
   - 如果只剩系统文件或完全为空：
     - 先清除系统文件的 System+Hidden 属性，然后删除
     - 清除文件夹属性，然后删除文件夹
   - 这解决了 Windows 自动生成的 `desktop.ini`（带 System+Hidden 属性）阻止文件夹删除的问题

#### `rollback-single`：撤销单个文件

```powershell
rollback.ps1 rollback-single -LogPath "C:\...\organize_20260306_103000.json" -FileName "截图2025.png"
```

执行流程：
1. 在日志的 `operations` 中查找匹配 `-FileName` 的记录
2. 将该文件移回原位置
3. 检查移出后源文件夹是否变空，如果是自动创建的文件夹且已空，执行清理（逻辑同上）

### 输出格式

```json
{
  "rollback_log": "...",
  "dry_run": false,
  "restored": [
    { "file": "截图2025.png", "from": "...", "to": "...", "status": "done" }
  ],
  "failed": [ ... ],
  "cleaned_folders": [
    { "folder": "不常用文件", "path": "...", "status": "removed" }
  ]
}
```

---

## 3. `sort_desktop.ps1` — 桌面图标排列脚本

### 基本信息
- **用途**：通过 Windows COM 接口控制桌面图标的排序方式和紧凑排列
- **平台**：仅限 Windows（通过 Shell COM 对象操作，无需重启资源管理器）

### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `-SortBy` | string | 否 | 空（不改排序） | 排序方式：`Name`/`Size`/`ItemType`/`DateModified` |

### 技术实现

脚本内嵌了一段 C# 代码（通过 `Add-Type` 编译），定义了以下 COM 接口：

#### COM 接口链路

```
ShellWindows (CLSID: 9BA05972-...)
  → FindWindowSW() 找到桌面窗口
    → IServiceProvider::QueryService() 获取 IShellBrowser
      → IShellBrowser::QueryActiveShellView() 获取当前视图
        → QueryInterface() 获取 IFolderView2 接口
```

#### IFolderView2 接口（完整 vtable 定义）

脚本定义了 IFolderView2 接口的完整 vtable（包括从 IFolderView 继承的 14 个方法 + IFolderView2 自己的方法），确保 COM 调用的 vtable 偏移正确。关键方法：

| 方法 | 功能 |
|------|------|
| `SetSortColumns` | 设置排序列（传入 SORTCOLUMN 数组） |
| `GetSortColumns` | 读取当前排序列（诊断用） |
| `SetCurrentFolderFlags` | 设置文件夹标志（自动排列、对齐网格等） |
| `GetCurrentFolderFlags` | 读取当前标志 |
| `GetAutoArrange` | 检查自动排列是否开启 |

#### 排序属性键（PROPERTYKEY）

| 排序方式 | FMTID | PID | 排序方向 |
|----------|-------|-----|---------|
| Name | B725F130-47EF-101A-A5F1-02608C9EEBAC | 10 | 升序 |
| Size | 同上 | 12 | 降序 |
| ItemType | 同上 | 4 | 升序 |
| DateModified | 同上 | 14 | 降序 |

### 执行流程

```
读取当前状态（flags、是否自动排列）
    ↓
[如果指定了 -SortBy]
    → 调用 SetSortColumns() 设置排序列
    → 等待 500ms 让系统刷新
    ↓
[紧凑排列]
    → 如果自动排列已开启：先关闭 → 等 500ms → 再开启 → 等 2s
    → 如果自动排列已关闭：先开启 → 等 2s → 再关闭（恢复原状）
```

这个"开关切换"策略的目的是触发 Windows 重新排列图标，消除文件移走后留下的空位。

### 输出格式

```json
{
  "status": "success",
  "platform": "Windows",
  "sort_by": "ItemType",
  "methods_tried": [
    "Current state: flags=0x00000001, autoArrange=True",
    "SetSortColumns('ItemType') HR=0x00000000",
    "Disabled auto-arrange (HR=0x00000000)",
    "Re-enabled auto-arrange (HR=0x00000000)"
  ],
  "note": "Desktop icons sorted and compacted via IFolderView2 COM interface (no Explorer restart)"
}
```

---

## 4. `organize-mac.sh` — macOS 文件整理脚本（纯 Bash）

### 基本信息
- **用途**：等价于 `organize.ps1`，在 macOS 上运行的纯 Bash 实现
- **依赖**：零依赖，仅需 macOS 自带的 `/bin/bash`
- **日志格式**：TSV（Tab 分隔），保存到 `<目标目录>/.file_organizer_logs/organize_<时间戳>.log`
- **stdout 输出**：结构化文本（`|` 分隔），供 AI 解析

### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `<TARGET_DIR>` | string | 是 | — | 要整理的目标目录路径（位置参数） |
| `--phase` | string | 否 | `all` | 执行阶段：`phase1`、`phase2`、`all` |
| `--size-threshold` | double | 否 | `1` | 超大文件阈值（GB） |
| `--whitelist` | string | 否 | `""` | 白名单文件列表，逗号分隔 |
| `--dry-run` | flag | 否 | — | 预览模式，不实际执行移动操作 |

### 调用示例

```bash
# Phase 1：关键词匹配 + 命名规律匹配
bash organize-mac.sh ~/Desktop --phase phase1

# Phase 2：兜底分类
bash organize-mac.sh ~/Desktop --phase phase2

# 完整流程（phase1 + phase2）
bash organize-mac.sh ~/Desktop

# 带选项
bash organize-mac.sh ~/Desktop --phase phase1 --size-threshold 2 --whitelist "important.txt,keep.pdf" --dry-run
```

### macOS 特有实现

- **文件属性读取**：使用 `stat -f%z`（大小）、`stat -f%a`（访问时间）、`stat -f%m`（修改时间），macOS `stat` 格式
- **别名检测**：通过 `mdls -name kMDItemKind` 检测 macOS Alias 文件
- **被占用文件检测**：通过 `lsof` 检查文件是否被其他进程打开
- **日志格式**：TSV 而非 JSON，避免依赖 `jq` 等外部工具

### 日志文件格式（TSV）

```
#META	timestamp=2026-03-13T10:30:00	target_dir=/Users/xxx/Desktop	phase=phase1	size_threshold_gb=1	dry_run=false
#CREATED_FOLDER	图片	/Users/xxx/Desktop/图片	2026-03-13T10:30:00
截图2025.png	/Users/xxx/Desktop/截图2025.png	/Users/xxx/Desktop/截图/截图2025.png	截图	关键词匹配已有文件夹	done
#SKIPPED	.DS_Store	/Users/xxx/Desktop/.DS_Store	系统文件，自动跳过
#ERROR	huge.zip	/Users/xxx/Desktop/huge.zip	文件大小 2.50 GB（超过 1 GB 阈值）	建议手动移入对应分类文件夹
#SUMMARY	total=25	organized=10	skipped=8	errors=2	created_folders=3
```

- 以 `#` 开头的行为元数据（`#META`、`#CREATED_FOLDER`、`#SKIPPED`、`#ERROR`、`#SUMMARY`）
- 不以 `#` 开头的行为操作记录：`文件名<TAB>原路径<TAB>目标路径<TAB>目标文件夹<TAB>整理方式<TAB>状态`

---

## 5. `rollback-mac.sh` — macOS 文件回撤脚本（纯 Bash）

### 基本信息
- **用途**：等价于 `rollback.ps1`，读取 `organize-mac.sh` 生成的 TSV 操作日志，将文件移回原位置
- **三个子命令**：`list-logs`、`rollback-all`、`rollback-single`

### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `<command>` | string | 是 | 子命令：`list-logs` / `rollback-all` / `rollback-single`（位置参数） |
| `--log-path` | string | rollback 时必填 | 操作日志文件路径 |
| `--filename` | string | rollback-single 时必填 | 要回撤的文件名 |
| `--target-dir` | string | list-logs 时必填 | 当初整理的目标目录 |
| `--dry-run` | flag | 否 | 预览模式 |

### 调用示例

```bash
# 列出可用日志
bash rollback-mac.sh list-logs --target-dir ~/Desktop

# 一键撤销所有操作
bash rollback-mac.sh rollback-all --log-path ~/Desktop/.file_organizer_logs/organize_20260313_103000.log

# 撤销单个文件
bash rollback-mac.sh rollback-single --log-path ~/Desktop/.file_organizer_logs/organize_20260313_103000.log --filename "截图2025.png"
```

### 空文件夹清理逻辑

回撤完成后，自动检查日志中记录的 `#CREATED_FOLDER`：
- 如果文件夹内只剩隐藏文件（`.DS_Store` 等）或系统文件（`desktop.ini`、`Thumbs.db`），视为空
- 先清除这些系统文件，再删除空文件夹

---

## 6. `sort-desktop-mac.sh` — macOS 桌面图标排列脚本（纯 Bash）

### 基本信息
- **用途**：等价于 `sort_desktop.ps1`，通过 AppleScript 调用 Finder 的 `clean up` 功能排列桌面图标
- **依赖**：仅需 macOS 自带的 `osascript`

### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--sort-by` | string | 否 | 空（不改排序） | 排序方式：仅支持 `ItemType` |

### 调用示例

```bash
# 仅紧凑排列（消除空位）
bash sort-desktop-mac.sh

# 按项目类型排序 + 紧凑排列
bash sort-desktop-mac.sh --sort-by ItemType
```

### 技术实现

- **不传 `--sort-by`**：执行 `tell desktop to clean up`（仅紧凑排列，不改变排序）
- **传 `--sort-by ItemType`**：执行 `tell desktop to clean up by name`（按名称排序 + 紧凑排列，这是 Finder 中最接近"按项目类型排列"的选项）

---

## 脚本对照表

| 功能 | Windows（PowerShell） | macOS（Bash） |
|------|----------------------|---------------|
| 文件整理 | `organize.ps1` | `organize-mac.sh` |
| 文件回撤 | `rollback.ps1` | `rollback-mac.sh` |
| 桌面排列 | `sort_desktop.ps1` | `sort-desktop-mac.sh` |

---

## 文件关系图

```
用户请求"整理桌面"
    │
    ├─ Phase 1: organize.ps1 / organize-mac.sh --phase phase1
    │   └─ 输出：已匹配文件(移动) + 未匹配文件
    │
    ├─ AI 语义分析（读取 phase1 输出，手动移动语义匹配的文件）
    │
    ├─ Phase 2: organize.ps1 / organize-mac.sh --phase phase2
    │   └─ 对剩余文件按频率+类型兜底分类
    │
    ├─ 排列: sort_desktop.ps1 / sort-desktop-mac.sh [--sort-by ...]
    │   └─ 消除桌面图标空位
    │
    └─ 需要回撤时: rollback.ps1 / rollback-mac.sh
        ├─ list-logs → 查看日志列表
        ├─ rollback-all → 全部恢复
        └─ rollback-single → 单个恢复
```
