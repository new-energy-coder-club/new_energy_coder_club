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
| 🤖 **Claude Skills 托管** | 50 个 Claude Code AI Skills，覆盖飞书/光伏/论文/开发等场景 |

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
├── 📁 skills/                               ← 🤖 50 个 Claude Code Skills
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

本仓库收录了 **50 个** Claude Code Skills，覆盖飞书办公、学术写作、新能源光伏、开发工具、效率自动化等多个领域。所有 Skill 存放在 [`skills/`](skills/) 目录下。

### 📊 技能分类总览

#### 🏢 飞书/Lark 办公套件 (25个)

飞书生态全流程覆盖：从通讯录、即时通讯、日历日程，到文档、表格、任务、审批、邮件、视频会议、知识库。

| Skill | 功能说明 |
|-------|---------|
| [lark-shared](skills/lark-shared/) | CLI 共享基础：配置初始化、认证登录、权限管理 |
| [lark-contact](skills/lark-contact/) | 通讯录：按姓名/邮箱解析 open_id，反查员工信息 |
| [lark-im](skills/lark-im/) | 即时通讯：收发消息、群聊管理、文件上传下载 |
| [lark-calendar](skills/lark-calendar/) | 日历日程：查看/创建/更新日程、预定会议室、忙闲查询 |
| [lark-doc](skills/lark-doc/) | 云文档 v2：创建/编辑/搜索飞书文档，DocxXML & Markdown |
| [lark-sheets](skills/lark-sheets/) | 电子表格：工作表管理、单元格读写、公式、筛选视图 |
| [lark-base](skills/lark-base/) | 多维表格：建表、字段管理、记录读写、仪表盘 |
| [lark-task](skills/lark-task/) | 任务管理：创建待办、子任务、清单、协作成员 |
| [lark-approval](skills/lark-approval/) | 审批 API：审批实例与任务管理 |
| [lark-mail](skills/lark-mail/) | 邮箱：起草/发送/回复/转发/搜索邮件 |
| [lark-drive](skills/lark-drive/) | 云空间：文件上传下载、文件夹管理、权限、导入导出 |
| [lark-wiki](skills/lark-wiki/) | 知识库：知识空间管理、成员管理、节点层级结构 |
| [lark-minutes](skills/lark-minutes/) | 妙记：音视频转文字、会议纪要、AI 总结/待办/章节 |
| [lark-vc](skills/lark-vc/) | 视频会议：查询会议记录、获取纪要产物 |
| [lark-vc-agent](skills/lark-vc-agent/) | 会议机器人：代用户加入/离开会议、实时事件监听 |
| [lark-okr](skills/lark-okr/) | OKR：目标与关键结果管理、进展记录 |
| [lark-slides](skills/lark-slides/) | 幻灯片：创建/编辑演示文稿（XML 协议） |
| [lark-whiteboard](skills/lark-whiteboard/) | 画板：导出/DLS/PlantUML/Mermaid 编辑 |
| [lark-markdown](skills/lark-markdown/) | Markdown：创建/查看/编辑 Markdown 文件 |
| [lark-event](skills/lark-event/) | 事件订阅：WebSocket 实时监听飞书事件 |
| [lark-attendance](skills/lark-attendance/) | 考勤打卡：查询打卡记录 |
| [lark-openapi-explorer](skills/lark-openapi-explorer/) | OpenAPI 探索：挖掘原生飞书 API |
| [lark-skill-maker](skills/lark-skill-maker/) | 自定义 Skill 创建：封装飞书 API 为可复用 Skill |
| [lark-workflow-meeting-summary](skills/lark-workflow-meeting-summary/) | 会议纪要工作流：汇总并生成结构化报告 |
| [lark-workflow-standup-report](skills/lark-workflow-standup-report/) | 日程待办摘要：日程 + 任务一站式概览 |

#### ☀️ 新能源 & 光伏 (2个)

| Skill | 功能说明 |
|-------|---------|
| [pv-station-rating](skills/pv-station-rating/) | 工商业光伏电站分层分级评分 (A/B/C/D + 十分制) |
| [pv-storage-bom](skills/pv-storage-bom/) | 光伏+储能系统标准产品 BOM 清单生成 |

