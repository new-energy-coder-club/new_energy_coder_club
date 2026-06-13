---
name: tme-openapi
description: 腾讯音乐开放平台（TME OpenAPI）算子平台通用客户端。提供对 `/musician/agent/operator/*` 一系列「算子」API 的发现、查询与调用能力，是所有需要调用 TME OpenAPI 算子的业务 Skill 的**基础依赖**。本 Skill 仅封装**通用的 API 调用与算子发现流程**，不关心任何具体业务语义（例如宣推、歌曲、发行等）。对调用方暴露 4 个通用工具：`list_apis` / `search_apis` / `get_api_detail` / `invoke_api`。**触发时机**：- 上层业务 Skill 需要调用 TME OpenAPI 算子时，作为**被引用的基础能力**加载；- 用户直接提问"列一下可用算子"、"调一下 xxx 算子"、"搜一下宣推相关的 API"等开发调试场景； - 用户提问"登录腾讯音乐人"、"获取登录态"等 —— 本 Skill 已自包含登录能力。**自包含**：登录态 Token 获取能力已**完整内嵌**到本 Skill，无需依赖任何外部 Skill，调用方无需设置任何环境变量。
---

# TME OpenAPI（腾讯音乐开放平台算子客户端）

> **✨ 自包含**：本 Skill 已内嵌完整登录能力，不依赖任何外部 Skill。首次使用会自动弹出浏览器扫码登录，Token 有效期约 30 天，之后日常调用秒级无感。
>
> **⚠️ 定位说明**：本 Skill 是**纯通用能力层**，不包含任何业务语义。业务 Skill（如 `ai-promotion-query`）应当**引用本 Skill**完成 API 发现与调用，自己只负责业务编排、参数组装、结果解读、对外表达规则。

## 是什么

腾讯音乐开放平台后端有一套「算子」体系：

- 每个算子 = 一个可被 Agent 调用的后端 API
- 算子的配置（名称、入参 schema、出参 schema 等）存储在数据库中，**可随时新增和修改**
- 上层 Agent / Skill **不应硬编码任何算子的 operatorCode 或参数结构**，而是通过本 Skill 提供的 4 个工具**动态发现和调用**
- 当前算子平台仅支持**同步调用**——`invoke_api` 直接返回最终结果，无需轮询

本 Skill 封装了算子平台对外的 4 个标准入口：

```
POST /musician/agent/operator/listApis       → list_apis
POST /musician/agent/operator/searchApis     → search_apis
POST /musician/agent/operator/getApiDetail   → get_api_detail
POST /musician/agent/operator/invokeApi      → invoke_api
```

所有接口：
- 域名：`https://y.tencentmusic.com/openapi`（正式环境，已硬编码）
- 方法：POST + JSON Body
- 鉴权：HTTP Header `tme-header-token: <token>`（Skill 内部自动获取，见下方「登录态管理」）
- 响应：统一 `{ success, data, error, meta }` 结构

---

## 登录态管理（内嵌能力）

### Token 获取的自动回退链

所有调用脚本在发起请求前，会通过内部模块 `scripts/_token.py` → `scripts/check_login.py` **自动获取 Token**，四级回退：

```
1. 本地缓存 ~/.tme-login/token.json              ← 秒级，99% 日常场景
       ↓（不存在或为空）
2. 无头 Playwright + ~/.tme-login/storage_state.json 刷新
       ↓（storage_state 失效或缺失）
3. 自动调起 login.py 做有头扫码登录（弹出 Chromium）
       ↓（用户未完成登录）
4. 手动粘贴 Token 兜底
```

每一步成功都会覆盖写入 `token.json`，供后续调用秒级复用。**Token 有效期约 30 天**。

### 双文件缓存

| 文件                                    | 作用                                                              |
| --------------------------------------- | ----------------------------------------------------------------- |
| `~/.tme-login/storage_state.json`       | Playwright 完整存档（cookies + localStorage），由 `login.py` 生成 |
| `~/.tme-login/token.json`               | `tmeHeaderToken` 快照，供 Skill 内部和外部脚本直接读取            |

### Playwright 依赖（🤖 AI 必读：缺失时自动安装，不要把错误丢给用户）

