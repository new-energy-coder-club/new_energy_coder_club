---
name: kdocs
description: "操作金山文档（WPS 云文档 / Kdocs / 365.kdocs.cn / www.kdocs.cn）云文档的官方 Skill。核心能力覆盖云端新建、读取、编辑、搜索、分享、整理在线文档（智能文档、Word、Excel、PDF、PPT、演示文稿、智能表格、多维表格）及个人知识库。当用户的任务涉及云文档操作时使用，包括但不限于：写周报/日报/工作汇报、处理合同/发票、创建报名表/登记表、网页剪藏、接龙转表格、信息收集、文档总结与内容生成、改写仿写、翻译、AI PPT生成、PDF拆分导出、标签分类归档、收藏管理、碎片笔记整理、表格美化、回收站还原、知识库管理。"
homepage: https://www.kdocs.cn/latest
version: 1.4.5
metadata: {"openclaw":{"category":"kdocs","tokenUrl":"https://www.kdocs.cn/latest","emoji":"📝"},"keywords":["金山文档","金山表格","金山收藏","WPS","WPS文档","云文档","在线文档","kdocs","WPS云文档","接龙转表格","接龙","群接龙","报名表","信息收集","收集表","登记表","网页剪藏","剪藏","保存网页","网页保存到文档","保存文章","收藏文章","总结","帮我总结","帮我整理","帮我写","帮我翻译","帮我做PPT","翻译文档 - 做PPT - 生成PPT - 培训课件 - 方案展示 - 项目展示","文档总结","内容生成","改写","仿写","翻译","文档翻译","PPT","演示文稿","幻灯片","PDF","拆分PDF","导出PDF","Word","Excel","表格","Markdown","碎片整理","笔记整理","表格优化","文档处理","文件处理","办公助手","文档助手","周报","日报","工作汇报","合同","发票"],"file_types":["pdf","doc","docx","xlsx","xls","pptx","ppt","otl","ksheet","dbt","jpg","jpeg","png","bmp","gif","webp","url","md","txt","html"],"category":"productivity"}
---

# 金山文档 Skill 使用指南

金山文档 Skill 提供了一套完整的在线文档操作工具，支持创建、查询、读取、编辑、分享、移动多种类型的在线文档。

## 严格规则

### 禁止（NEVER）

- 禁止将 Token 明文出现在对话、日志、命令输出、代码注释或任何文件中；不得写入 `.env` 或环境变量；仅允许存放在 `mcporter` 的 `kdocs-qclaw` 配置中
- 上传写入等接口需传入的 `content_base64` 可能非常大（编码后 >1 MB），禁止在对话中逐 token 生成 Base64 字符串，用脚本完成文件读取、编码和传参

### 必须（MUST）

- 不可逆操作（delete/close 类）执行前必须向用户确认
- 写操作完成后必须用独立读取请求验证实际结果（不信任 `code: 0`）
- 创建文档并验证通过后，必须调用 `get_file_link` 获取链接并展示给用户

---

## 版本自检

首次使用或间隔超过 24 小时后，需要确认当前 Skill 是否为最新版本。

从本文件头部 frontmatter 的 `version` 字段读取本地版本号（语义化版本 X.Y.Z），然后调用远端接口比对：

```bash
mcporter call kdocs-qclaw.check_skill_update version=<本地版本号>
```

返回：`stdout` 为 JSON，包含三个关键字段：

| 字段 | 含义 |
|------|------|
| `latest` | 远端最新版本号 (X.Y.Z) |
| `release_note` | 该版本的变更摘要 |
| `instruction` | 升级操作步骤 |

若本地版本落后于 `latest`，按 `instruction` 中的指引完成升级或者把最新版信息用户告知用户。升级时需要保留旧版 `mcporter` 配置中的 Token，并将其迁移到新版本配置中。

---

## 认证配置

### Token 获取与管理

