#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激进扁平化脚本 - 实现真正的两次点击可达性
将所有项目直接移动到主目录根级别
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def safe_move(src, dst):
    """安全移动文件或目录"""
    try:
        if os.path.exists(dst):
            # 如果目标存在，添加后缀
            counter = 1
            base_dst = dst
            while os.path.exists(dst):
                dst = f"{base_dst}_v{counter}"
                counter += 1
        
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        return True, dst
    except Exception as e:
        print(f"移动失败 {src} -> {dst}: {e}")
        return False, dst

def find_all_projects(base_dir):
    """查找所有包含README的项目目录"""
    projects = []
    
    for main_dir in ['competitions', 'projects', 'shared']:
        main_path = os.path.join(base_dir, main_dir)
        if not os.path.exists(main_path):
            continue
            
        for root, dirs, files in os.walk(main_path):
            # 查找README文件
            readme_files = [f for f in files if f.lower().startswith('readme')]
            if readme_files:
                rel_path = os.path.relpath(root, base_dir)
                depth = len(Path(rel_path).parts)
                
                if depth > 2:  # 超过2次点击
                    projects.append({
                        'path': root,
                        'relative_path': rel_path,
                        'depth': depth,
                        'category': main_dir,
                        'project_name': os.path.basename(root),
                        'readme_files': readme_files
                    })
    
    return projects

def create_unique_name(category, project_name, existing_names):
    """创建唯一的项目名称"""
    # 清理项目名称
    clean_name = project_name.replace('_migrated', '').replace('-migrated', '')
    clean_name = clean_name.replace('project-', '').replace('chinese-', '')
    
    # 提取有意义的关键词
    keywords = []
    for word in clean_name.split('-'):
        if word and len(word) > 2 and word not in ['the', 'and', 'for', 'with']:
            keywords.append(word)
    
    if not keywords:
        keywords = [clean_name[:10] if clean_name else 'project']
    
    # 构建基础名称
    if category == 'competitions':
        # 从路径中提取年份和类型信息
        base_name = '-'.join(keywords[:2])  # 最多取前两个关键词
    else:
        base_name = '-'.join(keywords[:3])  # 最多取前三个关键词
    
    # 确保名称唯一
    final_name = base_name
    counter = 1
    while final_name in existing_names:
        final_name = f"{base_name}-{counter}"
        counter += 1
    
    existing_names.add(final_name)
    return final_name

def aggressive_flatten(base_dir):
    """执行激进扁平化"""
    print(f"开始激进扁平化: {base_dir}")
    
    # 查找所有需要扁平化的项目
    projects = find_all_projects(base_dir)
    print(f"发现 {len(projects)} 个需要扁平化的项目")
    
    if not projects:
        print("没有需要扁平化的项目！")
        return
    
    # 创建备份
    backup_dir = os.path.join(base_dir, f"backup_aggressive_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(backup_dir, exist_ok=True)
    print(f"备份目录: {backup_dir}")
    
    # 按类别分组
    by_category = {}
    for project in projects:
        category = project['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(project)
    
    results = {
        'total_projects': len(projects),
        'successful': 0,
        'failed': 0,
        'actions': []
    }
    
    # 为每个类别执行扁平化
    for category, category_projects in by_category.items():
        print(f"\n处理 {category} 类别的 {len(category_projects)} 个项目...")
        
        existing_names = set()
        # 先检查已存在的项目名称
        category_root = os.path.join(base_dir, category)
        if os.path.exists(category_root):
            for item in os.listdir(category_root):
                if os.path.isdir(os.path.join(category_root, item)):
                    existing_names.add(item)
        
        for i, project in enumerate(category_projects, 1):
            print(f"\n[{i}/{len(category_projects)}] 处理: {project['relative_path']}")
            
            # 创建备份
            backup_path = os.path.join(backup_dir, project['relative_path'])
            try:
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.copytree(project['path'], backup_path)
                print(f"已备份: {backup_path}")
            except Exception as e:
                print(f"备份失败: {e}")
            
            # 创建唯一的目标名称
            unique_name = create_unique_name(category, project['project_name'], existing_names)
            target_path = os.path.join(base_dir, category, unique_name)
            
            # 执行移动
            success, final_target = safe_move(project['path'], target_path)
            
            action = {
                'source': project['relative_path'],
                'target': os.path.relpath(final_target, base_dir),
                'original_depth': project['depth'],
                'new_depth': 2,  # 直接在主目录下
                'success': success,
                'unique_name': unique_name
            }
            
            results['actions'].append(action)
            
            if success:
                print(f"✅ 成功: {project['relative_path']} -> {action['target']}")
                print(f"   深度: {project['depth']} -> 2")
                results['successful'] += 1
            else:
                print(f"❌ 失败: {project['relative_path']}")
                results['failed'] += 1
    
    # 保存结果报告
    report_path = os.path.join(base_dir, 'aggressive_flatten_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown报告
    md_content = f"""# 激进扁平化报告

**执行时间**: {datetime.now().isoformat()}

## 执行结果

- **总项目数**: {results['total_projects']}
- **成功扁平化**: {results['successful']}
- **失败项目**: {results['failed']}
- **成功率**: {results['successful']/results['total_projects']*100:.1f}%

## 扁平化详情

"""
    
    for action in results['actions']:
        status = "✅" if action['success'] else "❌"
        md_content += f"### {status} {action['source']}\n"
        md_content += f"- **目标**: `{action['target']}`\n"
        md_content += f"- **深度优化**: {action['original_depth']} -> {action['new_depth']}\n"
        md_content += f"- **唯一名称**: {action['unique_name']}\n\n"
    
    md_report_path = os.path.join(base_dir, 'aggressive_flatten_report.md')
    with open(md_report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n=== 激进扁平化完成 ===")
    print(f"总项目: {results['total_projects']}")
    print(f"成功: {results['successful']}")
    print(f"失败: {results['failed']}")
    print(f"成功率: {results['successful']/results['total_projects']*100:.1f}%")
    print(f"\n报告已保存:")
    print(f"- JSON: {report_path}")
    print(f"- Markdown: {md_report_path}")
    print(f"- 备份: {backup_dir}")
    
    return results

def clean_empty_directories(base_dir):
    """清理空目录"""
    print("\n清理空目录...")
    
    removed_count = 0
    for main_dir in ['competitions', 'projects', 'shared']:
        main_path = os.path.join(base_dir, main_dir)
        if not os.path.exists(main_path):
            continue
        
        # 从最深层开始清理
        for root, dirs, files in os.walk(main_path, topdown=False):
            if root == main_path:  # 不删除主目录
                continue
            
            try:
                if not dirs and not files:  # 空目录
                    os.rmdir(root)
                    print(f"删除空目录: {os.path.relpath(root, base_dir)}")
                    removed_count += 1
            except Exception as e:
                print(f"删除目录失败 {root}: {e}")
    
    print(f"清理了 {removed_count} 个空目录")

def main():
    base_dir = os.getcwd()
    print(f"激进扁平化目录: {base_dir}")
    
    # 执行激进扁平化
    results = aggressive_flatten(base_dir)
    
    # 清理空目录
    clean_empty_directories(base_dir)
    
    print(f"\n🎯 激进扁平化完成！")
    print(f"现在所有项目都应该在2次点击内可达")
    print(f"建议运行验证脚本确认效果")

if __name__ == '__main__':
    main()