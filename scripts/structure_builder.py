#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新能源编程俱乐部标准化目录结构构建器

功能:
- 创建新的标准化目录结构框架
- 基于项目分析结果设计目录层次
- 实现"一次点击原则"（核心项目最多2层目录访问）
- 使用英文标准化命名规范
- 生成目录结构文档

作者: 新能源编程俱乐部
日期: 2025-01-18
"""

import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('structure_builder.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

@dataclass
class DirectorySpec:
    """目录规范数据结构"""
    name: str
    path: str
    description: str
    purpose: str
    max_depth: int
    naming_convention: str
    required_files: List[str]
    optional_files: List[str]
    subdirectories: List[str]
    access_level: str  # core, important, supporting
    examples: List[str]

@dataclass
class StructureBlueprint:
    """结构蓝图数据结构"""
    version: str
    created_at: str
    description: str
    principles: List[str]
    root_directories: List[DirectorySpec]
    naming_rules: Dict[str, str]
    file_templates: Dict[str, str]
    migration_mapping: Dict[str, str]

class StructureBuilder:
    """标准化目录结构构建器"""
    
    def __init__(self, root_path: str, analysis_report_path: str = None):
        self.root_path = Path(root_path)
        self.analysis_report = None
        self.blueprint = None
        
        # 加载分析报告
        if analysis_report_path:
            self.load_analysis_report(analysis_report_path)
        
        # 设计原则
        self.design_principles = [
            "一次点击原则：核心项目最多2层目录访问",
            "英文标准化命名：使用kebab-case命名规范",
            "功能导向分类：按项目类型和用途分类",
            "时间维度组织：按年份和时间顺序组织",
            "资源共享优化：共享资源集中管理",
            "文档完整性：每个目录必须包含README文件",
            "可扩展性：支持未来项目类型扩展",
            "版本控制友好：避免特殊字符和空格"
        ]
        
        # 命名规范
        self.naming_rules = {
            "directories": "kebab-case (小写字母，连字符分隔)",
            "files": "kebab-case 或 snake_case",
            "projects": "年份+类型+简短描述",
            "competitions": "年份+竞赛类型+具体名称",
            "research": "项目代号或简短英文描述",
            "forbidden_chars": "空格、中文、特殊符号",
            "max_length": "50字符以内"
        }
    
    def load_analysis_report(self, report_path: str):
        """加载项目分析报告"""
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                self.analysis_report = json.load(f)
            logging.info(f"已加载分析报告: {report_path}")
        except Exception as e:
            logging.error(f"加载分析报告失败: {e}")
            raise
    
    def design_structure_blueprint(self) -> StructureBlueprint:
        """设计结构蓝图"""
        logging.info("开始设计标准化目录结构蓝图")
        
        # 根据分析报告设计目录结构
        root_directories = self._design_root_directories()
        
        # 生成文件模板
        file_templates = self._generate_file_templates()
        
        # 生成迁移映射
        migration_mapping = self._generate_migration_mapping()
        
        self.blueprint = StructureBlueprint(
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            description="新能源编程俱乐部标准化目录结构蓝图",
            principles=self.design_principles,
            root_directories=root_directories,
            naming_rules=self.naming_rules,
            file_templates=file_templates,
            migration_mapping=migration_mapping
        )
        
        logging.info("结构蓝图设计完成")
        return self.blueprint
    
    def _design_root_directories(self) -> List[DirectorySpec]:
        """设计根目录结构"""
        directories = []
        
        # 1. competitions/ - 竞赛项目（核心访问）
        competitions_spec = DirectorySpec(
            name="competitions",
            path="competitions",
            description="竞赛项目目录，按年份和竞赛类型组织",
            purpose="存储所有竞赛相关项目，实现快速访问",
            max_depth=3,  # competitions/2024/electronics-competition
            naming_convention="competitions/{year}/{competition-type}",
            required_files=["README.md"],
            optional_files=["CHANGELOG.md", "CONTRIBUTORS.md"],
            subdirectories=[
                "2024", "2025", "archive"
            ],
            access_level="core",
            examples=[
                "competitions/2024/electronics-competition",
                "competitions/2024/energy-saving-competition",
                "competitions/2025/robotics-robocon"
            ]
        )
        directories.append(competitions_spec)
        
        # 2. projects/ - 开发项目（核心访问）
        projects_spec = DirectorySpec(
            name="projects",
            path="projects",
            description="开发项目目录，按技术领域和项目类型组织",
            purpose="存储所有开发项目，支持技术分类和快速定位",
            max_depth=3,  # projects/ai/energy-monitoring
            naming_convention="projects/{technology}/{project-name}",
            required_files=["README.md"],
            optional_files=["CHANGELOG.md", "LICENSE", "requirements.txt"],
            subdirectories=[
                "ai", "embedded", "robotics", "research", "templates"
            ],
            access_level="core",
            examples=[
                "projects/ai/energy-monitoring",
                "projects/embedded/nearlink-controller",
                "projects/robotics/humanoid-robot"
            ]
        )
        directories.append(projects_spec)
        
        # 3. shared/ - 共享资源（重要访问）
        shared_spec = DirectorySpec(
            name="shared",
            path="shared",
            description="共享资源目录，存储可复用的资源和工具",
            purpose="集中管理共享资源，避免重复，提高复用性",
            max_depth=2,  # shared/assets/images
            naming_convention="shared/{resource-type}",
            required_files=["README.md"],
            optional_files=["INDEX.md", "USAGE.md"],
            subdirectories=[
                "assets", "libraries", "models", "tools", "templates"
            ],
            access_level="important",
            examples=[
                "shared/assets/images",
                "shared/models/3d-parts",
                "shared/tools/scripts"
            ]
        )
        directories.append(shared_spec)
        
        # 4. docs/ - 文档中心（重要访问）
        docs_spec = DirectorySpec(
            name="docs",
            path="docs",
            description="文档中心，存储所有项目文档和指南",
            purpose="提供统一的文档入口，支持知识管理和传承",
            max_depth=2,  # docs/guides/getting-started
            naming_convention="docs/{doc-type}",
            required_files=["README.md", "index.md"],
            optional_files=["CONTRIBUTING.md", "FAQ.md"],
            subdirectories=[
                "guides", "api", "tutorials", "references", "archive"
            ],
            access_level="important",
            examples=[
                "docs/guides/project-setup",
                "docs/tutorials/embedded-development",
                "docs/api/robotics-framework"
            ]
        )
        directories.append(docs_spec)
        
        # 5. tools/ - 工具和脚本（支持访问）
        tools_spec = DirectorySpec(
            name="tools",
            path="tools",
            description="开发工具和自动化脚本目录",
            purpose="提供开发和维护工具，支持自动化流程",
            max_depth=2,  # tools/automation/deploy
            naming_convention="tools/{tool-category}",
            required_files=["README.md"],
            optional_files=["INSTALL.md", "USAGE.md"],
            subdirectories=[
                "automation", "testing", "deployment", "monitoring", "utilities"
            ],
            access_level="supporting",
            examples=[
                "tools/automation/ci-cd",
                "tools/testing/unit-tests",
                "tools/deployment/docker"
            ]
        )
        directories.append(tools_spec)
        
        # 6. archive/ - 归档目录（支持访问）
        archive_spec = DirectorySpec(
            name="archive",
            path="archive",
            description="归档目录，存储历史项目和废弃内容",
            purpose="保存历史记录，避免丢失重要信息",
            max_depth=3,  # archive/2023/old-projects
            naming_convention="archive/{year}/{category}",
            required_files=["README.md", "ARCHIVE_INFO.md"],
            optional_files=["MIGRATION_LOG.md"],
            subdirectories=[
                "2023", "2024", "deprecated", "backup"
            ],
            access_level="supporting",
            examples=[
                "archive/2023/old-competitions",
                "archive/deprecated/legacy-tools",
                "archive/backup/migration-backup"
            ]
        )
        directories.append(archive_spec)
        
        return directories
    
    def _generate_file_templates(self) -> Dict[str, str]:
        """生成文件模板"""
        templates = {}
        
        # 根目录 README 模板
        templates["root_readme"] = """