| 步骤 | 操作 |
|------|------|
| 读取 | 仅从 `mcporter` 的 `kdocs-qclaw` 配置读取 `Authorization` header；不再依赖 `.env` 或环境变量 |
| 获取 | 若 Token 为空或过期（错误码 `400006`），运行 `bash scripts/get-token.sh` 或 `node scripts/get-token.js` 获取新 Token，并直接写入 `mcporter`；mac/Linux 下 `get-token.sh` 会自动尝试打开浏览器登录页；Windows 下若本机有 Node.js，优先运行 `node scripts/get-token.js`，若本机没有 Node.js，则改为运行 `powershell -ExecutionPolicy Bypass -File scripts\get-token.ps1`；如需允许脚本自动安装 `mcporter`，可显式追加 `--auto-install-mcporter`（Node / Bash）或 `-AutoInstallMcporter`（PowerShell）；**脚本失败时改用「手动获取 Token」兜底** |
| 配置 | 仅允许将 Token 保存到 `mcporter`；禁止继续写入 `.env`、`KINGSOFT_DOCS_TOKEN` 或其他环境变量 |
| 验证 | 调用任意读取工具（如 `search_files`），返回 `code: 0` 即认证成功 |
| 过期 | 收到错误码 `400006` 时，Token 已过期，按上述「获取」步骤重新获取 |

> ⚠️ **mcporter 中未配置 Token 或 Token 过期时，所有工具调用将返回鉴权失败（400006）。**
> 🔒 **Token 安全**：任何时候都不得将 Token 明文值展示给用户、写入 `.env`、导出到环境变量，或拼接到命令中。Token 仅允许保存在 `mcporter` 的 `kdocs-qclaw` 配置中。
> 🚫 **配置名绑定**：本 Skill 的所有 `mcporter` 操作必须且只能使用 `kdocs-qclaw` 这个配置名（`mcporter call kdocs-qclaw ...`、`mcporter config get kdocs-qclaw` 等）。即使本机存在其他名称的 mcporter 配置且可正常调用，也**严禁**使用。若 `kdocs-qclaw` 配置不存在，必须先按下方「环境配置」章节完成注册。
> 🔄 **旧配置迁移**：若检测到历史 `.env` 或环境变量 `KINGSOFT_DOCS_TOKEN`，只允许做一次性迁移到 `mcporter`；`.env` 仅移除 `KINGSOFT_DOCS_TOKEN` 键（其他键保留），若 `.env` 仅含该键则直接删除空 `.env` 文件。
> 🛡️ **避免改动系统环境**：默认不会执行 `npm install -g` 这类全局安装命令；只有你明确加上参数时，才会自动安装 `mcporter`（Node / bash: `--auto-install-mcporter`，PowerShell: `-AutoInstallMcporter`）。

#### 手动获取 Token（脚本失败时的兜底方案）

当 `get-token` 脚本因环境问题执行失败时，引导用户手动获取：

1. 用户在浏览器访问 https://www.kdocs.cn/latest （需已登录 WPS 账号）
2. 点击页面右上角个人头像旁的主菜单 → 选择「龙虾专属入口」→ 复制 Token
3. 用户将 Token 提供给 Agent
4. Agent 将 Token 写入 mcporter（`<VERSION>` 从 SKILL.md frontmatter 的 `version` 字段读取）：

```bash
mcporter config remove kdocs-qclaw 2>/dev/null; mcporter config add kdocs-qclaw "https://mcp-center.wps.cn/skill_hub/mcp" --header "Authorization=Bearer <TOKEN>" --header "X-Skill-Version=<VERSION>" --header "X-Request-Source=qclaw" --transport http --scope home
```

> 收到用户 Token 后直接写入 mcporter，禁止回显 Token 明文。写入后调用任意读取工具验证（`code: 0` 即成功）。

### 环境配置

本 Skill 通过 MCP 协议提供服务，不限定特定客户端，可在任何支持 MCP 的 Agent 中运行（如 OpenClaw、Cursor、Claude Code 等）。

**自动化注册（mcporter 环境）**：运行 `bash scripts/setup.sh` 即可完成 MCP 服务注册。首次使用时会自动拉起授权；若检测到 Token 过期，`setup.sh` 也会自动调用 `get-token.sh` 重新获取。mac/Linux 下 `get-token.sh` 会自动尝试打开浏览器登录页并等待回调完成。默认不会自动全局安装 `mcporter`，若需要可显式追加 `--auto-install-mcporter`。

`scripts/setup.sh` 会自动完成：
1. 从 `SKILL.md` frontmatter 提取 `version` 版本号
2. 检查 `mcporter` 中现有的 `kdocs-qclaw` 配置，并在版本更新时保留旧 Token
3. 若检测到历史 `.env` 或环境变量 `KINGSOFT_DOCS_TOKEN`，仅做一次性迁移到 `mcporter`（`.env` 只移除 token 键并保留其他配置）
4. 注册 `mcporter` 时携带 `Authorization`、`X-Skill-Version` 和 `X-Request-Source` header，用于服务端鉴权、版本追踪和渠道区分

