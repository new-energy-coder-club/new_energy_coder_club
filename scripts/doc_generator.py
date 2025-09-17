#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化文档生成脚本
支持API文档、代码文档、项目文档等多种文档类型的自动生成
"""

import os
import sys
import json
import yaml
import re
import ast
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import markdown
from jinja2 import Template, Environment, FileSystemLoader
import requests
from urllib.parse import urljoin

@dataclass
class DocumentConfig:
    """文档配置数据结构"""
    name: str
    type: str  # api, code, project, readme, changelog
    source_paths: List[str]
    output_path: str
    template_path: str = None
    format: str = "markdown"  # markdown, html, pdf, json
    language: str = "zh-CN"
    include_private: bool = False
    include_tests: bool = False
    auto_update: bool = True
    metadata: Dict[str, Any] = None

@dataclass
class CodeElement:
    """代码元素数据结构"""
    name: str
    type: str  # class, function, method, variable, constant
    file_path: str
    line_number: int
    docstring: str = None
    signature: str = None
    parameters: List[Dict] = None
    return_type: str = None
    decorators: List[str] = None
    access_level: str = "public"  # public, private, protected
    examples: List[str] = None
    related_elements: List[str] = None

@dataclass
class APIEndpoint:
    """API端点数据结构"""
    path: str
    method: str
    summary: str
    description: str = None
    parameters: List[Dict] = None
    request_body: Dict = None
    responses: Dict = None
    tags: List[str] = None
    deprecated: bool = False
    examples: List[Dict] = None

class CodeAnalyzer:
    """代码分析器"""
    
    def __init__(self):
        self.supported_extensions = {
            '.py': self._analyze_python,
            '.js': self._analyze_javascript,
            '.ts': self._analyze_typescript,
            '.java': self._analyze_java,
            '.cpp': self._analyze_cpp,
            '.c': self._analyze_c,
            '.go': self._analyze_go,
            '.rs': self._analyze_rust
        }
    
    def analyze_file(self, file_path: Path) -> List[CodeElement]:
        """分析单个文件"""
        try:
            if file_path.suffix not in self.supported_extensions:
                logging.warning(f"不支持的文件类型: {file_path}")
                return []
            
            analyzer = self.supported_extensions[file_path.suffix]
            return analyzer(file_path)
            
        except Exception as e:
            logging.error(f"分析文件失败 {file_path}: {e}")
            return []
    
    def analyze_directory(self, dir_path: Path, 
                         include_private: bool = False,
                         include_tests: bool = False) -> List[CodeElement]:
        """分析目录中的所有代码文件"""
        elements = []
        
        for file_path in dir_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            # 跳过测试文件
            if not include_tests and self._is_test_file(file_path):
                continue
            
            # 跳过私有文件
            if not include_private and self._is_private_file(file_path):
                continue
            
            file_elements = self.analyze_file(file_path)
            elements.extend(file_elements)
        
        return elements
    
    def _is_test_file(self, file_path: Path) -> bool:
        """判断是否为测试文件"""
        test_patterns = [
            'test_*.py', '*_test.py', 'test*.js', '*.test.js',
            '*.spec.js', '*.test.ts', '*.spec.ts', 'Test*.java',
            '*Test.java', '*_test.go', '*_test.cpp'
        ]
        
        for pattern in test_patterns:
            if file_path.match(pattern):
                return True
        
        return 'test' in str(file_path).lower()
    
    def _is_private_file(self, file_path: Path) -> bool:
        """判断是否为私有文件"""
        # 以下划线开头的文件通常是私有的
        if file_path.name.startswith('_') and not file_path.name.startswith('__'):
            return True
        
        # 在私有目录中的文件
        private_dirs = ['private', 'internal', '.git', 'node_modules', '__pycache__']
        for part in file_path.parts:
            if part in private_dirs or part.startswith('.'):
                return True
        
        return False
    
    def _analyze_python(self, file_path: Path) -> List[CodeElement]:
        """分析Python文件"""
        elements = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    element = self._extract_python_class(node, file_path)
                    elements.append(element)
                    
                    # 分析类方法
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_element = self._extract_python_function(
                                item, file_path, parent_class=node.name
                            )
                            elements.append(method_element)
                
                elif isinstance(node, ast.FunctionDef):
                    # 只处理模块级函数
                    if not any(isinstance(parent, ast.ClassDef) 
                             for parent in ast.walk(tree) 
                             if node in getattr(parent, 'body', [])):
                        element = self._extract_python_function(node, file_path)
                        elements.append(element)
                
                elif isinstance(node, ast.Assign):
                    # 提取模块级变量
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            element = self._extract_python_variable(
                                target, node, file_path
                            )
                            if element:
                                elements.append(element)
        
        except Exception as e:
            logging.error(f"分析Python文件失败 {file_path}: {e}")
        
        return elements
    
    def _extract_python_class(self, node: ast.ClassDef, file_path: Path) -> CodeElement:
        """提取Python类信息"""
        docstring = ast.get_docstring(node) or ""
        
        # 提取装饰器
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(f"{decorator.attr}")
        
        # 提取基类
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(f"{base.attr}")
        
        signature = f"class {node.name}"
        if bases:
            signature += f"({', '.join(bases)})"
        
        return CodeElement(
            name=node.name,
            type="class",
            file_path=str(file_path),
            line_number=node.lineno,
            docstring=docstring,
            signature=signature,
            decorators=decorators,
            access_level="private" if node.name.startswith('_') else "public"
        )
    
    def _extract_python_function(self, node: ast.FunctionDef, file_path: Path, 
                                parent_class: str = None) -> CodeElement:
        """提取Python函数/方法信息"""
        docstring = ast.get_docstring(node) or ""
        
        # 提取参数
        parameters = []
        for arg in node.args.args:
            param_info = {
                "name": arg.arg,
                "type": getattr(arg.annotation, 'id', None) if arg.annotation else None,
                "default": None
            }
            parameters.append(param_info)
        
        # 提取默认参数
        defaults = node.args.defaults
        if defaults:
            for i, default in enumerate(defaults):
                param_index = len(parameters) - len(defaults) + i
                if param_index >= 0 and param_index < len(parameters):
                    parameters[param_index]["default"] = ast.unparse(default)
        
        # 提取返回类型
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)
        
        # 提取装饰器
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(f"{decorator.attr}")
        
        # 构建签名
        param_strs = []
        for param in parameters:
            param_str = param["name"]
            if param["type"]:
                param_str += f": {param['type']}"
            if param["default"]:
                param_str += f" = {param['default']}"
            param_strs.append(param_str)
        
        signature = f"def {node.name}({', '.join(param_strs)})"
        if return_type:
            signature += f" -> {return_type}"
        
        element_type = "method" if parent_class else "function"
        access_level = "private" if node.name.startswith('_') else "public"
        
        return CodeElement(
            name=node.name,
            type=element_type,
            file_path=str(file_path),
            line_number=node.lineno,
            docstring=docstring,
            signature=signature,
            parameters=parameters,
            return_type=return_type,
            decorators=decorators,
            access_level=access_level
        )
    
    def _extract_python_variable(self, target: ast.Name, node: ast.Assign, 
                                file_path: Path) -> Optional[CodeElement]:
        """提取Python变量信息"""
        try:
            name = target.id
            
            # 跳过私有变量（除非是常量）
            if name.startswith('_') and not name.isupper():
                return None
            
            # 尝试获取值
            value = None
            if len(node.targets) == 1 and isinstance(node.value, (ast.Constant, ast.Str, ast.Num)):
                try:
                    value = ast.unparse(node.value)
                except:
                    value = str(node.value)
            
            element_type = "constant" if name.isupper() else "variable"
            
            return CodeElement(
                name=name,
                type=element_type,
                file_path=str(file_path),
                line_number=node.lineno,
                signature=f"{name} = {value}" if value else name,
                access_level="private" if name.startswith('_') else "public"
            )
            
        except Exception as e:
            logging.warning(f"提取变量信息失败: {e}")
            return None
    
    def _analyze_javascript(self, file_path: Path) -> List[CodeElement]:
        """分析JavaScript文件（简化版）"""
        elements = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用正则表达式提取函数和类（简化版）
            
            # 提取函数
            function_pattern = r'(?:function\s+|const\s+|let\s+|var\s+)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*(?:=\s*)?(?:async\s+)?function\s*\([^)]*\)'
            for match in re.finditer(function_pattern, content):
                line_number = content[:match.start()].count('\n') + 1
                
                element = CodeElement(
                    name=match.group(1),
                    type="function",
                    file_path=str(file_path),
                    line_number=line_number,
                    signature=match.group(0)
                )
                elements.append(element)
            
            # 提取类
            class_pattern = r'class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)(?:\s+extends\s+[a-zA-Z_$][a-zA-Z0-9_$]*)?\s*{'
            for match in re.finditer(class_pattern, content):
                line_number = content[:match.start()].count('\n') + 1
                
                element = CodeElement(
                    name=match.group(1),
                    type="class",
                    file_path=str(file_path),
                    line_number=line_number,
                    signature=match.group(0).rstrip('{')
                )
                elements.append(element)
        
        except Exception as e:
            logging.error(f"分析JavaScript文件失败 {file_path}: {e}")
        
        return elements
    
    def _analyze_typescript(self, file_path: Path) -> List[CodeElement]:
        """分析TypeScript文件（简化版）"""
        # TypeScript分析逻辑类似JavaScript，但需要处理类型信息
        return self._analyze_javascript(file_path)
    
    def _analyze_java(self, file_path: Path) -> List[CodeElement]:
        """分析Java文件（简化版）"""
        elements = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取类
            class_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:abstract\s+)?(?:final\s+)?class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)'
            for match in re.finditer(class_pattern, content):
                line_number = content[:match.start()].count('\n') + 1
                
                element = CodeElement(
                    name=match.group(1),
                    type="class",
                    file_path=str(file_path),
                    line_number=line_number,
                    signature=match.group(0)
                )
                elements.append(element)
            
            # 提取方法
            method_pattern = r'(?:public\s+|private\s+|protected\s+)?(?:static\s+)?(?:final\s+)?(?:abstract\s+)?[a-zA-Z_$<>\[\]\s]+\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)'
            for match in re.finditer(method_pattern, content):
                line_number = content[:match.start()].count('\n') + 1
                
                element = CodeElement(
                    name=match.group(1),
                    type="method",
                    file_path=str(file_path),
                    line_number=line_number,
                    signature=match.group(0)
                )
                elements.append(element)
        
        except Exception as e:
            logging.error(f"分析Java文件失败 {file_path}: {e}")
        
        return elements
    
    def _analyze_cpp(self, file_path: Path) -> List[CodeElement]:
        """分析C++文件（简化版）"""
        return []  # 简化实现
    
    def _analyze_c(self, file_path: Path) -> List[CodeElement]:
        """分析C文件（简化版）"""
        return []  # 简化实现
    
    def _analyze_go(self, file_path: Path) -> List[CodeElement]:
        """分析Go文件（简化版）"""
        return []  # 简化实现
    
    def _analyze_rust(self, file_path: Path) -> List[CodeElement]:
        """分析Rust文件（简化版）"""
        return []  # 简化实现

class APIDocGenerator:
    """API文档生成器"""
    
    def __init__(self):
        pass
    
    def extract_from_openapi(self, spec_path: Path) -> List[APIEndpoint]:
        """从OpenAPI规范提取API信息"""
        try:
            with open(spec_path, 'r', encoding='utf-8') as f:
                if spec_path.suffix.lower() in ['.yaml', '.yml']:
                    spec = yaml.safe_load(f)
                else:
                    spec = json.load(f)
            
            endpoints = []
            paths = spec.get('paths', {})
            
            for path, path_item in paths.items():
                for method, operation in path_item.items():
                    if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                        endpoint = APIEndpoint(
                            path=path,
                            method=method.upper(),
                            summary=operation.get('summary', ''),
                            description=operation.get('description', ''),
                            parameters=operation.get('parameters', []),
                            request_body=operation.get('requestBody'),
                            responses=operation.get('responses', {}),
                            tags=operation.get('tags', []),
                            deprecated=operation.get('deprecated', False)
                        )
                        endpoints.append(endpoint)
            
            return endpoints
            
        except Exception as e:
            logging.error(f"提取OpenAPI规范失败 {spec_path}: {e}")
            return []
    
    def extract_from_code(self, source_paths: List[str]) -> List[APIEndpoint]:
        """从代码中提取API信息"""
        endpoints = []
        
        for source_path in source_paths:
            path = Path(source_path)
            if path.is_file():
                file_endpoints = self._extract_from_file(path)
                endpoints.extend(file_endpoints)
            elif path.is_dir():
                for file_path in path.rglob("*.py"):
                    file_endpoints = self._extract_from_file(file_path)
                    endpoints.extend(file_endpoints)
        
        return endpoints
    
    def _extract_from_file(self, file_path: Path) -> List[APIEndpoint]:
        """从单个文件提取API信息"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取Flask路由
            flask_pattern = r'@app\.route\(["\']([^"\']*)["\'],[^)]*methods\s*=\s*\[([^\]]+)\]'
            for match in re.finditer(flask_pattern, content):
                path = match.group(1)
                methods = [m.strip().strip('"\'') for m in match.group(2).split(',')]
                
                for method in methods:
                    endpoint = APIEndpoint(
                        path=path,
                        method=method.upper(),
                        summary=f"{method.upper()} {path}",
                        description="从Flask路由提取"
                    )
                    endpoints.append(endpoint)
            
            # 提取FastAPI路由
            fastapi_pattern = r'@app\.(get|post|put|delete|patch)\(["\']([^"\']*)["\']
            for match in re.finditer(fastapi_pattern, content):
                method = match.group(1)
                path = match.group(2)
                
                endpoint = APIEndpoint(
                    path=path,
                    method=method.upper(),
                    summary=f"{method.upper()} {path}",
                    description="从FastAPI路由提取"
                )
                endpoints.append(endpoint)
        
        except Exception as e:
            logging.error(f"从文件提取API失败 {file_path}: {e}")
        
        return endpoints

