# HXC ESP A Board — AI 增强核心设备仓库 🚀

> HXC 战队 ESP32-S3 主控板（Board A）| 149 个 AI Coding Skills | 多工具链配置

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-149-blue)](skills/)
[![Last Updated](https://img.shields.io/badge/updated-2026.06.14-green)]()

---

## 📑 目录

- [🎯 分支定位](#-分支定位)
- [📋 仓库结构](#-仓库结构)
- [🚀 快速开始](#-快速开始)
- [🔌 硬件与命令](#-硬件与命令)
- [🤖 AI 工具配置](#-ai-工具配置) — AtomCode · Kimi CLI · Claude Code · Trae · Kimi Code
- [📚 Skills 技能库](#-skills-技能库) — 149 个技能完整索引
- [🛡️ 安全说明](#️-安全说明)
- [👥 团队与贡献](#-团队与贡献)

---

## 🎯 分支定位

本分支 (`SKill`) 是 **HXC ESP A Board 核心设备维护仓库**，也是 **AI Coding Skills 集中托管分支**。

| 场景 | 说明 | 关键入口 |
|------|------|----------|
| 🆕 **新设备环境搭建** | 从零搭建 PlatformIO + ESP32-S3 开发环境 | [环境搭建指南](docs/guides/development-setup.md) |
| 🔧 **固件开发与调试** | 基于上游模板进行位控/电流/位置控制开发 | [HXC_A 使用说明](projects/embedded/HXC_A_Usage_Guide.md) |
| 🔄 **跨工作区协作** | Vibe Coding 多机调试、代码同步 | [调试工作流](docs/guides/vibe-coding-debug.md) |
| 📚 **设备文档维护** | 板级使用说明、硬件参数、调试技巧 | [嵌入式项目](projects/embedded/) |
| 🤖 **AI Skills 托管** | **149 个** AI Coding Skills，跨 Claude Code / Trae / QClaw / Kimi | [Skills 目录](skills/) |
| 🛠️ **AI 工具配置** | AtomCode / Kimi CLI / Claude CLI / Trae / Kimi Code 项目级配置 | [AI 工具配置](#-ai-工具配置) |

### 📊 仓库统计

| 指标 | 数值 |
|------|------|
| Skills 总数 | **149** |
| Skill 文件 | 1,954 |
| 有效数据来源 | 6 个平台（Claude / QClaw / Trae / OpenClaw / Agents / Kimi） |
| Skills 体积 | ~44 MB |
| AI 工具配置文件 | 4 套（`.atomcode/` `.kimi/` `.trae/` + Claude CLI） |
| 硬件目标 | ESP32-S3 (N16R8), CAN TWAI 1Mbps |

---

## 📋 仓库结构

```
📦 new_energy_coder_club (SKill)
│
├── 📁 projects/embedded/                       ← 嵌入式固件主目录
│   ├── 📄 HXC_A_Usage_Guide.md                 ← 板级开发使用说明（必读）
│   ├── 📁 ESP32_platformio_temple_project/     ← ⬆️ 上游子模块 (CQUPTHXC)
│   └── 📄 README.md                            ← 嵌入式项目入口
│
├── 📁 skills/                                  ← 🤖 149 个 AI Coding Skills
│   ├── lark-*/                                 (飞书办公套件 ×25)
│   ├── qclaw-*/                                (QClaw 平台 ×6)
│   ├── tencent-*/                              (腾讯生态 ×4)
│   ├── react-*/ frontend-*/ web-*/             (前端开发 ×9)
│   ├── pv-*/                                   (新能源光伏 ×2)
│   ├── TRAE-*/                                 (TRAE 内置 ×3)
│   ├── docx/ pdf/ pptx/ xlsx/                  (文档处理 ×4)
│   ├── kimi-*/ claude-*/ gemini-*/             (AI CLI 调用器 ×6)
│   └── ...                                     (其他独立技能 ×90+)
│
├── 📁 docs/guides/                             ← 开发文档
│   ├── 📄 development-setup.md                 ← 新设备环境搭建
│   └── 📄 vibe-coding-debug.md                 ← 跨工作区调试工作流
│
├── 📁 .atomcode/                               ← 🏗️ AtomCode IDE 配置
│   ├── 📄 project-instructions.md
│   └── 📁 skills/hxc-esp-a-board/
│
├── 📁 .kimi/                                   ← 💻 Kimi CLI 配置
│   └── 📄 project-instructions.md
│
├── 📁 .trae/                                   ← 🔷 Trae IDE 配置
│   └── 📄 project-instructions.md
│
├── 📁 competitions/                            ← 竞赛项目存档
├── 📁 projects/                                ← 其他项目
├── 📁 shared/                                  ← 共享资源
├── 📁 tools/                                   ← 开发工具
├── 📁 archive/                                 ← 历史归档
├── 📄 .gitignore                               ← Git 忽略规则
└── 📄 .gitmodules                              ← 子模块配置
```

---

## 🚀 快速开始

### 1. 克隆仓库

```powershell
git clone -b SKill https://gitee.com/darrenpig/new_energy_coder_club.git
cd new_energy_coder_club
git submodule update --init --recursive
```

### 2. 安装 AI Skills

**Claude Code:**
```powershell
cp -r skills/* ~/.claude/skills/
```

**Trae IDE:**
```powershell
cp -r skills/* ~/.trae/skills/
```

**QClaw / OpenClaw:** 将 `skills/` 目录路径添加到 `openclaw.json` 的 `skills.load.extraDirs` 中。

### 3. 编译 & 烧录固件

```powershell
cd projects\embedded\ESP32_platformio_temple_project
pio run --environment temple_project                    # 编译
pio run --target upload --environment temple_project    # 烧录
pio device monitor -b 115200                            # 串口监视
```

---

## 🔌 硬件与命令

### 硬件参数速查

| 参数 | 值 |
|------|-----|
| **MCU** | ESP32-S3 (rev v0.2, N16R8) |
| **Flash / PSRAM** | 16MB / 8MB |
| **CAN TX / RX** | GPIO8 / GPIO18 |
| **串口** | USB CDC (115200, 8N1) |
| **CAN 协议** | TWAI 1Mbps (经典 CAN) |

### 常用命令

```powershell
# 编译与烧录
pio run --environment temple_project
pio run --target upload --environment temple_project

# 串口监视
pio device monitor -b 115200

# 电机控制（通过串口）
python send_cmd.py "c 0.3"    # 电流模式 0.3A
python send_cmd.py "p 90"     # 绝对位置 90°
python send_cmd.py "s"        # 停止
```

### 开发入口速查

| 目标 | 入口 | 说明 |
|------|------|------|
| 第一次搭建环境 | [环境搭建指南](docs/guides/development-setup.md) | 前置依赖、安装步骤、验证清单 |
| 快速调试电机 | [Vibe Coding 调试](docs/guides/vibe-coding-debug.md) | 调试工作流、命令速查、故障处理 |
| 理解板级设计 | [HXC_A 使用说明](projects/embedded/HXC_A_Usage_Guide.md) | 硬件参数、CAN/串口约定、三类工程用法 |
| 浏览全部技能 | [Skills 目录](skills/) | 149 个 AI Coding Skills |

---

## 🤖 AI 工具配置

本仓库为 **5 种 AI 编程工具**提供项目级配置，克隆后即可使用。

### 🏗️ AtomCode IDE

| 文件 | 说明 |
|------|------|
| [`.atomcode/project-instructions.md`](.atomcode/project-instructions.md) | 项目指令：结构、技能、命令速查 |
| [`.atomcode/skills/hxc-esp-a-board/SKILL.md`](.atomcode/skills/hxc-esp-a-board/SKILL.md) | HXC Board A 开发环境自动化 Skill |

**Skill 功能:** 从零搭建 PlatformIO + ESP32-S3 环境、固件提取、烧录、电机旋转测试。

### 💻 Kimi CLI

**配置:** [`.kimi/project-instructions.md`](.kimi/project-instructions.md)

```powershell
# 代码任务（kimi-for-coding）
kimi --print --final-message -m kimi-code/kimi-for-coding -w "." -p "审查 main.cpp"

# 复杂推理（kimi-k2-thinking-turbo）
kimi --print --final-message -m kimi/kimi-k2-thinking-turbo -w "." -p "架构设计"

# 续接上次会话
kimi --print --final-message -C -p "继续分析"
```

### 🧠 Claude Code CLI

```powershell
# 单次任务
claude -p "分析项目结构" --add-dir "."

# 允许工具执行
claude -p "创建测试文件" --permission-mode acceptEdits
```

Skills 目录可直接复制到 `~/.claude/skills/` 使用。

### 🖥️ Kimi Code IDE（桌面版）

在 Kimi Code IDE 中打开本目录，项目自动注册到 `~/.kimi/kimi.json`。CLI 可通过 `--continue` 续接 IDE 会话。

### 🔷 Trae IDE

**配置:** [`.trae/project-instructions.md`](.trae/project-instructions.md)

Trae IDE 支持 Skill 市场（marketplace），已安装 60+ Skills，包括 `lark-*`、`baidu-search`、`pv-storage-bom` 等。

### ⚡ 工具选择指南

| 任务场景 | 推荐工具 | 原因 |
|----------|---------|------|
| 嵌入式 C++ 开发 | Kimi CLI / AtomCode | kimi-for-coding 专长，AtomCode 一键环境 |
| 飞书办公自动化 | Claude Code + lark-* skills | 25 个飞书 Skill 完整生态 |
| 多步骤自动化 | Claude Code | 工具调用 + 文件操作 |
| 硬件调试分析 | AtomCode Skill | 一键搭建、烧录、测试 |
| 前端/React 开发 | Trae IDE | react-best-practices、shadcn 等 |
| 代码审查重构 | Kimi CLI / TRAE-code-review | 按复杂度选择 |
| 文档撰写翻译 | Kimi CLI | 长文本处理优 |
| IDE 内 AI 辅助 | Trae / Kimi Code | 原生 IDE 体验 |
| 办公文档生成 | docx / pdf / pptx / xlsx | 专业文档 Skill |

---

## 📚 Skills 技能库

### 概览

本仓库收录了 **149 个** AI Coding Skills，整合自 6 个平台的本地 Skill 生态：

| 来源 | Skills | 代表性技能 |
|------|--------|-----------|
| **Claude Code** (`~/.claude/skills/`) | 50 | lark-*, pv-*, latex-win, agent-browser |
| **QClaw/OpenClaw** (`~/.qclaw/skills/` + Program Files) | 60 | kimi-cli, claude-cli, docx/pdf/pptx/xlsx, qclaw-*, tencent-* |
| **Trae IDE** (`~/.trae/skills/` + builtin) | 34 | react-*, shadcn, git-commit, canvas-design, TRAE-* |
| **Agents** (`~/.agents/skills/`) | 5 | cit-thesis-writer, gradpilot, wechat-cli-export |

### 📊 13 大类完整索引

#### 🏢 飞书/Lark 办公套件 (25)

> 飞书生态全流程覆盖：通讯录→即时通讯→日历→文档→表格→任务→审批→邮件→会议→知识库。

`lark-shared` `lark-contact` `lark-im` `lark-calendar` `lark-doc` `lark-sheets` `lark-base` `lark-task` `lark-approval` `lark-mail` `lark-drive` `lark-wiki` `lark-minutes` `lark-vc` `lark-vc-agent` `lark-okr` `lark-slides` `lark-whiteboard` `lark-markdown` `lark-event` `lark-attendance` `lark-openapi-explorer` `lark-skill-maker` `lark-workflow-meeting-summary` `lark-workflow-standup-report`

#### 🤖 AI CLI 调用器 (6)

> 实现 Claude ⇄ Kimi ⇄ Gemini ⇄ AI Code With 互调，不同模型按需调度。

`kimi-cli` `claude-cli` `gemini-cli` `aicodewith` `trae-assistant` `persona-switch`

#### 🌐 前端 & 设计开发 (14)

> React 生态、UI 组件库、Canvas、Web 设计全栈能力。

`react-best-practices` `react-native-skills` `shadcn` `frontend-design` `frontend-skill` `web-design-guidelines` `web-artifacts-builder` `webapp-testing` `web-design` `canvas-design` `algorithmic-art` `brand-guidelines` `theme-factory` `chart-visualization`

#### 🔧 开发工程 & 工作流 (17)

> 从代码规范到 CI/CD、从规划到执行的完整工程链路。

`clean-code-zh` `security-best-practices` `git-commit` `gh-cli` `github-skill` `test-driven-development` `spec-to-implementation` `composition-patterns` `hook-analyzer-skill` `screenshot` `writing-plans` `executing-plans` `defuddle` `planning-with-files` `harness` `agentic-loop` `agent-browser`

#### 🔍 搜索 & 资讯聚合 (8)

> 多引擎搜索 + 新闻提取 + 金融/技术资讯，覆盖中英文全场景。

`baidu-search` `online-search` `multi-search-engine` `news` `news-extractor` `news-summary` `neodata-financial-search` `tech-news-digest`

#### 📄 文档 & 办公文件 (7)

> Word / PDF / PPT / Excel 专业文档生成与处理。

`docx` `pdf` `pptx` `xlsx` `doc-coauthoring` `file-skill` `email-skill`

#### 📡 集成 & 平台连接 (14)

> 腾讯文档、企微、金山、Notion、有道笔记等主流平台集成。

`tencent-docs` `tencent-meeting-mcp` `tencent-survey` `tencent-news` `wecomcli-setup` `wecom-weisheng-scrm` `weiyun` `youdaonote` `notion` `ima` `kdocs` `imap-smtp-email` `tme-openapi` `flyai`

#### 🎓 学术 & 论文 (6)

> 从开题到答辩、从中文到英文的全流程学术写作辅助。

`acad-paper-prompter` `paper-scaffold` `latex-win` `cit-thesis-writer` `gradpilot` `patent-application-cn`

#### ☀️ 新能源 & 光伏 (2)

> 光伏电站评估 + 储能 BOM 生成，新能源领域核心工具。

`pv-station-rating` `pv-storage-bom`

#### 🏗️ QClaw/OpenClaw 平台 (15)

> 代理框架管理：定时任务、规则引擎、Skill 创建/审查、会话日志。

`qclaw-cron-skill` `qclaw-env` `qclaw-rules` `qclaw-skill-creator` `qclaw-text-file` `qclaw-openclaw` `self-improving` `self-improving-agent` `session-logs` `skill-vetter` `public-skill` `content-factory` `cloud-upload-backup` `mcporter` `mcp-builder`

#### 📊 效率 & 头脑风暴 (9)

> 每日计划、学习管理、AI 仪表盘、数据分析和报告生成。

`productivity-automation-kit` `plan-my-day` `study-habits` `brainstorming` `consulting-analysis` `report-generator-skill` `ai-dev-dashboard` `ai-data-analysis` `ai-promotion-query`

#### 💬 社交 & 微信生态 (8)

> 微信本地数据、小红书图文、浏览器操控等社交场景工具。

`wx-cli-wechat-local-data` `wechat-cli-export` `nec-wechat-sync` `corporate-deep-query` `xiaohongshu-images` `xiaohongshu-skills` `kimi-webbridge` `xbrowser`

#### 🛠️ TRAE 内置 & 独立工具 (18)

> TRAE IDE 内置审查/调试/生成能力 + 各类独立辅助工具。

`TRAE-code-review` `TRAE-debugger` `TRAE-generate-mini-app` `data-analysis` `redis-development` `find-skills` `dogfood` `aippt` `weather-advisor` `slack-gif-creator` `fbs_bookwriter` `wendao-partner-qclaw-skill` `chuangye` `bdpan-storage` `kc-gui` `github-skill` `resume-builder` `resume-optimizer`

### 📁 Skill 文件结构

每个 Skill 目录的标准结构：

```
skill-name/
├── SKILL.md              ← 核心定义（名称、描述、触发条件、工作流）
├── references/           ← 参考文档（API 说明、使用示例）
├── scripts/              ← 执行脚本（Python / Shell / PowerShell）
├── templates/            ← 模板文件
└── assets/               ← 静态资源
```

### 🚀 Skill 使用方式

| 平台 | 安装路径 | 命令 |
|------|---------|------|
| Claude Code | `~/.claude/skills/` | `cp -r skills/* ~/.claude/skills/` |
| Trae IDE | `~/.trae/skills/` | `cp -r skills/* ~/.trae/skills/` |
| QClaw/OpenClaw | `~/.qclaw/skills/` | `cp -r skills/* ~/.qclaw/skills/` |

更多 Skill 开发与使用指南，参见 [Claude Code Skills 文档](https://docs.anthropic.com/en/docs/claude-code/skills)。

---

## 🛡️ 安全说明

本仓库已完成安全扫描（2026-06-14），确认：

- ✅ **无硬编码 API Key** — 所有 Token 通过运行时 OAuth/本地代理获取
- ✅ **无真实密码** — 示例中使用占位符
- ✅ **无 JWT / Bearer Token 泄露** — get-token 脚本运行时动态获取
- ✅ **无数据库连接字符串** — 不涉及持久化存储
- ✅ **无 SSH 私钥 / 证书** — 不包含加密凭证
- ⚠️ **用户路径已脱敏** — 工具安装路径使用 `<USERNAME>` 占位符

> ⚠️ 若发现任何安全风险，请通过邮箱联系我们，勿在 Issue 中公开讨论。

---

## 👥 团队与贡献

### 新能源编程俱乐部

> New Energy Coder Club — 致力于新能源技术与编程技术的融合创新。

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 重要文档

- [项目贡献指南](CONTRIBUTING.md)
- [项目索引](PROJECT_INDEX.md)
- [优化总结](PROJECT_OPTIMIZATION_SUMMARY.md)
- [清理报告](cleanup_report.md)

---

## 📞 联系我们

- **邮箱**: contact@new-energy-coder-club.org
- **官网**: https://new-energy-coder-club.org
- **Gitee**: [darrenpig/new_energy_coder_club](https://gitee.com/darrenpig/new_energy_coder_club)
- **GitHub**: [new-energy-coder-club](https://github.com/new-energy-coder-club)

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

感谢所有为本项目做出贡献的同学和老师们！

---

<div align="center">
  <strong>HXC ESP A Board — AI 增强核心设备仓库</strong><br>
  <sub>SKill 分支 · 149 Skills · 5 AI 工具链 · ESP32-S3</sub><br><br>
  <em>Innovation · Technology · Sustainability</em><br><br>
  <img src="https://img.shields.io/badge/Made%20with-❤️-red.svg" alt="Made with Love">
</div>