# 新能源编程俱乐部

> 🚀 致力于新能源技术创新与人才培养的开源社区

## 📁 目录结构

```
{{club_name}}/
├── competitions/          # 🏆 竞赛项目
├── projects/             # 💻 开发项目  
├── shared/               # 📦 共享资源
├── docs/                 # 📚 文档中心
├── tools/                # 🔧 开发工具
└── archive/              # 📋 历史归档
```

## 🎯 快速导航

### 核心项目（一键访问）
- [竞赛项目](./competitions/) - 各类竞赛参赛作品
- [开发项目](./projects/) - 技术开发和研究项目

### 重要资源
- [共享资源](./shared/) - 可复用的资源和工具
- [文档中心](./docs/) - 项目文档和开发指南

### 支持工具
- [开发工具](./tools/) - 自动化脚本和工具
- [历史归档](./archive/) - 历史项目和备份

## 📊 项目统计

- 总项目数：{{total_projects}}
- 竞赛项目：{{competition_count}}
- 开发项目：{{project_count}}
- 共享资源：{{shared_count}}

## 🚀 快速开始

1. **浏览竞赛项目**：`cd competitions/2024/`
2. **查看开发项目**：`cd projects/ai/`
3. **使用共享资源**：`cd shared/templates/`
4. **阅读文档**：`cd docs/guides/`