**手动配置（其他 MCP 客户端）**：在客户端 MCP 配置中添加金山文档服务时，仅维护 `mcporter` 中的 `kdocs-qclaw` 配置；不要再额外维护 `.env` 或 `KINGSOFT_DOCS_TOKEN`。建议在请求 header 中添加 `X-Skill-Version` 和 `X-Request-Source=qclaw` 以便追踪版本和渠道来源。

---

## 调用格式

根据运行环境选择对应方式：

- **MCP function call**（Cursor / Claude Code 等客户端）：直接构造 JSON，无需处理引号或转义：
  ```json
  {"name": "otl.insert_content", "arguments": {"file_id": "xxx", "content": "hello", "format": "markdown", "mode": "append"}}
  {"name": "read_file_content", "arguments": {"drive_id": "xxx", "file_id": "xxx", "format": "markdown", "include_elements": ["all"]}}
  ```
- **mcporter CLI**：`mcporter call` 按首个 `.` 拆分 `服务名.工具名`，工具名含点号时须分开传递以防截断：
  ```
  mcporter call kdocs-qclaw "otl.insert_content" file_id=xxx
  mcporter call kdocs-qclaw search_files keyword=test type=all
  ```
  - **数组/对象参数**：`key=value` 无法表达数组或对象，须用 `--args` 传 JSON
  - **值含空格或特殊字符**：值需引号包裹使其成为单个参数，如 `name="项目 周报.otl"`
  - **bash**：`--args` 用单引号包裹 JSON 即可：`--args '{"include_elements":["all"]}'`
  - **PowerShell**：单引号内的双引号会被吞掉，须用反斜杠转义：`--args '{\"include_elements\":[\"all\"]}'`


以下工具不可逆，调用前必须向用户确认（详细约束见各工具参考文档的「操作约束」区）：

`otl.block_delete`、`dbsheet.delete_sheet`、`kwiki.close_knowledge_view`、`sheet.delete_sheets`、`sheet.delete_range`、`dbsheet.delete_view`、`dbsheet.delete_fields`、`cancel_share`、`kwiki.delete_item`、`sheet.delete_protection_ranges`、`dbsheet.delete_records`、`sheet.delete_data_validations`、`sheet.delete_conditional_format_rules`、`sheet.delete_float_images`、`sheet.delete_filters`、`dbsheet.sheet_batch_delete`、`dbsheet.permission_delete_roles_async`

---

## 能力范围

### 支持的文档类型

| 类型 | 别名 | 文件后缀 | 说明 | 详细参考 |
|------|------|----------|------|----------|
| **智能文档** 首选 | ap | .otl | 排版美观，支持丰富组件 | `references/otl.md` — 页面、文本、标题、待办等元素操作 |
| 表格 | et / Excel | .xlsx | 数据表格专用 | `references/sheet.md` — 工作表管理、范围数据获取、批量更新 |
| PDF文档 | pdf | .pdf | PDF 文档专用 | `references/pdf.md` — PDF 创建与内容读取 |
| 文字文档 | wps / Word | .docx | 传统格式 | `references/wps.md` — Word 文档创建与内容操作 |
| 演示文稿 | wpp | .pptx | PPT 文档专用 | `references/wpp.md` — 幻灯片主题字体和配色设置、下载和导出 |
| 智能表格 | as | .ksheet | 结构化表格，支持多视图、字段管理 | `references/sheet.md` — 工作表管理、范围数据获取、批量更新 |
| 多维表格 | db / dbsheet | .dbt | 多数据表、丰富字段类型与视图（表格/看板/甘特等） | `references/dbsheet.md` — 支持数据表/视图/字段/记录的完整增删改查，含表单视图、父子记录、分享协作、高级权限与 Webhook |

### 通用工具总览

#### 文档创建与上传
| 工具 | 用途 |
|------|------|
| `create_file` | 在云盘下新建文件或文件夹 |
| `scrape_url` | 网页剪藏，抓取网页内容并自动保存为智能文档 |
| `scrape_progress` | 查询网页剪藏任务进度 |
| `upload_file` | 全量上传写入文件（更新已有 docx/pdf 或新建并上传本地文件） |

