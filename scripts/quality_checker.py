#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化代码质量检查脚本
支持多种编程语言的代码质量检查，包括语法检查、风格检查、安全检查等
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import ast
from collections import defaultdict

@dataclass
class QualityIssue:
    """代码质量问题数据结构"""
    file_path: str
    line_number: int
    column: int = 0
    severity: str = "info"  # error, warning, info
    category: str = "style"  # syntax, style, security, performance, maintainability
    rule_id: str = ""
    message: str = ""
    suggestion: str = ""
    tool: str = ""
    fixable: bool = False

@dataclass
class QualityReport:
    """质量检查报告数据结构"""
    project_name: str
    scan_time: str
    total_files: int
    scanned_files: int
    issues: List[QualityIssue]
    summary: Dict[str, int]
    tools_used: List[str]
    execution_time: float
    config_used: str

class CodeQualityChecker:
    """代码质量检查器主类"""
    
    def __init__(self, config_path: str = None):
        self.root_path = Path(".").resolve()
        self.config_path = config_path or self.root_path / "config" / "quality.yaml"
        self.config = self._load_config()
        
        # 支持的工具和语言
        self.language_tools = {
            'python': {
                'syntax': ['python', 'pyflakes'],
                'style': ['flake8', 'pylint', 'black', 'isort'],
                'security': ['bandit', 'safety'],
                'complexity': ['radon', 'mccabe'],
                'type_check': ['mypy', 'pyright']
            },
            'javascript': {
                'syntax': ['node'],
                'style': ['eslint', 'prettier'],
                'security': ['eslint-plugin-security'],
                'type_check': ['tsc']
            },
            'typescript': {
                'syntax': ['tsc'],
                'style': ['eslint', 'prettier'],
                'security': ['eslint-plugin-security'],
                'type_check': ['tsc']
            },
            'java': {
                'syntax': ['javac'],
                'style': ['checkstyle', 'spotbugs'],
                'security': ['spotbugs']
            },
            'go': {
                'syntax': ['go'],
                'style': ['gofmt', 'golint', 'go vet'],
                'security': ['gosec']
            },
            'rust': {
                'syntax': ['rustc'],
                'style': ['rustfmt', 'clippy']
            },
            'cpp': {
                'syntax': ['gcc', 'clang'],
                'style': ['clang-format', 'cppcheck']
            }
        }
        
        # 文件扩展名映射
        self.extension_language = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp'
        }
        
        # 配置日志
        log_level = self.config.get("logging", {}).get("level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _load_config(self) -> Dict:
        """加载质量检查配置"""
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
        """创建默认质量检查配置"""
        default_config = {
            "project": {
                "name": "New Energy Coder Club",
                "version": "1.0.0",
                "description": "新能源编程俱乐部代码质量检查"
            },
            "scan": {
                "directories": ["./src", "./api", "./scripts"],
                "exclude_patterns": [
                    "*.pyc", "__pycache__", ".git", "node_modules",
                    "*.log", "*.tmp", ".env", "dist", "build",
                    "*.min.js", "*.bundle.js", "coverage"
                ],
                "include_patterns": [
                    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx",
                    "*.java", "*.go", "*.rs", "*.cpp", "*.c", "*.h"
                ],
                "max_file_size": 1048576,  # 1MB
                "parallel_processing": True,
                "max_workers": 4
            },
            "tools": {
                "python": {
                    "enabled": True,
                    "syntax_check": True,
                    "style_check": True,
                    "security_check": True,
                    "complexity_check": True,
                    "type_check": False,
                    "tools": {
                        "flake8": {
                            "enabled": True,
                            "config": ".flake8",
                            "max_line_length": 88,
                            "ignore": ["E203", "W503"]
                        },
                        "pylint": {
                            "enabled": True,
                            "config": ".pylintrc",
                            "disable": ["C0114", "C0115", "C0116"]
                        },
                        "black": {
                            "enabled": True,
                            "line_length": 88,
                            "check_only": True
                        },
                        "isort": {
                            "enabled": True,
                            "profile": "black",
                            "check_only": True
                        },
                        "bandit": {
                            "enabled": True,
                            "config": ".bandit",
                            "skip_tests": True
                        },
                        "mypy": {
                            "enabled": False,
                            "config": "mypy.ini",
                            "strict": False
                        }
                    }
                },
                "javascript": {
                    "enabled": True,
                    "syntax_check": True,
                    "style_check": True,
                    "security_check": True,
                    "tools": {
                        "eslint": {
                            "enabled": True,
                            "config": ".eslintrc.js",
                            "fix": False
                        },
                        "prettier": {
                            "enabled": True,
                            "config": ".prettierrc",
                            "check_only": True
                        }
                    }
                },
                "typescript": {
                    "enabled": True,
                    "syntax_check": True,
                    "style_check": True,
                    "type_check": True,
                    "tools": {
                        "tsc": {
                            "enabled": True,
                            "config": "tsconfig.json",
                            "no_emit": True
                        },
                        "eslint": {
                            "enabled": True,
                            "config": ".eslintrc.js"
                        }
                    }
                }
            },
            "thresholds": {
                "error_threshold": 0,
                "warning_threshold": 10,
                "complexity_threshold": 10,
                "coverage_threshold": 80
            },
            "output": {
                "directory": "./reports/quality",
                "formats": ["json", "html", "console"],
                "detailed_report": True,
                "include_suggestions": True
            },
            "notifications": {
                "enabled": False,
                "webhook_url": "{{QUALITY_WEBHOOK_URL}}",
                "email": {
                    "enabled": False,
                    "recipients": ["{{TEAM_EMAIL}}"]
                }
            },
            "logging": {
                "level": "INFO",
                "file": "quality_checker.log"
            }
        }
        
        # 保存默认配置
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            logging.info("默认质量检查配置已创建")
        except Exception as e:
            logging.error(f"配置创建失败: {e}")
        
        return default_config
    
    def scan_project(self, target_paths: List[str] = None) -> QualityReport:
        """扫描项目代码质量"""
        start_time = datetime.now()
        
        # 确定扫描路径
        if not target_paths:
            target_paths = self.config.get("scan", {}).get("directories", ["."])
        
        # 收集文件
        files_to_scan = self._collect_files(target_paths)
        
        logging.info(f"开始扫描 {len(files_to_scan)} 个文件")
        
        # 执行扫描
        all_issues = []
        tools_used = set()
        
        if self.config.get("scan", {}).get("parallel_processing", True):
            # 并行扫描
            max_workers = self.config.get("scan", {}).get("max_workers", 4)
            all_issues, tools_used = self._scan_files_parallel(files_to_scan, max_workers)
        else:
            # 串行扫描
            all_issues, tools_used = self._scan_files_sequential(files_to_scan)
        
        # 生成报告
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        report = QualityReport(
            project_name=self.config.get("project", {}).get("name", "Unknown"),
            scan_time=start_time.isoformat(),
            total_files=len(files_to_scan),
            scanned_files=len([f for f in files_to_scan if self._should_scan_file(f)]),
            issues=all_issues,
            summary=self._generate_summary(all_issues),
            tools_used=list(tools_used),
            execution_time=execution_time,
            config_used=str(self.config_path)
        )
        
        logging.info(f"扫描完成，发现 {len(all_issues)} 个问题")
        
        return report
    
    def _collect_files(self, target_paths: List[str]) -> List[Path]:
        """收集需要扫描的文件"""
        files = []
        include_patterns = self.config.get("scan", {}).get("include_patterns", [])
        exclude_patterns = self.config.get("scan", {}).get("exclude_patterns", [])
        max_file_size = self.config.get("scan", {}).get("max_file_size", 1048576)
        
        for target_path in target_paths:
            path = Path(target_path)
            
            if path.is_file():
                if self._should_include_file(path, include_patterns, exclude_patterns, max_file_size):
                    files.append(path)
            elif path.is_dir():
                for file_path in path.rglob("*"):
                    if file_path.is_file() and self._should_include_file(
                        file_path, include_patterns, exclude_patterns, max_file_size
                    ):
                        files.append(file_path)
        
        return files
    
    def _should_include_file(self, file_path: Path, include_patterns: List[str], 
                           exclude_patterns: List[str], max_file_size: int) -> bool:
        """判断是否应该包含文件"""
        # 检查文件大小
        try:
            if file_path.stat().st_size > max_file_size:
                return False
        except OSError:
            return False
        
        # 检查排除模式
        for pattern in exclude_patterns:
            if file_path.match(pattern) or pattern in str(file_path):
                return False
        
        # 检查包含模式
        if include_patterns:
            for pattern in include_patterns:
                if file_path.match(pattern):
                    return True
            return False
        
        # 检查是否为支持的文件类型
        return file_path.suffix in self.extension_language
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """判断是否应该扫描文件"""
        language = self.extension_language.get(file_path.suffix)
        if not language:
            return False
        
        language_config = self.config.get("tools", {}).get(language, {})
        return language_config.get("enabled", False)
    
    def _scan_files_parallel(self, files: List[Path], max_workers: int) -> Tuple[List[QualityIssue], set]:
        """并行扫描文件"""
        all_issues = []
        tools_used = set()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self._scan_single_file, file_path): file_path
                for file_path in files
                if self._should_scan_file(file_path)
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    issues, file_tools = future.result()
                    all_issues.extend(issues)
                    tools_used.update(file_tools)
                except Exception as e:
                    logging.error(f"扫描文件失败 {file_path}: {e}")
        
        return all_issues, tools_used
    
    def _scan_files_sequential(self, files: List[Path]) -> Tuple[List[QualityIssue], set]:
        """串行扫描文件"""
        all_issues = []
        tools_used = set()
        
        for file_path in files:
            if self._should_scan_file(file_path):
                try:
                    issues, file_tools = self._scan_single_file(file_path)
                    all_issues.extend(issues)
                    tools_used.update(file_tools)
                except Exception as e:
                    logging.error(f"扫描文件失败 {file_path}: {e}")
        
        return all_issues, tools_used
    
    def _scan_single_file(self, file_path: Path) -> Tuple[List[QualityIssue], set]:
        """扫描单个文件"""
        language = self.extension_language.get(file_path.suffix)
        if not language:
            return [], set()
        
        language_config = self.config.get("tools", {}).get(language, {})
        if not language_config.get("enabled", False):
            return [], set()
        
        issues = []
        tools_used = set()
        
        # 语法检查
        if language_config.get("syntax_check", True):
            syntax_issues, syntax_tools = self._check_syntax(file_path, language)
            issues.extend(syntax_issues)
            tools_used.update(syntax_tools)
        
        # 风格检查
        if language_config.get("style_check", True):
            style_issues, style_tools = self._check_style(file_path, language)
            issues.extend(style_issues)
            tools_used.update(style_tools)
        
        # 安全检查
        if language_config.get("security_check", False):
            security_issues, security_tools = self._check_security(file_path, language)
            issues.extend(security_issues)
            tools_used.update(security_tools)
        
        # 复杂度检查
        if language_config.get("complexity_check", False):
            complexity_issues, complexity_tools = self._check_complexity(file_path, language)
            issues.extend(complexity_issues)
            tools_used.update(complexity_tools)
        
        # 类型检查
        if language_config.get("type_check", False):
            type_issues, type_tools = self._check_types(file_path, language)
            issues.extend(type_issues)
            tools_used.update(type_tools)
        
        return issues, tools_used
    
    def _check_syntax(self, file_path: Path, language: str) -> Tuple[List[QualityIssue], set]:
        """语法检查"""
        issues = []
        tools_used = set()
        
        try:
            if language == 'python':
                # Python语法检查
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    issue = QualityIssue(
                        file_path=str(file_path),
                        line_number=e.lineno or 1,
                        column=e.offset or 0,
                        severity="error",
                        category="syntax",
                        rule_id="E999",
                        message=f"语法错误: {e.msg}",
                        tool="python",
                        fixable=False
                    )
                    issues.append(issue)
                    tools_used.add("python")
            
            elif language in ['javascript', 'typescript']:
                # JavaScript/TypeScript语法检查
                cmd = ['node', '-c', str(file_path)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    # 解析错误信息
                    error_lines = result.stderr.strip().split('\n')
                    for line in error_lines:
                        if 'SyntaxError' in line:
                            issue = QualityIssue(
                                file_path=str(file_path),
                                line_number=1,
                                severity="error",
                                category="syntax",
                                rule_id="syntax-error",
                                message=line,
                                tool="node",
                                fixable=False
                            )
                            issues.append(issue)
                            tools_used.add("node")
        
        except Exception as e:
            logging.error(f"语法检查失败 {file_path}: {e}")
        
        return issues, tools_used
    
    def _check_style(self, file_path: Path, language: str) -> Tuple[List[QualityIssue], set]:
        """风格检查"""
        issues = []
        tools_used = set()
        
        try:
            language_config = self.config.get("tools", {}).get(language, {})
            tools_config = language_config.get("tools", {})
            
            if language == 'python':
                # Flake8检查
                if tools_config.get("flake8", {}).get("enabled", False):
                    flake8_issues = self._run_flake8(file_path, tools_config["flake8"])
                    issues.extend(flake8_issues)
                    if flake8_issues:
                        tools_used.add("flake8")
                
                # Black检查
                if tools_config.get("black", {}).get("enabled", False):
                    black_issues = self._run_black(file_path, tools_config["black"])
                    issues.extend(black_issues)
                    if black_issues:
                        tools_used.add("black")
                
                # isort检查
                if tools_config.get("isort", {}).get("enabled", False):
                    isort_issues = self._run_isort(file_path, tools_config["isort"])
                    issues.extend(isort_issues)
                    if isort_issues:
                        tools_used.add("isort")
            
            elif language in ['javascript', 'typescript']:
                # ESLint检查
                if tools_config.get("eslint", {}).get("enabled", False):
                    eslint_issues = self._run_eslint(file_path, tools_config["eslint"])
                    issues.extend(eslint_issues)
                    if eslint_issues:
                        tools_used.add("eslint")
                
                # Prettier检查
                if tools_config.get("prettier", {}).get("enabled", False):
                    prettier_issues = self._run_prettier(file_path, tools_config["prettier"])
                    issues.extend(prettier_issues)
                    if prettier_issues:
                        tools_used.add("prettier")
        
        except Exception as e:
            logging.error(f"风格检查失败 {file_path}: {e}")
        
        return issues, tools_used
    
    def _check_security(self, file_path: Path, language: str) -> Tuple[List[QualityIssue], set]:
        """安全检查"""
        issues = []
        tools_used = set()
        
        try:
            language_config = self.config.get("tools", {}).get(language, {})
            tools_config = language_config.get("tools", {})
            
            if language == 'python':
                # Bandit安全检查
                if tools_config.get("bandit", {}).get("enabled", False):
                    bandit_issues = self._run_bandit(file_path, tools_config["bandit"])
                    issues.extend(bandit_issues)
                    if bandit_issues:
                        tools_used.add("bandit")
        
        except Exception as e:
            logging.error(f"安全检查失败 {file_path}: {e}")
        
        return issues, tools_used
    
    def _check_complexity(self, file_path: Path, language: str) -> Tuple[List[QualityIssue], set]:
        """复杂度检查"""
        issues = []
        tools_used = set()
        
        try:
            if language == 'python':
                # 使用AST分析复杂度
                complexity_issues = self._analyze_python_complexity(file_path)
                issues.extend(complexity_issues)
                if complexity_issues:
                    tools_used.add("complexity-analyzer")
        
        except Exception as e:
            logging.error(f"复杂度检查失败 {file_path}: {e}")
        
        return issues, tools_used
    
    def _check_types(self, file_path: Path, language: str) -> Tuple[List[QualityIssue], set]:
        """类型检查"""
        issues = []
        tools_used = set()
        
        try:
            language_config = self.config.get("tools", {}).get(language, {})
            tools_config = language_config.get("tools", {})
            
            if language == 'python':
                # MyPy类型检查
                if tools_config.get("mypy", {}).get("enabled", False):
                    mypy_issues = self._run_mypy(file_path, tools_config["mypy"])
                    issues.extend(mypy_issues)
                    if mypy_issues:
                        tools_used.add("mypy")
            
            elif language == 'typescript':
                # TypeScript编译器检查
                if tools_config.get("tsc", {}).get("enabled", False):
                    tsc_issues = self._run_tsc(file_path, tools_config["tsc"])
                    issues.extend(tsc_issues)
                    if tsc_issues:
                        tools_used.add("tsc")
        
        except Exception as e:
            logging.error(f"类型检查失败 {file_path}: {e}")
        
        return issues, tools_used
    
    def _run_flake8(self, file_path: Path, config: Dict) -> List[QualityIssue]:
        """运行Flake8检查"""
        issues = []
        
        try:
            cmd = ['flake8', str(file_path), '--format=json']
            
            # 添加配置参数
            if config.get("max_line_length"):
                cmd.extend(['--max-line-length', str(config["max_line_length"])])
            
            if config.get("ignore"):
                cmd.extend(['--ignore', ','.join(config["ignore"])])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                # 解析JSON输出
                try:
                    data = json.loads(result.stdout)
                    for item in data:
                        issue = QualityIssue(
                            file_path=str(file_path),
                            line_number=item.get('line_number', 1),
                            column=item.get('column_number', 0),
                            severity="warning" if item.get('code', '').startswith('W') else "error",
                            category="style",
                            rule_id=item.get('code', ''),
                            message=item.get('text', ''),
                            tool="flake8",
                            fixable=False
                        )
                        issues.append(issue)
                except json.JSONDecodeError:
                    # 解析文本输出
                    for line in result.stdout.strip().split('\n'):
                        if ':' in line:
                            parts = line.split(':')
                            if len(parts) >= 4:
                                issue = QualityIssue(
                                    file_path=str(file_path),
                                    line_number=int(parts[1]) if parts[1].isdigit() else 1,
                                    column=int(parts[2]) if parts[2].isdigit() else 0,
                                    severity="warning",
                                    category="style",
                                    message=':'.join(parts[3:]).strip(),
                                    tool="flake8",
                                    fixable=False
                                )
                                issues.append(issue)
        
        except FileNotFoundError:
            logging.warning("Flake8未安装，跳过检查")
        except Exception as e:
            logging.error(f"Flake8检查失败: {e}")
        
        return issues
    
    def _run_black(self, file_path: Path, config: Dict) -> List[QualityIssue]:
        """运行Black格式检查"""
        issues = []
        
        try:
            cmd = ['black', '--check', '--diff', str(file_path)]
            
            if config.get("line_length"):
                cmd.extend(['--line-length', str(config["line_length"])])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0 and result.stdout:
                issue = QualityIssue(
                    file_path=str(file_path),
                    line_number=1,
                    severity="info",
                    category="style",
                    rule_id="black-format",
                    message="文件格式不符合Black标准",
                    suggestion="运行 'black {}' 自动格式化".format(file_path),
                    tool="black",
                    fixable=True
                )
                issues.append(issue)
        
        except FileNotFoundError:
            logging.warning("Black未安装，跳过检查")
        except Exception as e:
            logging.error(f"Black检查失败: {e}")
        
        return issues
    
    def _run_isort(self, file_path: Path, config: Dict) -> List[QualityIssue]:
        """运行isort导入排序检查"""
        issues = []
        
        try:
            cmd = ['isort', '--check-only', '--diff', str(file_path)]
            
            if config.get("profile"):
                cmd.extend(['--profile', config["profile"]])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                issue = QualityIssue(
                    file_path=str(file_path),
                    line_number=1,
                    severity="info",
                    category="style",
                    rule_id="isort-imports",
                    message="导入语句排序不正确",
                    suggestion="运行 'isort {}' 自动排序".format(file_path),
                    tool="isort",
                    fixable=True
                )
                issues.append(issue)
        
        except FileNotFoundError:
            logging.warning("isort未安装，跳过检查")
        except Exception as e:
            logging.error(f"isort检查失败: {e}")
        
        return issues
    
    def _run_bandit(self, file_path: Path, config: Dict) -> List[QualityIssue]:
        """运行Bandit安全检查"""
        issues = []
        
        try:
            cmd = ['bandit', '-f', 'json', str(file_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data.get('results', []):
                        severity_map = {
                            'LOW': 'info',
                            'MEDIUM': 'warning',
                            'HIGH': 'error'
                        }
                        
                        issue = QualityIssue(
                            file_path=str(file_path),
                            line_number=item.get('line_number', 1),
                            severity=severity_map.get(item.get('issue_severity', 'LOW'), 'info'),
                            category="security",
                            rule_id=item.get('test_id', ''),
                            message=item.get('issue_text', ''),
                            tool="bandit",
                            fixable=False
                        )
                        issues.append(issue)
                except json.JSONDecodeError:
                    pass
        
        except FileNotFoundError:
            logging.warning("Bandit未安装，跳过检查")
        except Exception as e:
            logging.error(f"Bandit检查失败: {e}")
        
        return issues
    
    def _run_eslint(self, file_path: Path, config: Dict) -> List[QualityIssue]:
        """运行ESLint检查"""
        issues = []
        
        try:
            cmd = ['eslint', '--format', 'json', str(file_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for file_result in data:
                        for message in file_result.get('messages', []):
                            severity_map = {
                                1: 'warning',
                                2: 'error'
                            }
                            
                            issue = QualityIssue(
                                file_path=str(file_path),
                                line_number=message.get('line', 1),
                                column=message.get('column', 0),
                                severity=severity_map.get(message.get('severity', 1), 'warning'),
                                category="style",
                                rule_id=message.get('ruleId', ''),
                                message=message.get('message', ''),
                                tool="eslint",
                                fixable=message.get('fix') is not None
                            )
                            issues.append(issue)
                except json.JSONDecodeError:
                    pass
        
        except FileNotFoundError:
            logging.warning("ESLint未安装，跳过检查")
        except Exception as e:
            logging.error(f"ESLint检查失败: {e}")
        
        return issues
    
    def _run_prettier(self, file_path: Path, config: Dict) -> List[QualityIssue]:
        """运行Prettier格式检查"""
        issues = []
        
        try:
            cmd = ['prettier', '--check', str(file_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                issue = QualityIssue(
                    file_path=str(file_path),
                    line_number=1,
                    severity="info",
                    category="style",
                    rule_id="prettier-format",
                    message="文件格式不符合Prettier标准",
                    suggestion="运行 'prettier --write {}' 自动格式化".format(file_path),
                    tool="prettier",
                    fixable=True
                )
                issues.append(issue)
        
        except FileNotFoundError:
            logging.warning("Prettier未安装，跳过检查")
        except Exception as e:
            logging.error(f"Prettier检查失败: {e}")
        
        return issues
    
    def _run_mypy(self, file_path: Path, config: Dict) -> List[QualityIssue]:
        """运行MyPy类型检查"""
        issues = []
        
        try:
            cmd = ['mypy', '--show-error-codes', str(file_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line and 'error:' in line:
                        parts = line.split(':')
                        if len(parts) >= 3:
                            issue = QualityIssue(
                                file_path=str(file_path),
                                line_number=int(parts[1]) if parts[1].isdigit() else 1,
                                severity="error",
                                category="type",
                                message=':'.join(parts[2:]).strip(),
                                tool="mypy",
                                fixable=False
                            )
                            issues.append(issue)
        
        except FileNotFoundError:
            logging.warning("MyPy未安装，跳过检查")
        except Exception as e:
            logging.error(f"MyPy检查失败: {e}")
        
        return issues
    
    def _run_tsc(self, file_path: Path, config: Dict) -> List[QualityIssue]:
        """运行TypeScript编译器检查"""
        issues = []
        
        try:
            cmd = ['tsc', '--noEmit', str(file_path)]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if '(' in line and ')' in line:
                        # 解析TypeScript错误格式
                        match = re.search(r'\((\d+),(\d+)\):', line)
                        if match:
                            line_num = int(match.group(1))
                            col_num = int(match.group(2))
                            message = line.split('): ', 1)[-1] if '): ' in line else line
                            
                            issue = QualityIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                column=col_num,
                                severity="error",
                                category="type",
                                message=message,
                                tool="tsc",
                                fixable=False
                            )
                            issues.append(issue)
        
        except FileNotFoundError:
            logging.warning("TypeScript编译器未安装，跳过检查")
        except Exception as e:
            logging.error(f"TypeScript检查失败: {e}")
        
        return issues
    
    def _analyze_python_complexity(self, file_path: Path) -> List[QualityIssue]:
        """分析Python代码复杂度"""
        issues = []
        complexity_threshold = self.config.get("thresholds", {}).get("complexity_threshold", 10)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    
                    if complexity > complexity_threshold:
                        issue = QualityIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            severity="warning" if complexity <= complexity_threshold * 1.5 else "error",
                            category="maintainability",
                            rule_id="high-complexity",
                            message=f"函数 '{node.name}' 的圈复杂度过高: {complexity}",
                            suggestion=f"建议将复杂度降低到 {complexity_threshold} 以下",
                            tool="complexity-analyzer",
                            fixable=False
                        )
                        issues.append(issue)
        
        except Exception as e:
            logging.error(f"复杂度分析失败 {file_path}: {e}")
        
        return issues
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度"""
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # and/or 操作符增加复杂度
                complexity += len(child.values) - 1
        
        return complexity
    
    def _generate_summary(self, issues: List[QualityIssue]) -> Dict[str, int]:
        """生成问题摘要"""
        summary = {
            "total": len(issues),
            "error": 0,
            "warning": 0,
            "info": 0,
            "fixable": 0,
            "by_category": defaultdict(int),
            "by_tool": defaultdict(int)
        }
        
        for issue in issues:
            summary[issue.severity] += 1
            
            if issue.fixable:
                summary["fixable"] += 1
            
            summary["by_category"][issue.category] += 1
            summary["by_tool"][issue.tool] += 1
        
        # 转换defaultdict为普通dict
        summary["by_category"] = dict(summary["by_category"])
        summary["by_tool"] = dict(summary["by_tool"])
        
        return summary
    
    def generate_report(self, report: QualityReport, output_formats: List[str] = None) -> Dict[str, str]:
        """生成质量报告"""
        if not output_formats:
            output_formats = self.config.get("output", {}).get("formats", ["console"])
        
        output_dir = Path(self.config.get("output", {}).get("directory", "./reports/quality"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        for format_type in output_formats:
            if format_type == "json":
                json_file = output_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self._generate_json_report(report, json_file)
                generated_files["json"] = str(json_file)
            
            elif format_type == "html":
                html_file = output_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                self._generate_html_report(report, html_file)
                generated_files["html"] = str(html_file)
            
            elif format_type == "console":
                self._generate_console_report(report)
                generated_files["console"] = "控制台输出"
        
        return generated_files
    
    def _generate_json_report(self, report: QualityReport, output_file: Path):
        """生成JSON格式报告"""
        try:
            report_data = asdict(report)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            logging.info(f"JSON报告已生成: {output_file}")
        
        except Exception as e:
            logging.error(f"生成JSON报告失败: {e}")
    
    def _generate_html_report(self, report: QualityReport, output_file: Path):
        """生成HTML格式报告"""
        try:
            html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码质量报告 - {project_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
        .metric {{ background: white; padding: 15px; border: 1px solid #ddd; border-radius: 5px; flex: 1; }}
        .metric h3 {{ margin: 0 0 10px 0; }}
        .metric .value {{ font-size: 24px; font-weight: bold; }}
        .error {{ color: #d32f2f; }}
        .warning {{ color: #f57c00; }}
        .info {{ color: #1976d2; }}
        .issues {{ margin: 20px 0; }}
        .issue {{ background: white; border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .issue-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .issue-file {{ font-weight: bold; }}
        .issue-location {{ color: #666; }}
        .issue-message {{ margin: 10px 0; }}
        .issue-suggestion {{ background: #f0f8ff; padding: 10px; border-radius: 3px; margin-top: 10px; }}
        .badge {{ padding: 3px 8px; border-radius: 3px; color: white; font-size: 12px; }}
        .badge.error {{ background: #d32f2f; }}
        .badge.warning {{ background: #f57c00; }}
        .badge.info {{ background: #1976d2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>代码质量报告</h1>
        <p><strong>项目:</strong> {project_name}</p>
        <p><strong>扫描时间:</strong> {scan_time}</p>
        <p><strong>扫描文件:</strong> {scanned_files}/{total_files}</p>
        <p><strong>执行时间:</strong> {execution_time:.2f}秒</p>
        <p><strong>使用工具:</strong> {tools_used}</p>
    </div>
    
    <div class="summary">
        <div class="metric">
            <h3>总问题数</h3>
            <div class="value">{total_issues}</div>
        </div>
        <div class="metric">
            <h3 class="error">错误</h3>
            <div class="value error">{error_count}</div>
        </div>
        <div class="metric">
            <h3 class="warning">警告</h3>
            <div class="value warning">{warning_count}</div>
        </div>
        <div class="metric">
            <h3 class="info">信息</h3>
            <div class="value info">{info_count}</div>
        </div>
        <div class="metric">
            <h3>可修复</h3>
            <div class="value">{fixable_count}</div>
        </div>
    </div>
    
    <div class="issues">
        <h2>问题详情</h2>
        {issues_html}
    </div>
</body>
</html>
            """
            
            # 生成问题HTML
            issues_html = ""
            for issue in report.issues:
                suggestion_html = ""
                if issue.suggestion:
                    suggestion_html = f'<div class="issue-suggestion"><strong>建议:</strong> {issue.suggestion}</div>'
                
                issue_html = f"""
                <div class="issue">
                    <div class="issue-header">
                        <div>
                            <div class="issue-file">{issue.file_path}</div>
                            <div class="issue-location">行 {issue.line_number}, 列 {issue.column}</div>
                        </div>
                        <div>
                            <span class="badge {issue.severity}">{issue.severity.upper()}</span>
                            <span class="badge info">{issue.category}</span>
                            <span class="badge info">{issue.tool}</span>
                        </div>
                    </div>
                    <div class="issue-message">
                        <strong>{issue.rule_id}:</strong> {issue.message}
                    </div>
                    {suggestion_html}
                </div>
                """
                issues_html += issue_html
            
            # 填充模板
            html_content = html_template.format(
                project_name=report.project_name,
                scan_time=report.scan_time,
                scanned_files=report.scanned_files,
                total_files=report.total_files,
                execution_time=report.execution_time,
                tools_used=", ".join(report.tools_used),
                total_issues=report.summary["total"],
                error_count=report.summary["error"],
                warning_count=report.summary["warning"],
                info_count=report.summary["info"],
                fixable_count=report.summary["fixable"],
                issues_html=issues_html
            )
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logging.info(f"HTML报告已生成: {output_file}")
        
        except Exception as e:
            logging.error(f"生成HTML报告失败: {e}")
    
    def _generate_console_report(self, report: QualityReport):
        """生成控制台格式报告"""
        try:
            print("\n" + "="*80)
            print(f"📊 代码质量报告 - {report.project_name}")
            print("="*80)
            
            print(f"⏰ 扫描时间: {report.scan_time}")
            print(f"📁 扫描文件: {report.scanned_files}/{report.total_files}")
            print(f"⚡ 执行时间: {report.execution_time:.2f}秒")
            print(f"🔧 使用工具: {', '.join(report.tools_used)}")
            
            print("\n📈 问题统计:")
            print(f"  总计: {report.summary['total']}")
            print(f"  ❌ 错误: {report.summary['error']}")
            print(f"  ⚠️  警告: {report.summary['warning']}")
            print(f"  ℹ️  信息: {report.summary['info']}")
            print(f"  🔧 可修复: {report.summary['fixable']}")
            
            if report.summary.get("by_category"):
                print("\n📂 按类别统计:")
                for category, count in report.summary["by_category"].items():
                    print(f"  {category}: {count}")
            
            if report.summary.get("by_tool"):
                print("\n🔧 按工具统计:")
                for tool, count in report.summary["by_tool"].items():
                    print(f"  {tool}: {count}")
            
            # 显示前10个问题
            if report.issues:
                print("\n🔍 主要问题 (前10个):")
                for i, issue in enumerate(report.issues[:10], 1):
                    severity_icon = {
                        "error": "❌",
                        "warning": "⚠️",
                        "info": "ℹ️"
                    }.get(issue.severity, "•")
                    
                    print(f"\n{i}. {severity_icon} {issue.file_path}:{issue.line_number}")
                    print(f"   [{issue.tool}] {issue.rule_id}: {issue.message}")
                    
                    if issue.suggestion:
                        print(f"   💡 建议: {issue.suggestion}")
            
            # 质量评估
            print("\n🎯 质量评估:")
            error_threshold = self.config.get("thresholds", {}).get("error_threshold", 0)
            warning_threshold = self.config.get("thresholds", {}).get("warning_threshold", 10)
            
            if report.summary["error"] > error_threshold:
                print("  ❌ 质量不合格 - 存在错误需要修复")
            elif report.summary["warning"] > warning_threshold:
                print("  ⚠️  质量一般 - 建议修复警告")
            else:
                print("  ✅ 质量良好 - 符合标准")
            
            print("\n" + "="*80)
        
        except Exception as e:
            logging.error(f"生成控制台报告失败: {e}")
    
    def fix_issues(self, report: QualityReport, auto_fix: bool = False) -> int:
        """修复可修复的问题"""
        fixed_count = 0
        
        fixable_issues = [issue for issue in report.issues if issue.fixable]
        
        if not fixable_issues:
            logging.info("没有可自动修复的问题")
            return 0
        
        logging.info(f"发现 {len(fixable_issues)} 个可修复问题")
        
        for issue in fixable_issues:
            try:
                if issue.tool == "black" and auto_fix:
                    # 自动运行Black格式化
                    cmd = ['black', issue.file_path]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        logging.info(f"已修复格式问题: {issue.file_path}")
                        fixed_count += 1
                
                elif issue.tool == "isort" and auto_fix:
                    # 自动运行isort排序
                    cmd = ['isort', issue.file_path]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        logging.info(f"已修复导入排序: {issue.file_path}")
                        fixed_count += 1
                
                elif issue.tool == "prettier" and auto_fix:
                    # 自动运行Prettier格式化
                    cmd = ['prettier', '--write', issue.file_path]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        logging.info(f"已修复格式问题: {issue.file_path}")
                        fixed_count += 1
                
                else:
                    # 显示修复建议
                    if not auto_fix:
                        print(f"💡 {issue.file_path}:{issue.line_number} - {issue.suggestion}")
            
            except Exception as e:
                logging.error(f"修复问题失败 {issue.file_path}: {e}")
        
        if auto_fix:
            logging.info(f"自动修复完成，共修复 {fixed_count} 个问题")
        
        return fixed_count

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="代码质量检查系统")
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    parser.add_argument(
        "--path",
        nargs="+",
        help="要扫描的路径"
    )
    parser.add_argument(
        "--format",
        choices=["json", "html", "console"],
        nargs="+",
        default=["console"],
        help="报告格式"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
       help="自动修复可修复的问题"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化默认配置文件"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    try:
        # 创建质量检查器
        checker = CodeQualityChecker(args.config)
        
        # 初始化配置
        if args.init:
            print("✅ 默认配置文件已创建")
            return 0
        
        # 设置日志级别
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # 执行扫描
        report = checker.scan_project(args.path)
        
        # 生成报告
        generated_files = checker.generate_report(report, args.format)
        
        # 自动修复
        if args.fix:
            fixed_count = checker.fix_issues(report, auto_fix=True)
            print(f"\n🔧 自动修复完成，共修复 {fixed_count} 个问题")
        
        # 返回退出码
        error_threshold = checker.config.get("thresholds", {}).get("error_threshold", 0)
        if report.summary["error"] > error_threshold:
            return 1  # 存在错误
        
        return 0
    
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        return 130
    except Exception as e:
        logging.error(f"执行失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())