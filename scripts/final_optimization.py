#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终优化脚本 - 实现真正的两次点击可达性
针对仍然超过2次点击的项目进行深度扁平化
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def safe_copy_tree(src, dst):
    """安全复制目录树"""
    try:
        if os.path.exists(dst):
            print(f"目标已存在，跳过: {dst}")
            return False
        shutil.copytree(src, dst)
        return True
    except Exception as e:
        print(f"复制失败 {src} -> {dst}: {e}")
        return False

def safe_move(src, dst):
    """安全移动文件或目录"""
    try:
        if os.path.exists(dst):
            print(f"目标已存在，跳过: {dst}")
            return False
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        return True
    except Exception as e:
        print(f"移动失败 {src} -> {dst}: {e}")
        return False

def find_readme_files(directory):
    """查找README文件"""
    readme_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().startswith('readme'):
                readme_files.append(os.path.join(root, file))
    return readme_files

def calculate_click_depth(path, base_path):
    """计算从基础路径到目标路径的点击深度"""
    rel_path = os.path.relpath(path, base_path)
    if rel_path == '.':
        return 0
    return len(Path(rel_path).parts)

def analyze_deep_projects(base_dir):
    """分析仍然过深的项目"""
    deep_projects = []
    
    for main_dir in ['competitions', 'projects', 'shared']:
        main_path = os.path.join(base_dir, main_dir)
        if not os.path.exists(main_path):
            continue
            
        for root, dirs, files in os.walk(main_path):
            # 查找README文件
            readme_files = [f for f in files if f.lower().startswith('readme')]
            if readme_files:
                depth = calculate_click_depth(root, base_dir)
                if depth > 2:
                    deep_projects.append({
                        'path': root,
                        'relative_path': os.path.relpath(root, base_dir),
                        'depth': depth,
                        'category': main_dir,
                        'readme_files': readme_files
                    })
    
    return deep_projects