## 📝 贡献指南

请参阅 [贡献指南](./docs/guides/contributing.md) 了解如何参与项目开发。

## 📄 许可证

本项目采用 [MIT License](./LICENSE) 开源协议。

---

💡 **提示**：使用 `find . -name "README.md" | head -10` 快速浏览项目结构
"""
        
        # 竞赛项目 README 模板
        templates["competition_readme"] = """
# {{competition_name}}

> {{competition_description}}

## 📋 项目信息

- **竞赛名称**：{{competition_full_name}}
- **参赛时间**：{{competition_date}}
- **团队成员**：{{team_members}}
- **项目状态**：{{project_status}}
- **获奖情况**：{{awards}}

## 🎯 项目目标

{{project_objectives}}

## 🏗️ 技术架构

{{technical_architecture}}

## 📁 目录结构

```
{{project_name}}/
├── src/                  # 源代码
├── docs/                 # 项目文档
├── hardware/             # 硬件设计文件
├── tests/                # 测试文件
├── assets/               # 资源文件
└── README.md            # 项目说明
```

## 🚀 快速开始

### 环境要求

{{requirements}}

### 安装步骤

```bash
{{installation_steps}}
```

### 运行项目

```bash
{{run_commands}}
```

## 📊 项目成果

{{project_results}}

## 🤝 团队成员

{{team_details}}

## 📝 更新日志

查看 [CHANGELOG.md](./CHANGELOG.md) 了解项目更新历史。

## 📄 许可证

{{license_info}}
"""
        
        # 开发项目 README 模板
        templates["project_readme"] = """
# {{project_name}}

> {{project_description}}

## 📋 项目信息

- **项目类型**：{{project_type}}
- **技术栈**：{{tech_stack}}
- **开发状态**：{{development_status}}
- **维护者**：{{maintainers}}
- **最后更新**：{{last_updated}}

## 🎯 项目特性

{{project_features}}

## 🏗️ 系统架构

{{system_architecture}}

## 📁 目录结构

```
{{project_name}}/
├── src/                  # 源代码
│   ├── main/            # 主要代码
│   └── test/            # 测试代码
├── docs/                # 项目文档
├── config/              # 配置文件
├── scripts/             # 脚本文件
├── assets/              # 资源文件
└── README.md           # 项目说明
```

## 🚀 快速开始

### 环境要求

{{requirements}}

### 安装依赖

```bash
{{install_dependencies}}
```

### 配置项目

```bash
{{configuration_steps}}
```

### 运行项目

```bash
{{run_commands}}
```

## 📖 使用指南

{{usage_guide}}

## 🧪 测试

```bash
{{test_commands}}
```

## 🚀 部署

{{deployment_guide}}

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 更新日志

