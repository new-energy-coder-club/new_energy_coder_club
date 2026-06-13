# HXC 跨工作 Vibe Coding 调试指南

> 在多个工作区间/环境间流畅切换，调试 HXC ESP A Board 固件与电机控制。

## 1️⃣ 工作区结构

推荐的工作区组织方式：

```
D:\HXC\                     # HXC 工作根目录（自定义）
├── new_energy_coder_club\  # SKill 分支（核心设备仓库）
│   ├── projects\embedded\
│   │   ├── HXC_A_Usage_Guide.md
│   │   └── ESP32_platformio_temple_project\  # ← 子模块（上游项目）
│   ├── docs\guides\        # 开发文档
│   └── shared\             # 共享资源
├── gripper_debug\          # 夹爪/混合集成调试工程（可选）
└── HXC_A_C620\             # C620 单电机调试工程（可选）
```

## 2️⃣ VSCode 工作区配置

创建 `.code-workspace` 文件实现多项目统一管理：

```json
{
  "folders": [
    { "name": "SKill", "path": "D:\\HXC\\new_energy_coder_club" },
    { "name": "ESP32", "path": "D:\\HXC\\new_energy_coder_club\\projects\\embedded\\ESP32_platformio_temple_project" }
  ],
  "settings": {
    "terminal.integrated.defaultProfile.windows": "PowerShell",
    "files.associations": {
      "*.cpp": "cpp",
      "*.h": "cpp"
    }
  }
}
```

## 3️⃣ 多环境切换速查

### 切换 Git 工作树

```powershell
# SKill 分支工作
cd D:\HXC\new_energy_coder_club
git checkout SKill

# 子模块更新
git submodule update --remote projects/embedded/ESP32_platformio_temple_project

# 上游 ESP32 项目工作
cd D:\HXC\new_energy_coder_club\projects\embedded\ESP32_platformio_temple_project
git checkout main
git pull origin main
```

### 切换 COM 口配置

当在不同电脑/环境间切换时，ESP32-S3 COM 口可能变化：

```powershell
# 自动检测 COM 口脚本（保存为 find_com.py）
python -c "
import serial.tools.list_ports as lp
ports = [p for p in lp.comports() if '303A' in (p.hwid or '')]
if ports:
    for p in ports:
        print(f'{p.device} - {p.description}')
else:
    print('未找到 ESP32-S3')
"
```

## 4️⃣ Vibe Coding 调试工作流

### 4.1 快速迭代循环

```
写代码 → 构建 → 烧录 → 串口观察 → 调整参数 → 重复
```

**每条命令速查：**

| 步骤 | 命令 |
|------|------|
| 编译 | `pio run --environment temple_project` |
| 烧录 | `pio run --target upload --environment temple_project` |
| 串口监视 | `pio device monitor -b 115200` |
| 发送指令 | `python send_cmd.py "c 0.3"` |
| 检测 COM | `python -c "import serial.tools.list_ports as lp; print([p.device for p in lp.comports() if '303A' in (p.hwid or '')])"` |

### 4.2 三屏工作区推荐

| 屏幕 | 用途 | 内容 |
|------|------|------|
| 🖥️ 主屏 | 代码编辑 | VSCode + PlatformIO |
| 📺 副屏左 | 串口监视 | `pio device monitor` 或串口工具 |
| 📺 副屏右 | 参考文档 | HXC_A_Usage_Guide.md + 浏览器 |

### 4.3 调试三板斧

```python
# 1. 停止所有电机（安全第一）
send: s

# 2. 检查状态（确认 CAN 通信正常）
#    关注: tx/rx 持续递增, erpm≈0, vin≈22.9V

# 3. 低电流测试（0.3A 安全起转）
send: c 0.3
```

## 5️⃣ AtomCode 跨工作区 Skill 管理

### 5.1 加载 HXC 专用 Skill

```powershell
# 在任意工作区使用
use_skill hxc-esp-a-board
```

### 5.2 常用 Skill 速查表

| Skill 名称 | 用途 | 触发场景 |
|-----------|------|----------|
| `hxc-esp-a-board` | HXC ESP32-S3 环境搭建/烧录/测试 | 新设备搭建、烧录固件、电机测试 |
| `clean-code-zh` | 代码审查与重构 | 提交前审查、重构 C++ 代码 |
| `acad-paper-prompter` | 技术文档润色 | 写 README、设计文档、竞赛说明 |
| `baidu-search` | 技术资料搜索 | 查芯片手册、协议文档、开源库 |
| `news` | 行业资讯 | 查竞赛动态、技术趋势 |
| `web-design` | 网页部署 | 制作调试仪表盘、竞赛展示页 |

### 5.3 快速加载所有 HXC 相关 Skill

```powershell
# 一键加载 HXC 开发环境
use_skill hxc-esp-a-board
use_skill clean-code-zh
```

## 6️⃣ Git 多仓库协作

### 6.1 同步上游改动

```powershell
# 更新上游 ESP32 项目
cd projects\embedded\ESP32_platformio_temple_project
git pull origin main

# 更新 SKill 分支自身
cd D:\HXC\new_energy_coder_club
git pull origin SKill

# 提交子模块更新
git add projects/embedded/ESP32_platformio_temple_project
git commit -m "chore: update ESP32 submodule to latest"
git push origin SKill
```

### 6.2 在 SKill 分支中修改子模块

```powershell
# 进入子模块，创建特性分支
cd projects\embedded\ESP32_platformio_temple_project
git checkout -b feat/my-feature

# 修改代码后提交
git add .
git commit -m "feat: add my feature"

# 推送到上游
git push origin feat/my-feature

# 回到 SKill 分支，更新子模块引用
cd D:\HXC\new_energy_coder_club
git add projects/embedded/ESP32_platformio_temple_project
git commit -m "chore: update submodule to feat/my-feature"
```

## 7️⃣ 紧急情况处理

| 情况 | 操作 |
|------|------|
| 电机异常运转 | 立即拔掉电源或发送 `s` |
| CAN 总线挂死 | 重新上电 N630 驱动器 |
| 固件刷死 | 进入下载模式重新烧录 |
| COM 口找不到 | 换 USB 口 + 重启板子 |
| 代码冲突 | `git stash` 后 `git pull --rebase` |

---

*最后更新: 2026-06-08*
