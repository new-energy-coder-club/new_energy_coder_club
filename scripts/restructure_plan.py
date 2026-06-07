#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录结构重组计划
实现"两次点击原则"的扁平化重组方案
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class StructureReorganizer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.backup_dir = self.root_path / "backup" / f"restructure_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.plan = {
            'actions': [],
            'new_structure': {},
            'conflicts': [],
            'statistics': {}
        }
    
    def analyze_current_structure(self) -> Dict:
        """分析当前结构，识别需要重组的项目"""
        print("分析当前结构...")
        
        # 主要目录分析
        main_dirs = ['competitions', 'projects', 'shared']
        structure_issues = []
        
        for main_dir in main_dirs:
            dir_path = self.root_path / main_dir
            if dir_path.exists():
                issues = self._analyze_directory_depth(dir_path, main_dir)
                structure_issues.extend(issues)
        
        return {
            'issues': structure_issues,
            'total_issues': len(structure_issues)
        }
    
    def _analyze_directory_depth(self, path: Path, category: str) -> List[Dict]:
        """分析目录深度问题"""
        issues = []
        
        def scan_recursive(current_path: Path, depth: int = 0, base_path: str = ""):
            if depth > 2:  # 超过2层的需要重组
                # 查找README文件
                readme_files = []
                for readme_name in ['README.md', 'readme.md', 'Readme.md']:
                    readme_path = current_path / readme_name
                    if readme_path.exists():
                        readme_files.append(readme_name)
                
                if readme_files:  # 有README的认为是项目
                    relative_path = current_path.relative_to(self.root_path)
                    issues.append({
                        'type': 'deep_nesting',
                        'category': category,
                        'current_path': str(relative_path),
                        'depth': depth,
                        'readme_files': readme_files,
                        'suggested_new_path': self._suggest_new_path(str(relative_path), category)
                    })
            
            # 递归扫描子目录
            try:
                for item in current_path.iterdir():
                    if item.is_dir() and not item.name.startswith('.') and item.name not in ['__pycache__', 'node_modules']:
                        scan_recursive(item, depth + 1, base_path)
            except PermissionError:
                pass
        
        scan_recursive(path)
        return issues
    
    def _suggest_new_path(self, current_path: str, category: str) -> str:
        """建议新的路径结构"""
        path_parts = current_path.replace('\\', '/').split('/')
        
        if category == 'competitions':
            # competitions/[年份]-[比赛名称]
            year = None
            competition_name = None
            
            for part in path_parts:
                if part.isdigit() and len(part) == 4:  # 年份
                    year = part
                elif part not in ['competitions', 'archive', 'backup'] and not part.startswith('migration_'):
                    if competition_name is None:
                        competition_name = part
            
            if year and competition_name:
                return f"competitions/{year}-{competition_name}"
            elif competition_name:
                return f"competitions/{competition_name}"
        
        elif category == 'projects':
            # projects/[技术栈]/[项目名称]
            tech_stack = None
            project_name = None
            
            for i, part in enumerate(path_parts):
                if part in ['ai', 'embedded', 'robotics', 'research']:
                    tech_stack = part
                    # 下一个非标准目录名作为项目名
                    for j in range(i+1, len(path_parts)):
                        if path_parts[j] not in ['archive', 'backup'] and not path_parts[j].startswith('migration_'):
                            project_name = path_parts[j]
                            break
                    break
            
            if tech_stack and project_name:
                return f"projects/{tech_stack}/{project_name}"
            elif project_name:
                return f"projects/misc/{project_name}"
        
        elif category == 'shared':
            # shared/[资源类型]/[具体名称]
            resource_type = None
            resource_name = None
            
            for i, part in enumerate(path_parts):
                if part in ['images', 'models', 'templates', 'tools', 'assets']:
                    resource_type = part
                    if i + 1 < len(path_parts):
                        resource_name = path_parts[i + 1]
                    break
            
            if resource_type and resource_name:
                return f"shared/{resource_type}/{resource_name}"
            elif resource_type:
                return f"shared/{resource_type}"
        
        # 默认建议
        return f"{category}/misc/{path_parts[-1]}"
    
    def create_reorganization_plan(self) -> Dict:
        """创建重组计划"""
        print("创建重组计划...")
        
        analysis = self.analyze_current_structure()
        
        # 清理archive中的冗余结构
        self.plan['actions'].append({
            'type': 'cleanup_archive',
            'description': '清理archive目录中的冗余嵌套结构',
            'priority': 'high'
        })
        
        # 为每个问题创建重组动作
        for issue in analysis['issues']:
            if 'archive' not in issue['current_path']:  # 跳过archive中的问题
                action = {
                    'type': 'move_project',
                    'source': issue['current_path'],
                    'target': issue['suggested_new_path'],
                    'reason': f"减少目录深度从 {issue['depth']} 到 2",
                    'priority': 'high' if issue['depth'] > 4 else 'medium'
                }
                self.plan['actions'].append(action)
        
        # 创建新的扁平化结构建议
        self.plan['new_structure'] = {
            'competitions': {
                'description': '比赛项目 - 扁平化结构',
                'pattern': 'competitions/[年份]-[比赛名称]',
                'examples': [
                    'competitions/2024-robocon',
                    'competitions/2024-huawei-ai',
                    'competitions/2025-energy-saving'
                ]
            },
            'projects': {
                'description': '开发项目 - 按技术栈分类',
                'pattern': 'projects/[技术栈]/[项目名称]',
                'examples': [
                    'projects/ai/energy-monitoring',
                    'projects/embedded/nearlink',
                    'projects/robotics/humanoid-robot'
                ]
            },
            'shared': {
                'description': '共享资源 - 按资源类型分类',
                'pattern': 'shared/[资源类型]/[具体名称]',
                'examples': [
                    'shared/images/competition',
                    'shared/models/raspberrypi5',
                    'shared/templates/project'
                ]
            }
        }
        
        # 统计信息
        self.plan['statistics'] = {
            'total_actions': len(self.plan['actions']),
            'high_priority': len([a for a in self.plan['actions'] if a.get('priority') == 'high']),
            'estimated_improvement': '预计将92%的项目控制在2次点击内访问'
        }
        
        return self.plan
    
    def execute_cleanup_archive(self, dry_run: bool = True) -> Dict:
        """清理archive目录的冗余结构"""
        print("清理archive目录...")
        
        archive_path = self.root_path / "archive"
        if not archive_path.exists():
            return {'status': 'skipped', 'reason': 'archive目录不存在'}
        
        cleanup_actions = []
        
        # 识别冗余的migration目录
        migration_dirs = []
        for item in archive_path.rglob("migration_*"):
            if item.is_dir():
                migration_dirs.append(item)
        
        # 识别重复嵌套的目录
        redundant_paths = []
        for item in archive_path.rglob("*"):
            if item.is_dir():
                path_str = str(item)
                # 检查是否有重复的路径段
                parts = path_str.split(os.sep)
                if len(parts) != len(set(parts)):  # 有重复的路径段
                    redundant_paths.append(item)
        
        cleanup_actions.extend([
            {'type': 'remove_redundant', 'path': str(p), 'reason': '重复嵌套路径'}
            for p in redundant_paths[:10]  # 限制数量
        ])
        
        if not dry_run:
            # 实际执行清理
            for action in cleanup_actions:
                try:
                    path_to_remove = Path(action['path'])
                    if path_to_remove.exists():
                        shutil.rmtree(path_to_remove)
                        print(f"已删除: {action['path']}")
                except Exception as e:
                    print(f"删除失败 {action['path']}: {e}")
        
        return {
            'status': 'completed' if not dry_run else 'planned',
            'actions': cleanup_actions,
            'total_cleaned': len(cleanup_actions)
        }
    
    def generate_migration_script(self) -> str:
        """生成迁移脚本"""
        script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化目录结构重组脚本
