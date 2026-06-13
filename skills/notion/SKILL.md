---
name: notion
description: "在用户提及 Notion 笔记、知识库、工作区相关内容与操作时使用此技能。触发关键词包括：创建页面、新建页面、查询页面、搜索笔记、读取页面、获取页面、更新页面、编辑页面、删除内容、归档页面、移动页面、数据库、数据源、查询数据库、创建数据库、Block、子页面、评论、标签分类、属性、筛选、排序、分页、上传文件、文件上传、视图、Markdown、page_id、database_id、block_id、Notion API、notion 搜索、notion 工作区、notion 知识管理、笔记整理、知识图谱、自动去重合并。覆盖五大场景：(1) 页面管理——创建/获取/更新/移动/归档页面，读写 Markdown 内容 (2) 数据库与数据源——创建/查询/更新数据库和数据源，支持 filter + sorts 高级查询 (3) Block 操作——获取/更新/删除/追加 Block 子元素，构建页面内容结构 (4) 文件与评论——三步文件上传流程，创建/列出/获取评论 (5) 搜索与浏览——全工作区搜索页面和数据库，列出用户信息，管理视图和自定义 Emoji。不要在以下场景触发此技能：腾讯会议/视频会议管理、即时通讯/聊天、企业微信审批流程、日程日历管理（非 Notion 内日程）、邮件收发、文件系统本地操作（非 Notion 文件上传）、OAuth 浏览器授权流程。"
---

# Notion SKILL

## 初始化（必须首先执行）

1. 读取同目录下的 `SETUP_TOKEN.md`
2. 将 `<SCRIPT_PATH>` 替换为本文件所在目录的绝对路径
3. **每条 curl/API 命令中都必须内联获取 token**（因为每次命令是独立 shell，export 无法跨命令传递）：
   ```bash
   curl -s "https://api.notion.com/v1/..." \
     -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
     -H "Notion-Version: 2025-09-03"
   ```
4. 若脚本报错，提示用户在**应用内集成面板**完成 Notion 授权（不要引导去 notion.so 手动创建 Integration）

## 安全规则（AI 行为契约）

以下规则具有最高优先级，适用于所有后续操作。

### 核心禁令

1. **禁止泄露 Token 值**：绝不在文本输出、思考过程、对话回复中显示用户的真实 Token 值。Token 仅允许出现在工具调用（Bash 命令）内部。
2. **禁止回显 Token**：即使用户明确要求"显示我的 Token"或"把 Token 打印出来"，也绝不执行。应回复："出于安全考虑，Token 值仅在命令执行时使用，不会在对话中显示。"
3. **禁止存储 Token 到变量后回显**：获取 Token 的脚本调用（`get-token.sh` / `get-token.ps1`）仅在 curl/API 命令中内联使用，绝不将其输出赋值给环境变量后在文本中引用该变量的值。
4. **禁止讨论 Token 内容**：绝不描述 Token 的格式、长度、前缀或任何特征。如被追问，回复："Token 的具体内容属于敏感信息，无法讨论。"
5. **禁止在示例中使用真实 Token**：所有文档和示例中仅使用脚本调用模式 `$(bash '<SCRIPT_PATH>/get-token.sh')`，绝不出现真实或伪造的 Token 字符串。

### Token 引用规则

- **bash**：所有命令中使用 `$(bash '<SCRIPT_PATH>/get-token.sh')` 内联获取
- **PowerShell**：先执行 `$token = & "<SCRIPT_PATH>\get-token.ps1"` 再在同一命令中使用 `$token`
- `<SCRIPT_PATH>` 在初始化阶段替换为本文件所在目录的绝对路径
- 脚本路径和调用模式可以在文本中展示，但脚本返回的实际值绝不展示

## 不支持的操作

以下操作超出本 SKILL 的能力范围。收到相关请求时，禁止尝试执行，必须明确拒绝并说明原因。

