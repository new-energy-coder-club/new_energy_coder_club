# HXC ESP A Board — 核心设备仓库 🚀

> HXC 战队 ESP32-S3 主控板（Board A）开发环境搭建、固件烧录、电机调试

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 分支定位

本分支 (`SKill`) 是 **HXC ESP A Board 核心设备维护仓库**，用于：

| 场景 | 说明 |
|------|------|
| 🆕 **新设备环境搭建** | 从零搭建 PlatformIO + ESP32-S3 开发环境 |
| 🔧 **固件开发与调试** | 基于上游模板进行位控/电流/位置控制开发 |
| 🔄 **跨工作区协作** | Vibe Coding 多机调试、代码同步 |
| 📚 **设备文档维护** | 板级使用说明、硬件参数、调试技巧 |
| 🤖 **Claude Skills 托管** | 149 个 Claude Code AI Skills，覆盖飞书/光伏/论文/开发等场景 |

## 📋 目录结构

```
📦 new_energy_coder_club (SKill)
├── 📁 projects/embedded/
│   ├── 📄 HXC_A_Usage_Guide.md              ← 板级开发使用说明（必读）
│   ├── 📁 ESP32_platformio_temple_project/  ← ⬆️ 上游子模块
│   └── 📄 README.md                         ← 嵌入式项目入口
├── 📁 docs/guides/
│   ├── 📄 development-setup.md              ← 新设备环境搭建
│   └── 📄 vibe-coding-debug.md              ← 跨工作区调试工作流
├── 📁 skills/                               ← 🤖 149 个 AI Coding Skills
├── 📁 competitions/                         ← 竞赛项目存档
├── 📁 projects/                             ← 其他项目
├── 📁 shared/                               ← 共享资源
├── 📁 tools/                                ← 开发工具
├── 📁 .kimi/
│   └── 📄 project-instructions.md           ← Kimi CLI 项目配置
├── 📁 .trae/
│   └── 📄 project-instructions.md           ← Trae IDE 项目配置
└── 📁 .atomcode/
    ├── 📄 project-instructions.md           ← AtomCode 项目指令
    └── 📁 skills/                           ← AtomCode 本地 Skill
```

## ⬆️ 上游项目

