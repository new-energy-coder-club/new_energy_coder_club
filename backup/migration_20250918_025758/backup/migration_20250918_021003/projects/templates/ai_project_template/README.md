# 🤖 AI项目模板

这是一个标准的AI项目模板，适用于新能源编程俱乐部的所有人工智能项目。遵循此模板可以确保项目结构统一、文档完整、易于维护。

## 🎯 模板特性

- ✅ **标准化结构** - 统一的目录组织和文件命名
- ✅ **完整文档** - 包含所有必要的技术文档
- ✅ **质量保障** - 代码规范、测试覆盖、CI/CD集成
- ✅ **易于部署** - Docker容器化，一键部署
- ✅ **团队协作** - 清晰的贡献指南和开发流程

## 📁 项目结构

```bash
ai_project_template/
├── 📄 README.md                 # 项目说明文档 (当前文件)
├── ⚙️  pyproject.toml          # Poetry依赖管理 (推荐)
├── ⚙️  requirements.txt         # Pip依赖列表 (备用)
├── 🗂️  config/                  # 配置文件目录
│   ├── config.yaml             # 主配置文件
│   ├── model_config.yaml       # 模型配置
│   └── logging_config.yaml     # 日志配置
├── 🐍 src/                      # 源代码目录
│   ├── __init__.py            # 包初始化
│   ├── data_processing/       # 数据处理模块
│   │   ├── __init__.py
│   │   ├── data_loader.py     # 数据加载
│   │   ├── data_cleaner.py    # 数据清洗
│   │   └── feature_engineering.py # 特征工程
│   ├── models/                # 模型定义模块
│   │   ├── __init__.py
│   │   ├── base_model.py      # 基础模型类
│   │   ├── neural_networks.py # 神经网络模型
│   │   └── traditional_ml.py  # 传统机器学习模型
│   ├── training/              # 训练模块
│   │   ├── __init__.py
│   │   ├── trainer.py         # 训练器
│   │   ├── hyperparameter_tuning.py # 超参数优化
│   │   └── early_stopping.py  # 早停策略
│   ├── evaluation/            # 评估模块
│   │   ├── __init__.py
│   │   ├── metrics.py         # 评估指标
│   │   ├── visualization.py   # 结果可视化
│   │   └── comparison.py      # 模型对比
│   ├── deployment/            # 部署模块
│   │   ├── __init__.py
│   │   ├── api_server.py      # API服务
│   │   ├── model_serving.py   # 模型服务
│   │   └── monitoring.py      # 监控服务
│   ├── utils/                 # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py          # 日志工具
│   │   ├── file_io.py         # 文件IO工具
│   │   └── helpers.py         # 辅助函数
│   └── main.py                # 主程序入口
├── 📓 notebooks/              # Jupyter笔记本
│   ├── 01_data_exploration.ipynb     # 数据探索
│   ├── 02_feature_analysis.ipynb     # 特征分析
│   ├── 03_model_experiments.ipynb   # 模型实验
│   └── 04_result_visualization.ipynb # 结果可视化
├── 📊 data/                    # 数据目录 (.gitignore)
│   ├── raw/                   # 原始数据
│   ├── processed/             # 处理后的数据
│   ├── external/              # 外部数据源
│   └── models/                # 训练好的模型
├── ✅ tests/                   # 测试目录
│   ├── __init__.py
│   ├── unit_tests/            # 单元测试
│   │   ├── test_data_processing.py
│   │   ├── test_models.py
│   │   └── test_utils.py
│   ├── integration_tests/      # 集成测试
│   │   ├── test_training_pipeline.py
│   │   └── test_deployment.py
│   └── conftest.py            # pytest配置
├── 📚 docs/                   # 文档目录
│   ├── architecture.md        # 系统架构设计
│   ├── api.md                 # API接口文档
│   ├── deployment.md         # 部署指南
│   ├── contributing.md        # 贡献指南
│   └── troubleshooting.md     # 故障排查
├── 🐳 docker/                 # Docker配置
│   ├── Dockerfile            # 生产环境Dockerfile
│   ├── Dockerfile.dev        # 开发环境Dockerfile
│   └── docker-compose.yml     # Docker Compose配置
├── 🔧 .github/                # GitHub配置
│   ├── workflows/            # GitHub Actions
│   │   ├── ci.yml           # 持续集成
│   │   ├── cd.yml           # 持续部署
│   │   └── release.yml      # 发布流程
│   └── ISSUE_TEMPLATE/       # Issue模板
│       ├── bug_report.md     # Bug报告模板
│       └── feature_request.md # 功能请求模板
├── 📋 .pre-commit-config.yaml # Git预提交钩子
├── ⚙️  .env.example           # 环境变量示例
└── 📝 LICENSE                 # 开源许可证
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 使用Poetry (推荐)
curl -sSL https://install.python-poetry.org | python3 -
poetry install

# 或者使用pip
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 2. 数据准备

将数据文件放置在 `data/raw/` 目录下，更新 `config/config.yaml` 中的数据路径配置。

### 3. 运行项目

```bash
# 开发模式
python src/main.py --mode train --config config/config.yaml