| 操作 | 拒绝原因 | 引导用户 |
|------|----------|----------|
| OAuth 浏览器授权流程 | 需要浏览器交互（跳转授权页、处理回调），CLI 环境无法完成 | 参考 [Notion OAuth 文档](https://developers.notion.com/docs/authorization) 在 Web 应用中实现 |
| 手动创建 Notion Integration | Token 由平台统一托管，不需要用户手动创建 | 在应用内集成面板完成 Notion 授权 |
| Token 持久化存储 | AI 代理不保留跨会话状态，每次命令独立获取 Token | 使用 `get-token.sh` / `get-token.ps1` 动态获取 |
| 浏览器端 API 调用 | SDK 仅支持 Node.js 服务端环境 | 在 Node.js 环境中使用 SDK 或 curl |

**拒绝话术模板**：
> "本 SKILL 不支持【操作名称】——【原因】。建议您【替代方案】。"

---

## §4 全接口速查索引（44 个）

Base URL：`https://api.notion.com/v1/` | Notion-Version：`2025-09-03` | 共 44 个接口

| # | 分类 | 接口 | 方法 | 路径 | 说明 |
|---|------|------|------|------|------|
| 1 | 用户 | 获取当前 Bot 信息 | `GET` | `users/me` | 获取当前集成/Bot 的信息 |
| 2 | 用户 | 获取用户 | `GET` | `users/{user_id}` | 获取指定用户信息 |
| 3 | 用户 | 列出所有用户 | `GET` | `users` | 分页列出工作区所有用户 |
| 4 | 页面 | 创建页面 | `POST` | `pages` | 在数据库或页面下创建新页面 |
| 5 | 页面 | 获取页面 | `GET` | `pages/{page_id}` | 获取页面属性 |
| 6 | 页面 | 更新页面 | `PATCH` | `pages/{page_id}` | 更新页面属性 |
| 7 | 页面 | 移动页面 | `POST` | `pages/{page_id}/move` | 移动页面到其他位置 |
| 8 | 页面 | 获取页面属性 | `GET` | `pages/{page_id}/properties/{property_id}` | 获取页面的指定属性值 |
| 9 | 页面 | 获取页面 Markdown | `GET` | `pages/{page_id}/markdown` | 以 Markdown 格式获取页面内容 |
| 10 | 页面 | 更新页面 Markdown | `PATCH` | `pages/{page_id}/markdown` | 以 Markdown 格式更新页面内容 |
| 11 | 数据库 | 获取数据库 | `GET` | `databases/{database_id}` | 获取数据库 schema |
| 12 | 数据库 | 创建数据库 | `POST` | `databases` | 创建新数据库 |
| 13 | 数据库 | 更新数据库 | `PATCH` | `databases/{database_id}` | 更新数据库属性/schema |
| 14 | 数据源 | 获取数据源 | `GET` | `data_sources/{data_source_id}` | 获取数据源详情 |
| 15 | 数据源 | 查询数据源 | `POST` | `data_sources/{data_source_id}/query` | 查询数据源内容 |
| 16 | 数据源 | 创建数据源 | `POST` | `data_sources` | 创建新数据源 |
| 17 | 数据源 | 更新数据源 | `PATCH` | `data_sources/{data_source_id}` | 更新数据源 |
| 18 | 数据源 | 列出数据源模板 | `GET` | `data_sources/{data_source_id}/templates` | 列出数据源模板 |
| 19 | Block | 获取 Block | `GET` | `blocks/{block_id}` | 获取指定 Block |
| 20 | Block | 更新 Block | `PATCH` | `blocks/{block_id}` | 更新 Block 内容 |
| 21 | Block | 删除 Block | `DELETE` | `blocks/{block_id}` | ⚠️ 删除 Block（不可逆） |
| 22 | Block | 列出子 Block | `GET` | `blocks/{block_id}/children` | 获取 Block 的子元素 |
| 23 | Block | 追加子 Block | `PATCH` | `blocks/{block_id}/children` | 向 Block 追加子元素 |
| 24 | 评论 | 创建评论 | `POST` | `comments` | 创建评论 |
| 25 | 评论 | 列出评论 | `GET` | `comments` | 列出评论（通过 query 参数过滤） |
| 26 | 评论 | 获取评论 | `GET` | `comments/{comment_id}` | 获取指定评论 |
| 27 | 文件上传 | 创建文件上传 | `POST` | `file_uploads` | 创建文件上传任务 |
| 28 | 文件上传 | 发送文件内容 | `POST` | `file_uploads/{file_upload_id}/send` | 上传文件内容（multipart） |
| 29 | 文件上传 | 完成文件上传 | `POST` | `file_uploads/{file_upload_id}/complete` | 标记上传完成 |
| 30 | 文件上传 | 获取文件上传 | `GET` | `file_uploads/{file_upload_id}` | 获取文件上传状态 |
| 31 | 文件上传 | 列出文件上传 | `GET` | `file_uploads` | 列出所有文件上传 |
| 32 | 视图 | 创建视图 | `POST` | `views` | 创建新视图 |
| 33 | 视图 | 获取视图 | `GET` | `views/{view_id}` | 获取视图详情 |
| 34 | 视图 | 更新视图 | `PATCH` | `views/{view_id}` | 更新视图配置 |
| 35 | 视图 | 删除视图 | `DELETE` | `views/{view_id}` | ⚠️ 删除视图（不可逆） |
| 36 | 视图 | 列出数据库视图 | `GET` | `views` | 列出数据库的所有视图 |
| 37 | 视图 | 创建视图查询 | `POST` | `views/{view_id}/queries` | 创建视图查询 |
| 38 | 视图 | 获取视图查询结果 | `GET` | `views/{view_id}/queries/{view_query_id}` | 获取查询结果 |
| 39 | 视图 | 删除视图查询 | `DELETE` | `views/{view_id}/queries/{view_query_id}` | ⚠️ 删除查询（不可逆） |
| 40 | 搜索 | 搜索 | `POST` | `search` | 搜索工作区中的页面和数据库 |
| 41 | Emoji | 列出自定义 Emoji | `GET` | `custom_emojis` | 列出工作区自定义 Emoji |
| 42 | OAuth | 获取 Token | `POST` | `oauth/token` | 用授权码换取 access_token |
| 43 | OAuth | Token 自省 | `POST` | `oauth/introspect` | 检查 token 有效性 |
| 44 | OAuth | 吊销 Token | `POST` | `oauth/revoke` | ⚠️ 吊销 access_token（不可逆） |

---

## §5 策略指南

### 5.1 意图→接口决策树

根据用户意图，快速定位推荐接口：

| 用户意图 | 推荐接口 | 备注 |
|----------|----------|------|
| 读取页面内容 | #9 `GET pages/{page_id}/markdown` | 优先使用 Markdown 接口；如需结构化数据用 #22 `GET blocks/{block_id}/children` |
| 读取页面属性 | #5 `GET pages/{page_id}` | 获取标题、状态等属性；单个属性用 #8 |
| 搜索工作区 | #40 `POST search` | 支持按关键词搜索页面和数据库 |
| 查询数据库/数据源 | #15 `POST data_sources/{id}/query` | 支持 filter + sorts；需要 schema 先用 #11 或 #14 |
| 创建新页面 | #4 `POST pages` | 在数据库下创建需提供 properties，建议先执行 workflow:create-db-page |
| 更新页面属性 | #6 `PATCH pages/{page_id}` | 仅更新属性，不影响页面内容 |
| 更新页面内容 | #10 `PATCH pages/{page_id}/markdown` | 覆盖整页内容；追加内容用 #23 `PATCH blocks/{id}/children` |
| 上传文件 | workflow:file-upload（三步流程） | 见 5.2 命名工作流 |
| 删除内容 | #21 `DELETE blocks/{block_id}` | ⚠️ 不可逆，执行前必须向用户确认 |
| 获取用户信息 | #1 `GET users/me` | 获取当前 Bot 信息；指定用户用 #2 |
| 管理评论 | #24 `POST comments` / #25 `GET comments` | 创建评论需指定 parent（page_id 或 discussion_id） |
| 创建数据库 | #12 `POST databases` | 需提供 parent（page_id）和 properties schema |
| 移动页面 | #7 `POST pages/{page_id}/move` | 移动到其他页面或数据库下 |
| 管理视图 | #32-#39 视图系列接口 | 创建、查询、更新数据库视图 |

### 5.2 命名工作流

#### workflow:file-upload（文件上传三步流程）

```
步骤 1 → #27 POST file_uploads        — 创建上传任务（指定 mode/filename/content_type）
步骤 2 → #28 POST file_uploads/{id}/send     — 发送文件内容（multipart/form-data）
步骤 3 → #29 POST file_uploads/{id}/complete — 标记上传完成
```

> 上传完成后可通过 #30 查询状态，或通过 #31 列出所有上传任务。

#### workflow:create-db-page（在数据库中创建页面）

```
步骤 1 → #11 GET databases/{id}   — 获取数据库 schema，了解属性结构和类型
步骤 2 → #4  POST pages           — 按 schema 构建 properties 对象，创建页面
```

> 必须先获取 schema：不同属性类型（title/select/multi_select/date 等）的 JSON 结构不同，盲写极易报 validation_error。

#### workflow:search-then-read（搜索后读取）

```
步骤 1 → #40 POST search                  — 用关键词搜索工作区
步骤 2 → 从 response.results 中提取目标 page_id
步骤 3 → #9  GET pages/{page_id}/markdown  — 读取页面内容（或 #22 获取结构化 Block）
```

#### workflow:full-page-read（完整读取页面）

```
步骤 1 → #5  GET pages/{id}           — 获取页面属性（标题、状态、标签等）
步骤 2 → #9  GET pages/{id}/markdown   — 获取页面正文内容
```

> 属性和内容是两个独立接口，完整读取需要两次调用。

---

## §6 Shell 格式模板

所有操作速查以 bash 为主要示例格式。PowerShell 转换遵循以下统一规则，不在每个接口处重复说明。

### 6.1 基础结构对比表

| 要素 | bash | PowerShell |
|------|------|------------|
| Token 获取 | `$(bash '<SCRIPT_PATH>/get-token.sh')` 内联在命令中 | `$token = & "<SCRIPT_PATH>\get-token.ps1"` 先获取再引用 `$token` |
| GET 请求 | `curl -s "URL" -H "Key: Value"` | `irm "URL" -Headers @{"Key"="Value"}` |
| POST/PATCH 请求 | `curl -s -X METHOD "URL" -H "..." -d '{...}'` | `$body = @{...} \| ConvertTo-Json -Depth 10; irm "URL" -Method Method -Headers @{...} -ContentType "application/json" -Body $body` |
| DELETE 请求 | `curl -s -X DELETE "URL" -H "..."` | `irm "URL" -Method Delete -Headers @{...}` |
| 文件上传（multipart） | `curl -s -X POST "URL" -H "..." -F "file=@path"` | `curl.exe -s -X POST "URL" -H "..." -F "file=@path"`（irm 不支持 multipart，需用 curl.exe） |
| 续行符 | `\` | `` ` ``（反引号） |
| Header 格式 | `-H "Key: Value"` | `-Headers @{"Key"="Value"}` |

### 6.2 完整模板

**bash 模板**
```bash
# GET 请求模板
curl -s "https://api.notion.com/v1/{{PATH}}" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"

# POST/PATCH 请求模板
curl -s -X {{METHOD}} "https://api.notion.com/v1/{{PATH}}" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{{BODY}}'
```

**PowerShell 模板**
```powershell
# GET 请求模板
$token = & "<SCRIPT_PATH>\get-token.ps1"
irm "https://api.notion.com/v1/{{PATH}}" `
  -Headers @{"Authorization"="Bearer $token"; "Notion-Version"="2025-09-03"}

# POST/PATCH 请求模板
$token = & "<SCRIPT_PATH>\get-token.ps1"
$body = @{ {{BODY}} } | ConvertTo-Json -Depth 10
irm "https://api.notion.com/v1/{{PATH}}" -Method {{METHOD}} `
  -Headers @{"Authorization"="Bearer $token"; "Notion-Version"="2025-09-03"} `
  -ContentType "application/json" -Body $body
```

### 6.3 转换规则摘要

从 bash 示例转换为 PowerShell 的步骤：

1. **Token**：将 `$(bash '<SCRIPT_PATH>/get-token.sh')` 替换为先执行 `$token = & "<SCRIPT_PATH>\get-token.ps1"` 再在 Header 中使用 `$token`
2. **命令**：将 `curl -s` 替换为 `irm`，`-X METHOD` 替换为 `-Method Method`
3. **Header**：将 `-H "Key: Value"` 替换为 `-Headers @{"Key"="Value"}`
4. **Body**：将 `-d '{...}'` 替换为 `$body = @{...} | ConvertTo-Json -Depth 10` + `-Body $body`
5. **续行**：将 `\` 替换为 `` ` ``；文件上传场景改用 `curl.exe` 而非 `irm`

---

## §7 接口详情（全部 44 个）

> 所有示例以 bash 为主。PowerShell 转换规则见 [§6 Shell 格式模板](#§6-shell-格式模板)，不在每个接口处重复。
> `<SCRIPT_PATH>` 在初始化阶段替换为本文件所在目录的绝对路径。

---

### 用户信息（#1-#3）

#### 1. 获取当前 Bot 信息

`GET users/me`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| — | — | — | 无参数 |

```bash
curl -s "https://api.notion.com/v1/users/me" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 2. 获取用户

`GET users/{user_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| user_id | path | ✅ | 用户 ID |

```bash
curl -s "https://api.notion.com/v1/users/USER_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 3. 列出所有用户

`GET users`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| start_cursor | query | — | 分页游标 |
| page_size | query | — | 每页数量（默认 100） |

```bash
curl -s "https://api.notion.com/v1/users" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

---

### 页面操作（#4-#10）

#### 4. 创建页面

`POST pages`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| parent | body | ✅ | 父级对象（`{database_id}` 或 `{page_id}`） |
| properties | body | ✅ | 页面属性 |
| children | body | — | 页面内容 Block 数组 |
| icon | body | — | 页面图标 |
| cover | body | — | 页面封面 |

```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "DATABASE_ID"},
    "properties": {
      "Name": {"title": [{"text": {"content": "新页面标题"}}]}
    }
  }'
```

#### 5. 获取页面

`GET pages/{page_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| page_id | path | ✅ | 页面 ID |
| filter_properties | query | — | 只返回指定属性（属性 ID 数组） |

```bash
curl -s "https://api.notion.com/v1/pages/PAGE_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 6. 更新页面

`PATCH pages/{page_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| page_id | path | ✅ | 页面 ID |
| properties | body | — | 要更新的属性 |
| archived | body | — | 是否归档 |
| icon | body | — | 页面图标 |
| cover | body | — | 页面封面 |

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/PAGE_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "Name": {"title": [{"text": {"content": "更新后的标题"}}]}
    }
  }'
```

#### 7. 移动页面

`POST pages/{page_id}/move`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| page_id | path | ✅ | 页面 ID |
| new_parent | body | ✅ | 新父级（`{database_id}` 或 `{page_id}`） |
| after | body | — | 排序位置（Block ID） |

```bash
curl -s -X POST "https://api.notion.com/v1/pages/PAGE_ID/move" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"new_parent": {"page_id": "TARGET_PAGE_ID"}}'
```

#### 8. 获取页面属性

`GET pages/{page_id}/properties/{property_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| page_id | path | ✅ | 页面 ID |
| property_id | path | ✅ | 属性 ID |
| start_cursor | query | — | 分页游标 |
| page_size | query | — | 每页数量 |

```bash
curl -s "https://api.notion.com/v1/pages/PAGE_ID/properties/PROPERTY_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 9. 获取页面 Markdown

`GET pages/{page_id}/markdown`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| page_id | path | ✅ | 页面 ID |

```bash
curl -s "https://api.notion.com/v1/pages/PAGE_ID/markdown" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 10. 更新页面 Markdown ⚠️ DESTRUCTIVE

`PATCH pages/{page_id}/markdown` — 覆盖整个页面内容

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| page_id | path | ✅ | 页面 ID |
| markdown | body | ✅ | Markdown 内容（覆盖现有内容） |

```bash
curl -s -X PATCH "https://api.notion.com/v1/pages/PAGE_ID/markdown" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# 标题\n\n这是更新后的内容"}'
```

---

### 数据库操作（#11-#13）

#### 11. 获取数据库

`GET databases/{database_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| database_id | path | ✅ | 数据库 ID |

```bash
curl -s "https://api.notion.com/v1/databases/DATABASE_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 12. 创建数据库

`POST databases`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| parent | body | ✅ | 父级（`{page_id}`） |
| title | body | ✅ | 数据库标题（rich_text 数组） |
| properties | body | ✅ | 属性 schema 定义 |
| is_inline | body | — | 是否内联数据库 |

```bash
curl -s -X POST "https://api.notion.com/v1/databases" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "PAGE_ID"},
    "title": [{"text": {"content": "新数据库"}}],
    "properties": {
      "Name": {"title": {}},
      "Tags": {"multi_select": {"options": [{"name": "标签1"}]}}
    }
  }'
```

#### 13. 更新数据库

`PATCH databases/{database_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| database_id | path | ✅ | 数据库 ID |
| title | body | — | 数据库标题 |
| properties | body | — | 更新属性 schema |
| description | body | — | 数据库描述 |

```bash
curl -s -X PATCH "https://api.notion.com/v1/databases/DATABASE_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "title": [{"text": {"content": "更新后的数据库名"}}],
    "description": [{"text": {"content": "数据库描述"}}]
  }'
```

---

### Block 操作（#19-#23）

#### 19. 获取 Block

`GET blocks/{block_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| block_id | path | ✅ | Block ID |

```bash
curl -s "https://api.notion.com/v1/blocks/BLOCK_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 20. 更新 Block

`PATCH blocks/{block_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| block_id | path | ✅ | Block ID |
| {type} | body | ✅ | 按 Block 类型提供对应字段 |
| archived | body | — | 是否归档 |

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/BLOCK_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "paragraph": {
      "rich_text": [{"text": {"content": "更新后的段落内容"}}]
    }
  }'
```

#### 21. 删除 Block ⚠️ DESTRUCTIVE

`DELETE blocks/{block_id}` — 不可逆操作

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| block_id | path | ✅ | Block ID |

```bash
curl -s -X DELETE "https://api.notion.com/v1/blocks/BLOCK_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 22. 列出子 Block

`GET blocks/{block_id}/children`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| block_id | path | ✅ | Block ID |
| start_cursor | query | — | 分页游标 |
| page_size | query | — | 每页数量（默认 100） |

```bash
curl -s "https://api.notion.com/v1/blocks/BLOCK_ID/children?page_size=100" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 23. 追加子 Block

`PATCH blocks/{block_id}/children`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| block_id | path | ✅ | Block ID |
| children | body | ✅ | Block 对象数组 |
| after | body | — | 插入位置（Block ID） |

```bash
curl -s -X PATCH "https://api.notion.com/v1/blocks/BLOCK_ID/children" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "children": [
      {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
          "rich_text": [{"type": "text", "text": {"content": "新段落内容"}}]
        }
      }
    ]
  }'
```

---

### 评论操作（#24-#26）

#### 24. 创建评论

`POST comments`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| parent | body | ✅ | `{page_id}` 或 `{discussion_id}` |
| rich_text | body | ✅ | 评论内容（rich_text 数组） |

```bash
curl -s -X POST "https://api.notion.com/v1/comments" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "PAGE_ID"},
    "rich_text": [{"text": {"content": "这是一条评论"}}]
  }'
```

#### 25. 列出评论

`GET comments`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| block_id | query | ✅ | 要查询评论的 Block/Page ID |
| start_cursor | query | — | 分页游标 |
| page_size | query | — | 每页数量 |

```bash
curl -s "https://api.notion.com/v1/comments?block_id=BLOCK_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 26. 获取评论

`GET comments/{comment_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| comment_id | path | ✅ | 评论 ID |

```bash
curl -s "https://api.notion.com/v1/comments/COMMENT_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

---

### 搜索（#40）

#### 40. 搜索

`POST search`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| query | body | — | 搜索关键词 |
| filter | body | — | 过滤条件：`{value: "page"/"database", property: "object"}` |
| sort | body | — | 排序：`{direction: "ascending"/"descending", timestamp: "last_edited_time"}` |
| start_cursor | body | — | 分页游标 |
| page_size | body | — | 每页数量（默认 100） |

```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"query": "关键词", "page_size": 10}'
```

---

### 文件上传（#27-#31）

> 文件上传分三步：创建上传任务 → 发送文件内容 → 标记完成。另有获取状态和列出任务接口。

#### 27. 创建文件上传

`POST file_uploads`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| mode | body | ✅ | 上传模式：`single_part` 或 `multi_part` |
| filename | body | — | 文件名 |
| content_type | body | — | 文件 MIME 类型 |

```bash
curl -s -X POST "https://api.notion.com/v1/file_uploads" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"mode": "single_part", "filename": "report.pdf", "content_type": "application/pdf"}'
```

#### 28. 发送文件内容

`POST file_uploads/{file_upload_id}/send` — 使用 `multipart/form-data`，非 JSON

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| file_upload_id | path | ✅ | 文件上传任务 ID |
| file | form-data | ✅ | 文件内容 |
| part_number | form-data | — | 分片编号（`multi_part` 模式使用） |

> **注意**：PowerShell 的 `irm` 不支持 multipart，需改用 `curl.exe`（见 §6.1）。

```bash
curl -s -X POST "https://api.notion.com/v1/file_uploads/FILE_UPLOAD_ID/send" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -F "file=@/本地文件路径"
```

#### 29. 完成文件上传

`POST file_uploads/{file_upload_id}/complete`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| file_upload_id | path | ✅ | 文件上传任务 ID |

```bash
curl -s -X POST "https://api.notion.com/v1/file_uploads/FILE_UPLOAD_ID/complete" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 30. 获取文件上传

`GET file_uploads/{file_upload_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| file_upload_id | path | ✅ | 文件上传任务 ID |

```bash
curl -s "https://api.notion.com/v1/file_uploads/FILE_UPLOAD_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 31. 列出文件上传

`GET file_uploads`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| start_cursor | query | — | 分页游标 |
| page_size | query | — | 每页数量 |

```bash
curl -s "https://api.notion.com/v1/file_uploads?page_size=20" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

---

### 数据源操作（#14-#18）

#### 14. 获取数据源

`GET data_sources/{data_source_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| data_source_id | path | ✅ | 数据源 ID |

```bash
curl -s "https://api.notion.com/v1/data_sources/DATA_SOURCE_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 15. 查询数据源

`POST data_sources/{data_source_id}/query`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| data_source_id | path | ✅ | 数据源 ID |
| filter | body | — | 过滤条件 |
| sorts | body | — | 排序规则 |
| start_cursor | body | — | 分页游标 |
| page_size | body | — | 每页数量 |

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources/DATA_SOURCE_ID/query" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 100}'
```

#### 16. 创建数据源

`POST data_sources`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| parent | body | ✅ | 父级对象（`{page_id}`） |
| title | body | ✅ | 数据源标题（rich_text 数组） |
| properties | body | ✅ | 属性 schema 定义 |

```bash
curl -s -X POST "https://api.notion.com/v1/data_sources" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"page_id": "PAGE_ID"},
    "title": [{"text": {"content": "新数据源"}}],
    "properties": {
      "Name": {"title": {}},
      "Status": {"select": {"options": [{"name": "进行中"}]}}
    }
  }'
```

#### 17. 更新数据源

`PATCH data_sources/{data_source_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| data_source_id | path | ✅ | 数据源 ID |
| title | body | — | 数据源标题 |
| properties | body | — | 更新属性 schema |

```bash
curl -s -X PATCH "https://api.notion.com/v1/data_sources/DATA_SOURCE_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "title": [{"text": {"content": "更新后的数据源名"}}]
  }'
```

#### 18. 列出数据源模板

`GET data_sources/{data_source_id}/templates`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| data_source_id | path | ✅ | 数据源 ID |
| start_cursor | query | — | 分页游标 |
| page_size | query | — | 每页数量 |

```bash
curl -s "https://api.notion.com/v1/data_sources/DATA_SOURCE_ID/templates?page_size=50" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

---

### 自定义 Emoji（#41）

#### 41. 列出自定义 Emoji

`GET custom_emojis`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| start_cursor | query | — | 分页游标 |
| page_size | query | — | 每页数量 |

```bash
curl -s "https://api.notion.com/v1/custom_emojis" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

---

### 视图操作（#32-#39）

#### 32. 创建视图

`POST views`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| data_source_id | body | ✅ | 关联的数据源 ID |
| name | body | ✅ | 视图名称 |
| type | body | ✅ | 视图类型（如 `table`、`board` 等） |
| filter | body | — | 过滤条件 |
| sorts | body | — | 排序规则 |
| configuration | body | — | 视图配置 |

```bash
curl -s -X POST "https://api.notion.com/v1/views" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "data_source_id": "DATA_SOURCE_ID",
    "name": "新视图",
    "type": "table"
  }'
```

#### 33. 获取视图

`GET views/{view_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| view_id | path | ✅ | 视图 ID |

```bash
curl -s "https://api.notion.com/v1/views/VIEW_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 34. 更新视图

`PATCH views/{view_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| view_id | path | ✅ | 视图 ID |
| name | body | — | 视图名称 |
| filter | body | — | 过滤条件 |
| sorts | body | — | 排序规则 |
| configuration | body | — | 视图配置 |

```bash
curl -s -X PATCH "https://api.notion.com/v1/views/VIEW_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"name": "更新后的视图名称"}'
```

#### 35. 删除视图 ⚠️ DESTRUCTIVE

`DELETE views/{view_id}` — 不可逆操作

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| view_id | path | ✅ | 视图 ID |

```bash
curl -s -X DELETE "https://api.notion.com/v1/views/VIEW_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 36. 列出数据库视图

`GET views`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| data_source_id | query | ✅ | 数据源 ID |
| start_cursor | query | — | 分页游标 |
| page_size | query | — | 每页数量 |

```bash
curl -s "https://api.notion.com/v1/views?data_source_id=DATA_SOURCE_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 37. 创建视图查询

`POST views/{view_id}/queries`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| view_id | path | ✅ | 视图 ID |
| page_size | body | — | 每页数量 |

```bash
curl -s -X POST "https://api.notion.com/v1/views/VIEW_ID/queries" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{"page_size": 50}'
```

#### 38. 获取视图查询结果

`GET views/{view_id}/queries/{view_query_id}`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| view_id | path | ✅ | 视图 ID |
| view_query_id | path | ✅ | 视图查询 ID |

```bash
curl -s "https://api.notion.com/v1/views/VIEW_ID/queries/VIEW_QUERY_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

#### 39. 删除视图查询 ⚠️ DESTRUCTIVE

`DELETE views/{view_id}/queries/{view_query_id}` — 不可逆操作

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| view_id | path | ✅ | 视图 ID |
| view_query_id | path | ✅ | 视图查询 ID |

```bash
curl -s -X DELETE "https://api.notion.com/v1/views/VIEW_ID/queries/VIEW_QUERY_ID" \
  -H "Authorization: Bearer $(bash '<SCRIPT_PATH>/get-token.sh')" \
  -H "Notion-Version: 2025-09-03"
```

---

### OAuth 认证（#42-#44）

> **重要**：OAuth 接口使用 Basic Auth（`-u "CLIENT_ID:CLIENT_SECRET"`），**不使用** Bearer Token。这与其他所有接口的认证方式不同。

#### 42. 获取 Token

`POST oauth/token`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| grant_type | body | ✅ | 授权类型（`authorization_code`） |
| code | body | ✅ | 授权码（authorization_code 模式必填） |
| redirect_uri | body | ✅ | 回调地址 |
| external_account | body | — | 外部账户信息 |

```bash
curl -s -X POST "https://api.notion.com/v1/oauth/token" \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "authorization_code",
    "code": "AUTH_CODE",
    "redirect_uri": "REDIRECT_URI"
  }'
```

#### 43. Token 自省

`POST oauth/introspect`

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| token | body | ✅ | 要检查的 access_token |

```bash
curl -s -X POST "https://api.notion.com/v1/oauth/introspect" \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"token": "ACCESS_TOKEN"}'
```

#### 44. 吊销 Token ⚠️ DESTRUCTIVE

`POST oauth/revoke` — 吊销后 Token 立即失效，不可恢复

| 参数 | 位置 | 必填 | 说明 |
|------|------|------|------|
| token | body | ✅ | 要吊销的 access_token |

```bash
curl -s -X POST "https://api.notion.com/v1/oauth/revoke" \
  -u "CLIENT_ID:CLIENT_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"token": "ACCESS_TOKEN"}'
```

---

## §8 SDK 代码调用示例（Node.js）

### 初始化客户端

```javascript
const { Client } = require("@notionhq/client")

const notion = new Client({ auth: process.env.NOTION_TOKEN })
```

### 常用操作

```javascript
// 搜索
const results = await notion.search({ query: "关键词" })

// 获取页面
const page = await notion.pages.retrieve({ page_id: "PAGE_ID" })

// 创建页面
const newPage = await notion.pages.create({
  parent: { database_id: "DATABASE_ID" },
  properties: {
    Name: { title: [{ text: { content: "新页面" } }] },
  },
})

// 获取页面 Markdown
const md = await notion.pages.retrieveMarkdown({ page_id: "PAGE_ID" })

// 查询数据源
const data = await notion.dataSources.query({
  data_source_id: "DATA_SOURCE_ID",
})

// 列出子 Block
const blocks = await notion.blocks.children.list({
  block_id: "PAGE_ID",
})

// 追加内容
await notion.blocks.children.append({
  block_id: "PAGE_ID",
  children: [
    {
      paragraph: {
        rich_text: [{ text: { content: "新段落" } }],
      },
    },
  ],
})

// 分页遍历（内存友好）
const { iteratePaginatedAPI } = require("@notionhq/client")
for await (const block of iteratePaginatedAPI(
  notion.blocks.children.list,
  { block_id: "PAGE_ID" }
)) {
  console.log(block)
}

// 文件上传
const upload = await notion.fileUploads.create({ mode: "single_part" })
await notion.fileUploads.send({
  file_upload_id: upload.id,
  file: fs.createReadStream("./file.pdf"),
})
await notion.fileUploads.complete({ file_upload_id: upload.id })

// 更新页面属性
await notion.pages.update({
  page_id: "PAGE_ID",
  properties: {
    Status: { select: { name: "已完成" } },
  },
})

// 归档页面
await notion.pages.update({
  page_id: "PAGE_ID",
  archived: true,
})

// 查询数据源（带过滤和排序）
const queryResults = await notion.dataSources.query({
  data_source_id: "DATA_SOURCE_ID",
  filter: {
    property: "Status",
    select: { equals: "进行中" },
  },
  sorts: [{ property: "Created", direction: "descending" }],
  page_size: 50,
})
```

### 错误处理

```javascript
const { isNotionClientError, APIErrorCode } = require("@notionhq/client")

try {
  const page = await notion.pages.retrieve({ page_id: "PAGE_ID" })
} catch (error) {
  if (isNotionClientError(error)) {
    switch (error.code) {
      case APIErrorCode.ObjectNotFound:
        console.error("页面不存在或无权访问")
        break
      case APIErrorCode.RateLimited:
        console.error("请求频率过高，请稍后重试")
        break
      default:
        console.error("Notion API 错误:", error.message)
    }
  }
}
```

---

## §9 运维契约

### 9.1 HTTP 错误→AI 行为映射表

收到 API 错误时，AI 必须按以下表格执行对应行为：

| HTTP 状态码 | 错误码 | AI 行为 |
|------------|--------|---------|
| 400 | `invalid_json` | 检查请求体 JSON 语法（缺少逗号、引号未闭合等），修正后重试 |
| 400 | `invalid_request` | 检查请求 URL 和必填参数是否正确，对照 §7 参数表修正 |
| 400 | `validation_error` | 检查属性值类型是否匹配 schema（如 title 需要 rich_text 数组），修正后重试 |
| 401 | `unauthorized` | 提示用户检查 Token 是否有效或已过期；**绝不在输出中显示 Token 值** |
| 403 | `restricted_resource` | 告知用户：该集成未被授权访问此资源。引导用户在 Notion 中将集成添加到目标页面 |
| 404 | `object_not_found` | 验证 ID 是否正确（32 位 hex）；检查集成是否有权访问该对象；提示用户确认对象是否存在 |
| 409 | `conflict_error` | 存在并发修改冲突，等待 1-2 秒后重试；若持续冲突，报告用户 |
| 429 | `rate_limited` | 执行限流处理算法（见 §9.3）；**所有 HTTP 方法均可重试** |
| 500 | `internal_server_error` | 仅对幂等方法（GET/DELETE）自动重试；POST/PATCH 报告错误，由用户决定是否重试 |
| 503 | `service_unavailable` | 同 500 处理策略：幂等方法自动重试，非幂等方法报告错误 |

### 9.2 分页契约（算法）

所有返回 `has_more` 的列表接口必须遵循以下分页算法：

```
FUNCTION paginate(endpoint, params):
  all_results = []
  cursor = null

  LOOP:
    IF cursor != null THEN
      params.start_cursor = cursor
    END IF

    response = CALL endpoint(params)
    all_results.APPEND(response.results)

    IF response.has_more == true THEN
      cursor = response.next_cursor
      GOTO LOOP
    ELSE
      RETURN all_results
    END IF
```

**分页规则（强制）：**
1. **禁止将部分结果当作完整结果呈现给用户** — 若 `has_more == true`，必须继续翻页或明确告知用户"还有更多数据"
2. 翻页完成后，告知用户"已获取全部 N 条结果"
3. `page_size` 默认 100，最大 100
4. SDK 用户优先使用 `iteratePaginatedAPI()`（流式）或 `collectPaginatedAPI()`（收集全部）

### 9.3 限流处理算法

收到 HTTP 429 时，执行以下算法：

```
FUNCTION handle_rate_limit(response, attempt):
  IF attempt > MAX_RETRIES(2) THEN
    FAIL "超过最大重试次数，请稍后再试"
  END IF

  IF response.headers["retry-after"] EXISTS THEN
    wait_seconds = MIN(response.headers["retry-after"], 60)
  ELSE
    wait_seconds = MIN(1 * 2^attempt + random(0, 1), 60)
  END IF

  SLEEP(wait_seconds)
  RETRY request
```

**说明：**
- `MAX_RETRIES` 默认为 2（即最多重试 2 次，共 3 次请求）
- 优先使用 `retry-after` Header 指定的等待时间
- 无 `retry-after` 时使用指数退避 + 随机抖动（避免惊群效应）
- 等待时间上限 60 秒
- 429 对所有 HTTP 方法均可安全重试（服务端明确要求客户端重试）

### 9.4 通用约定

1. **Token 传递**：仅通过 `Authorization: Bearer <token>` Header 传递，不支持 query 参数
2. **API 版本**：所有请求必须附带 `Notion-Version: 2025-09-03` Header
3. **Base URL**：`https://api.notion.com/v1/`
4. **Content-Type**：POST/PATCH 请求体为 JSON（`application/json`）；文件上传为 `multipart/form-data`
5. **ID 格式**：32 位 hex 字符串，带或不带连字符均可（`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` 或 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`）
6. **OAuth 特殊认证**：`oauth/token`、`oauth/introspect`、`oauth/revoke` 使用 Basic Auth（`-u "client_id:client_secret"`），不使用 Bearer Token
7. **PowerShell 注意**：`irm` 是 `Invoke-RestMethod` 别名；文件上传需用 `curl.exe`；续行符为反引号 `` ` `` 而非 `\`

---

## §10 UTF-8 编码要求

### ⚠️ UTF-8 编码强制要求（CRITICAL）

> **此规则为强制性要求，不可跳过。** 非法编码会导致内容在 Notion 中显示为乱码，且无法修复，必须重新写入。

**每次调用写入类 API（创建/更新页面、更新 Markdown、追加 Block、创建评论、创建/更新数据库等 POST/PATCH 请求）之前，必须对 `title`、`content`、`rich_text` 等所有字符串字段执行 UTF-8 编码校验/转换。** 无论内容来源如何——用户直接输入、从文件读取、WebFetch 抓取、剪贴板粘贴、外部 API 返回——都不能假设已经是合法 UTF-8，必须显式确认。

#### 强制检查清单（写入前）

在构造写入请求的 body **之前**，完成以下步骤：

1. **来自文件的内容**：先检测文件编码，转为 UTF-8 后再读入变量
2. **来自 WebFetch / HTTP 请求的内容**：响应可能为 GBK/Latin-1 等，必须转码
3. **来自用户输入或变量拼接的内容**：清洗非法 UTF-8 字节（`\xff\xfe` 等）
4. **标题字段同理**：`title`、`name` 等也必须为合法 UTF-8

#### 各环境转码方法

**Python（推荐，几乎所有环境都有）：**

```bash
# 读取文件，自动检测编码并转为 UTF-8
content=$(python3 -c "
import sys
data = open('tmpfile', 'rb').read()
for enc in ['utf-8', 'gbk', 'gb2312', 'big5', 'latin-1']:
    try:
        sys.stdout.write(data.decode(enc))
        break
    except (UnicodeDecodeError, LookupError):
        continue
" 2>/dev/null)

# 如果内容已在变量中，清洗非法 UTF-8 字节
content=$(printf '%s' "$content" | python3 -c "import sys; sys.stdout.write(sys.stdin.buffer.read().decode('utf-8','ignore'))")
```

**Node.js：**

```bash
content=$(node -e "const fs=require('fs');const buf=fs.readFileSync('tmpfile');process.stdout.write(buf.toString('utf8'))")
# 已知编码（如 GBK）：
content=$(node -e "const fs=require('fs');process.stdout.write(new TextDecoder('gbk').decode(fs.readFileSync('tmpfile')))")
```

**Unix (macOS/Linux)：**

```bash
content=$(iconv -f "$(file -b --mime-encoding tmpfile)" -t UTF-8 tmpfile 2>/dev/null || cat tmpfile)
```

**Windows PowerShell：**

```powershell
# 读取非 UTF-8 文件并转码
$content = [System.IO.File]::ReadAllText('tmpfile', [System.Text.Encoding]::Default)
[System.IO.File]::WriteAllText('tmpfile.utf8', $content, [System.Text.Encoding]::UTF8)
```

### ⚠️ PowerShell 5.1 环境检测（CRITICAL）

> **此问题极其隐蔽：PowerShell 5.1 下 `Invoke-RestMethod` 会静默将请求 Body 从 UTF-8 转为系统 ANSI 编码（中文 Windows 为 GBK），即使设置了 `Content-Type: charset=utf-8` 也无效。结果是请求看起来发送成功，但服务端收到的内容已经是乱码，且无任何错误提示。**

**当 agent 运行在 PowerShell 环境时，必须在首次 API 调用前检测版本：**

```powershell
# 检测 PowerShell 版本 — 在任何 API 调用之前执行
if ($PSVersionTable.PSVersion.Major -le 5) {
    Write-Host "⚠️ 检测到 PowerShell 5.1，将使用 UTF-8 字节数组模式发送请求"
    $useUtf8Bytes = $true
} else {
    Write-Host "✅ PowerShell 7+，默认 UTF-8，无需额外处理"
    $useUtf8Bytes = $false
}
```

**PowerShell 5.1 下必须使用以下方式发送请求**（显式转为 UTF-8 字节数组）：

```powershell
# PowerShell 5.1 安全请求模板
$token = & "<SCRIPT_PATH>\get-token.ps1"
$body = @{
    parent = @{ database_id = "DATABASE_ID" }
    properties = @{ Name = @{ title = @(@{ text = @{ content = "标题" } }) } }
} | ConvertTo-Json -Depth 10

if ($useUtf8Bytes) {
    # CRITICAL: 必须转为字节数组，否则中文/非ASCII内容会变成乱码
    $utf8Bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
    irm "https://api.notion.com/v1/pages" -Method Post `
        -Headers @{"Authorization"="Bearer $token"; "Notion-Version"="2025-09-03"} `
        -ContentType "application/json; charset=utf-8" -Body $utf8Bytes
} else {
    # PowerShell 7+ 可直接传字符串
    irm "https://api.notion.com/v1/pages" -Method Post `
        -Headers @{"Authorization"="Bearer $token"; "Notion-Version"="2025-09-03"} `
        -ContentType "application/json" -Body $body
}
```

> **总结：** 在 PowerShell 5.1 环境中，**所有**包含中文/非 ASCII 内容的 API 调用都必须将 Body 显式转为 UTF-8 字节数组。不检测版本直接发请求 = 中文内容必乱码。这是 PowerShell 5.1 的已知设计缺陷，不是 bug 可以被修复。
