#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化备份脚本
支持文件、数据库、配置等多种备份类型
"""

import os
import sys
import json
import yaml
import shutil
import tarfile
import zipfile
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
import logging
from dataclasses import dataclass, asdict
import threading
import queue
import time
import sqlite3
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class BackupJob:
    """备份任务数据结构"""
    id: str
    name: str
    type: str  # file, database, git, custom
    source: str
    destination: str
    schedule: str  # cron expression or interval
    retention_days: int = 30
    compression: str = "gzip"  # none, gzip, zip
    encryption: bool = False
    enabled: bool = True
    exclude_patterns: List[str] = None
    include_patterns: List[str] = None
    pre_commands: List[str] = None
    post_commands: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class BackupResult:
    """备份结果数据结构"""
    job_id: str
    job_name: str
    start_time: str
    end_time: str
    status: str  # success, failed, partial
    size_bytes: int
    file_count: int
    backup_path: str
    checksum: str
    error_message: str = None
    warnings: List[str] = None

class DatabaseBackup:
    """数据库备份器"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def backup_sqlite(self, db_path: str, backup_path: str) -> bool:
        """备份SQLite数据库"""
        try:
            # 使用SQLite的备份API
            source_conn = sqlite3.connect(db_path)
            backup_conn = sqlite3.connect(backup_path)
            
            source_conn.backup(backup_conn)
            
            source_conn.close()
            backup_conn.close()
            
            return True
            
        except Exception as e:
            logging.error(f"SQLite备份失败: {e}")
            return False
    
    def backup_mysql(self, config: Dict, backup_path: str) -> bool:
        """备份MySQL数据库"""
        try:
            host = config.get("host", "localhost")
            port = config.get("port", 3306)
            username = config.get("username")
            password = config.get("password")
            database = config.get("database")
            
            if not all([username, password, database]):
                logging.error("MySQL配置不完整")
                return False
            
            # 构建mysqldump命令
            cmd = [
                "mysqldump",
                f"--host={host}",
                f"--port={port}",
                f"--user={username}",
                f"--password={password}",
                "--single-transaction",
                "--routines",
                "--triggers",
                database
            ]
            
            # 执行备份
            with open(backup_path, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                logging.error(f"MySQL备份失败: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"MySQL备份失败: {e}")
            return False
    
    def backup_postgresql(self, config: Dict, backup_path: str) -> bool:
        """备份PostgreSQL数据库"""
        try:
            host = config.get("host", "localhost")
            port = config.get("port", 5432)
            username = config.get("username")
            password = config.get("password")
            database = config.get("database")
            
            if not all([username, database]):
                logging.error("PostgreSQL配置不完整")
                return False
            
            # 设置环境变量
            env = os.environ.copy()
            if password:
                env["PGPASSWORD"] = password
            
            # 构建pg_dump命令
            cmd = [
                "pg_dump",
                f"--host={host}",
                f"--port={port}",
                f"--username={username}",
                "--no-password",
                "--format=custom",
                "--compress=9",
                database
            ]
            
            # 执行备份
            with open(backup_path, 'wb') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, env=env)
            
            if result.returncode != 0:
                logging.error(f"PostgreSQL备份失败: {result.stderr.decode()}")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"PostgreSQL备份失败: {e}")
            return False

