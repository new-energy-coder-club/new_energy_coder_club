# HXC ESP32-S3 电机控制 Demo 合集

> 三份独立可运行的电机控制调试工程，基于 ESP32-S3 + PlatformIO + Arduino。
>
> ⚠️ 这三份代码均为**调试快照 / 功能验证 Demo**，不是交付级工程。
> 代码质量不一，存在冗余和未完善之处，但每个都能独立编译烧录运行。

---

## 工程列表

### 1. hxc_a_c620 — C620 标准 CAN 调试

| 项目 | 说明 |
|------|------|
| **目标** | 用 CAN 标准帧控制 C620 电调 |
| **CAN 类型** | 标准帧（11-bit ID） |
| **控制方式** | 电流给定，速度环为 ESP32 软件外环 |
| **命令接口** | `r`(速度)、`i`(电流)、`s`(停机)、`scan`(扫描)、`diag`(诊断) |
| **安全** | 上电 listen-only 模式，不发控制帧 |

**典型场景**：单 C620 起转、电流/速度环调试、CAN 接线排错。

---

### 2. hcx_a_n630 — N630/VESC 扩展 CAN 位控

| 项目 | 说明 |
|------|------|
| **目标** | 用 CAN 扩展帧驱动 N630(VESC)，主控做位置闭环 |
| **CAN 类型** | 扩展帧（EID = packet_id<<8 \| controller_id） |
| **控制方式** | 主控只发 `CAN_PACKET_SET_CURRENT`，N630 做电流执行器 |
| **位置环** | 轨迹规划 + PID + 速度阻尼 + 静摩擦补偿 + 多圈展开 |
| **命令接口** | `p`(抱持)、`p deg`(绝对移动)、`r deg`(相对移动)、`c A`(开环电流)、`s`(停机) |

**⚠️ 重要**：N630 侧 VESC 上位机必须勾选 Status 4 / Status 5 并写入 App Configuration，否则收不到位置反馈。

**典型场景**：N630 位置控制、夹爪/执行器开发。

---

### 3. am32_board_a — AM32 DSHOT 驱动 + BoardA 模块库

| 项目 | 说明 |
|------|------|
| **目标** | 用 DSHOT300 数字协议驱动 AM32 电调（FLYROUN） |
| **开发历程** | 阶段二：正反转验证 ✅ → 阶段三：四轮小车 ✅ → 遥控+缓冲 ✅ |
| **DSHOT 驱动** | 基于 ESP32 RMT 外设（兼容 IDF 4.x，非 DShotRMT 库） |
| **小车功能** | 四路独立电机、串口控制、HotRC 遥控、缓冲模式、失控保护 |
| **模块库** | `module/` 内含 16 个可复用模块（HXCthread、VOFA、ESP-NOW 等） |

**典型场景**：AM32 替代 C620、四轮底盘调试、模块化库参考。

---

## 硬件共性

| 参数 | 值 |
|------|-----|
| MCU | ESP32-S3-DevKitC-1 (N16R8) |
| Flash | 16MB（⚠️ 必须配 16MB，默认 8MB 导致重启） |
| PSRAM | 8MB (OPI) |
| CAN TX/RX | GPIO8 / GPIO18 |
| UART0 | RX=GPIO44, TX=GPIO43 |
| USB CDC | 原生 USB（Serial），无 CH340 |
| 串口波特率 | 115200 |

## 已知问题 / 未完善项

### C620
- `src/main.cpp` 尚未按模块拆分，所有逻辑在单文件中
- 速度环参数未做 NVS 保存

### N630
- N630 波特率不应写死，调试前需接 VESC 上位机确认
- 缺少软限位保护
- 单文件 main.cpp 未拆分

### AM32
- 四轮底盘左转/右转方向与实际遥控操作相反（已知 bug，暂不修复）
- `VOFA` 参数名 `F` 不带数值时默认替换为 10%（若想精确 1% 不生效）
- GPIO12 在经典 ESP32 是 strapping 脚，但 ESP32-S3 无此限制（已在日志中修正）

## 目录结构

```
motor-demos/
├── README.md                 ← 本文件
├── hxc_a_c620/               ← C620 标准 CAN 调试工程
│   ├── src/main.cpp
│   ├── platformio.ini
│   ├── merge_bins.py
│   └── .gitignore
├── hcx_a_n630/               ← N630 VESC 扩展 CAN 位控工程
│   ├── src/main.cpp
│   ├── platformio.ini
│   └── merge_bins.py
└── am32_board_a/             ← AM32 DSHOT + BoardA 模块库
    ├── src/main.cpp
    ├── module/               ← 16 个可复用模块（核心资产）
    ├── platformio.ini
    └── .gitignore
```

## 参考文档

- `../hxc-motor-control-projects-skill.md` — 综合 SKILL 文档，含完整命令表、参数和开发规则
- `../HXC_A_Usage_Guide.md` — [已删除，内容合并至上方 SKILL 文档]

## License

各子工程沿用原始开源协议（MIT）。BoardA 模块库遵循 MIT License。