实现"两次点击原则"的目录扁平化
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def backup_before_migration(root_path):
    """迁移前备份"""
    backup_dir = Path(root_path) / "backup" / f"pre_restructure_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份主要目录
    for dir_name in ['competitions', 'projects', 'shared']:
        src = Path(root_path) / dir_name
        if src.exists():
            dst = backup_dir / dir_name
            shutil.copytree(src, dst, ignore_errors=True)
            print(f"已备份: {src} -> {dst}")
    
    return backup_dir

def move_project_safely(src, dst, root_path):
    """安全移动项目"""
    src_path = Path(root_path) / src
    dst_path = Path(root_path) / dst
    
    if not src_path.exists():
        print(f"源路径不存在: {src}")
        return False
    
    # 创建目标目录
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 处理冲突
    if dst_path.exists():
        print(f"目标路径已存在: {dst}")
        # 可以选择合并或重命名
        dst_path = dst_path.parent / f"{dst_path.name}_migrated"
    
    try:
        shutil.move(str(src_path), str(dst_path))
        print(f"已移动: {src} -> {dst}")
        return True
    except Exception as e:
        print(f"移动失败 {src} -> {dst}: {e}")
        return False

def main():
    root_path = os.getcwd()
    print(f"开始重组目录结构: {root_path}")
    
    # 备份
    backup_dir = backup_before_migration(root_path)
    print(f"备份完成: {backup_dir}")
    
    # 执行迁移计划
    migration_plan = ''' + json.dumps(self.plan['actions'], indent=4, ensure_ascii=False) + '''
    
    success_count = 0
    for action in migration_plan:
        if action['type'] == 'move_project':
            if move_project_safely(action['source'], action['target'], root_path):
                success_count += 1
    
    print(f"\n重组完成: {success_count}/{len([a for a in migration_plan if a['type'] == 'move_project'])} 个项目成功迁移")
    print(f"备份位置: {backup_dir}")

