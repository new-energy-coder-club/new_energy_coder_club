#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化目录结构重组脚本
实现"两次点击原则"的目录扁平化
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def backup_before_migration(root_path):
    """迁移前备份"""
    backup_dir = Path(root_path) / "backup" / f"pre_restructure_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 备份主要目录
    for dir_name in ['competitions', 'projects', 'shared']:
        src = Path(root_path) / dir_name
        if src.exists():
            dst = backup_dir / dir_name
            try:
                shutil.copytree(src, dst)
            except Exception as e:
                print(f"备份失败 {src}: {e}")
            print(f"已备份: {src} -> {dst}")
    
    return backup_dir

def move_project_safely(src, dst, root_path):
    """安全移动项目"""
    src_path = Path(root_path) / src
    dst_path = Path(root_path) / dst
    
    if not src_path.exists():
        print(f"源路径不存在: {src}")
        return False
    
    # 创建目标目录
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 处理冲突
    if dst_path.exists():
        print(f"目标路径已存在: {dst}")
        # 可以选择合并或重命名
        dst_path = dst_path.parent / f"{dst_path.name}_migrated"
    
    try:
        shutil.move(str(src_path), str(dst_path))
        print(f"已移动: {src} -> {dst}")
        return True
    except Exception as e:
        print(f"移动失败 {src} -> {dst}: {e}")
        return False

