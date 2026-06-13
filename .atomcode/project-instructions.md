# ESP32 PlatformIO 模板项目 — HXC 战队

> HXC 战队标准 ESP32 PlatformIO 项目模板工程

## 项目结构

```
src/                    ← 主要代码 (main.cpp)
include/                ← 头文件
lib/                    ← 外部库
test/                   ← 测试代码
platformio.ini           ← PlatformIO 配置
merge_bins.py            ← 固件合并脚本
.github/workflows/       ← CI/CD 自动编译
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

# 串口监视
pio device monitor -b 115200
```
