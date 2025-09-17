#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新能源编程俱乐部自动化迁移脚本

功能:
- 基于结构蓝图自动迁移现有项目
- 保持Git历史记录完整
- 实现增量迁移和回滚机制
- 生成详细的迁移日志和验证报告
- 支持批量迁移和优先级排序

作者: 新能源编程俱乐部
日期: 2025-01-18
"""

import os
import json
import shutil
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_migrator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

@dataclass
class MigrationTask:
    """迁移任务数据结构"""
    id: str
    source_path: str
    target_path: str
    priority: str  # high, medium, low
    category: str
    subcategory: str
    project_name: str
    size_mb: float
    file_count: int
    complexity: str
    migration_type: str  # move, copy, symlink
    dependencies: List[str]
    status: str  # pending, in_progress, completed, failed, skipped
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    backup_path: Optional[str] = None

@dataclass
class MigrationReport:
    """迁移报告数据结构"""
    migration_id: str
    start_time: str
    end_time: Optional[str]
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    skipped_tasks: int
    total_size_mb: float
    total_files: int
    tasks: List[MigrationTask]
    git_commits: List[str]
    backup_location: str
    rollback_available: bool
    validation_results: Dict[str, Any]

class AutoMigrator:
    """自动化迁移器"""
    
    def __init__(self, root_path: str, blueprint_path: str = None, analysis_report_path: str = None):
        self.root_path = Path(root_path)
        self.blueprint = None
        self.analysis_report = None
        self.migration_tasks = []
        self.migration_report = None
        
        # 迁移配置
        self.config = {
            'preserve_git_history': True,
            'create_backup': True,
            'use_git_mv': True,
            'parallel_migration': True,
            'max_workers': 4,
            'dry_run': False,
            'force_overwrite': False,
            'skip_validation': False,
            'rollback_on_failure': True
        }
        
        # 加载数据
        if blueprint_path:
            self.load_blueprint(blueprint_path)
        if analysis_report_path:
            self.load_analysis_report(analysis_report_path)
        
        # 初始化Git仓库检查
        self.is_git_repo = self._check_git_repository()
        
        # 创建备份目录
        self.backup_dir = self.root_path / 'backup' / f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def load_blueprint(self, blueprint_path: str):
        """加载结构蓝图"""
        try:
            with open(blueprint_path, 'r', encoding='utf-8') as f:
                self.blueprint = json.load(f)
            logging.info(f"已加载结构蓝图: {blueprint_path}")
        except Exception as e:
            logging.error(f"加载结构蓝图失败: {e}")
            raise
    
    def load_analysis_report(self, report_path: str):
        """加载项目分析报告"""
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                self.analysis_report = json.load(f)
            logging.info(f"已加载分析报告: {report_path}")
        except Exception as e:
            logging.error(f"加载分析报告失败: {e}")
            raise
    
    def _check_git_repository(self) -> bool:
        """检查是否为Git仓库"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def generate_migration_tasks(self) -> List[MigrationTask]:
        """生成迁移任务列表"""
        if not self.blueprint or not self.analysis_report:
            raise ValueError("请先加载结构蓝图和分析报告")
        
        logging.info("生成迁移任务列表")
        
        tasks = []
        migration_mapping = self.blueprint.get('migration_mapping', {})
        projects = self.analysis_report.get('projects', [])
        
        # 创建项目映射
        project_map = {proj['path']: proj for proj in projects}
        
        for source_path, target_path in migration_mapping.items():
            # 检查源路径是否存在
            full_source_path = self.root_path / source_path
            if not full_source_path.exists():
                logging.warning(f"源路径不存在，跳过: {source_path}")
                continue
            
            # 获取项目信息
            project_info = project_map.get(source_path, {})
            
            # 生成任务ID
            task_id = f"task_{len(tasks):04d}_{datetime.now().strftime('%H%M%S')}"
            
            # 确定迁移类型
            migration_type = self._determine_migration_type(source_path, target_path)
            
            # 创建迁移任务
            task = MigrationTask(
                id=task_id,
                source_path=source_path,
                target_path=target_path,
                priority=project_info.get('priority', 'medium'),
                category=project_info.get('category', 'unknown'),
                subcategory=project_info.get('subcategory', 'unknown'),
                project_name=project_info.get('name', Path(source_path).name),
                size_mb=project_info.get('size_mb', 0),
                file_count=project_info.get('file_count', 0),
                complexity=project_info.get('complexity', 'medium'),
                migration_type=migration_type,
                dependencies=self._find_dependencies(source_path, migration_mapping),
                status='pending'
            )
            
            tasks.append(task)
        
        # 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        tasks.sort(key=lambda t: (priority_order.get(t.priority, 3), t.size_mb), reverse=True)
        
        self.migration_tasks = tasks
        logging.info(f"生成了 {len(tasks)} 个迁移任务")
        
        return tasks
    
    def _determine_migration_type(self, source_path: str, target_path: str) -> str:
        """确定迁移类型"""
        # 如果是Git仓库且配置使用git mv，则使用move
        if self.is_git_repo and self.config['use_git_mv']:
            return 'move'
        
        # 如果目标路径已存在，使用copy
        full_target_path = self.root_path / target_path
        if full_target_path.exists():
            return 'copy'
        
        # 默认使用move
        return 'move'
    
    def _find_dependencies(self, source_path: str, migration_mapping: Dict[str, str]) -> List[str]:
        """查找项目依赖关系"""
        dependencies = []
        
        # 简单的依赖检测：如果源路径包含在其他路径中，则存在依赖
        for other_source, other_target in migration_mapping.items():
            if other_source != source_path:
                if source_path.startswith(other_source + '/'):
                    dependencies.append(other_source)
                elif other_source.startswith(source_path + '/'):
                    dependencies.append(other_source)
        
        return dependencies
    
    def create_backup(self) -> bool:
        """创建完整备份"""
        if not self.config['create_backup']:
            return True
        
        logging.info(f"创建备份到: {self.backup_dir}")
        
        try:
            # 备份所有待迁移的源路径
            for task in self.migration_tasks:
                source_path = self.root_path / task.source_path
                if source_path.exists():
                    backup_path = self.backup_dir / task.source_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if source_path.is_dir():
                        shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_path, backup_path)
                    
                    task.backup_path = str(backup_path)
            
            # 备份Git状态
            if self.is_git_repo:
                self._backup_git_state()
            
            logging.info("备份创建完成")
            return True
        
        except Exception as e:
            logging.error(f"创建备份失败: {e}")
            return False
    
    def _backup_git_state(self):
        """备份Git状态"""
        try:
            # 保存当前分支信息
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip()
            
            # 保存Git状态信息
            git_info = {
                'current_branch': current_branch,
                'commit_hash': self._get_current_commit_hash(),
                'status': self._get_git_status(),
                'backup_time': datetime.now().isoformat()
            }
            
            git_backup_file = self.backup_dir / 'git_state.json'
            with open(git_backup_file, 'w', encoding='utf-8') as f:
                json.dump(git_info, f, ensure_ascii=False, indent=2)
            
            logging.info(f"Git状态已备份: {git_backup_file}")
        
        except Exception as e:
            logging.warning(f"备份Git状态失败: {e}")
    
    def _get_current_commit_hash(self) -> str:
        """获取当前提交哈希"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception:
            return ''
    
    def _get_git_status(self) -> str:
        """获取Git状态"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception:
            return ''
    
    def execute_migration(self, dry_run: bool = False) -> MigrationReport:
        """执行迁移"""
        if not self.migration_tasks:
            raise ValueError("请先生成迁移任务")
        
        self.config['dry_run'] = dry_run
        
        # 初始化迁移报告
        migration_id = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.migration_report = MigrationReport(
            migration_id=migration_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            total_tasks=len(self.migration_tasks),
            completed_tasks=0,
            failed_tasks=0,
            skipped_tasks=0,
            total_size_mb=sum(task.size_mb for task in self.migration_tasks),
            total_files=sum(task.file_count for task in self.migration_tasks),
            tasks=self.migration_tasks,
            git_commits=[],
            backup_location=str(self.backup_dir),
            rollback_available=self.config['create_backup'],
            validation_results={}
        )
        
        logging.info(f"开始执行迁移 (干运行: {dry_run})")
        logging.info(f"总任务数: {len(self.migration_tasks)}")
        
        try:
            # 创建备份
            if not dry_run and not self.create_backup():
                raise Exception("创建备份失败")
            
            # 执行迁移任务
            if self.config['parallel_migration']:
                self._execute_parallel_migration()
            else:
                self._execute_sequential_migration()
            
            # 更新统计信息
            self._update_migration_statistics()
            
            # 验证迁移结果
            if not self.config['skip_validation']:
                self._validate_migration()
            
            # 提交Git更改
            if not dry_run and self.is_git_repo:
                self._commit_migration_changes()
            
            self.migration_report.end_time = datetime.now().isoformat()
            
            logging.info("迁移执行完成")
            logging.info(f"成功: {self.migration_report.completed_tasks}")
            logging.info(f"失败: {self.migration_report.failed_tasks}")
            logging.info(f"跳过: {self.migration_report.skipped_tasks}")
            
            return self.migration_report
        
        except Exception as e:
            logging.error(f"迁移执行失败: {e}")
            
            # 如果配置了失败回滚，执行回滚
            if self.config['rollback_on_failure'] and not dry_run:
                self.rollback_migration()
            
            raise
    
    def _execute_parallel_migration(self):
        """并行执行迁移"""
        max_workers = self.config['max_workers']
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(self._execute_single_task, task): task
                for task in self.migration_tasks
                if task.status == 'pending'
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"任务 {task.id} 执行失败: {e}")
                    task.status = 'failed'
                    task.error_message = str(e)
    
    def _execute_sequential_migration(self):
        """顺序执行迁移"""
        for task in self.migration_tasks:
            if task.status == 'pending':
                try:
                    self._execute_single_task(task)
                except Exception as e:
                    logging.error(f"任务 {task.id} 执行失败: {e}")
                    task.status = 'failed'
                    task.error_message = str(e)
    
    def _execute_single_task(self, task: MigrationTask):
        """执行单个迁移任务"""
        task.status = 'in_progress'
        task.start_time = datetime.now().isoformat()
        
        logging.info(f"执行任务 {task.id}: {task.source_path} -> {task.target_path}")
        
        try:
            source_path = self.root_path / task.source_path
            target_path = self.root_path / task.target_path
            
            # 检查源路径是否存在
            if not source_path.exists():
                task.status = 'skipped'
                task.error_message = '源路径不存在'
                return
            
            # 创建目标目录
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查目标路径是否已存在
            if target_path.exists() and not self.config['force_overwrite']:
                task.status = 'skipped'
                task.error_message = '目标路径已存在'
                return
            
            # 执行迁移操作
            if not self.config['dry_run']:
                if task.migration_type == 'move':
                    self._move_path(source_path, target_path, task)
                elif task.migration_type == 'copy':
                    self._copy_path(source_path, target_path, task)
                elif task.migration_type == 'symlink':
                    self._create_symlink(source_path, target_path, task)
            
            task.status = 'completed'
            task.end_time = datetime.now().isoformat()
            
            logging.info(f"任务 {task.id} 完成")
        
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.end_time = datetime.now().isoformat()
            raise
    
    def _move_path(self, source_path: Path, target_path: Path, task: MigrationTask):
        """移动路径"""
        if self.is_git_repo and self.config['use_git_mv']:
            # 使用git mv保持历史记录
            result = subprocess.run(
                ['git', 'mv', str(source_path), str(target_path)],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # 如果git mv失败，回退到普通移动
                logging.warning(f"git mv失败，使用普通移动: {result.stderr}")
                shutil.move(str(source_path), str(target_path))
        else:
            # 普通移动
            shutil.move(str(source_path), str(target_path))
    
    def _copy_path(self, source_path: Path, target_path: Path, task: MigrationTask):
        """复制路径"""
        if source_path.is_dir():
            shutil.copytree(source_path, target_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, target_path)
    
    def _create_symlink(self, source_path: Path, target_path: Path, task: MigrationTask):
        """创建符号链接"""
        target_path.symlink_to(source_path.resolve())
    
    def _update_migration_statistics(self):
        """更新迁移统计信息"""
        completed = sum(1 for task in self.migration_tasks if task.status == 'completed')
        failed = sum(1 for task in self.migration_tasks if task.status == 'failed')
        skipped = sum(1 for task in self.migration_tasks if task.status == 'skipped')
        
        self.migration_report.completed_tasks = completed
        self.migration_report.failed_tasks = failed
        self.migration_report.skipped_tasks = skipped
    
    def _validate_migration(self):
        """验证迁移结果"""
        logging.info("验证迁移结果")
        
        validation_results = {
            'total_validated': 0,
            'validation_passed': 0,
            'validation_failed': 0,
            'missing_targets': [],
            'size_mismatches': [],
            'permission_issues': []
        }
        
        for task in self.migration_tasks:
            if task.status == 'completed':
                validation_results['total_validated'] += 1
                
                target_path = self.root_path / task.target_path
                
                # 检查目标路径是否存在
                if not target_path.exists():
                    validation_results['validation_failed'] += 1
                    validation_results['missing_targets'].append(task.target_path)
                    continue
                
                # 检查大小（对于文件）
                if target_path.is_file() and task.migration_type in ['move', 'copy']:
                    if task.backup_path:
                        backup_path = Path(task.backup_path)
                        if backup_path.exists():
                            backup_size = backup_path.stat().st_size
                            target_size = target_path.stat().st_size
                            
                            if backup_size != target_size:
                                validation_results['validation_failed'] += 1
                                validation_results['size_mismatches'].append({
                                    'path': task.target_path,
                                    'expected_size': backup_size,
                                    'actual_size': target_size
                                })
                                continue
                
                validation_results['validation_passed'] += 1
        
        self.migration_report.validation_results = validation_results
        
        logging.info(f"验证完成: {validation_results['validation_passed']}/{validation_results['total_validated']} 通过")
    
    def _commit_migration_changes(self):
        """提交Git更改"""
        try:
            # 添加所有更改
            subprocess.run(
                ['git', 'add', '.'],
                cwd=self.root_path,
                check=True
            )
            
            # 提交更改
            commit_message = f"feat: 自动迁移项目到标准化目录结构\n\n" \
                           f"- 迁移任务数: {len(self.migration_tasks)}\n" \
                           f"- 成功: {self.migration_report.completed_tasks}\n" \
                           f"- 失败: {self.migration_report.failed_tasks}\n" \
                           f"- 跳过: {self.migration_report.skipped_tasks}\n" \
                           f"- 迁移ID: {self.migration_report.migration_id}"
            
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commit_hash = self._get_current_commit_hash()
                self.migration_report.git_commits.append(commit_hash)
                logging.info(f"Git提交成功: {commit_hash}")
            else:
                logging.warning(f"Git提交失败: {result.stderr}")
        
        except Exception as e:
            logging.error(f"Git提交失败: {e}")
    
    def rollback_migration(self) -> bool:
        """回滚迁移"""
        if not self.migration_report or not self.migration_report.rollback_available:
            logging.error("无法回滚：没有可用的备份")
            return False
        
        logging.info("开始回滚迁移")
        
        try:
            # 恢复文件
            for task in self.migration_tasks:
                if task.status == 'completed' and task.backup_path:
                    backup_path = Path(task.backup_path)
                    target_path = self.root_path / task.target_path
                    source_path = self.root_path / task.source_path
                    
                    # 删除目标文件/目录
                    if target_path.exists():
                        if target_path.is_dir():
                            shutil.rmtree(target_path)
                        else:
                            target_path.unlink()
                    
                    # 恢复源文件/目录
                    if backup_path.exists():
                        source_path.parent.mkdir(parents=True, exist_ok=True)
                        if backup_path.is_dir():
                            shutil.copytree(backup_path, source_path)
                        else:
                            shutil.copy2(backup_path, source_path)
            
            # 恢复Git状态
            if self.is_git_repo:
                self._rollback_git_changes()
            
            logging.info("迁移回滚完成")
            return True
        
        except Exception as e:
            logging.error(f"回滚失败: {e}")
            return False
    
    def _rollback_git_changes(self):
        """回滚Git更改"""
        try:
            # 重置到迁移前的状态
            git_state_file = self.backup_dir / 'git_state.json'
            if git_state_file.exists():
                with open(git_state_file, 'r', encoding='utf-8') as f:
                    git_info = json.load(f)
                
                commit_hash = git_info.get('commit_hash')
                if commit_hash:
                    subprocess.run(
                        ['git', 'reset', '--hard', commit_hash],
                        cwd=self.root_path,
                        check=True
                    )
                    logging.info(f"Git状态已恢复到: {commit_hash}")
        
        except Exception as e:
            logging.error(f"Git回滚失败: {e}")
    
    def save_migration_report(self, output_file: str = None) -> str:
        """保存迁移报告"""
        if not self.migration_report:
            raise ValueError("没有可保存的迁移报告")
        
        if not output_file:
            output_file = f'migration_report_{self.migration_report.migration_id}.json'
        
        output_path = self.root_path / output_file
        
        # 转换为可序列化的格式
        report_dict = asdict(self.migration_report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
        
        logging.info(f"迁移报告已保存: {output_path}")
        return str(output_path)
    
    def generate_migration_summary(self) -> str:
        """生成迁移摘要"""
        if not self.migration_report:
            return "没有可用的迁移报告"
        
        report = self.migration_report
        
        summary = f"""
# 迁移摘要报告

## 基本信息
- **迁移ID**: {report.migration_id}
- **开始时间**: {report.start_time}
- **结束时间**: {report.end_time or '进行中'}
- **备份位置**: {report.backup_location}

## 统计信息
- **总任务数**: {report.total_tasks}
- **成功完成**: {report.completed_tasks}
- **执行失败**: {report.failed_tasks}
- **跳过执行**: {report.skipped_tasks}
- **总文件大小**: {report.total_size_mb:.2f} MB
- **总文件数量**: {report.total_files}

## 执行结果
- **成功率**: {(report.completed_tasks / report.total_tasks * 100):.1f}%
- **回滚可用**: {'是' if report.rollback_available else '否'}
- **Git提交**: {len(report.git_commits)} 个

## 验证结果
"""
        
        if report.validation_results:
            validation = report.validation_results
            summary += f"""
- **验证总数**: {validation.get('total_validated', 0)}
- **验证通过**: {validation.get('validation_passed', 0)}
- **验证失败**: {validation.get('validation_failed', 0)}
- **缺失目标**: {len(validation.get('missing_targets', []))}
- **大小不匹配**: {len(validation.get('size_mismatches', []))}
"""
        
        # 按状态分组显示任务
        completed_tasks = [t for t in report.tasks if t.status == 'completed']
        failed_tasks = [t for t in report.tasks if t.status == 'failed']
        skipped_tasks = [t for t in report.tasks if t.status == 'skipped']
        
        if completed_tasks:
            summary += "\n## 成功完成的任务\n\n"
            for task in completed_tasks[:10]:  # 只显示前10个
                summary += f"- `{task.source_path}` → `{task.target_path}`\n"
            if len(completed_tasks) > 10:
                summary += f"- ... 还有 {len(completed_tasks) - 10} 个任务\n"
        
        if failed_tasks:
            summary += "\n## 失败的任务\n\n"
            for task in failed_tasks:
                summary += f"- `{task.source_path}`: {task.error_message}\n"
        
        if skipped_tasks:
            summary += "\n## 跳过的任务\n\n"
            for task in skipped_tasks[:5]:  # 只显示前5个
                summary += f"- `{task.source_path}`: {task.error_message}\n"
            if len(skipped_tasks) > 5:
                summary += f"- ... 还有 {len(skipped_tasks) - 5} 个任务\n"
        
        return summary

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新能源编程俱乐部自动化迁移脚本")
    parser.add_argument('--root', '-r', default='.', help='项目根目录路径')
    parser.add_argument('--blueprint', '-b', required=True, help='结构蓝图文件路径')
    parser.add_argument('--analysis', '-a', required=True, help='项目分析报告路径')
    parser.add_argument('--dry-run', '-d', action='store_true', help='干运行模式（不实际执行）')
    parser.add_argument('--parallel', '-p', action='store_true', help='并行执行迁移')
    parser.add_argument('--workers', '-w', type=int, default=4, help='并行工作线程数')
    parser.add_argument('--force', '-f', action='store_true', help='强制覆盖已存在的目标')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份')
    parser.add_argument('--no-git', action='store_true', help='不使用Git操作')
    parser.add_argument('--rollback', action='store_true', help='回滚上次迁移')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 初始化迁移器
        migrator = AutoMigrator(args.root, args.blueprint, args.analysis)
        
        # 更新配置
        migrator.config.update({
            'parallel_migration': args.parallel,
            'max_workers': args.workers,
            'force_overwrite': args.force,
            'create_backup': not args.no_backup,
            'use_git_mv': not args.no_git
        })
        
        if args.rollback:
            # 执行回滚
            print("执行迁移回滚...")
            success = migrator.rollback_migration()
            if success:
                print("✅ 回滚成功")
            else:
                print("❌ 回滚失败")
            return
        
        # 生成迁移任务
        print("生成迁移任务...")
        tasks = migrator.generate_migration_tasks()
        print(f"生成了 {len(tasks)} 个迁移任务")
        
        # 显示任务摘要
        priority_counts = {}
        for task in tasks:
            priority_counts[task.priority] = priority_counts.get(task.priority, 0) + 1
        
        print("\n任务优先级分布:")
        for priority, count in priority_counts.items():
            print(f"  {priority}: {count} 个")
        
        # 执行迁移
        print(f"\n开始执行迁移 (干运行: {args.dry_run})...")
        report = migrator.execute_migration(dry_run=args.dry_run)
        
        # 保存报告
        report_file = migrator.save_migration_report()
        print(f"\n迁移报告已保存: {report_file}")
        
        # 显示摘要
        print("\n" + "="*50)
        print(migrator.generate_migration_summary())
        
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        logging.error(f"迁移失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()