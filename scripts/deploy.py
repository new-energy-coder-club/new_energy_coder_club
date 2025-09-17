#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化部署脚本
用于自动化部署项目到各种环境（开发、测试、生产）
"""

import os
import sys
import json
import yaml
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import shutil
import tempfile

class DeploymentManager:
    """部署管理器"""
    
    def __init__(self, config_path: str = None):
        self.root_path = Path(".").resolve()
        self.config_path = config_path or self.root_path / "config" / "deploy.yaml"
        self.config = self._load_config()
        self.deployment_log = []
        self.errors = []
        self.warnings = []
        
        # 支持的部署目标
        self.supported_targets = {
            "github-pages": self._deploy_github_pages,
            "vercel": self._deploy_vercel,
            "netlify": self._deploy_netlify,
            "docker": self._deploy_docker,
            "aws-s3": self._deploy_aws_s3,
            "local": self._deploy_local
        }
        
        # 环境配置
        self.environments = {
            "development": {
                "branch": "develop",
                "build_command": "npm run build:dev",
                "test_required": True
            },
            "staging": {
                "branch": "staging",
                "build_command": "npm run build:staging",
                "test_required": True
            },
            "production": {
                "branch": "main",
                "build_command": "npm run build:prod",
                "test_required": True
            }
        }
    
    def _load_config(self) -> Dict:
        """加载部署配置"""
        if not self.config_path.exists():
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.suffix.lower() == '.yaml' or self.config_path.suffix.lower() == '.yml':
                    return yaml.safe_load(f)
                else:
                    return json.load(f)
        except Exception as e:
            self.log_action("load_config", str(self.config_path), "", "error", f"配置加载失败: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """创建默认配置"""
        default_config = {
            "project": {
                "name": "new-energy-coder-club",
                "version": "1.0.0",
                "description": "新能源编程俱乐部项目仓库"
            },
            "environments": {
                "development": {
                    "target": "local",
                    "branch": "develop",
                    "build_dir": "dist",
                    "build_command": "npm run build:dev",
                    "test_command": "npm test",
                    "pre_deploy_hooks": [],
                    "post_deploy_hooks": []
                },
                "staging": {
                    "target": "vercel",
                    "branch": "staging",
                    "build_dir": "dist",
                    "build_command": "npm run build:staging",
                    "test_command": "npm test",
                    "pre_deploy_hooks": ["lint", "test"],
                    "post_deploy_hooks": ["notify"]
                },
                "production": {
                    "target": "github-pages",
                    "branch": "main",
                    "build_dir": "dist",
                    "build_command": "npm run build:prod",
                    "test_command": "npm run test:prod",
                    "pre_deploy_hooks": ["lint", "test", "security-scan"],
                    "post_deploy_hooks": ["notify", "update-docs"]
                }
            },
            "targets": {
                "github-pages": {
                    "repository": "username/new-energy-coder-club",
                    "branch": "gh-pages",
                    "domain": "your-domain.github.io"
                },
                "vercel": {
                    "project_id": "your-vercel-project-id",
                    "org_id": "your-vercel-org-id",
                    "domain": "your-project.vercel.app"
                },
                "netlify": {
                    "site_id": "your-netlify-site-id",
                    "domain": "your-project.netlify.app"
                },
                "docker": {
                    "registry": "docker.io",
                    "image_name": "username/new-energy-coder-club",
                    "tag": "latest"
                },
                "aws-s3": {
                    "bucket": "your-s3-bucket",
                    "region": "us-east-1",
                    "cloudfront_distribution": "your-cloudfront-id"
                },
                "local": {
                    "output_dir": "./deploy",
                    "server_port": 8080
                }
            },
            "hooks": {
                "lint": "npm run lint",
                "test": "npm test",
                "security-scan": "npm audit",
                "notify": "echo 'Deployment completed'",
                "update-docs": "python scripts/update_docs.py"
            },
            "notifications": {
                "slack": {
                    "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                    "channel": "#deployments"
                },
                "email": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "from_email": "noreply@example.com",
                    "to_emails": ["admin@example.com"]
                }
            }
        }
        
        # 保存默认配置
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            self.log_action("create_config", "", str(self.config_path), "success", "默认配置已创建")
        except Exception as e:
            self.log_action("create_config", "", str(self.config_path), "error", f"配置创建失败: {e}")
        
        return default_config
    
    def log_action(self, action: str, source: str = "", target: str = "", status: str = "success", message: str = ""):
        """记录部署操作"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "source": source,
            "target": target,
            "status": status,
            "message": message
        }
        self.deployment_log.append(log_entry)
        
        # 实时输出
        status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
        print(f"{status_icon} {action}: {message}")
    
    def check_prerequisites(self, environment: str) -> bool:
        """检查部署前置条件"""
        print(f"🔍 检查 {environment} 环境部署前置条件")
        
        env_config = self.config.get("environments", {}).get(environment, {})
        if not env_config:
            self.log_action("check_prerequisites", environment, "", "error", "环境配置不存在")
            return False
        
        # 检查Git状态
        if not self._check_git_status(env_config.get("branch")):
            return False
        
        # 检查依赖
        if not self._check_dependencies():
            return False
        
        # 检查构建工具
        if not self._check_build_tools():
            return False
        
        # 检查环境变量
        if not self._check_environment_variables(environment):
            return False
        
        self.log_action("check_prerequisites", environment, "", "success", "前置条件检查通过")
        return True
    
    def _check_git_status(self, required_branch: str = None) -> bool:
        """检查Git状态"""
        try:
            # 检查是否在Git仓库中
            result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                                  capture_output=True, text=True, cwd=self.root_path)
            if result.returncode != 0:
                self.log_action("check_git", "", "", "error", "不在Git仓库中")
                return False
            
            # 检查当前分支
            result = subprocess.run(["git", "branch", "--show-current"], 
                                  capture_output=True, text=True, cwd=self.root_path)
            current_branch = result.stdout.strip()
            
            if required_branch and current_branch != required_branch:
                self.log_action("check_git", current_branch, required_branch, "warning", 
                               f"当前分支 {current_branch} 不是目标分支 {required_branch}")
            
            # 检查是否有未提交的更改
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, cwd=self.root_path)
            if result.stdout.strip():
                self.log_action("check_git", "", "", "warning", "存在未提交的更改")
            
            self.log_action("check_git", "", "", "success", f"Git状态正常，当前分支: {current_branch}")
            return True
            
        except Exception as e:
            self.log_action("check_git", "", "", "error", f"Git检查失败: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """检查项目依赖"""
        # 检查Node.js项目
        package_json = self.root_path / "package.json"
        if package_json.exists():
            node_modules = self.root_path / "node_modules"
            if not node_modules.exists():
                self.log_action("check_deps", "", "", "error", "Node.js依赖未安装，请运行 npm install")
                return False
        
        # 检查Python项目
        requirements_txt = self.root_path / "requirements.txt"
        if requirements_txt.exists():
            try:
                result = subprocess.run(["pip", "check"], capture_output=True, text=True)
                if result.returncode != 0:
                    self.log_action("check_deps", "", "", "warning", "Python依赖可能存在问题")
            except FileNotFoundError:
                self.log_action("check_deps", "", "", "error", "pip未找到")
                return False
        
        self.log_action("check_deps", "", "", "success", "依赖检查通过")
        return True
    
    def _check_build_tools(self) -> bool:
        """检查构建工具"""
        tools = []
        
        # 检查Node.js和npm
        if (self.root_path / "package.json").exists():
            tools.extend(["node", "npm"])
        
        # 检查Python
        if (self.root_path / "requirements.txt").exists() or (self.root_path / "pyproject.toml").exists():
            tools.append("python")
        
        # 检查Docker
        if (self.root_path / "Dockerfile").exists():
            tools.append("docker")
        
        for tool in tools:
            try:
                result = subprocess.run([tool, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.log_action("check_tools", tool, "", "success", f"{tool} 可用: {version}")
                else:
                    self.log_action("check_tools", tool, "", "error", f"{tool} 不可用")
                    return False
            except FileNotFoundError:
                self.log_action("check_tools", tool, "", "error", f"{tool} 未安装")
                return False
        
        return True
    
    def _check_environment_variables(self, environment: str) -> bool:
        """检查环境变量"""
        env_config = self.config.get("environments", {}).get(environment, {})
        target = env_config.get("target")
        
        required_vars = {
            "github-pages": ["GITHUB_TOKEN"],
            "vercel": ["VERCEL_TOKEN"],
            "netlify": ["NETLIFY_AUTH_TOKEN"],
            "aws-s3": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
            "docker": ["DOCKER_USERNAME", "DOCKER_PASSWORD"]
        }
        
        if target in required_vars:
            missing_vars = []
            for var in required_vars[target]:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                self.log_action("check_env_vars", target, "", "error", 
                               f"缺少环境变量: {', '.join(missing_vars)}")
                return False
        
        self.log_action("check_env_vars", target, "", "success", "环境变量检查通过")
        return True
    
    def run_hooks(self, hooks: List[str], stage: str) -> bool:
        """运行钩子脚本"""
        if not hooks:
            return True
        
        print(f"🔧 运行 {stage} 钩子")
        
        hook_commands = self.config.get("hooks", {})
        
        for hook in hooks:
            if hook not in hook_commands:
                self.log_action("run_hook", hook, "", "warning", f"钩子 {hook} 未定义")
                continue
            
            command = hook_commands[hook]
            try:
                self.log_action("run_hook", hook, "", "info", f"执行: {command}")
                result = subprocess.run(command, shell=True, cwd=self.root_path, 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.log_action("run_hook", hook, "", "success", "钩子执行成功")
                else:
                    self.log_action("run_hook", hook, "", "error", 
                                   f"钩子执行失败: {result.stderr}")
                    return False
                    
            except Exception as e:
                self.log_action("run_hook", hook, "", "error", f"钩子执行异常: {e}")
                return False
        
        return True
    
    def build_project(self, environment: str) -> bool:
        """构建项目"""
        print(f"🏗️  构建 {environment} 环境")
        
        env_config = self.config.get("environments", {}).get(environment, {})
        build_command = env_config.get("build_command")
        
        if not build_command:
            self.log_action("build", environment, "", "warning", "未配置构建命令")
            return True
        
        try:
            self.log_action("build", environment, "", "info", f"执行构建: {build_command}")
            result = subprocess.run(build_command, shell=True, cwd=self.root_path,
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action("build", environment, "", "success", "项目构建成功")
                return True
            else:
                self.log_action("build", environment, "", "error", 
                               f"构建失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_action("build", environment, "", "error", f"构建异常: {e}")
            return False
    
    def _deploy_github_pages(self, environment: str) -> bool:
        """部署到GitHub Pages"""
        env_config = self.config.get("environments", {}).get(environment, {})
        target_config = self.config.get("targets", {}).get("github-pages", {})
        
        build_dir = env_config.get("build_dir", "dist")
        build_path = self.root_path / build_dir
        
        if not build_path.exists():
            self.log_action("deploy_gh_pages", "", "", "error", f"构建目录不存在: {build_dir}")
            return False
        
        try:
            # 使用gh-pages工具部署
            gh_pages_branch = target_config.get("branch", "gh-pages")
            
            # 检查是否安装了gh-pages
            result = subprocess.run(["npx", "gh-pages", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                # 安装gh-pages
                subprocess.run(["npm", "install", "-g", "gh-pages"], cwd=self.root_path)
            
            # 部署到GitHub Pages
            deploy_cmd = f"npx gh-pages -d {build_dir} -b {gh_pages_branch}"
            result = subprocess.run(deploy_cmd, shell=True, cwd=self.root_path,
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                domain = target_config.get("domain", "your-domain.github.io")
                self.log_action("deploy_gh_pages", build_dir, domain, "success", 
                               "GitHub Pages部署成功")
                return True
            else:
                self.log_action("deploy_gh_pages", build_dir, "", "error", 
                               f"GitHub Pages部署失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_action("deploy_gh_pages", "", "", "error", f"GitHub Pages部署异常: {e}")
            return False
    
    def _deploy_vercel(self, environment: str) -> bool:
        """部署到Vercel"""
        env_config = self.config.get("environments", {}).get(environment, {})
        target_config = self.config.get("targets", {}).get("vercel", {})
        
        try:
            # 检查Vercel CLI
            result = subprocess.run(["vercel", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.log_action("deploy_vercel", "", "", "error", "Vercel CLI未安装")
                return False
            
            # 部署到Vercel
            deploy_cmd = "vercel --prod" if environment == "production" else "vercel"
            result = subprocess.run(deploy_cmd, shell=True, cwd=self.root_path,
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # 从输出中提取部署URL
                deploy_url = result.stdout.strip().split('\n')[-1]
                self.log_action("deploy_vercel", "", deploy_url, "success", "Vercel部署成功")
                return True
            else:
                self.log_action("deploy_vercel", "", "", "error", 
                               f"Vercel部署失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_action("deploy_vercel", "", "", "error", f"Vercel部署异常: {e}")
            return False
    
    def _deploy_netlify(self, environment: str) -> bool:
        """部署到Netlify"""
        env_config = self.config.get("environments", {}).get(environment, {})
        target_config = self.config.get("targets", {}).get("netlify", {})
        
        build_dir = env_config.get("build_dir", "dist")
        site_id = target_config.get("site_id")
        
        if not site_id:
            self.log_action("deploy_netlify", "", "", "error", "Netlify站点ID未配置")
            return False
        
        try:
            # 使用Netlify CLI部署
            deploy_cmd = f"netlify deploy --dir={build_dir} --site={site_id}"
            if environment == "production":
                deploy_cmd += " --prod"
            
            result = subprocess.run(deploy_cmd, shell=True, cwd=self.root_path,
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                domain = target_config.get("domain", "your-project.netlify.app")
                self.log_action("deploy_netlify", build_dir, domain, "success", "Netlify部署成功")
                return True
            else:
                self.log_action("deploy_netlify", build_dir, "", "error", 
                               f"Netlify部署失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_action("deploy_netlify", "", "", "error", f"Netlify部署异常: {e}")
            return False
    
    def _deploy_docker(self, environment: str) -> bool:
        """部署到Docker"""
        target_config = self.config.get("targets", {}).get("docker", {})
        
        image_name = target_config.get("image_name")
        tag = target_config.get("tag", "latest")
        
        if not image_name:
            self.log_action("deploy_docker", "", "", "error", "Docker镜像名未配置")
            return False
        
        try:
            # 构建Docker镜像
            build_cmd = f"docker build -t {image_name}:{tag} ."
            result = subprocess.run(build_cmd, shell=True, cwd=self.root_path,
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log_action("deploy_docker", "", "", "error", 
                               f"Docker镜像构建失败: {result.stderr}")
                return False
            
            # 推送Docker镜像
            push_cmd = f"docker push {image_name}:{tag}"
            result = subprocess.run(push_cmd, shell=True, cwd=self.root_path,
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_action("deploy_docker", "", f"{image_name}:{tag}", "success", 
                               "Docker镜像部署成功")
                return True
            else:
                self.log_action("deploy_docker", "", "", "error", 
                               f"Docker镜像推送失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_action("deploy_docker", "", "", "error", f"Docker部署异常: {e}")
            return False
    
    def _deploy_aws_s3(self, environment: str) -> bool:
        """部署到AWS S3"""
        env_config = self.config.get("environments", {}).get(environment, {})
        target_config = self.config.get("targets", {}).get("aws-s3", {})
        
        build_dir = env_config.get("build_dir", "dist")
        bucket = target_config.get("bucket")
        
        if not bucket:
            self.log_action("deploy_s3", "", "", "error", "S3存储桶未配置")
            return False
        
        try:
            # 同步到S3
            sync_cmd = f"aws s3 sync {build_dir} s3://{bucket} --delete"
            result = subprocess.run(sync_cmd, shell=True, cwd=self.root_path,
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # 清除CloudFront缓存（如果配置了）
                cloudfront_id = target_config.get("cloudfront_distribution")
                if cloudfront_id:
                    invalidate_cmd = f"aws cloudfront create-invalidation --distribution-id {cloudfront_id} --paths '/*'"
                    subprocess.run(invalidate_cmd, shell=True, cwd=self.root_path)
                
                self.log_action("deploy_s3", build_dir, bucket, "success", "S3部署成功")
                return True
            else:
                self.log_action("deploy_s3", build_dir, "", "error", 
                               f"S3部署失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_action("deploy_s3", "", "", "error", f"S3部署异常: {e}")
            return False
    
    def _deploy_local(self, environment: str) -> bool:
        """本地部署"""
        env_config = self.config.get("environments", {}).get(environment, {})
        target_config = self.config.get("targets", {}).get("local", {})
        
        build_dir = env_config.get("build_dir", "dist")
        output_dir = target_config.get("output_dir", "./deploy")
        
        build_path = self.root_path / build_dir
        output_path = self.root_path / output_dir
        
        try:
            # 复制构建文件到输出目录
            if output_path.exists():
                shutil.rmtree(output_path)
            
            shutil.copytree(build_path, output_path)
            
            self.log_action("deploy_local", str(build_path), str(output_path), "success", 
                           "本地部署成功")
            
            # 启动本地服务器（可选）
            port = target_config.get("server_port", 8080)
            print(f"💡 可以运行以下命令启动本地服务器:")
            print(f"   cd {output_dir} && python -m http.server {port}")
            
            return True
            
        except Exception as e:
            self.log_action("deploy_local", "", "", "error", f"本地部署异常: {e}")
            return False
    
    def send_notification(self, environment: str, success: bool):
        """发送部署通知"""
        notification_config = self.config.get("notifications", {})
        
        status = "成功" if success else "失败"
        message = f"项目部署到 {environment} 环境{status}"
        
        # Slack通知
        slack_config = notification_config.get("slack", {})
        if slack_config.get("webhook_url"):
            self._send_slack_notification(slack_config, message, success)
        
        # 邮件通知
        email_config = notification_config.get("email", {})
        if email_config.get("smtp_server"):
            self._send_email_notification(email_config, message, success)
    
    def _send_slack_notification(self, config: Dict, message: str, success: bool):
        """发送Slack通知"""
        try:
            import requests
            
            payload = {
                "text": message,
                "channel": config.get("channel", "#deployments"),
                "username": "DeployBot",
                "icon_emoji": ":rocket:" if success else ":x:"
            }
            
            response = requests.post(config["webhook_url"], json=payload)
            if response.status_code == 200:
                self.log_action("notify_slack", "", "", "success", "Slack通知发送成功")
            else:
                self.log_action("notify_slack", "", "", "error", "Slack通知发送失败")
                
        except Exception as e:
            self.log_action("notify_slack", "", "", "error", f"Slack通知异常: {e}")
    
    def _send_email_notification(self, config: Dict, message: str, success: bool):
        """发送邮件通知"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = config["from_email"]
            msg['To'] = ", ".join(config["to_emails"])
            msg['Subject'] = f"部署通知 - {message}"
            
            body = f"""
            部署状态: {message}
            时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            项目: {self.config.get('project', {}).get('name', 'Unknown')}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
            server.starttls()
            server.login(config["from_email"], os.getenv("EMAIL_PASSWORD", ""))
            server.send_message(msg)
            server.quit()
            
            self.log_action("notify_email", "", "", "success", "邮件通知发送成功")
            
        except Exception as e:
            self.log_action("notify_email", "", "", "error", f"邮件通知异常: {e}")
    
    def deploy(self, environment: str, skip_tests: bool = False, skip_build: bool = False) -> bool:
        """执行部署"""
        print(f"🚀 开始部署到 {environment} 环境")
        print("=" * 60)
        
        env_config = self.config.get("environments", {}).get(environment, {})
        if not env_config:
            self.log_action("deploy", environment, "", "error", "环境配置不存在")
            return False
        
        target = env_config.get("target")
        if target not in self.supported_targets:
            self.log_action("deploy", environment, target, "error", "不支持的部署目标")
            return False
        
        try:
            # 1. 检查前置条件
            if not self.check_prerequisites(environment):
                return False
            
            # 2. 运行预部署钩子
            pre_hooks = env_config.get("pre_deploy_hooks", [])
            if not skip_tests and not self.run_hooks(pre_hooks, "pre-deploy"):
                return False
            
            # 3. 构建项目
            if not skip_build and not self.build_project(environment):
                return False
            
            # 4. 执行部署
            deploy_func = self.supported_targets[target]
            if not deploy_func(environment):
                return False
            
            # 5. 运行后部署钩子
            post_hooks = env_config.get("post_deploy_hooks", [])
            self.run_hooks(post_hooks, "post-deploy")
            
            # 6. 发送通知
            self.send_notification(environment, True)
            
            print("\n" + "=" * 60)
            print(f"🎉 {environment} 环境部署成功！")
            
            return True
            
        except Exception as e:
            self.log_action("deploy", environment, "", "error", f"部署过程异常: {e}")
            self.send_notification(environment, False)
            print(f"❌ 部署失败: {e}")
            return False
    
    def rollback(self, environment: str, version: str = None) -> bool:
        """回滚部署"""
        print(f"🔄 回滚 {environment} 环境")
        
        # 这里可以实现具体的回滚逻辑
        # 例如：恢复到上一个Git提交、恢复备份文件等
        
        self.log_action("rollback", environment, version or "previous", "info", "回滚功能待实现")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动化部署工具")
    parser.add_argument(
        "environment",
        choices=["development", "staging", "production"],
        help="部署环境"
    )
    parser.add_argument(
        "--config",
        help="配置文件路径"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="跳过测试"
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="跳过构建"
    )
    parser.add_argument(
        "--rollback",
        help="回滚到指定版本"
    )
    
    args = parser.parse_args()
    
    # 创建部署管理器
    deployer = DeploymentManager(args.config)
    
    # 执行操作
    if args.rollback:
        success = deployer.rollback(args.environment, args.rollback)
    else:
        success = deployer.deploy(args.environment, args.skip_tests, args.skip_build)
    
    # 返回适当的退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()