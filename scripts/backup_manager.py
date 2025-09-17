#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新能源编程俱乐部备份和回滚管理器

功能:
- 创建完整的项目备份
- 支持增量备份和差异备份
- 实现快速回滚机制
- 管理备份版本和清理
- 验证备份完整性
- 支持Git集成和状态保存

作者: 新能源编程俱乐部
日期: 2025-01-18
"""

import os
import json
import shutil
import hashlib
import logging
import argparse
import subprocess
import tarfile
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

@dataclass
class BackupItem:
    """备份项数据结构"""
    path: str
    size: int
    checksum: str
    modified_time: str
    backup_time: str
    backup_type: str  # full, incremental, differential
    compression: str  # none, zip, tar.gz
    status: str  # pending, completed, failed

@dataclass
class BackupMetadata:
    """备份元数据"""
    backup_id: str
    backup_type: str
    creation_time: str
    completion_time: Optional[str]
    source_path: str
    backup_path: str
    total_size: int
    total_files: int
    compression_ratio: float
    git_commit: Optional[str]
    git_branch: Optional[str]
    items: List[BackupItem]
    verification_status: str
    retention_policy: str
    tags: List[str]

@dataclass
class RestorePoint:
    """恢复点数据结构"""
    restore_id: str
    backup_id: str
    creation_time: str
    description: str
    git_state: Dict[str, Any]
    file_state: Dict[str, Any]
    dependencies: List[str]
    rollback_script: str

class BackupManager:
    """备份和回滚管理器"""
    
    def __init__(self, root_path: str, backup_root: str = None):
        self.root_path = Path(root_path)
        self.backup_root = Path(backup_root) if backup_root else self.root_path / 'backup'
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        # 备份配置
        self.config = {
            'compression': 'tar.gz',  # none, zip, tar.gz
            'verify_backup': True,
            'parallel_backup': True,
            'max_workers': 4,
            'chunk_size': 1024 * 1024,  # 1MB
            'exclude_patterns': [
                '.git/objects/*',
                '*.pyc',
                '__pycache__/*',
                'node_modules/*',
                '.DS_Store',
                'Thumbs.db',
                '*.tmp',
                '*.log'
            ],
            'retention_days': 30,
            'max_backups': 50,
            'auto_cleanup': True
        }
        
        # 元数据存储
        self.metadata_file = self.backup_root / 'backup_metadata.json'
        self.restore_points_file = self.backup_root / 'restore_points.json'
        
        # 加载现有元数据
        self.backups = self._load_backup_metadata()
        self.restore_points = self._load_restore_points()
        
        # Git仓库检查
        self.is_git_repo = self._check_git_repository()
    
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
    
    def _load_backup_metadata(self) -> Dict[str, BackupMetadata]:
        """加载备份元数据"""
        if not self.metadata_file.exists():
            return {}
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            backups = {}
            for backup_id, backup_data in data.items():
                # 转换为BackupMetadata对象
                items = [BackupItem(**item) for item in backup_data.get('items', [])]
                backup_data['items'] = items
                backups[backup_id] = BackupMetadata(**backup_data)
            
            return backups
        
        except Exception as e:
            logging.error(f"加载备份元数据失败: {e}")
            return {}
    
    def _save_backup_metadata(self):
        """保存备份元数据"""
        try:
            data = {}
            for backup_id, metadata in self.backups.items():
                data[backup_id] = asdict(metadata)
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logging.error(f"保存备份元数据失败: {e}")
    
    def _load_restore_points(self) -> Dict[str, RestorePoint]:
        """加载恢复点"""
        if not self.restore_points_file.exists():
            return {}
        
        try:
            with open(self.restore_points_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            restore_points = {}
            for restore_id, point_data in data.items():
                restore_points[restore_id] = RestorePoint(**point_data)
            
            return restore_points
        
        except Exception as e:
            logging.error(f"加载恢复点失败: {e}")
            return {}
    
    def _save_restore_points(self):
        """保存恢复点"""
        try:
            data = {}
            for restore_id, point in self.restore_points.items():
                data[restore_id] = asdict(point)
            
            with open(self.restore_points_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logging.error(f"保存恢复点失败: {e}")
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        hash_md5 = hashlib.md5()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(self.config['chunk_size']), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logging.warning(f"计算校验和失败 {file_path}: {e}")
            return ''
    
    def _should_exclude(self, path: Path) -> bool:
        """检查路径是否应该被排除"""
        path_str = str(path.relative_to(self.root_path))
        
        for pattern in self.config['exclude_patterns']:
            if self._match_pattern(path_str, pattern):
                return True
        
        return False
    
    def _match_pattern(self, path: str, pattern: str) -> bool:
        """简单的模式匹配"""
        import fnmatch
        return fnmatch.fnmatch(path, pattern)
    
    def _collect_files(self, source_path: Path) -> List[Path]:
        """收集需要备份的文件"""
        files = []
        
        if source_path.is_file():
            if not self._should_exclude(source_path):
                files.append(source_path)
        elif source_path.is_dir():
            for item in source_path.rglob('*'):
                if item.is_file() and not self._should_exclude(item):
                    files.append(item)
        
        return files
    
    def create_backup(self, 
                     backup_type: str = 'full',
                     description: str = '',
                     tags: List[str] = None,
                     paths: List[str] = None) -> str:
        """创建备份"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logging.info(f"开始创建备份: {backup_id} (类型: {backup_type})")
        
        # 确定备份路径
        if paths is None:
            paths = [str(self.root_path)]
        
        # 创建备份目录
        backup_dir = self.backup_root / backup_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 收集文件
            all_files = []
            for path_str in paths:
                path = Path(path_str)
                if not path.is_absolute():
                    path = self.root_path / path
                all_files.extend(self._collect_files(path))
            
            logging.info(f"收集到 {len(all_files)} 个文件")
            
            # 创建备份项
            backup_items = []
            total_size = 0
            
            # 获取Git状态
            git_commit = None
            git_branch = None
            if self.is_git_repo:
                git_commit = self._get_current_commit_hash()
                git_branch = self._get_current_branch()
            
            # 执行备份
            if self.config['parallel_backup']:
                backup_items = self._backup_files_parallel(all_files, backup_dir)
            else:
                backup_items = self._backup_files_sequential(all_files, backup_dir)
            
            # 计算总大小
            total_size = sum(item.size for item in backup_items)
            
            # 压缩备份（如果配置了压缩）
            compressed_size = total_size
            if self.config['compression'] != 'none':
                compressed_size = self._compress_backup(backup_dir, backup_id)
            
            # 创建备份元数据
            metadata = BackupMetadata(
                backup_id=backup_id,
                backup_type=backup_type,
                creation_time=datetime.now().isoformat(),
                completion_time=datetime.now().isoformat(),
                source_path=str(self.root_path),
                backup_path=str(backup_dir),
                total_size=total_size,
                total_files=len(backup_items),
                compression_ratio=compressed_size / total_size if total_size > 0 else 1.0,
                git_commit=git_commit,
                git_branch=git_branch,
                items=backup_items,
                verification_status='pending',
                retention_policy=f"{self.config['retention_days']}d",
                tags=tags or []
            )
            
            # 验证备份
            if self.config['verify_backup']:
                metadata.verification_status = 'verified' if self._verify_backup(metadata) else 'failed'
            
            # 保存元数据
            self.backups[backup_id] = metadata
            self._save_backup_metadata()
            
            # 自动清理旧备份
            if self.config['auto_cleanup']:
                self._cleanup_old_backups()
            
            logging.info(f"备份创建完成: {backup_id}")
            logging.info(f"文件数量: {len(backup_items)}")
            logging.info(f"总大小: {total_size / 1024 / 1024:.2f} MB")
            logging.info(f"压缩比: {metadata.compression_ratio:.2f}")
            
            return backup_id
        
        except Exception as e:
            logging.error(f"创建备份失败: {e}")
            # 清理失败的备份
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            raise
    
    def _backup_files_sequential(self, files: List[Path], backup_dir: Path) -> List[BackupItem]:
        """顺序备份文件"""
        backup_items = []
        
        for file_path in files:
            try:
                item = self._backup_single_file(file_path, backup_dir)
                if item:
                    backup_items.append(item)
            except Exception as e:
                logging.error(f"备份文件失败 {file_path}: {e}")
        
        return backup_items
    
    def _backup_files_parallel(self, files: List[Path], backup_dir: Path) -> List[BackupItem]:
        """并行备份文件"""
        backup_items = []
        
        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(self._backup_single_file, file_path, backup_dir): file_path
                for file_path in files
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    item = future.result()
                    if item:
                        backup_items.append(item)
                except Exception as e:
                    logging.error(f"备份文件失败 {file_path}: {e}")
        
        return backup_items
    
    def _backup_single_file(self, file_path: Path, backup_dir: Path) -> Optional[BackupItem]:
        """备份单个文件"""
        try:
            # 计算相对路径
            rel_path = file_path.relative_to(self.root_path)
            backup_file_path = backup_dir / rel_path
            
            # 创建目标目录
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(file_path, backup_file_path)
            
            # 获取文件信息
            stat = file_path.stat()
            checksum = self._calculate_file_checksum(file_path)
            
            return BackupItem(
                path=str(rel_path),
                size=stat.st_size,
                checksum=checksum,
                modified_time=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                backup_time=datetime.now().isoformat(),
                backup_type='full',
                compression='none',
                status='completed'
            )
        
        except Exception as e:
            logging.error(f"备份文件失败 {file_path}: {e}")
            return None
    
    def _compress_backup(self, backup_dir: Path, backup_id: str) -> int:
        """压缩备份"""
        compression = self.config['compression']
        
        if compression == 'zip':
            archive_path = backup_dir.parent / f"{backup_id}.zip"
            return self._create_zip_archive(backup_dir, archive_path)
        elif compression == 'tar.gz':
            archive_path = backup_dir.parent / f"{backup_id}.tar.gz"
            return self._create_tar_archive(backup_dir, archive_path)
        
        return sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
    
    def _create_zip_archive(self, source_dir: Path, archive_path: Path) -> int:
        """创建ZIP压缩包"""
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
        
        # 删除原始目录
        shutil.rmtree(source_dir)
        
        return archive_path.stat().st_size
    
    def _create_tar_archive(self, source_dir: Path, archive_path: Path) -> int:
        """创建TAR.GZ压缩包"""
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(source_dir, arcname=source_dir.name)
        
        # 删除原始目录
        shutil.rmtree(source_dir)
        
        return archive_path.stat().st_size
    
    def _verify_backup(self, metadata: BackupMetadata) -> bool:
        """验证备份完整性"""
        logging.info(f"验证备份: {metadata.backup_id}")
        
        try:
            backup_path = Path(metadata.backup_path)
            
            # 检查备份路径是否存在
            if not backup_path.exists():
                # 检查是否有压缩文件
                for ext in ['.zip', '.tar.gz']:
                    archive_path = backup_path.parent / f"{metadata.backup_id}{ext}"
                    if archive_path.exists():
                        backup_path = archive_path
                        break
                else:
                    logging.error(f"备份路径不存在: {backup_path}")
                    return False
            
            # 验证文件数量和大小
            verified_count = 0
            total_count = len(metadata.items)
            
            for item in metadata.items:
                if self._verify_backup_item(item, backup_path, metadata.backup_id):
                    verified_count += 1
            
            success_rate = verified_count / total_count if total_count > 0 else 0
            
            logging.info(f"验证完成: {verified_count}/{total_count} ({success_rate:.1%})")
            
            return success_rate >= 0.95  # 95%以上验证成功才算通过
        
        except Exception as e:
            logging.error(f"验证备份失败: {e}")
            return False
    
    def _verify_backup_item(self, item: BackupItem, backup_path: Path, backup_id: str) -> bool:
        """验证单个备份项"""
        try:
            # 如果是压缩文件，需要解压验证
            if backup_path.suffix in ['.zip', '.tar.gz']:
                return self._verify_compressed_item(item, backup_path)
            
            # 直接验证文件
            item_path = backup_path / item.path
            if not item_path.exists():
                return False
            
            # 验证大小
            if item_path.stat().st_size != item.size:
                return False
            
            # 验证校验和（如果有）
            if item.checksum:
                current_checksum = self._calculate_file_checksum(item_path)
                if current_checksum != item.checksum:
                    return False
            
            return True
        
        except Exception:
            return False
    
    def _verify_compressed_item(self, item: BackupItem, archive_path: Path) -> bool:
        """验证压缩文件中的项"""
        try:
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    info = zipf.getinfo(item.path)
                    return info.file_size == item.size
            elif archive_path.suffix == '.gz':
                with tarfile.open(archive_path, 'r:gz') as tar:
                    member = tar.getmember(f"{archive_path.stem}/{item.path}")
                    return member.size == item.size
        
        except Exception:
            return False
        
        return False
    
    def _get_current_commit_hash(self) -> str:
        """获取当前Git提交哈希"""
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
    
    def _get_current_branch(self) -> str:
        """获取当前Git分支"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception:
            return ''
    
    def create_restore_point(self, description: str = '', backup_id: str = None) -> str:
        """创建恢复点"""
        restore_id = f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logging.info(f"创建恢复点: {restore_id}")
        
        # 如果没有指定备份ID，创建一个新备份
        if not backup_id:
            backup_id = self.create_backup(
                backup_type='restore_point',
                description=f"恢复点备份: {description}",
                tags=['restore_point']
            )
        
        # 收集Git状态
        git_state = {}
        if self.is_git_repo:
            git_state = {
                'commit_hash': self._get_current_commit_hash(),
                'branch': self._get_current_branch(),
                'status': self._get_git_status(),
                'remotes': self._get_git_remotes()
            }
        
        # 收集文件状态
        file_state = {
            'root_path': str(self.root_path),
            'total_files': len(list(self.root_path.rglob('*'))),
            'total_size': sum(f.stat().st_size for f in self.root_path.rglob('*') if f.is_file())
        }
        
        # 生成回滚脚本
        rollback_script = self._generate_rollback_script(backup_id, git_state)
        
        # 创建恢复点
        restore_point = RestorePoint(
            restore_id=restore_id,
            backup_id=backup_id,
            creation_time=datetime.now().isoformat(),
            description=description,
            git_state=git_state,
            file_state=file_state,
            dependencies=[],
            rollback_script=rollback_script
        )
        
        # 保存恢复点
        self.restore_points[restore_id] = restore_point
        self._save_restore_points()
        
        logging.info(f"恢复点创建完成: {restore_id}")
        return restore_id
    
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
    
    def _get_git_remotes(self) -> List[str]:
        """获取Git远程仓库"""
        try:
            result = subprocess.run(
                ['git', 'remote', '-v'],
                cwd=self.root_path,
                capture_output=True,
                text=True
            )
            return result.stdout.strip().split('\n')
        except Exception:
            return []
    
    def _generate_rollback_script(self, backup_id: str, git_state: Dict[str, Any]) -> str:
        """生成回滚脚本"""
        script_lines = [
            "#!/bin/bash",
            "# 自动生成的回滚脚本",
            f"# 备份ID: {backup_id}",
            f"# 创建时间: {datetime.now().isoformat()}",
            "",
            "set -e",
            "",
            "echo '开始回滚操作...'",
            "",
            "# 恢复文件",
            f"python backup_manager.py --restore {backup_id}",
            ""
        ]
        
        # 添加Git回滚命令
        if git_state and git_state.get('commit_hash'):
            script_lines.extend([
                "# 恢复Git状态",
                f"git checkout {git_state['branch']}",
                f"git reset --hard {git_state['commit_hash']}",
                ""
            ])
        
        script_lines.extend([
            "echo '回滚完成'",
            "echo '请验证系统状态'"
        ])
        
        return '\n'.join(script_lines)
    
    def restore_from_backup(self, backup_id: str, target_path: str = None) -> bool:
        """从备份恢复"""
        if backup_id not in self.backups:
            logging.error(f"备份不存在: {backup_id}")
            return False
        
        metadata = self.backups[backup_id]
        target_path = Path(target_path) if target_path else self.root_path
        
        logging.info(f"开始恢复备份: {backup_id} -> {target_path}")
        
        try:
            backup_path = Path(metadata.backup_path)
            
            # 检查备份是否存在
            if not backup_path.exists():
                # 检查压缩文件
                for ext in ['.zip', '.tar.gz']:
                    archive_path = backup_path.parent / f"{backup_id}{ext}"
                    if archive_path.exists():
                        # 解压缩
                        self._extract_backup(archive_path, backup_path)
                        break
                else:
                    logging.error(f"备份文件不存在: {backup_path}")
                    return False
            
            # 恢复文件
            restored_count = 0
            for item in metadata.items:
                if self._restore_backup_item(item, backup_path, target_path):
                    restored_count += 1
            
            success_rate = restored_count / len(metadata.items) if metadata.items else 0
            
            logging.info(f"恢复完成: {restored_count}/{len(metadata.items)} ({success_rate:.1%})")
            
            return success_rate >= 0.95
        
        except Exception as e:
            logging.error(f"恢复备份失败: {e}")
            return False
    
    def _extract_backup(self, archive_path: Path, extract_path: Path):
        """解压备份文件"""
        extract_path.mkdir(parents=True, exist_ok=True)
        
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(extract_path)
        elif archive_path.suffix == '.gz':
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_path.parent)
    
    def _restore_backup_item(self, item: BackupItem, backup_path: Path, target_path: Path) -> bool:
        """恢复单个备份项"""
        try:
            source_file = backup_path / item.path
            target_file = target_path / item.path
            
            # 创建目标目录
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 复制文件
            shutil.copy2(source_file, target_file)
            
            return True
        
        except Exception as e:
            logging.error(f"恢复文件失败 {item.path}: {e}")
            return False
    
    def rollback_to_restore_point(self, restore_id: str) -> bool:
        """回滚到恢复点"""
        if restore_id not in self.restore_points:
            logging.error(f"恢复点不存在: {restore_id}")
            return False
        
        restore_point = self.restore_points[restore_id]
        
        logging.info(f"回滚到恢复点: {restore_id}")
        logging.info(f"描述: {restore_point.description}")
        
        try:
            # 恢复文件
            if not self.restore_from_backup(restore_point.backup_id):
                logging.error("文件恢复失败")
                return False
            
            # 恢复Git状态
            if self.is_git_repo and restore_point.git_state:
                self._restore_git_state(restore_point.git_state)
            
            logging.info("回滚完成")
            return True
        
        except Exception as e:
            logging.error(f"回滚失败: {e}")
            return False
    
    def _restore_git_state(self, git_state: Dict[str, Any]):
        """恢复Git状态"""
        try:
            commit_hash = git_state.get('commit_hash')
            branch = git_state.get('branch')
            
            if branch:
                # 切换分支
                subprocess.run(
                    ['git', 'checkout', branch],
                    cwd=self.root_path,
                    check=True
                )
            
            if commit_hash:
                # 重置到指定提交
                subprocess.run(
                    ['git', 'reset', '--hard', commit_hash],
                    cwd=self.root_path,
                    check=True
                )
            
            logging.info(f"Git状态已恢复: {branch}@{commit_hash[:8]}")
        
        except Exception as e:
            logging.error(f"恢复Git状态失败: {e}")
    
    def _cleanup_old_backups(self):
        """清理过期备份"""
        cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
        
        # 按创建时间排序
        sorted_backups = sorted(
            self.backups.items(),
            key=lambda x: x[1].creation_time,
            reverse=True
        )
        
        # 保留最新的备份
        to_keep = sorted_backups[:self.config['max_backups']]
        to_remove = []
        
        for backup_id, metadata in sorted_backups[self.config['max_backups']:]:
            creation_time = datetime.fromisoformat(metadata.creation_time)
            if creation_time < cutoff_date:
                to_remove.append(backup_id)
        
        # 删除过期备份
        for backup_id in to_remove:
            self._remove_backup(backup_id)
        
        if to_remove:
            logging.info(f"清理了 {len(to_remove)} 个过期备份")
    
    def _remove_backup(self, backup_id: str):
        """删除备份"""
        if backup_id not in self.backups:
            return
        
        metadata = self.backups[backup_id]
        
        try:
            # 删除备份文件
            backup_path = Path(metadata.backup_path)
            if backup_path.exists():
                if backup_path.is_dir():
                    shutil.rmtree(backup_path)
                else:
                    backup_path.unlink()
            
            # 检查并删除压缩文件
            for ext in ['.zip', '.tar.gz']:
                archive_path = backup_path.parent / f"{backup_id}{ext}"
                if archive_path.exists():
                    archive_path.unlink()
            
            # 从元数据中删除
            del self.backups[backup_id]
            
            logging.info(f"已删除备份: {backup_id}")
        
        except Exception as e:
            logging.error(f"删除备份失败 {backup_id}: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        backups = []
        
        for backup_id, metadata in sorted(
            self.backups.items(),
            key=lambda x: x[1].creation_time,
            reverse=True
        ):
            backups.append({
                'backup_id': backup_id,
                'backup_type': metadata.backup_type,
                'creation_time': metadata.creation_time,
                'total_size_mb': metadata.total_size / 1024 / 1024,
                'total_files': metadata.total_files,
                'compression_ratio': metadata.compression_ratio,
                'verification_status': metadata.verification_status,
                'tags': metadata.tags
            })
        
        return backups
    
    def list_restore_points(self) -> List[Dict[str, Any]]:
        """列出所有恢复点"""
        points = []
        
        for restore_id, point in sorted(
            self.restore_points.items(),
            key=lambda x: x[1].creation_time,
            reverse=True
        ):
            points.append({
                'restore_id': restore_id,
                'backup_id': point.backup_id,
                'creation_time': point.creation_time,
                'description': point.description,
                'git_commit': point.git_state.get('commit_hash', '')[:8] if point.git_state else '',
                'git_branch': point.git_state.get('branch', '') if point.git_state else ''
            })
        
        return points
    
    def generate_backup_report(self) -> str:
        """生成备份报告"""
        total_backups = len(self.backups)
        total_size = sum(metadata.total_size for metadata in self.backups.values())
        total_files = sum(metadata.total_files for metadata in self.backups.values())
        
        # 按类型统计
        type_stats = {}
        for metadata in self.backups.values():
            backup_type = metadata.backup_type
            if backup_type not in type_stats:
                type_stats[backup_type] = {'count': 0, 'size': 0}
            type_stats[backup_type]['count'] += 1
            type_stats[backup_type]['size'] += metadata.total_size
        
        # 验证状态统计
        verification_stats = {}
        for metadata in self.backups.values():
            status = metadata.verification_status
            verification_stats[status] = verification_stats.get(status, 0) + 1
        
        report = f"""
