---
name: nec-docs-maintainer
description: 维护 NEC 新能源开发者社区 Mintlify 文档站点。用于新增页面、修复死链、重构导航、运行 CI 健康检查并推送到 main 分支自动部署。触发词：维护 NEC 文档、修复文档死链、重构导航、新增 NEC 页面、部署文档站、运行 docs-check。
---

# NEC 文档站点维护

## 项目概览

- **仓库**: `https://github.com/new-energy-coder-club/docs.git`
- **站点**: `https://docs.newenergycoder.club/`
- **框架**: Mintlify v3，配置在 `docs.json`
- **入口**: `index.mdx`
- **自动部署**: 推送到 `main` 分支后 Mintlify 自动部署
- **本地预览**: `mint dev`（默认 `localhost:3000`）

## 核心规范

### 文件规范

- 页面使用 `.mdx`（推荐）或 `.md`
- 每个 `.mdx` 必须包含非空 YAML frontmatter：
  ```yaml
  ---
  title: "页面标题"
  description: "页面描述"
  ---
  ```
- 图片统一放入 `images/` 目录，引用路径以 `/images/` 开头
- 禁止重新引入归档目录：`legacy/`、`api-reference/`、`essentials/`
- 允许不注册导航的孤儿文件：`AGENTS.md`、`snippets/snippet-intro.mdx`、`wiki/README.md`

### 导航规则

- 所有新页面必须在 `docs.json` 的 `navigation.tabs[].groups[].pages` 中注册
- 当前 6 个顶部 Tab：
  1. **首页**: `index`
  2. **文档**: 快速开始、新手上路、重要文档、项目模块、技术专题、模板与规范、Wiki 知识库
  3. **竞赛**: 竞赛概览、CURC 2026
  4. **AI 工具**: Claude Code、Cursor、Windsurf、MCP Server、AI 可行性研究
  5. **社区**: 关于我们、社区治理、贡献指南
  6. **关于**: README、路线图、资源汇总
- 修改导航结构后同步更新 `AGENTS.md` 的「导航结构」说明

## 标准工作流

1. **编辑内容**：新增/修改 `.mdx`、图片、`docs.json`
2. **本地检查**：`python tools/ci/check_docs.py`
3. **修复问题**：死链、未注册页面、frontmatter 缺失、localhost 链接等
4. **提交推送**：使用 Conventional Commits，例如 `docs(scope): 描述`
5. **等待部署**：Mintlify 自动部署，约 1–2 分钟

## 常见任务

### 新增页面

1. 在合适目录创建 `.mdx`，写好 frontmatter
2. 如需图片，放入 `images/<topic>/` 并以 `/images/<topic>/file.png` 引用
3. 在 `docs.json` 对应分组注册页面路径（省略 `.mdx` 扩展名）
4. 运行 CI 检查并修复报错
5. 提交推送

### 修复死链

1. 运行 `python tools/ci/check_docs.py`
2. 内部死链：修正路径或删除链接
3. 外部死链：确认是否真实失效，可加入 `EXTERNAL_LINK_ALLOWLIST` 中登录墙/证书异常的域名
4. 重新运行 CI 直到通过

### 重构导航

1. 修改 `docs.json` 的 `navigation` 字段
2. 确保所有注册页面存在且非空
3. 更新 `AGENTS.md` 中的导航结构描述
4. 运行 CI 检查无未注册页面
5. 提交推送

## CI 检查项

脚本：`tools/ci/check_docs.py`

- `docs.json` JSON 合法性与推荐字段（`metadata`、`search`、`seo`、`styles`）
- 导航页面文件存在性
- `.mdx` 文件包含非空 `title` 与 `description`
- 内部 Markdown / MDX / HTML 链接可解析
- 无 `localhost` 链接、无非 ASCII 内部路径
- 外部链接抽样检查（HEAD/GET）
- 未引入禁止目录

## 参考文件

- [项目结构与关键文件](references/project-structure.md)
- [CI 脚本说明](references/ci-checks.md)
