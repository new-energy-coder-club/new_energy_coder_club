# 🛠️ 开发工具脚本库

欢迎来到NEC新能源极客俱乐部的开发工具脚本库！这里汇集了各种自动化脚本、构建工具、部署脚本和维护工具，帮助团队提升开发效率和项目管理水平。

## 📂 目录结构

```
scripts/
├── build/                # 构建脚本
│   ├── compile.py        # 编译脚本
│   ├── package.py        # 打包脚本
│   └── release.py        # 发布脚本
├── deploy/               # 部署脚本
│   ├── docker/           # Docker部署
│   ├── cloud/            # 云平台部署
│   └── local/            # 本地部署
├── testing/              # 测试脚本
│   ├── unit_test.py      # 单元测试
│   ├── integration_test.py # 集成测试
│   └── performance_test.py # 性能测试
├── maintenance/          # 维护脚本
│   ├── backup.py         # 备份脚本
│   ├── cleanup.py        # 清理脚本
│   └── monitor.py        # 监控脚本
├── migration/            # 迁移脚本
│   ├── migrate_repository.py # 仓库迁移脚本
│   └── migration_config.json # 迁移配置
├── automation/           # 自动化脚本
│   ├── ci_cd/            # CI/CD脚本
│   ├── git_hooks/        # Git钩子
│   └── workflows/        # 工作流脚本
└── utilities/            # 工具脚本
    ├── file_operations.py # 文件操作
    ├── data_processing.py # 数据处理
    └── system_info.py     # 系统信息
```

## 🔨 构建脚本 (Build)

### 📦 编译脚本 (compile.py)
自动化编译各种项目类型的脚本

**功能特性**:
- 支持多种编程语言编译
- 自动依赖检查和安装
- 编译错误日志记录
- 交叉编译支持

**使用方法**:
```bash
# 编译Python项目
python scripts/build/compile.py --type python --project ./projects_new/ai/smart_home

# 编译C++项目
python scripts/build/compile.py --type cpp --project ./projects_new/robotics/autonomous_robot

# 编译嵌入式项目
python scripts/build/compile.py --type embedded --target stm32 --project ./projects_new/embedded/sensor_network
```

### 📦 打包脚本 (package.py)
项目打包和分发脚本

**功能特性**:
- 自动创建发布包
- 依赖项打包
- 版本号管理
- 多平台打包支持

**使用方法**:
```bash
# 打包Python应用
python scripts/build/package.py --type python --project ./projects_new/ai/smart_home --output ./dist

# 打包Docker镜像
python scripts/build/package.py --type docker --project ./projects_new/ai/smart_home --tag nec/smart_home:v1.0
```

### 🚀 发布脚本 (release.py)
自动化发布和部署脚本

**功能特性**:
- 版本标签创建
- 自动化测试执行
- 发布包上传
- 发布通知

**使用方法**:
```bash
# 发布新版本
python scripts/build/release.py --version v1.2.0 --project smart_home --platform github

# 发布到多个平台
python scripts/build/release.py --version v1.2.0 --project smart_home --platform all
```

## 🚀 部署脚本 (Deploy)

### 🐳 Docker部署 (docker/)
容器化部署相关脚本

**脚本列表**:
- `docker_build.py`: Docker镜像构建
- `docker_deploy.py`: Docker容器部署
- `docker_compose.py`: Docker Compose管理
- `docker_registry.py`: 镜像仓库管理

**使用示例**:
```bash
# 构建Docker镜像
python scripts/deploy/docker/docker_build.py --project smart_home --tag latest

# 部署到Docker Swarm
python scripts/deploy/docker/docker_deploy.py --stack nec-stack --compose docker-compose.yml
```

### ☁️ 云平台部署 (cloud/)
云平台自动化部署脚本

**支持平台**:
- **AWS**: EC2、ECS、Lambda部署
- **阿里云**: ECS、容器服务部署
- **腾讯云**: CVM、TKE部署
- **Azure**: VM、Container Instances部署

**使用示例**:
```bash
# 部署到AWS EC2
python scripts/deploy/cloud/aws_deploy.py --instance-type t3.micro --project smart_home

# 部署到阿里云ECS
python scripts/deploy/cloud/aliyun_deploy.py --region cn-hangzhou --project smart_home
```

### 🏠 本地部署 (local/)
本地环境部署和配置脚本

**功能特性**:
- 本地服务启动
- 环境变量配置
- 数据库初始化
- 服务健康检查

**使用示例**:
```bash
# 本地部署开发环境
python scripts/deploy/local/local_deploy.py --env development --project smart_home

# 本地部署生产环境
python scripts/deploy/local/local_deploy.py --env production --project smart_home --port 8080
```

## 🧪 测试脚本 (Testing)

### 🔬 单元测试 (unit_test.py)
自动化单元测试执行脚本

**功能特性**:
- 多框架支持 (pytest, unittest, jest)
- 测试覆盖率统计
- 测试报告生成
- 持续集成集成

