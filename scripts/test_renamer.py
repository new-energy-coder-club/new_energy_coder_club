#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件重命名工具
"""

import sys
sys.path.append('.')

# from scripts.file_renamer import FileRenamer  # 文件不存在，已注释

def test_renamer():
    """测试文件重命名工具"""
    print("开始测试文件重命名工具...")
    
    try:
        renamer = FileRenamer('.')
        stats = renamer.run(dry_run=True)
        
        print(f"\n扫描结果:")
        print(f"- 总文件数: {stats['total_count']}")
        print(f"- 成功处理: {stats['success_count']}")
        print(f"- 跳过文件: {stats['skipped_count']}")
        print(f"- 冲突处理: {stats['conflict_count']}")
        print(f"- 失败文件: {stats['error_count']}")
        
        return stats
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    test_renamer()