查看 [CHANGELOG.md](./CHANGELOG.md) 了解项目更新历史。

## 📄 许可证

{{license_info}}
"""
        
        # 共享资源 README 模板
        templates["shared_readme"] = """
# {{resource_name}}

> {{resource_description}}

## 📋 资源信息

- **资源类型**：{{resource_type}}
- **适用项目**：{{applicable_projects}}
- **维护者**：{{maintainers}}
- **最后更新**：{{last_updated}}

## 📁 资源列表

{{resource_list}}

## 🚀 使用方法

{{usage_instructions}}

## 📖 使用示例

{{usage_examples}}

## 🤝 贡献资源

{{contribution_guide}}

## 📝 更新日志

{{changelog}}
"""
        
        return templates
    
    def _generate_migration_mapping(self) -> Dict[str, str]:
        """生成迁移映射"""
        if not self.analysis_report:
            return {}
        
        mapping = {}
        
        # 基于分析报告生成映射规则
        for project in self.analysis_report.get('projects', []):
            old_path = project['path']
            category = project['category']
            subcategory = project['subcategory']
            name = project['name']
            
            # 生成新路径
            new_path = self._generate_new_path(category, subcategory, name, old_path)
            mapping[old_path] = new_path
        
        return mapping
    
    def _generate_new_path(self, category: str, subcategory: str, name: str, old_path: str) -> str:
        """生成新的标准化路径"""
        # 清理名称
        clean_name = self._clean_name(name)
        
        if category == 'competitions':
            # 从旧路径提取年份
            year = self._extract_year_from_path(old_path)
            if not year:
                year = '2024'  # 默认年份
            
            # 映射子类别到标准名称
            competition_type = self._map_competition_subcategory(subcategory)
            return f"competitions/{year}/{competition_type}/{clean_name}"
        
        elif category == 'projects':
            # 映射子类别到技术领域
            tech_field = self._map_project_subcategory(subcategory)
            return f"projects/{tech_field}/{clean_name}"
        
        elif category == 'shared':
            resource_type = self._map_shared_subcategory(subcategory)
            return f"shared/{resource_type}/{clean_name}"
        
        elif category == 'docs':
            doc_type = self._map_docs_subcategory(subcategory)
            return f"docs/{doc_type}/{clean_name}"
        
        elif category == 'infrastructure':
            return f"tools/{subcategory}/{clean_name}"
        
        else:
            return f"archive/uncategorized/{clean_name}"
    
    def _clean_name(self, name: str) -> str:
        """清理名称，转换为标准格式"""
        import re
        
        # 移除特殊字符，转换为小写
        clean = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff\-_]', '-', name)
        clean = clean.lower()
        
        # 处理中文字符（保留但用拼音替换更好）
        # 这里简化处理，实际应该使用拼音转换库
        clean = re.sub(r'[\u4e00-\u9fff]+', 'chinese-project', clean)
        
        # 清理多余的连字符
        clean = re.sub(r'-+', '-', clean)
        clean = clean.strip('-')
        
        return clean or 'unnamed-project'
    
    def _extract_year_from_path(self, path: str) -> Optional[str]:
        """从路径中提取年份"""
        import re
        match = re.search(r'20\d{2}', path)
        return match.group(0) if match else None
    
    def _map_competition_subcategory(self, subcategory: str) -> str:
        """映射竞赛子类别"""
        mapping = {
            'electronics': 'electronics-competition',
            'robotics': 'robotics-robocon',
            'ai': 'ai-huawei-cloud',
            'iot': 'iot-design-competition',
            'energy': 'energy-saving-competition',
            'traffic': 'traffic-design-competition',
            'other': 'other-competitions'
        }
        return mapping.get(subcategory, 'other-competitions')
    
    def _map_project_subcategory(self, subcategory: str) -> str:
        """映射项目子类别"""
        mapping = {
            'ai': 'ai',
            'embedded': 'embedded',
            'robotics': 'robotics',
            'research': 'research',
            'templates': 'templates',
            'other': 'misc'
        }
        return mapping.get(subcategory, 'misc')
    
    def _map_shared_subcategory(self, subcategory: str) -> str:
        """映射共享资源子类别"""
        mapping = {
            'assets': 'assets',
            'models': 'models',
            'libraries': 'libraries',
            'tools': 'tools',
            'other': 'misc'
        }
        return mapping.get(subcategory, 'misc')
    
    def _map_docs_subcategory(self, subcategory: str) -> str:
        """映射文档子类别"""
        mapping = {
            'api': 'api',
            'user': 'guides',
            'developer': 'references',
            'tutorial': 'tutorials',
            'other': 'misc'
        }
        return mapping.get(subcategory, 'misc')
    
    def create_directory_structure(self) -> bool:
        """创建目录结构"""
        if not self.blueprint:
            raise ValueError("请先运行 design_structure_blueprint()")
        
        logging.info("开始创建标准化目录结构")
        
        try:
            # 创建根目录
            for dir_spec in self.blueprint.root_directories:
                self._create_directory_tree(dir_spec)
            
            # 创建根目录 README
            self._create_root_readme()
            
            logging.info("目录结构创建完成")
            return True
        
        except Exception as e:
            logging.error(f"创建目录结构失败: {e}")
            return False
    
    def _create_directory_tree(self, dir_spec: DirectorySpec):
        """创建目录树"""
        base_path = self.root_path / dir_spec.path
        
        # 创建主目录
        base_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"创建目录: {base_path}")
        
        # 创建子目录
        for subdir in dir_spec.subdirectories:
            subdir_path = base_path / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
            logging.info(f"创建子目录: {subdir_path}")
            
            # 为子目录创建 README
            self._create_subdirectory_readme(subdir_path, dir_spec, subdir)
        
        # 创建必需文件
        for required_file in dir_spec.required_files:
            file_path = base_path / required_file
            if not file_path.exists():
                self._create_directory_readme(file_path, dir_spec)
    
    def _create_directory_readme(self, file_path: Path, dir_spec: DirectorySpec):
        """创建目录 README 文件"""
        content = f"""