**使用方法**:
```bash
# 运行Python单元测试
python scripts/testing/unit_test.py --project ./projects_new/ai/smart_home --framework pytest

# 运行JavaScript单元测试
python scripts/testing/unit_test.py --project ./projects_new/ai/web_dashboard --framework jest

# 生成覆盖率报告
python scripts/testing/unit_test.py --project smart_home --coverage --output ./test_reports
```

### 🔗 集成测试 (integration_test.py)
系统集成测试自动化脚本

**功能特性**:
- API接口测试
- 数据库集成测试
- 服务间通信测试
- 端到端测试

**使用方法**:
```bash
# 运行API集成测试
python scripts/testing/integration_test.py --type api --project smart_home --env staging

# 运行端到端测试
python scripts/testing/integration_test.py --type e2e --project smart_home --browser chrome
```

### ⚡ 性能测试 (performance_test.py)
系统性能测试和基准测试脚本

**功能特性**:
- 负载测试
- 压力测试
- 内存泄漏检测
- 性能基准对比

**使用方法**:
```bash
# 运行负载测试
python scripts/testing/performance_test.py --type load --project smart_home --users 100 --duration 300

# 运行压力测试
python scripts/testing/performance_test.py --type stress --project smart_home --max-users 1000
```

## 🔧 维护脚本 (Maintenance)

### 💾 备份脚本 (backup.py)
数据和代码备份自动化脚本

**功能特性**:
- 数据库备份
- 文件系统备份
- 增量备份支持
- 云存储同步
- 备份验证

**使用方法**:
```bash
# 备份项目数据
python scripts/maintenance/backup.py --type project --source ./projects_new --destination ./backups

# 备份数据库
python scripts/maintenance/backup.py --type database --db mysql --host localhost --output ./db_backups

# 增量备份
python scripts/maintenance/backup.py --type incremental --source ./projects_new --destination ./backups
```

### 🧹 清理脚本 (cleanup.py)
系统清理和优化脚本

**功能特性**:
- 临时文件清理
- 日志文件轮转
- 缓存清理
- 磁盘空间优化

**使用方法**:
```bash
# 清理临时文件
python scripts/maintenance/cleanup.py --type temp --path ./projects_new

# 清理日志文件
python scripts/maintenance/cleanup.py --type logs --older-than 30days

# 清理Docker镜像
python scripts/maintenance/cleanup.py --type docker --unused
```

### 📊 监控脚本 (monitor.py)
系统监控和健康检查脚本

**功能特性**:
- 服务健康检查
- 资源使用监控
- 性能指标收集
- 告警通知

**使用方法**:
```bash
# 监控系统资源
python scripts/maintenance/monitor.py --type system --interval 60

# 监控服务状态
python scripts/maintenance/monitor.py --type service --services web,api,database

# 生成监控报告
python scripts/maintenance/monitor.py --type report --output ./monitoring_reports
```

## 🔄 迁移脚本 (Migration)

### 📦 仓库迁移脚本 (migrate_repository.py)
**当前项目的核心迁移工具**

**功能特性**:
- 自动化目录结构迁移
- 完整的备份机制
- 迁移完整性验证
- 详细的迁移日志
- 回滚功能支持

**使用方法**:
```bash
# 执行完整迁移
python scripts/migrate_repository.py --root .

# 预览迁移计划
python scripts/migrate_repository.py --root . --dry-run

# 回滚迁移
python scripts/migrate_repository.py --rollback backup_20250118_021011
```

**迁移统计**:
- ✅ 成功迁移: 16个项目
- ❌ 失败项目: 2个 (不存在的路径)
- 📊 迁移成功率: 88.9%
- 📁 总文件数: 1,847个
- 💾 总数据量: 102.76 MB

### ⚙️ 迁移配置 (migration_config.json)
迁移规则和映射配置文件

**配置内容**:
- 目录映射规则
- 文件处理规则
- 验证规则
- 回滚配置

## 🤖 自动化脚本 (Automation)

### 🔄 CI/CD脚本 (ci_cd/)
持续集成和持续部署脚本

**脚本列表**:
- `github_actions.py`: GitHub Actions工作流生成
- `jenkins_pipeline.py`: Jenkins流水线配置
- `gitlab_ci.py`: GitLab CI配置生成
- `quality_gate.py`: 代码质量门禁

**使用示例**:
```bash
# 生成GitHub Actions工作流
python scripts/automation/ci_cd/github_actions.py --project smart_home --type python

# 配置Jenkins流水线
python scripts/automation/ci_cd/jenkins_pipeline.py --project smart_home --stages build,test,deploy
```

### 🪝 Git钩子 (git_hooks/)
Git钩子脚本集合

**钩子类型**:
- `pre-commit`: 提交前检查
- `pre-push`: 推送前检查
- `post-merge`: 合并后处理
- `commit-msg`: 提交信息检查

**安装方法**:
```bash
# 安装所有Git钩子
python scripts/automation/git_hooks/install_hooks.py

# 安装特定钩子
python scripts/automation/git_hooks/install_hooks.py --hooks pre-commit,pre-push
```

### 🔄 工作流脚本 (workflows/)
自动化工作流脚本