def main():
    root_path = os.getcwd()
    print(f"开始重组目录结构: {root_path}")
    
    # 备份
    backup_dir = backup_before_migration(root_path)
    print(f"备份完成: {backup_dir}")
    
    # 执行迁移计划
    migration_plan = [
    {
        "type": "cleanup_archive",
        "description": "清理archive目录中的冗余嵌套结构",
        "priority": "high"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\ai-huawei-cloud\\2024华为云AI挑战赛",
        "target": "competitions/2024-ai-huawei-cloud",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\ai-huawei-cloud\\huawei-cloud-ai",
        "target": "competitions/2024-ai-huawei-cloud",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\ai-huawei-cloud\\huawei-cloud-ai\\project-2024",
        "target": "competitions/2024-ai-huawei-cloud",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\electronics-competition\\2024电赛预选-EB25-SIG",
        "target": "competitions/2024-electronics-competition",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\electronics-competition\\2024电赛预选-EB25-SIG\\chinese-project",
        "target": "competitions/2024-electronics-competition",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\electronics-competition\\electronics",
        "target": "competitions/2024-electronics-competition",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\electronics-competition\\electronics\\project-2024",
        "target": "competitions/2024-electronics-competition",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\electronics-competition\\electronics\\project-2024\\chinese-project",
        "target": "competitions/2024-electronics-competition",
        "reason": "减少目录深度从 5 到 2",
        "priority": "high"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\energy-saving-competition\\2024节能减排-NearLink组",
        "target": "competitions/2024-energy-saving-competition",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\energy-saving-competition\\2024节能减排-NearLink组\\chinese-project",
        "target": "competitions/2024-energy-saving-competition",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\energy-saving-competition\\energy-saving",
        "target": "competitions/2024-energy-saving-competition",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\energy-saving-competition\\energy-saving\\project-2024",
        "target": "competitions/2024-energy-saving-competition",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\energy-saving-competition\\energy-saving\\project-2024\\chinese-project",
        "target": "competitions/2024-energy-saving-competition",
        "reason": "减少目录深度从 5 到 2",
        "priority": "high"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\iot-design-competition\\iot-design",
        "target": "competitions/2024-iot-design-competition",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\iot-design-competition\\iot-design\\project-2024",
        "target": "competitions/2024-iot-design-competition",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\iot-design-competition\\iot-design\\project-2024\\chinese-project",
        "target": "competitions/2024-iot-design-competition",
        "reason": "减少目录深度从 5 到 2",
        "priority": "high"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\iot-design-competition\\iot-design-huawei",
        "target": "competitions/2024-iot-design-competition",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\iot-design-competition\\iot-design-huawei\\project-2024",
        "target": "competitions/2024-iot-design-competition",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\iot-design-competition\\iot-design-huawei\\project-2024\\chinese-project",
        "target": "competitions/2024-iot-design-competition",
        "reason": "减少目录深度从 5 到 2",
        "priority": "high"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\other-competitions\\competition",
        "target": "competitions/2024-other-competitions",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\robotics-robocon\\2024Robocon机器人大赛",
        "target": "competitions/2024-robotics-robocon",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\robotics-robocon\\2024Robocon机器人大赛\\chinese-project",
        "target": "competitions/2024-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\robotics-robocon\\robocon",
        "target": "competitions/2024-robotics-robocon",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\robotics-robocon\\robocon\\project-2024",
        "target": "competitions/2024-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\robotics-robocon\\robocon\\project-2024\\chinese-project",
        "target": "competitions/2024-robotics-robocon",
        "reason": "减少目录深度从 5 到 2",
        "priority": "high"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\robotics-robocon\\smart-car",
        "target": "competitions/2024-robotics-robocon",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\robotics-robocon\\smart-car\\project-2024",
        "target": "competitions/2024-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\robotics-robocon\\smart-car-outdoor",
        "target": "competitions/2024-robotics-robocon",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2024\\robotics-robocon\\smart-car-outdoor\\project-2024",
        "target": "competitions/2024-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\energy-saving\\project-2025",
        "target": "competitions/2025-energy-saving",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\energy-saving\\project-2025\\chinese-project",
        "target": "competitions/2025-energy-saving",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\energy-saving\\project-2025\\chinese-project_1",
        "target": "competitions/2025-energy-saving",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\energy-saving\\project-2025\\chinese-project_2",
        "target": "competitions/2025-energy-saving",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\energy-saving-competition\\2025节能减排-DUMA组",
        "target": "competitions/2025-energy-saving-competition",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\energy-saving-competition\\2025节能减排-DUMA组\\chinese-project",
        "target": "competitions/2025-energy-saving-competition",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\energy-saving-competition\\2025节能减排-DUMA组\\chinese-project_1",
        "target": "competitions/2025-energy-saving-competition",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\energy-saving-competition\\2025节能减排-DUMA组\\chinese-project_2",
        "target": "competitions/2025-energy-saving-competition",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\iot-design-competition\\2025物联网设计竞赛",
        "target": "competitions/2025-iot-design-competition",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project\\chinese-project",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 5 到 2",
        "priority": "high"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project_1",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project_2",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project_3",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project_4",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project_5",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project_6",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project_7",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robocon\\project-2025\\chinese-project_8",
        "target": "competitions/2025-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project\\chinese-project",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 5 到 2",
        "priority": "high"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project_1",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project_2",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project_3",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project_4",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project_5",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project_6",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project_7",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\robotics-robocon\\2025Robocon机器人大赛\\chinese-project_8",
        "target": "competitions/2025-robotics-robocon",
        "reason": "减少目录深度从 4 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "competitions\\2025\\traffic-design\\project-2025",
        "target": "competitions/2025-traffic-design",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\ai\\energy-monitoring\\20250319-fluid-workstation",
        "target": "projects/ai/energy-monitoring",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\embedded\\nearlink\\project-20250426",
        "target": "projects/embedded/nearlink",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\docs\\source",
        "target": "projects/research/docs",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\meta-rtthread\\conf",
        "target": "projects/research/meta-rtthread",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\meta-rtthread\\recipes-kernel",
        "target": "projects/research/meta-rtthread",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\mica-validation\\docs",
        "target": "projects/research/mica-validation",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\mica-validation\\gcc-arm-none-eabi",
        "target": "projects/research/mica-validation",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\mica-validation\\meta-rtthread",
        "target": "projects/research/mica-validation",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\research\\3d-printing-sig",
        "target": "projects/research/research",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\research\\dexterous-hand",
        "target": "projects/research/research",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\research\\image",
        "target": "projects/research/research",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\research\\mica-validation",
        "target": "projects/research/research",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\research\\pneumatic-system",
        "target": "projects/research/research",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\research\\电控组-RC5-RM1\\image",
        "target": "projects/research/电控组-RC5-RM1",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\robotics\\humanoid-robot\\人形机器人主线",
        "target": "projects/robotics/humanoid-robot",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "projects\\templates\\ai_project_template\\config",
        "target": "projects/misc/config",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "shared\\assets\\images\\competition",
        "target": "shared/assets/images",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "shared\\assets\\images\\equipment",
        "target": "shared/assets/images",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "shared\\assets\\images\\Image",
        "target": "shared/assets/images",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "shared\\assets\\images\\others",
        "target": "shared/assets/images",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "shared\\assets\\images\\project",
        "target": "shared/assets/images",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "shared\\assets\\images\\screenshots",
        "target": "shared/assets/images",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "shared\\assets\\images\\team",
        "target": "shared/assets/images",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "shared\\assets\\images\\technical",
        "target": "shared/assets/images",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    },
    {
        "type": "move_project",
        "source": "shared\\assets\\images\\wechat_images",
        "target": "shared/assets/images",
        "reason": "减少目录深度从 3 到 2",
        "priority": "medium"
    }
]
    
    success_count = 0
    for action in migration_plan:
        if action['type'] == 'move_project':
            if move_project_safely(action['source'], action['target'], root_path):
                success_count += 1
    
    print(f"\n重组完成: {success_count}/{len([a for a in migration_plan if a['type'] == 'move_project'])} 个项目成功迁移")
    print(f"备份位置: {backup_dir}")

if __name__ == "__main__":
    main()
