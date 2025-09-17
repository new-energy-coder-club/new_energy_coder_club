# 📋 项目模板库

欢迎使用新能源编程俱乐部的标准化项目模板库！这里提供了各种类型项目的标准化模板，帮助快速启动新项目并保持一致的项目结构和文档规范。

## 📁 目录结构

```
templates/
├── project/                      # 通用项目模板
│   ├── README.md.template        # 项目说明文档模板
│   ├── package.json.template     # 项目配置文件模板
│   ├── .env.template             # 环境变量模板
│   ├── Dockerfile.template       # Docker配置模板
│   ├── .gitignore.template       # Git忽略文件模板
│   ├── LICENSE.template          # 开源协议模板
│   └── CONTRIBUTING.md.template  # 贡献指南模板
├── competition/                  # 竞赛项目模板
│   ├── README.md.template        # 竞赛项目说明模板
│   ├── solution.md.template      # 解决方案文档模板
│   ├── experiment.md.template    # 实验记录模板
│   └── presentation.md.template  # 汇报材料模板
├── research/                     # 研究项目模板
│   ├── README.md.template        # 研究项目说明模板
│   ├── proposal.md.template      # 研究提案模板
│   ├── methodology.md.template   # 研究方法模板
│   ├── results.md.template       # 研究结果模板
│   └── publication.md.template   # 论文发表模板
├── documentation/                # 文档模板
│   ├── README.md.template        # 文档说明模板
│   ├── api.md.template           # API文档模板
│   ├── tutorial.md.template      # 教程文档模板
│   ├── guide.md.template         # 指南文档模板
│   └── specification.md.template # 规范文档模板
├── scripts/                      # 脚本模板
│   ├── create_project.py         # 项目创建脚本
│   ├── generate_docs.py          # 文档生成脚本
│   └── template_validator.py     # 模板验证脚本
└── README.md                     # 本文档
```

## 🎯 模板分类

### 📦 通用项目模板 (project/)
适用于各种类型的技术项目，包含：
- **项目结构**: 标准化的目录结构和文件组织
- **配置文件**: 环境变量、依赖管理、构建配置
- **文档规范**: README、贡献指南、许可证
- **开发工具**: Docker、Git配置、CI/CD模板

**适用场景**:
- Web应用开发
- 移动应用开发
- 桌面应用开发
- 库和框架开发
- 工具和脚本开发

### 🏆 竞赛项目模板 (competition/)
专为各类编程竞赛和技术挑战设计，包含：
- **竞赛信息**: 赛事背景、规则、要求
- **解决方案**: 问题分析、算法设计、实现方案
- **实验记录**: 测试数据、性能分析、优化过程
- **成果展示**: 汇报材料、演示文档、总结报告

**适用场景**:
- ACM/ICPC竞赛
- 算法竞赛
- 黑客马拉松
- 创新创业大赛
- 技术挑战赛

### 🔬 研究项目模板 (research/)
面向学术研究和科研项目，包含：
- **研究计划**: 研究目标、方法、时间安排
- **文献综述**: 相关工作、理论基础、研究现状
- **实验设计**: 实验方案、数据收集、分析方法
- **成果产出**: 论文发表、专利申请、技术转化

**适用场景**:
- 学术研究项目
- 科研合作项目
- 毕业设计
- 创新研究
- 产学研合作

### 📚 文档模板 (documentation/)
提供各种类型的技术文档模板，包含：
- **API文档**: 接口说明、参数定义、示例代码
- **用户指南**: 安装配置、使用说明、故障排除
- **开发文档**: 架构设计、开发规范、贡献指南
- **规范标准**: 编码规范、设计规范、流程规范

**适用场景**:
- 技术文档编写
- 用户手册制作
- 开发指南创建
- 规范标准制定

## 🚀 快速开始

### 📋 使用步骤

1. **选择模板**
   ```bash
   # 浏览可用模板
   ls templates/
   
   # 查看具体模板内容
   ls templates/project/
   ```

2. **复制模板**
   ```bash
   # 复制到新项目目录
   cp -r templates/project/* /path/to/new/project/
   
   # 或使用脚本创建
   python scripts/create_project.py --template project --name my-new-project
   ```

3. **自定义内容**
   - 替换模板中的占位符 `{{PLACEHOLDER}}`
   - 根据项目需求调整结构和内容
   - 更新配置文件和依赖项

4. **验证模板**
   ```bash
   # 验证模板完整性
   python scripts/template_validator.py --project /path/to/new/project/
   ```

### 🔧 自动化工具

#### 项目创建脚本
```bash
# 创建新项目
python scripts/create_project.py \
  --template project \
  --name "My Awesome Project" \
  --description "A fantastic new project" \
  --author "Your Name" \
  --output ./my-awesome-project
```

