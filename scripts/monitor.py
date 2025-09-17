#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化监控脚本
监控项目健康状态、性能指标、资源使用情况等
"""

import os
import sys
import json
import yaml
import time
import psutil
import requests
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
import queue
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from dataclasses import dataclass, asdict
import sqlite3
import schedule

@dataclass
class MetricData:
    """指标数据结构"""
    timestamp: str
    metric_type: str
    name: str
    value: float
    unit: str
    tags: Dict[str, str] = None
    threshold: float = None
    status: str = "normal"  # normal, warning, critical

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    tags TEXT,
                    threshold REAL,
                    status TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metric_name TEXT,
                    metric_value REAL,
                    threshold REAL,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON metrics(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp 
                ON alerts(timestamp)
            """)
    
    def save_metric(self, metric: MetricData):
        """保存指标数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO metrics 
                (timestamp, metric_type, name, value, unit, tags, threshold, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.timestamp,
                metric.metric_type,
                metric.name,
                metric.value,
                metric.unit,
                json.dumps(metric.tags) if metric.tags else None,
                metric.threshold,
                metric.status
            ))
    
    def save_alert(self, alert_type: str, severity: str, message: str, 
                   metric_name: str = None, metric_value: float = None, 
                   threshold: float = None):
        """保存告警信息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO alerts 
                (timestamp, alert_type, severity, message, metric_name, metric_value, threshold)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                alert_type,
                severity,
                message,
                metric_name,
                metric_value,
                threshold
            ))
    
    def get_metrics(self, metric_type: str = None, hours: int = 24) -> List[Dict]:
        """获取指标数据"""
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if metric_type:
                cursor = conn.execute("""
                    SELECT * FROM metrics 
                    WHERE metric_type = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                """, (metric_type, since))
            else:
                cursor = conn.execute("""
                    SELECT * FROM metrics 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (since,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_alerts(self, resolved: bool = False, hours: int = 24) -> List[Dict]:
        """获取告警信息"""
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM alerts 
                WHERE resolved = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (resolved, since))
            
            return [dict(row) for row in cursor.fetchall()]

class NotificationManager:
    """通知管理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.email_config = config.get("email", {})
        self.slack_config = config.get("slack", {})
        self.webhook_config = config.get("webhook", {})
    
    def send_alert(self, alert_type: str, severity: str, message: str, 
                   metric_data: MetricData = None):
        """发送告警通知"""
        notification_methods = self.config.get("methods", ["console"])
        
        for method in notification_methods:
            try:
                if method == "email":
                    self._send_email(alert_type, severity, message, metric_data)
                elif method == "slack":
                    self._send_slack(alert_type, severity, message, metric_data)
                elif method == "webhook":
                    self._send_webhook(alert_type, severity, message, metric_data)
                elif method == "console":
                    self._send_console(alert_type, severity, message, metric_data)
            except Exception as e:
                logging.error(f"发送 {method} 通知失败: {e}")
    
    def _send_email(self, alert_type: str, severity: str, message: str, 
                    metric_data: MetricData = None):
        """发送邮件通知"""
        if not self.email_config.get("enabled", False):
            return
        
        smtp_server = self.email_config.get("smtp_server")
        smtp_port = self.email_config.get("smtp_port", 587)
        username = self.email_config.get("username")
        password = self.email_config.get("password")
        recipients = self.email_config.get("recipients", [])
        
        if not all([smtp_server, username, password, recipients]):
            logging.warning("邮件配置不完整")
            return
        
        # 创建邮件内容
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"[{severity.upper()}] {alert_type} - 监控告警"
        
        body = f"""
        告警类型: {alert_type}
        严重程度: {severity}
        消息: {message}
        时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        if metric_data:
            body += f"""
        
        指标详情:
        - 名称: {metric_data.name}
        - 当前值: {metric_data.value} {metric_data.unit}
        - 阈值: {metric_data.threshold} {metric_data.unit}
        - 状态: {metric_data.status}
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 发送邮件
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
    
    def _send_slack(self, alert_type: str, severity: str, message: str, 
                    metric_data: MetricData = None):
        """发送Slack通知"""
        if not self.slack_config.get("enabled", False):
            return
        
        webhook_url = self.slack_config.get("webhook_url")
        if not webhook_url:
            logging.warning("Slack webhook URL未配置")
            return
        
        # 设置颜色
        color_map = {
            "critical": "danger",
            "warning": "warning",
            "info": "good"
        }
        color = color_map.get(severity, "good")
        
        # 创建Slack消息
        payload = {
            "attachments": [{
                "color": color,
                "title": f"{alert_type} - {severity.upper()}",
                "text": message,
                "fields": [
                    {
                        "title": "时间",
                        "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "short": True
                    }
                ],
                "footer": "项目监控系统",
                "ts": int(time.time())
            }]
        }
        
        if metric_data:
            payload["attachments"][0]["fields"].extend([
                {
                    "title": "指标名称",
                    "value": metric_data.name,
                    "short": True
                },
                {
                    "title": "当前值",
                    "value": f"{metric_data.value} {metric_data.unit}",
                    "short": True
                },
                {
                    "title": "阈值",
                    "value": f"{metric_data.threshold} {metric_data.unit}",
                    "short": True
                }
            ])
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    
    def _send_webhook(self, alert_type: str, severity: str, message: str, 
                      metric_data: MetricData = None):
        """发送Webhook通知"""
        if not self.webhook_config.get("enabled", False):
            return
        
        webhook_url = self.webhook_config.get("url")
        if not webhook_url:
            logging.warning("Webhook URL未配置")
            return
        
        payload = {
            "alert_type": alert_type,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metric_data": asdict(metric_data) if metric_data else None
        }
        
        headers = self.webhook_config.get("headers", {})
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    
    def _send_console(self, alert_type: str, severity: str, message: str, 
                      metric_data: MetricData = None):
        """控制台输出"""
        severity_icons = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        icon = severity_icons.get(severity, "📊")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{icon} [{timestamp}] {severity.upper()} - {alert_type}: {message}")
        
        if metric_data:
            print(f"   指标: {metric_data.name} = {metric_data.value} {metric_data.unit} (阈值: {metric_data.threshold})")

class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.thresholds = config.get("thresholds", {})
    
    def collect_metrics(self) -> List[MetricData]:
        """收集系统指标"""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_threshold = self.thresholds.get("cpu_percent", 80)
        cpu_status = self._get_status(cpu_percent, cpu_threshold)
        
        metrics.append(MetricData(
            timestamp=timestamp,
            metric_type="system",
            name="cpu_percent",
            value=cpu_percent,
            unit="%",
            threshold=cpu_threshold,
            status=cpu_status,
            tags={"host": os.uname().nodename}
        ))
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_threshold = self.thresholds.get("memory_percent", 85)
        memory_status = self._get_status(memory.percent, memory_threshold)
        
        metrics.append(MetricData(
            timestamp=timestamp,
            metric_type="system",
            name="memory_percent",
            value=memory.percent,
            unit="%",
            threshold=memory_threshold,
            status=memory_status,
            tags={"host": os.uname().nodename}
        ))
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        disk_threshold = self.thresholds.get("disk_percent", 90)
        disk_status = self._get_status(disk.percent, disk_threshold)
        
        metrics.append(MetricData(
            timestamp=timestamp,
            metric_type="system",
            name="disk_percent",
            value=disk.percent,
            unit="%",
            threshold=disk_threshold,
            status=disk_status,
            tags={"host": os.uname().nodename, "mount": "/"}
        ))
        
        # 网络IO
        network = psutil.net_io_counters()
        metrics.extend([
            MetricData(
                timestamp=timestamp,
                metric_type="system",
                name="network_bytes_sent",
                value=network.bytes_sent,
                unit="bytes",
                tags={"host": os.uname().nodename}
            ),
            MetricData(
                timestamp=timestamp,
                metric_type="system",
                name="network_bytes_recv",
                value=network.bytes_recv,
                unit="bytes",
                tags={"host": os.uname().nodename}
            )
        ])
        
        # 负载平均值 (仅Linux)
        try:
            load_avg = os.getloadavg()
            load_threshold = self.thresholds.get("load_avg_1m", psutil.cpu_count())
            load_status = self._get_status(load_avg[0], load_threshold)
            
            metrics.append(MetricData(
                timestamp=timestamp,
                metric_type="system",
                name="load_avg_1m",
                value=load_avg[0],
                unit="",
                threshold=load_threshold,
                status=load_status,
                tags={"host": os.uname().nodename}
            ))
        except (OSError, AttributeError):
            # Windows系统不支持getloadavg
            pass
        
        return metrics
    
    def _get_status(self, value: float, threshold: float) -> str:
        """根据阈值判断状态"""
        if value >= threshold * 0.95:  # 95%阈值为critical
            return "critical"
        elif value >= threshold * 0.8:  # 80%阈值为warning
            return "warning"
        else:
            return "normal"

class ApplicationMonitor:
    """应用监控器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.endpoints = config.get("endpoints", [])
        self.processes = config.get("processes", [])
        self.thresholds = config.get("thresholds", {})
    
    def collect_metrics(self) -> List[MetricData]:
        """收集应用指标"""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        # 监控HTTP端点
        for endpoint in self.endpoints:
            url = endpoint.get("url")
            name = endpoint.get("name", url)
            timeout = endpoint.get("timeout", 10)
            expected_status = endpoint.get("expected_status", 200)
            
            try:
                start_time = time.time()
                response = requests.get(url, timeout=timeout)
                response_time = (time.time() - start_time) * 1000  # ms
                
                # 响应时间指标
                response_time_threshold = self.thresholds.get("response_time_ms", 5000)
                response_time_status = self._get_status(response_time, response_time_threshold)
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_type="application",
                    name=f"{name}_response_time",
                    value=response_time,
                    unit="ms",
                    threshold=response_time_threshold,
                    status=response_time_status,
                    tags={"url": url, "endpoint": name}
                ))
                
                # 状态码指标
                status_code_status = "normal" if response.status_code == expected_status else "critical"
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_type="application",
                    name=f"{name}_status_code",
                    value=response.status_code,
                    unit="",
                    threshold=expected_status,
                    status=status_code_status,
                    tags={"url": url, "endpoint": name}
                ))
                
                # 可用性指标
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_type="application",
                    name=f"{name}_availability",
                    value=1.0,
                    unit="",
                    status="normal",
                    tags={"url": url, "endpoint": name}
                ))
                
            except Exception as e:
                # 服务不可用
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_type="application",
                    name=f"{name}_availability",
                    value=0.0,
                    unit="",
                    status="critical",
                    tags={"url": url, "endpoint": name, "error": str(e)}
                ))
        
        # 监控进程
        for process_config in self.processes:
            process_name = process_config.get("name")
            process_pattern = process_config.get("pattern")
            
            try:
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if process_pattern:
                        if any(process_pattern in cmd for cmd in proc.info['cmdline'] or []):
                            processes.append(proc)
                    elif proc.info['name'] == process_name:
                        processes.append(proc)
                
                # 进程数量
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_type="application",
                    name=f"{process_name}_process_count",
                    value=len(processes),
                    unit="",
                    status="normal" if processes else "critical",
                    tags={"process": process_name}
                ))
                
                # 进程资源使用
                for proc in processes[:5]:  # 最多监控5个进程
                    try:
                        proc_info = proc.as_dict(['pid', 'cpu_percent', 'memory_percent'])
                        
                        metrics.extend([
                            MetricData(
                                timestamp=timestamp,
                                metric_type="application",
                                name=f"{process_name}_cpu_percent",
                                value=proc_info['cpu_percent'],
                                unit="%",
                                tags={"process": process_name, "pid": str(proc_info['pid'])}
                            ),
                            MetricData(
                                timestamp=timestamp,
                                metric_type="application",
                                name=f"{process_name}_memory_percent",
                                value=proc_info['memory_percent'],
                                unit="%",
                                tags={"process": process_name, "pid": str(proc_info['pid'])}
                            )
                        ])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
            except Exception as e:
                logging.error(f"监控进程 {process_name} 失败: {e}")
        
        return metrics
    
    def _get_status(self, value: float, threshold: float) -> str:
        """根据阈值判断状态"""
        if value >= threshold:
            return "critical"
        elif value >= threshold * 0.8:
            return "warning"
        else:
            return "normal"

class LogMonitor:
    """日志监控器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.log_files = config.get("log_files", [])
        self.patterns = config.get("patterns", {})
        self.file_positions = {}  # 记录文件读取位置
    
    def collect_metrics(self) -> List[MetricData]:
        """收集日志指标"""
        metrics = []
        timestamp = datetime.now().isoformat()
        
        for log_config in self.log_files:
            log_file = log_config.get("path")
            log_name = log_config.get("name", Path(log_file).name)
            
            if not Path(log_file).exists():
                continue
            
            try:
                # 读取新增的日志内容
                new_lines = self._read_new_lines(log_file)
                
                # 分析日志模式
                error_count = 0
                warning_count = 0
                
                error_patterns = self.patterns.get("error", ["ERROR", "FATAL"])
                warning_patterns = self.patterns.get("warning", ["WARN", "WARNING"])
                
                for line in new_lines:
                    if any(pattern in line.upper() for pattern in error_patterns):
                        error_count += 1
                    elif any(pattern in line.upper() for pattern in warning_patterns):
                        warning_count += 1
                
                # 错误数量指标
                error_threshold = self.config.get("thresholds", {}).get("error_count", 10)
                error_status = "critical" if error_count >= error_threshold else "normal"
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_type="logs",
                    name=f"{log_name}_error_count",
                    value=error_count,
                    unit="",
                    threshold=error_threshold,
                    status=error_status,
                    tags={"log_file": log_file, "log_name": log_name}
                ))
                
                # 警告数量指标
                warning_threshold = self.config.get("thresholds", {}).get("warning_count", 50)
                warning_status = "warning" if warning_count >= warning_threshold else "normal"
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_type="logs",
                    name=f"{log_name}_warning_count",
                    value=warning_count,
                    unit="",
                    threshold=warning_threshold,
                    status=warning_status,
                    tags={"log_file": log_file, "log_name": log_name}
                ))
                
                # 日志文件大小
                file_size = Path(log_file).stat().st_size / (1024 * 1024)  # MB
                size_threshold = self.config.get("thresholds", {}).get("file_size_mb", 100)
                size_status = "warning" if file_size >= size_threshold else "normal"
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_type="logs",
                    name=f"{log_name}_file_size",
                    value=file_size,
                    unit="MB",
                    threshold=size_threshold,
                    status=size_status,
                    tags={"log_file": log_file, "log_name": log_name}
                ))
                
            except Exception as e:
                logging.error(f"监控日志文件 {log_file} 失败: {e}")
        
        return metrics
    
    def _read_new_lines(self, log_file: str) -> List[str]:
        """读取日志文件的新增行"""
        try:
            current_size = Path(log_file).stat().st_size
            last_position = self.file_positions.get(log_file, 0)
            
            if current_size < last_position:
                # 文件被轮转，重新开始读取
                last_position = 0
            
            new_lines = []
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                self.file_positions[log_file] = f.tell()
            
            return [line.strip() for line in new_lines if line.strip()]
            
        except Exception as e:
            logging.error(f"读取日志文件 {log_file} 失败: {e}")
            return []