| 项目 | 链接 | 说明 |
|------|------|------|
| ESP32 PlatformIO 模板 | [CQUPTHXC/ESP32_platformio_temple_project](https://github.com/CQUPTHXC/ESP32_platformio_temple_project) | 作为 git submodule 引用，`projects/embedded/` 下 |
| 社区主仓库 | [new-energy-coder-club](https://github.com/new-energy-coder-club/new_energy_coder_club.git) | 社区同步 |

## 🚀 快速开始

### 克隆仓库

```powershell
git clone -b SKill https://gitee.com/darrenpig/new_energy_coder_club.git
cd new_energy_coder_club
git submodule update --init --recursive
```

### 编译 & 烧录

```powershell
cd projects\embedded\ESP32_platformio_temple_project

# 编译
pio run --environment temple_project

# 烧录（自动检测 COM 口）
pio run --target upload --environment temple_project
```

### 串口调试

```powershell
# 串口监视
pio device monitor -b 115200

# 发送指令（停止电机）
python send_cmd.py "s"
```

### 安装 Claude Skills

```powershell
# 将所有 Skills 复制到 Claude Code skills 目录
cp -r skills/* ~/.claude/skills/
```

## 🛠️ 开发入口速查

| 目标 | 入口 | 推荐文档 |
|------|------|----------|
| 第一次搭建环境 | → [环境搭建指南](docs/guides/development-setup.md) | 前置依赖、安装步骤、验证清单 |
| 快速调试电机 | → [Vibe Coding 调试](docs/guides/vibe-coding-debug.md) | 调试工作流、命令速查、故障处理 |
| 理解板级设计 | → [HXC_A 使用说明](projects/embedded/HXC_A_Usage_Guide.md) | 硬件参数、CAN/串口约定、三类工程用法 |

## 🤖 硬件参数速查

| 参数 | 值 |
|------|-----|
| **MCU** | ESP32-S3 (rev v0.2, N16R8) |
| **Flash / PSRAM** | 16MB / 8MB |
| **CAN TX / RX** | GPIO8 / GPIO18 |
| **串口** | USB CDC (115200, 8N1) |
| **CAN 协议** | TWAI 1Mbps (经典 CAN) |

## 🔌 常用命令

```powershell
pio run --environment temple_project                    # 编译
pio run --target upload --environment temple_project    # 烧录
pio device monitor -b 115200                            # 串口监视
python send_cmd.py "c 0.3"                              # 电流模式 0.3A
python send_cmd.py "p 90"                               # 绝对位置 90°
python send_cmd.py "s"                                  # 停止
```

## 🤖 AI 工具配置

本仓库为多种 AI 编程工具提供项目级配置，开箱即用。

### 🏗️ AtomCode IDE

**配置文件:** [`.atomcode/`](.atomcode/)

| 文件 | 说明 |
|------|------|
| [`project-instructions.md`](.atomcode/project-instructions.md) | AtomCode 项目指令：结构、技能、命令速查 |
| [`skills/hxc-esp-a-board/SKILL.md`](.atomcode/skills/hxc-esp-a-board/SKILL.md) | HXC Board A 开发环境自动化 Skill |

**Skill 功能:** 从零搭建 PlatformIO + ESP32-S3 环境、固件烧录、电机测试。

### 💻 Kimi CLI

**配置文件:** [`.kimi/`](.kimi/)

| 文件 | 说明 |
|------|------|
| [`project-instructions.md`](.kimi/project-instructions.md) | Kimi CLI 项目配置：调用方式、常用场景、模型选择 |

**快速调用：**

```powershell
# 代码任务（kimi-for-coding，推荐）
kimi --print --final-message -m kimi-code/kimi-for-coding -w "." -p "审查 main.cpp"

# 复杂推理（kimi-k2-thinking-turbo）
kimi --print --final-message -m kimi/kimi-k2-thinking-turbo -w "." -p "架构设计"

# 续接上次会话
kimi --print --final-message -C -p "继续分析"
```

**版本要求:** ≥ 1.9.0 | **路径:** `C:/Users/29711/.local/bin/kimi.exe`

### 🧠 Claude Code CLI

**CLI 路径:** `C:/Users/29711/AppData/Roaming/npm/claude.cmd`

```powershell
# 单次任务
claude -p "分析项目结构" --add-dir "."

# 允许工具执行
claude -p "创建测试文件" --permission-mode acceptEdits
```

**Skills 目录:** 本仓库 `skills/` 目录可直接复制到 `~/.claude/skills/` 使用（50 个 Skills）。

### 🖥️ Kimi Code IDE（桌面版）

**安装路径:** `C:/Users/29711/AppData/Local/Programs/kimi-desktop/Kimi.exe`

在 Kimi Code IDE 中打开本目录后，项目自动注册到 `~/.kimi/kimi.json`，CLI 可通过 `--continue` 续接 IDE 会话。

### 🔷 Trae IDE

**配置文件:** [`.trae/`](.trae/)

| 文件 | 说明 |
|------|------|
| [`project-instructions.md`](.trae/project-instructions.md) | Trae IDE 项目指令 |

Trae IDE 支持 Skill 市场（marketplace），已安装 60+ Skills，包括 `lark-*`、`baidu-search`、`pv-storage-bom` 等。

### ⚡ 工具选择指南

| 任务场景 | 推荐工具 | 原因 |
|----------|---------|------|
| 嵌入式 C++ 开发 | Kimi CLI / AtomCode | kimi-for-coding 专长 |
| 飞书办公自动化 | Claude Code / Trae + lark-* skills | Skill 生态完整 |
| 多步骤自动化 | Claude Code | 工具调用 + 文件操作 |
| 硬件调试分析 | AtomCode Skill | 一键环境搭建 |
| 代码审查重构 | Kimi CLI / Claude Code | 按复杂度选择 |
| 文档撰写翻译 | Kimi CLI | 长文本处理优 |
| IDE 内 AI 辅助 | Trae / Kimi Code | 原生 IDE 体验 |

## 🤖 Claude Skills 技能库

本仓库收录了 **149 个** AI Coding Skills，整合自 Claude Code、Trae IDE、QClaw、OpenClaw、Kimi 等平台的本地 Skill 生态。所有 Skill 存放在 [`skills/`](skills/) 目录下。

### 📊 技能分类总览 (149个)

#### 🏢 飞书/Lark 办公套件 (25个)

飞书生态全流程覆盖：通讯录、即时通讯、日历日程、文档、表格、任务、审批、邮件、视频会议、知识库。

| Skill | 说明 | | Skill | 说明 |
|-------|------|-|-------|------|
| lark-shared | CLI 共享基础 | | lark-contact | 通讯录 |
| lark-im | 即时通讯 | | lark-calendar | 日历日程 |
| lark-doc | 云文档 v2 | | lark-sheets | 电子表格 |
| lark-base | 多维表格 | | lark-task | 任务管理 |
| lark-approval | 审批 API | | lark-mail | 邮箱 |
| lark-drive | 云空间 | | lark-wiki | 知识库 |
| lark-minutes | 妙记 | | lark-vc | 视频会议 |
| lark-vc-agent | 会议机器人 | | lark-okr | OKR |
| lark-slides | 幻灯片 | | lark-whiteboard | 画板 |
| lark-markdown | Markdown | | lark-event | 事件订阅 |
| lark-attendance | 考勤打卡 | | lark-openapi-explorer | OpenAPI 探索 |
| lark-skill-maker | 自定义 Skill | | lark-workflow-meeting-summary | 会议纪要工作流 |
| lark-workflow-standup-report | 日程待办摘要 |

#### 🤖 AI CLI 调用器 (6个)

本地 AI CLI 调度能力，实现 Claude ⇄ Kimi ⇄ Gemini ⇄ AI Code With 互调。

| Skill | 说明 |
|-------|------|
| [kimi-cli](skills/kimi-cli/) | 调用本地 Kimi CLI (`kimi-for-coding`, `kimi-k2-thinking-turbo`) |
| [claude-cli](skills/claude-cli/) | 调用本地 Claude Code CLI（工具调用/文件操作） |
| [gemini-cli](skills/gemini-cli/) | 调用本地 Gemini CLI |
| [aicodewith](skills/aicodewith/) | AI Code With 中转服务配置与调用 |
| [trae-assistant](skills/trae-assistant/) | Trae IDE 代理：委托任务到 Trae Desktop |
| [persona-switch](skills/persona-switch/) | AI 角色切换：在不同模型/人格间切换 |

#### 🌐 前端 & 设计开发 (14个)

| Skill | 说明 | | Skill | 说明 |
|-------|------|-|-------|------|
| react-best-practices | React 最佳实践 | | react-native-skills | React Native 开发 |
| shadcn | shadcn/ui 组件 | | frontend-design | 前端设计 |
| frontend-skill | 前端通用 | | web-design-guidelines | Web 设计规范 |
| web-artifacts-builder | Web Artifact 构建 | | webapp-testing | Web 应用测试 |
| canvas-design | Canvas 设计 | | algorithmic-art | 算法艺术 |
| brand-guidelines | 品牌指南 | | theme-factory | 主题工厂 |
| chart-visualization | 图表可视化 | | web-design | Tailwind + CF Pages |

#### 🔧 开发工程 & 工作流 (17个)

| Skill | 说明 | | Skill | 说明 |
|-------|------|-|-------|------|
| clean-code-zh | 代码整洁之道 | | security-best-practices | 安全最佳实践 |
| git-commit | Git 提交规范 | | gh-cli | GitHub CLI |
| github-skill | GitHub 操作 | | test-driven-development | TDD 测试驱动 |
| spec-to-implementation | 规格→实现 | | composition-patterns | 组合模式 |
| hook-analyzer-skill | Hook 分析 | | screenshot | 截图 |
| writing-plans | 计划编写 | | executing-plans | 计划执行 |
| defuddle | 代码解混淆 | | planning-with-files | Manus 式文件规划 |
| harness | 多会话自治 Agent | | agentic-loop | Agentic Loop 防护 |
| agent-browser | 浏览器自动化 CLI |

#### 🔍 搜索 & 资讯聚合 (8个)

| Skill | 说明 | | Skill | 说明 |
|-------|------|-|-------|------|
| baidu-search | 百度 AI 搜索 | | online-search | 在线搜索 |
| multi-search-engine | 多引擎搜索 | | news | 新闻资讯 |
| news-extractor | 新闻提取 | | news-summary | 新闻摘要 |
| neodata-financial-search | 金融数据搜索 | | tech-news-digest | 技术资讯摘要 |

#### 📄 文档 & 办公文件 (7个)

| Skill | 说明 |
|-------|------|
| [docx](skills/docx/) | Word 文档生成与编辑 |
| [pdf](skills/pdf/) | PDF 文件处理 |
| [pptx](skills/pptx/) | PPT 演示文稿生成 |
| [xlsx](skills/xlsx/) | Excel 电子表格生成 |
| [doc-coauthoring](skills/doc-coauthoring/) | 文档协作撰写 |
| [file-skill](skills/file-skill/) | 通用文件操作 |
| [email-skill](skills/email-skill/) | 邮件操作 |

#### 📡 集成 & 平台连接 (14个)

| Skill | 说明 | | Skill | 说明 |
|-------|------|-|-------|------|
| tencent-docs | 腾讯文档 | | tencent-meeting-mcp | 腾讯会议 MCP |
| tencent-survey | 腾讯问卷 | | tencent-news | 腾讯新闻 |
| wecomcli-setup | 企微 CLI 配置 | | wecom-weisheng-scrm | 企微微盛 SCRM |
| weiyun | 微云 | | youdaonote | 有道笔记 |
| notion | Notion | | ima | 腾讯 IMA |
| kdocs | 金山文档 | | imap-smtp-email | 邮件协议 |
| tme-openapi | TME OpenAPI | | flyai | FlyAI |

#### 🎓 学术 & 论文 (6个)

| Skill | 说明 |
|-------|------|
| [acad-paper-prompter](skills/acad-paper-prompter/) | 学术论文写作助手：润色/翻译/回复信/选刊 |
| [paper-scaffold](skills/paper-scaffold/) | 论文目录标准化 (CIT/国际会议/通用) |
| [latex-win](skills/latex-win/) | Windows LaTeX 编译修复 |
| [cit-thesis-writer](skills/cit-thesis-writer/) | CIT 毕业论文写作 |
| [gradpilot](skills/gradpilot/) | 研究生学业助手 |
| [patent-application-cn](skills/patent-application-cn/) | 中国专利申请撰写 |

#### ☀️ 新能源 & 光伏 (2个)

| Skill | 说明 |
|-------|------|
| [pv-station-rating](skills/pv-station-rating/) | 工商业光伏电站分层分级评分 (A/B/C/D + 十分制) |
| [pv-storage-bom](skills/pv-storage-bom/) | 光伏+储能系统标准产品 BOM 清单 |

#### 🏗️ QClaw/OpenClaw 平台 (15个)

| Skill | 说明 | | Skill | 说明 |
|-------|------|-|-------|------|
| qclaw-cron-skill | 定时任务 | | qclaw-env | 环境管理 |
| qclaw-rules | 规则引擎 | | qclaw-skill-creator | Skill 创建器 |
| qclaw-text-file | 文本文件操作 | | qclaw-openclaw | OpenClaw 集成 |
| self-improving | 自我改进 | | self-improving-agent | 自我改进 Agent |
| session-logs | 会话日志 | | skill-vetter | Skill 审查 |
| public-skill | 公共技能 | | content-factory | 内容工厂 |
| cloud-upload-backup | 云端备份 | | mcporter | MCP 导入导出 |
| mcp-builder | MCP 构建器 |

#### 📊 效率 & 头脑风暴 (9个)

| Skill | 说明 | | Skill | 说明 |
|-------|------|-|-------|------|
| productivity-automation-kit | 效率自动化 | | plan-my-day | 每日计划 |
| study-habits | 学习习惯 | | brainstorming | 头脑风暴 |
| consulting-analysis | 咨询分析 | | report-generator-skill | 报告生成 |
| ai-dev-dashboard | AI 开发面板 | | ai-data-analysis | AI 数据分析 |
| ai-promotion-query | AI 推广查询 |

#### 💬 社交 & 微信生态 (8个)

| Skill | 说明 |
|-------|------|
| [wx-cli-wechat-local-data](skills/wx-cli-wechat-local-data/) | 微信本地数据查询导出 |
| [wechat-cli-export](skills/wechat-cli-export/) | 微信数据 CLI 导出 |
| [nec-wechat-sync](skills/nec-wechat-sync/) | NEC 微信同步 |
| [corporate-deep-query](skills/corporate-deep-query/) | 企业深度查询 |
| [xiaohongshu-images](skills/xiaohongshu-images/) | 小红书 3:4 图文 |
| [xiaohongshu-skills](skills/xiaohongshu-skills/) | 小红书技能集 |
| [kimi-webbridge](skills/kimi-webbridge/) | Kimi 真实浏览器操控 |
| [xbrowser](skills/xbrowser/) | 浏览器扩展 |

#### 🛠️ TRAE 内置 & 其他 (18个)

| Skill | 说明 | | Skill | 说明 |
|-------|------|-|-------|------|
| TRAE-code-review | TRAE 代码审查 | | TRAE-debugger | TRAE 调试器 |
| TRAE-generate-mini-app | TRAE 小程序生成 | | data-analysis | 数据分析 |
| redis-development | Redis 开发 | | find-skills | SkillHub 技能搜索 |
| dogfood | 内部测试 | | aippt | AI PPT 生成 |
| weather-advisor | 天气顾问 | | slack-gif-creator | Slack GIF |
| fbs_bookwriter | FBS 书籍撰写 | | wendao-partner-qclaw-skill | 问道伙伴 |
| chuangye | 创业助手 | | bdpan-storage | 百度网盘 |
| kc-gui | KC GUI | | github-skill | GitHub |
| resume-builder | 简历生成器 | | resume-optimizer | 简历优化 |

### 📁 Skills 目录结构

```
skills/
├── lark-*/              # 飞书办公套件 (25 个)
├── qclaw-*/             # QClaw 平台 (6 个)
├── tencent-*/           # 腾讯生态 (4 个)
├── react-*/             # React 开发 (2 个)
├── web-*/               # Web 开发 (5 个)
├── frontend-*/          # 前端 (2 个)
├── pv-*/                # 新能源光伏 (2 个)
├── TRAE-*/              # TRAE 内置 (3 个)
├── xiaohongshu-*/       # 小红书 (2 个)
├── news-*/              # 新闻资讯 (3 个)
├── ai-*/                # AI 工具 (3 个)
├── resume-*/            # 简历 (2 个)
├── wechat-*/ wecom-*/   # 微信/企微 (4 个)
├── kimi-*/ claude-*/    # AI CLI (5 个)
├── docx/ pdf/ pptx/ xlsx/  # 文档处理 (4 个)
└── ...                  # 其他独立技能 (80+ 个)
```

每个 Skill 目录包含 `SKILL.md`（核心定义文件）以及可选的 `references/`（参考文档）、`scripts/`（执行脚本）、`templates/`（模板文件）。

### 🚀 如何使用 Skills

1. **Claude Code:** 将 `skills/` 复制到 `~/.claude/skills/`
   ```bash
   cp -r skills/* ~/.claude/skills/
   ```

2. **Trae IDE:** 将 `skills/` 复制到 `~/.trae/skills/`
   ```bash
   cp -r skills/* ~/.trae/skills/
   ```

3. **QClaw/OpenClaw:** 将 `skills/` 复制到 `~/.qclaw/skills/`
   ```bash
   cp -r skills/* ~/.qclaw/skills/
   ```

4. 或在各平台通过 SkillHub/市场搜索安装

更多 Skill 开发与使用指南，参见 [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code/skills)。

## 👥 团队

新能源编程俱乐部 (New Energy Coder Club) — 致力于新能源技术与编程技术的融合创新。

## 📞 联系我们

- **邮箱**: contact@new-energy-coder-club.org
- **官网**: https://new-energy-coder-club.org

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为本项目做出贡献的同学和老师们！

---

<div align="center">
  <strong>HXC ESP A Board — 核心设备仓库 (SKill 分支)</strong><br>
  <em>Innovation • Technology • Sustainability</em><br><br>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red.svg" alt="Made with Love">
</div>
