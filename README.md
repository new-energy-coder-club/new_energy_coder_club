# NEC Motor Control 电机控制资源集

> New Energy Coder Club · 电机控制方向 skill 与工程模板合集

从 NEC 主仓 `SKill` 分支独立出来的电机控制专项分支，面向机器人电控、电机调试与嵌入式驱动开发场景。

## 📁 目录导航

| 路径 | 内容 | 适用场景 |
|---|---|---|
| [`skills/ak10-motor-debug/`](skills/ak10-motor-debug/) | Cubemars AK10-9 电机 MIT/CAN 控制调试指南 | AK 系列电机上电调试、丢反馈/飞车诊断 |
| [`skills/hxc-esp-a-board/`](skills/hxc-esp-a-board/) | HXC ESP32-S3 主控板开发环境自动化配置 skill | PlatformIO 编译/烧录/串口调试一键工作流 |
| [`boards/am32_board_a/`](boards/am32_board_a/) | AM32 电调工程（STM32） | DSHOT、EMM V5.0 步进闭环、SBUS/DBUS、麦克纳姆/舵轮底盘解算、ESP-NOW、VOFA 调试 |
| [`boards/hcx_a_n630/`](boards/hcx_a_n630/) | HXC N630 板 PlatformIO 工程 | N630 板固件开发（含 `merge_bins.py` 合并烧录） |
| [`boards/hxc_a_c620/`](boards/hxc_a_c620/) | HXC A 板 + C620 电调工程 | RoboMaster C620 电调控制开发 |
| [`boards/hxc_wireless_flash/`](boards/hxc_wireless_flash/) | HXC 无线烧录 + 串口控制工程 | 无线烧录（禁用自动复位）、UART0 串口控制 |
| [`boards/hxc-motor-control-projects-skill.md`](boards/hxc-motor-control-projects-skill.md) | HXC 电机控制项目 skill 总说明 | 了解 HXC 系列板卡与项目全貌 |
| [`templates/esp32_platformio/`](templates/esp32_platformio/) | ESP32 PlatformIO 工程模板 | 新项目起步脚手架 |

## 🚀 快速开始

### AK10-9 电机调试（skill）

`skills/ak10-motor-debug/SKILL.md` 覆盖：

- 上电首次 CAN 通信检查、使能/置零
- 速度 / 位置 / MIT 模式控制帧发送
- 反馈解析与丢反馈诊断、飞车/饱和排查

关键参数速查：Motor ID `1–8`，位置 `±12.56 rad`，速度 `±60 rad/s`，力矩 `±12 N·m`。

### 编译板级工程

```bash
# 需要安装 PlatformIO
cd boards/am32_board_a
pio run
```

### 用模板起新项目

```bash
cp -r templates/esp32_platformio my_motor_project
cd my_motor_project && pio run
```

## 🔗 相关分支

| 分支 | 内容 |
|---|---|
| [`SKill`](https://github.com/new-energy-coder-club/new_energy_coder_club/tree/SKill) | 全量 160+ Agent Skills |
| `motor-control`（本分支） | 电机控制专项合集 |

## 🤝 贡献

欢迎提交电机驱动、调试工具类 skill 与工程模板。新增内容请遵循现有目录分类：

- 调试/控制指南 → `skills/`
- 可编译板级工程 → `boards/<板名>/`（目录名用 ASCII）
- 工程模板 → `templates/`
