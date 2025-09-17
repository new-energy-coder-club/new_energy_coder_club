#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新能源编程俱乐部项目结构分析器

功能:
- 分析现有项目结构
- 生成项目清单和分类表
- 统计项目规模和复杂度
- 识别迁移优先级
- 生成分析报告

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
from collections import defaultdict, Counter
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('project_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

@dataclass
class ProjectInfo:
    """项目信息数据结构"""
    name: str
    path: str
    category: str
    subcategory: str
    size_mb: float
    file_count: int
    directory_count: int
    readme_exists: bool
    has_code: bool
    has_docs: bool
    has_images: bool
    has_models: bool
    languages: List[str]
    last_modified: str
    priority: str
    complexity: str
    migration_difficulty: str
    description: str
    tags: List[str]

@dataclass
class AnalysisReport:
    """分析报告数据结构"""
    timestamp: str
    total_projects: int
    categories: Dict[str, int]
    subcategories: Dict[str, int]
    total_size_mb: float
    total_files: int
    total_directories: int
    languages_stats: Dict[str, int]
    priority_distribution: Dict[str, int]
    complexity_distribution: Dict[str, int]
    migration_difficulty_stats: Dict[str, int]
    projects: List[ProjectInfo]
    recommendations: List[str]
    migration_plan: Dict[str, List[str]]

class ProjectAnalyzer:
    """项目结构分析器"""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.projects = []
        self.analysis_report = None
        
        # 项目分类规则
        self.category_rules = {
            'competitions': {
                'pattern': r'competitions?',
                'subcategories': {
                    'electronics': ['electronics', 'electronic'],
                    'robotics': ['robocon', 'robot', 'smart-car'],
                    'ai': ['ai', 'huawei-cloud'],
                    'iot': ['iot', 'design'],
                    'energy': ['energy-saving', 'energy'],
                    'traffic': ['traffic']
                }
            },
            'projects': {
                'pattern': r'projects?',
                'subcategories': {
                    'ai': ['ai', 'machine-learning', 'deep-learning'],
                    'embedded': ['embedded', 'mcu', 'arduino'],
                    'robotics': ['robotics', 'robot', 'robocon'],
                    'research': ['research', '科研', 'horizontal'],
                    'templates': ['template']
                }
            },
            'shared': {
                'pattern': r'shared',
                'subcategories': {
                    'assets': ['images', 'videos', 'assets'],
                    'models': ['models', '3d'],
                    'libraries': ['lib', 'libraries'],
                    'tools': ['tools', 'utils']
                }
            },
            'docs': {
                'pattern': r'docs?',
                'subcategories': {
                    'api': ['api'],
                    'user': ['user', 'guide'],
                    'developer': ['dev', 'developer'],
                    'tutorial': ['tutorial', 'example']
                }
            },
            'infrastructure': {
                'pattern': r'(scripts?|config|templates?|\.github)',
                'subcategories': {
                    'automation': ['scripts', 'ci', 'cd'],
                    'configuration': ['config', 'settings'],
                    'templates': ['templates', 'template'],
                    'workflows': ['github', 'workflow']
                }
            }
        }
        
        # 编程语言识别
        self.language_extensions = {
            'Python': ['.py', '.pyw', '.pyx'],
            'C/C++': ['.c', '.cpp', '.cxx', '.cc', '.h', '.hpp', '.hxx'],
            'JavaScript': ['.js', '.jsx', '.ts', '.tsx'],
            'Java': ['.java'],
            'C#': ['.cs'],
            'Go': ['.go'],
            'Rust': ['.rs'],
            'MATLAB': ['.m'],
            'R': ['.r', '.R'],
            'Shell': ['.sh', '.bash', '.zsh'],
            'PowerShell': ['.ps1'],
            'HTML': ['.html', '.htm'],
            'CSS': ['.css', '.scss', '.sass'],
            'Markdown': ['.md', '.markdown'],
            'YAML': ['.yml', '.yaml'],
            'JSON': ['.json'],
            'XML': ['.xml'],
            'Dockerfile': ['Dockerfile'],
            'Makefile': ['Makefile', 'makefile']
        }
        
        # 忽略的目录和文件
        self.ignore_patterns = {
            '.git', '.svn', '.hg',
            '__pycache__', '.pytest_cache',
            'node_modules', '.npm',
            '.vscode', '.idea',
            'build', 'dist', 'target',
            '.DS_Store', 'Thumbs.db'
        }
    
    def analyze_project_structure(self) -> AnalysisReport:
        """分析项目结构"""
        logging.info(f"开始分析项目结构: {self.root_path}")
        
        # 扫描所有项目
        self._scan_projects()
        
        # 生成分析报告
        self.analysis_report = self._generate_analysis_report()
        
        logging.info(f"项目结构分析完成，共发现 {len(self.projects)} 个项目")
        return self.analysis_report
    
    def _scan_projects(self):
        """扫描项目目录"""
        for root, dirs, files in os.walk(self.root_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            root_path = Path(root)
            relative_path = root_path.relative_to(self.root_path)
            
            # 跳过根目录和一级目录
            if len(relative_path.parts) < 2:
                continue
            
            # 检查是否为项目目录
            if self._is_project_directory(root_path, files):
                project_info = self._analyze_project(root_path, files)
                if project_info:
                    self.projects.append(project_info)
    
    def _is_project_directory(self, path: Path, files: List[str]) -> bool:
        """判断是否为项目目录"""
        # 包含README文件
        has_readme = any(f.lower().startswith('readme') for f in files)
        
        # 包含代码文件
        has_code = any(self._get_file_language(f) for f in files)
        
        # 包含配置文件
        config_files = {
            'package.json', 'requirements.txt', 'Cargo.toml',
            'pom.xml', 'build.gradle', 'CMakeLists.txt',
            'Makefile', 'Dockerfile', '.gitignore'
        }
        has_config = any(f in config_files for f in files)
        
        # 目录深度合理（避免过深的子目录）
        relative_path = path.relative_to(self.root_path)
        reasonable_depth = len(relative_path.parts) <= 4
        
        return (has_readme or has_code or has_config) and reasonable_depth
    
    def _analyze_project(self, path: Path, files: List[str]) -> Optional[ProjectInfo]:
        """分析单个项目"""
        try:
            relative_path = path.relative_to(self.root_path)
            project_name = path.name
            
            # 计算项目大小和文件统计
            size_mb, file_count, dir_count = self._calculate_project_size(path)
            
            # 分析项目类别
            category, subcategory = self._classify_project(relative_path)
            
            # 检查文件类型
            readme_exists = any(f.lower().startswith('readme') for f in files)
            has_code = any(self._get_file_language(f) for f in files)
            has_docs = any(f.endswith(('.md', '.rst', '.txt', '.pdf')) for f in files)
            has_images = any(f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')) for f in files)
            has_models = any(f.lower().endswith(('.step', '.stl', '.obj', '.fbx', '.blend')) for f in files)
            
            # 识别编程语言
            languages = self._identify_languages(path)
            
            # 获取最后修改时间
            last_modified = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            
            # 评估优先级和复杂度
            priority = self._assess_priority(category, subcategory, size_mb, has_code)
            complexity = self._assess_complexity(size_mb, file_count, languages)
            migration_difficulty = self._assess_migration_difficulty(size_mb, file_count, has_code, languages)
            
            # 生成描述和标签
            description = self._generate_description(path, category, subcategory)
            tags = self._generate_tags(category, subcategory, languages, has_code, has_docs)
            
            return ProjectInfo(
                name=project_name,
                path=str(relative_path),
                category=category,
                subcategory=subcategory,
                size_mb=size_mb,
                file_count=file_count,
                directory_count=dir_count,
                readme_exists=readme_exists,
                has_code=has_code,
                has_docs=has_docs,
                has_images=has_images,
                has_models=has_models,
                languages=languages,
                last_modified=last_modified,
                priority=priority,
                complexity=complexity,
                migration_difficulty=migration_difficulty,
                description=description,
                tags=tags
            )
        
        except Exception as e:
            logging.error(f"分析项目 {path} 时出错: {e}")
            return None
    
    def _calculate_project_size(self, path: Path) -> Tuple[float, int, int]:
        """计算项目大小和文件统计"""
        total_size = 0
        file_count = 0
        dir_count = 0
        
        for root, dirs, files in os.walk(path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            dir_count += len(dirs)
            file_count += len(files)
            
            for file in files:
                try:
                    file_path = Path(root) / file
                    total_size += file_path.stat().st_size
                except (OSError, IOError):
                    continue
        
        return total_size / (1024 * 1024), file_count, dir_count  # 转换为MB
    
    def _classify_project(self, relative_path: Path) -> Tuple[str, str]:
        """分类项目"""
        path_str = str(relative_path).lower()
        
        for category, rules in self.category_rules.items():
            if re.search(rules['pattern'], path_str):
                # 查找子类别
                for subcategory, keywords in rules['subcategories'].items():
                    if any(keyword in path_str for keyword in keywords):
                        return category, subcategory
                return category, 'other'
        
        return 'other', 'unknown'
    
    def _get_file_language(self, filename: str) -> Optional[str]:
        """识别文件编程语言"""
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        for language, extensions in self.language_extensions.items():
            if extension in extensions or filename in extensions:
                return language
        
        return None
    
    def _identify_languages(self, path: Path) -> List[str]:
        """识别项目中的编程语言"""
        languages = set()
        
        for root, dirs, files in os.walk(path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            for file in files:
                language = self._get_file_language(file)
                if language:
                    languages.add(language)
        
        return sorted(list(languages))
    
    def _assess_priority(self, category: str, subcategory: str, size_mb: float, has_code: bool) -> str:
        """评估项目优先级"""
        # 高优先级：核心项目、大型项目、有代码的项目
        if category in ['projects', 'competitions'] and has_code and size_mb > 10:
            return 'high'
        
        # 中优先级：中等规模项目、文档项目
        if (category in ['projects', 'competitions'] and size_mb > 1) or category == 'docs':
            return 'medium'
        
        # 低优先级：小型项目、基础设施项目
        return 'low'
    
    def _assess_complexity(self, size_mb: float, file_count: int, languages: List[str]) -> str:
        """评估项目复杂度"""
        complexity_score = 0
        
        # 大小因子
        if size_mb > 100:
            complexity_score += 3
        elif size_mb > 10:
            complexity_score += 2
        elif size_mb > 1:
            complexity_score += 1
        
        # 文件数量因子
        if file_count > 100:
            complexity_score += 2
        elif file_count > 20:
            complexity_score += 1
        
        # 语言多样性因子
        complexity_score += min(len(languages), 3)
        
        if complexity_score >= 6:
            return 'high'
        elif complexity_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _assess_migration_difficulty(self, size_mb: float, file_count: int, has_code: bool, languages: List[str]) -> str:
        """评估迁移难度"""
        difficulty_score = 0
        
        # 大小因子
        if size_mb > 50:
            difficulty_score += 3
        elif size_mb > 5:
            difficulty_score += 2
        elif size_mb > 0.5:
            difficulty_score += 1
        
        # 文件数量因子
        if file_count > 50:
            difficulty_score += 2
        elif file_count > 10:
            difficulty_score += 1
        
        # 代码复杂度因子
        if has_code:
            difficulty_score += 1
            if len(languages) > 2:
                difficulty_score += 1
        
        if difficulty_score >= 5:
            return 'hard'
        elif difficulty_score >= 3:
            return 'medium'
        else:
            return 'easy'
    
    def _generate_description(self, path: Path, category: str, subcategory: str) -> str:
        """生成项目描述"""
        descriptions = {
            'competitions': f'{subcategory}类竞赛项目',
            'projects': f'{subcategory}类开发项目',
            'shared': f'共享{subcategory}资源',
            'docs': f'{subcategory}类文档',
            'infrastructure': f'{subcategory}类基础设施'
        }
        
        base_desc = descriptions.get(category, '其他类型项目')
        
        # 尝试从README获取更多信息
        readme_files = ['README.md', 'readme.md', 'README.txt', 'readme.txt']
        for readme_file in readme_files:
            readme_path = path / readme_file
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:200]  # 读取前200字符
                        # 提取第一行作为简短描述
                        first_line = content.split('\n')[0].strip('#').strip()
                        if first_line and len(first_line) < 100:
                            return first_line
                except Exception:
                    pass
        
        return base_desc
    
    def _generate_tags(self, category: str, subcategory: str, languages: List[str], has_code: bool, has_docs: bool) -> List[str]:
        """生成项目标签"""
        tags = [category, subcategory]
        
        if has_code:
            tags.append('code')
        if has_docs:
            tags.append('documentation')
        
        # 添加主要编程语言
        if languages:
            tags.extend(languages[:3])  # 最多添加3种语言
        
        return list(set(tags))  # 去重
    
    def _generate_analysis_report(self) -> AnalysisReport:
        """生成分析报告"""
        # 统计信息
        categories = Counter(p.category for p in self.projects)
        subcategories = Counter(p.subcategory for p in self.projects)
        total_size_mb = sum(p.size_mb for p in self.projects)
        total_files = sum(p.file_count for p in self.projects)
        total_directories = sum(p.directory_count for p in self.projects)
        
        # 语言统计
        languages_stats = Counter()
        for project in self.projects:
            for language in project.languages:
                languages_stats[language] += 1
        
        # 优先级和复杂度分布
        priority_distribution = Counter(p.priority for p in self.projects)
        complexity_distribution = Counter(p.complexity for p in self.projects)
        migration_difficulty_stats = Counter(p.migration_difficulty for p in self.projects)
        
        # 生成建议
        recommendations = self._generate_recommendations()
        
        # 生成迁移计划
        migration_plan = self._generate_migration_plan()
        
        return AnalysisReport(
            timestamp=datetime.now().isoformat(),
            total_projects=len(self.projects),
            categories=dict(categories),
            subcategories=dict(subcategories),
            total_size_mb=total_size_mb,
            total_files=total_files,
            total_directories=total_directories,
            languages_stats=dict(languages_stats),
            priority_distribution=dict(priority_distribution),
            complexity_distribution=dict(complexity_distribution),
            migration_difficulty_stats=dict(migration_difficulty_stats),
            projects=self.projects,
            recommendations=recommendations,
            migration_plan=migration_plan
        )
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 分析项目分布
        categories = Counter(p.category for p in self.projects)
        
        if categories.get('other', 0) > len(self.projects) * 0.2:
            recommendations.append("建议重新分类未分类的项目，提高目录结构的清晰度")
        
        # 分析大型项目
        large_projects = [p for p in self.projects if p.size_mb > 50]
        if large_projects:
            recommendations.append(f"发现 {len(large_projects)} 个大型项目，建议优先迁移并考虑拆分")
        
        # 分析无README项目
        no_readme_projects = [p for p in self.projects if not p.readme_exists]
        if no_readme_projects:
            recommendations.append(f"发现 {len(no_readme_projects)} 个项目缺少README文件，建议补充文档")
        
        # 分析语言分布
        languages_stats = Counter()
        for project in self.projects:
            for language in project.languages:
                languages_stats[language] += 1
        
        if len(languages_stats) > 10:
            recommendations.append("项目使用的编程语言较多，建议按语言类型进一步组织项目结构")
        
        return recommendations
    
    def _generate_migration_plan(self) -> Dict[str, List[str]]:
        """生成迁移计划"""
        plan = {
            'phase1_high_priority': [],
            'phase2_medium_priority': [],
            'phase3_low_priority': [],
            'phase4_infrastructure': []
        }
        
        for project in self.projects:
            if project.priority == 'high':
                plan['phase1_high_priority'].append(project.path)
            elif project.priority == 'medium':
                plan['phase2_medium_priority'].append(project.path)
            elif project.category == 'infrastructure':
                plan['phase4_infrastructure'].append(project.path)
            else:
                plan['phase3_low_priority'].append(project.path)
        
        return plan
    
    def save_report(self, output_file: str = None) -> str:
        """保存分析报告"""
        if not self.analysis_report:
            raise ValueError("请先运行 analyze_project_structure()")
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'project_analysis_report_{timestamp}.json'
        
        output_path = self.root_path / output_file
        
        # 转换为可序列化的格式
        report_dict = asdict(self.analysis_report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
        
        logging.info(f"分析报告已保存到: {output_path}")
        return str(output_path)
    
    def generate_html_report(self, output_file: str = None) -> str:
        """生成HTML格式报告"""
        if not self.analysis_report:
            raise ValueError("请先运行 analyze_project_structure()")
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'project_analysis_report_{timestamp}.html'
        
        output_path = self.root_path / output_file
        
        html_content = self._generate_html_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logging.info(f"HTML报告已生成: {output_path}")
        return str(output_path)
    
    def _generate_html_content(self) -> str:
        """生成HTML报告内容"""
        report = self.analysis_report
        
        # 生成项目表格
        projects_table = ""
        for project in sorted(report.projects, key=lambda p: (p.priority, -p.size_mb)):
            priority_class = f"priority-{project.priority}"
            complexity_class = f"complexity-{project.complexity}"
            
            projects_table += f"""
            <tr class="{priority_class}">
                <td>{project.name}</td>
                <td>{project.category}</td>
                <td>{project.subcategory}</td>
                <td>{project.size_mb:.2f} MB</td>
                <td>{project.file_count}</td>
                <td>{'✓' if project.readme_exists else '✗'}</td>
                <td>{'✓' if project.has_code else '✗'}</td>
                <td>{', '.join(project.languages[:3])}</td>
                <td><span class="{priority_class}">{project.priority}</span></td>
                <td><span class="{complexity_class}">{project.complexity}</span></td>
                <td>{project.migration_difficulty}</td>
                <td title="{project.description}">{project.description[:50]}...</td>
            </tr>
            """
        
        # 生成统计图表数据
        categories_data = json.dumps(list(report.categories.items()))
        languages_data = json.dumps(list(report.languages_stats.items()))
        
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目结构分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .charts-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .projects-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .projects-table th,
        .projects-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .projects-table th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .priority-high {{
            background-color: #fff5f5;
        }}
        .priority-medium {{
            background-color: #fffbf0;
        }}
        .priority-low {{
            background-color: #f0fff4;
        }}
        .complexity-high {{
            color: #dc3545;
            font-weight: bold;
        }}
        .complexity-medium {{
            color: #ffc107;
            font-weight: bold;
        }}
        .complexity-low {{
            color: #28a745;
            font-weight: bold;
        }}
        .recommendations {{
            background: #e7f3ff;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
        }}
        .recommendations h3 {{
            color: #0066cc;
            margin-top: 0;
        }}
        .recommendations ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .migration-plan {{
            background: #f0f8f0;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .migration-plan h3 {{
            color: #006600;
            margin-top: 0;
        }}
        .phase {{
            margin-bottom: 15px;
        }}
        .phase h4 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .phase ul {{
            margin: 0;
            padding-left: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>项目结构分析报告</h1>
            <p>生成时间: {report.timestamp}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{report.total_projects}</div>
                <div class="stat-label">总项目数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.total_size_mb:.1f} MB</div>
                <div class="stat-label">总大小</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.total_files:,}</div>
                <div class="stat-label">总文件数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(report.languages_stats)}</div>
                <div class="stat-label">编程语言数</div>
            </div>
        </div>
        
        <div class="charts-container">
            <div class="chart-container">
                <h3>项目分类分布</h3>
                <canvas id="categoriesChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>编程语言分布</h3>
                <canvas id="languagesChart"></canvas>
            </div>
        </div>
        
        <h2>项目详细列表</h2>
        <table class="projects-table">
            <thead>
                <tr>
                    <th>项目名称</th>
                    <th>类别</th>
                    <th>子类别</th>
                    <th>大小</th>
                    <th>文件数</th>
                    <th>README</th>
                    <th>代码</th>
                    <th>语言</th>
                    <th>优先级</th>
                    <th>复杂度</th>
                    <th>迁移难度</th>
                    <th>描述</th>
                </tr>
            </thead>
            <tbody>
                {projects_table}
            </tbody>
        </table>
        
        <div class="recommendations">
            <h3>优化建议</h3>
            <ul>
        """
        
        for recommendation in report.recommendations:
            html_template += f"<li>{recommendation}</li>"
        
        html_template += """
            </ul>
        </div>
        
        <div class="migration-plan">
            <h3>迁移计划</h3>
        """
        
        phase_names = {
            'phase1_high_priority': '第一阶段：高优先级项目',
            'phase2_medium_priority': '第二阶段：中优先级项目',
            'phase3_low_priority': '第三阶段：低优先级项目',
            'phase4_infrastructure': '第四阶段：基础设施项目'
        }
        
        for phase_key, projects in report.migration_plan.items():
            if projects:
                phase_name = phase_names.get(phase_key, phase_key)
                html_template += f"""
                <div class="phase">
                    <h4>{phase_name} ({len(projects)} 个项目)</h4>
                    <ul>
                """
                for project_path in projects[:10]:  # 只显示前10个
                    html_template += f"<li>{project_path}</li>"
                if len(projects) > 10:
                    html_template += f"<li>... 还有 {len(projects) - 10} 个项目</li>"
                html_template += "</ul></div>"
        
        html_template += f"""
        </div>
    </div>
    
    <script>
        // 项目分类饼图
        const categoriesCtx = document.getElementById('categoriesChart').getContext('2d');
        const categoriesData = {categories_data};
        new Chart(categoriesCtx, {{
            type: 'pie',
            data: {{
                labels: categoriesData.map(item => item[0]),
                datasets: [{{
                    data: categoriesData.map(item => item[1]),
                    backgroundColor: [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // 编程语言柱状图
        const languagesCtx = document.getElementById('languagesChart').getContext('2d');
        const languagesData = {languages_data};
        new Chart(languagesCtx, {{
            type: 'bar',
            data: {{
                labels: languagesData.map(item => item[0]),
                datasets: [{{
                    label: '项目数量',
                    data: languagesData.map(item => item[1]),
                    backgroundColor: '#36A2EB'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
        
        return html_template
    
    def generate_csv_report(self, output_file: str = None) -> str:
        """生成CSV格式报告"""
        if not self.analysis_report:
            raise ValueError("请先运行 analyze_project_structure()")
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'project_analysis_report_{timestamp}.csv'
        
        output_path = self.root_path / output_file
        
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow([
                '项目名称', '路径', '类别', '子类别', '大小(MB)', '文件数', '目录数',
                'README存在', '包含代码', '包含文档', '包含图片', '包含模型',
                '编程语言', '最后修改时间', '优先级', '复杂度', '迁移难度', '描述', '标签'
            ])
            
            # 写入数据行
            for project in self.analysis_report.projects:
                writer.writerow([
                    project.name,
                    project.path,
                    project.category,
                    project.subcategory,
                    f"{project.size_mb:.2f}",
                    project.file_count,
                    project.directory_count,
                    '是' if project.readme_exists else '否',
                    '是' if project.has_code else '否',
                    '是' if project.has_docs else '否',
                    '是' if project.has_images else '否',
                    '是' if project.has_models else '否',
                    ', '.join(project.languages),
                    project.last_modified,
                    project.priority,
                    project.complexity,
                    project.migration_difficulty,
                    project.description,
                    ', '.join(project.tags)
                ])
        
        logging.info(f"CSV报告已生成: {output_path}")
        return str(output_path)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新能源编程俱乐部项目结构分析器")
    parser.add_argument('--root', '-r', default='.', help='项目根目录路径')
    parser.add_argument('--output', '-o', nargs='+',
                       choices=['json', 'html', 'csv'],
                       default=['json', 'html'],
                       help='报告输出格式')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 初始化分析器
        analyzer = ProjectAnalyzer(args.root)
        
        # 运行分析
        print("开始分析项目结构...")
        report = analyzer.analyze_project_structure()
        
        # 生成报告
        generated_files = []
        
        if 'json' in args.output:
            json_file = analyzer.save_report()
            generated_files.append(('JSON', json_file))
        
        if 'html' in args.output:
            html_file = analyzer.generate_html_report()
            generated_files.append(('HTML', html_file))
        
        if 'csv' in args.output:
            csv_file = analyzer.generate_csv_report()
            generated_files.append(('CSV', csv_file))
        
        # 输出摘要
        print(f"\n分析完成！")
        print(f"总项目数: {report.total_projects}")
        print(f"总大小: {report.total_size_mb:.1f} MB")
        print(f"总文件数: {report.total_files:,}")
        print(f"编程语言数: {len(report.languages_stats)}")
        
        print("\n报告已生成:")
        for format_type, file_path in generated_files:
            print(f"  {format_type}: {file_path}")
        
    except KeyboardInterrupt:
        print("\n分析被用户中断")
    except Exception as e:
        logging.error(f"项目分析失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()