class FileBackup:
    """文件备份器"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def backup_directory(self, source: str, destination: str, 
                        exclude_patterns: List[str] = None,
                        include_patterns: List[str] = None,
                        compression: str = "gzip") -> tuple:
        """备份目录"""
        try:
            source_path = Path(source)
            if not source_path.exists():
                raise FileNotFoundError(f"源目录不存在: {source}")
            
            # 创建目标目录
            dest_path = Path(destination)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 收集要备份的文件
            files_to_backup = self._collect_files(
                source_path, exclude_patterns, include_patterns
            )
            
            if not files_to_backup:
                logging.warning(f"没有找到要备份的文件: {source}")
                return 0, 0
            
            # 根据压缩类型创建备份
            if compression == "gzip":
                return self._create_tar_backup(source_path, dest_path, files_to_backup)
            elif compression == "zip":
                return self._create_zip_backup(source_path, dest_path, files_to_backup)
            else:
                return self._create_copy_backup(source_path, dest_path, files_to_backup)
                
        except Exception as e:
            logging.error(f"目录备份失败: {e}")
            raise
    
    def _collect_files(self, source_path: Path, 
                      exclude_patterns: List[str] = None,
                      include_patterns: List[str] = None) -> List[Path]:
        """收集要备份的文件"""
        files = []
        exclude_patterns = exclude_patterns or []
        include_patterns = include_patterns or ["*"]
        
        for file_path in source_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(source_path)
                
                # 检查排除模式
                excluded = False
                for pattern in exclude_patterns:
                    if file_path.match(pattern) or str(relative_path).find(pattern) != -1:
                        excluded = True
                        break
                
                if excluded:
                    continue
                
                # 检查包含模式
                included = False
                for pattern in include_patterns:
                    if pattern == "*" or file_path.match(pattern) or str(relative_path).find(pattern) != -1:
                        included = True
                        break
                
                if included:
                    files.append(file_path)
        
        return files
    
    def _create_tar_backup(self, source_path: Path, dest_path: Path, 
                          files: List[Path]) -> tuple:
        """创建tar.gz备份"""
        total_size = 0
        file_count = len(files)
        
        with tarfile.open(dest_path, "w:gz") as tar:
            for file_path in files:
                try:
                    relative_path = file_path.relative_to(source_path)
                    tar.add(file_path, arcname=relative_path)
                    total_size += file_path.stat().st_size
                except Exception as e:
                    logging.warning(f"添加文件到tar失败 {file_path}: {e}")
                    file_count -= 1
        
        return total_size, file_count
    
    def _create_zip_backup(self, source_path: Path, dest_path: Path, 
                          files: List[Path]) -> tuple:
        """创建zip备份"""
        total_size = 0
        file_count = len(files)
        
        with zipfile.ZipFile(dest_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in files:
                try:
                    relative_path = file_path.relative_to(source_path)
                    zip_file.write(file_path, arcname=relative_path)
                    total_size += file_path.stat().st_size
                except Exception as e:
                    logging.warning(f"添加文件到zip失败 {file_path}: {e}")
                    file_count -= 1
        
        return total_size, file_count
    
    def _create_copy_backup(self, source_path: Path, dest_path: Path, 
                           files: List[Path]) -> tuple:
        """创建复制备份"""
        total_size = 0
        file_count = len(files)
        
        for file_path in files:
            try:
                relative_path = file_path.relative_to(source_path)
                target_path = dest_path / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(file_path, target_path)
                total_size += file_path.stat().st_size
            except Exception as e:
                logging.warning(f"复制文件失败 {file_path}: {e}")
                file_count -= 1
        
        return total_size, file_count

class GitBackup:
    """Git仓库备份器"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def backup_repository(self, repo_path: str, backup_path: str, 
                         include_lfs: bool = False) -> bool:
        """备份Git仓库"""
        try:
            repo_path = Path(repo_path)
            if not (repo_path / ".git").exists():
                raise ValueError(f"不是有效的Git仓库: {repo_path}")
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建bare clone
            cmd = ["git", "clone", "--bare", str(repo_path), str(backup_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logging.error(f"Git备份失败: {result.stderr}")
                return False
            
            # 如果启用LFS，备份LFS对象
            if include_lfs:
                self._backup_lfs_objects(repo_path, backup_path)
            
            return True
            
        except Exception as e:
            logging.error(f"Git仓库备份失败: {e}")
            return False
    
    def _backup_lfs_objects(self, repo_path: Path, backup_path: Path):
        """备份Git LFS对象"""
        try:
            lfs_dir = repo_path / ".git" / "lfs"
            if lfs_dir.exists():
                backup_lfs_dir = backup_path / "lfs"
                shutil.copytree(lfs_dir, backup_lfs_dir, dirs_exist_ok=True)
                logging.info("Git LFS对象备份完成")
        except Exception as e:
            logging.warning(f"Git LFS备份失败: {e}")

class BackupManager:
    """备份管理器"""
    
    def __init__(self, config_path: str = None):
        self.root_path = Path(".").resolve()
        self.config_path = config_path or self.root_path / "config" / "backup.yaml"
        self.config = self._load_config()
        
        # 初始化备份器
        self.file_backup = FileBackup(self.config.get("file", {}))
        self.db_backup = DatabaseBackup(self.config.get("database", {}))
        self.git_backup = GitBackup(self.config.get("git", {}))
        
        # 初始化数据库
        self.db_path = self.config.get("storage", {}).get("database", "backup.db")
        self._init_database()
        
        # 配置日志
        log_level = self.config.get("logging", {}).get("level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('backup.log'),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self) -> Dict:
        """加载备份配置"""
        if not self.config_path.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            logging.error(f"配置加载失败: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """创建默认备份配置"""
        default_config = {
            "project": {
                "name": "new-energy-coder-club",
                "version": "1.0.0"
            },
            "storage": {
                "base_path": "./backups",
                "database": "backup.db",
                "retention_days": 30,
                "max_backup_size_gb": 10
            },
            "compression": {
                "default": "gzip",
                "level": 6
            },
            "encryption": {
                "enabled": False,
                "algorithm": "AES-256",
                "key_file": "backup.key"
            },
            "notifications": {
                "enabled": True,
                "on_success": False,
                "on_failure": True,
                "email": {
                    "enabled": False,
                    "recipients": ["admin@example.com"]
                }
            },
            "jobs": [
                {
                    "id": "source_code",
                    "name": "源代码备份",
                    "type": "file",
                    "source": "./src",
                    "destination": "source_code_{timestamp}.tar.gz",
                    "schedule": "0 2 * * *",  # 每天凌晨2点
                    "retention_days": 30,
                    "compression": "gzip",
                    "enabled": True,
                    "exclude_patterns": [
                        "*.log",
                        "*.tmp",
                        "node_modules",
                        ".git",
                        "__pycache__",
                        "*.pyc",
                        ".env",
                        "dist",
                        "build"
                    ]
                },
                {
                    "id": "config_files",
                    "name": "配置文件备份",
                    "type": "file",
                    "source": "./config",
                    "destination": "config_{timestamp}.tar.gz",
                    "schedule": "0 3 * * *",  # 每天凌晨3点
                    "retention_days": 60,
                    "compression": "gzip",
                    "enabled": True
                },
                {
                    "id": "documentation",
                    "name": "文档备份",
                    "type": "file",
                    "source": "./docs_new",
                    "destination": "docs_{timestamp}.tar.gz",
                    "schedule": "0 4 * * 0",  # 每周日凌晨4点
                    "retention_days": 90,
                    "compression": "gzip",
                    "enabled": True
                },
                {
                    "id": "git_repository",
                    "name": "Git仓库备份",
                    "type": "git",
                    "source": ".",
                    "destination": "repository_{timestamp}.git",
                    "schedule": "0 1 * * *",  # 每天凌晨1点
                    "retention_days": 30,
                    "enabled": True,
                    "metadata": {
                        "include_lfs": True
                    }
                },
                {
                    "id": "database_backup",
                    "name": "数据库备份",
                    "type": "database",
                    "source": "sqlite:./data/app.db",
                    "destination": "database_{timestamp}.db",
                    "schedule": "0 */6 * * *",  # 每6小时
                    "retention_days": 14,
                    "enabled": False,
                    "metadata": {
                        "db_type": "sqlite"
                    }
                }
            ],
            "logging": {
                "level": "INFO",
                "file": "backup.log",
                "max_size_mb": 10,
                "backup_count": 5
            }
        }
        
        # 保存默认配置
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            logging.info("默认备份配置已创建")
        except Exception as e:
            logging.error(f"配置创建失败: {e}")
        
        return default_config
    
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_jobs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    schedule TEXT,
                    retention_days INTEGER DEFAULT 30,
                    compression TEXT DEFAULT 'gzip',
                    encryption BOOLEAN DEFAULT FALSE,
                    enabled BOOLEAN DEFAULT TRUE,
                    exclude_patterns TEXT,
                    include_patterns TEXT,
                    pre_commands TEXT,
                    post_commands TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    job_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT NOT NULL,
                    size_bytes INTEGER DEFAULT 0,
                    file_count INTEGER DEFAULT 0,
                    backup_path TEXT,
                    checksum TEXT,
                    error_message TEXT,
                    warnings TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES backup_jobs (id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_backup_results_job_id 
                ON backup_results(job_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_backup_results_start_time 
                ON backup_results(start_time)
            """)
    
    def load_jobs_from_config(self):
        """从配置文件加载备份任务"""
        jobs = self.config.get("jobs", [])
        
        with sqlite3.connect(self.db_path) as conn:
            for job_config in jobs:
                job = BackupJob(
                    id=job_config["id"],
                    name=job_config["name"],
                    type=job_config["type"],
                    source=job_config["source"],
                    destination=job_config["destination"],
                    schedule=job_config.get("schedule"),
                    retention_days=job_config.get("retention_days", 30),
                    compression=job_config.get("compression", "gzip"),
                    encryption=job_config.get("encryption", False),
                    enabled=job_config.get("enabled", True),
                    exclude_patterns=job_config.get("exclude_patterns"),
                    include_patterns=job_config.get("include_patterns"),
                    pre_commands=job_config.get("pre_commands"),
                    post_commands=job_config.get("post_commands"),
                    metadata=job_config.get("metadata")
                )
                
                # 插入或更新任务
                conn.execute("""
                    INSERT OR REPLACE INTO backup_jobs 
                    (id, name, type, source, destination, schedule, retention_days, 
                     compression, encryption, enabled, exclude_patterns, include_patterns,
                     pre_commands, post_commands, metadata, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job.id, job.name, job.type, job.source, job.destination,
                    job.schedule, job.retention_days, job.compression, job.encryption,
                    job.enabled, json.dumps(job.exclude_patterns),
                    json.dumps(job.include_patterns), json.dumps(job.pre_commands),
                    json.dumps(job.post_commands), json.dumps(job.metadata),
                    datetime.now().isoformat()
                ))
        
        logging.info(f"加载了 {len(jobs)} 个备份任务")
    
    def execute_job(self, job_id: str) -> BackupResult:
        """执行备份任务"""
        start_time = datetime.now()
        
        try:
            # 获取任务信息
            job = self._get_job(job_id)
            if not job:
                raise ValueError(f"备份任务不存在: {job_id}")
            
            if not job.enabled:
                raise ValueError(f"备份任务已禁用: {job_id}")
            
            logging.info(f"开始执行备份任务: {job.name}")
            
            # 执行前置命令
            if job.pre_commands:
                self._execute_commands(job.pre_commands, "前置")
            
            # 准备备份路径
            backup_path = self._prepare_backup_path(job)
            
            # 执行备份
            size_bytes, file_count = self._execute_backup(job, backup_path)
            
            # 计算校验和
            checksum = self._calculate_checksum(backup_path)
            
            # 执行后置命令
            if job.post_commands:
                self._execute_commands(job.post_commands, "后置")
            
            end_time = datetime.now()
            
            # 创建结果
            result = BackupResult(
                job_id=job.id,
                job_name=job.name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                status="success",
                size_bytes=size_bytes,
                file_count=file_count,
                backup_path=str(backup_path),
                checksum=checksum
            )
            
            # 保存结果
            self._save_result(result)
            
            duration = (end_time - start_time).total_seconds()
            logging.info(f"备份任务完成: {job.name}, 耗时: {duration:.2f}秒, 大小: {size_bytes / 1024 / 1024:.2f}MB")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            
            # 创建失败结果
            result = BackupResult(
                job_id=job_id,
                job_name=job.name if 'job' in locals() else job_id,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                status="failed",
                size_bytes=0,
                file_count=0,
                backup_path="",
                checksum="",
                error_message=str(e)
            )
            
            # 保存结果
            self._save_result(result)
            
            logging.error(f"备份任务失败: {job_id}, 错误: {e}")
            
            return result
    
    def _get_job(self, job_id: str) -> Optional[BackupJob]:
        """获取备份任务"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM backup_jobs WHERE id = ?", 
                (job_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return BackupJob(
                id=row["id"],
                name=row["name"],
                type=row["type"],
                source=row["source"],
                destination=row["destination"],
                schedule=row["schedule"],
                retention_days=row["retention_days"],
                compression=row["compression"],
                encryption=bool(row["encryption"]),
                enabled=bool(row["enabled"]),
                exclude_patterns=json.loads(row["exclude_patterns"] or "null"),
                include_patterns=json.loads(row["include_patterns"] or "null"),
                pre_commands=json.loads(row["pre_commands"] or "null"),
                post_commands=json.loads(row["post_commands"] or "null"),
                metadata=json.loads(row["metadata"] or "null")
            )
    
    def _prepare_backup_path(self, job: BackupJob) -> Path:
        """准备备份路径"""
        base_path = Path(self.config.get("storage", {}).get("base_path", "./backups"))
        base_path.mkdir(parents=True, exist_ok=True)
        
        # 替换时间戳占位符
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = job.destination.replace("{timestamp}", timestamp)
        
        return base_path / destination
    
    def _execute_backup(self, job: BackupJob, backup_path: Path) -> tuple:
        """执行具体的备份操作"""
        if job.type == "file":
            return self.file_backup.backup_directory(
                source=job.source,
                destination=str(backup_path),
                exclude_patterns=job.exclude_patterns,
                include_patterns=job.include_patterns,
                compression=job.compression
            )
        
        elif job.type == "database":
            metadata = job.metadata or {}
            db_type = metadata.get("db_type", "sqlite")
            
            if db_type == "sqlite":
                success = self.db_backup.backup_sqlite(job.source, str(backup_path))
                if success:
                    size = backup_path.stat().st_size
                    return size, 1
                else:
                    raise RuntimeError("SQLite备份失败")
            
            elif db_type == "mysql":
                success = self.db_backup.backup_mysql(metadata, str(backup_path))
                if success:
                    size = backup_path.stat().st_size
                    return size, 1
                else:
                    raise RuntimeError("MySQL备份失败")
            
            elif db_type == "postgresql":
                success = self.db_backup.backup_postgresql(metadata, str(backup_path))
                if success:
                    size = backup_path.stat().st_size
                    return size, 1
                else:
                    raise RuntimeError("PostgreSQL备份失败")
            
            else:
                raise ValueError(f"不支持的数据库类型: {db_type}")
        
        elif job.type == "git":
            metadata = job.metadata or {}
            include_lfs = metadata.get("include_lfs", False)
            
            success = self.git_backup.backup_repository(
                repo_path=job.source,
                backup_path=str(backup_path),
                include_lfs=include_lfs
            )
            
            if success:
                # 计算Git仓库大小
                total_size = sum(
                    f.stat().st_size for f in backup_path.rglob("*") if f.is_file()
                )
                file_count = len(list(backup_path.rglob("*")))
                return total_size, file_count
            else:
                raise RuntimeError("Git仓库备份失败")
        
        else:
            raise ValueError(f"不支持的备份类型: {job.type}")
    
    def _execute_commands(self, commands: List[str], command_type: str):
        """执行命令列表"""
        for cmd in commands:
            try:
                logging.info(f"执行{command_type}命令: {cmd}")
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=300
                )
                
                if result.returncode != 0:
                    logging.warning(f"{command_type}命令执行失败: {cmd}, 错误: {result.stderr}")
                else:
                    logging.info(f"{command_type}命令执行成功: {cmd}")
                    
            except subprocess.TimeoutExpired:
                logging.error(f"{command_type}命令超时: {cmd}")
            except Exception as e:
                logging.error(f"{command_type}命令执行异常: {cmd}, 错误: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        try:
            hash_md5 = hashlib.md5()
            
            if file_path.is_file():
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
            else:
                # 目录的话，计算所有文件的校验和
                for file in sorted(file_path.rglob("*")):
                    if file.is_file():
                        with open(file, "rb") as f:
                            for chunk in iter(lambda: f.read(4096), b""):
                                hash_md5.update(chunk)
            
            return hash_md5.hexdigest()
            
        except Exception as e:
            logging.warning(f"计算校验和失败: {e}")
            return ""
    
    def _save_result(self, result: BackupResult):
        """保存备份结果"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO backup_results 
                (job_id, job_name, start_time, end_time, status, size_bytes, 
                 file_count, backup_path, checksum, error_message, warnings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.job_id, result.job_name, result.start_time, result.end_time,
                result.status, result.size_bytes, result.file_count, result.backup_path,
                result.checksum, result.error_message, json.dumps(result.warnings)
            ))
    
    def execute_all_jobs(self, parallel: bool = False) -> List[BackupResult]:
        """执行所有启用的备份任务"""
        # 获取所有启用的任务
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id FROM backup_jobs WHERE enabled = 1"
            )
            job_ids = [row["id"] for row in cursor.fetchall()]
        
        if not job_ids:
            logging.info("没有启用的备份任务")
            return []
        
        results = []
        
        if parallel:
            # 并行执行
            max_workers = min(len(job_ids), 4)  # 最多4个并行任务
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_job = {
                    executor.submit(self.execute_job, job_id): job_id 
                    for job_id in job_ids
                }
                
                for future in as_completed(future_to_job):
                    job_id = future_to_job[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logging.error(f"并行执行任务 {job_id} 失败: {e}")
        else:
            # 串行执行
            for job_id in job_ids:
                result = self.execute_job(job_id)
                results.append(result)
        
        return results
    
    def cleanup_old_backups(self):
        """清理过期备份"""
        try:
            base_path = Path(self.config.get("storage", {}).get("base_path", "./backups"))
            if not base_path.exists():
                return
            
            # 获取所有任务的保留策略
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT id, retention_days FROM backup_jobs"
                )
                retention_policies = {row["id"]: row["retention_days"] for row in cursor.fetchall()}
            
            # 获取所有备份结果
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM backup_results WHERE status = 'success' ORDER BY start_time DESC"
                )
                backup_results = [dict(row) for row in cursor.fetchall()]
            
            deleted_count = 0
            freed_space = 0
            
            for result in backup_results:
                job_id = result["job_id"]
                retention_days = retention_policies.get(job_id, 30)
                
                # 检查是否过期
                backup_time = datetime.fromisoformat(result["start_time"])
                cutoff_time = datetime.now() - timedelta(days=retention_days)
                
                if backup_time < cutoff_time:
                    backup_path = Path(result["backup_path"])
                    
                    if backup_path.exists():
                        try:
                            # 计算文件大小
                            if backup_path.is_file():
                                file_size = backup_path.stat().st_size
                            else:
                                file_size = sum(
                                    f.stat().st_size for f in backup_path.rglob("*") if f.is_file()
                                )
                            
                            # 删除备份文件
                            if backup_path.is_file():
                                backup_path.unlink()
                            else:
                                shutil.rmtree(backup_path)
                            
                            deleted_count += 1
                            freed_space += file_size
                            
                            logging.info(f"删除过期备份: {backup_path}")
                            
                        except Exception as e:
                            logging.error(f"删除备份文件失败 {backup_path}: {e}")
            
            if deleted_count > 0:
                logging.info(f"清理完成: 删除 {deleted_count} 个过期备份, 释放空间 {freed_space / 1024 / 1024:.2f}MB")
            else:
                logging.info("没有需要清理的过期备份")
                
        except Exception as e:
            logging.error(f"清理过期备份失败: {e}")
    
    def get_backup_status(self) -> Dict:
        """获取备份状态"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # 统计任务数量
                cursor = conn.execute(
                    "SELECT enabled, COUNT(*) as count FROM backup_jobs GROUP BY enabled"
                )
                job_stats = {row["enabled"]: row["count"] for row in cursor.fetchall()}
                
                # 统计最近24小时的备份结果
                since = (datetime.now() - timedelta(hours=24)).isoformat()
                cursor = conn.execute(
                    "SELECT status, COUNT(*) as count FROM backup_results WHERE start_time >= ? GROUP BY status",
                    (since,)
                )
                result_stats = {row["status"]: row["count"] for row in cursor.fetchall()}
                
                # 获取最近的备份结果
                cursor = conn.execute(
                    "SELECT * FROM backup_results ORDER BY start_time DESC LIMIT 10"
                )
                recent_results = [dict(row) for row in cursor.fetchall()]
                
                # 计算总备份大小
                cursor = conn.execute(
                    "SELECT SUM(size_bytes) as total_size FROM backup_results WHERE status = 'success'"
                )
                total_size = cursor.fetchone()["total_size"] or 0
                
                return {
                    "job_stats": {
                        "total": sum(job_stats.values()),
                        "enabled": job_stats.get(1, 0),
                        "disabled": job_stats.get(0, 0)
                    },
                    "result_stats_24h": result_stats,
                    "recent_results": recent_results,
                    "total_backup_size_mb": total_size / 1024 / 1024,
                    "storage_path": str(Path(self.config.get("storage", {}).get("base_path", "./backups")).resolve())
                }
                
        except Exception as e:
            logging.error(f"获取备份状态失败: {e}")
            return {}
    
    def verify_backup(self, backup_path: str) -> bool:
        """验证备份完整性"""
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                logging.error(f"备份文件不存在: {backup_path}")
                return False
            
            # 根据文件类型进行验证
            if backup_path.suffix == ".gz":
                # 验证tar.gz文件
                with tarfile.open(backup_path, "r:gz") as tar:
                    # 尝试列出所有文件
                    members = tar.getmembers()
                    logging.info(f"备份文件包含 {len(members)} 个文件")
                    return True
                    
            elif backup_path.suffix == ".zip":
                # 验证zip文件
                with zipfile.ZipFile(backup_path, 'r') as zip_file:
                    # 测试zip文件完整性
                    bad_file = zip_file.testzip()
                    if bad_file:
                        logging.error(f"zip文件损坏: {bad_file}")
                        return False
                    
                    file_list = zip_file.namelist()
                    logging.info(f"备份文件包含 {len(file_list)} 个文件")
                    return True
                    
            else:
                # 其他文件类型，检查文件是否可读
                with open(backup_path, 'rb') as f:
                    # 读取前1KB检查文件是否可读
                    f.read(1024)
                    logging.info(f"备份文件验证通过: {backup_path}")
                    return True
                    
        except Exception as e:
            logging.error(f"备份验证失败 {backup_path}: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动化备份系统")
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    parser.add_argument(
        "--job",
        help="执行指定的备份任务ID"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="执行所有启用的备份任务"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="并行执行备份任务"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="清理过期备份"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="显示备份状态"
    )
    parser.add_argument(
        "--verify",
        help="验证指定备份文件的完整性"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化备份配置"
    )
    
    args = parser.parse_args()
    
    # 创建备份管理器
    backup_manager = BackupManager(args.config)
    
    if args.init:
        # 初始化配置
        backup_manager.load_jobs_from_config()
        print("✅ 备份配置初始化完成")
        
    elif args.status:
        # 显示备份状态
        status = backup_manager.get_backup_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
    elif args.verify:
        # 验证备份
        is_valid = backup_manager.verify_backup(args.verify)
        if is_valid:
            print(f"✅ 备份文件验证通过: {args.verify}")
        else:
            print(f"❌ 备份文件验证失败: {args.verify}")
            sys.exit(1)
            
    elif args.cleanup:
        # 清理过期备份
        print("🧹 开始清理过期备份")
        backup_manager.cleanup_old_backups()
        print("✅ 清理完成")
        
    elif args.job:
        # 执行指定任务
        print(f"🚀 执行备份任务: {args.job}")
        result = backup_manager.execute_job(args.job)
        
        if result.status == "success":
            print(f"✅ 备份成功: {result.backup_path}")
            print(f"   大小: {result.size_bytes / 1024 / 1024:.2f}MB")
            print(f"   文件数: {result.file_count}")
            print(f"   校验和: {result.checksum}")
        else:
            print(f"❌ 备份失败: {result.error_message}")
            sys.exit(1)
            
    elif args.all:
        # 执行所有任务
        print("🚀 执行所有备份任务")
        results = backup_manager.execute_all_jobs(parallel=args.parallel)
        
        success_count = len([r for r in results if r.status == "success"])
        failed_count = len([r for r in results if r.status == "failed"])
        
        print(f"✅ 备份完成: {success_count} 成功, {failed_count} 失败")
        
        if failed_count > 0:
            print("\n失败的任务:")
            for result in results:
                if result.status == "failed":
                    print(f"  - {result.job_name}: {result.error_message}")
            sys.exit(1)
    else:
        # 显示帮助
        parser.print_help()

if __name__ == "__main__":
    main()