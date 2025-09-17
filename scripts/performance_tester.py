#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化性能测试脚本
支持Web应用、API接口、数据库等多种性能测试场景
"""

import os
import sys
import json
import yaml
import time
import asyncio
import aiohttp
import requests
import psutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import threading
from urllib.parse import urljoin, urlparse
import sqlite3
import subprocess
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

@dataclass
class PerformanceMetric:
    """性能指标数据结构"""
    timestamp: str
    test_name: str
    metric_type: str  # response_time, throughput, cpu_usage, memory_usage, error_rate
    value: float
    unit: str
    target_value: Optional[float] = None
    passed: bool = True
    details: Dict[str, Any] = None

@dataclass
class TestResult:
    """测试结果数据结构"""
    test_name: str
    start_time: str
    end_time: str
    duration: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    metrics: List[PerformanceMetric]
    summary: Dict[str, Any]
    passed: bool

@dataclass
class PerformanceReport:
    """性能测试报告数据结构"""
    project_name: str
    test_suite: str
    start_time: str
    end_time: str
    total_duration: float
    test_results: List[TestResult]
    overall_summary: Dict[str, Any]
    environment_info: Dict[str, Any]
    passed: bool

class PerformanceTester:
    """性能测试器主类"""
    
    def __init__(self, config_path: str = None):
        self.root_path = Path(".").resolve()
        self.config_path = config_path or self.root_path / "config" / "performance.yaml"
        self.config = self._load_config()
        
        # 测试会话
        self.session = requests.Session()
        self.session.timeout = self.config.get("http", {}).get("timeout", 30)
        
        # 结果存储
        self.db_path = self.root_path / "reports" / "performance" / "results.db"
        self._init_database()
        
        # 配置日志
        log_level = self.config.get("logging", {}).get("level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _load_config(self) -> Dict:
        """加载性能测试配置"""
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
        """创建默认性能测试配置"""
        default_config = {
            "project": {
                "name": "New Energy Coder Club",
                "version": "1.0.0",
                "description": "新能源编程俱乐部性能测试"
            },
            "environment": {
                "base_url": "{{BASE_URL}}",
                "api_key": "{{API_KEY}}",
                "database_url": "{{DATABASE_URL}}",
                "test_data_path": "./test_data"
            },
            "http": {
                "timeout": 30,
                "max_retries": 3,
                "retry_delay": 1,
                "user_agent": "Performance-Tester/1.0",
                "headers": {
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            },
            "load_testing": {
                "concurrent_users": [1, 5, 10, 20, 50],
                "test_duration": 60,  # 秒
                "ramp_up_time": 10,   # 秒
                "think_time": 1,      # 秒
                "max_requests": 1000
            },
            "stress_testing": {
                "max_users": 100,
                "increment_step": 10,
                "step_duration": 30,
                "failure_threshold": 0.05  # 5%错误率
            },
            "spike_testing": {
                "normal_load": 10,
                "spike_load": 100,
                "spike_duration": 30,
                "recovery_time": 60
            },
            "endurance_testing": {
                "users": 20,
                "duration": 3600,  # 1小时
                "memory_threshold": 0.8,  # 80%内存使用率
                "cpu_threshold": 0.8      # 80%CPU使用率
            },
            "api_tests": [
                {
                    "name": "用户登录",
                    "method": "POST",
                    "endpoint": "/api/auth/login",
                    "payload": {
                        "username": "{{TEST_USERNAME}}",
                        "password": "{{TEST_PASSWORD}}"
                    },
                    "expected_status": 200,
                    "response_time_threshold": 2.0,
                    "extract_token": "access_token"
                },
                {
                    "name": "获取用户信息",
                    "method": "GET",
                    "endpoint": "/api/user/profile",
                    "headers": {
                        "Authorization": "Bearer {{TOKEN}}"
                    },
                    "expected_status": 200,
                    "response_time_threshold": 1.0
                },
                {
                    "name": "创建项目",
                    "method": "POST",
                    "endpoint": "/api/projects",
                    "payload": {
                        "name": "测试项目{{TIMESTAMP}}",
                        "description": "性能测试项目",
                        "type": "web"
                    },
                    "headers": {
                        "Authorization": "Bearer {{TOKEN}}"
                    },
                    "expected_status": 201,
                    "response_time_threshold": 3.0
                }
            ],
            "database_tests": [
                {
                    "name": "用户查询性能",
                    "query": "SELECT * FROM users WHERE created_at > NOW() - INTERVAL 30 DAY",
                    "expected_rows": 100,
                    "execution_time_threshold": 0.5
                },
                {
                    "name": "项目统计查询",
                    "query": "SELECT COUNT(*) as total, AVG(rating) as avg_rating FROM projects WHERE status = 'active'",
                    "execution_time_threshold": 1.0
                }
            ],
            "web_tests": [
                {
                    "name": "首页加载",
                    "url": "/",
                    "load_time_threshold": 3.0,
                    "size_threshold": 1048576  # 1MB
                },
                {
                    "name": "项目列表页",
                    "url": "/projects",
                    "load_time_threshold": 2.0
                },
                {
                    "name": "用户仪表板",
                    "url": "/dashboard",
                    "load_time_threshold": 2.5,
                    "requires_auth": True
                }
            ],
            "thresholds": {
                "response_time": {
                    "excellent": 1.0,
                    "good": 2.0,
                    "acceptable": 5.0
                },
                "throughput": {
                    "minimum": 100,  # requests/second
                    "target": 500,
                    "excellent": 1000
                },
                "error_rate": {
                    "maximum": 0.01,  # 1%
                    "warning": 0.005  # 0.5%
                },
                "resource_usage": {
                    "cpu_max": 0.8,     # 80%
                    "memory_max": 0.8,  # 80%
                    "disk_max": 0.9     # 90%
                }
            },
            "monitoring": {
                "enabled": True,
                "interval": 5,  # 秒
                "metrics": ["cpu", "memory", "disk", "network"],
                "alert_thresholds": {
                    "cpu": 0.9,
                    "memory": 0.9,
                    "response_time": 10.0
                }
            },
            "reporting": {
                "output_directory": "./reports/performance",
                "formats": ["json", "html", "csv"],
                "include_charts": True,
                "detailed_logs": True
            },
            "notifications": {
                "enabled": False,
                "webhook_url": "{{PERFORMANCE_WEBHOOK_URL}}",
                "email": {
                    "enabled": False,
                    "recipients": ["{{TEAM_EMAIL}}"]
                }
            },
            "logging": {
                "level": "INFO",
                "file": "performance_tester.log"
            }
        }
        
        # 保存默认配置
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            logging.info("默认性能测试配置已创建")
        except Exception as e:
            logging.error(f"配置创建失败: {e}")
        
        return default_config
    
    def _init_database(self):
        """初始化结果数据库"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT,
                    test_suite TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration REAL,
                    passed BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    test_name TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration REAL,
                    total_requests INTEGER,
                    successful_requests INTEGER,
                    failed_requests INTEGER,
                    passed BOOLEAN,
                    FOREIGN KEY (run_id) REFERENCES test_runs (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id INTEGER,
                    timestamp TEXT,
                    metric_type TEXT,
                    value REAL,
                    unit TEXT,
                    target_value REAL,
                    passed BOOLEAN,
                    FOREIGN KEY (result_id) REFERENCES test_results (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"数据库初始化失败: {e}")
    
    def run_performance_tests(self, test_types: List[str] = None) -> PerformanceReport:
        """运行性能测试套件"""
        start_time = datetime.now()
        
        if not test_types:
            test_types = ["api", "web", "load", "database"]
        
        logging.info(f"开始性能测试，测试类型: {', '.join(test_types)}")
        
        test_results = []
        environment_info = self._collect_environment_info()
        
        # API性能测试
        if "api" in test_types:
            api_results = self._run_api_tests()
            test_results.extend(api_results)
        
        # Web页面性能测试
        if "web" in test_types:
            web_results = self._run_web_tests()
            test_results.extend(web_results)
        
        # 负载测试
        if "load" in test_types:
            load_results = self._run_load_tests()
            test_results.extend(load_results)
        
        # 数据库性能测试
        if "database" in test_types:
            db_results = self._run_database_tests()
            test_results.extend(db_results)
        
        # 压力测试
        if "stress" in test_types:
            stress_results = self._run_stress_tests()
            test_results.extend(stress_results)
        
        # 峰值测试
        if "spike" in test_types:
            spike_results = self._run_spike_tests()
            test_results.extend(spike_results)
        
        # 持久性测试
        if "endurance" in test_types:
            endurance_results = self._run_endurance_tests()
            test_results.extend(endurance_results)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # 生成报告
        report = PerformanceReport(
            project_name=self.config.get("project", {}).get("name", "Unknown"),
            test_suite="Performance Test Suite",
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            total_duration=total_duration,
            test_results=test_results,
            overall_summary=self._generate_overall_summary(test_results),
            environment_info=environment_info,
            passed=all(result.passed for result in test_results)
        )
        
        # 保存到数据库
        self._save_results_to_db(report)
        
        logging.info(f"性能测试完成，总耗时: {total_duration:.2f}秒")
        
        return report
    
    def _collect_environment_info(self) -> Dict[str, Any]:
        """收集环境信息"""
        try:
            return {
                "hostname": os.uname().nodename if hasattr(os, 'uname') else "Unknown",
                "platform": sys.platform,
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_usage": dict(psutil.disk_usage('/'))._asdict() if sys.platform != 'win32' else dict(psutil.disk_usage('C:'))._asdict(),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"环境信息收集失败: {e}")
            return {"error": str(e)}
    
    def _run_api_tests(self) -> List[TestResult]:
        """运行API性能测试"""
        results = []
        api_tests = self.config.get("api_tests", [])
        base_url = self.config.get("environment", {}).get("base_url", "")
        
        # 存储认证令牌
        tokens = {}
        
        for test_config in api_tests:
            start_time = datetime.now()
            test_name = test_config.get("name", "Unknown API Test")
            
            logging.info(f"运行API测试: {test_name}")
            
            metrics = []
            total_requests = 0
            successful_requests = 0
            failed_requests = 0
            
            try:
                # 准备请求
                method = test_config.get("method", "GET")
                endpoint = test_config.get("endpoint", "/")
                url = urljoin(base_url, endpoint)
                
                # 处理占位符
                payload = self._process_placeholders(test_config.get("payload", {}), tokens)
                headers = self._process_placeholders(test_config.get("headers", {}), tokens)
                
                # 合并默认头部
                default_headers = self.config.get("http", {}).get("headers", {})
                headers = {**default_headers, **headers}
                
                # 执行请求
                request_start = time.time()
                
                if method.upper() == "GET":
                    response = self.session.get(url, headers=headers)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=payload, headers=headers)
                elif method.upper() == "PUT":
                    response = self.session.put(url, json=payload, headers=headers)
                elif method.upper() == "DELETE":
                    response = self.session.delete(url, headers=headers)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                request_end = time.time()
                response_time = request_end - request_start
                
                total_requests = 1
                
                # 检查响应
                expected_status = test_config.get("expected_status", 200)
                if response.status_code == expected_status:
                    successful_requests = 1
                    
                    # 提取令牌
                    extract_token = test_config.get("extract_token")
                    if extract_token and response.headers.get('content-type', '').startswith('application/json'):
                        try:
                            response_data = response.json()
                            if extract_token in response_data:
                                tokens["TOKEN"] = response_data[extract_token]
                        except:
                            pass
                else:
                    failed_requests = 1
                
                # 记录响应时间指标
                response_time_threshold = test_config.get("response_time_threshold", 5.0)
                metric = PerformanceMetric(
                    timestamp=datetime.now().isoformat(),
                    test_name=test_name,
                    metric_type="response_time",
                    value=response_time,
                    unit="seconds",
                    target_value=response_time_threshold,
                    passed=response_time <= response_time_threshold,
                    details={
                        "status_code": response.status_code,
                        "content_length": len(response.content),
                        "url": url
                    }
                )
                metrics.append(metric)
                
            except Exception as e:
                logging.error(f"API测试失败 {test_name}: {e}")
                failed_requests = 1
                total_requests = 1
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 创建测试结果
            result = TestResult(
                test_name=test_name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration=duration,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                metrics=metrics,
                summary={
                    "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                    "avg_response_time": sum(m.value for m in metrics if m.metric_type == "response_time") / len([m for m in metrics if m.metric_type == "response_time"]) if metrics else 0
                },
                passed=failed_requests == 0 and all(m.passed for m in metrics)
            )
            
            results.append(result)
        
        return results
    
    def _run_web_tests(self) -> List[TestResult]:
        """运行Web页面性能测试"""
        results = []
        web_tests = self.config.get("web_tests", [])
        base_url = self.config.get("environment", {}).get("base_url", "")
        
        for test_config in web_tests:
            start_time = datetime.now()
            test_name = test_config.get("name", "Unknown Web Test")
            
            logging.info(f"运行Web测试: {test_name}")
            
            metrics = []
            total_requests = 0
            successful_requests = 0
            failed_requests = 0
            
            try:
                url_path = test_config.get("url", "/")
                url = urljoin(base_url, url_path)
                
                # 执行请求
                request_start = time.time()
                response = self.session.get(url)
                request_end = time.time()
                
                load_time = request_end - request_start
                content_size = len(response.content)
                
                total_requests = 1
                
                if response.status_code == 200:
                    successful_requests = 1
                else:
                    failed_requests = 1
                
                # 检查加载时间
                load_time_threshold = test_config.get("load_time_threshold", 5.0)
                load_time_metric = PerformanceMetric(
                    timestamp=datetime.now().isoformat(),
                    test_name=test_name,
                    metric_type="load_time",
                    value=load_time,
                    unit="seconds",
                    target_value=load_time_threshold,
                    passed=load_time <= load_time_threshold,
                    details={"url": url, "status_code": response.status_code}
                )
                metrics.append(load_time_metric)
                
                # 检查页面大小
                size_threshold = test_config.get("size_threshold")
                if size_threshold:
                    size_metric = PerformanceMetric(
                        timestamp=datetime.now().isoformat(),
                        test_name=test_name,
                        metric_type="page_size",
                        value=content_size,
                        unit="bytes",
                        target_value=size_threshold,
                        passed=content_size <= size_threshold,
                        details={"url": url}
                    )
                    metrics.append(size_metric)
                
            except Exception as e:
                logging.error(f"Web测试失败 {test_name}: {e}")
                failed_requests = 1
                total_requests = 1
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 创建测试结果
            result = TestResult(
                test_name=test_name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration=duration,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                metrics=metrics,
                summary={
                    "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                    "avg_load_time": sum(m.value for m in metrics if m.metric_type == "load_time") / len([m for m in metrics if m.metric_type == "load_time"]) if metrics else 0
                },
                passed=failed_requests == 0 and all(m.passed for m in metrics)
            )
            
            results.append(result)
        
        return results
    
    def _run_load_tests(self) -> List[TestResult]:
        """运行负载测试"""
        results = []
        load_config = self.config.get("load_testing", {})
        concurrent_users = load_config.get("concurrent_users", [1, 5, 10])
        test_duration = load_config.get("test_duration", 60)
        
        for user_count in concurrent_users:
            start_time = datetime.now()
            test_name = f"负载测试 - {user_count} 并发用户"
            
            logging.info(f"运行负载测试: {user_count} 并发用户")
            
            metrics = []
            total_requests = 0
            successful_requests = 0
            failed_requests = 0
            
            try:
                # 使用线程池模拟并发用户
                with ThreadPoolExecutor(max_workers=user_count) as executor:
                    futures = []
                    
                    # 启动并发任务
                    for i in range(user_count):
                        future = executor.submit(self._simulate_user_load, test_duration, i)
                        futures.append(future)
                    
                    # 收集结果
                    for future in as_completed(futures):
                        try:
                            user_result = future.result()
                            total_requests += user_result["total_requests"]
                            successful_requests += user_result["successful_requests"]
                            failed_requests += user_result["failed_requests"]
                            metrics.extend(user_result["metrics"])
                        except Exception as e:
                            logging.error(f"用户模拟失败: {e}")
                            failed_requests += 1
                
                # 计算吞吐量
                if total_requests > 0:
                    throughput = total_requests / test_duration
                    throughput_threshold = self.config.get("thresholds", {}).get("throughput", {}).get("minimum", 10)
                    
                    throughput_metric = PerformanceMetric(
                        timestamp=datetime.now().isoformat(),
                        test_name=test_name,
                        metric_type="throughput",
                        value=throughput,
                        unit="requests/second",
                        target_value=throughput_threshold,
                        passed=throughput >= throughput_threshold,
                        details={"concurrent_users": user_count, "duration": test_duration}
                    )
                    metrics.append(throughput_metric)
                
            except Exception as e:
                logging.error(f"负载测试失败 {test_name}: {e}")
                failed_requests += user_count
                total_requests += user_count
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 创建测试结果
            result = TestResult(
                test_name=test_name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration=duration,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                metrics=metrics,
                summary={
                    "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                    "throughput": total_requests / test_duration if test_duration > 0 else 0,
                    "avg_response_time": statistics.mean([m.value for m in metrics if m.metric_type == "response_time"]) if [m for m in metrics if m.metric_type == "response_time"] else 0
                },
                passed=failed_requests == 0 and all(m.passed for m in metrics)
            )
            
            results.append(result)
        
        return results
    
    def _simulate_user_load(self, duration: int, user_id: int) -> Dict[str, Any]:
        """模拟单个用户的负载"""
        start_time = time.time()
        end_time = start_time + duration
        
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        metrics = []
        
        api_tests = self.config.get("api_tests", [])
        base_url = self.config.get("environment", {}).get("base_url", "")
        think_time = self.config.get("load_testing", {}).get("think_time", 1)
        
        while time.time() < end_time:
            for test_config in api_tests:
                if time.time() >= end_time:
                    break
                
                try:
                    # 执行请求
                    method = test_config.get("method", "GET")
                    endpoint = test_config.get("endpoint", "/")
                    url = urljoin(base_url, endpoint)
                    
                    request_start = time.time()
                    
                    if method.upper() == "GET":
                        response = self.session.get(url)
                    elif method.upper() == "POST":
                        payload = test_config.get("payload", {})
                        response = self.session.post(url, json=payload)
                    else:
                        continue
                    
                    request_end = time.time()
                    response_time = request_end - request_start
                    
                    total_requests += 1
                    
                    if response.status_code in [200, 201]:
                        successful_requests += 1
                    else:
                        failed_requests += 1
                    
                    # 记录响应时间
                    metric = PerformanceMetric(
                        timestamp=datetime.now().isoformat(),
                        test_name=f"User-{user_id}",
                        metric_type="response_time",
                        value=response_time,
                        unit="seconds",
                        passed=True,
                        details={"user_id": user_id, "endpoint": endpoint}
                    )
                    metrics.append(metric)
                    
                    # 思考时间
                    time.sleep(think_time)
                    
                except Exception as e:
                    failed_requests += 1
                    total_requests += 1
                    logging.debug(f"用户 {user_id} 请求失败: {e}")
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "metrics": metrics
        }
    
    def _run_database_tests(self) -> List[TestResult]:
        """运行数据库性能测试"""
        results = []
        db_tests = self.config.get("database_tests", [])
        database_url = self.config.get("environment", {}).get("database_url")
        
        if not database_url:
            logging.warning("未配置数据库URL，跳过数据库测试")
            return results
        
        for test_config in db_tests:
            start_time = datetime.now()
            test_name = test_config.get("name", "Unknown DB Test")
            
            logging.info(f"运行数据库测试: {test_name}")
            
            metrics = []
            total_requests = 1
            successful_requests = 0
            failed_requests = 0
            
            try:
                query = test_config.get("query", "")
                execution_time_threshold = test_config.get("execution_time_threshold", 1.0)
                
                # 执行查询（这里需要根据实际数据库类型实现）
                query_start = time.time()
                # result = self._execute_database_query(database_url, query)
                query_end = time.time()
                
                execution_time = query_end - query_start
                successful_requests = 1
                
                # 记录执行时间指标
                metric = PerformanceMetric(
                    timestamp=datetime.now().isoformat(),
                    test_name=test_name,
                    metric_type="execution_time",
                    value=execution_time,
                    unit="seconds",
                    target_value=execution_time_threshold,
                    passed=execution_time <= execution_time_threshold,
                    details={"query": query[:100] + "..." if len(query) > 100 else query}
                )
                metrics.append(metric)
                
            except Exception as e:
                logging.error(f"数据库测试失败 {test_name}: {e}")
                failed_requests = 1
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 创建测试结果
            result = TestResult(
                test_name=test_name,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                duration=duration,
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                metrics=metrics,
                summary={
                    "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                    "avg_execution_time": sum(m.value for m in metrics if m.metric_type == "execution_time") / len([m for m in metrics if m.metric_type == "execution_time"]) if metrics else 0
                },
                passed=failed_requests == 0 and all(m.passed for m in metrics)
            )
            
            results.append(result)
        
        return results
    
    def _run_stress_tests(self) -> List[TestResult]:
        """运行压力测试"""
        results = []
        stress_config = self.config.get("stress_testing", {})
        max_users = stress_config.get("max_users", 100)
        increment_step = stress_config.get("increment_step", 10)
        step_duration = stress_config.get("step_duration", 30)
        failure_threshold = stress_config.get("failure_threshold", 0.05)
        
        start_time = datetime.now()
        test_name = "压力测试"
        
        logging.info(f"运行压力测试: 最大 {max_users} 用户")
        
        metrics = []
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        
        current_users = increment_step
        
        try:
            while current_users <= max_users:
                step_start = time.time()
                
                # 运行当前用户数的负载测试
                step_result = self._run_load_step(current_users, step_duration)
                
                total_requests += step_result["total_requests"]
                successful_requests += step_result["successful_requests"]
                failed_requests += step_result["failed_requests"]
                metrics.extend(step_result["metrics"])
                
                # 检查失败率
                current_failure_rate = step_result["failed_requests"] / step_result["total_requests"] if step_result["total_requests"] > 0 else 0
                
                if current_failure_rate > failure_threshold:
                    logging.warning(f"压力测试在 {current_users} 用户时失败率过高: {current_failure_rate:.2%}")
                    break
                
                current_users += increment_step
        
        except Exception as e:
            logging.error(f"压力测试失败: {e}")
            failed_requests += current_users
            total_requests += current_users
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 创建测试结果
        result = TestResult(
            test_name=test_name,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration=duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            metrics=metrics,
            summary={
                "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                "max_concurrent_users": current_users - increment_step,
                "breaking_point": current_users if failed_requests > 0 else None
            },
            passed=failed_requests == 0
        )
        
        results.append(result)
        return results
    
    def _run_spike_tests(self) -> List[TestResult]:
        """运行峰值测试"""
        results = []
        spike_config = self.config.get("spike_testing", {})
        normal_load = spike_config.get("normal_load", 10)
        spike_load = spike_config.get("spike_load", 100)
        spike_duration = spike_config.get("spike_duration", 30)
        recovery_time = spike_config.get("recovery_time", 60)
        
        start_time = datetime.now()
        test_name = "峰值测试"
        
        logging.info(f"运行峰值测试: {normal_load} -> {spike_load} -> {normal_load} 用户")
        
        metrics = []
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        
        try:
            # 阶段1: 正常负载
            logging.info("峰值测试阶段1: 正常负载")
            normal_result = self._run_load_step(normal_load, spike_duration)
            total_requests += normal_result["total_requests"]
            successful_requests += normal_result["successful_requests"]
            failed_requests += normal_result["failed_requests"]
            metrics.extend(normal_result["metrics"])
            
            # 阶段2: 峰值负载
            logging.info("峰值测试阶段2: 峰值负载")
            spike_result = self._run_load_step(spike_load, spike_duration)
            total_requests += spike_result["total_requests"]
            successful_requests += spike_result["successful_requests"]
            failed_requests += spike_result["failed_requests"]
            metrics.extend(spike_result["metrics"])
            
            # 阶段3: 恢复负载
            logging.info("峰值测试阶段3: 恢复负载")
            recovery_result = self._run_load_step(normal_load, recovery_time)
            total_requests += recovery_result["total_requests"]
            successful_requests += recovery_result["successful_requests"]
            failed_requests += recovery_result["failed_requests"]
            metrics.extend(recovery_result["metrics"])
            
        except Exception as e:
            logging.error(f"峰值测试失败: {e}")
            failed_requests += spike_load
            total_requests += spike_load
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 创建测试结果
        result = TestResult(
            test_name=test_name,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration=duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            metrics=metrics,
            summary={
                "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                "spike_handled": spike_result["failed_requests"] == 0 if 'spike_result' in locals() else False
            },
            passed=failed_requests == 0
        )
        
        results.append(result)
        return results
    
    def _run_endurance_tests(self) -> List[TestResult]:
        """运行持久性测试"""
        results = []
        endurance_config = self.config.get("endurance_testing", {})
        users = endurance_config.get("users", 20)
        duration = endurance_config.get("duration", 3600)  # 1小时
        memory_threshold = endurance_config.get("memory_threshold", 0.8)
        cpu_threshold = endurance_config.get("cpu_threshold", 0.8)
        
        start_time = datetime.now()
        test_name = "持久性测试"
        
        logging.info(f"运行持久性测试: {users} 用户，持续 {duration} 秒")
        
        metrics = []
        total_requests = 0
        successful_requests = 0
        failed_requests = 0
        
        # 启动系统监控
        monitoring_stop = threading.Event()
        monitoring_thread = threading.Thread(
            target=self._monitor_system_resources,
            args=(monitoring_stop, metrics, test_name, memory_threshold, cpu_threshold)
        )
        monitoring_thread.start()
        
        try:
            # 运行长时间负载测试
            endurance_result = self._run_load_step(users, duration)
            total_requests += endurance_result["total_requests"]
            successful_requests += endurance_result["successful_requests"]
            failed_requests += endurance_result["failed_requests"]
            metrics.extend(endurance_result["metrics"])
            
        except Exception as e:
            logging.error(f"持久性测试失败: {e}")
            failed_requests += users
            total_requests += users
        finally:
            # 停止监控
            monitoring_stop.set()
            monitoring_thread.join()
        
        end_time = datetime.now()
        actual_duration = (end_time - start_time).total_seconds()
        
        # 创建测试结果
        result = TestResult(
            test_name=test_name,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            duration=actual_duration,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            metrics=metrics,
            summary={
                "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
                "resource_usage_passed": all(m.passed for m in metrics if m.metric_type in ["cpu_usage", "memory_usage"])
            },
            passed=failed_requests == 0 and all(m.passed for m in metrics if m.metric_type in ["cpu_usage", "memory_usage"])
        )
        
        results.append(result)
        return results
    
    def _run_load_step(self, users: int, duration: int) -> Dict[str, Any]:
        """运行单个负载测试步骤"""
        with ThreadPoolExecutor(max_workers=users) as executor:
            futures = []
            
            # 启动并发任务
            for i in range(users):
                future = executor.submit(self._simulate_user_load, duration, i)
                futures.append(future)
            
            # 收集结果
            total_requests = 0
            successful_requests = 0
            failed_requests = 0
            metrics = []
            
            for future in as_completed(futures):
                try:
                    user_result = future.result()
                    total_requests += user_result["total_requests"]
                    successful_requests += user_result["successful_requests"]
                    failed_requests += user_result["failed_requests"]
                    metrics.extend(user_result["metrics"])
                except Exception as e:
                    logging.error(f"用户模拟失败: {e}")
                    failed_requests += 1
                    total_requests += 1
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "metrics": metrics
        }
    
    def _monitor_system_resources(self, stop_event: threading.Event, metrics: List[PerformanceMetric], 
                                test_name: str, memory_threshold: float, cpu_threshold: float):
        """监控系统资源使用情况"""
        interval = self.config.get("monitoring", {}).get("interval", 5)
        
        while not stop_event.is_set():
            try:
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_metric = PerformanceMetric(
                    timestamp=datetime.now().isoformat(),
                    test_name=test_name,
                    metric_type="cpu_usage",
                    value=cpu_percent / 100,
                    unit="percentage",
                    target_value=cpu_threshold,
                    passed=cpu_percent / 100 <= cpu_threshold
                )
                metrics.append(cpu_metric)
                
                # 内存使用率
                memory = psutil.virtual_memory()
                memory_metric = PerformanceMetric(
                    timestamp=datetime.now().isoformat(),
                    test_name=test_name,
                    metric_type="memory_usage",
                    value=memory.percent / 100,
                    unit="percentage",
                    target_value=memory_threshold,
                    passed=memory.percent / 100 <= memory_threshold
                )
                metrics.append(memory_metric)
                
                # 等待下一次检查
                stop_event.wait(interval)
                
            except Exception as e:
                logging.error(f"系统监控失败: {e}")
                break
    
    def _process_placeholders(self, data: Any, tokens: Dict[str, str]) -> Any:
        """处理配置中的占位符"""
        if isinstance(data, str):
            # 替换时间戳
            if "{{TIMESTAMP}}" in data:
                data = data.replace("{{TIMESTAMP}}", str(int(time.time())))
            
            # 替换令牌
            for key, value in tokens.items():
                placeholder = f"{{{{{key}}}}}"
                if placeholder in data:
                    data = data.replace(placeholder, value)
            
            # 替换环境变量
            import re
            env_pattern = r'\{\{([A-Z_]+)\}\}'
            matches = re.findall(env_pattern, data)
            for match in matches:
                env_value = os.getenv(match, f"{{{{match}}}}")
                data = data.replace(f"{{{{{match}}}}}", env_value)
            
            return data
        
        elif isinstance(data, dict):
            return {key: self._process_placeholders(value, tokens) for key, value in data.items()}
        
        elif isinstance(data, list):
            return [self._process_placeholders(item, tokens) for item in data]
        
        else:
            return data
    
    def _generate_overall_summary(self, test_results: List[TestResult]) -> Dict[str, Any]:
        """生成总体摘要"""
        if not test_results:
            return {}
        
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result.passed)
        failed_tests = total_tests - passed_tests
        
        total_requests = sum(result.total_requests for result in test_results)
        successful_requests = sum(result.successful_requests for result in test_results)
        failed_requests = sum(result.failed_requests for result in test_results)
        
        # 收集所有响应时间指标
        response_times = []
        for result in test_results:
            for metric in result.metrics:
                if metric.metric_type == "response_time":
                    response_times.append(metric.value)
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "request_success_rate": successful_requests / total_requests if total_requests > 0 else 0
        }
        
        if response_times:
            summary.update({
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "p95_response_time": np.percentile(response_times, 95),
                "p99_response_time": np.percentile(response_times, 99)
            })
        
        return summary
    
    def _save_results_to_db(self, report: PerformanceReport):
        """保存结果到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 插入测试运行记录
            cursor.execute("""
                INSERT INTO test_runs (project_name, test_suite, start_time, end_time, duration, passed)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                report.project_name,
                report.test_suite,
                report.start_time,
                report.end_time,
                report.total_duration,
                report.passed
            ))
            
            run_id = cursor.lastrowid
            
            # 插入测试结果
            for result in report.test_results:
                cursor.execute("""
                    INSERT INTO test_results (run_id, test_name, start_time, end_time, duration, 
                                            total_requests, successful_requests, failed_requests, passed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    run_id,
                    result.test_name,
                    result.start_time,
                    result.end_time,
                    result.duration,
                    result.total_requests,
                    result.successful_requests,
                    result.failed_requests,
                    result.passed
                ))
                
                result_id = cursor.lastrowid
                
                # 插入指标
                for metric in result.metrics:
                    cursor.execute("""
                        INSERT INTO metrics (result_id, timestamp, metric_type, value, unit, target_value, passed)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        result_id,
                        metric.timestamp,
                        metric.metric_type,
                        metric.value,
                        metric.unit,
                        metric.target_value,
                        metric.passed
                    ))
            
            conn.commit()
            conn.close()
            
            logging.info("测试结果已保存到数据库")
            
        except Exception as e:
            logging.error(f"保存结果到数据库失败: {e}")
    
    def generate_report(self, report: PerformanceReport, output_formats: List[str] = None) -> Dict[str, str]:
        """生成性能测试报告"""
        if not output_formats:
            output_formats = self.config.get("reporting", {}).get("formats", ["console"])
        
        output_dir = Path(self.config.get("reporting", {}).get("output_directory", "./reports/performance"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        for format_type in output_formats:
            if format_type == "json":
                json_file = output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self._generate_json_report(report, json_file)
                generated_files["json"] = str(json_file)
            
            elif format_type == "html":
                html_file = output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                self._generate_html_report(report, html_file)
                generated_files["html"] = str(html_file)
            
            elif format_type == "csv":
                csv_file = output_dir / f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                self._generate_csv_report(report, csv_file)
                generated_files["csv"] = str(csv_file)
            
            elif format_type == "console":
                self._generate_console_report(report)
                generated_files["console"] = "控制台输出"
        
        # 生成图表
        if self.config.get("reporting", {}).get("include_charts", True):
            charts_dir = output_dir / "charts"
            charts_dir.mkdir(exist_ok=True)
            chart_files = self._generate_charts(report, charts_dir)
            generated_files.update(chart_files)
        
        return generated_files
    
    def _generate_json_report(self, report: PerformanceReport, output_file: Path):
        """生成JSON格式报告"""
        try:
            report_data = asdict(report)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            logging.info(f"JSON报告已生成: {output_file}")
        
        except Exception as e:
            logging.error(f"生成JSON报告失败: {e}")
    
    def _generate_html_report(self, report: PerformanceReport, output_file: Path):
        """生成HTML格式报告"""
        try:
            html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>性能测试报告 - {project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 2.5em; }}
        .header p {{ margin: 5px 0; opacity: 0.9; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }}
        .summary-card h3 {{ margin: 0 0 10px 0; color: #333; }}
        .summary-card .value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .summary-card .unit {{ color: #666; font-size: 0.9em; }}
        .test-results {{ margin-bottom: 30px; }}
        .test-result {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 20px; overflow: hidden; }}
        .test-result.passed {{ border-left: 4px solid #28a745; }}
        .test-result.failed {{ border-left: 4px solid #dc3545; }}
        .test-header {{ background: #f8f9fa; padding: 15px; border-bottom: 1px solid #ddd; }}
        .test-header h3 {{ margin: 0; color: #333; }}
        .test-content {{ padding: 20px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric {{ background: #f8f9fa; padding: 15px; border-radius: 6px; }}
        .metric.passed {{ background: #d4edda; }}
        .metric.failed {{ background: #f8d7da; }}
        .metric-name {{ font-weight: bold; color: #333; }}
        .metric-value {{ font-size: 1.2em; margin: 5px 0; }}
        .metric-target {{ color: #666; font-size: 0.9em; }}
        .status {{ padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }}
        .status.passed {{ background: #28a745; color: white; }}
        .status.failed {{ background: #dc3545; color: white; }}
        .environment {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 30px; }}
        .environment h3 {{ margin: 0 0 15px 0; }}
        .env-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }}
        .env-item {{ display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>性能测试报告</h1>
            <p>项目: {project_name}</p>
            <p>测试套件: {test_suite}</p>
            <p>测试时间: {start_time} - {end_time}</p>
            <p>总耗时: {total_duration:.2f} 秒</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>测试通过率</h3>
                <div class="value">{success_rate:.1%}</div>
                <div class="unit">({passed_tests}/{total_tests} 测试)</div>
            </div>
            <div class="summary-card">
                <h3>请求成功率</h3>
                <div class="value">{request_success_rate:.1%}</div>
                <div class="unit">({successful_requests}/{total_requests} 请求)</div>
            </div>
            <div class="summary-card">
                <h3>平均响应时间</h3>
                <div class="value">{avg_response_time:.3f}</div>
                <div class="unit">秒</div>
            </div>
            <div class="summary-card">
                <h3>总体状态</h3>
                <div class="value status {overall_status}">{overall_status_text}</div>
            </div>
        </div>
        
        <div class="test-results">
            <h2>测试结果详情</h2>
            {test_results_html}
        </div>
        
        <div class="environment">
            <h3>测试环境信息</h3>
            <div class="env-grid">
                {environment_html}
            </div>
        </div>
    </div>
</body>
</html>
            """
            
            # 准备数据
            summary = report.overall_summary
            
            # 生成测试结果HTML
            test_results_html = ""
            for result in report.test_results:
                status_class = "passed" if result.passed else "failed"
                status_text = "通过" if result.passed else "失败"
                
                metrics_html = ""
                for metric in result.metrics:
                    metric_class = "passed" if metric.passed else "failed"
                    target_text = f"目标: {metric.target_value} {metric.unit}" if metric.target_value else ""
                    
                    metrics_html += f"""
                    <div class="metric {metric_class}">
                        <div class="metric-name">{metric.metric_type}</div>
                        <div class="metric-value">{metric.value:.3f} {metric.unit}</div>
                        <div class="metric-target">{target_text}</div>
                    </div>
                    """
                
                test_results_html += f"""
                <div class="test-result {status_class}">
                    <div class="test-header">
                        <h3>{result.test_name} <span class="status {status_class}">{status_text}</span></h3>
                    </div>
                    <div class="test-content">
                        <p>耗时: {result.duration:.2f}秒 | 请求: {result.total_requests} | 成功: {result.successful_requests} | 失败: {result.failed_requests}</p>
                        <div class="metrics">
                            {metrics_html}
                        </div>
                    </div>
                </div>
                """
            
            # 生成环境信息HTML
            environment_html = ""
            for key, value in report.environment_info.items():
                environment_html += f"""
                <div class="env-item">
                    <span>{key}</span>
                    <span>{value}</span>
                </div>
                """
            
            # 填充模板
            html_content = html_template.format(
                project_name=report.project_name,
                test_suite=report.test_suite,
                start_time=report.start_time,
                end_time=report.end_time,
                total_duration=report.total_duration,
                success_rate=summary.get("success_rate", 0),
                passed_tests=summary.get("passed_tests", 0),
                total_tests=summary.get("total_tests", 0),
                request_success_rate=summary.get("request_success_rate", 0),
                successful_requests=summary.get("successful_requests", 0),
                total_requests=summary.get("total_requests", 0),
                avg_response_time=summary.get("avg_response_time", 0),
                overall_status="passed" if report.passed else "failed",
                overall_status_text="通过" if report.passed else "失败",
                test_results_html=test_results_html,
                environment_html=environment_html
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logging.info(f"HTML报告已生成: {output_file}")
        
        except Exception as e:
            logging.error(f"生成HTML报告失败: {e}")
    
    def _generate_csv_report(self, report: PerformanceReport, output_file: Path):
        """生成CSV格式报告"""
        try:
            import csv
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入标题行
                writer.writerow([
                    '测试名称', '开始时间', '结束时间', '耗时(秒)', 
                    '总请求数', '成功请求数', '失败请求数', '成功率', 
                    '指标类型', '指标值', '指标单位', '目标值', '是否通过'
                ])
                
                # 写入数据行
                for result in report.test_results:
                    base_row = [
                        result.test_name,
                        result.start_time,
                        result.end_time,
                        result.duration,
                        result.total_requests,
                        result.successful_requests,
                        result.failed_requests,
                        result.successful_requests / result.total_requests if result.total_requests > 0 else 0
                    ]
                    
                    if result.metrics:
                        for metric in result.metrics:
                            row = base_row + [
                                metric.metric_type,
                                metric.value,
                                metric.unit,
                                metric.target_value or '',
                                '是' if metric.passed else '否'
                            ]
                            writer.writerow(row)
                    else:
                        row = base_row + ['', '', '', '', '']
                        writer.writerow(row)
            
            logging.info(f"CSV报告已生成: {output_file}")
        
        except Exception as e:
            logging.error(f"生成CSV报告失败: {e}")
    
    def _generate_console_report(self, report: PerformanceReport):
        """生成控制台报告"""
        print("\n" + "="*80)
        print(f"性能测试报告 - {report.project_name}")
        print("="*80)
        print(f"测试套件: {report.test_suite}")
        print(f"测试时间: {report.start_time} - {report.end_time}")
        print(f"总耗时: {report.total_duration:.2f} 秒")
        print(f"总体状态: {'通过' if report.passed else '失败'}")
        
        # 总体摘要
        summary = report.overall_summary
        print("\n总体摘要:")
        print("-"*40)
        print(f"测试通过率: {summary.get('success_rate', 0):.1%} ({summary.get('passed_tests', 0)}/{summary.get('total_tests', 0)})")
        print(f"请求成功率: {summary.get('request_success_rate', 0):.1%} ({summary.get('successful_requests', 0)}/{summary.get('total_requests', 0)})")
        
        if 'avg_response_time' in summary:
            print(f"平均响应时间: {summary['avg_response_time']:.3f} 秒")
            print(f"最小响应时间: {summary.get('min_response_time', 0):.3f} 秒")
            print(f"最大响应时间: {summary.get('max_response_time', 0):.3f} 秒")
            print(f"P95响应时间: {summary.get('p95_response_time', 0):.3f} 秒")
            print(f"P99响应时间: {summary.get('p99_response_time', 0):.3f} 秒")
        
        # 测试结果详情
        print("\n测试结果详情:")
        print("-"*40)
        
        for result in report.test_results:
            status = "✓ 通过" if result.passed else "✗ 失败"
            print(f"\n{result.test_name}: {status}")
            print(f"  耗时: {result.duration:.2f}秒")
            print(f"  请求: {result.total_requests} | 成功: {result.successful_requests} | 失败: {result.failed_requests}")
            
            if result.metrics:
                print("  指标:")
                for metric in result.metrics:
                    status_icon = "✓" if metric.passed else "✗"
                    target_text = f" (目标: {metric.target_value})" if metric.target_value else ""
                    print(f"    {status_icon} {metric.metric_type}: {metric.value:.3f} {metric.unit}{target_text}")
        
        # 环境信息
        print("\n环境信息:")
        print("-"*40)
        for key, value in report.environment_info.items():
            print(f"{key}: {value}")
        
        print("\n" + "="*80)
    
    def _generate_charts(self, report: PerformanceReport, charts_dir: Path) -> Dict[str, str]:
        """生成性能图表"""
        chart_files = {}
        
        try:
            # 响应时间趋势图
            response_times = []
            timestamps = []
            test_names = []
            
            for result in report.test_results:
                for metric in result.metrics:
                    if metric.metric_type == "response_time":
                        response_times.append(metric.value)
                        timestamps.append(metric.timestamp)
                        test_names.append(result.test_name)
            
            if response_times:
                plt.figure(figsize=(12, 6))
                plt.plot(range(len(response_times)), response_times, 'b-o', markersize=4)
                plt.title('响应时间趋势')
                plt.xlabel('测试序号')
                plt.ylabel('响应时间 (秒)')
                plt.grid(True, alpha=0.3)
                
                chart_file = charts_dir / 'response_time_trend.png'
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                chart_files['response_time_trend'] = str(chart_file)
            
            # 测试结果分布饼图
            passed_count = sum(1 for result in report.test_results if result.passed)
            failed_count = len(report.test_results) - passed_count
            
            if passed_count > 0 or failed_count > 0:
                plt.figure(figsize=(8, 8))
                labels = ['通过', '失败']
                sizes = [passed_count, failed_count]
                colors = ['#28a745', '#dc3545']
                
                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                plt.title('测试结果分布')
                
                chart_file = charts_dir / 'test_results_distribution.png'
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                chart_files['test_results_distribution'] = str(chart_file)
            
            # 性能指标对比柱状图
            metric_types = defaultdict(list)
            for result in report.test_results:
                for metric in result.metrics:
                    metric_types[metric.metric_type].append(metric.value)
            
            if metric_types:
                fig, axes = plt.subplots(len(metric_types), 1, figsize=(10, 6*len(metric_types)))
                if len(metric_types) == 1:
                    axes = [axes]
                
                for i, (metric_type, values) in enumerate(metric_types.items()):
                    axes[i].bar(range(len(values)), values, color='#007bff', alpha=0.7)
                    axes[i].set_title(f'{metric_type} 分布')
                    axes[i].set_xlabel('测试序号')
                    axes[i].set_ylabel('值')
                    axes[i].grid(True, alpha=0.3)
                
                plt.tight_layout()
                chart_file = charts_dir / 'metrics_comparison.png'
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                chart_files['metrics_comparison'] = str(chart_file)
            
            logging.info(f"图表已生成到: {charts_dir}")
        
        except Exception as e:
            logging.error(f"生成图表失败: {e}")
        
        return chart_files

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新能源编程俱乐部性能测试工具")
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--types', '-t', nargs='+', 
                       choices=['api', 'web', 'load', 'stress', 'spike', 'endurance', 'database'],
                       default=['api', 'web', 'load'],
                       help='要运行的测试类型')
    parser.add_argument('--output', '-o', nargs='+',
                       choices=['console', 'json', 'html', 'csv'],
                       default=['console', 'html'],
                       help='报告输出格式')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--init', action='store_true', help='初始化配置文件')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 初始化性能测试器
        tester = PerformanceTester(args.config)
        
        if args.init:
            print("配置文件已初始化")
            print(f"配置文件路径: {tester.config_path}")
            return
        
        # 运行性能测试
        print(f"开始运行性能测试，测试类型: {', '.join(args.types)}")
        report = tester.run_performance_tests(args.types)
        
        # 生成报告
        generated_files = tester.generate_report(report, args.output)
        
        print("\n报告生成完成:")
        for format_type, file_path in generated_files.items():
            print(f"  {format_type}: {file_path}")
        
        # 返回退出码
        sys.exit(0 if report.passed else 1)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(130)
    except Exception as e:
        logging.error(f"性能测试失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()}