# {dir_spec.name.title()}

> {dir_spec.description}

## 📋 目录说明

**用途**：{dir_spec.purpose}

**访问级别**：{dir_spec.access_level}

**最大深度**：{dir_spec.max_depth} 层

**命名规范**：`{dir_spec.naming_convention}`

## 📁 子目录

"""
        
        for subdir in dir_spec.subdirectories:
            content += f"- `{subdir}/` - {self._get_subdirectory_description(dir_spec.name, subdir)}\n"
        
        content += f"""

## 📖 使用示例

"""
        
        for example in dir_spec.examples:
            content += f"- `{example}`\n"
        
        content += f"""

## 📝 文件要求

### 必需文件
"""
        
        for required_file in dir_spec.required_files:
            content += f"- `{required_file}`\n"
        
        if dir_spec.optional_files:
            content += "\n### 可选文件\n"
            for optional_file in dir_spec.optional_files:
                content += f"- `{optional_file}`\n"
        
        content += f"""

## 🚀 快速开始

1. 在相应子目录下创建项目文件夹
2. 添加项目 README.md 文件
3. 按照命名规范组织文件结构
4. 更新上级目录的索引文件

---

📅 最后更新：{datetime.now().strftime('%Y-%m-%d')}
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"创建 README: {file_path}")
    
    def _create_subdirectory_readme(self, subdir_path: Path, parent_spec: DirectorySpec, subdir_name: str):
        """创建子目录 README 文件"""
        readme_path = subdir_path / "README.md"
        
        if readme_path.exists():
            return
        
        description = self._get_subdirectory_description(parent_spec.name, subdir_name)
        
        content = f"""
# {subdir_name.title().replace('-', ' ')}

> {description}

## 📋 目录信息

- **父目录**：{parent_spec.name}
- **类型**：{subdir_name}
- **用途**：{description}

## 📁 项目列表

<!-- 请在此处添加项目列表 -->

| 项目名称 | 描述 | 状态 | 最后更新 |
|---------|------|------|----------|
| 示例项目 | 项目描述 | 开发中 | 2025-01-18 |

## 🚀 添加新项目

1. 创建项目目录：`mkdir your-project-name`
2. 添加项目 README：`touch your-project-name/README.md`
3. 更新上述项目列表
4. 提交更改到版本控制

## 📝 命名规范

- 使用 kebab-case 命名（小写字母，连字符分隔）
- 避免使用空格和特殊字符
- 名称应简洁明了，不超过50字符

---

📅 创建时间：{datetime.now().strftime('%Y-%m-%d')}
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"创建子目录 README: {readme_path}")
    
    def _get_subdirectory_description(self, parent_name: str, subdir_name: str) -> str:
        """获取子目录描述"""
        descriptions = {
            'competitions': {
                '2024': '2024年度竞赛项目',
                '2025': '2025年度竞赛项目',
                'archive': '历史竞赛项目归档'
            },
            'projects': {
                'ai': '人工智能相关项目',
                'embedded': '嵌入式系统项目',
                'robotics': '机器人技术项目',
                'research': '科研和横向项目',
                'templates': '项目模板和脚手架'
            },
            'shared': {
                'assets': '共享资源文件（图片、视频等）',
                'libraries': '共享代码库和组件',
                'models': '3D模型和设计文件',
                'tools': '共享工具和脚本',
                'templates': '通用模板文件'
            },
            'docs': {
                'guides': '使用指南和教程',
                'api': 'API文档和接口说明',
                'tutorials': '详细教程和示例',
                'references': '参考文档和规范',
                'archive': '历史文档归档'
            },
            'tools': {
                'automation': '自动化脚本和工具',
                'testing': '测试工具和框架',
                'deployment': '部署和发布工具',
                'monitoring': '监控和分析工具',
                'utilities': '通用工具和实用程序'
            },
            'archive': {
                '2023': '2023年历史项目',
                '2024': '2024年历史项目',
                'deprecated': '已废弃的项目和工具',
                'backup': '备份和迁移文件'
            }
        }
        
        return descriptions.get(parent_name, {}).get(subdir_name, f'{subdir_name} 相关内容')
    
    def _create_root_readme(self):
        """创建根目录 README 文件"""
        readme_path = self.root_path / "README.md"
        
        # 统计信息
        stats = self._calculate_structure_stats()
        
        template = self.blueprint.file_templates.get('root_readme', '')
        
        # 替换模板变量
        content = template.replace('{{club_name}}', '新能源编程俱乐部')
        content = content.replace('{{total_projects}}', str(stats.get('total_projects', 0)))
        content = content.replace('{{competition_count}}', str(stats.get('competition_count', 0)))
        content = content.replace('{{project_count}}', str(stats.get('project_count', 0)))
        content = content.replace('{{shared_count}}', str(stats.get('shared_count', 0)))
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"创建根目录 README: {readme_path}")
    
    def _calculate_structure_stats(self) -> Dict[str, int]:
        """计算结构统计信息"""
        if not self.analysis_report:
            return {}
        
        categories = self.analysis_report.get('categories', {})
        
        return {
            'total_projects': self.analysis_report.get('total_projects', 0),
            'competition_count': categories.get('competitions', 0),
            'project_count': categories.get('projects', 0),
            'shared_count': categories.get('shared', 0)
        }
    
    def save_blueprint(self, output_file: str = None) -> str:
        """保存结构蓝图"""
        if not self.blueprint:
            raise ValueError("请先运行 design_structure_blueprint()")
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'structure_blueprint_{timestamp}.json'
        
        output_path = self.root_path / output_file
        
        # 转换为可序列化的格式
        blueprint_dict = asdict(self.blueprint)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(blueprint_dict, f, ensure_ascii=False, indent=2)
        
        logging.info(f"结构蓝图已保存到: {output_path}")
        return str(output_path)
    
    def generate_structure_documentation(self, output_file: str = None) -> str:
        """生成结构文档"""
        if not self.blueprint:
            raise ValueError("请先运行 design_structure_blueprint()")
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'structure_documentation_{timestamp}.md'
        
        output_path = self.root_path / output_file
        
        content = self._generate_documentation_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logging.info(f"结构文档已生成: {output_path}")
        return str(output_path)
    
    def _generate_documentation_content(self) -> str:
        """生成文档内容"""
        blueprint = self.blueprint
        
        content = f"""
