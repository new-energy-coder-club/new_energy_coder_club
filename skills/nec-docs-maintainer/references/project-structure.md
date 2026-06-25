# NEC 文档项目结构与关键文件

## 目录结构

```
D:/Project_env/docs/
├── docs.json                 # Mintlify 站点配置与导航
├── index.mdx                 # 首页
├── AGENTS.md                 # Agent 说明（必须保持与 docs.json 一致）
├── development.mdx           # 本地开发指南
├── style.css                 # 自定义主题（GitHub Dark × McKinsey Blue）
├── robots.txt / llms.txt     # SEO / LLM 抓取说明
├── tools/ci/check_docs.py    # 文档健康检查脚本
│
├── ai-tools/                 # AI 工具指南（独立顶部 Tab）
├── community/                # 社区介绍与治理
├── competition/              # 竞赛概览
├── contributing/             # 贡献指南
├── curc26/                   # CURC 2026 赛季文档
├── embedded-software/        # 嵌入式软件专题
├── images/                   # 图片资源根目录
├── learn/                    # 学习资源（导航中并入「新手上路」）
├── mechanical/               # 机械设计专题
├── modules/                  # 项目模块总览
├── start-here/               # 新手上路
├── templates/                # 文档模板
├── vision/                   # 机器视觉专题
└── wiki/                     # Wiki 知识库（飞书导出快照）
```

## 关键文件

### `docs.json`

- 定义顶部 Tab、分组、页面、主题、SEO、搜索提示
- 页面路径省略 `.mdx` 扩展名
- 新增/删除/移动页面必须修改此文件

### `AGENTS.md`

- 描述项目类型、开发命令、部署方式、文件规范、导航结构
- 修改导航结构后必须同步更新

### `tools/ci/check_docs.py`

- 健康检查入口
- 白名单：`EXTERNAL_LINK_ALLOWLIST` 用于跳过登录墙/反爬域名
- 允许孤儿文件：`ALLOWED_ORPHANS`
- 禁止目录：`FORBIDDEN_PATHS`

### `development.mdx`

- 本地开发指南：Node.js 18+、Python 3、`mint dev`、CI 检查命令