本 Skill 依赖 [Playwright](https://playwright.dev/python/) 驱动 Chromium 完成登录与 Token 刷新。

#### 脚本层已自动处理

`scripts/login.py` 与 `scripts/get_token_from_browser.py` 在运行时会**自动检测 Playwright 是否已安装**，若未安装会**自动在当前 Python 环境下执行安装**（`pip install playwright` + `playwright install chromium`），无需人工干预。正常情况下，AI 和用户都**不需要手动装依赖**，直接调用脚本即可。

#### ⚠️ 强制行为规范（给调用本 Skill 的 AI）

当你（AI）运行本 Skill 的任何脚本，**看到以下任一信号时**：

- 脚本 stderr 出现 `❌ 未检测到 Playwright` / `PLAYWRIGHT_MISSING` / `ModuleNotFoundError: No module named 'playwright'`
- 提示「请安装依赖：pip install playwright && playwright install chromium」
- `check_login.py` 因 `PLAYWRIGHT_MISSING` 走到手动粘贴兜底

**你必须立刻在终端主动执行下面的安装命令，然后重跑原脚本**，而不是把错误提示原样抛给用户、让用户自己去装：

```bash
python3 -m pip install --upgrade playwright
python3 -m playwright install chromium
```

说明：
1. 使用 `python3 -m pip` / `python3 -m playwright`，避免 `pip` / `playwright` 不在 PATH 里导致的误判
2. 若当前处于虚拟环境或 conda 环境，继续在该环境中执行即可，**不要**切换到系统 Python
3. `playwright install chromium` 会下载约 150MB 浏览器二进制，首次耗时 1-2 分钟是正常的
4. 安装完成后**必须重新执行**原本失败的脚本（例如 `python3 scripts/login.py` 或上层的 `check_login.py`），确认流程能走通再向用户汇报
5. **禁止**向用户输出"请你先执行 pip install ..."这类把安装动作甩回给用户的话

> Chromium 约 150MB，仅本 Skill 使用，不影响系统浏览器。

### 登录相关脚本（普通调用方不需要直接用）

| 功能                                      | 脚本                                   | 典型用法                                 |
| ----------------------------------------- | -------------------------------------- | ---------------------------------------- |
| 首次登录 / 扫码登录（有头）               | `scripts/login.py`                     | `python scripts/login.py`                |
| 获取登录态（缓存→无头→扫码 自动回退）     | `scripts/check_login.py`               | `TOKEN=$(python scripts/check_login.py)` |
| 从 storage_state 无头读取 Token（内部）   | `scripts/get_token_from_browser.py`    | 由 `check_login.py` 调用                 |
| 验证指定 Token 是否有效                   | `scripts/verify_token.py`              | `python scripts/verify_token.py <token>` |

### 强制重新登录（Token 过期或失效）

```bash
rm -f ~/.tme-login/storage_state.json ~/.tme-login/token.json
python scripts/login.py
```

---

## 可用 Tools（算子平台调用）

| Tool             | 作用                   | 什么时候用                                 |
| ---------------- | ---------------------- | ------------------------------------------ |
| `list_apis`      | 列出所有可用算子摘要   | 想看全貌，或不确定该搜什么关键词           |
| `search_apis`    | 按关键词模糊搜索算子   | 知道大概要什么能力（如"宣推概览"、"发行"） |
| `get_api_detail` | 获取指定算子的完整详情 | 需要精确了解参数结构再调用                 |
| `invoke_api`     | 调用指定算子           | 参数已准备好，可以执行了                   |

### 脚本一览

| Tool             | 脚本                        | 命令行用法                                                       |
| ---------------- | --------------------------- | ---------------------------------------------------------------- |
| `list_apis`      | `scripts/list_apis.py`      | `python scripts/list_apis.py`                                    |
| `search_apis`    | `scripts/search_apis.py`    | `python scripts/search_apis.py <keyword>`                        |
| `get_api_detail` | `scripts/get_api_detail.py` | `python scripts/get_api_detail.py <operatorCode>`                |
| `invoke_api`     | `scripts/invoke_api.py`     | `python scripts/invoke_api.py <operatorCode> '<arguments_json>'` |

> 这 4 个脚本仅用 Python 3 标准库（`urllib` / `json`），零额外依赖。Token 由内部模块 `_token.py` 自动管理，调用方**无需**传任何参数或设置任何环境变量。

---

## 标准调用流程

```
1. 发现算子
   search_apis({ keyword: "..." })  或  list_apis()
        ↓
2. 判断：search/list 返回的摘要信息够不够组装参数？
   ├── 够了 → 直接到第 3 步
   └── 不够 → get_api_detail({ name: "<operatorCode>" })
        ↓
3. 调用算子（同步）
   invoke_api({ name: "<operatorCode>", arguments: { ... } })
        ↓
4. 直接读取 output，完成
```

> 当前算子平台**仅支持同步调用**，`invoke_api` 一次请求即可拿到最终结果。如未来新增异步算子，会另行在本 Skill 中补回轮询能力，业务 Skill 无需关心。

### 关于 `detailedDescription` 字段

`get_api_detail` 返回的详情中包含一个 `detailedDescription` 字段（Markdown 格式的长文本），是算子作者为该能力撰写的**详细使用说明**，通常包含：

- 该算子具体是什么、适用场景
- 参数的详细含义、约束和取值范围
- 调用注意事项和最佳实践
- 常见错误和处理建议

> **⚠️ 强烈建议**：在首次调用一个不熟悉的算子之前，先通过 `get_api_detail` 获取详情，**仔细阅读 `detailedDescription` 字段的内容**，再组装参数发起调用。这能大幅减少因参数错误导致的调用失败。

### 判断是否需要查 detail 的经验法则

**可以跳过 detail 直接 invoke** — 当以下三个条件同时满足：

1. `search/list` 返回的 `inputSchema` 信息齐全，所有 `required` 参数你都能确定值
2. 参数结构是扁平的（没有嵌套的 object/array），或者嵌套结构你已完全理解
3. 对参数含义没有任何歧义

**必须先查 detail** — 当以下任一条件成立：

1. `inputSchema` 有嵌套 object 或 array，你不确定内部结构
2. 对某个参数的含义、格式、取值范围有疑问
3. 想参考 `exampleInput` / `exampleOutput` 来确认参数怎么组装
4. 想查看 `detailedDescription` 获取该算子的详细使用指南

---

## 参数构造规则

- `arguments` 必须是结构化 JSON 对象（`Map<String, Object>`），严格匹配 `inputSchema`
- 所有 `required` 字段必须提供，少一个都会返回 `INVALID_ARGUMENT`
- 参数类型必须匹配 schema 声明的 type（`string` / `number` / `boolean` / `object` / `array`）
- 可选参数不确定就不传，后端会用默认值
- 登录态下**不要**传 `accountId` / `userId` 等当前用户身份参数，后端会从 Token 中自动识别
- **禁止**把自然语言拼接成字符串塞到 `arguments` 里

---

## 错误处理

所有响应外层结构为 `{ success, data, error, meta }`。当 `success=false` 时，读 `error` 字段：

| error.code         | 含义         | 能重试吗 | 怎么办                                                               |
| ------------------ | ------------ | -------- | -------------------------------------------------------------------- |
| `INVALID_ARGUMENT` | 参数错误     | 否       | 调 `get_api_detail` 重新确认 schema，修正参数再试                    |
| `NOT_FOUND`        | 算子不存在   | 否       | 调 `search_apis` 重新确认 `operatorCode`                             |
| `UNAUTHORIZED`     | 未认证       | 否       | 删除 `~/.tme-login/token.json` 后重跑脚本，本 Skill 会自动触发重新登录 |
| `RATE_LIMITED`     | 限流         | 是       | 等一会儿再试                                                         |
| `TIMEOUT`          | 超时         | 是       | 重试，可设更大 `timeoutMs`                                           |
| `UPSTREAM_ERROR`   | 上游服务异常 | 是       | 重试 1-2 次，仍失败交给上层业务 Skill 处理                           |

> 所有算子当前都是**同步返回**，`invoke_api` 的响应即为最终结果，无 `async=true` 的情况。

**关键策略**：遇到 `INVALID_ARGUMENT` 时，别用同样的参数重试——回退到 `get_api_detail` 查完整 schema 和 example，重新组装参数。

---

## 典型调用示例

### 示例 1：发现 + 调用算子（自动处理登录态）

```bash
# 首次会弹出 Chromium 让你扫码；之后 30 天内秒级复用
python scripts/search_apis.py 宣推概览
python scripts/invoke_api.py 宣推概览 '{"accountId":282250}'
```

### 示例 2：对参数有疑问时先查 detail

```bash
python scripts/get_api_detail.py <operatorCode>
# 查看 detailedDescription / inputSchema / exampleInput / exampleOutput
# 然后再组装 arguments 调用 invoke_api
```

### 示例 3：主动刷新登录态（Token 过期）

```bash
rm -f ~/.tme-login/token.json ~/.tme-login/storage_state.json
python scripts/login.py     # 有头扫码，重新登录
# 之后直接跑任意算子调用即可
```

---

## 给上层业务 Skill 的使用契约

业务 Skill（如 `ai-promotion-query`）引用本 Skill 时，**只需要做 2 件事**：

1. **通过本 Skill 的 4 个算子脚本完成调用**——不要自己写 HTTP 请求，Token 由本 Skill 自动处理
2. **自己负责业务编排**——包括：
   - 业务场景 → 关键词的映射（如"宣推概览"该搜什么词）
   - `operatorCode` 的缓存策略（是否每次都 `search_apis`）
   - 返回结果的业务解读与对外表达

> 业务 Skill **无需**做任何登录态相关的事情，也**无需**引用其他 Skill 来获取 Token——本 Skill 已自包含。

本 Skill **不关心、不干涉**业务语义，只保证"给算子 code 和参数，就能拿到调用结果"这一通用契约。

---

## 环境配置

| 项                  | 值                                                               | 说明                                                                 |
| ------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------- |
| 域名                | `https://y.tencentmusic.com/openapi`                             | 正式环境，已硬编码在所有调用脚本中                                   |
| 鉴权 Header         | `tme-header-token: <token>`                                      | Skill 内部自动获取，Token 有效期约 30 天                             |
| Content-Type        | `application/json`                                               | 所有请求体均为 JSON                                                  |
| 调用脚本依赖        | Python 3 标准库（`urllib` / `json`）                             | 零额外依赖                                                           |
| 登录脚本依赖        | Playwright + Chromium                                            | 脚本内置自动安装；若脚本提示缺失，AI 必须自动执行 `python3 -m pip install playwright && python3 -m playwright install chromium`，不要把安装动作交给用户 |
| 缓存目录            | `~/.tme-login/`                                                  | 存放 `token.json` 和 `storage_state.json`，权限 0600                 |
