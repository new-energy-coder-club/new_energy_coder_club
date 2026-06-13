# wecom-weisheng-scrm

面向 AI 代理的微盛企微管家 SCRM Skill 插件，提供与微盛企微管家开放平台（`https://open.wshoto.com`）的集成能力。本仓库不包含业务逻辑实现，而是通过动态接口发现和通用代理调用机制，将 AI 代理与企微管家 SCRM 系统打通，覆盖客户管理、标签、群聊、素材、活码、群发、跟进记录、会话存档、商机、产品库、汇报、抽奖、日程等业务场景。

## 特性

- **零外部依赖** — 仅使用 Python 标准库，无需 `pip install`
- **动态接口发现** — 通过 Claw 模块实时拉取开放平台 API 目录，支持关键词模糊搜索
- **通用代理转发** — 统一通过 `/openapi/claw/proxy/forward` 代理调用所有业务接口
- **角色权限感知** — 自动识别当前用户身份（超管/分管/普通员工），约束数据访问范围
- **写操作保护** — 自动识别写操作（新增、创建、删除、发送等），禁止失败自动重试
- **结构化 JSON 输出** — 所有命令输出标准化 JSON，适合 AI 代理解析

## 仓库结构

```text
wecom-weisheng-scrm/
├── SKILL.md                  # Skill 描述文件，供 openclaw 平台识别
├── install.sh                # 安装/卸载脚本（symlink 到 ~/.openclaw/skills/）
├── references/               # AI 代理执行参考文档
│   ├── agent-runbook.md      # 代理执行手册（流程、权限、错误处理）
│   ├── examples.md           # 用户查询示例与预期输出
│   ├── file-utils.md         # 文件上传/下载说明
│   └── guide.md              # 用户使用指南
├── scripts/                  # Python CLI 实现
│   ├── scrm.py               # 主入口，命令分发
│   ├── api_client.py         # HTTP 客户端（GET/POST/multipart）
│   ├── claw_client.py        # Claw 模块客户端（API 目录 + 代理转发）
│   ├── environment.py        # 环境检查（Python >= 3.9、APP_KEY）
│   ├── file_utils.py         # 图片上传/下载工具
│   ├── get_access_token.py   # Token 管理（获取 + 缓存 + 刷新）
│   ├── identity_manager.py   # 用户身份管理（角色检测 + 缓存）
│   ├── raw_fetcher.py        # 受控远程文档读取（域名白名单）
│   ├── chat_mode.py          # 会话存档模式管理（key/zone）
│   └── utils.py              # 公共工具（异常、日志、JSON 输出、时间处理）
├── .cache/                   # 运行时缓存（Token、API 目录、身份信息）
├── logs/                     # 运行日志
└── README.md
```

## 快速开始

### 1. 安装

```bash
./install.sh install     # 创建 symlink 到 ~/.openclaw/skills/wecom-weisheng-scrm
./install.sh uninstall   # 移除 symlink
```

### 2. 配置环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `SCRM_APP_KEY` | 是 | 企微管家个人访问令牌。获取路径：企业微信 → 工作台 → 企微管家 → 我的 → 我的 APP KEY |
| `SCRM_BASE_URL` | 否 | 覆盖默认地址（默认 `https://open.wshoto.com`） |
| `SCRM_SKIP_SSL_VERIFY` | 否 | 设为 `1` 跳过 SSL 验证（内网环境使用） |
| `SCRM_MEDIA_CATEGORY_ID` | 否 | 素材上传分类 ID |

### 3. 检查运行环境

```bash
python3 scripts/scrm.py check-env
```

### 4. 设置凭证

```bash
python3 scripts/scrm.py set-app-key "your_personal_access_token"
```

### 5. 获取当前身份

```bash
python3 scripts/scrm.py check-identity
```

返回用户角色：超管（`super_user=1`）、分管（`super_user=2`）、普通员工（`super_user=0 或 3`）。

## 命令说明

| 命令 | 说明 |
|------|------|
| `check-env` | 检查运行环境（Python 版本、APP_KEY 配置） |
| `set-app-key <key>` | 持久化写入 APP KEY 到 Shell 配置文件 |
| `check-identity` | 获取当前用户身份与角色 |
| `list-apis --keyword <关键词>` | 按关键词搜索 API 目录（逗号分隔多关键词） |
| `call-api --service-name <服务名> --uri <路径> --biz-params <JSON>` | 通过通用代理调用业务接口 |
| `fetch-raw-doc --url <文档URL>` | 获取远程接口文档原始内容（仅限 `open.wshoto.com` 域名） |
| `upload-image --path <本地路径>` | 上传本地图片，返回公开 URL 和 file_id |
| `set-chat-mode --mode <key\|zone>` | 设置会话存档模式 |

### 使用示例

**搜索接口：**

```bash
python3 scripts/scrm.py list-apis --keyword "客户,标签,群发"
```

**调用接口：**

```bash
python3 scripts/scrm.py call-api \
  --service-name "wshoto-basebiz-service" \
  --uri "/bff/crm/private/h5/customer/list" \
  --biz-params '{"currentIndex":1,"pageSize":10}'
```

**获取文档：**

```bash
python3 scripts/scrm.py fetch-raw-doc \
  --url "https://open.wshoto.com/doc/pages/claw/CLAW_SUMMARY.md"
```

**上传图片：**

```bash
python3 scripts/scrm.py upload-image --path ./poster.png
```

## 工作机制

```
用户提问
  ↓
check-env → 校验环境
  ↓
check-identity → 确定用户角色
  ↓
fetch-raw-doc → 拉取远程接口目录
  ↓
list-apis → 关键词搜索匹配接口
  ↓
fetch-raw-doc → 阅读对应接口文档
  ↓
call-api → 通过代理转发调用业务接口
  ↓
结构化 JSON 返回结果
```

关键约束：

- 每次会话首次触发时必须通过 `fetch-raw-doc` 获取远程接口目录原始内容，再按关键词搜索匹配接口
- 普通员工（`super_user=0/3`）仅可查看个人数据，无法查询团队数据或搜索组织架构
- 写操作（新增、创建、删除、发送等）失败后禁止自动重试，防止重复操作
- 本地图片类输入需先通过 `upload-image` 上传，再将返回的 URL 用于后续业务接口
- 读取接口文档必须使用 `fetch-raw-doc` 命令（受域名白名单约束），不可使用其他工具替代

## 缓存策略

| 缓存文件 | 内容 | TTL |
|----------|------|-----|
| `.cache/access_token.json` | OAuth Token + user_id + 过期时间 | Token 有效期 - 5 分钟 |
| `.cache/api_list.json` | 完整 API 目录（约 44KB） | 2 小时 |
| `.cache/identity.json` | 用户角色信息 | 2 小时 |

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.9+（零外部依赖） |
| HTTP 客户端 | `urllib.request`（标准库） |
| CLI 框架 | `argparse`（标准库） |
| 数据格式 | JSON |
| 日志 | `logging` 模块，输出到 `logs/scrm.log` |
| 目标平台 | 微盛企微管家开放平台 |
| 部署方式 | OpenClaw：symlink 到 `~/.openclaw/skills/`；QClaw：设置 → 技能管理一键启用 |
