# 📋 腾讯问卷 MCP Skill

[腾讯问卷](https://wj.qq.com) 的 MCP（Model Context Protocol）技能包，让 AI 助手能够直接操作腾讯问卷平台，支持问卷的查询、创建、编辑与回答查看。

## ✨ 功能特性

- **获取问卷详情** — 查看问卷的完整结构（标题、设置、页面、题目、选项 + 纯文本 DSL）
- **创建问卷** — 使用纯文本快速创建问卷，支持调查、考试、测评、投票等场景
- **更新题目** — 修改问卷中的单个题目内容
- **查看回答** — 获取问卷回答列表，支持游标分页

## 📦 项目结构

```
mcp-skill/
├── SKILL.md              # Skill 定义文件（AI Agent 加载入口）
├── setup.sh              # 自动化配置与授权脚本
├── references/           # 工具参考文档
│   ├── auth.md           # 鉴权流程说明
│   ├── get_survey.md     # get_survey 工具参考
│   ├── create_survey.md  # create_survey 工具参考
│   ├── update_question.md# update_question 工具参考
│   └── list_answers.md   # list_answers 工具参考
└── README.md
```

## 🚀 快速开始

### 前置依赖

- [Node.js](https://nodejs.org)（用于安装 mcporter）
- [mcporter](https://www.npmjs.com/package/mcporter) — MCP 服务管理工具
- [jq](https://jqlang.github.io/jq/)（用于 JSON 解析）

```bash
npm install -g mcporter
```

### 配置授权

运行交互式配置向导：

```bash
bash ./setup.sh setup
```

脚本会自动引导你完成以下步骤：

1. 检查并安装 mcporter
2. 生成授权链接
3. 等待你在浏览器中完成 QQ / 微信 扫码授权
4. 自动将 Token 写入 mcporter 配置

> 💡 也可以手动获取 Token：访问 [https://wj.qq.com/claw](https://wj.qq.com/claw) 登录后创建 Token（`wjpt_` 前缀），然后执行：
>
> ```bash
> mcporter config add tencent-survey "https://wj.qq.com/api/v2/mcp" \
>     --header "Authorization=Bearer <your_token>" \
>     --transport http \
>     --scope home
> ```

### 验证配置

```bash
mcporter list tencent-survey
```

## 🔧 工具列表

| 工具 | 说明 | 参考文档 |
|------|------|---------|
| `get_survey` | 获取问卷详情（标题、页面、题目、选项 + DSL） | [get_survey.md](references/get_survey.md) |
| `create_survey` | 使用纯文本创建问卷 | [create_survey.md](references/create_survey.md) |
| `update_question` | 更新问卷中的单个题目 | [update_question.md](references/update_question.md) |
| `list_answers` | 获取问卷回答列表（游标分页） | [list_answers.md](references/list_answers.md) |

### 调用示例

```bash
# 获取问卷详情
mcporter call tencent-survey.get_survey --args '{"survey_id": 12345}'

# 创建调查问卷
mcporter call tencent-survey.create_survey --args '{"text": "员工满意度调查\n\n1. 您对工作环境是否满意？[单选题]\n非常满意\n满意\n一般\n不满意"}'

# 创建投票（scene=8）
mcporter call tencent-survey.create_survey --args '{"scene": 8, "text": "年度最佳员工投票\n\n1. 请选择您心目中的最佳员工[单选题]\n张三\n李四\n王五"}'

# 更新题目（需先通过 get_survey 获取 question_id）
mcporter call tencent-survey.update_question --args '{"survey_id": 12345, "question_id": "q-1-abcd1234", "text": "您的性别[单选题]\n男\n女\n其他"}'

# 获取问卷回答
mcporter call tencent-survey.list_answers --args '{"survey_id": 12345}'
```

## 📝 问卷场景

| scene | 场景 | 说明 |
|-------|------|------|
| 1 | 调查 | 默认值，通用问卷调查 |
| 3 | 考试 | 带评分的考试问卷 |
| 6 | 测评 | 测评类问卷 |
| 8 | 投票 | 投票类问卷 |

## 📐 数据模型

```
问卷（Survey）
├── 基本信息：id, hash, title, scene, state
├── 设置：prefix(欢迎语), suffix(结束语), started_at, end_at ...
├── 项目：project { id, name }
├── 纯文本内容：text（DSL 格式）
├── 页面列表（Pages[]）
│   └── 题目列表（Questions[]）
│       ├── 基本属性：id, type, sub_type, title, required
│       ├── 选项列表（Options[]）：id, text, exclusive
│       ├── 量表属性：starBeginNum, starNum
│       ├── 矩阵子问题：subTitles[]
│       └── 联动层级：levels[], groups[]
└── 回答列表（Answers[]）← 通过 list_answers 获取
    ├── 基本信息：answer_id, respondent_nickname, started_at, ended_at
    ├── 地理信息：country, province, city
    └── 回答内容（answer[]）
        └── 页面 → 题目回答 { id, type, text, options, blanks, groups }
```

## 🔗 URL 解析

问卷投放链接格式：`https://wj.qq.com/s2/{survey_id}/{hash}`

从链接中提取 `survey_id`（路径第二段），即可调用 `get_survey` 获取问卷详情。

## 🤖 AI Agent 集成

本 Skill 支持两种调用方式：

1. **MCP 原生调用** — AI Agent 通过 MCP 协议直接连接 `tencent-survey` 服务，使用 `mcp.json` 配置
2. **mcporter CLI 调用** — 通过终端执行 `mcporter call tencent-survey.<tool_name> --args '{...}'`

### Agent 鉴权流程

在会话首次调用工具前，执行鉴权检查：

```bash
# 第一步：检查状态（立即返回）
bash ./setup.sh wj_check_and_start_auth
# 输出 READY → 直接使用
# 输出 AUTH_REQUIRED:<url> → 展示链接给用户，然后执行第二步

# 第二步：等待授权完成（仅 AUTH_REQUIRED 时执行）
bash ./setup.sh wj_wait_auth
# 输出 TOKEN_READY:* → 授权成功
```

> 鉴权通过后，同一会话内后续调用无需重复检查。

## ❓ 常见问题

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| `missing_token` | 未携带 Token | 检查 Authorization Header |
| `invalid_token` | Token 不存在或已撤销 | 重新授权获取 Token |
| `token expired` | Token 已过期 | 重新执行授权流程 |
| `claim_error` | 问卷不属于当前团队 | 确认问卷 ID 与 Token 绑定的团队一致 |
| `invalid_text_format` | 文本格式错误 | 检查 DSL 语法 |
| `survey_not_editable` | 问卷不可编辑 | 问卷可能在回收中，需先暂停 |

## 📄 许可

腾讯问卷 © [Tencent](https://wj.qq.com)