# 新能源编程俱乐部目录结构设计文档

> 版本：{blueprint.version}  
> 创建时间：{blueprint.created_at}  
> 描述：{blueprint.description}

## 🎯 设计原则

"""
        
        for i, principle in enumerate(blueprint.principles, 1):
            content += f"{i}. {principle}\n"
        
        content += """

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

"""
        
        for dir_spec in blueprint.root_directories:
            content += f"""
### {dir_spec.name}/ - {dir_spec.description}

**访问级别**：{dir_spec.access_level}  
**最大深度**：{dir_spec.max_depth} 层  
**命名规范**：`{dir_spec.naming_convention}`

**用途**：{dir_spec.purpose}

**子目录**：
"""
            for subdir in dir_spec.subdirectories:
                desc = self._get_subdirectory_description(dir_spec.name, subdir)
                content += f"- `{subdir}/` - {desc}\n"
            
            content += "\n**示例路径**:\n"
            for example in dir_spec.examples:
                content += f"- `{example}`\n"
            
            content += "\n**必需文件**:\n"
            for required_file in dir_spec.required_files:
                content += f"- `{required_file}`\n"
            
            if dir_spec.optional_files:
                content += "\n**可选文件**:\n"
                for optional_file in dir_spec.optional_files:
                    content += f"- `{optional_file}`\n"
            
            content += "\n---\n\n"
        
        content += """
