# 🤖 人工智能项目 (AI Projects)

本目录包含新能源编程俱乐部在人工智能领域的各类项目，主要聚焦于能源监控、智能分析、工业自动化和机器人视觉等应用场景。

## 📊 项目概览

### 🏭 工业AI项目
#### [流体工作站智能监控系统](./energy-monitoring/20250319流体工作站/)
- **项目类型**: 工业物联网 + AI分析 + 预测性维护
- **技术栈**: Python, PyTorch, Modbus, Qt, 树莓派5
- **应用场景**: 流体系统实时监控、故障预测、自动化控制
- **状态**: 🟢 活跃开发中
- **负责人**: @DarrenPig, @单广志, @杨鑫海, @殷统创

### 🔋 能源AI项目
#### [智能能源管理系统](./energy-monitoring/) 
- **项目类型**: 能源数据分析 + 优化调度
- **技术栈**: TensorFlow, Pandas, Flask, 时序预测
- **应用场景**: 能源消耗预测、智能调度优化
- **状态**: 🟡 规划中
- **负责人**: 待认领

## 🎯 技术架构

### 核心技术栈
- **机器学习框架**: PyTorch, TensorFlow, Scikit-learn
- **数据处理**: Pandas, NumPy, OpenCV, Dask
- **可视化**: Matplotlib, Plotly, Streamlit, Grafana
- **部署**: Docker, FastAPI, 边缘计算 (树莓派5)
- **工业协议**: Modbus, OPC UA, MQTT

### 应用领域矩阵
| 领域 | 技术重点 | 应用场景 | 状态 |
|------|----------|----------|------|
| 🏭 工业监控 | 预测性维护、异常检测 | 流体工作站、设备监控 | 🟢 活跃 |
| 🔋 能源管理 | 时序预测、优化调度 | 智能电网、储能优化 | 🟡 规划 |
| 🤖 机器视觉 | 目标检测、图像分割 | 质量检测、导航 | 🟡 规划 |
| 📊 数据分析 | 统计分析、模式识别 | 业务洞察、决策支持 | 🟡 规划 |

## 📁 项目标准规范

### 目录结构标准
```bash
project_name/
├── 📄 README.md                 # 项目说明文档
├── ⚙️  requirements.txt          # Python依赖列表
├── 🗂️  config/                  # 配置文件
│   ├── config.yaml             # 主配置文件
│   └── model_config/           # 模型配置
├── 📊 data/                    # 数据文件 (.gitignore)
│   ├── raw/                   # 原始数据
│   ├── processed/             # 处理后的数据
│   └── external/              # 外部数据源
├── 🐍 src/                     # 源代码
│   ├── models/               # 模型定义
│   ├── utils/                # 工具函数
│   ├── data_processing/      # 数据处理
│   ├── training/            # 训练脚本
│   ├── inference/           # 推理部署
│   └── main.py              # 主程序入口
├── 📓 notebooks/             # Jupyter笔记本
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_evaluation.ipynb
├── ✅ tests/                  # 测试代码
│   ├── unit_tests/          # 单元测试
│   └── integration_tests/   # 集成测试
├── 📚 docs/                  # 详细文档
│   ├── architecture.md      # 架构设计
│   ├── api.md              # API文档
│   └── deployment.md       # 部署指南
└── 🐳 docker/               # Docker配置
    ├── Dockerfile
    └── docker-compose.yml
```

### 🎯 代码质量要求
- **Python版本**: 3.8+ (推荐3.10)
- **代码规范**: 严格遵循PEP 8，使用black格式化
- **类型提示**: 全面使用type hints
- **文档要求**: 所有函数/类包含Google风格docstring
- **测试覆盖**: 单元测试覆盖率 > 80%
- **依赖管理**: 使用poetry或requirements.txt
- **版本控制**: 语义化版本控制 (SemVer)

### 📋 文档标准
每个AI项目必须包含：
1. **项目概述** - 业务背景、技术价值、项目目标
2. **数据文档** - 数据字典、预处理流程、数据质量
3. **模型文档** - 算法选择、架构设计、超参数说明
4. **实验报告** - 评估指标、对比分析、消融实验
5. **部署手册** - 环境配置、运行指南、监控方案
6. **API文档** - 接口说明、请求示例、响应格式

## 🚀 快速入门

### 环境配置
```bash
# 1. 安装Python 3.10+
# 2. 安装poetry (推荐)
pip install poetry

# 3. 克隆项目
git clone https://gitee.com/darrenpig/new_energy_coder_club.git
cd projects/ai/

# 4. 安装依赖
poetry install

# 5. 激活环境
poetry shell
```

