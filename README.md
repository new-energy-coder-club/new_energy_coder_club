# NEC Motor Control 电机控制资源集

> New Energy Coder Club · 电机控制方向 skill 与工程模板合集

从 NEC 主仓 `SKill` 分支独立出来的电机控制专项分支，面向机器人电控、电机调试与嵌入式驱动开发场景。

## 📁 目录结构

```
├── skills/            # Agent Skills（调试/控制指南）
│   └── ak10-motor-debug/          # Cubemars AK10-9 电机 MIT/CAN 控制调试指南
├── projects/          # 可编译的参考工程
│   ├── motor-demos/
│   │   ├── am32_board_a/          # AM32 电调工程（STM32）
│   │   │   └── module/            # DSHOT、EMM V5.0 步进闭环、SBUS/DBUS、
│   │   │                          # 舵机、底盘解算（麦克纳姆/舵轮）、
│   │   │                          # ESP-NOW、PCNT 编码器、VOFA 调试等模块
│   │   └── hcx_a_n630/            # HXC N630 板 PlatformIO 工程（含 merge_bins.py）
│   └── ESP32_platformio_temple_project/   # ESP32 PlatformIO 工程模板
└── docs/              # 说明文档
    └── hxc-motor-control-projects-skill.md   # HXC 电机控制项目 skill 说明
```

## 🚀 快速开始

### AK10-9 电机调试（skill）

`skills/ak10-motor-debug/SKILL.md` 覆盖：

- 上电首次 CAN 通信检查、使能/置零
- 速度 / 位置 / MIT 模式控制帧发送
- 反馈解析与丢反馈诊断、飞车/饱和排查

关键参数速查：Motor ID `1–8`，位置 `±12.56 rad`，速度 `±60 rad/s`，力矩 `±12 N·m`。

### 编译 motor-demos

```bash
# 需要安装 PlatformIO
cd projects/motor-demos/am32_board_a
pio run
```

## 🔗 相关分支

| 分支 | 内容 |
|---|---|
| [`SKill`](https://github.com/new-energy-coder-club/new_energy_coder_club/tree/SKill) | 全量 160+ Agent Skills |
| `motor-control`（本分支） | 电机控制专项合集 |

## 🤝 贡献

欢迎提交电机驱动、调试工具类 skill 与工程模板。新增内容请遵循现有目录分类：调试指南进 `skills/`，可编译工程进 `projects/`，说明文档进 `docs/`。
