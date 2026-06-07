# 自动化检测脚本集合

本目录包含新能源编程俱乐部项目的各种自动化检测和优化脚本。

## 脚本说明

### 结构分析脚本

- **`analyze_structure.py`** - 目录结构分析工具
  - 分析当前仓库结构，识别超过2层的项目路径
  - 统计README文件位置和访问深度
  - 生成结构分析报告和优化建议

- **`verify_accessibility.py`** - 可访问性验证脚本
  - 验证项目的两次点击可达性
  - 检查README文件的访问路径

### 结构优化脚本

- **`aggressive_flatten.py`** - 激进扁平化脚本
  - 实现真正的两次点击可达性
  - 将所有项目直接移动到主目录根级别
  - 自动创建备份和生成详细报告

- **`final_optimization.py`** - 最终优化脚本
  - 针对仍然超过2次点击的项目进行深度扁平化
  - 智能分组和重命名
  - 保持项目结构的逻辑性

- **`restructure_plan.py`** - 重构计划脚本
  - 生成项目重构计划
  - 分析现有结构并提供优化方案

- **`restructure_plan_migration.py`** - 重构迁移脚本
  - 执行项目重构迁移
  - 安全移动项目文件

### 辅助工具脚本

- **`find_unused_images.py`** - 未使用图片查找工具
  - 扫描项目中未被引用的图片文件
  - 帮助清理冗余资源

- **`test_renamer.py`** - 测试重命名工具
  - 批量重命名测试文件
  - 标准化文件命名规范

## 使用方法

### 基本用法

```bash
# 分析当前项目结构
python scripts/analyze_structure.py

# 执行激进扁平化
python scripts/aggressive_flatten.py

# 最终优化处理
python scripts/final_optimization.py

# 验证可访问性
python scripts/verify_accessibility.py
```

### 推荐执行顺序

1. **结构分析**: 首先运行 `analyze_structure.py` 了解当前项目结构
2. **制定计划**: 运行 `restructure_plan.py` 生成优化计划
3. **执行优化**: 根据需要运行相应的优化脚本
4. **验证结果**: 使用 `verify_accessibility.py` 验证优化效果

## 注意事项

- ⚠️ **备份重要**: 所有脚本在执行前都会自动创建备份
- 📊 **报告生成**: 每个脚本都会生成详细的执行报告
- 🔍 **安全检查**: 脚本包含安全检查机制，避免意外覆盖
- 📝 **日志记录**: 所有操作都有详细的日志记录

## 依赖要求

- Python 3.6+
- 标准库模块：`os`, `json`, `shutil`, `pathlib`, `datetime`

## 输出文件

脚本执行后会在项目根目录生成以下文件：

- `structure_analysis_report.json/md` - 结构分析报告
- `aggressive_flatten_report.json` - 扁平化执行报告
- `backup_*` - 自动备份目录

## 维护说明

本脚本集合专门用于新能源编程俱乐部项目的结构优化和维护。如需修改或添加新脚本，请确保：

1. 遵循现有的代码风格和注释规范
2. 包含适当的错误处理和日志记录
3. 提供详细的功能说明和使用示例
4. 更新本README文档

---

*最后更新: 2025年1月*