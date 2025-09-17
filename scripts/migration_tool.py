#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目迁移工具
用于将现有项目从旧目录结构迁移到新的标准化目录结构
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import subprocess
import re

class ProjectMigrator:
    """项目迁移器"""
    
    def __init__(self, root_path: str = ".", dry_run: bool = False):
        self.root_path = Path(root_path).resolve()
        self.dry_run = dry_run
        self.migration_log = []
        self.errors = []
        self.warnings = []
        
        # 迁移映射规则
        self.migration_mapping = {
            "competitions": "competitions_new",
            "projects": "projects_new",
            "shared": "shared_new",
            "docs": "docs_new"
        }
        
        # 项目分类规则
        self.project_categories = {
            "ai": ["machine_learning", "deep_learning", "neural_network", "tensorflow", "pytorch", "ai", "ml", "nlp"],
            "robotics": ["robot", "arduino", "raspberry", "sensor", "motor", "control", "automation"],
            "embedded": ["embedded", "microcontroller", "stm32", "esp32", "firmware", "hardware"],
            "web": ["web", "html", "css", "javascript", "react", "vue", "angular", "node", "express", "django", "flask"],
            "mobile": ["android", "ios", "flutter", "react_native", "mobile", "app"],
            "desktop": ["desktop", "gui", "qt", "tkinter", "electron", "wpf", "winforms"],
            "research": ["research", "paper", "thesis", "experiment", "analysis", "study"]
        }
        
        # 竞赛项目年份识别
        self.competition_years = ["2024", "2025", "2026"]
        
        # 备份目录
        self.backup_dir = self.root_path / "migration_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 日志目录
        self.log_dir = self.root_path / "migration_logs"
    
    def log_action(self, action: str, source: str = "", target: str = "", status: str = "success", message: str = ""):
        """记录迁移操作"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "source": source,
            "target": target,
            "status": status,
            "message": message
        }
        self.migration_log.append(log_entry)
        
        # 实时输出
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        print(f"{status_icon} {action}: {source} -> {target} ({message})")
    
    def create_backup(self) -> bool:
        """创建备份"""
        print(f"📦 创建备份到: {self.backup_dir}")
        
        if self.dry_run:
            self.log_action("backup", str(self.root_path), str(self.backup_dir), "skipped", "dry-run模式")
            return True
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 备份旧目录结构
            for old_dir in self.migration_mapping.keys():
                old_path = self.root_path / old_dir
                if old_path.exists():
                    backup_path = self.backup_dir / old_dir
                    shutil.copytree(old_path, backup_path)
                    self.log_action("backup", str(old_path), str(backup_path), "success", "目录备份完成")
            
            # 备份重要文件
            important_files = ["README.md", "LICENSE", ".gitignore", "package.json", "requirements.txt"]
            for file_name in important_files:
                file_path = self.root_path / file_name
                if file_path.exists():
                    backup_file = self.backup_dir / file_name
                    shutil.copy2(file_path, backup_file)
                    self.log_action("backup", str(file_path), str(backup_file), "success", "文件备份完成")
            
            return True
            
        except Exception as e:
            self.log_action("backup", str(self.root_path), str(self.backup_dir), "error", str(e))
            self.errors.append(f"备份失败: {e}")
            return False
    
    def analyze_project_structure(self) -> Dict:
        """分析现有项目结构"""
        print("🔍 分析现有项目结构")
        
        analysis = {
            "directories": {},
            "files": {},
            "projects": [],
            "competitions": [],
            "statistics": {}
        }
        
        # 扫描所有目录和文件
        for item in self.root_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                analysis["directories"][item.name] = self._analyze_directory(item)
            elif item.is_file():
                analysis["files"][item.name] = {
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                }
        
        # 识别项目和竞赛
        for dir_name, dir_info in analysis["directories"].items():
            if self._is_competition_project(dir_name, dir_info):
                analysis["competitions"].append({
                    "name": dir_name,
                    "year": self._extract_year(dir_name),
                    "path": dir_name,
                    "info": dir_info
                })
            elif self._is_regular_project(dir_name, dir_info):
                analysis["projects"].append({
                    "name": dir_name,
                    "category": self._categorize_project(dir_name, dir_info),
                    "path": dir_name,
                    "info": dir_info
                })
        
        # 统计信息
        analysis["statistics"] = {
            "total_directories": len(analysis["directories"]),
            "total_files": len(analysis["files"]),
            "total_projects": len(analysis["projects"]),
            "total_competitions": len(analysis["competitions"]),
            "categories": {}
        }
        
        # 统计项目分类
        for project in analysis["projects"]:
            category = project["category"]
            if category not in analysis["statistics"]["categories"]:
                analysis["statistics"]["categories"][category] = 0
            analysis["statistics"]["categories"][category] += 1
        
        self.log_action("analyze", str(self.root_path), "", "success", 
                       f"发现 {len(analysis['projects'])} 个项目, {len(analysis['competitions'])} 个竞赛")
        
        return analysis
    
    def _analyze_directory(self, dir_path: Path) -> Dict:
        """分析单个目录"""
        info = {
            "files": [],
            "subdirs": [],
            "size": 0,
            "file_count": 0,
            "has_readme": False,
            "has_config": False,
            "languages": set(),
            "frameworks": set()
        }
        
        try:
            for item in dir_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(dir_path)
                    info["files"].append(str(relative_path))
                    info["size"] += item.stat().st_size
                    info["file_count"] += 1
                    
                    # 检查特殊文件
                    if item.name.lower() == "readme.md":
                        info["has_readme"] = True
                    
                    if item.suffix in [".json", ".yaml", ".yml", ".toml", ".ini"]:
                        info["has_config"] = True
                    
                    # 识别编程语言
                    self._detect_language(item, info["languages"])
                    
                    # 识别框架
                    self._detect_framework(item, info["frameworks"])
                
                elif item.is_dir():
                    relative_path = item.relative_to(dir_path)
                    if len(relative_path.parts) == 1:  # 只记录直接子目录
                        info["subdirs"].append(str(relative_path))
        
        except PermissionError:
            self.warnings.append(f"无法访问目录: {dir_path}")
        
        # 转换set为list以便JSON序列化
        info["languages"] = list(info["languages"])
        info["frameworks"] = list(info["frameworks"])
        
        return info
    
    def _detect_language(self, file_path: Path, languages: set):
        """检测编程语言"""
        extension_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".go": "Go",
            ".rs": "Rust",
            ".php": "PHP",
            ".rb": "Ruby",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".dart": "Dart",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".vue": "Vue",
            ".jsx": "React",
            ".tsx": "React"
        }
        
        if file_path.suffix.lower() in extension_map:
            languages.add(extension_map[file_path.suffix.lower()])
    
    def _detect_framework(self, file_path: Path, frameworks: set):
        """检测框架"""
        framework_indicators = {
            "package.json": ["React", "Vue", "Angular", "Express", "Node.js"],
            "requirements.txt": ["Django", "Flask", "FastAPI"],
            "pom.xml": ["Spring", "Maven"],
            "build.gradle": ["Spring", "Gradle"],
            "Cargo.toml": ["Rust"],
            "go.mod": ["Go"],
            "composer.json": ["Laravel", "Symfony"]
        }
        
        if file_path.name in framework_indicators:
            try:
                content = file_path.read_text(encoding='utf-8')
                for framework in framework_indicators[file_path.name]:
                    if framework.lower() in content.lower():
                        frameworks.add(framework)
            except (UnicodeDecodeError, PermissionError):
                pass
    
    def _is_competition_project(self, dir_name: str, dir_info: Dict) -> bool:
        """判断是否为竞赛项目"""
        competition_keywords = [
            "competition", "contest", "challenge", "hackathon", 
            "竞赛", "比赛", "挑战赛", "黑客松"
        ]
        
        # 检查目录名
        for keyword in competition_keywords:
            if keyword in dir_name.lower():
                return True
        
        # 检查是否包含年份
        for year in self.competition_years:
            if year in dir_name:
                return True
        
        # 检查README内容
        if dir_info["has_readme"]:
            try:
                readme_files = [f for f in dir_info["files"] if f.lower().endswith("readme.md")]
                if readme_files:
                    readme_path = self.root_path / dir_name / readme_files[0]
                    content = readme_path.read_text(encoding='utf-8').lower()
                    for keyword in competition_keywords:
                        if keyword in content:
                            return True
            except (UnicodeDecodeError, FileNotFoundError):
                pass
        
        return False
    
    def _is_regular_project(self, dir_name: str, dir_info: Dict) -> bool:
        """判断是否为常规项目"""
        # 排除系统目录和特殊目录
        excluded_dirs = [
            ".git", ".github", ".vscode", ".idea", "node_modules", 
            "__pycache__", "venv", "env", "build", "dist", "target",
            "migration_backup", "migration_logs", "scripts", "config", "templates"
        ]
        
        if dir_name in excluded_dirs or dir_name.startswith('.'):
            return False
        
        # 检查是否包含代码文件
        code_extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rs"]
        has_code = any(any(f.endswith(ext) for ext in code_extensions) for f in dir_info["files"])
        
        # 检查是否有配置文件或README
        has_project_files = dir_info["has_readme"] or dir_info["has_config"]
        
        return has_code or has_project_files
    
    def _extract_year(self, dir_name: str) -> Optional[str]:
        """提取年份"""
        for year in self.competition_years:
            if year in dir_name:
                return year
        
        # 使用正则表达式匹配年份
        year_match = re.search(r'20\d{2}', dir_name)
        if year_match:
            return year_match.group()
        
        return "2024"  # 默认年份
    
    def _categorize_project(self, dir_name: str, dir_info: Dict) -> str:
        """项目分类"""
        # 基于目录名分类
        for category, keywords in self.project_categories.items():
            for keyword in keywords:
                if keyword in dir_name.lower():
                    return category
        
        # 基于编程语言分类
        languages = set(dir_info["languages"])
        if "Python" in languages and any(fw in dir_info["frameworks"] for fw in ["Django", "Flask", "FastAPI"]):
            return "web"
        elif "JavaScript" in languages or "TypeScript" in languages:
            return "web"
        elif "Java" in languages and "Android" in dir_info["frameworks"]:
            return "mobile"
        elif "Swift" in languages or "Kotlin" in languages:
            return "mobile"
        elif "C++" in languages or "C" in languages:
            return "embedded"
        
        # 基于框架分类
        frameworks = set(dir_info["frameworks"])
        if any(fw in frameworks for fw in ["React", "Vue", "Angular", "Express", "Django", "Flask"]):
            return "web"
        elif "Spring" in frameworks:
            return "web"
        
        # 默认分类
        return "research"
    
    def create_new_structure(self) -> bool:
        """创建新目录结构"""
        print("🏗️  创建新目录结构")
        
        new_dirs = [
            "competitions_new",
            "competitions_new/2024",
            "competitions_new/2025",
            "projects_new",
            "projects_new/ai",
            "projects_new/robotics",
            "projects_new/embedded",
            "projects_new/web",
            "projects_new/mobile",
            "projects_new/desktop",
            "projects_new/research",
            "shared_new",
            "shared_new/media",
            "shared_new/models",
            "shared_new/code",
            "shared_new/tools",
            "docs_new",
            "docs_new/technical",
            "docs_new/tutorials",
            "docs_new/guides",
            "docs_new/standards",
            "docs_new/best_practices",
            "scripts",
            "scripts/build",
            "scripts/deploy",
            "scripts/test",
            "scripts/maintenance",
            "scripts/migration",
            "scripts/automation",
            "scripts/tools",
            "config",
            "config/environments",
            "config/applications",
            "config/infrastructure",
            "config/ci_cd",
            "config/security",
            "templates",
            "templates/project",
            "templates/competition",
            "templates/research",
            "templates/documentation"
        ]
        
        for dir_path in new_dirs:
            full_path = self.root_path / dir_path
            
            if self.dry_run:
                self.log_action("create_dir", "", str(full_path), "skipped", "dry-run模式")
                continue
            
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                self.log_action("create_dir", "", str(full_path), "success", "目录创建成功")
            except Exception as e:
                self.log_action("create_dir", "", str(full_path), "error", str(e))
                self.errors.append(f"创建目录失败: {full_path} - {e}")
                return False
        
        return True
    
    def migrate_projects(self, analysis: Dict) -> bool:
        """迁移项目"""
        print("🚚 开始迁移项目")
        
        success_count = 0
        failed_count = 0
        
        # 迁移竞赛项目
        for competition in analysis["competitions"]:
            source_path = self.root_path / competition["path"]
            target_path = self.root_path / "competitions_new" / competition["year"] / competition["name"]
            
            if self._migrate_single_project(source_path, target_path, "competition"):
                success_count += 1
            else:
                failed_count += 1
        
        # 迁移常规项目
        for project in analysis["projects"]:
            source_path = self.root_path / project["path"]
            target_path = self.root_path / "projects_new" / project["category"] / project["name"]
            
            if self._migrate_single_project(source_path, target_path, "project"):
                success_count += 1
            else:
                failed_count += 1
        
        print(f"📊 迁移完成: {success_count} 成功, {failed_count} 失败")
        return failed_count == 0
    
    def _migrate_single_project(self, source_path: Path, target_path: Path, project_type: str) -> bool:
        """迁移单个项目"""
        if not source_path.exists():
            self.log_action("migrate", str(source_path), str(target_path), "error", "源路径不存在")
            return False
        
        if target_path.exists():
            self.log_action("migrate", str(source_path), str(target_path), "warning", "目标路径已存在，跳过")
            return True
        
        if self.dry_run:
            self.log_action("migrate", str(source_path), str(target_path), "skipped", "dry-run模式")
            return True
        
        try:
            # 创建目标目录
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制项目文件
            shutil.copytree(source_path, target_path)
            
            # 更新项目内部的路径引用
            self._update_internal_references(target_path)
            
            self.log_action("migrate", str(source_path), str(target_path), "success", f"{project_type}迁移成功")
            return True
            
        except Exception as e:
            self.log_action("migrate", str(source_path), str(target_path), "error", str(e))
            self.errors.append(f"迁移失败: {source_path} -> {target_path} - {e}")
            return False
    
    def _update_internal_references(self, project_path: Path):
        """更新项目内部的路径引用"""
        # 需要更新的文件类型
        update_files = [
            "README.md", "*.md", "package.json", "requirements.txt",
            "*.py", "*.js", "*.ts", "*.html", "*.css"
        ]
        
        for pattern in update_files:
            for file_path in project_path.rglob(pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        
                        # 更新路径引用
                        for old_dir, new_dir in self.migration_mapping.items():
                            content = content.replace(f"/{old_dir}/", f"/{new_dir}/")
                            content = content.replace(f"\\{old_dir}\\", f"\\{new_dir}\\")
                            content = content.replace(f"./{old_dir}/", f"./{new_dir}/")
                            content = content.replace(f"../{old_dir}/", f"../{new_dir}/")
                        
                        file_path.write_text(content, encoding='utf-8')
                        
                    except (UnicodeDecodeError, PermissionError):
                        # 跳过二进制文件或无权限文件
                        continue
    
    def cleanup_old_structure(self, analysis: Dict) -> bool:
        """清理旧目录结构"""
        print("🧹 清理旧目录结构")
        
        if self.dry_run:
            print("⚠️  dry-run模式，跳过清理操作")
            return True
        
        # 询问用户确认
        response = input("⚠️  确定要删除旧目录结构吗？这个操作不可逆！(y/N): ")
        if response.lower() != 'y':
            print("❌ 用户取消清理操作")
            return False
        
        # 删除已迁移的项目目录
        for competition in analysis["competitions"]:
            old_path = self.root_path / competition["path"]
            self._safe_remove_directory(old_path)
        
        for project in analysis["projects"]:
            old_path = self.root_path / project["path"]
            self._safe_remove_directory(old_path)
        
        # 删除旧的主目录（如果为空）
        for old_dir in self.migration_mapping.keys():
            old_path = self.root_path / old_dir
            if old_path.exists() and self._is_directory_empty(old_path):
                self._safe_remove_directory(old_path)
        
        return True
    
    def _safe_remove_directory(self, dir_path: Path):
        """安全删除目录"""
        try:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.log_action("cleanup", str(dir_path), "", "success", "目录删除成功")
        except Exception as e:
            self.log_action("cleanup", str(dir_path), "", "error", str(e))
            self.errors.append(f"删除目录失败: {dir_path} - {e}")
    
    def _is_directory_empty(self, dir_path: Path) -> bool:
        """检查目录是否为空"""
        try:
            return not any(dir_path.iterdir())
        except OSError:
            return False
    
    def generate_migration_report(self, analysis: Dict) -> Dict:
        """生成迁移报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "root_path": str(self.root_path),
            "dry_run": self.dry_run,
            "analysis": analysis,
            "migration_log": self.migration_log,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_operations": len(self.migration_log),
                "successful_operations": len([log for log in self.migration_log if log["status"] == "success"]),
                "failed_operations": len([log for log in self.migration_log if log["status"] == "error"]),
                "skipped_operations": len([log for log in self.migration_log if log["status"] == "skipped"]),
                "total_errors": len(self.errors),
                "total_warnings": len(self.warnings),
                "migration_success": len(self.errors) == 0
            }
        }
        
        return report
    
    def save_migration_report(self, report: Dict):
        """保存迁移报告"""
        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.log_dir / f"migration_report_{timestamp}.json"
        
        # 保存JSON报告
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 生成可读性报告
        readable_report = self.log_dir / f"migration_summary_{timestamp}.txt"
        with open(readable_report, 'w', encoding='utf-8') as f:
            f.write(f"项目迁移报告\n")
            f.write(f"生成时间: {report['timestamp']}\n")
            f.write(f"项目路径: {report['root_path']}\n")
            f.write(f"运行模式: {'Dry Run' if report['dry_run'] else 'Normal'}\n\n")
            
            f.write(f"迁移统计:\n")
            f.write(f"  总操作数: {report['summary']['total_operations']}\n")
            f.write(f"  成功操作: {report['summary']['successful_operations']}\n")
            f.write(f"  失败操作: {report['summary']['failed_operations']}\n")
            f.write(f"  跳过操作: {report['summary']['skipped_operations']}\n")
            f.write(f"  错误数量: {report['summary']['total_errors']}\n")
            f.write(f"  警告数量: {report['summary']['total_warnings']}\n")
            f.write(f"  迁移结果: {'成功' if report['summary']['migration_success'] else '失败'}\n\n")
            
            if report['errors']:
                f.write("错误列表:\n")
                for error in report['errors']:
                    f.write(f"  - {error}\n")
                f.write("\n")
            
            if report['warnings']:
                f.write("警告列表:\n")
                for warning in report['warnings']:
                    f.write(f"  - {warning}\n")
        
        print(f"📄 迁移报告已保存:")
        print(f"   JSON报告: {report_file}")
        print(f"   摘要报告: {readable_report}")
    
    def run_migration(self, skip_backup: bool = False, skip_cleanup: bool = False) -> bool:
        """运行完整迁移流程"""
        print(f"🚀 开始项目迁移: {self.root_path}")
        print(f"📋 运行模式: {'Dry Run (预览模式)' if self.dry_run else 'Normal (实际执行)'}")
        print("=" * 60)
        
        try:
            # 1. 创建备份
            if not skip_backup and not self.create_backup():
                print("❌ 备份失败，迁移中止")
                return False
            
            # 2. 分析现有结构
            analysis = self.analyze_project_structure()
            
            # 3. 创建新目录结构
            if not self.create_new_structure():
                print("❌ 创建新目录结构失败")
                return False
            
            # 4. 迁移项目
            if not self.migrate_projects(analysis):
                print("⚠️  部分项目迁移失败")
            
            # 5. 清理旧结构（可选）
            if not skip_cleanup and not self.dry_run:
                self.cleanup_old_structure(analysis)
            
            # 6. 生成报告
            report = self.generate_migration_report(analysis)
            self.save_migration_report(report)
            
            # 7. 输出结果
            print("\n" + "=" * 60)
            print("📊 迁移结果汇总")
            print("=" * 60)
            
            if report["summary"]["migration_success"]:
                print("🎉 迁移成功完成！")
            else:
                print("⚠️  迁移完成，但存在错误")
            
            print(f"📈 统计: {report['summary']['successful_operations']} 成功, "
                  f"{report['summary']['failed_operations']} 失败, "
                  f"{report['summary']['skipped_operations']} 跳过")
            
            if self.dry_run:
                print("\n💡 这是预览模式，没有实际修改文件。")
                print("   要执行实际迁移，请移除 --dry-run 参数。")
            
            return report["summary"]["migration_success"]
            
        except Exception as e:
            self.log_action("migration", "", "", "error", f"迁移过程中发生未预期错误: {e}")
            print(f"❌ 迁移失败: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="项目迁移工具")
    parser.add_argument(
        "--path", 
        default=".", 
        help="要迁移的项目路径 (默认: 当前目录)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="预览模式：只显示将要执行的操作，不实际修改文件"
    )
    parser.add_argument(
        "--skip-backup", 
        action="store_true",
        help="跳过备份步骤"
    )
    parser.add_argument(
        "--skip-cleanup", 
        action="store_true",
        help="跳过清理旧目录结构"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="强制执行，不询问确认"
    )
    
    args = parser.parse_args()
    
    # 安全检查
    if not args.dry_run and not args.force:
        print("⚠️  警告：这个操作将修改您的项目结构！")
        print("   建议先使用 --dry-run 参数预览迁移计划。")
        response = input("   确定要继续吗？(y/N): ")
        if response.lower() != 'y':
            print("❌ 用户取消操作")
            sys.exit(0)
    
    # 创建迁移器并运行迁移
    migrator = ProjectMigrator(args.path, args.dry_run)
    success = migrator.run_migration(args.skip_backup, args.skip_cleanup)
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()