#### 文档读取与下载
| 工具 | 用途 |
|------|------|
| `list_files` | 获取指定文件夹下的子文件列表 |
| `download_file` | 获取文件下载信息 |
| `read_file_content` | 文档内容抽取为 Markdown/纯文本 |

#### 文件组织
| 工具 | 用途 |
|------|------|
| `move_file` | 批量移动文件(夹) |
| `rename_file` | 重命名文件（夹） |

#### 分享与访问
| 工具 | 用途 |
|------|------|
| `share_file` | 开启文件分享 |
| `set_share_permission` | 修改分享链接属性 |
| `cancel_share` | 取消文件分享 |
| `get_share_info` | 获取分享链接信息 |
| `get_file_link` | 获取文件的云文档在线访问链接 |

#### 搜索
| 工具 | 用途 |
|------|------|
| `search_files` | 文件（夹）搜索 |

完整参数、示例与返回值见 `references/drive.md`。

### 不支持的操作

- 无批量删除文件工具（仅支持移动）
- 云盘 drive 侧暂无逐文件 ACL 成员矩阵（以分享链接为主）；多维表格（.dbt）见 dbsheet.permission_* 与 dbsheet.share_*（详阅 references/dbsheet.md）
- 在线 Excel / 智能表格工作表区域保护见 sheet.*_protection_ranges 相关工具（详阅 references/sheet.md）
- 无文件版本回滚
- 无实时协同编辑控制

---

## 操作指南

### 执行指南

> 执行以下操作前，**必须**先阅读对应指南文件：

| 操作类型 | 指南文件 | 何时阅读 |
|----------|----------|----------|
| 获取文件标识指南 | `references/file-locating-guide.md` | 需要搜索或浏览文件时 |
| 文件读取指南 | `references/file-reading-guide.md` | 需要获取文档内容时 |
| 文件创建与写入指南 | `references/file-writing-guide.md` | 需要创建或编辑文档时 |

⚠️ 不阅读指南直接操作可能导致：参数错误、内容丢失、格式异常。

### 高频流程指引

#### 创建并写入文档

执行顺序：
1) 先按 `references/file-locating-guide.md` 获取目标目录 `drive_id`(可选)、`parent_id`(可选)。
2) 再按 `references/file-writing-guide.md` 选择文档类型与写入路径。
字段传递：步骤 1 获取 `drive_id`(可选)、`parent_id`(可选)，作为步骤 2 的输入，执行“新建写入”流程。

#### 上传本地文件到云盘

执行顺序：
1) 先按 `references/file-locating-guide.md` 获取目标目录 `drive_id`(可选)、`parent_id`(可选)、`file_id`(可选)。
2) 再按 `references/file-writing-guide.md` 的“本地文件上传（upload_file）”路径调用上传能力（新建上传或覆盖更新）。
字段传递：新建上传使用步骤 1 的 `drive_id`(可选)、`parent_id`(可选) + `name`；覆盖更新使用步骤 1 的 `file_id` 。

#### 搜索定位文档

工具说明：`search_files(keyword="关键词", type="all", page_size=20)`，获取 `file_id`、`drive_id` 供后续链路使用。
详细参数与返回结构见 `references/drive/search.md`。

### 更多操作流程

| 流程 | 说明 | 详细参考 |
|------|------|---------|
| AI 主题生成演示文稿 | 主题生成 PPT 标准链路：澄清需求、研究资料、大纲与生成上传 | `references/workflows/topic-ppt.md` |
| AI 文档生成演示文稿 | 文档生成 PPT 标准链路：创建会话、解析文档、生成大纲、美化风格与生成上传 | `references/workflows/doc-ppt.md` |
| 网页剪藏 | 抓取网页内容并自动保存为智能文档 | `references/workflows/web-scrape.md` |
| 搜索-读取-汇报撰写 | 搜索多份文档、提取信息、汇总撰写新报告 | `references/workflows/search-read-report.md` |
| 定期读取与播报 | 定期读取指定文档，提取关键信息生成摘要 | `references/workflows/periodic-read-summary.md` |
| 智能分类整理 | 列出目录，按内容或指定维度分类创建文件夹并归档 | `references/workflows/smart-classify.md` |
| 精准搜索与风险排查 | 在特定目录批量搜索文档，逐一读取分析，汇总到新文档 | `references/workflows/precise-search-analysis.md` |
| 接龙转表格 | 识别接龙文本内容，自动提取并转为在线表格 | `references/workflows/jielong-to-table.md` |
| 信息收集表单生成 | 根据用户需求自动设计并创建信息收集表格 | `references/workflows/form-generator.md` |
| 知识智能整理 | 对知识库中的零散内容进行智能化整理和结构化重组 | `references/workflows/knowledge-format.md` |
| 知识一键存入 | 将各类内容（网页、文件、文本）一键保存到知识库 | `references/workflows/knowledge-save.md` |
| 表格美化与数据规范 | 读取表格数据，进行格式美化、数据规范化和样式调整，并通过条件格式、数据校验、区域权限固化规则 | `references/workflows/table-beautify.md` |

