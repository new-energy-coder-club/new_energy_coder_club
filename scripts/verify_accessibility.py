#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证两次点击可达性
检查重组后的目录结构是否满足"两次点击原则"
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class AccessibilityVerifier:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.results = {
            'verification_time': datetime.now().isoformat(),
            'total_projects': 0,
            'accessible_within_2_clicks': 0,
            'still_deep_nested': 0,
            'improvement_rate': 0,
            'categories': {},
            'detailed_results': []
        }
    
    def find_readme_files(self, directory: Path) -> List[Path]:
        """查找目录中的README文件"""
        readme_patterns = ['README.md', 'readme.md', 'Readme.md', 'README.txt', 'readme.txt']
        readme_files = []
        
        for pattern in readme_patterns:
            readme_path = directory / pattern
            if readme_path.exists():
                readme_files.append(readme_path)
        
        return readme_files
    
    def calculate_click_depth(self, file_path: Path) -> int:
        """计算从根目录到文件需要的点击次数"""
        relative_path = file_path.relative_to(self.root_path)
        # 点击次数 = 路径深度 - 1 (因为文件本身不算点击)
        return len(relative_path.parts) - 1
    
    def scan_directory_structure(self) -> Dict:
        """扫描目录结构，统计README文件的可达性"""
        print("扫描重组后的目录结构...")
        
        main_categories = ['competitions', 'projects', 'shared']
        
        for category in main_categories:
            category_path = self.root_path / category
            if not category_path.exists():
                continue
            
            category_results = {
                'total_projects': 0,
                'accessible_within_2_clicks': 0,
                'projects': []
            }
            
            # 递归扫描类别目录
            self._scan_category_recursive(category_path, category, category_results)
            
            self.results['categories'][category] = category_results
            self.results['total_projects'] += category_results['total_projects']
            self.results['accessible_within_2_clicks'] += category_results['accessible_within_2_clicks']
        
        # 计算改进率
        if self.results['total_projects'] > 0:
            self.results['improvement_rate'] = (
                self.results['accessible_within_2_clicks'] / self.results['total_projects'] * 100
            )
        
        self.results['still_deep_nested'] = (
            self.results['total_projects'] - self.results['accessible_within_2_clicks']
        )
        
        return self.results
    
    def _scan_category_recursive(self, path: Path, category: str, category_results: Dict, depth: int = 0):
        """递归扫描类别目录"""
        try:
            for item in path.iterdir():
                if item.is_dir() and not item.name.startswith('.') and item.name not in ['__pycache__', 'node_modules']:
                    # 检查当前目录是否有README文件
                    readme_files = self.find_readme_files(item)
                    
                    if readme_files:
                        # 这是一个项目目录
                        click_depth = self.calculate_click_depth(readme_files[0])
                        
                        project_info = {
                            'name': item.name,
                            'path': str(item.relative_to(self.root_path)),
                            'click_depth': click_depth,
                            'accessible_within_2_clicks': click_depth <= 2,
                            'readme_files': [f.name for f in readme_files]
                        }
                        
                        category_results['projects'].append(project_info)
                        category_results['total_projects'] += 1
                        
                        if click_depth <= 2:
                            category_results['accessible_within_2_clicks'] += 1
                        
                        self.results['detailed_results'].append({
                            'category': category,
                            **project_info
                        })
                    
                    # 继续递归扫描子目录
                    if depth < 5:  # 限制递归深度
                        self._scan_category_recursive(item, category, category_results, depth + 1)
        
        except PermissionError:
            pass
    
    def generate_comparison_report(self) -> Dict:
        """生成对比报告"""
        print("生成对比报告...")
        
        # 读取之前的分析结果
        old_analysis_file = self.root_path / "structure_analysis_report.md"
        old_stats = {'total_projects': 484, 'accessible_within_2_clicks': 40}  # 从之前的报告中获取
        
        comparison = {
            'before_optimization': {
                'total_projects': old_stats['total_projects'],
                'accessible_within_2_clicks': old_stats['accessible_within_2_clicks'],
                'accessibility_rate': old_stats['accessible_within_2_clicks'] / old_stats['total_projects'] * 100
            },
            'after_optimization': {
                'total_projects': self.results['total_projects'],
                'accessible_within_2_clicks': self.results['accessible_within_2_clicks'],
                'accessibility_rate': self.results['improvement_rate']
            },
            'improvement': {
                'projects_improved': self.results['accessible_within_2_clicks'] - old_stats['accessible_within_2_clicks'],
                'rate_improvement': self.results['improvement_rate'] - (old_stats['accessible_within_2_clicks'] / old_stats['total_projects'] * 100)
            }
        }
        
        return comparison
    
    def save_verification_report(self, output_file: str) -> None:
        """保存验证报告"""
        # 保存JSON格式
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 生成Markdown报告
        md_file = output_file.replace('.json', '.md')
        comparison = self.generate_comparison_report()
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# 两次点击可达性验证报告\n\n")
            f.write(f"**验证时间**: {self.results['verification_time']}\n\n")
            
            f.write("## 优化效果总览\n\n")
            f.write("### 优化前后对比\n")
            f.write("| 指标 | 优化前 | 优化后 | 改进 |\n")
            f.write("|------|--------|--------|------|\n")
            f.write(f"| 总项目数 | {comparison['before_optimization']['total_projects']} | {comparison['after_optimization']['total_projects']} | - |\n")
            f.write(f"| 2次点击内可达 | {comparison['before_optimization']['accessible_within_2_clicks']} | {comparison['after_optimization']['accessible_within_2_clicks']} | +{comparison['improvement']['projects_improved']} |\n")
            f.write(f"| 可达性比例 | {comparison['before_optimization']['accessibility_rate']:.1f}% | {comparison['after_optimization']['accessibility_rate']:.1f}% | +{comparison['improvement']['rate_improvement']:.1f}% |\n\n")
            
            f.write("## 分类统计\n\n")
            for category, stats in self.results['categories'].items():
                f.write(f"### {category}\n")
                f.write(f"- **总项目数**: {stats['total_projects']}\n")
                f.write(f"- **2次点击内可达**: {stats['accessible_within_2_clicks']}\n")
                if stats['total_projects'] > 0:
                    rate = stats['accessible_within_2_clicks'] / stats['total_projects'] * 100
                    f.write(f"- **可达性比例**: {rate:.1f}%\n")
                f.write("\n")
            
            f.write("## 仍需优化的项目\n\n")
            deep_projects = [p for p in self.results['detailed_results'] if not p['accessible_within_2_clicks']]
            
            if deep_projects:
                f.write("以下项目仍然超过2次点击深度：\n\n")
                for project in deep_projects[:20]:  # 只显示前20个
                    f.write(f"- **{project['name']}** (`{project['path']}`) - 深度: {project['click_depth']}\n")
                
                if len(deep_projects) > 20:
                    f.write(f"\n... 还有 {len(deep_projects) - 20} 个项目需要进一步优化\n")
            else:
                f.write("🎉 所有项目都已实现2次点击内可达！\n")
            
            f.write("\n## 优化建议\n\n")
            if self.results['improvement_rate'] < 90:
                f.write("### 进一步优化建议\n")
                f.write("1. 继续扁平化深层嵌套的项目目录\n")
                f.write("2. 合并功能相似的项目到同一目录\n")
                f.write("3. 重新审视项目分类逻辑\n")
                f.write("4. 考虑创建项目索引页面\n")
            else:
                f.write("### 维护建议\n")
                f.write("1. 定期检查新增项目的目录深度\n")
                f.write("2. 建立目录结构规范文档\n")
                f.write("3. 在项目创建时强制执行2次点击原则\n")
        
        print(f"验证报告已保存到: {output_file}")
        print(f"Markdown报告: {md_file}")
    
    def create_navigation_index(self) -> None:
        """创建导航索引"""
        print("创建导航索引...")
        
        index_content = "# 项目导航索引\n\n"
        index_content += "本索引帮助快速定位所有项目，实现2次点击内访问任何项目的README文件。\n\n"
        
        for category, stats in self.results['categories'].items():
            index_content += f"## {category.title()}\n\n"
            
            # 按项目名称排序
            projects = sorted(stats['projects'], key=lambda x: x['name'])
            
            for project in projects:
                status_icon = "✅" if project['accessible_within_2_clicks'] else "⚠️"
                index_content += f"- {status_icon} **[{project['name']}]({project['path']}/README.md)** (深度: {project['click_depth']})\n"
            
            index_content += "\n"
        
        # 保存导航索引
        index_file = self.root_path / "PROJECT_INDEX.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"导航索引已创建: {index_file}")

def main():
    root_path = os.getcwd()
    verifier = AccessibilityVerifier(root_path)
    
    print(f"验证目录: {root_path}")
    print("开始验证两次点击可达性...")
    
    # 扫描并验证
    results = verifier.scan_directory_structure()
    
    # 保存验证报告
    output_file = "accessibility_verification.json"
    verifier.save_verification_report(output_file)
    
    # 创建导航索引
    verifier.create_navigation_index()
    
    print(f"\n=== 验证结果摘要 ===")
    print(f"总项目数: {results['total_projects']}")
    print(f"2次点击内可达: {results['accessible_within_2_clicks']}")
    print(f"可达性比例: {results['improvement_rate']:.1f}%")
    print(f"仍需优化: {results['still_deep_nested']}")
    
    if results['improvement_rate'] >= 90:
        print("\n🎉 优化目标达成！超过90%的项目实现2次点击内访问")
    elif results['improvement_rate'] >= 80:
        print("\n✅ 优化效果良好，大部分项目实现2次点击内访问")
    else:
        print("\n⚠️ 仍需进一步优化以达到目标")

if __name__ == "__main__":
    main()