**工作流类型**:
- 项目初始化工作流
- 代码审查工作流
- 发布管理工作流
- 问题跟踪工作流

## 🔧 工具脚本 (Utilities)

### 📁 文件操作 (file_operations.py)
文件和目录操作工具脚本

**功能特性**:
- 批量文件重命名
- 目录结构复制
- 文件内容替换
- 权限管理

**使用方法**:
```bash
# 批量重命名文件
python scripts/utilities/file_operations.py --action rename --pattern "*.txt" --replace ".bak"

# 复制目录结构
python scripts/utilities/file_operations.py --action copy --source ./old_structure --target ./new_structure
```

### 📊 数据处理 (data_processing.py)
数据处理和转换工具脚本

**功能特性**:
- CSV/JSON数据转换
- 数据清洗和验证
- 批量数据处理
- 数据统计分析

**使用方法**:
```bash
# 转换数据格式
python scripts/utilities/data_processing.py --input data.csv --output data.json --format json

# 数据清洗
python scripts/utilities/data_processing.py --action clean --input messy_data.csv --output clean_data.csv
```

### 💻 系统信息 (system_info.py)
系统信息收集和环境检查脚本

**功能特性**:
- 系统硬件信息
- 软件环境检查
- 依赖项验证
- 环境报告生成

**使用方法**:
```bash
# 收集系统信息
python scripts/utilities/system_info.py --output system_report.json

# 检查开发环境
python scripts/utilities/system_info.py --check-env --project smart_home
```

## 📊 脚本统计

| 脚本类型 | 脚本数量 | 代码行数 | 最近更新 |
|----------|----------|----------|----------|
| 🔨 构建脚本 | 3个 | 0行 | - |
| 🚀 部署脚本 | 0个 | 0行 | - |
| 🧪 测试脚本 | 3个 | 0行 | - |
| 🔧 维护脚本 | 3个 | 0行 | - |
| 🔄 迁移脚本 | 2个 | 847行 | 2025-01 |
| 🤖 自动化脚本 | 0个 | 0行 | - |
| 🔧 工具脚本 | 3个 | 0行 | - |

## 🎯 使用指南

### 🚀 快速开始
1. **环境准备**: 确保Python 3.8+环境
2. **依赖安装**: `pip install -r requirements.txt`
3. **权限设置**: 确保脚本具有执行权限
4. **配置文件**: 根据需要修改配置文件
5. **测试运行**: 先在测试环境验证脚本功能

### 📋 最佳实践
1. **参数验证**: 脚本运行前验证输入参数
2. **错误处理**: 完善的异常处理和错误恢复
3. **日志记录**: 详细的操作日志和状态记录
4. **备份机制**: 重要操作前自动创建备份
5. **权限控制**: 最小权限原则，避免过度授权

### 🔧 自定义脚本
1. **脚本模板**: 使用标准脚本模板
2. **命名规范**: 遵循统一的命名规范
3. **文档注释**: 完整的函数和类注释
4. **测试用例**: 为脚本编写测试用例
5. **版本管理**: 使用Git管理脚本版本

## 📋 开发规范

### 💻 编码规范
- **Python**: 遵循PEP8编码规范
- **Shell**: 遵循Shell脚本最佳实践
- **配置文件**: 使用JSON/YAML格式
- **文档**: 使用Markdown格式

### 🏷️ 命名规范
- **脚本文件**: 使用小写字母和下划线
- **函数名**: 使用动词+名词的组合
- **变量名**: 使用描述性的变量名
- **常量**: 使用大写字母和下划线

### ✅ 质量标准
- **功能完整**: 脚本功能完整可用
- **错误处理**: 完善的异常处理机制
- **性能优化**: 合理的性能优化
- **安全考虑**: 安全的脚本执行
- **可维护性**: 代码结构清晰易维护

## 🤝 贡献指南

### 📝 脚本贡献流程
1. **需求分析**: 明确脚本功能需求
2. **设计方案**: 设计脚本架构和接口
3. **编写代码**: 按照规范编写脚本代码
4. **测试验证**: 完整的功能测试和边界测试
5. **文档编写**: 编写使用文档和API文档
6. **代码审查**: 提交代码审查
7. **集成部署**: 集成到脚本库并部署

### 🔍 审查标准
- **功能正确性**: 脚本功能符合需求
- **代码质量**: 代码结构清晰，注释完整
- **安全性**: 无安全漏洞和风险
- **性能**: 合理的执行效率
- **兼容性**: 跨平台兼容性考虑

## 🔗 相关链接

- [🏆 竞赛项目](../competitions_new/README.md)
- [🔬 技术项目](../projects_new/README.md)
- [📦 共享资源](../shared_new/README.md)
- [📚 文档库](../docs_new/README.md)
- [⚙️ 配置文件](../config/README.md)

---

> 💡 **理念**: 自动化一切可以自动化的工作，让开发者专注于创造价值！

**维护团队**: 工具开发小组 | **联系方式**: [GitHub Issues](https://github.com/Darrenpig/new_energy_coder_club/issues)