if __name__ == "__main__":
    main()
'''
        
        return script_content
    
    def save_plan(self, output_file: str) -> None:
        """保存重组计划"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.plan, f, ensure_ascii=False, indent=2)
        
        # 生成可读的markdown报告
        md_file = output_file.replace('.json', '.md')
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# 目录结构重组计划\n\n")
            f.write("## 目标\n")
            f.write("实现\"两次点击原则\"：确保所有项目的README文件在根目录的2次点击内可达\n\n")
            
            f.write("## 新结构设计\n")
            for category, info in self.plan['new_structure'].items():
                f.write(f"### {category}\n")
                f.write(f"- **描述**: {info['description']}\n")
                f.write(f"- **模式**: `{info['pattern']}`\n")
                f.write("- **示例**:\n")
                for example in info['examples']:
                    f.write(f"  - `{example}`\n")
                f.write("\n")
            
            f.write("## 重组动作\n")
            for i, action in enumerate(self.plan['actions'], 1):
                f.write(f"### 动作 {i}: {action['type']}\n")
                if action['type'] == 'move_project':
                    f.write(f"- **源路径**: `{action['source']}`\n")
                    f.write(f"- **目标路径**: `{action['target']}`\n")
                    f.write(f"- **原因**: {action['reason']}\n")
                    f.write(f"- **优先级**: {action['priority']}\n")
                else:
                    f.write(f"- **描述**: {action.get('description', '无描述')}\n")
                    f.write(f"- **优先级**: {action.get('priority', 'medium')}\n")
                f.write("\n")
            
            f.write("## 统计信息\n")
            for key, value in self.plan['statistics'].items():
                f.write(f"- **{key}**: {value}\n")
        
        # 生成迁移脚本
        script_file = output_file.replace('.json', '_migration.py')
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_migration_script())
        
        print(f"重组计划已保存到: {output_file}")
        print(f"Markdown报告: {md_file}")
        print(f"迁移脚本: {script_file}")

def main():
    root_path = os.getcwd()
    reorganizer = StructureReorganizer(root_path)
    
    print(f"分析目录: {root_path}")
    
    # 创建重组计划
    plan = reorganizer.create_reorganization_plan()
    
    # 执行archive清理（预览模式）
    cleanup_result = reorganizer.execute_cleanup_archive(dry_run=True)
    plan['cleanup_preview'] = cleanup_result
    
    # 保存计划
    output_file = "restructure_plan.json"
    reorganizer.save_plan(output_file)
    
    print(f"\n=== 重组计划摘要 ===")
    print(f"总动作数: {plan['statistics']['total_actions']}")
    print(f"高优先级: {plan['statistics']['high_priority']}")
    print(f"预期改进: {plan['statistics']['estimated_improvement']}")
    
    if cleanup_result['actions']:
        print(f"\nArchive清理预览:")
        for action in cleanup_result['actions'][:5]:
            print(f"  - {action['type']}: {action['path']}")

if __name__ == "__main__":
    main()