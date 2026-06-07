#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录结构分析工具
分析当前仓库结构，识别超过2层的项目路径和README文件位置
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple

class StructureAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.analysis_result = {
            'total_projects': 0,
            'projects_over_2_clicks': [],
            'projects_within_2_clicks': [],
            'readme_locations': [],
            'directory_depth_stats': {},
            'recommendations': []
        }
    
    def analyze_directory_depth(self, path: Path, current_depth: int = 0) -> Dict:
        """分析目录深度"""
        results = {
            'path': str(path.relative_to(self.root_path)),
            'depth': current_depth,
            'has_readme': False,
            'readme_files': [],
            'subdirectories': []
        }
        
        # 检查是否有README文件
        for readme_name in ['README.md', 'readme.md', 'Readme.md', 'README.txt']:
            readme_path = path / readme_name
            if readme_path.exists():
                results['has_readme'] = True
                results['readme_files'].append(readme_name)
                self.analysis_result['readme_locations'].append({
                    'path': str(readme_path.relative_to(self.root_path)),
                    'depth': current_depth,
                    'clicks_from_root': current_depth
                })
        
        # 递归分析子目录
        try:
            for item in path.iterdir():
                if item.is_dir() and not item.name.startswith('.') and item.name not in ['__pycache__', 'node_modules']:
                    subdir_result = self.analyze_directory_depth(item, current_depth + 1)
                    results['subdirectories'].append(subdir_result)
        except PermissionError:
            pass
        
        return results
    
    def identify_projects(self, analysis_data: Dict, path_prefix: str = "") -> None:
        """识别项目并分类"""
        current_path = path_prefix + "/" + analysis_data['path'] if path_prefix else analysis_data['path']
        
        # 如果有README文件，认为是一个项目
        if analysis_data['has_readme']:
            self.analysis_result['total_projects'] += 1
            project_info = {
                'path': current_path,
                'depth': analysis_data['depth'],
                'clicks_from_root': analysis_data['depth'],
                'readme_files': analysis_data['readme_files']
            }
            
            if analysis_data['depth'] <= 2:
                self.analysis_result['projects_within_2_clicks'].append(project_info)
            else:
                self.analysis_result['projects_over_2_clicks'].append(project_info)
        
        # 递归处理子目录
        for subdir in analysis_data['subdirectories']:
            self.identify_projects(subdir, current_path)
    
    def generate_recommendations(self) -> None:
        """生成优化建议"""
        recommendations = []
        
        # 统计深度分布
        depth_count = {}
        for project in self.analysis_result['projects_over_2_clicks'] + self.analysis_result['projects_within_2_clicks']:
            depth = project['depth']
            depth_count[depth] = depth_count.get(depth, 0) + 1
        
        self.analysis_result['directory_depth_stats'] = depth_count
        
        # 生成建议
        over_2_clicks = len(self.analysis_result['projects_over_2_clicks'])
        total_projects = self.analysis_result['total_projects']
        
        if over_2_clicks > 0:
            recommendations.append(f"发现 {over_2_clicks} 个项目需要超过2次点击才能访问到README文件")
            recommendations.append(f"建议将这些项目重新组织，减少目录层级")
        
        # 分析具体的问题路径
        problematic_paths = []
        for project in self.analysis_result['projects_over_2_clicks']:
            if project['depth'] > 3:
                problematic_paths.append(project['path'])
        
        if problematic_paths:
            recommendations.append(f"特别关注以下深层嵌套的项目路径：")
            for path in problematic_paths[:5]:  # 只显示前5个
                recommendations.append(f"  - {path}")
        
        # 提供具体的重组建议
        if 'competitions' in str(self.root_path):
            recommendations.append("建议competitions目录采用扁平化结构：competitions/[年份]-[比赛名称]")
        
        if 'projects' in str(self.root_path):
            recommendations.append("建议projects目录按技术栈分类：projects/[技术栈]/[项目名称]")
        
        self.analysis_result['recommendations'] = recommendations
    
    def run_analysis(self) -> Dict:
        """运行完整分析"""
        print("开始分析目录结构...")
        
        # 分析目录深度
        structure_data = self.analyze_directory_depth(self.root_path)
        
        # 识别项目
        self.identify_projects(structure_data)
        
        # 生成建议
        self.generate_recommendations()
        
        return self.analysis_result
    
    def save_report(self, output_file: str) -> None:
        """保存分析报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_result, f, ensure_ascii=False, indent=2)
        
        # 同时生成可读的markdown报告
        md_file = output_file.replace('.json', '.md')
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# 目录结构分析报告\n\n")
            f.write(f"## 总体统计\n")
            f.write(f"- 总项目数: {self.analysis_result['total_projects']}\n")
            f.write(f"- 2次点击内可达: {len(self.analysis_result['projects_within_2_clicks'])}\n")
            f.write(f"- 超过2次点击: {len(self.analysis_result['projects_over_2_clicks'])}\n\n")
            
            f.write("## 深度分布\n")
            for depth, count in sorted(self.analysis_result['directory_depth_stats'].items()):
                f.write(f"- 深度 {depth}: {count} 个项目\n")
            f.write("\n")
            
            if self.analysis_result['projects_over_2_clicks']:
                f.write("## 需要优化的项目路径\n")
                for project in self.analysis_result['projects_over_2_clicks']:
                    f.write(f"- `{project['path']}` (深度: {project['depth']})\n")
                f.write("\n")
            
            f.write("## 优化建议\n")
            for rec in self.analysis_result['recommendations']:
                f.write(f"- {rec}\n")

def main():
    root_path = os.getcwd()
    analyzer = StructureAnalyzer(root_path)
    
    print(f"分析根目录: {root_path}")
    result = analyzer.run_analysis()
    
    # 保存报告
    output_file = "structure_analysis_report.json"
    analyzer.save_report(output_file)
    
    print(f"\n=== 分析结果 ===")
    print(f"总项目数: {result['total_projects']}")
    print(f"2次点击内可达: {len(result['projects_within_2_clicks'])}")
    print(f"超过2次点击: {len(result['projects_over_2_clicks'])}")
    
    if result['projects_over_2_clicks']:
        print("\n需要优化的项目:")
        for project in result['projects_over_2_clicks'][:10]:  # 显示前10个
            print(f"  - {project['path']} (深度: {project['depth']})")
    
    print(f"\n详细报告已保存到: {output_file}")
    print(f"Markdown报告: {output_file.replace('.json', '.md')}")

if __name__ == "__main__":
    main()