# 备份管理报告

## 总体统计
- **备份总数**: {total_backups}
- **总大小**: {total_size / 1024 / 1024 / 1024:.2f} GB
- **总文件数**: {total_files:,}
- **恢复点数**: {len(self.restore_points)}

## 备份类型分布
"""
        
        for backup_type, stats in type_stats.items():
            report += f"- **{backup_type}**: {stats['count']} 个 ({stats['size'] / 1024 / 1024:.2f} MB)\n"
        
        report += "\n## 验证状态\n"
        for status, count in verification_stats.items():
            report += f"- **{status}**: {count} 个\n"
        
        # 最近的备份
        recent_backups = sorted(
            self.backups.items(),
            key=lambda x: x[1].creation_time,
            reverse=True
        )[:5]
        
        if recent_backups:
            report += "\n## 最近的备份\n\n"
            for backup_id, metadata in recent_backups:
                report += f"- **{backup_id}** ({metadata.backup_type})\n"
                report += f"  - 时间: {metadata.creation_time}\n"
                report += f"  - 大小: {metadata.total_size / 1024 / 1024:.2f} MB\n"
                report += f"  - 文件: {metadata.total_files} 个\n"
                report += f"  - 状态: {metadata.verification_status}\n\n"
        
        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新能源编程俱乐部备份和回滚管理器")
    parser.add_argument('--root', '-r', default='.', help='项目根目录路径')
    parser.add_argument('--backup-root', '-b', help='备份根目录路径')
    
    # 备份操作
    parser.add_argument('--create', '-c', action='store_true', help='创建备份')
    parser.add_argument('--type', '-t', default='full', choices=['full', 'incremental', 'differential'], help='备份类型')
    parser.add_argument('--description', '-d', default='', help='备份描述')
    parser.add_argument('--tags', nargs='*', help='备份标签')
    parser.add_argument('--paths', nargs='*', help='指定备份路径')
    
    # 恢复操作
    parser.add_argument('--restore', help='从备份恢复（指定备份ID）')
    parser.add_argument('--target', help='恢复目标路径')
    
    # 恢复点操作
    parser.add_argument('--create-restore-point', action='store_true', help='创建恢复点')
    parser.add_argument('--rollback', help='回滚到恢复点（指定恢复点ID）')
    
    # 管理操作
    parser.add_argument('--list', '-l', action='store_true', help='列出所有备份')
    parser.add_argument('--list-restore-points', action='store_true', help='列出所有恢复点')
    parser.add_argument('--verify', help='验证备份（指定备份ID）')
    parser.add_argument('--cleanup', action='store_true', help='清理过期备份')
    parser.add_argument('--report', action='store_true', help='生成备份报告')
    
    # 配置选项
    parser.add_argument('--compression', choices=['none', 'zip', 'tar.gz'], help='压缩方式')
    parser.add_argument('--parallel', action='store_true', help='并行处理')
    parser.add_argument('--workers', type=int, default=4, help='并行工作线程数')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 初始化备份管理器
        manager = BackupManager(args.root, args.backup_root)
        
        # 更新配置
        if args.compression:
            manager.config['compression'] = args.compression
        if args.parallel:
            manager.config['parallel_backup'] = True
        if args.workers:
            manager.config['max_workers'] = args.workers
        
        # 执行操作
        if args.create:
            backup_id = manager.create_backup(
                backup_type=args.type,
                description=args.description,
                tags=args.tags,
                paths=args.paths
            )
            print(f"✅ 备份创建成功: {backup_id}")
        
        elif args.restore:
            success = manager.restore_from_backup(args.restore, args.target)
            if success:
                print(f"✅ 恢复成功: {args.restore}")
            else:
                print(f"❌ 恢复失败: {args.restore}")
        
        elif args.create_restore_point:
            restore_id = manager.create_restore_point(args.description)
            print(f"✅ 恢复点创建成功: {restore_id}")
        
        elif args.rollback:
            success = manager.rollback_to_restore_point(args.rollback)
            if success:
                print(f"✅ 回滚成功: {args.rollback}")
            else:
                print(f"❌ 回滚失败: {args.rollback}")
        
        elif args.list:
            backups = manager.list_backups()
            print("\n📦 备份列表:")
            print(f"{'ID':<25} {'类型':<12} {'时间':<20} {'大小(MB)':<10} {'文件数':<8} {'状态':<10}")
            print("-" * 90)
            for backup in backups:
                print(f"{backup['backup_id']:<25} {backup['backup_type']:<12} "
                      f"{backup['creation_time'][:19]:<20} {backup['total_size_mb']:<10.2f} "
                      f"{backup['total_files']:<8} {backup['verification_status']:<10}")
        
        elif args.list_restore_points:
            points = manager.list_restore_points()
            print("\n🔄 恢复点列表:")
            print(f"{'ID':<25} {'时间':<20} {'Git分支':<15} {'Git提交':<10} {'描述':<30}")
            print("-" * 100)
            for point in points:
                print(f"{point['restore_id']:<25} {point['creation_time'][:19]:<20} "
                      f"{point['git_branch']:<15} {point['git_commit']:<10} {point['description']:<30}")
        
        elif args.verify:
            if args.verify in manager.backups:
                success = manager._verify_backup(manager.backups[args.verify])
                if success:
                    print(f"✅ 验证通过: {args.verify}")
                else:
                    print(f"❌ 验证失败: {args.verify}")
            else:
                print(f"❌ 备份不存在: {args.verify}")
        
        elif args.cleanup:
            manager._cleanup_old_backups()
            print("✅ 清理完成")
        
        elif args.report:
            report = manager.generate_backup_report()
            print(report)
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        logging.error(f"操作失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()