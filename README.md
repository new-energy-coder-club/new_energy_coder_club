# HXC ESP A Board — 核心设备仓库 🚀

> HXC 战队 ESP32-S3 主控板（Board A）开发环境搭建、固件烧录、电机调试

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 分支定位

本分支 (`SKill`) 是 **HXC ESP A Board 核心设备维护仓库**，用于：

| 场景 | 说明 |
|------|------|
| 🆕 **新设备环境搭建** | 从零搭建 PlatformIO + ESP32-S3 开发环境 |
| 🔧 **固件开发与调试** | 基于上游模板进行位控/电流/位置控制开发 |
| 🔄 **跨工作区协作** | Vibe Coding 多机调试、代码同步 |
| 📚 **设备文档维护** | 板级使用说明、硬件参数、调试技巧 |

## 📋 目录结构

```
📦 new_energy_coder_club (SKill)
├── 📁 projects/embedded/
│   ├── 📄 HXC_A_Usage_Guide.md              ← 板级开发使用说明（必读）
│   ├── 📁 ESP32_platformio_temple_project/  ← ⬆️ 上游子模块
│   └── 📄 README.md                         ← 嵌入式项目入口
├── 📁 docs/guides/
│   ├── 📄 development-setup.md              ← 新设备环境搭建
│   └── 📄 vibe-coding-debug.md              ← 跨工作区调试工作流
├── 📁 competitions/                         ← 竞赛项目存档
├── 📁 projects/                             ← 其他项目
├── 📁 shared/                               ← 共享资源
├── 📁 tools/                                ← 开发工具
└── 📁 .atomcode/
    └── 📄 project-instructions.md           ← AtomCode 项目指令
```

## ⬆️ 上游项目

| 项目 | 链接 | 说明 |
|------|------|------|
| ESP32 PlatformIO 模板 | [CQUPTHXC/ESP32_platformio_temple_project](https://github.com/CQUPTHXC/ESP32_platformio_temple_project) | 作为 git submodule 引用，`projects/embedded/` 下 |
| 社区主仓库 | [new-energy-coder-club](https://github.com/new-energy-coder-club/new_energy_coder_club.git) | 社区同步 |

## 🚀 快速开始

### 克隆仓库

```powershell
git clone -b SKill https://gitee.com/darrenpig/new_energy_coder_club.git
cd new_energy_coder_club
git submodule update --init --recursive
```

### 编译 & 烧录

```powershell
cd projects\embedded\ESP32_platformio_temple_project

# 编译
pio run --environment temple_project

# 烧录（自动检测 COM 口）
pio run --target upload --environment temple_project
```

### 串口调试

```powershell
# 串口监视
pio device monitor -b 115200

# 发送指令（停止电机）
python send_cmd.py "s"
```

## 🛠️ 开发入口速查

| 目标 | 入口 | 推荐文档 |
|------|------|----------|
| 第一次搭建环境 | → [环境搭建指南](docs/guides/development-setup.md) | 前置依赖、安装步骤、验证清单 |
| 快速调试电机 | → [Vibe Coding 调试](docs/guides/vibe-coding-debug.md) | 调试工作流、命令速查、故障处理 |
| 理解板级设计 | → [HXC_A 使用说明](projects/embedded/HXC_A_Usage_Guide.md) | 硬件参数、CAN/串口约定、三类工程用法 |

## 🤖 硬件参数速查

| 参数 | 值 |
|------|-----|
| **MCU** | ESP32-S3 (rev v0.2, N16R8) |
| **Flash / PSRAM** | 16MB / 8MB |
| **CAN TX / RX** | GPIO8 / GPIO18 |
| **串口** | USB CDC (115200, 8N1) |
| **CAN 协议** | TWAI 1Mbps (经典 CAN) |

## 🔌 常用命令

```powershell
pio run --environment temple_project                    # 编译
pio run --target upload --environment temple_project    # 烧录
pio device monitor -b 115200                            # 串口监视
python send_cmd.py "c 0.3"                              # 电流模式 0.3A
python send_cmd.py "p 90"                               # 绝对位置 90°
python send_cmd.py "s"                                  # 停止
```

## 🧩 关联 AtomCode Skill

| Skill | 用途 | 加载 |
|-------|------|------|
| `hxc-esp-a-board` | HXC 环境搭建/烧录/测试全流程 | `use_skill hxc-esp-a-board` |
| `clean-code-zh` | 代码审查与重构 | `use_skill clean-code-zh` |
| `baidu-search` | 技术资料/芯片手册搜索 | `use_skill baidu-search` |

## 📄 许可证

本项目采用 MIT 许可证 — 查看 [LICENSE](LICENSE) 文件了解详情。

---

<div align="center">
  <strong>HXC 战队 · 常州工学院 NEC 机器人团队</strong><br>
  <img src="https://img.shields.io/badge/Made%20with-ESP32--S3-red.svg" alt="ESP32-S3">
  <img src="https://img.shields.io/badge/Platform-PlatformIO-blue.svg" alt="PlatformIO">
</div>