### 项目模板
使用标准化模板快速创建新项目：
```bash
# 从模板创建新项目
cp -r ../templates/ai_project_template/ ./new_project/

# 或使用cookiecutter
pip install cookiecutter
cookiecutter https://github.com/audreyr/cookiecutter-pypackage.git
```

## 📊 当前项目状态

### 🎯 活跃项目
| 项目名称 | 进度 | 下一里程碑 | 负责人 |
|----------|------|------------|--------|
| 流体工作站 | 70% | HMI界面联调 | @殷统创 |
| 数据采集 | 85% | 数据管道完善 | @单广志 |
| 模型训练 | 60% | 超参数优化 | @DarrenPig |

### 🔄 开发流程
1. **需求分析** - 明确业务需求和技术方案
2. **数据准备** - 数据收集、清洗、标注
3. **模型开发** - 实验设计、模型训练、评估
4. **部署上线** - 模型部署、性能监控、迭代优化

## 🛠️ 开发工具链

### 必备工具
- **IDE**: VS Code + Python插件 或 PyCharm
- **版本控制**: Git + GitHub/Gitee
- **环境管理**: Poetry 或 Conda
- **代码质量**: black, flake8, mypy, pytest
- **文档生成**: Sphinx + ReadTheDocs

### 协作平台
- **代码托管**: Gitee (主) + GitHub (镜像)
- **项目管理**: GitHub Projects + Issues
- **文档协作**: Markdown + 飞书文档
- **沟通交流**: 微信技术群 + 周会

## 📚 学习资源中心

### 核心课程
- [机器学习实战 - ApacheCN](https://github.com/apachecn/MachineLearning)
- [PyTorch官方教程](https://pytorch.org/tutorials/)
- [工业AI应用案例](https://github.com/industrial-ai)

### 数据集资源
- [Kaggle竞赛平台](https://www.kaggle.com/)
- [UCI机器学习库](https://archive.ics.uci.edu/ml/)
- [天池大数据竞赛](https://tianchi.aliyun.com/)
- [工业数据集收集](https://github.com/industrial-ai/industrial-datasets)

### 开发文档
- [Python最佳实践](https://gitee.com/darrenpig/new_energy_coder_club/blob/master/projects/templates/ai_project_template/README.md)
- [模型部署指南](https://github.com/alexeygrigorev/mlbookcamp-code)
- [性能优化技巧](https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html)

## 🤝 贡献指南

### 开发流程
1. **认领任务** - 在Issues中认领开发任务
2. **创建分支** - `git checkout -b feature/your-feature`
3. **开发测试** - 遵循编码规范，编写单元测试
4. **提交PR** - 描述变更内容，关联Issue
5. **代码审查** - 至少需要1名reviewer审核
6. **合并部署** - CI/CD自动测试和部署

### 贡献者公约
- ✅ 尊重他人，友好沟通
- ✅ 代码优先，文档随后  
- ✅ 测试驱动，质量第一
- ✅ 及时更新，避免冲突
- ✅ 遵守协议，开源共享

## 🐛 问题支持

### 常见问题排查
1. **环境问题** - 检查Python版本和依赖兼容性
2. **数据问题** - 验证数据格式和完整性
3. **模型问题** - 检查超参数和训练日志
4. **部署问题** - 查看容器日志和监控指标

### 获取帮助
- **技术讨论**: 加入AI技术交流群 (联系@DarrenPig)
- **文档问题**: 提交GitHub Issue
- **紧急支持**: darrenpig@outlook.com
- **项目合作**: 22230635@czu.cn

## 📞 核心团队

| 角色 | 负责人 | 联系方式 | 负责领域 |
|------|--------|----------|----------|
| 项目负责人 | @DarrenPig | darrenpig@outlook.com | 整体规划、技术架构 |
| 算法工程师 | @单广志 | - | 模型开发、算法优化 |
| 硬件工程师 | @杨鑫海 | - | 传感器、数据采集 |
| 前端工程师 | @殷统创 | - | HMI界面、可视化 |

---

**最后更新**: 2025年8月  
**维护团队**: AI项目组 - NEC新能源极客俱乐部  
**许可证**: MIT License - 详见 [LICENSE](../../../LICENSE.md)

> 🌟 欢迎加入AI项目组！我们正在构建智能化的工业未来，期待你的创意和代码！
