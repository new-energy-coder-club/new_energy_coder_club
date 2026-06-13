# Embedded — HXC 嵌入式开发项目

> HXC 战队 ESP32-S3 主控板（Board A）核心开发目录

## 📋 目录内容

| 路径 | 说明 |
|------|------|
| `HXC_A_Usage_Guide.md` | HXC_A 板级开发使用说明（推荐先读） |
| `ESP32_platformio_temple_project/` | ⬆️ 上游子模块 — CQUPTHXC 的 ESP32 PlatformIO 模板项目 |

**上游项目：** https://github.com/CQUPTHXC/ESP32_platformio_temple_project

## 🚀 快速开始

```powershell
# 编译
cd ESP32_platformio_temple_project
pio run --environment temple_project

# 烧录
pio run --target upload --environment temple_project

# 串口监视
pio device monitor -b 115200
```

## 🛠️ 开发指南

- [环境搭建指南](../../docs/guides/development-setup.md) — 新设备从零搭建
- [Vibe Coding 调试指南](../../docs/guides/vibe-coding-debug.md) — 跨工作区调试工作流
- [HXC_A 使用说明](HXC_A_Usage_Guide.md) — 板级详细使用说明

## 📌 硬件配置速查

| 参数 | 值 |
|------|-----|
| MCU | ESP32-S3 (rev v0.2) |
| Flash | 16MB (QIO OPI) |
| PSRAM | 8MB |
| CAN TX | GPIO8 |
| CAN RX | GPIO18 |
| 串口 | USB CDC (115200, 8N1) |

---

*HXC 战队 — 常州工学院 NEC 机器人团队*