def create_optimization_plan(deep_projects):
    """创建最终优化计划"""
    plan = {
        'timestamp': datetime.now().isoformat(),
        'total_deep_projects': len(deep_projects),
        'actions': []
    }
    
    # 按类别分组
    by_category = {}
    for project in deep_projects:
        category = project['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(project)
    
    # 为每个类别创建优化动作
    for category, projects in by_category.items():
        print(f"\n处理 {category} 类别的 {len(projects)} 个深层项目...")
        
        # 按年份和类型进一步分组
        year_type_groups = {}
        for project in projects:
            parts = Path(project['relative_path']).parts
            
            # 提取年份和类型信息
            year = None
            project_type = None
            
            for part in parts:
                if part.isdigit() and len(part) == 4:  # 年份
                    year = part
                elif any(keyword in part.lower() for keyword in ['ai', 'energy', 'iot', 'robot', 'electronic']):
                    project_type = part
                    break
            
            if not year:
                year = '2024'  # 默认年份
            if not project_type:
                project_type = 'general'
            
            group_key = f"{year}_{project_type}"
            if group_key not in year_type_groups:
                year_type_groups[group_key] = []
            year_type_groups[group_key].append(project)
        
        # 为每个分组创建扁平化动作
        for group_key, group_projects in year_type_groups.items():
            year, project_type = group_key.split('_', 1)
            
            # 创建新的扁平化目标目录
            if category == 'competitions':
                if project_type == 'general':
                    target_base = f"{category}/{year}"
                else:
                    # 简化项目类型名称
                    simplified_type = simplify_project_type(project_type)
                    target_base = f"{category}/{year}-{simplified_type}"
            else:
                target_base = f"{category}/{project_type}"
            
            # 为每个项目创建移动动作
            for i, project in enumerate(group_projects):
                project_name = os.path.basename(project['path'])
                
                # 如果同一组有多个项目，添加序号
                if len(group_projects) > 1:
                    target_path = f"{target_base}/{project_name}-{i+1}"
                else:
                    target_path = f"{target_base}/{project_name}"
                
                plan['actions'].append({
                    'type': 'flatten_project',
                    'source': project['relative_path'],
                    'target': target_path,
                    'current_depth': project['depth'],
                    'target_depth': calculate_click_depth(target_path, ''),
                    'priority': 'high' if project['depth'] > 4 else 'medium',
                    'category': category,
                    'readme_files': project['readme_files']
                })
    
    return plan

def simplify_project_type(project_type):
    """简化项目类型名称"""
    simplifications = {
        'ai-huawei-cloud': 'ai-huawei',
        'energy-saving-competition': 'energy-saving',
        'electronics-competition': 'electronics',
        'iot-design-competition': 'iot-design',
        'robotics-robocon': 'robotics',
        'other-competitions': 'others'
    }
    
    for original, simplified in simplifications.items():
        if original in project_type.lower():
            return simplified
    
    return project_type[:15]  # 限制长度

def execute_optimization_plan(base_dir, plan):
    """执行优化计划"""
    print(f"\n开始执行最终优化计划...")
    print(f"总计 {len(plan['actions'])} 个优化动作")
    
    success_count = 0
    skip_count = 0
    
    # 创建备份
    backup_dir = os.path.join(base_dir, f"backup_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(backup_dir, exist_ok=True)
    
    for i, action in enumerate(plan['actions'], 1):
        print(f"\n[{i}/{len(plan['actions'])}] 处理: {action['source']}")
        
        source_path = os.path.join(base_dir, action['source'])
        target_path = os.path.join(base_dir, action['target'])
        
        if not os.path.exists(source_path):
            print(f"源路径不存在，跳过: {source_path}")
            skip_count += 1
            continue
        
        # 创建备份
        backup_path = os.path.join(backup_dir, action['source'])
        if safe_copy_tree(source_path, backup_path):
            print(f"已备份到: {backup_path}")
        
        # 执行移动
        if safe_move(source_path, target_path):
            print(f"成功移动: {action['source']} -> {action['target']}")
            print(f"深度优化: {action['current_depth']} -> {action['target_depth']}")
            success_count += 1
        else:
            skip_count += 1
    
    print(f"\n=== 最终优化完成 ===")
    print(f"成功处理: {success_count}")
    print(f"跳过项目: {skip_count}")
    print(f"备份位置: {backup_dir}")
    
    return success_count, skip_count

def generate_final_report(base_dir, plan, success_count, skip_count):
    """生成最终优化报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'optimization_plan': plan,
        'execution_results': {
            'total_actions': len(plan['actions']),
            'successful': success_count,
            'skipped': skip_count,
            'success_rate': f"{success_count/len(plan['actions'])*100:.1f}%" if plan['actions'] else "0%"
        }
    }
    
    # 保存JSON报告
    with open(os.path.join(base_dir, 'final_optimization_report.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown报告
    md_content = f"""# 最终优化报告

**优化时间**: {report['timestamp']}

## 执行结果

- **总动作数**: {report['execution_results']['total_actions']}
- **成功执行**: {report['execution_results']['successful']}
- **跳过项目**: {report['execution_results']['skipped']}
- **成功率**: {report['execution_results']['success_rate']}

## 优化动作详情

"""
    
    for action in plan['actions']:
        md_content += f"### {action['source']}\n"
        md_content += f"- **目标路径**: `{action['target']}`\n"
        md_content += f"- **深度优化**: {action['current_depth']} -> {action['target_depth']}\n"
        md_content += f"- **优先级**: {action['priority']}\n"
        md_content += f"- **类别**: {action['category']}\n\n"
    
    with open(os.path.join(base_dir, 'final_optimization_report.md'), 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n最终优化报告已保存:")
    print(f"- JSON: final_optimization_report.json")
    print(f"- Markdown: final_optimization_report.md")

def main():
    base_dir = os.getcwd()
    print(f"最终优化目录: {base_dir}")
    
    # 分析仍然过深的项目
    print("\n分析仍然过深的项目...")
    deep_projects = analyze_deep_projects(base_dir)
    print(f"发现 {len(deep_projects)} 个仍需优化的项目")
    
    if not deep_projects:
        print("所有项目已达到两次点击可达性要求！")
        return
    
    # 创建优化计划
    print("\n创建最终优化计划...")
    plan = create_optimization_plan(deep_projects)
    
    # 保存计划
    with open('final_optimization_plan.json', 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    print(f"优化计划已保存: final_optimization_plan.json")
    print(f"计划包含 {len(plan['actions'])} 个优化动作")
    
    # 执行优化计划
    success_count, skip_count = execute_optimization_plan(base_dir, plan)
    
    # 生成最终报告
    generate_final_report(base_dir, plan, success_count, skip_count)
    
    print(f"\n=== 最终优化摘要 ===")
    print(f"处理项目: {len(deep_projects)}")
    print(f"执行动作: {len(plan['actions'])}")
    print(f"成功优化: {success_count}")
    print(f"\n建议运行验证脚本检查最终效果")

if __name__ == '__main__':
    main()