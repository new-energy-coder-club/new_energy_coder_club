# HXC ESP A Board — 核心设备开发仓库

## 项目结构

```
projects/embedded/ESP32_platformio_temple_project/  ← 上游子模块 (CQUPTHXC)
projects/embedded/HXC_A_Usage_Guide.md               ← 板级开发说明
docs/guides/development-setup.md                     ← 环境搭建指南
docs/guides/vibe-coding-debug.md                     ← 调试工作流指南
```

## 常用技能

- **hxc-esp-a-board**：HXC ESP32-S3 主控板环境搭建、烧录、测试
- **clean-code-zh**：C++ 代码审查与重构
- **acad-paper-prompter**：技术文档润色

## 上游项目

- ESP32 PlatformIO 模板：https://github.com/CQUPTHXC/ESP32_platformio_temple_project
- 社区仓库：https://github.com/new-energy-coder-club/new_energy_coder_club.git

## 硬件速查

| 引脚 | 功能 |
|------|------|
| GPIO8 | CAN TX |
| GPIO18 | CAN RX |
| GPIO43 | UART0 TX |
| GPIO44 | UART0 RX |

## 快速命令

```powershell
# 编译
pio run --environment temple_project

# 烧录
pio run --target upload --environment temple_project

# 串口
pio device monitor -b 115200
```