# 训练模式
python src/main.py --mode train --config config/config.yaml

# 推理模式
python src/main.py --mode inference --config config/config.yaml

# 服务模式
python src/main.py --mode serve --config config/config.yaml
```

### 4. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit_tests/test_models.py -v

# 生成测试覆盖率报告
pytest --cov=src --cov-report=html
```

## 🎯 配置说明

### 配置文件示例 (`config/config.yaml`)

```yaml
# 项目配置
project:
  name: "ai_project_template"
  version: "1.0.0"
  description: "标准AI项目模板"

# 数据配置
data:
  raw_path: "data/raw/"
  processed_path: "data/processed/"
  external_path: "data/external/"
  train_ratio: 0.8
  validation_ratio: 0.1
  test_ratio: 0.1

# 模型配置
model:
  name: "random_forest"
  parameters:
    n_estimators: 100
    max_depth: 10
    random_state: 42
  input_features:
    - "feature_1"
    - "feature_2"
    - "feature_3"
  target_feature: "target"

# 训练配置
training:
  batch_size: 32
  epochs: 100
  learning_rate: 0.001
  early_stopping_patience: 10

# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/app.log"

# API配置
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
```

## 📊 开发规范

### 代码风格

```python
# ✅ 好的代码示例
def calculate_feature_importance(
    model: RandomForestClassifier, 
    feature_names: List[str]
) -> Dict[str, float]:
    """
    计算随机森林特征重要性
    
    Args:
        model: 训练好的随机森林模型
        feature_names: 特征名称列表
        
    Returns:
        特征重要性字典，键为特征名，值为重要性分数
    """
    importances = model.feature_importances_
    return dict(zip(feature_names, importances))

# ❌ 避免的代码风格
def calc_imp(m, f):
    # 缺少类型提示和文档
    return dict(zip(f, m.feature_importances_))
```

### 测试规范

```python
# 单元测试示例
def test_calculate_feature_importance():
    """测试特征重要性计算函数"""
    # 准备测试数据
    mock_model = Mock()
    mock_model.feature_importances_ = [0.3, 0.7]
    feature_names = ["feature_1", "feature_2"]
    
    # 执行测试
    result = calculate_feature_importance(mock_model, feature_names)
    
    # 验证结果
    expected = {"feature_1": 0.3, "feature_2": 0.7}
    assert result == expected
```

## 🛠️ 工具链配置

### Pre-commit 配置 (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
```

### GitHub Actions 配置 (`.github/workflows/ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
        
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## 📝 文档要求

### README.md 必备章节

1. **项目概述** - 项目背景、目标、价值
2. **快速开始** - 环境配置、安装、运行
3. **项目结构** - 目录说明、文件作用
4. **配置说明** - 配置文件详解
5. **API文档** - 接口说明和使用示例
6. **部署指南** - 生产环境部署步骤
7. **贡献指南** - 如何参与开发
8. **许可证** - 开源协议信息

### 代码文档要求

```python
def preprocess_data(
    data: pd.DataFrame, 
    config: Dict[str, Any]
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    数据预处理函数
    
    对输入数据进行清洗、特征工程、分割等处理，
    返回处理后的特征数据和标签数据。
    
    Args:
        data: 原始数据DataFrame
        config: 预处理配置字典
        
    Returns:
        Tuple[pd.DataFrame, pd.Series]: 
            - 处理后的特征数据
            - 对应的标签数据
            
    Raises:
        ValueError: 当数据格式不符合要求时
        KeyError: 当配置中缺少必要参数时
            
    Examples:
        >>> data = pd.DataFrame({'feature': [1, 2, 3], 'target': [0, 1, 0]})
        >>> config = {'target_col': 'target'}
        >>> X, y = preprocess_data(data, config)
        >>> len(X)
        3
    """
    # 函数实现...
```

## 🤝 贡献指南

### 开发流程

1. **认领任务** - 在Issues中认领开发任务
2. **创建分支** - `git checkout -b feature/your-feature`
3. **开发实现** - 遵循编码规范，编写测试
4. **提交PR** - 描述变更内容，关联Issue
5. **代码审查** - 至少需要1名reviewer审核
6. **合并部署** - CI/CD自动测试和部署

### 提交信息规范

```
类型(范围): 简短描述

详细描述（可选）

关联Issue: #123

类型说明:
- feat: 新功能
- fix: bug修复
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建过程或辅助工具变动
```

## 📞 支持与联系

### 获取帮助

- **技术问题**: 提交GitHub Issue
- **文档问题**: 查看项目Wiki
- **紧急支持**: 联系项目负责人
- **项目合作**: 发送邮件至合作邮箱

### 社区资源

- **技术论坛**: [NEC技术社区](https://gitee.com/darrenpig/new_energy_coder_club)
- **学习资源**: [AI项目组文档](../ai/README.md)
- **培训材料**: [项目模板指南](./docs/)

---

**许可证**: MIT License  
**版本**: v1.0.0  
**维护团队**: AI项目组 - NEC新能源极客俱乐部

> 🌟 使用此模板创建新项目时，请更新项目名称、描述和配置信息！