## 📝 命名规范

"""
        
        for rule_type, rule_desc in blueprint.naming_rules.items():
            content += f"- **{rule_type}**：{rule_desc}\n"
        
        content += f"""

## 🔄 迁移映射

基于项目分析结果，生成了 {len(blueprint.migration_mapping)} 个项目的迁移映射。

### 示例映射

| 原路径 | 新路径 | 说明 |
|--------|--------|------|
"""
        
        # 显示前10个映射示例
        for i, (old_path, new_path) in enumerate(list(blueprint.migration_mapping.items())[:10]):
            content += f"| `{old_path}` | `{new_path}` | 自动映射 |\n"
        
        if len(blueprint.migration_mapping) > 10:
            content += f"| ... | ... | 还有 {len(blueprint.migration_mapping) - 10} 个映射 |\n"
        
        content += f"""

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

📅 文档生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return content

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新能源编程俱乐部标准化目录结构构建器")
    parser.add_argument('--root', '-r', default='.', help='项目根目录路径')
    parser.add_argument('--analysis', '-a', help='项目分析报告路径')
    parser.add_argument('--create', '-c', action='store_true', help='创建目录结构')
    parser.add_argument('--blueprint', '-b', action='store_true', help='生成结构蓝图')
    parser.add_argument('--docs', '-d', action='store_true', help='生成结构文档')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 初始化构建器
        builder = StructureBuilder(args.root, args.analysis)
        
        # 设计结构蓝图
        print("设计标准化目录结构蓝图...")
        blueprint = builder.design_structure_blueprint()
        
        generated_files = []
        
        # 保存蓝图
        if args.blueprint:
            blueprint_file = builder.save_blueprint()
            generated_files.append(('蓝图', blueprint_file))
        
        # 生成文档
        if args.docs:
            docs_file = builder.generate_structure_documentation()
            generated_files.append(('文档', docs_file))
        
        # 创建目录结构
        if args.create:
            success = builder.create_directory_structure()
            if success:
                print("✅ 目录结构创建成功")
            else:
                print("❌ 目录结构创建失败")
        
        # 输出摘要
        print(f"\n结构设计完成！")
        print(f"根目录数量: {len(blueprint.root_directories)}")
        print(f"设计原则: {len(blueprint.principles)} 条")
        print(f"迁移映射: {len(blueprint.migration_mapping)} 个")
        
        if generated_files:
            print("\n生成的文件:")
            for file_type, file_path in generated_files:
                print(f"  {file_type}: {file_path}")
        
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        logging.error(f"结构构建失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()