#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找项目中未被README文件引用的图片文件
"""

import os
import re
from pathlib import Path
from urllib.parse import unquote

def read_file_list(filename):
    """读取文件列表"""
    files = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    # 转换为相对路径格式
                    file_path = line.replace('\\', '/')
                    files.append(file_path)
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
    return files

def read_image_references(filename):
    """读取README文件中的图片引用"""
    references = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ' : ' in line:
                    # 提取图片路径
                    content = line.split(' : ', 1)[1]
                    # 使用正则表达式提取图片路径
                    matches = re.findall(r'!\[.*?\]\(([^)]*\.(png|jpg|jpeg|gif|svg|bmp|webp)[^)]*)\)', content)
                    for match in matches:
                        img_path = match[0]
                        # 跳过网络链接
                        if img_path.startswith(('http://', 'https://')):
                            continue
                        # 跳过绝对路径（如C:\Users\...）
                        if ':' in img_path and not img_path.startswith('./'):
                            continue
                        # URL解码
                        img_path = unquote(img_path)
                        # 标准化路径
                        img_path = img_path.replace('\\', '/')
                        references.add(img_path)
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
    return references

def normalize_path(path):
    """标准化路径格式"""
    return path.replace('\\', '/').replace('//', '/')

def resolve_relative_path(base_dir, relative_path):
    """解析相对路径为绝对路径"""
    if relative_path.startswith('./'):
        relative_path = relative_path[2:]
    elif relative_path.startswith('../'):
        # 处理 ../ 路径
        parts = base_dir.split('/')
        rel_parts = relative_path.split('/')
        
        for part in rel_parts:
            if part == '..':
                if parts:
                    parts.pop()
            elif part and part != '.':
                parts.append(part)
        
        return '/'.join(parts)
    
    # 直接拼接
    if base_dir:
        return f"{base_dir}/{relative_path}"
    else:
        return relative_path

def find_unused_images():
    """查找未使用的图片文件"""
    print("正在分析图片文件和引用...")
    
    # 读取所有图片文件
    image_files = read_file_list('image_files_list.txt')
    print(f"找到 {len(image_files)} 个图片文件")
    
    # 读取所有README引用
    references = read_image_references('readme_image_references.txt')
    print(f"找到 {len(references)} 个图片引用")
    
    # 创建引用路径的集合（包含各种可能的路径形式）
    referenced_paths = set()
    
    # 处理每个引用，生成可能的完整路径
    for ref in references:
        referenced_paths.add(normalize_path(ref))
        
        # 如果是相对路径，尝试从不同的基础目录解析
        if ref.startswith(('./', '../')) or not ref.startswith('/'):
            # 从项目根目录解析
            if ref.startswith('./'):
                full_path = ref[2:]
            else:
                full_path = ref
            referenced_paths.add(normalize_path(full_path))
    
    # 查找未引用的图片
    unused_images = []
    
    for img_file in image_files:
        img_path = normalize_path(img_file)
        is_referenced = False
        
        # 检查是否被引用
        for ref_path in referenced_paths:
            if img_path.endswith(ref_path) or ref_path.endswith(img_path.split('/')[-1]):
                is_referenced = True
                break
            
            # 检查文件名匹配
            img_filename = img_path.split('/')[-1]
            ref_filename = ref_path.split('/')[-1]
            if img_filename == ref_filename:
                is_referenced = True
                break
        
        if not is_referenced:
            unused_images.append(img_file)
    
    return unused_images, len(image_files), len(references)

def calculate_file_sizes(file_list):
    """计算文件大小"""
    total_size = 0
    valid_files = []
    
    for file_path in file_list:
        # 转换为Windows路径格式
        windows_path = file_path.replace('/', '\\')
        if os.path.exists(windows_path):
            size = os.path.getsize(windows_path)
            total_size += size
            valid_files.append((file_path, size))
        else:
            print(f"警告: 文件不存在 {windows_path}")
    
    return valid_files, total_size

def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

if __name__ == "__main__":
    unused_images, total_images, total_references = find_unused_images()
    
    print(f"\n=== 分析结果 ===")
    print(f"总图片文件数: {total_images}")
    print(f"总引用数: {total_references}")
    print(f"未引用图片数: {len(unused_images)}")
    
    if unused_images:
        print(f"\n=== 未引用的图片文件 ===")
        valid_files, total_size = calculate_file_sizes(unused_images)
        
        for file_path, size in valid_files:
            print(f"{file_path} ({format_size(size)})")
        
        print(f"\n总计可释放空间: {format_size(total_size)}")
        
        # 保存结果到文件
        with open('unused_images_report.txt', 'w', encoding='utf-8') as f:
            f.write("未引用图片删除报告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"分析时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总图片文件数: {total_images}\n")
            f.write(f"总引用数: {total_references}\n")
            f.write(f"未引用图片数: {len(unused_images)}\n")
            f.write(f"可释放空间: {format_size(total_size)}\n\n")
            
            f.write("未引用的图片文件列表:\n")
            f.write("-" * 30 + "\n")
            for file_path, size in valid_files:
                f.write(f"{file_path} ({format_size(size)})\n")
        
        print(f"\n详细报告已保存到: unused_images_report.txt")
    else:
        print("\n所有图片文件都被引用，没有需要删除的文件。")