#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本依赖关系检查工具
检查scripts文件夹中所有Python脚本的依赖关系和可执行性
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Set

def extract_imports(file_path: Path) -> Set[str]:
    """提取Python文件中的导入模块"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
    
    except Exception as e:
        print(f"解析文件 {file_path} 时出错: {e}")
    
    return imports

def check_module_availability(module_name: str) -> bool:
    """检查模块是否可用"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def get_builtin_modules() -> Set[str]:
    """获取Python内置模块列表"""
    return set(sys.builtin_module_names) | {
        'os', 'sys', 'json', 'pathlib', 'datetime', 'shutil', 're', 
        'urllib', 'typing', 'ast', 'importlib', 'traceback'
    }

def main():
    """主函数"""
    scripts_dir = Path(__file__).parent
    print(f"检查目录: {scripts_dir}")
    print("=" * 60)
    
    builtin_modules = get_builtin_modules()
    all_dependencies = set()
    script_dependencies = {}
    
    # 扫描所有Python脚本
    for script_file in scripts_dir.glob('*.py'):
        if script_file.name == 'check_dependencies.py':
            continue
            
        print(f"\n检查脚本: {script_file.name}")
        print("-" * 40)
        
        imports = extract_imports(script_file)
        script_dependencies[script_file.name] = imports
        
        missing_deps = []
        available_deps = []
        
        for module in imports:
            if module in builtin_modules:
                available_deps.append(f"{module} (内置)")
            elif check_module_availability(module):
                available_deps.append(f"{module} (已安装)")
            else:
                missing_deps.append(module)
                all_dependencies.add(module)
        
        if available_deps:
            print("✓ 可用依赖:")
            for dep in sorted(available_deps):
                print(f"  - {dep}")
        
        if missing_deps:
            print("✗ 缺失依赖:")
            for dep in sorted(missing_deps):
                print(f"  - {dep}")
        else:
            print("✓ 所有依赖都可用")
    
    # 生成总结报告
    print("\n" + "=" * 60)
    print("依赖关系总结")
    print("=" * 60)
    
    if all_dependencies:
        print("\n需要安装的依赖包:")
        for dep in sorted(all_dependencies):
            print(f"  - {dep}")
        
        print("\n安装命令:")
        print(f"pip install {' '.join(sorted(all_dependencies))}")
    else:
        print("\n✓ 所有脚本的依赖都已满足")
    
    # 检查脚本可执行性
    print("\n" + "=" * 60)
    print("脚本可执行性检查")
    print("=" * 60)
    
    for script_file in scripts_dir.glob('*.py'):
        if script_file.name == 'check_dependencies.py':
            continue
            
        try:
            # 尝试编译脚本
            with open(script_file, 'r', encoding='utf-8') as f:
                compile(f.read(), script_file, 'exec')
            print(f"✓ {script_file.name} - 语法正确")
        except SyntaxError as e:
            print(f"✗ {script_file.name} - 语法错误: {e}")
        except Exception as e:
            print(f"? {script_file.name} - 检查异常: {e}")
    
    print("\n检查完成!")

if __name__ == '__main__':
    main()