#### 文档生成脚本
```bash
# 生成项目文档
python scripts/generate_docs.py \
  --project ./my-awesome-project \
  --template documentation \
  --format markdown
```

#### 模板验证脚本
```bash
# 验证模板规范性
python scripts/template_validator.py \
  --template ./templates/project \
  --check-placeholders \
  --check-structure
```

## 📝 占位符规范

### 🏷️ 命名规则
- 使用双大括号包围: `{{PLACEHOLDER_NAME}}`
- 全大写字母，下划线分隔
- 语义明确，易于理解

### 📋 通用占位符
| 占位符 | 说明 | 示例 |
|--------|------|------|
| `{{PROJECT_NAME}}` | 项目名称 | "My Awesome Project" |
| `{{PROJECT_DESCRIPTION}}` | 项目描述 | "A fantastic web application" |
| `{{AUTHOR_NAME}}` | 作者姓名 | "张三" |
| `{{AUTHOR_EMAIL}}` | 作者邮箱 | "zhangsan@example.com" |
| `{{CREATION_DATE}}` | 创建日期 | "2024-01-15" |
| `{{VERSION}}` | 版本号 | "1.0.0" |
| `{{LICENSE}}` | 许可证 | "MIT" |
| `{{REPOSITORY_URL}}` | 仓库地址 | "https://github.com/user/repo" |

### 🎯 项目特定占位符
| 占位符 | 说明 | 适用模板 |
|--------|------|----------|
| `{{TECH_STACK}}` | 技术栈 | project |
| `{{COMPETITION_NAME}}` | 竞赛名称 | competition |
| `{{RESEARCH_FIELD}}` | 研究领域 | research |
| `{{DOCUMENT_TYPE}}` | 文档类型 | documentation |

## 🛠️ 自定义模板

### 📋 创建新模板

1. **创建模板目录**
   ```bash
   mkdir templates/my-custom-template
   ```

2. **添加模板文件**
   ```bash
   # 创建基础文件
   touch templates/my-custom-template/README.md.template
   touch templates/my-custom-template/config.json.template
   ```

3. **定义占位符**
   ```markdown
   # {{TEMPLATE_NAME}}
   
   {{TEMPLATE_DESCRIPTION}}
   
   ## 配置
   - 作者: {{AUTHOR_NAME}}
   - 版本: {{VERSION}}
   ```

4. **添加元数据**
   ```json
   {
     "name": "my-custom-template",
     "description": "自定义模板描述",
     "version": "1.0.0",
     "placeholders": [
       "TEMPLATE_NAME",
       "TEMPLATE_DESCRIPTION",
       "AUTHOR_NAME",
       "VERSION"
     ]
   }
   ```

### ✅ 模板验证

```bash
# 验证新模板
python scripts/template_validator.py --template templates/my-custom-template
```

## 📊 模板统计

### 📈 使用统计
- **模板总数**: 4个主要类别
- **文件总数**: 20+个模板文件
- **占位符数量**: 100+个标准占位符
- **支持格式**: Markdown, JSON, YAML, Dockerfile

### 🏆 热门模板
1. **通用项目模板** - 适用性最广
2. **文档模板** - 使用频率最高
3. **竞赛项目模板** - 竞赛季节热门
4. **研究项目模板** - 学术项目首选

## 🔄 维护更新

### 📅 更新计划
- **每月**: 检查模板完整性和准确性
- **每季度**: 根据用户反馈优化模板
- **每半年**: 添加新的模板类型
- **每年**: 全面审查和重构模板库

### 🐛 问题反馈
如果发现模板问题或有改进建议，请通过以下方式反馈：
- 提交Issue到项目仓库
- 发送邮件到技术支持邮箱
- 在社区论坛发起讨论

### 🤝 贡献指南
欢迎贡献新的模板或改进现有模板：
1. Fork项目仓库
2. 创建新的模板分支
3. 添加或修改模板文件
4. 提交Pull Request
5. 等待代码审查和合并

## 📚 相关资源

### 🔗 内部链接
- [项目规范文档](../docs_new/standards/)
- [开发指南](../docs_new/guides/)
- [最佳实践](../docs_new/best_practices/)

### 🌐 外部资源
- [GitHub模板最佳实践](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)
- [项目文档编写指南](https://www.writethedocs.org/guide/)
- [开源项目规范](https://opensource.guide/)

### 🛠️ 推荐工具
- **Cookiecutter**: Python项目模板工具
- **Yeoman**: Web应用脚手架工具
- **Plop**: 微型生成器框架

## 📄 许可证

本模板库采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情

## 📞 联系方式

- **技术支持**: templates@newenergy-club.org
- **问题反馈**: issues@newenergy-club.org
- **改进建议**: suggestions@newenergy-club.org

---

> 📋 **模板理念**: 标准化流程，提升效率，保证质量，促进协作！

**最后更新**: 2024-01-15 | **版本**: v1.0.0