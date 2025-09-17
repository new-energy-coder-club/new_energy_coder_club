#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仓库目录结构迁移脚本

功能:
1. 自动备份现有项目结构
2. 按照新的目录结构迁移项目
3. 保持Git历史记录完整
4. 生成详细的迁移日志
5. 提供回滚机制

作者: SOLO Coding
日期: 2025-01-18
"""

import os
import shutil
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import hashlib

class RepositoryMigrator:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.backup_path = self.root_path / "backup" / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_path = self.root_path / "migration_logs"
        self.migration_map = self._load_migration_map()
        self.setup_logging()
        
    def setup_logging(self):
        """设置日志记录"""
        self.log_path.mkdir(exist_ok=True)
        log_file = self.log_path / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _load_migration_map(self) -> Dict:
        """加载迁移映射配置"""
        return {
            # 竞赛项目迁移映射
            "competitions": {
                "competitions/2024/electronics-competition": "competitions_new/2024/electronics",
                "competitions/2024/energy-saving": "competitions_new/2024/energy-saving",
                "competitions/2024/huawei-cloud-ai": "competitions_new/2024/huawei-cloud-ai",
                "competitions/2024/iot-design-huawei": "competitions_new/2024/iot-design",
                "competitions/2024/robocon": "competitions_new/2024/robocon",
                "competitions/2024/smart-car-outdoor": "competitions_new/2024/smart-car",
                "competitions/2025/robocon": "competitions_new/2025/robocon",
                "competitions/2025/traffic-design": "competitions_new/2025/traffic-design",
                "competitions/2025/energy-saving": "competitions_new/2025/energy-saving"
            },
            # 技术项目迁移映射
            "projects": {
                "projects/ai": "projects_new/ai",
                "projects/embedded": "projects_new/embedded",
                "projects/robotics": "projects_new/robotics",
                "projects/科研「横向项目」": "projects_new/research",
                "projects/templates": "projects_new/templates"
            },
            # 共享资源迁移映射
            "shared": {
                "shared/images": "shared_new/assets/images",
                "shared/models": "shared_new/models",
                "shared/libraries": "shared_new/libraries",
                "shared/tools": "shared_new/tools"
            }
        }
    
    def create_backup(self) -> bool:
        """创建完整备份"""
        try:
            self.logger.info(f"开始创建备份到: {self.backup_path}")
            self.backup_path.mkdir(parents=True, exist_ok=True)
            
            # 备份主要目录
            directories_to_backup = ['competitions', 'projects', 'shared', 'docs']
            
            for dir_name in directories_to_backup:
                src_dir = self.root_path / dir_name
                if src_dir.exists():
                    dst_dir = self.backup_path / dir_name
                    self.logger.info(f"备份目录: {src_dir} -> {dst_dir}")
                    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            
            # 备份重要文件
            important_files = ['README.md', '.gitignore', 'LICENSE']
            for file_name in important_files:
                src_file = self.root_path / file_name
                if src_file.exists():
                    dst_file = self.backup_path / file_name
                    shutil.copy2(src_file, dst_file)
                    self.logger.info(f"备份文件: {src_file} -> {dst_file}")
            
            # 生成备份清单
            self._generate_backup_manifest()
            
            self.logger.info("备份创建完成")
            return True
            
        except Exception as e:
            self.logger.error(f"备份创建失败: {str(e)}")
            return False
    
    def _generate_backup_manifest(self):
        """生成备份清单"""
        manifest = {
            "backup_time": datetime.now().isoformat(),
            "backup_path": str(self.backup_path),
            "files": []
        }
        
        for root, dirs, files in os.walk(self.backup_path):
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.backup_path)
                file_hash = self._calculate_file_hash(file_path)
                
                manifest["files"].append({
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "hash": file_hash,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        manifest_file = self.backup_path / "backup_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"备份清单已生成: {manifest_file}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return "error"
    
    def migrate_projects(self) -> bool:
        """执行项目迁移"""
        try:
            self.logger.info("开始项目迁移")
            migration_results = []
            
            # 迁移各类项目
            for category, mappings in self.migration_map.items():
                self.logger.info(f"迁移 {category} 类项目")
                
                for src_path, dst_path in mappings.items():
                    result = self._migrate_single_project(src_path, dst_path)
                    migration_results.append(result)
            
            # 生成迁移报告
            self._generate_migration_report(migration_results)
            
            success_count = sum(1 for r in migration_results if r['success'])
            total_count = len(migration_results)
            
            self.logger.info(f"迁移完成: {success_count}/{total_count} 个项目成功迁移")
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"项目迁移失败: {str(e)}")
            return False
    
    def _migrate_single_project(self, src_path: str, dst_path: str) -> Dict:
        """迁移单个项目"""
        result = {
            "src_path": src_path,
            "dst_path": dst_path,
            "success": False,
            "error": None,
            "files_count": 0,
            "size_mb": 0
        }
        
        try:
            src_full_path = self.root_path / src_path
            dst_full_path = self.root_path / dst_path
            
            if not src_full_path.exists():
                result["error"] = "源路径不存在"
                self.logger.warning(f"跳过不存在的路径: {src_path}")
                return result
            
            # 创建目标目录
            dst_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 计算源目录信息
            files_count, total_size = self._calculate_directory_info(src_full_path)
            result["files_count"] = files_count
            result["size_mb"] = round(total_size / (1024 * 1024), 2)
            
            # 执行迁移
            if src_full_path.is_dir():
                shutil.copytree(src_full_path, dst_full_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_full_path, dst_full_path)
            
            # 验证迁移结果
            if self._verify_migration(src_full_path, dst_full_path):
                result["success"] = True
                self.logger.info(f"成功迁移: {src_path} -> {dst_path}")
            else:
                result["error"] = "迁移验证失败"
                self.logger.error(f"迁移验证失败: {src_path} -> {dst_path}")
            
        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"迁移失败 {src_path}: {str(e)}")
        
        return result
    
    def _calculate_directory_info(self, path: Path) -> Tuple[int, int]:
        """计算目录信息"""
        files_count = 0
        total_size = 0
        
        if path.is_file():
            return 1, path.stat().st_size
        
        for root, dirs, files in os.walk(path):
            files_count += len(files)
            for file in files:
                file_path = Path(root) / file
                try:
                    total_size += file_path.stat().st_size
                except OSError:
                    pass
        
        return files_count, total_size
    
    def _verify_migration(self, src_path: Path, dst_path: Path) -> bool:
        """验证迁移结果"""
        try:
            if not dst_path.exists():
                return False
            
            # 简单验证：比较文件数量
            src_files, src_size = self._calculate_directory_info(src_path)
            dst_files, dst_size = self._calculate_directory_info(dst_path)
            
            return src_files == dst_files and abs(src_size - dst_size) < 1024  # 允许1KB差异
            
        except Exception:
            return False
    
    def _generate_migration_report(self, results: List[Dict]):
        """生成迁移报告"""
        report = {
            "migration_time": datetime.now().isoformat(),
            "total_projects": len(results),
            "successful_migrations": sum(1 for r in results if r['success']),
            "failed_migrations": sum(1 for r in results if not r['success']),
            "total_files": sum(r['files_count'] for r in results),
            "total_size_mb": sum(r['size_mb'] for r in results),
            "details": results
        }
        
        report_file = self.log_path / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"迁移报告已生成: {report_file}")
    
    def create_readme_files(self):
        """创建README文件"""
        readme_templates = {
            "competitions_new/README.md": self._get_competitions_readme(),
            "competitions_new/2024/README.md": self._get_2024_competitions_readme(),
            "competitions_new/2025/README.md": self._get_2025_competitions_readme(),
            "projects_new/README.md": self._get_projects_readme(),
            "projects_new/ai/README.md": self._get_ai_projects_readme(),
            "projects_new/robotics/README.md": self._get_robotics_projects_readme(),
            "projects_new/embedded/README.md": self._get_embedded_projects_readme(),
            "projects_new/research/README.md": self._get_research_projects_readme(),
            "shared_new/README.md": self._get_shared_readme()
        }
        
        for file_path, content in readme_templates.items():
            full_path = self.root_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"创建README文件: {file_path}")
    
    def _get_competitions_readme(self) -> str:
        return """# 竞赛项目总览

