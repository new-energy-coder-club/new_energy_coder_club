#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目结构验证脚本
用于验证仓库目录结构是否符合标准化规范
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class StructureValidator:
    """项目结构验证器"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.errors = []
        self.warnings = []
        self.info = []
        
        # 标准目录结构定义
        self.required_dirs = {
            "competitions_new": "竞赛项目目录",
            "projects_new": "技术项目目录", 
            "shared_new": "共享资源目录",
            "docs_new": "文档库目录",
            "scripts": "脚本工具目录",
            "config": "配置文件目录",
            "templates": "项目模板目录"
        }
        
        self.required_files = {
            "README.md": "项目主说明文档",
            "LICENSE": "开源协议文件",
            ".gitignore": "Git忽略文件"
        }
        
        # 子目录结构规范
        self.subdir_structure = {
            "competitions_new": ["2024", "2025"],
            "projects_new": ["ai", "robotics", "embedded", "web", "mobile", "desktop", "research"],
            "shared_new": ["media", "models", "code", "tools"],
            "docs_new": ["technical", "tutorials", "guides", "standards", "best_practices"],
            "scripts": ["build", "deploy", "test", "maintenance", "migration", "automation", "tools"],
            "config": ["environments", "applications", "infrastructure", "ci_cd", "security"],
            "templates": ["project", "competition", "research", "documentation"]
        }
        
        # 文件命名规范
        self.naming_patterns = {
            "directories": r"^[a-z0-9_]+$",  # 目录名：小写字母、数字、下划线
            "files": r"^[a-zA-Z0-9_.-]+$",     # 文件名：字母、数字、下划线、点、连字符
            "readme": r"^README\.md$",        # README文件
            "config": r"^[a-z0-9_.-]+\.(json|yaml|yml|toml|ini|conf)$"  # 配置文件
        }
    
    def validate_directory_structure(self) -> bool:
        """验证目录结构"""
        print(f"🔍 验证目录结构: {self.root_path}")
        
        # 检查必需目录
        for dir_name, description in self.required_dirs.items():
            dir_path = self.root_path / dir_name
            if not dir_path.exists():
                self.errors.append(f"缺少必需目录: {dir_name} ({description})")
            elif not dir_path.is_dir():
                self.errors.append(f"{dir_name} 应该是目录，但发现是文件")
            else:
                self.info.append(f"✅ 找到目录: {dir_name}")
        
        # 检查必需文件
        for file_name, description in self.required_files.items():
            file_path = self.root_path / file_name
            if not file_path.exists():
                self.errors.append(f"缺少必需文件: {file_name} ({description})")
            elif not file_path.is_file():
                self.errors.append(f"{file_name} 应该是文件，但发现是目录")
            else:
                self.info.append(f"✅ 找到文件: {file_name}")
        
        return len(self.errors) == 0
    
    def validate_subdirectory_structure(self) -> bool:
        """验证子目录结构"""
        print("🔍 验证子目录结构")
        
        for parent_dir, expected_subdirs in self.subdir_structure.items():
            parent_path = self.root_path / parent_dir
            if not parent_path.exists():
                continue  # 父目录不存在，已在上一步检查中报告
            
            for subdir in expected_subdirs:
                subdir_path = parent_path / subdir
                if not subdir_path.exists():
                    self.warnings.append(f"建议创建子目录: {parent_dir}/{subdir}")
                else:
                    self.info.append(f"✅ 找到子目录: {parent_dir}/{subdir}")
        
        return True
    
    def validate_readme_files(self) -> bool:
        """验证README文件"""
        print("🔍 验证README文件")
        
        readme_files = list(self.root_path.rglob("README.md"))
        
        if not readme_files:
            self.errors.append("未找到任何README.md文件")
            return False
        
        for readme_file in readme_files:
            # 检查文件是否为空
            if readme_file.stat().st_size == 0:
                self.errors.append(f"README文件为空: {readme_file.relative_to(self.root_path)}")
                continue
            
            # 检查基本内容
            try:
                content = readme_file.read_text(encoding='utf-8')
                if len(content.strip()) < 50:
                    self.warnings.append(f"README文件内容过短: {readme_file.relative_to(self.root_path)}")
                
                # 检查是否包含标题
                if not content.startswith('#'):
                    self.warnings.append(f"README文件缺少标题: {readme_file.relative_to(self.root_path)}")
                
                self.info.append(f"✅ README文件有效: {readme_file.relative_to(self.root_path)}")
                
            except UnicodeDecodeError:
                self.errors.append(f"README文件编码错误: {readme_file.relative_to(self.root_path)}")
        
        return len([e for e in self.errors if "README" in e]) == 0
    
    def validate_naming_conventions(self) -> bool:
        """验证命名规范"""
        print("🔍 验证命名规范")
        
        import re
        
        # 检查目录命名
        for dir_path in self.root_path.rglob("*"):
            if dir_path.is_dir() and dir_path != self.root_path:
                dir_name = dir_path.name
                if not re.match(self.naming_patterns["directories"], dir_name):
                    # 排除一些特殊目录
                    if dir_name not in [".git", ".github", ".vscode", ".idea", "node_modules", "__pycache__"]:
                        self.warnings.append(f"目录命名不规范: {dir_path.relative_to(self.root_path)} (建议使用小写字母、数字、下划线)")
        
        # 检查文件命名
        for file_path in self.root_path.rglob("*"):
            if file_path.is_file():
                file_name = file_path.name
                if not re.match(self.naming_patterns["files"], file_name):
                    # 排除一些特殊文件
                    if not file_name.startswith('.') and file_name not in ["LICENSE"]:
                        self.warnings.append(f"文件命名不规范: {file_path.relative_to(self.root_path)}")
        
        return True
    
    def validate_project_metadata(self) -> bool:
        """验证项目元数据"""
        print("🔍 验证项目元数据")
        
        # 检查项目配置文件
        config_files = [
            "package.json",
            "pyproject.toml", 
            "setup.py",
            "Cargo.toml",
            "pom.xml",
            "build.gradle"
        ]
        
        found_configs = []
        for config_file in config_files:
            config_path = self.root_path / config_file
            if config_path.exists():
                found_configs.append(config_file)
                self.info.append(f"✅ 找到配置文件: {config_file}")
        
        if not found_configs:
            self.warnings.append("未找到项目配置文件 (package.json, pyproject.toml 等)")
        
        # 检查CI/CD配置
        ci_configs = [
            ".github/workflows",
            ".gitlab-ci.yml",
            "Jenkinsfile",
            ".travis.yml"
        ]
        
        found_ci = False
        for ci_config in ci_configs:
            ci_path = self.root_path / ci_config
            if ci_path.exists():
                found_ci = True
                self.info.append(f"✅ 找到CI/CD配置: {ci_config}")
                break
        
        if not found_ci:
            self.warnings.append("未找到CI/CD配置文件")
        
        return True
    
    def check_migration_completeness(self) -> bool:
        """检查迁移完整性"""
        print("🔍 检查迁移完整性")
        
        # 检查是否存在旧目录结构
        old_dirs = ["competitions", "projects", "shared", "docs"]
        old_dirs_found = []
        
        for old_dir in old_dirs:
            old_path = self.root_path / old_dir
            if old_path.exists():
                old_dirs_found.append(old_dir)
        
        if old_dirs_found:
            self.warnings.append(f"发现旧目录结构，建议清理: {', '.join(old_dirs_found)}")
        
        # 检查迁移日志
        migration_logs = list(self.root_path.glob("migration_logs/migration_report_*.json"))
        if migration_logs:
            latest_log = max(migration_logs, key=lambda x: x.stat().st_mtime)
            self.info.append(f"✅ 找到迁移日志: {latest_log.name}")
            
            # 分析迁移日志
            try:
                with open(latest_log, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                
                if log_data.get('summary', {}).get('failed_count', 0) > 0:
                    self.warnings.append(f"迁移日志显示有 {log_data['summary']['failed_count']} 个项目迁移失败")
                else:
                    self.info.append("✅ 迁移日志显示所有项目迁移成功")
                    
            except (json.JSONDecodeError, FileNotFoundError) as e:
                self.warnings.append(f"无法读取迁移日志: {e}")
        else:
            self.warnings.append("未找到迁移日志文件")
        
        return True
    
    def generate_report(self) -> Dict:
        """生成验证报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "validation_results": {
                "errors": self.errors,
                "warnings": self.warnings,
                "info": self.info
            },
            "summary": {
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "total_info": len(self.info),
                "validation_passed": len(self.errors) == 0
            }
        }
        
        return report
    
    def run_validation(self) -> bool:
        """运行完整验证"""
        print(f"🚀 开始验证项目结构: {self.root_path}")
        print("=" * 60)
        
        # 执行各项验证
        validations = [
            self.validate_directory_structure,
            self.validate_subdirectory_structure,
            self.validate_readme_files,
            self.validate_naming_conventions,
            self.validate_project_metadata,
            self.check_migration_completeness
        ]
        
        for validation in validations:
            try:
                validation()
            except Exception as e:
                self.errors.append(f"验证过程中发生错误: {e}")
        
        # 生成报告
        report = self.generate_report()
        
        # 输出结果
        print("\n" + "=" * 60)
        print("📊 验证结果汇总")
        print("=" * 60)
        
        if self.errors:
            print(f"❌ 错误 ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.info:
            print(f"\n✅ 信息 ({len(self.info)}):")
            for info in self.info[:10]:  # 只显示前10条信息
                print(f"   • {info}")
            if len(self.info) > 10:
                print(f"   ... 还有 {len(self.info) - 10} 条信息")
        
        print("\n" + "=" * 60)
        if report["summary"]["validation_passed"]:
            print("🎉 验证通过！项目结构符合标准化规范。")
        else:
            print("❌ 验证失败！请修复上述错误后重新验证。")
        
        print(f"📈 统计: {len(self.errors)} 错误, {len(self.warnings)} 警告, {len(self.info)} 信息")
        
        return report["summary"]["validation_passed"]

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="项目结构验证工具")
    parser.add_argument(
        "--path", 
        default=".", 
        help="要验证的项目路径 (默认: 当前目录)"
    )
    parser.add_argument(
        "--output", 
        help="输出验证报告到文件"
    )
    parser.add_argument(
        "--format", 
        choices=["json", "text"], 
        default="text",
        help="报告格式 (默认: text)"
    )
    parser.add_argument(
        "--strict", 
        action="store_true",
        help="严格模式：将警告视为错误"
    )
    
    args = parser.parse_args()
    
    # 创建验证器并运行验证
    validator = StructureValidator(args.path)
    success = validator.run_validation()
    
    # 严格模式下，有警告也视为失败
    if args.strict and validator.warnings:
        success = False
        print("\n⚠️  严格模式：由于存在警告，验证失败。")
    
    # 输出报告到文件
    if args.output:
        report = validator.generate_report()
        
        if args.format == "json":
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(f"项目结构验证报告\n")
                f.write(f"生成时间: {report['timestamp']}\n")
                f.write(f"项目路径: {report['root_path']}\n\n")
                
                if report['validation_results']['errors']:
                    f.write("错误:\n")
                    for error in report['validation_results']['errors']:
                        f.write(f"  - {error}\n")
                    f.write("\n")
                
                if report['validation_results']['warnings']:
                    f.write("警告:\n")
                    for warning in report['validation_results']['warnings']:
                        f.write(f"  - {warning}\n")
                    f.write("\n")
                
                f.write(f"验证结果: {'通过' if report['summary']['validation_passed'] else '失败'}\n")
        
        print(f"\n📄 验证报告已保存到: {args.output}")
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()