---

## 错误速查

| 错误特征 | 原因 | 处理方式 |
|----------|------|----------|
| `400006` / 鉴权失败 | Token 过期或未配置 | 先运行 get-token 脚本重新获取；脚本失败则引导用户手动获取（见「认证配置」章节） |
| `429001` / 限频 | 请求过于频繁，响应含**限频恢复时间** | 立即停止命令调用，直到达到恢复时间；禁止立即重试、换参、换子命令连续请求 |
| `429002` / 熔断 | 多因短时间内连续触发 `429001` ，响应含**熔断持续时间** | 熔断时长内零请求，期满再试；重新规划任务避免请求过频 |
| 工具找不到 | 未注册 MCP 服务 | 运行 `bash scripts/setup.sh` 重新注册（mcporter 环境），或检查客户端 MCP 配置 |
| `mcporter` 未找到 | 运行环境缺少 mcporter | 默认不会改动系统环境（不执行全局安装）；可先手动安装后重试，或显式使用 `bash scripts/setup.sh --auto-install-mcporter` / `bash scripts/get-token.sh --auto-install-mcporter`（PowerShell: `-AutoInstallMcporter`） |
| `.env` 迁移后其他配置丢失 | 脚本会整文件删除 `.env` | 新流程仅移除 `KINGSOFT_DOCS_TOKEN` 键并保留其他键；若 `.env` 仅含该键会直接删除空 `.env` |
| 搜索无结果 | 关键词过精确 / 索引延迟 | 缩短关键词 / 等待 3-5 秒重试 |
| 读取内容为空 | 文件无内容或格式不支持 | 确认文件非空且后缀正确 |
| `read_file_content` 对 .csv 长时间 `running` | CSV 格式不支持 | 勿对 .csv 调用 `read_file_content`，建议用户转为 .xlsx 后用 `sheet.*` 读取 |
| 创建文件失败 | 文件名后缀不正确 | 检查后缀：`.otl` / `.docx` / `.xlsx` / `.ksheet` / `.dbt` / `.pdf` / `.pptx` |
| 移动文件失败 | 目标文件夹不存在 | 先搜索确认或创建文件夹 |
| HTTP 5xx / 超时 | 服务端故障 | 等 3 秒重试 1 次 |
| 验证不通过（回读值与预期不符） | 写入未生效或延迟 | 等 2 秒重新验证，仍不通过则报告用户 |
| `setup.sh` 执行失败 / 安装报错 | 当前版本可能已不兼容 | 执行上方「版本自检」流程 |
| MCP 接口返回未知错误码（非 5xx、非 400006、非 429001/429002、非工具不存在） | Skill 版本过旧导致接口不兼容 | 执行上方「版本自检」流程 |
| 错误信息含 `version`、`incompatible`、`not_supported`、`deprecated` 等版本关键词 | Skill 或 API 版本不兼容 | 执行上方「版本自检」流程 |
| 工具调用失败且原因不明 | 可能是 Skill 版本过旧 | 执行上方「版本自检」流程 |
| 工具调用失败需判断是否可重试 | 不同工具幂等性不同 | 查看该工具参考文档「操作约束」区的幂等性说明，幂等工具可安全重试，非幂等工具须先确认状态 |

---

## 安全约束

- 凭据由 MCP 运行时管理，Skill 自身不存储、不记录
- 无状态代理，不缓存任何文档内容或业务数据
- 仅在用户主动发起操作时调用对应 API