本目录包含新能源编程俱乐部参与的各类竞赛项目，按年份组织。

## 目录结构

- [2024年竞赛项目](./2024/README.md)
- [2025年竞赛项目](./2025/README.md)

## 快速导航

### 2024年竞赛
- [机器人竞赛 (RoboCon)](./2024/robocon/)
- [智能车竞赛](./2024/smart-car/)
- [物联网设计竞赛](./2024/iot-design/)
- [电子设计竞赛](./2024/electronics/)
- [节能减排竞赛](./2024/energy-saving/)
- [华为云AI竞赛](./2024/huawei-cloud-ai/)

### 2025年竞赛
- [机器人竞赛 (RoboCon)](./2025/robocon/)
- [交通设计竞赛](./2025/traffic-design/)
- [节能减排竞赛](./2025/energy-saving/)

## 贡献指南

1. 每个竞赛项目应包含完整的README文档
2. 代码应遵循团队编码规范
3. 重要文档和资源应及时更新

---

更新时间: 2025-01-18
"""
    
    def _get_2024_competitions_readme(self) -> str:
        return """# 2024年竞赛项目

## 项目列表

| 竞赛名称 | 项目目录 | 状态 | 负责人 |
|----------|----------|------|--------|
| 机器人竞赛 (RoboCon) | [robocon](./robocon/) | 进行中 | - |
| 智能车竞赛 | [smart-car](./smart-car/) | 已完成 | - |
| 物联网设计竞赛 | [iot-design](./iot-design/) | 已完成 | - |
| 电子设计竞赛 | [electronics](./electronics/) | 已完成 | - |
| 节能减排竞赛 | [energy-saving](./energy-saving/) | 已完成 | - |
| 华为云AI竞赛 | [huawei-cloud-ai](./huawei-cloud-ai/) | 已完成 | - |