#### 📝 学术论文写作 (3个)

| Skill | 功能说明 |
|-------|---------|
| [acad-paper-prompter](skills/acad-paper-prompter/) | 学术论文写作助手：润色、翻译、回复信、文献综述、选刊 |
| [paper-scaffold](skills/paper-scaffold/) | 论文目录标准化：CIT/国际会议/通用模板 |
| [latex-win](skills/latex-win/) | Windows LaTeX 编译修复：XeLaTeX/CJK/PDF 锁定 |

#### 💻 开发工具 & AI 工程 (6个)

| Skill | 功能说明 |
|-------|---------|
| [agent-browser](skills/agent-browser/) | 浏览器自动化 CLI：导航、表单、截图、数据提取 |
| [kimi-webbridge](skills/kimi-webbridge/) | Kimi WebBridge：AI 操控真实浏览器 |
| [clean-code-zh](skills/clean-code-zh/) | 《代码整洁之道》审查与重构 |
| [planning-with-files](skills/planning-with-files/) | Manus 式文件规划：task_plan/findings/progress |
| [harness](skills/harness/) | 多会话自治 Agent：进度检查点、故障恢复 |
| [agentic-loop](skills/agentic-loop/) | Agentic Loop 防护：工具调用上限与重复检测 |

#### 📊 效率 & 日程 (4个)

| Skill | 功能说明 |
|-------|---------|
| [productivity-automation-kit](skills/productivity-automation-kit/) | 效率自动化工具箱：工作流模板 + 日程管理 + 任务提醒 |
| [plan-my-day](skills/plan-my-day/) | 能量优化每日计划 |
| [study-habits](skills/study-habits/) | 学习习惯管理：间隔重复、主动回忆 |
| [ai-dev-dashboard](skills/ai-dev-dashboard/) | PowerShell AI 开发面板 |

#### 🔍 搜索 & 资讯 (3个)

| Skill | 功能说明 |
|-------|---------|
| [baidu-search](skills/baidu-search/) | 百度 AI 搜索：网页/百科/秒懂百科/AI 智能生成 |
| [news](skills/news/) | 新闻资讯：中文新闻 + 全球 AI 技术资讯 |
| [news-extractor](skills/news-extractor/) | 新闻提取：公众号/头条/网易/搜狐/腾讯 |

#### 🎨 设计 & 发布 (3个)

| Skill | 功能说明 |
|-------|---------|
| [web-design](skills/web-design/) | 网页设计部署：Tailwind CSS + Cloudflare Pages |
| [mintlify](skills/mintlify/) | Mintlify 文档站点构建 |
| [xiaohongshu-images](skills/xiaohongshu-images/) | 小红书 3:4 图文生成 |

#### 📄 简历 & 求职 (2个)

| Skill | 功能说明 |
|-------|---------|
| [resume-builder](skills/resume-builder/) | 简历生成器：Reactive Resume JSON 输出 |
| [resume-optimizer](skills/resume-optimizer/) | 简历优化：PDF 导出、ATS 分析 |

#### 💬 社交数据 & 工具 (2个)

| Skill | 功能说明 |
|-------|---------|
| [wx-cli-wechat-local-data](skills/wx-cli-wechat-local-data/) | 微信本地数据查询导出 |
| [find-skills](skills/find-skills/) | SkillHub 技能搜索与管理 |

### 📁 Skills 目录结构

```
skills/
├── lark-*/          # 飞书办公套件 (25 个)
├── pv-*/            # 新能源光伏 (2 个)
├── acad-paper-*/    # 学术论文 (3 个，含 latex-win)
├── agent-*/         # 浏览器/Agent 工具 (3 个，含 kimi-webbridge)
├── productivity-*/  # 效率工具 (1 个)
└── ...              # 其他技能
```

每个 Skill 目录包含 `SKILL.md`（核心定义文件）以及可选的 `references/`（参考文档）、`scripts/`（执行脚本）、`templates/`（模板文件）。

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
