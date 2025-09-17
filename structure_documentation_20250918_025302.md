
# 新能源编程俱乐部目录结构设计文档

> 版本：1.0.0  
> 创建时间：2025-09-18T02:53:02.549860  
> 描述：新能源编程俱乐部标准化目录结构蓝图

## 🎯 设计原则

1. 一次点击原则：核心项目最多2层目录访问
2. 英文标准化命名：使用kebab-case命名规范
3. 功能导向分类：按项目类型和用途分类
4. 时间维度组织：按年份和时间顺序组织
5. 资源共享优化：共享资源集中管理
6. 文档完整性：每个目录必须包含README文件
7. 可扩展性：支持未来项目类型扩展
8. 版本控制友好：避免特殊字符和空格


## 📁 目录结构概览

```
新能源编程俱乐部/
├── competitions/          # 🏆 竞赛项目（核心访问）
├── projects/             # 💻 开发项目（核心访问）
├── shared/               # 📦 共享资源（重要访问）
├── docs/                 # 📚 文档中心（重要访问）
├── tools/                # 🔧 开发工具（支持访问）
└── archive/              # 📋 历史归档（支持访问）
```

## 📋 详细规范


### competitions/ - 竞赛项目目录，按年份和竞赛类型组织

**访问级别**：core  
**最大深度**：3 层  
**命名规范**：`competitions/{year}/{competition-type}`

**用途**：存储所有竞赛相关项目，实现快速访问

**子目录**：
- `2024/` - 2024年度竞赛项目
- `2025/` - 2025年度竞赛项目
- `archive/` - 历史竞赛项目归档

**示例路径**:
- `competitions/2024/electronics-competition`
- `competitions/2024/energy-saving-competition`
- `competitions/2025/robotics-robocon`

**必需文件**:
- `README.md`

**可选文件**:
- `CHANGELOG.md`
- `CONTRIBUTORS.md`

---


### projects/ - 开发项目目录，按技术领域和项目类型组织

**访问级别**：core  
**最大深度**：3 层  
**命名规范**：`projects/{technology}/{project-name}`

**用途**：存储所有开发项目，支持技术分类和快速定位

**子目录**：
- `ai/` - 人工智能相关项目
- `embedded/` - 嵌入式系统项目
- `robotics/` - 机器人技术项目
- `research/` - 科研和横向项目
- `templates/` - 项目模板和脚手架

**示例路径**:
- `projects/ai/energy-monitoring`
- `projects/embedded/nearlink-controller`
- `projects/robotics/humanoid-robot`

**必需文件**:
- `README.md`

**可选文件**:
- `CHANGELOG.md`
- `LICENSE`
- `requirements.txt`

---


### shared/ - 共享资源目录，存储可复用的资源和工具

**访问级别**：important  
**最大深度**：2 层  
**命名规范**：`shared/{resource-type}`

**用途**：集中管理共享资源，避免重复，提高复用性

**子目录**：
- `assets/` - 共享资源文件（图片、视频等）
- `libraries/` - 共享代码库和组件
- `models/` - 3D模型和设计文件
- `tools/` - 共享工具和脚本
- `templates/` - 通用模板文件

**示例路径**:
- `shared/assets/images`
- `shared/models/3d-parts`
- `shared/tools/scripts`

**必需文件**:
- `README.md`

**可选文件**:
- `INDEX.md`
- `USAGE.md`

---


### docs/ - 文档中心，存储所有项目文档和指南

**访问级别**：important  
**最大深度**：2 层  
**命名规范**：`docs/{doc-type}`

**用途**：提供统一的文档入口，支持知识管理和传承

**子目录**：
- `guides/` - 使用指南和教程
- `api/` - API文档和接口说明
- `tutorials/` - 详细教程和示例
- `references/` - 参考文档和规范
- `archive/` - 历史文档归档