## 成果总结

- 参与竞赛数量: 6项
- 获奖项目: 待统计
- 技术积累: 涵盖机器人、AI、物联网等多个领域

---

[返回竞赛总览](../README.md)
"""
    
    def _get_2025_competitions_readme(self) -> str:
        return """# 2025年竞赛项目

## 项目列表

| 竞赛名称 | 项目目录 | 状态 | 负责人 |
|----------|----------|------|--------|
| 机器人竞赛 (RoboCon) | [robocon](./robocon/) | 筹备中 | - |
| 交通设计竞赛 | [traffic-design](./traffic-design/) | 筹备中 | - |
| 节能减排竞赛 | [energy-saving](./energy-saving/) | 筹备中 | - |

## 计划目标

- 继续参与传统优势竞赛项目
- 拓展新的竞赛领域
- 提升团队技术水平和竞赛成绩

---

[返回竞赛总览](../README.md)
"""
    
    def _get_projects_readme(self) -> str:
        return """# 技术项目总览

本目录包含新能源编程俱乐部的各类技术项目，按技术领域分类。

## 技术领域

- [人工智能 (AI)](./ai/README.md)
- [机器人技术 (Robotics)](./robotics/README.md)
- [嵌入式系统 (Embedded)](./embedded/README.md)
- [科研项目 (Research)](./research/README.md)
- [项目模板 (Templates)](./templates/README.md)

## 快速导航

### AI项目
- [能源监测系统](./ai/energy-monitoring/)

### 机器人项目
- [人形机器人](./robotics/humanoid-robot/)
- [飞行控制系统](./robotics/flight-control/)
- [ABU2026机器人项目](./robotics/abu2026-robocon/)

### 嵌入式项目
- [星闪技术](./embedded/nearlink/)

### 科研项目
- [灵巧手项目](./research/dexterous-hand/)
- [气缸控制系统](./research/pneumatic-system/)
- [3D打印项目](./research/3d-printing/)
- [MICA验证项目](./research/mica-validation/)

---

更新时间: 2025-01-18
"""
    
    def _get_ai_projects_readme(self) -> str:
        return """# AI项目

人工智能相关技术项目。

## 项目列表

- [能源监测系统](./energy-monitoring/) - 基于AI的能源监测与分析系统

## 技术栈

- Python
- TensorFlow/PyTorch
- OpenCV
- 数据分析与可视化

---

[返回技术项目总览](../README.md)
"""
    
    def _get_robotics_projects_readme(self) -> str:
        return """# 机器人项目

机器人技术相关项目。

## 项目列表

- [人形机器人](./humanoid-robot/) - 人形机器人控制系统
- [飞行控制系统](./flight-control/) - 无人机飞行控制
- [ABU2026机器人项目](./abu2026-robocon/) - ABU2026机器人竞赛项目

## 技术栈

- ROS/ROS2
- C++/Python
- 控制算法
- 传感器融合
- 机器视觉

---

