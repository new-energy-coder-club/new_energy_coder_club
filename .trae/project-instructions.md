# HXC ESP A Board — Trae IDE 项目配置

> Trae IDE 项目指令，用于 AI 辅助嵌入式开发

## 项目信息

- **项目名称:** HXC ESP A Board
- **分支:** SKill
- **硬件:** ESP32-S3 (N16R8), CAN TWAI 1Mbps

## 项目结构

```
projects/embedded/ESP32_platformio_temple_project/  ← 固件主项目 (PlatformIO)
projects/embedded/HXC_A_Usage_Guide.md               ← 板级说明
docs/guides/development-setup.md                     ← 环境搭建
docs/guides/vibe-coding-debug.md                     ← 调试指南
skills/                                              ← Claude Code Skills (50个)
```

## 常用技能

Trae IDE 已安装的技能与本仓库 `skills/` 目录可共享使用：

| Skill | 用途 |
|-------|------|
| `lark-*` | 飞书办公自动化 |
| `baidu-search` | 百度搜索 |
| `pv-storage-bom` | 光伏储能 BOM |
| `study-habits` | 学习管理 |

完整技能列表参见 [skill-config.json](../../.trae/skill-config.json) 或 README 的 Skills 章节。

## 编译命令

```powershell
cd projects/embedded/ESP32_platformio_temple_project
pio run --environment temple_project                    # 编译
pio run --target upload --environment temple_project    # 烧录
pio device monitor -b 115200                            # 串口监视
```

## 调试技巧

- 使用 Vibe Coding 工作流快速迭代: 参见 `docs/guides/vibe-coding-debug.md`
- 多机协作时注意 COM 口占用
- 烧录后检查串口输出确认固件启动