class DocumentGenerator:
    """文档生成器主类"""
    
    def __init__(self, config_path: str = None):
        self.root_path = Path(".").resolve()
        self.config_path = config_path or self.root_path / "config" / "docs.yaml"
        self.config = self._load_config()
        
        # 初始化组件
        self.code_analyzer = CodeAnalyzer()
        self.api_generator = APIDocGenerator()
        
        # 初始化模板环境
        template_dir = self.config.get("templates", {}).get("directory", "templates")
        self.template_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
        # 配置日志
        log_level = self.config.get("logging", {}).get("level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def _load_config(self) -> Dict:
        """加载文档配置"""
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
        """创建默认文档配置"""
        default_config = {
            "project": {
                "name": "New Energy Coder Club",
                "version": "1.0.0",
                "description": "新能源编程俱乐部项目文档",
                "author": "Development Team",
                "license": "MIT"
            },
            "output": {
                "directory": "./docs_generated",
                "formats": ["markdown", "html"],
                "language": "zh-CN"
            },
            "templates": {
                "directory": "./templates/documentation",
                "api_template": "api.md.template",
                "code_template": "code.md.template",
                "readme_template": "README.md.template"
            },
            "sources": {
                "code_directories": ["./src", "./api", "./scripts"],
                "api_specs": ["./api/openapi.yaml"],
                "exclude_patterns": [
                    "*.pyc", "__pycache__", ".git", "node_modules",
                    "*.log", "*.tmp", ".env", "dist", "build"
                ]
            },
            "generation": {
                "include_private": False,
                "include_tests": False,
                "auto_update": True,
                "parallel_processing": True,
                "max_workers": 4
            },
            "documents": [
                {
                    "name": "API文档",
                    "type": "api",
                    "source_paths": ["./api"],
                    "output_path": "api/index.md",
                    "template_path": "api.md.template",
                    "format": "markdown",
                    "auto_update": True
                },
                {
                    "name": "代码文档",
                    "type": "code",
                    "source_paths": ["./src", "./scripts"],
                    "output_path": "code/index.md",
                    "template_path": "code.md.template",
                    "format": "markdown",
                    "include_private": False,
                    "include_tests": False,
                    "auto_update": True
                },
                {
                    "name": "项目README",
                    "type": "readme",
                    "source_paths": ["."],
                    "output_path": "README.md",
                    "template_path": "README.md.template",
                    "format": "markdown",
                    "auto_update": True
                },
                {
                    "name": "变更日志",
                    "type": "changelog",
                    "source_paths": [".git"],
                    "output_path": "CHANGELOG.md",
                    "template_path": "changelog.md.template",
                    "format": "markdown",
                    "auto_update": True
                }
            ],
            "logging": {
                "level": "INFO",
                "file": "doc_generator.log"
            }
        }
        
        # 保存默认配置
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            logging.info("默认文档配置已创建")
        except Exception as e:
            logging.error(f"配置创建失败: {e}")
        
        return default_config
    
    def generate_document(self, doc_name: str) -> bool:
        """生成指定文档"""
        try:
            # 查找文档配置
            doc_config = None
            for doc in self.config.get("documents", []):
                if doc["name"] == doc_name:
                    doc_config = DocumentConfig(**doc)
                    break
            
            if not doc_config:
                logging.error(f"文档配置不存在: {doc_name}")
                return False
            
            logging.info(f"开始生成文档: {doc_name}")
            
            # 根据文档类型生成
            if doc_config.type == "api":
                return self._generate_api_doc(doc_config)
            elif doc_config.type == "code":
                return self._generate_code_doc(doc_config)
            elif doc_config.type == "readme":
                return self._generate_readme_doc(doc_config)
            elif doc_config.type == "changelog":
                return self._generate_changelog_doc(doc_config)
            else:
                logging.error(f"不支持的文档类型: {doc_config.type}")
                return False
                
        except Exception as e:
            logging.error(f"生成文档失败 {doc_name}: {e}")
            return False
    
    def _generate_api_doc(self, config: DocumentConfig) -> bool:
        """生成API文档"""
        try:
            endpoints = []
            
            # 从OpenAPI规范提取
            for source_path in config.source_paths:
                path = Path(source_path)
                if path.is_file() and path.suffix.lower() in ['.yaml', '.yml', '.json']:
                    spec_endpoints = self.api_generator.extract_from_openapi(path)
                    endpoints.extend(spec_endpoints)
                elif path.is_dir():
                    # 从代码提取
                    code_endpoints = self.api_generator.extract_from_code([str(path)])
                    endpoints.extend(code_endpoints)
            
            if not endpoints:
                logging.warning(f"没有找到API端点: {config.source_paths}")
                return True
            
            # 按标签分组
            grouped_endpoints = {}
            for endpoint in endpoints:
                tags = endpoint.tags or ["default"]
                for tag in tags:
                    if tag not in grouped_endpoints:
                        grouped_endpoints[tag] = []
                    grouped_endpoints[tag].append(endpoint)
            
            # 准备模板数据
            template_data = {
                "project": self.config.get("project", {}),
                "endpoints": endpoints,
                "grouped_endpoints": grouped_endpoints,
                "generation_time": datetime.now().isoformat(),
                "total_endpoints": len(endpoints)
            }
            
            # 渲染模板
            content = self._render_template(config.template_path, template_data)
            
            # 保存文档
            output_path = Path(self.config["output"]["directory"]) / config.output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logging.info(f"API文档生成完成: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"生成API文档失败: {e}")
            return False
    
    def _generate_code_doc(self, config: DocumentConfig) -> bool:
        """生成代码文档"""
        try:
            all_elements = []
            
            # 分析所有源代码目录
            for source_path in config.source_paths:
                path = Path(source_path)
                if path.is_file():
                    elements = self.code_analyzer.analyze_file(path)
                    all_elements.extend(elements)
                elif path.is_dir():
                    elements = self.code_analyzer.analyze_directory(
                        path,
                        include_private=config.include_private,
                        include_tests=config.include_tests
                    )
                    all_elements.extend(elements)
            
            if not all_elements:
                logging.warning(f"没有找到代码元素: {config.source_paths}")
                return True
            
            # 按文件和类型分组
            grouped_elements = {}
            for element in all_elements:
                file_path = element.file_path
                if file_path not in grouped_elements:
                    grouped_elements[file_path] = {
                        "classes": [],
                        "functions": [],
                        "methods": [],
                        "variables": [],
                        "constants": []
                    }
                
                if element.type in grouped_elements[file_path]:
                    grouped_elements[file_path][element.type + "s"].append(element)
                else:
                    grouped_elements[file_path]["functions"].append(element)
            
            # 统计信息
            stats = {
                "total_files": len(grouped_elements),
                "total_elements": len(all_elements),
                "by_type": {}
            }
            
            for element in all_elements:
                element_type = element.type
                if element_type not in stats["by_type"]:
                    stats["by_type"][element_type] = 0
                stats["by_type"][element_type] += 1
            
            # 准备模板数据
            template_data = {
                "project": self.config.get("project", {}),
                "elements": all_elements,
                "grouped_elements": grouped_elements,
                "stats": stats,
                "generation_time": datetime.now().isoformat()
            }
            
            # 渲染模板
            content = self._render_template(config.template_path, template_data)
            
            # 保存文档
            output_path = Path(self.config["output"]["directory"]) / config.output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logging.info(f"代码文档生成完成: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"生成代码文档失败: {e}")
            return False
    
    def _generate_readme_doc(self, config: DocumentConfig) -> bool:
        """生成README文档"""
        try:
            # 收集项目信息
            project_info = self.config.get("project", {})
            
            # 分析项目结构
            structure = self._analyze_project_structure()
            
            # 收集依赖信息
            dependencies = self._collect_dependencies()
            
            # 准备模板数据
            template_data = {
                "project": project_info,
                "structure": structure,
                "dependencies": dependencies,
                "generation_time": datetime.now().isoformat()
            }
            
            # 渲染模板
            content = self._render_template(config.template_path, template_data)
            
            # 保存文档
            output_path = Path(self.config["output"]["directory"]) / config.output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logging.info(f"README文档生成完成: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"生成README文档失败: {e}")
            return False
    
    def _generate_changelog_doc(self, config: DocumentConfig) -> bool:
        """生成变更日志文档"""
        try:
            # 从Git历史提取变更信息
            changes = self._extract_git_changes()
            
            # 准备模板数据
            template_data = {
                "project": self.config.get("project", {}),
                "changes": changes,
                "generation_time": datetime.now().isoformat()
            }
            
            # 渲染模板
            content = self._render_template(config.template_path, template_data)
            
            # 保存文档
            output_path = Path(self.config["output"]["directory"]) / config.output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logging.info(f"变更日志生成完成: {output_path}")
            return True
            
        except Exception as e:
            logging.error(f"生成变更日志失败: {e}")
            return False
    
    def _render_template(self, template_path: str, data: Dict) -> str:
        """渲染模板"""
        try:
            if template_path and Path(template_path).exists():
                template = self.template_env.get_template(template_path)
                return template.render(**data)
            else:
                # 使用默认模板
                return self._generate_default_content(data)
                
        except Exception as e:
            logging.error(f"模板渲染失败: {e}")
            return self._generate_default_content(data)
    
    def _generate_default_content(self, data: Dict) -> str:
        """生成默认内容"""
        content = f"# {data.get('project', {}).get('name', '项目文档')}\n\n"
        content += f"生成时间: {data.get('generation_time', '')}\n\n"
        
        # 添加数据的JSON表示（用于调试）
        content += "## 数据内容\n\n"
        content += "```json\n"
        content += json.dumps(data, indent=2, ensure_ascii=False, default=str)
        content += "\n```\n"
        
        return content
    
    def _analyze_project_structure(self) -> Dict:
        """分析项目结构"""
        structure = {
            "directories": [],
            "files": [],
            "total_files": 0,
            "total_directories": 0
        }
        
        try:
            for item in self.root_path.rglob("*"):
                if item.is_file():
                    structure["files"].append({
                        "path": str(item.relative_to(self.root_path)),
                        "size": item.stat().st_size,
                        "extension": item.suffix
                    })
                    structure["total_files"] += 1
                elif item.is_dir():
                    structure["directories"].append({
                        "path": str(item.relative_to(self.root_path))
                    })
                    structure["total_directories"] += 1
        
        except Exception as e:
            logging.error(f"分析项目结构失败: {e}")
        
        return structure
    
    def _collect_dependencies(self) -> Dict:
        """收集依赖信息"""
        dependencies = {
            "python": [],
            "node": [],
            "other": []
        }
        
        try:
            # Python依赖
            requirements_files = [
                "requirements.txt", "requirements-dev.txt", 
                "Pipfile", "pyproject.toml", "setup.py"
            ]
            
            for req_file in requirements_files:
                req_path = self.root_path / req_file
                if req_path.exists():
                    dependencies["python"].append({
                        "file": req_file,
                        "exists": True
                    })
            
            # Node.js依赖
            package_json = self.root_path / "package.json"
            if package_json.exists():
                try:
                    with open(package_json, 'r', encoding='utf-8') as f:
                        package_data = json.load(f)
                        dependencies["node"] = {
                            "dependencies": package_data.get("dependencies", {}),
                            "devDependencies": package_data.get("devDependencies", {})
                        }
                except Exception as e:
                    logging.error(f"读取package.json失败: {e}")
        
        except Exception as e:
            logging.error(f"收集依赖信息失败: {e}")
        
        return dependencies
    
    def _extract_git_changes(self) -> List[Dict]:
        """从Git历史提取变更信息"""
        changes = []
        
        try:
            # 获取Git提交历史
            result = subprocess.run(
                ["git", "log", "--oneline", "--max-count=50"],
                capture_output=True, text=True, cwd=self.root_path
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        if len(parts) >= 2:
                            changes.append({
                                "hash": parts[0],
                                "message": parts[1],
                                "type": self._classify_commit_type(parts[1])
                            })
        
        except Exception as e:
            logging.error(f"提取Git变更失败: {e}")
        
        return changes
    
    def _classify_commit_type(self, message: str) -> str:
        """分类提交类型"""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ['feat', 'feature', '新增', '添加']):
            return "feature"
        elif any(keyword in message_lower for keyword in ['fix', 'bug', '修复', '修正']):
            return "bugfix"
        elif any(keyword in message_lower for keyword in ['doc', '文档', 'readme']):
            return "documentation"
        elif any(keyword in message_lower for keyword in ['refactor', '重构', '优化']):
            return "refactor"
        elif any(keyword in message_lower for keyword in ['test', '测试']):
            return "test"
        else:
            return "other"
    
    def generate_all_documents(self, parallel: bool = False) -> Dict[str, bool]:
        """生成所有文档"""
        documents = self.config.get("documents", [])
        results = {}
        
        if not documents:
            logging.info("没有配置的文档")
            return results
        
        if parallel:
            # 并行生成
            max_workers = min(len(documents), self.config.get("generation", {}).get("max_workers", 4))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_doc = {
                    executor.submit(self.generate_document, doc["name"]): doc["name"]
                    for doc in documents
                }
                
                for future in as_completed(future_to_doc):
                    doc_name = future_to_doc[future]
                    try:
                        result = future.result()
                        results[doc_name] = result
                    except Exception as e:
                        logging.error(f"并行生成文档失败 {doc_name}: {e}")
                        results[doc_name] = False
        else:
            # 串行生成
            for doc in documents:
                doc_name = doc["name"]
                result = self.generate_document(doc_name)
                results[doc_name] = result
        
        return results
    
    def watch_and_update(self):
        """监控文件变化并自动更新文档"""
        try:
            import watchdog
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class DocumentUpdateHandler(FileSystemEventHandler):
                def __init__(self, generator):
                    self.generator = generator
                    self.last_update = datetime.now()
                
                def on_modified(self, event):
                    if event.is_directory:
                        return
                    
                    # 避免频繁更新
                    now = datetime.now()
                    if (now - self.last_update).seconds < 5:
                        return
                    
                    self.last_update = now
                    
                    # 检查是否为源文件
                    file_path = Path(event.src_path)
                    if self._should_update(file_path):
                        logging.info(f"检测到文件变化，更新文档: {file_path}")
                        self.generator.generate_all_documents()
                
                def _should_update(self, file_path: Path) -> bool:
                    # 检查文件是否在源目录中
                    source_dirs = self.generator.config.get("sources", {}).get("code_directories", [])
                    for source_dir in source_dirs:
                        try:
                            file_path.relative_to(Path(source_dir))
                            return True
                        except ValueError:
                            continue
                    return False
            
            observer = Observer()
            handler = DocumentUpdateHandler(self)
            
            # 监控源代码目录
            source_dirs = self.config.get("sources", {}).get("code_directories", [])
            for source_dir in source_dirs:
                if Path(source_dir).exists():
                    observer.schedule(handler, source_dir, recursive=True)
                    logging.info(f"开始监控目录: {source_dir}")
            
            observer.start()
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
                logging.info("停止文档监控")
            
            observer.join()
            
        except ImportError:
            logging.error("需要安装watchdog库来支持文件监控: pip install watchdog")
        except Exception as e:
            logging.error(f"文档监控失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动化文档生成系统")
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    parser.add_argument(
        "--doc",
        help="生成指定文档"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="生成所有文档"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="并行生成文档"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="监控文件变化并自动更新文档"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化文档配置"
    )
    
    args = parser.parse_args()
    
    # 创建文档生成器
    doc_generator = DocumentGenerator(args.config)
    
    if args.init:
        # 初始化配置
        print("✅ 文档配置初始化完成")
        
    elif args.watch:
        # 监控模式
        print("🔍 开始监控文件变化")
        doc_generator.watch_and_update()
        
    elif args.doc:
        # 生成指定文档
        print(f"📝 生成文档: {args.doc}")
        success = doc_generator.generate_document(args.doc)
        
        if success:
            print(f"✅ 文档生成成功: {args.doc}")
        else:
            print(f"❌ 文档生成失败: {args.doc}")
            sys.exit(1)
            
    elif args.all:
        # 生成所有文档
        print("📚 生成所有文档")
        results = doc_generator.generate_all_documents(parallel=args.parallel)
        
        success_count = len([r for r in results.values() if r])
        failed_count = len([r for r in results.values() if not r])
        
        print(f"✅ 文档生成完成: {success_count} 成功, {failed_count} 失败")
        
        if failed_count > 0:
            print("\n失败的文档:")
            for doc_name, success in results.items():
                if not success:
                    print(f"  - {doc_name}")
            sys.exit(1)
    else:
        # 显示帮助
        parser.print_help()

if __name__ == "__main__":
    main()