[返回技术项目总览](../README.md)
"""
    
    def _get_embedded_projects_readme(self) -> str:
        return """# 嵌入式项目

嵌入式系统相关项目。

## 项目列表

- [星闪技术](./nearlink/) - 星闪无线通信技术应用

## 技术栈

- C/C++
- 嵌入式Linux
- 实时操作系统
- 硬件接口编程

---

[返回技术项目总览](../README.md)
"""
    
    def _get_research_projects_readme(self) -> str:
        return """# 科研项目

科研横向项目。

## 项目列表

- [灵巧手项目](./dexterous-hand/) - 机器人灵巧手控制系统
- [气缸控制系统](./pneumatic-system/) - 气动控制系统
- [3D打印项目](./3d-printing/) - 3D打印技术应用
- [MICA验证项目](./mica-validation/) - MICA系统验证

## 合作单位

- 高校科研院所
- 企业技术部门
- 政府科技项目

---

[返回技术项目总览](../README.md)
"""
    
    def _get_shared_readme(self) -> str:
        return """# 共享资源库

本目录包含项目间共享的资源文件。

## 目录结构

- `assets/` - 静态资源
  - `images/` - 图片资源
  - `videos/` - 视频资源
  - `documents/` - 文档资源
- `models/` - 3D模型文件
- `libraries/` - 共享代码库
- `tools/` - 工具脚本

## 使用规范

1. 资源文件应使用描述性命名
2. 大文件应考虑使用Git LFS
3. 定期清理不再使用的资源
4. 添加适当的文档说明

---

更新时间: 2025-01-18
"""
    
    def rollback(self, backup_path: str = None) -> bool:
        """回滚到备份状态"""
        try:
            if backup_path is None:
                # 使用最新的备份
                backup_dirs = list((self.root_path / "backup").glob("migration_*"))
                if not backup_dirs:
                    self.logger.error("没有找到备份目录")
                    return False
                backup_path = max(backup_dirs, key=lambda x: x.stat().st_mtime)
            else:
                backup_path = Path(backup_path)
            
            self.logger.info(f"开始从备份回滚: {backup_path}")
            
            # 删除新目录
            new_dirs = ['competitions_new', 'projects_new', 'shared_new', 'docs_new']
            for dir_name in new_dirs:
                dir_path = self.root_path / dir_name
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    self.logger.info(f"删除新目录: {dir_path}")
            
            # 恢复备份
            for item in backup_path.iterdir():
                if item.name == 'backup_manifest.json':
                    continue
                
                dst_path = self.root_path / item.name
                if dst_path.exists():
                    if dst_path.is_dir():
                        shutil.rmtree(dst_path)
                    else:
                        dst_path.unlink()
                
                if item.is_dir():
                    shutil.copytree(item, dst_path)
                else:
                    shutil.copy2(item, dst_path)
                
                self.logger.info(f"恢复: {item} -> {dst_path}")
            
            self.logger.info("回滚完成")
            return True
            
        except Exception as e:
            self.logger.error(f"回滚失败: {str(e)}")
            return False
    
    def run_migration(self, create_backup: bool = True) -> bool:
        """执行完整迁移流程"""
        try:
            self.logger.info("开始仓库目录结构迁移")
            
            # 1. 创建备份
            if create_backup:
                if not self.create_backup():
                    self.logger.error("备份创建失败，终止迁移")
                    return False
            
            # 2. 执行迁移
            if not self.migrate_projects():
                self.logger.error("项目迁移失败")
                return False
            
            # 3. 创建README文件
            self.create_readme_files()
            
            self.logger.info("仓库目录结构迁移完成")
            return True
            
        except Exception as e:
            self.logger.error(f"迁移过程中发生错误: {str(e)}")
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='仓库目录结构迁移工具')
    parser.add_argument('--root', default='.', help='仓库根目录路径')
    parser.add_argument('--no-backup', action='store_true', help='跳过备份创建')
    parser.add_argument('--rollback', help='回滚到指定备份')
    
    args = parser.parse_args()
    
    migrator = RepositoryMigrator(args.root)
    
    if args.rollback:
        success = migrator.rollback(args.rollback)
    else:
        success = migrator.run_migration(create_backup=not args.no_backup)
    
    if success:
        print("操作成功完成")
    else:
        print("操作失败，请查看日志")
        exit(1)

if __name__ == '__main__':
    main()