class MonitoringSystem:
    """监控系统主类"""
    
    def __init__(self, config_path: str = None):
        self.root_path = Path(".").resolve()
        self.config_path = config_path or self.root_path / "config" / "monitor.yaml"
        self.config = self._load_config()
        
        # 初始化组件
        self.db_manager = DatabaseManager(self.config.get("database", {}).get("path", "monitor.db"))
        self.notification_manager = NotificationManager(self.config.get("notifications", {}))
        
        # 初始化监控器
        self.system_monitor = SystemMonitor(self.config.get("system", {}))
        self.app_monitor = ApplicationMonitor(self.config.get("application", {}))
        self.log_monitor = LogMonitor(self.config.get("logs", {}))
        
        # 监控状态
        self.running = False
        self.metrics_queue = queue.Queue()
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitor.log'),
                logging.StreamHandler()
            ]
        )
    
    def _load_config(self) -> Dict:
        """加载监控配置"""
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
        """创建默认监控配置"""
        default_config = {
            "project": {
                "name": "new-energy-coder-club",
                "version": "1.0.0"
            },
            "database": {
                "path": "monitor.db",
                "retention_days": 30
            },
            "collection": {
                "interval_seconds": 60,
                "enabled_monitors": ["system", "application", "logs"]
            },
            "system": {
                "thresholds": {
                    "cpu_percent": 80,
                    "memory_percent": 85,
                    "disk_percent": 90,
                    "load_avg_1m": 4
                }
            },
            "application": {
                "endpoints": [
                    {
                        "name": "main_site",
                        "url": "http://localhost:3000",
                        "timeout": 10,
                        "expected_status": 200
                    },
                    {
                        "name": "api_health",
                        "url": "http://localhost:3001/api/health",
                        "timeout": 5,
                        "expected_status": 200
                    }
                ],
                "processes": [
                    {
                        "name": "node_app",
                        "pattern": "node"
                    },
                    {
                        "name": "nginx",
                        "pattern": "nginx"
                    }
                ],
                "thresholds": {
                    "response_time_ms": 5000
                }
            },
            "logs": {
                "log_files": [
                    {
                        "name": "app_log",
                        "path": "logs/app.log"
                    },
                    {
                        "name": "error_log",
                        "path": "logs/error.log"
                    }
                ],
                "patterns": {
                    "error": ["ERROR", "FATAL", "EXCEPTION"],
                    "warning": ["WARN", "WARNING"]
                },
                "thresholds": {
                    "error_count": 10,
                    "warning_count": 50,
                    "file_size_mb": 100
                }
            },
            "notifications": {
                "methods": ["console"],
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "${EMAIL_USERNAME}",
                    "password": "${EMAIL_PASSWORD}",
                    "recipients": ["admin@example.com"]
                },
                "slack": {
                    "enabled": False,
                    "webhook_url": "${SLACK_WEBHOOK_URL}"
                },
                "webhook": {
                    "enabled": False,
                    "url": "${WEBHOOK_URL}",
                    "headers": {
                        "Authorization": "Bearer ${WEBHOOK_TOKEN}"
                    }
                }
            },
            "alerting": {
                "enabled": True,
                "rules": [
                    {
                        "name": "high_cpu_usage",
                        "condition": "cpu_percent > 90",
                        "severity": "critical",
                        "duration_minutes": 5
                    },
                    {
                        "name": "high_memory_usage",
                        "condition": "memory_percent > 95",
                        "severity": "critical",
                        "duration_minutes": 3
                    },
                    {
                        "name": "service_down",
                        "condition": "availability == 0",
                        "severity": "critical",
                        "duration_minutes": 1
                    },
                    {
                        "name": "slow_response",
                        "condition": "response_time > 10000",
                        "severity": "warning",
                        "duration_minutes": 5
                    }
                ]
            },
            "dashboard": {
                "enabled": True,
                "port": 8080,
                "refresh_interval_seconds": 30
            }
        }
        
        # 保存默认配置
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            logging.info("默认监控配置已创建")
        except Exception as e:
            logging.error(f"配置创建失败: {e}")
        
        return default_config
    
    def collect_all_metrics(self) -> List[MetricData]:
        """收集所有监控指标"""
        all_metrics = []
        enabled_monitors = self.config.get("collection", {}).get("enabled_monitors", [])
        
        try:
            if "system" in enabled_monitors:
                all_metrics.extend(self.system_monitor.collect_metrics())
            
            if "application" in enabled_monitors:
                all_metrics.extend(self.app_monitor.collect_metrics())
            
            if "logs" in enabled_monitors:
                all_metrics.extend(self.log_monitor.collect_metrics())
                
        except Exception as e:
            logging.error(f"收集指标失败: {e}")
        
        return all_metrics
    
    def process_metrics(self, metrics: List[MetricData]):
        """处理指标数据"""
        for metric in metrics:
            # 保存到数据库
            self.db_manager.save_metric(metric)
            
            # 检查告警条件
            if metric.status in ["warning", "critical"]:
                self._check_alert_rules(metric)
    
    def _check_alert_rules(self, metric: MetricData):
        """检查告警规则"""
        alerting_config = self.config.get("alerting", {})
        if not alerting_config.get("enabled", True):
            return
        
        rules = alerting_config.get("rules", [])
        
        for rule in rules:
            rule_name = rule.get("name")
            condition = rule.get("condition")
            severity = rule.get("severity", "warning")
            
            try:
                # 简单的条件检查（实际应用中可以使用更复杂的规则引擎）
                if self._evaluate_condition(condition, metric):
                    message = f"告警规则 '{rule_name}' 触发: {metric.name} = {metric.value} {metric.unit}"
                    
                    # 保存告警
                    self.db_manager.save_alert(
                        alert_type=rule_name,
                        severity=severity,
                        message=message,
                        metric_name=metric.name,
                        metric_value=metric.value,
                        threshold=metric.threshold
                    )
                    
                    # 发送通知
                    self.notification_manager.send_alert(
                        alert_type=rule_name,
                        severity=severity,
                        message=message,
                        metric_data=metric
                    )
                    
            except Exception as e:
                logging.error(f"评估告警规则 {rule_name} 失败: {e}")
    
    def _evaluate_condition(self, condition: str, metric: MetricData) -> bool:
        """评估告警条件"""
        try:
            # 替换条件中的变量
            condition = condition.replace("cpu_percent", str(metric.value) if "cpu_percent" in metric.name else "0")
            condition = condition.replace("memory_percent", str(metric.value) if "memory_percent" in metric.name else "0")
            condition = condition.replace("disk_percent", str(metric.value) if "disk_percent" in metric.name else "0")
            condition = condition.replace("availability", str(metric.value) if "availability" in metric.name else "1")
            condition = condition.replace("response_time", str(metric.value) if "response_time" in metric.name else "0")
            
            # 安全地评估条件
            return eval(condition, {"__builtins__": {}})
            
        except Exception:
            return False
    
    def start_monitoring(self):
        """开始监控"""
        self.running = True
        interval = self.config.get("collection", {}).get("interval_seconds", 60)
        
        logging.info(f"开始监控，采集间隔: {interval}秒")
        
        # 启动指标收集线程
        collection_thread = threading.Thread(target=self._collection_loop, args=(interval,))
        collection_thread.daemon = True
        collection_thread.start()
        
        # 启动指标处理线程
        processing_thread = threading.Thread(target=self._processing_loop)
        processing_thread.daemon = True
        processing_thread.start()
        
        # 启动定时任务
        self._setup_scheduled_tasks()
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("收到停止信号")
            self.stop_monitoring()
    
    def _collection_loop(self, interval: int):
        """指标收集循环"""
        while self.running:
            try:
                metrics = self.collect_all_metrics()
                for metric in metrics:
                    self.metrics_queue.put(metric)
                
                time.sleep(interval)
                
            except Exception as e:
                logging.error(f"指标收集异常: {e}")
                time.sleep(interval)
    
    def _processing_loop(self):
        """指标处理循环"""
        while self.running:
            try:
                metrics_batch = []
                
                # 批量处理指标
                while not self.metrics_queue.empty() and len(metrics_batch) < 100:
                    metrics_batch.append(self.metrics_queue.get_nowait())
                
                if metrics_batch:
                    self.process_metrics(metrics_batch)
                
                time.sleep(1)
                
            except queue.Empty:
                time.sleep(1)
            except Exception as e:
                logging.error(f"指标处理异常: {e}")
                time.sleep(1)
    
    def _setup_scheduled_tasks(self):
        """设置定时任务"""
        # 每天清理过期数据
        schedule.every().day.at("02:00").do(self._cleanup_old_data)
        
        # 每小时生成健康报告
        schedule.every().hour.do(self._generate_health_report)
    
    def _cleanup_old_data(self):
        """清理过期数据"""
        try:
            retention_days = self.config.get("database", {}).get("retention_days", 30)
            cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                # 清理过期指标
                result = conn.execute(
                    "DELETE FROM metrics WHERE timestamp < ?", 
                    (cutoff_date,)
                )
                metrics_deleted = result.rowcount
                
                # 清理过期告警
                result = conn.execute(
                    "DELETE FROM alerts WHERE timestamp < ?", 
                    (cutoff_date,)
                )
                alerts_deleted = result.rowcount
                
                logging.info(f"清理过期数据: {metrics_deleted} 条指标, {alerts_deleted} 条告警")
                
        except Exception as e:
            logging.error(f"清理过期数据失败: {e}")
    
    def _generate_health_report(self):
        """生成健康报告"""
        try:
            # 获取最近1小时的指标
            metrics = self.db_manager.get_metrics(hours=1)
            alerts = self.db_manager.get_alerts(resolved=False, hours=1)
            
            # 统计健康状态
            total_metrics = len(metrics)
            critical_metrics = len([m for m in metrics if json.loads(m.get('tags', '{}') or '{}').get('status') == 'critical'])
            warning_metrics = len([m for m in metrics if json.loads(m.get('tags', '{}') or '{}').get('status') == 'warning'])
            
            health_score = max(0, 100 - (critical_metrics * 10 + warning_metrics * 5))
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "health_score": health_score,
                "total_metrics": total_metrics,
                "critical_metrics": critical_metrics,
                "warning_metrics": warning_metrics,
                "active_alerts": len(alerts)
            }
            
            logging.info(f"健康报告: 得分 {health_score}/100, {len(alerts)} 个活跃告警")
            
            # 如果健康得分过低，发送通知
            if health_score < 70:
                self.notification_manager.send_alert(
                    alert_type="health_check",
                    severity="warning" if health_score >= 50 else "critical",
                    message=f"系统健康得分过低: {health_score}/100"
                )
                
        except Exception as e:
            logging.error(f"生成健康报告失败: {e}")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        logging.info("监控已停止")
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表板数据"""
        try:
            # 获取最近24小时的数据
            metrics = self.db_manager.get_metrics(hours=24)
            alerts = self.db_manager.get_alerts(resolved=False, hours=24)
            
            # 按类型分组指标
            metrics_by_type = {}
            for metric in metrics:
                metric_type = metric['metric_type']
                if metric_type not in metrics_by_type:
                    metrics_by_type[metric_type] = []
                metrics_by_type[metric_type].append(metric)
            
            # 计算统计信息
            stats = {
                "total_metrics": len(metrics),
                "active_alerts": len(alerts),
                "metrics_by_type": {k: len(v) for k, v in metrics_by_type.items()},
                "latest_metrics": metrics[:20] if metrics else [],
                "recent_alerts": alerts[:10] if alerts else []
            }
            
            return stats
            
        except Exception as e:
            logging.error(f"获取仪表板数据失败: {e}")
            return {}

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动化监控系统")
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="后台运行"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="只运行一次收集"
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="显示仪表板数据"
    )
    
    args = parser.parse_args()
    
    # 创建监控系统
    monitor = MonitoringSystem(args.config)
    
    if args.dashboard:
        # 显示仪表板数据
        data = monitor.get_dashboard_data()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.once:
        # 只运行一次收集
        print("🔍 执行一次性监控收集")
        metrics = monitor.collect_all_metrics()
        monitor.process_metrics(metrics)
        print(f"✅ 收集完成，共 {len(metrics)} 个指标")
    else:
        # 启动持续监控
        monitor.start_monitoring()

if __name__ == "__main__":
    main()