#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试运行器
支持多种测试类型和测试框架的统一测试执行
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
import shutil
import re

class TestRunner:
    """测试运行器"""
    
    def __init__(self, config_path: str = None):
        self.root_path = Path(".").resolve()
        self.config_path = config_path or self.root_path / "config" / "test.yaml"
        self.config = self._load_config()
        self.test_results = []
        self.coverage_data = {}
        self.performance_data = {}
        
        # 支持的测试类型
        self.test_types = {
            "unit": self._run_unit_tests,
            "integration": self._run_integration_tests,
            "e2e": self._run_e2e_tests,
            "performance": self._run_performance_tests,
            "security": self._run_security_tests,
            "accessibility": self._run_accessibility_tests,
            "visual": self._run_visual_tests,
            "api": self._run_api_tests
        }
        
        # 支持的测试框架
        self.frameworks = {
            "jest": self._run_jest,
            "vitest": self._run_vitest,
            "pytest": self._run_pytest,
            "mocha": self._run_mocha,
            "cypress": self._run_cypress,
            "playwright": self._run_playwright,
            "selenium": self._run_selenium,
            "postman": self._run_postman
        }
    
    def _load_config(self) -> Dict:
        """加载测试配置"""
        if not self.config_path.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            self.log_result("load_config", "error", f"配置加载失败: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """创建默认测试配置"""
        default_config = {
            "project": {
                "name": "new-energy-coder-club",
                "version": "1.0.0",
                "test_environments": ["development", "staging", "production"]
            },
            "frameworks": {
                "unit": {
                    "framework": "jest",
                    "config_file": "jest.config.js",
                    "test_dir": "tests/unit",
                    "pattern": "**/*.test.{js,ts,jsx,tsx}",
                    "coverage": True,
                    "threshold": {
                        "statements": 80,
                        "branches": 75,
                        "functions": 80,
                        "lines": 80
                    }
                },
                "integration": {
                    "framework": "jest",
                    "config_file": "jest.integration.config.js",
                    "test_dir": "tests/integration",
                    "pattern": "**/*.integration.{js,ts}",
                    "setup_script": "scripts/setup-integration.sh",
                    "teardown_script": "scripts/teardown-integration.sh"
                },
                "e2e": {
                    "framework": "playwright",
                    "config_file": "playwright.config.ts",
                    "test_dir": "tests/e2e",
                    "pattern": "**/*.spec.{js,ts}",
                    "browsers": ["chromium", "firefox", "webkit"],
                    "headless": True,
                    "video": "retain-on-failure",
                    "screenshot": "only-on-failure"
                },
                "api": {
                    "framework": "postman",
                    "collection": "tests/api/collection.json",
                    "environment": "tests/api/environment.json",
                    "globals": "tests/api/globals.json"
                },
                "performance": {
                    "framework": "lighthouse",
                    "config_file": "lighthouse.config.js",
                    "urls": [
                        "http://localhost:3000",
                        "http://localhost:3000/projects",
                        "http://localhost:3000/docs"
                    ],
                    "thresholds": {
                        "performance": 90,
                        "accessibility": 95,
                        "best-practices": 90,
                        "seo": 85
                    }
                },
                "security": {
                    "tools": ["npm-audit", "snyk", "semgrep"],
                    "config_files": {
                        "snyk": ".snyk",
                        "semgrep": "semgrep.yml"
                    }
                },
                "accessibility": {
                    "framework": "axe",
                    "config_file": "axe.config.js",
                    "standards": ["wcag2a", "wcag2aa", "wcag21aa"]
                },
                "visual": {
                    "framework": "percy",
                    "config_file": "percy.config.yml",
                    "snapshots_dir": "tests/visual/snapshots"
                }
            },
            "environments": {
                "development": {
                    "base_url": "http://localhost:3000",
                    "api_url": "http://localhost:3001/api",
                    "database_url": "postgresql://localhost:5432/test_db",
                    "redis_url": "redis://localhost:6379"
                },
                "staging": {
                    "base_url": "https://staging.example.com",
                    "api_url": "https://api-staging.example.com",
                    "database_url": "${STAGING_DATABASE_URL}",
                    "redis_url": "${STAGING_REDIS_URL}"
                },
                "production": {
                    "base_url": "https://example.com",
                    "api_url": "https://api.example.com",
                    "database_url": "${PRODUCTION_DATABASE_URL}",
                    "redis_url": "${PRODUCTION_REDIS_URL}"
                }
            },
            "reporting": {
                "formats": ["json", "html", "junit"],
                "output_dir": "test-results",
                "merge_reports": True,
                "upload_to_s3": False,
                "slack_webhook": "${SLACK_WEBHOOK_URL}"
            },
            "parallel": {
                "enabled": True,
                "workers": 4,
                "shard": False
            },
            "retry": {
                "enabled": True,
                "max_attempts": 3,
                "delay": 1000
            },
            "timeouts": {
                "unit": 30000,
                "integration": 60000,
                "e2e": 120000,
                "performance": 300000
            }
        }
        
        # 保存默认配置
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            self.log_result("create_config", "success", "默认测试配置已创建")
        except Exception as e:
            self.log_result("create_config", "error", f"配置创建失败: {e}")
        
        return default_config
    
    def log_result(self, test_type: str, status: str, message: str, details: Dict = None):
        """记录测试结果"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_type": test_type,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        
        # 实时输出
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️" if status == "warning" else "ℹ️"
        print(f"{status_icon} {test_type}: {message}")
    
    def setup_test_environment(self, environment: str) -> bool:
        """设置测试环境"""
        print(f"🔧 设置 {environment} 测试环境")
        
        env_config = self.config.get("environments", {}).get(environment, {})
        if not env_config:
            self.log_result("setup_env", "error", f"环境 {environment} 配置不存在")
            return False
        
        # 设置环境变量
        for key, value in env_config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                value = os.getenv(env_var, value)
            os.environ[key.upper()] = str(value)
        
        # 检查必要的服务
        if not self._check_services(env_config):
            return False
        
        # 准备测试数据
        if not self._prepare_test_data(environment):
            return False
        
        self.log_result("setup_env", "success", f"{environment} 环境设置完成")
        return True
    
    def _check_services(self, env_config: Dict) -> bool:
        """检查必要的服务"""
        services = {
            "database": env_config.get("database_url"),
            "redis": env_config.get("redis_url"),
            "api": env_config.get("api_url")
        }
        
        for service, url in services.items():
            if url and not self._is_service_available(service, url):
                self.log_result("check_services", "warning", f"{service} 服务不可用: {url}")
        
        return True
    
    def _is_service_available(self, service: str, url: str) -> bool:
        """检查服务是否可用"""
        try:
            if service == "database":
                # 检查数据库连接
                if "postgresql" in url:
                    import psycopg2
                    conn = psycopg2.connect(url)
                    conn.close()
                elif "mysql" in url:
                    import mysql.connector
                    conn = mysql.connector.connect(url)
                    conn.close()
                return True
            elif service == "redis":
                # 检查Redis连接
                import redis
                r = redis.from_url(url)
                r.ping()
                return True
            elif service == "api":
                # 检查API可用性
                import requests
                response = requests.get(f"{url}/health", timeout=5)
                return response.status_code == 200
        except Exception:
            return False
        
        return True
    
    def _prepare_test_data(self, environment: str) -> bool:
        """准备测试数据"""
        test_data_dir = self.root_path / "tests" / "data" / environment
        if not test_data_dir.exists():
            return True
        
        try:
            # 执行数据准备脚本
            setup_script = test_data_dir / "setup.py"
            if setup_script.exists():
                result = subprocess.run(["python", str(setup_script)], 
                                      cwd=self.root_path, capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_result("prepare_data", "error", f"测试数据准备失败: {result.stderr}")
                    return False
            
            self.log_result("prepare_data", "success", "测试数据准备完成")
            return True
            
        except Exception as e:
            self.log_result("prepare_data", "error", f"测试数据准备异常: {e}")
            return False
    
    def _run_unit_tests(self, config: Dict) -> bool:
        """运行单元测试"""
        framework = config.get("framework", "jest")
        
        if framework in self.frameworks:
            return self.frameworks[framework](config, "unit")
        else:
            self.log_result("unit_tests", "error", f"不支持的测试框架: {framework}")
            return False
    
    def _run_integration_tests(self, config: Dict) -> bool:
        """运行集成测试"""
        # 运行设置脚本
        setup_script = config.get("setup_script")
        if setup_script and Path(setup_script).exists():
            subprocess.run(["bash", setup_script], cwd=self.root_path)
        
        try:
            framework = config.get("framework", "jest")
            result = self.frameworks[framework](config, "integration")
            
            # 运行清理脚本
            teardown_script = config.get("teardown_script")
            if teardown_script and Path(teardown_script).exists():
                subprocess.run(["bash", teardown_script], cwd=self.root_path)
            
            return result
            
        except Exception as e:
            self.log_result("integration_tests", "error", f"集成测试异常: {e}")
            return False
    
    def _run_e2e_tests(self, config: Dict) -> bool:
        """运行端到端测试"""
        framework = config.get("framework", "playwright")
        
        if framework in self.frameworks:
            return self.frameworks[framework](config, "e2e")
        else:
            self.log_result("e2e_tests", "error", f"不支持的E2E框架: {framework}")
            return False
    
    def _run_performance_tests(self, config: Dict) -> bool:
        """运行性能测试"""
        framework = config.get("framework", "lighthouse")
        
        if framework == "lighthouse":
            return self._run_lighthouse(config)
        elif framework == "k6":
            return self._run_k6(config)
        else:
            self.log_result("performance_tests", "error", f"不支持的性能测试框架: {framework}")
            return False
    
    def _run_security_tests(self, config: Dict) -> bool:
        """运行安全测试"""
        tools = config.get("tools", ["npm-audit"])
        all_passed = True
        
        for tool in tools:
            if tool == "npm-audit":
                result = self._run_npm_audit()
            elif tool == "snyk":
                result = self._run_snyk(config)
            elif tool == "semgrep":
                result = self._run_semgrep(config)
            else:
                self.log_result("security_tests", "warning", f"未知的安全工具: {tool}")
                continue
            
            if not result:
                all_passed = False
        
        return all_passed
    
    def _run_accessibility_tests(self, config: Dict) -> bool:
        """运行可访问性测试"""
        framework = config.get("framework", "axe")
        
        if framework == "axe":
            return self._run_axe(config)
        else:
            self.log_result("accessibility_tests", "error", f"不支持的可访问性测试框架: {framework}")
            return False
    
    def _run_visual_tests(self, config: Dict) -> bool:
        """运行视觉回归测试"""
        framework = config.get("framework", "percy")
        
        if framework == "percy":
            return self._run_percy(config)
        elif framework == "chromatic":
            return self._run_chromatic(config)
        else:
            self.log_result("visual_tests", "error", f"不支持的视觉测试框架: {framework}")
            return False
    
    def _run_api_tests(self, config: Dict) -> bool:
        """运行API测试"""
        framework = config.get("framework", "postman")
        
        if framework == "postman":
            return self._run_postman(config, "api")
        elif framework == "rest-assured":
            return self._run_rest_assured(config)
        else:
            self.log_result("api_tests", "error", f"不支持的API测试框架: {framework}")
            return False
    
    def _run_jest(self, config: Dict, test_type: str) -> bool:
        """运行Jest测试"""
        try:
            cmd = ["npx", "jest"]
            
            # 配置文件
            config_file = config.get("config_file")
            if config_file:
                cmd.extend(["--config", config_file])
            
            # 测试模式
            test_dir = config.get("test_dir")
            if test_dir:
                cmd.append(test_dir)
            
            # 覆盖率
            if config.get("coverage", False):
                cmd.append("--coverage")
            
            # 并行执行
            parallel_config = self.config.get("parallel", {})
            if parallel_config.get("enabled", True):
                workers = parallel_config.get("workers", 4)
                cmd.extend(["--maxWorkers", str(workers)])
            
            # 输出格式
            reporting_config = self.config.get("reporting", {})
            output_dir = reporting_config.get("output_dir", "test-results")
            
            if "junit" in reporting_config.get("formats", []):
                cmd.extend(["--testResultsProcessor", "jest-junit"])
                os.environ["JEST_JUNIT_OUTPUT_DIR"] = output_dir
            
            # 执行测试
            result = subprocess.run(cmd, cwd=self.root_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result(f"jest_{test_type}", "success", "Jest测试通过")
                self._parse_jest_results(result.stdout, test_type)
                return True
            else:
                self.log_result(f"jest_{test_type}", "error", f"Jest测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result(f"jest_{test_type}", "error", f"Jest执行异常: {e}")
            return False
    
    def _run_vitest(self, config: Dict, test_type: str) -> bool:
        """运行Vitest测试"""
        try:
            cmd = ["npx", "vitest", "run"]
            
            # 配置文件
            config_file = config.get("config_file")
            if config_file:
                cmd.extend(["--config", config_file])
            
            # 覆盖率
            if config.get("coverage", False):
                cmd.append("--coverage")
            
            # 执行测试
            result = subprocess.run(cmd, cwd=self.root_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result(f"vitest_{test_type}", "success", "Vitest测试通过")
                return True
            else:
                self.log_result(f"vitest_{test_type}", "error", f"Vitest测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result(f"vitest_{test_type}", "error", f"Vitest执行异常: {e}")
            return False
    
    def _run_pytest(self, config: Dict, test_type: str) -> bool:
        """运行Pytest测试"""
        try:
            cmd = ["python", "-m", "pytest"]
            
            # 测试目录
            test_dir = config.get("test_dir")
            if test_dir:
                cmd.append(test_dir)
            
            # 覆盖率
            if config.get("coverage", False):
                cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=xml"])
            
            # 并行执行
            parallel_config = self.config.get("parallel", {})
            if parallel_config.get("enabled", True):
                workers = parallel_config.get("workers", 4)
                cmd.extend(["-n", str(workers)])
            
            # JUnit输出
            reporting_config = self.config.get("reporting", {})
            if "junit" in reporting_config.get("formats", []):
                output_dir = reporting_config.get("output_dir", "test-results")
                cmd.extend(["--junit-xml", f"{output_dir}/pytest-results.xml"])
            
            # 执行测试
            result = subprocess.run(cmd, cwd=self.root_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result(f"pytest_{test_type}", "success", "Pytest测试通过")
                return True
            else:
                self.log_result(f"pytest_{test_type}", "error", f"Pytest测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result(f"pytest_{test_type}", "error", f"Pytest执行异常: {e}")
            return False
    
    def _run_playwright(self, config: Dict, test_type: str) -> bool:
        """运行Playwright测试"""
        try:
            cmd = ["npx", "playwright", "test"]
            
            # 配置文件
            config_file = config.get("config_file")
            if config_file:
                cmd.extend(["--config", config_file])
            
            # 浏览器
            browsers = config.get("browsers", ["chromium"])
            for browser in browsers:
                cmd.extend(["--project", browser])
            
            # 无头模式
            if config.get("headless", True):
                cmd.append("--headed=false")
            else:
                cmd.append("--headed=true")
            
            # 并行执行
            parallel_config = self.config.get("parallel", {})
            if parallel_config.get("enabled", True):
                workers = parallel_config.get("workers", 4)
                cmd.extend(["--workers", str(workers)])
            
            # 报告格式
            reporting_config = self.config.get("reporting", {})
            output_dir = reporting_config.get("output_dir", "test-results")
            
            if "html" in reporting_config.get("formats", []):
                cmd.extend(["--reporter", "html"])
            
            if "junit" in reporting_config.get("formats", []):
                cmd.extend(["--reporter", f"junit:{output_dir}/playwright-results.xml"])
            
            # 执行测试
            result = subprocess.run(cmd, cwd=self.root_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result(f"playwright_{test_type}", "success", "Playwright测试通过")
                return True
            else:
                self.log_result(f"playwright_{test_type}", "error", f"Playwright测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result(f"playwright_{test_type}", "error", f"Playwright执行异常: {e}")
            return False
    
    def _run_cypress(self, config: Dict, test_type: str) -> bool:
        """运行Cypress测试"""
        try:
            cmd = ["npx", "cypress", "run"]
            
            # 配置文件
            config_file = config.get("config_file")
            if config_file:
                cmd.extend(["--config-file", config_file])
            
            # 浏览器
            browser = config.get("browser", "chrome")
            cmd.extend(["--browser", browser])
            
            # 无头模式
            if config.get("headless", True):
                cmd.append("--headless")
            
            # 执行测试
            result = subprocess.run(cmd, cwd=self.root_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result(f"cypress_{test_type}", "success", "Cypress测试通过")
                return True
            else:
                self.log_result(f"cypress_{test_type}", "error", f"Cypress测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result(f"cypress_{test_type}", "error", f"Cypress执行异常: {e}")
            return False
    
    def _run_postman(self, config: Dict, test_type: str) -> bool:
        """运行Postman测试"""
        try:
            cmd = ["npx", "newman", "run"]
            
            # 集合文件
            collection = config.get("collection")
            if not collection or not Path(collection).exists():
                self.log_result(f"postman_{test_type}", "error", "Postman集合文件不存在")
                return False
            
            cmd.append(collection)
            
            # 环境文件
            environment = config.get("environment")
            if environment and Path(environment).exists():
                cmd.extend(["--environment", environment])
            
            # 全局变量
            globals_file = config.get("globals")
            if globals_file and Path(globals_file).exists():
                cmd.extend(["--globals", globals_file])
            
            # 报告格式
            reporting_config = self.config.get("reporting", {})
            output_dir = reporting_config.get("output_dir", "test-results")
            
            if "junit" in reporting_config.get("formats", []):
                cmd.extend(["--reporters", "junit", "--reporter-junit-export", f"{output_dir}/newman-results.xml"])
            
            if "html" in reporting_config.get("formats", []):
                cmd.extend(["--reporters", "html", "--reporter-html-export", f"{output_dir}/newman-report.html"])
            
            # 执行测试
            result = subprocess.run(cmd, cwd=self.root_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result(f"postman_{test_type}", "success", "Postman测试通过")
                return True
            else:
                self.log_result(f"postman_{test_type}", "error", f"Postman测试失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result(f"postman_{test_type}", "error", f"Postman执行异常: {e}")
            return False
    
    def _run_lighthouse(self, config: Dict) -> bool:
        """运行Lighthouse性能测试"""
        try:
            urls = config.get("urls", [])
            thresholds = config.get("thresholds", {})
            
            for url in urls:
                cmd = ["npx", "lighthouse", url, "--output=json", "--quiet"]
                
                result = subprocess.run(cmd, cwd=self.root_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # 解析Lighthouse结果
                    lighthouse_data = json.loads(result.stdout)
                    scores = {
                        "performance": lighthouse_data["categories"]["performance"]["score"] * 100,
                        "accessibility": lighthouse_data["categories"]["accessibility"]["score"] * 100,
                        "best-practices": lighthouse_data["categories"]["best-practices"]["score"] * 100,
                        "seo": lighthouse_data["categories"]["seo"]["score"] * 100
                    }
                    
                    # 检查阈值
                    passed = True
                    for category, score in scores.items():
                        threshold = thresholds.get(category, 0)
                        if score < threshold:
                            passed = False
                            self.log_result("lighthouse", "warning", 
                                          f"{url} {category} 得分 {score:.1f} 低于阈值 {threshold}")
                    
                    if passed:
                        self.log_result("lighthouse", "success", f"{url} 性能测试通过")
                    
                    # 保存性能数据
                    self.performance_data[url] = scores
                else:
                    self.log_result("lighthouse", "error", f"{url} Lighthouse测试失败: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            self.log_result("lighthouse", "error", f"Lighthouse执行异常: {e}")
            return False
    
    def _run_npm_audit(self) -> bool:
        """运行npm安全审计"""
        try:
            result = subprocess.run(["npm", "audit", "--audit-level", "moderate"], 
                                  cwd=self.root_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_result("npm_audit", "success", "npm安全审计通过")
                return True
            else:
                # 解析审计结果
                if "vulnerabilities" in result.stdout:
                    self.log_result("npm_audit", "warning", f"发现安全漏洞: {result.stdout}")
                else:
                    self.log_result("npm_audit", "error", f"npm审计失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_result("npm_audit", "error", f"npm审计异常: {e}")
            return False
    
    def _parse_jest_results(self, output: str, test_type: str):
        """解析Jest测试结果"""
        try:
            # 提取测试统计信息
            lines = output.split('\n')
            for line in lines:
                if "Tests:" in line:
                    # 解析测试数量
                    match = re.search(r'(\d+) passed.*?(\d+) total', line)
                    if match:
                        passed = int(match.group(1))
                        total = int(match.group(2))
                        failed = total - passed
                        
                        self.test_results[-1]["details"] = {
                            "passed": passed,
                            "failed": failed,
                            "total": total,
                            "success_rate": (passed / total) * 100 if total > 0 else 0
                        }
                        break
        except Exception as e:
            self.log_result("parse_results", "warning", f"结果解析失败: {e}")
    
    def generate_report(self) -> Dict:
        """生成测试报告"""
        print("📊 生成测试报告")
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "success"])
        failed_tests = len([r for r in self.test_results if r["status"] == "error"])
        warning_tests = len([r for r in self.test_results if r["status"] == "warning"])
        
        report = {
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "results": self.test_results,
            "coverage": self.coverage_data,
            "performance": self.performance_data
        }
        
        # 保存报告
        reporting_config = self.config.get("reporting", {})
        output_dir = Path(reporting_config.get("output_dir", "test-results"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        formats = reporting_config.get("formats", ["json"])
        
        if "json" in formats:
            json_file = output_dir / "test-report.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        if "html" in formats:
            self._generate_html_report(report, output_dir)
        
        self.log_result("generate_report", "success", f"测试报告已生成: {output_dir}")
        return report
    
    def _generate_html_report(self, report: Dict, output_dir: Path):
        """生成HTML测试报告"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>测试报告 - {self.config.get('project', {}).get('name', 'Unknown')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .success {{ color: #28a745; }}
                .error {{ color: #dc3545; }}
                .warning {{ color: #ffc107; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .status-success {{ background-color: #d4edda; }}
                .status-error {{ background-color: #f8d7da; }}
                .status-warning {{ background-color: #fff3cd; }}
            </style>
        </head>
        <body>
            <h1>测试报告</h1>
            
            <div class="summary">
                <h2>测试摘要</h2>
                <p><strong>总测试数:</strong> {report['summary']['total']}</p>
                <p><strong>通过:</strong> <span class="success">{report['summary']['passed']}</span></p>
                <p><strong>失败:</strong> <span class="error">{report['summary']['failed']}</span></p>
                <p><strong>警告:</strong> <span class="warning">{report['summary']['warnings']}</span></p>
                <p><strong>成功率:</strong> {report['summary']['success_rate']:.1f}%</p>
                <p><strong>生成时间:</strong> {report['summary']['timestamp']}</p>
            </div>
            
            <h2>详细结果</h2>
            <table>
                <thead>
                    <tr>
                        <th>测试类型</th>
                        <th>状态</th>
                        <th>消息</th>
                        <th>时间</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for result in report['results']:
            status_class = f"status-{result['status']}"
            html_content += f"""
                    <tr class="{status_class}">
                        <td>{result['test_type']}</td>
                        <td>{result['status']}</td>
                        <td>{result['message']}</td>
                        <td>{result['timestamp']}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        html_file = output_dir / "test-report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def run_tests(self, test_types: List[str], environment: str = "development") -> bool:
        """运行指定类型的测试"""
        print(f"🧪 开始运行测试 - 环境: {environment}")
        print("=" * 60)
        
        # 设置测试环境
        if not self.setup_test_environment(environment):
            return False
        
        # 运行测试
        all_passed = True
        frameworks_config = self.config.get("frameworks", {})
        
        for test_type in test_types:
            if test_type not in self.test_types:
                self.log_result("run_tests", "error", f"不支持的测试类型: {test_type}")
                all_passed = False
                continue
            
            config = frameworks_config.get(test_type, {})
            if not config:
                self.log_result("run_tests", "warning", f"测试类型 {test_type} 未配置")
                continue
            
            print(f"\n🔍 运行 {test_type} 测试")
            test_func = self.test_types[test_type]
            
            try:
                result = test_func(config)
                if not result:
                    all_passed = False
            except Exception as e:
                self.log_result(test_type, "error", f"测试执行异常: {e}")
                all_passed = False
        
        # 生成报告
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        if all_passed:
            print("🎉 所有测试通过！")
        else:
            print("❌ 部分测试失败")
        
        print(f"📊 测试摘要: {report['summary']['passed']}/{report['summary']['total']} 通过")
        
        return all_passed

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动化测试运行器")
    parser.add_argument(
        "--types",
        nargs="+",
        choices=["unit", "integration", "e2e", "performance", "security", "accessibility", "visual", "api"],
        default=["unit"],
        help="要运行的测试类型"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        default="development",
        help="测试环境"
    )
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="并行运行测试"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="生成覆盖率报告"
    )
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = TestRunner(args.config)
    
    # 运行测试
    success = runner.run_tests(args.types, args.environment)
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()