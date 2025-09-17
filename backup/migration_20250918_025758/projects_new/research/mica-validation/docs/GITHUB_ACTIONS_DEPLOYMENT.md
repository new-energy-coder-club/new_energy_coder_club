# GitHub Actions 自动部署 Sphinx 文档指南

本指南详细介绍如何使用 GitHub Actions 自动构建和部署 Sphinx 文档到 GitHub Pages。

## 📋 目录

- [前置条件](#前置条件)
- [配置步骤](#配置步骤)
- [工作流详解](#工作流详解)
- [故障排除](#故障排除)
- [最佳实践](#最佳实践)
- [参考文档](#参考文档)

## 🔧 前置条件

### 1. 仓库设置
- GitHub 仓库已创建
- 本地项目已推送到 GitHub
- 仓库包含 Sphinx 文档项目

### 2. 文件结构
```
project-root/
├── .github/
│   └── workflows/
│       └── docs.yml          # GitHub Actions 工作流文件
├── docs/
│   ├── source/
│   │   ├── conf.py           # Sphinx 配置文件
│   │   └── index.rst         # 文档主页
│   ├── requirements.txt      # Python 依赖
│   └── Makefile             # 构建脚本
├── .nojekyll                # 禁用 Jekyll
└── README.md
```

## ⚙️ 配置步骤

### 步骤 1：创建工作流文件

在项目根目录创建 `.github/workflows/docs.yml`：

```yaml
name: Build and Deploy Sphinx Documentation

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r docs/requirements.txt
        
    - name: Build documentation
      run: |
        cd docs
        make html
        
    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/build/html
        force_orphan: true
        user_name: 'github-actions[bot]'
        user_email: 'github-actions[bot]@users.noreply.github.com'
        commit_message: 'Deploy Sphinx documentation'
```

### 步骤 2：配置 Python 依赖

创建 `docs/requirements.txt`：

```txt
sphinx>=4.0.0
sphinx-rtd-theme>=1.0.0
sphinxcontrib-mermaid>=0.7.0
myst-parser>=0.18.0
sphinx-copybutton>=0.5.0
sphinx-tabs>=3.4.0
```

### 步骤 3：创建 .nojekyll 文件

在项目根目录创建空的 `.nojekyll` 文件：

```bash
touch .nojekyll
```

### 步骤 4：配置 GitHub Pages

1. 进入 GitHub 仓库页面
2. 点击 **Settings** 选项卡
3. 在左侧菜单中选择 **Pages**
4. 在 **Source** 下拉菜单中选择 **Deploy from a branch**
5. 选择 **gh-pages** 分支和 **/ (root)** 文件夹
6. 点击 **Save** 保存设置

### 步骤 5：推送代码触发部署

```bash
git add .
git commit -m "Add GitHub Actions workflow for documentation"
git push origin main
```

## 🔍 工作流详解

### 触发条件
```yaml
on:
  push:
    branches: [ main, master ]  # 推送到主分支时触发
  pull_request:
    branches: [ main, master ]  # PR 到主分支时触发（仅构建，不部署）
```

### 构建环境
```yaml
runs-on: ubuntu-latest        # 使用最新的 Ubuntu 环境
python-version: '3.9'         # 使用 Python 3.9
```

### 部署条件
```yaml
if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
```
只有推送到主分支时才会部署，PR 只会构建测试。

### 部署配置
- `publish_dir`: 指定要发布的目录
- `force_orphan`: 创建独立的 gh-pages 分支
- `github_token`: 使用内置的 GitHub token

## 🚨 故障排除

### 常见问题

#### 1. 构建失败：依赖安装错误
**问题**：`pip install` 失败
**解决**：
- 检查 `requirements.txt` 文件路径
- 确认依赖版本兼容性
- 添加 `--no-cache-dir` 参数

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install --no-cache-dir -r docs/requirements.txt
```

#### 2. 部署失败：权限错误
**问题**：`Permission denied` 错误
**解决**：
- 确认仓库设置中启用了 Actions
- 检查 `GITHUB_TOKEN` 权限
- 在仓库设置中启用 "Read and write permissions"

#### 3. 文档不显示：404 错误
**问题**：访问文档链接显示 404
**解决**：
- 确认 `.nojekyll` 文件存在
- 检查 `publish_dir` 路径是否正确
- 确认 GitHub Pages 设置正确

#### 4. 样式丢失：CSS/JS 文件加载失败
**问题**：文档显示但样式异常
**解决**：
在 `conf.py` 中添加：
```python
html_baseurl = 'https://username.github.io/repository-name/'
```

### 调试技巧

#### 1. 查看构建日志
- 进入 GitHub 仓库的 **Actions** 选项卡
- 点击失败的工作流运行
- 展开各个步骤查看详细日志

#### 2. 本地测试
```bash
# 本地构建测试
cd docs
make clean
make html

# 检查生成的文件
ls -la build/html/
```

#### 3. 添加调试输出
```yaml
- name: Debug - List files
  run: |
    echo "Current directory:"
    pwd
    echo "Files in docs/build/html:"
    ls -la docs/build/html/
```

## 🎯 最佳实践

### 1. 版本管理
```yaml
# 固定 Action 版本以确保稳定性
- uses: actions/checkout@v4
- uses: actions/setup-python@v4
- uses: peaceiris/actions-gh-pages@v3
```

### 2. 缓存优化
```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('docs/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

### 3. 多版本支持
```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10']
```

### 4. 条件部署
```yaml
# 只在特定条件下部署
- name: Deploy to GitHub Pages
  if: |
    github.event_name == 'push' && 
    github.ref == 'refs/heads/main' && 
    !contains(github.event.head_commit.message, '[skip deploy]')
```

### 5. 通知集成
```yaml
- name: Notify deployment
  if: success()
  run: |
    echo "📚 Documentation deployed successfully!"
    echo "🔗 URL: https://${{ github.repository_owner }}.github.io/${{ github.event.repository.name }}/"
```

## 📚 参考文档

### 官方文档
- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [Sphinx 官方文档](https://www.sphinx-doc.org/)

### 相关 Actions
- [actions/checkout](https://github.com/actions/checkout) - 代码检出
- [actions/setup-python](https://github.com/actions/setup-python) - Python 环境设置
- [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages) - GitHub Pages 部署

### 示例项目
- [Sphinx 官方示例](https://github.com/sphinx-doc/sphinx/tree/master/.github/workflows)
- [Read the Docs 主题示例](https://github.com/readthedocs/sphinx_rtd_theme)

### 进阶配置
- [自定义域名配置](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [多语言文档部署](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-language)
- [版本化文档](https://github.com/sphinx-doc/sphinx/issues/3382)

## 🔄 工作流模板

### 基础模板
适用于简单的 Sphinx 项目：

```yaml
name: Deploy Docs
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - run: pip install sphinx sphinx-rtd-theme
    - run: cd docs && make html
    - uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/build/html
```

### 高级模板
包含缓存、多版本测试、通知等功能：

```yaml
name: Documentation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10']
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip packages
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('docs/requirements.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r docs/requirements.txt
    
    - name: Test documentation build
      run: |
        cd docs
        make html
        make linkcheck
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r docs/requirements.txt
    
    - name: Build documentation
      run: |
        cd docs
        make html
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/build/html
        force_orphan: true
        user_name: 'github-actions[bot]'
        user_email: 'github-actions[bot]@users.noreply.github.com'
        commit_message: 'Deploy documentation ${{ github.sha }}'
    
    - name: Create deployment summary
      run: |
        echo "## 📚 Documentation Deployment" >> $GITHUB_STEP_SUMMARY
        echo "" >> $GITHUB_STEP_SUMMARY
        echo "✅ **Status**: Successfully deployed" >> $GITHUB_STEP_SUMMARY
        echo "🔗 **URL**: https://${{ github.repository_owner }}.github.io/${{ github.event.repository.name }}/" >> $GITHUB_STEP_SUMMARY
        echo "📝 **Commit**: ${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
        echo "🕐 **Time**: $(date)" >> $GITHUB_STEP_SUMMARY
```

## 🎉 总结

通过以上配置，你的 Sphinx 文档将实现：

- ✅ **自动化构建**：每次推送代码自动构建文档
- ✅ **自动化部署**：构建成功后自动部署到 GitHub Pages
- ✅ **错误检测**：PR 时进行构建测试，及早发现问题
- ✅ **版本控制**：文档版本与代码版本同步
- ✅ **零维护**：一次配置，长期使用

现在你可以专注于编写文档内容，让 GitHub Actions 处理所有的构建和部署工作！