**示例路径**:
- `docs/guides/project-setup`
- `docs/tutorials/embedded-development`
- `docs/api/robotics-framework`

**必需文件**:
- `README.md`
- `index.md`

**可选文件**:
- `CONTRIBUTING.md`
- `FAQ.md`

---


### tools/ - 开发工具和自动化脚本目录

**访问级别**：supporting  
**最大深度**：2 层  
**命名规范**：`tools/{tool-category}`

**用途**：提供开发和维护工具，支持自动化流程

**子目录**：
- `automation/` - 自动化脚本和工具
- `testing/` - 测试工具和框架
- `deployment/` - 部署和发布工具
- `monitoring/` - 监控和分析工具
- `utilities/` - 通用工具和实用程序

**示例路径**:
- `tools/automation/ci-cd`
- `tools/testing/unit-tests`
- `tools/deployment/docker`

**必需文件**:
- `README.md`

**可选文件**:
- `INSTALL.md`
- `USAGE.md`

---


### archive/ - 归档目录，存储历史项目和废弃内容

**访问级别**：supporting  
**最大深度**：3 层  
**命名规范**：`archive/{year}/{category}`

**用途**：保存历史记录，避免丢失重要信息

**子目录**：
- `2023/` - 2023年历史项目
- `2024/` - 2024年历史项目
- `deprecated/` - 已废弃的项目和工具
- `backup/` - 备份和迁移文件

**示例路径**:
- `archive/2023/old-competitions`
- `archive/deprecated/legacy-tools`
- `archive/backup/migration-backup`

**必需文件**:
- `README.md`
- `ARCHIVE_INFO.md`

**可选文件**:
- `MIGRATION_LOG.md`

---


## 📝 命名规范

- **directories**：kebab-case (小写字母，连字符分隔)
- **files**：kebab-case 或 snake_case
- **projects**：年份+类型+简短描述
- **competitions**：年份+竞赛类型+具体名称
- **research**：项目代号或简短英文描述
- **forbidden_chars**：空格、中文、特殊符号
- **max_length**：50字符以内


## 🔄 迁移映射

基于项目分析结果，生成了 89 个项目的迁移映射。

### 示例映射

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
| `.github\workflows` | `tools/workflows/workflows` | 自动映射 |
| `.trae\documents` | `docs/misc/documents` | 自动映射 |
| `.trae\rules` | `archive/uncategorized/rules` | 自动映射 |
| `backup\migration_20250918_021003` | `archive/uncategorized/migration_20250918_021003` | 自动映射 |
| `backup\migration_20250918_021003\competitions\2024` | `competitions/2025/other-competitions/2024` | 自动映射 |
| `backup\migration_20250918_021003\projects` | `projects/misc/projects` | 自动映射 |
| `backup\migration_20250918_021003\projects\ai` | `projects/ai/ai` | 自动映射 |
| `backup\migration_20250918_021003\projects\embedded` | `projects/embedded/embedded` | 自动映射 |
| `backup\migration_20250918_021003\projects\robotics` | `projects/robotics/robotics` | 自动映射 |
| `backup\migration_20250918_021003\projects\templates` | `projects/templates/templates` | 自动映射 |
| ... | ... | 还有 79 个映射 |


## 🚀 实施计划

### 第一阶段：结构创建
1. 创建标准化目录结构
2. 生成必要的 README 文件
3. 建立命名规范和模板

### 第二阶段：项目迁移
1. 按优先级迁移现有项目
2. 更新项目路径和链接
3. 验证迁移完整性

### 第三阶段：优化完善
1. 更新文档和导航
2. 建立自动化工具
3. 培训团队成员

## 📊 预期效果

- **访问效率**：核心项目实现一次点击访问
- **结构清晰**：按功能和类型明确分类
- **易于维护**：标准化命名和文档规范
- **可扩展性**：支持未来项目类型扩展

---

📅 文档生成时间：2025-09-18 02:53:02
