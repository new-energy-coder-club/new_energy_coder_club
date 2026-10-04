# HXC 电机控制项目 — 三套工程模板 & AM32 开发 Skill

## 概述

综合三个电机控制项目（`HXC_A_C620`、`HCX_A_N630`、`AM32`）的文档和经验沉淀。涵盖基于 **ESP32-S3 + PlatformIO + Arduino** 的电机驱动开发全链路：C620 标准 CAN 调试、N630/VESC 扩展 CAN 位控开发、AM32 DSHOT 数字协议驱动，以及 BoardA 模块化库的使用。

## 前置条件

- ESP32-S3-DevKitC-1（N16R8：16MB Flash + 8MB PSRAM）
- Visual Studio Code + PlatformIO 插件
- 对应硬件：C620 电调 / N630(VESC) 电调 / AM32(FLYROUN) 电调
- USB 数据线（支持数据传输）

## 硬件平台共性

| 参数 | 值 |
|------|-----|
| **MCU** | ESP32-S3 |
| **板型** | ESP32-S3-DevKitC-1 (N16R8) |
| **Flash** | 16MB（⚠️ 模板默认 8MB 是错的，必须修改） |
| **PSRAM** | 8MB (OPI) |
| **CAN TX** | GPIO8 |
| **CAN RX** | GPIO18 |
| **串口 UART0** | RX=GPIO44, TX=GPIO43 |
| **USB CDC** | GPIO19/20 原生 USB，代码中用 `Serial` |
| **串口波特率** | 115200 |

### PlatformIO 正确配置（关键踩坑）

```ini
[env:temple_project]
platform = espressif32
framework = arduino
board = esp32-s3-devkitc-1

; ⚠️ N16R8 模组必须配 16MB，否则导致 rst:0x3 (RTC_SW_SYS_RST) 反复重启
board_build.flash_size = 16MB
board_build.partitions = default_16MB.csv
board_build.arduino.memory_type = qio_opi

build_flags =
    -DARDUINO_USB_CDC_ON_BOOT=1
    -D CORE_DEBUG_LEVEL=ARDUHAL_LOG_LEVEL_VERBOSE

monitor_speed = 115200
```

### 串口约定

- `Serial` = USB CDC（原生 USB，无 CH340）
- `Serial0` = UART0 (GPIO43/44) — 无线烧录器/外部串口链路
- 初始化：`Serial0.begin(115200, SERIAL_8N1, 44, 43);`
- USB CDC 枚举较慢，Python 读串口前需 `time.sleep(3)`

### 无线烧录配置

无线 DAP-Link 缺少 DTR/RTS 信号，需手动进入下载模式：

```ini
upload_protocol = esptool
upload_flags =
    --before=no_reset      ; 禁用自动复位
    --after=hard_reset
    --connect-attempts=10  ; 适应无线延迟
    --baud=115200
```

**烧录步骤**：按住 BOOT → 按一下 EN → 继续按住 BOOT → 执行 `pio run -t upload` → 看到 `Connecting...` 后松手。

---

## 项目一：HXC_A_C620 — 单 C620 调试模板

### 用途

单 C620 电调起转、电流环/速度环调试、电机 ID 排查、CAN 接线排错。

### CAN 约定

| 参数 | 值 |
|------|-----|
| CAN 帧类型 | 标准帧（11-bit） |
| 波特率 | `TWAI_TIMING_CONFIG_1MBITS()` |
| 控制 ID（电机 1~4） | `0x200` |
| 控制 ID（电机 5~8） | `0x1FF` |
| 反馈 ID | `0x200 + motor_id` |

控制本质：通过 CAN 发**电流给定**。"速度模式"是 ESP32 侧基于反馈转速做的软件外环。

### 串口命令

| 命令 | 含义 | 示例 |
|------|------|------|
| `r <value>` | 速度模式 | `r 3000` |
| `i <value>` | 电流模式 | `i 3.5` |
| `l <value>` | 限流 | `l 8` |
| `s` | 停机 | `s` |
| `scan` | 扫描可能的电机 ID | `scan` |
| `diag` | 诊断快照 | `diag` |

### 安全特性

- 上电先用 `listen-only` 模式只听总线，不先乱发控制帧
- 支持主动发送"零电流扫描帧"找电机 ID

### 适合使用场景

- 需要调试单台 C620 电机的参数和响应
- 排查 CAN 总线接线问题
- 确认电机 ID 和方向

---

## 项目二：HCX_A_N630 — N630/VESC 位控开发

### 用途

基于 VESC 协议的 N630 电调位置控制开发。主控做位置环，N630 只做电流执行器。

### 控制架构

```
目标位置
  → 主控位控（轨迹规划 + 位置 PID + 速度阻尼 + 静摩擦补偿）
  → CAN_PACKET_SET_CURRENT（扩展帧，ID=0x101）
  → N630 内部 FOC 电流环
  → 电机
```

⚠️ 主控初版**只发** `CAN_PACKET_SET_CURRENT`，**不发** `CAN_PACKET_SET_RPM` / `CAN_PACKET_SET_POS`。

### VESC CAN 协议

使用扩展帧：

| 字段 | 值 |
|------|-----|
| EID | `(CAN_PACKET_SET_CURRENT << 8) \| controller_id` |
| 示例 | `(1 << 8) \| 1 = 0x101` |
| 数据格式 | `int32(current_A * 1000)` 大端序 |
| +1.5A | `00 00 05 DC` |
| -1.0A | `FF FF FC 18` |

反馈帧：

| 状态帧 | 内容 |
|--------|------|
| Status 1 | erpm / motor current / duty |
| Status 4 | 温度 / input current / pid_pos（单圈位置） |
| Status 5 | tachometer / input voltage |

### N630 侧 VESC 上位机必须确认

**Motor Settings → FOC：**
- Sensor Mode = Encoder（不要停在 HFI）
- Sensor Port Mode = Sin/Cos
- Encoder Detection 已成功
- Motor Configuration 已写入，点 ↓M

**App Settings → General：**
- CAN Status Rate 1 = 50Hz，勾选 Status 1 + Status 4
- CAN Status Rate 2 = 5Hz，勾选 Status 5
- App Configuration 已写入，点 ↓A

### 已知硬件参数

| 参数 | 值 |
|------|-----|
| CAN ID | 1 |
| CAN 波特率 | 1 Mbps |
| Motor Current Limit | +20A / -20A |
| 编码器 | M3508 7Pin Sin/Cos |
| 极对数 | 7（14 极） |
| 减速比 | ≈19.2 |
| 输出轴一圈电角度 | 7 × 19.2 = 134.4 |
| Position Angle Division | 134.4 |

### 串口命令

| 命令 | 含义 | 示例 |
|------|------|------|
| `p` | 抱住当前多圈位置 | `p` |
| `p <deg>` | 移到绝对多圈角度 | `p 6400` |
| `r <deg>` | 相对移动 | `r 90` / `r -90` |
| `c <A>` | 开环电流测试 | `c 1.0` |
| `s` | 停止，回到 IDLE | `s` |

### 位置反馈和多圈展开

Status 4 的 `pid_pos` 解析为单圈角度：

```cpp
pid_pos_deg = int16(data[6..7]) / 50.0;
```

主控通过相邻两次单圈角度的跨越判断圈数：

```cpp
delta > +180deg  → turns--
delta < -180deg  → turns++
multi_deg = turns * 360 + pid_pos_deg;
```

### 控制算法（PID + 轨迹规划）

```
用户目标 tgt
  → 轨迹规划（最大速度 300deg/s，最大加速度 900deg/s²）
  → ref / ref_vel
  → 位置误差 err = ref - multi_deg
  → current = kp × err + integral - kd × velocity + static × sign(err)
  → 限幅 ±4A
  → CAN_PACKET_SET_CURRENT
```

### 当前已调优的参数

```cpp
kp = 0.015 A/deg
ki = 0.0015 A/(deg·s)
kd = 0.005 A/(deg/s)
积分限幅 = ±0.8A
静摩擦补偿 = 0.65A（abs(err) >= 1.0deg 时启用）
位置死区 = 0.5deg
静止判定速度 = 8deg/s
位置模式电流限幅 = ±4A
```

### 安全限制（首次调试）

```text
current_cmd 限幅：±0.5A 起步 → ±1A → ±2A
发送频率：200Hz → 500Hz / 1kHz
CAN 超时：主控掉线时发 0A
调试时手放 STOP 附近
优先用电池供电（刹车电流大）
```

### 推荐试车顺序

```text
p
r 10    → r -10
r 30    → r -30
r 100   → r -100
s
```

### 状态回显格式

```text
CAN tx=ok/fail rx=count age=ms S=145 M=P | out=A tgt=deg ref=deg err=deg vel=deg/s i=A | pos=... mt=...
```

### 适合使用场景

- N630/VESC 电调的位置控制开发
- 需要多圈角度控制和轨迹规划的场合
- 夹爪/执行器类精准位置控制

---

## 项目三：AM32 — DSHOT 驱动开发 & BoardA 模块库

### 用途

用 ESP32-S3 通过 DSHOT300 数字协议驱动 AM32 电调（FLYROUN, NXN 18M09），作为 C620 的应急替代方案。同时包含 HXC 战队 BoardA 板的所有模块化库。

### DSHOT300 协议

#### 时序参数（RMT 外设生成）

```text
APB 时钟：80MHz，clk_div=1，每 tick = 12.5ns
Bit 周期：3.33µs = 266 ticks
逻辑 1：高电平 2.50µs(200t) + 低电平 0.83µs(66t)
逻辑 0：高电平 1.25µs(100t) + 低电平 2.08µs(166t)
```

#### 数据帧格式（16bit，MSB 先发）

```text
[15:5] 油门值（11bit, 0~2047）
[4]    遥测请求位
[3:0]  CRC = (data ^ data>>4 ^ data>>8) & 0x0F
```

#### 油门值定义

| 值 | 含义 |
|----|------|
| 0 | 解锁信号（电调上电后持续发此值） |
| 1~47 | 保留（特殊指令区间） |
| 48 | 最小油门 |
| 2047 | 最大油门 |
| 20 | 正转指令（需重复 ≥10 次） |
| 21 | 反转指令（需重复 ≥10 次） |

### DSHOT_ESC 驱动 API

```cpp
class DSHOT_ESC {
public:
    DSHOT_ESC(gpio_num_t pin, rmt_channel_t channel, Print* logger);
    bool begin();                           // 初始化 RMT
    void arm(uint32_t ms = 1000);           // 解锁电调
    void sendThrottle(uint16_t throttle);   // 发送原始值 0~2047
    void sendThrottlePercent(float percent);// 发送百分比 0~100%
    void setDirection(bool reverse, int repeat = 15);  // 设置方向
    void stop();                            // 停止
};
```

### AM32Motor 状态机封装

```cpp
class AM32Motor {
public:
    bool begin();
    void arm(uint32_t ms);
    void setOutputEnabled(bool);
    void setThrottle(float percent);         // -100~100，负数=反转
    void update();                           // 每 loop 调用，推进方向切换状态机
};
```

**方向切换非阻塞状态机**（在 `update()` 内驱动）：
```
RUNNING → STOP_WAIT(150ms) → CMD_WAIT(100ms) → RUNNING
```

### 四轮小车控制（已验证）

#### 硬件映射

| 电机 | 位置 | GPIO | RMT 通道 |
|------|------|------|----------|
| M1 | 左前 | GPIO9 | RMT_CHANNEL_0 |
| M2 | 左后 | GPIO10 | RMT_CHANNEL_1 |
| M3 | 右前 | GPIO11 | RMT_CHANNEL_2 |
| M4 | 右后 | GPIO12 | RMT_CHANNEL_3 |

#### 运动逻辑

| 命令 | M1 | M2 | M3 | M4 |
|------|----|----|----|----|
| 前进 F | -x | -x | +x | +x |
| 后退 B | +x | +x | -x | -x |
| 左转 L | +x | +x | +x | +x |
| 右转 R | -x | -x | -x | -x |
| 停止 S | 0 | 0 | 0 | 0 |

#### 串口命令

| 命令 | 示例 | 说明 |
|------|------|------|
| `F` / `F20` | 前进 | 默认速度 10 |
| `B` / `B20` | 后退 | |
| `L` / `L20` | 左转 | |
| `R` / `R20` | 右转 | |
| `S` | 停止 | |
| `arm 1` | 重新解锁 | |
| `m1 ~ m4` | `m1 -10` | 单路控制 -100~100 |
| `all 10` | 四路统一油门 | |
| `rc_enable` | 遥控模式开关 | 0=串口, 1=遥控 |
| `smooth` | 缓冲模式开关 | 0=直通, 1=缓起 |
| `accel` | 加速度上限 %/s | 默认 200 |

### 遥控集成（HotRC RC）

- CH1 → GPIO48（左右转向）
- CH3 → GPIO38（前后油门）
- 1000~2000us 脉宽，50Hz
- 60us 死区消除中位抖动
- 100ms 超时自动停车（失控保护）
- `toNormalized()` → -1.0~+1.0

#### 混控公式

```text
turn     = normalize(ch1) × 60   // -60 ~ +60
throttle = normalize(ch3) × 80   // -80 ~ +80

M1 = -throttle - turn
M2 = -throttle - turn
M3 = +throttle - turn
M4 = +throttle - turn
```

### 缓冲模式（加速度限制）

```cpp
motorTargets[]          // 指令期望值（瞬时变化）
motorTargetsSmoothed[]  // DSHOT 实际送出值
updateSmoothedTargets(dt_ms)  // 以 accel × dt 逼近目标
```

遥控 + 串口全部适用，任何突发指令都会被平滑。

### 适合使用场景

- 用 AM32 电调替代 C620 驱动 M3508 类电机
- 需要 DSHOT 数字协议的高精度/抗干扰场景
- 四轮底盘调试（开环验证）
- 遥控 + 串口双模控制
- 需要加速度缓冲保护的小车

---

## BoardA 模块库索引

| 模块 | 文件名 | 用途 |
|------|--------|------|
| **HXCthread** | `HXCthread.hpp` | 基于 FreeRTOS 的轻量级线程库，类 std::thread 接口 |
| **HXC_NVS** | `HXC_NVS.hpp` | NVS 存储封装，支持 int/float/struct/String |
| **ESP-NOW** | `ESPNOW.hpp` | ESP-NOW 通信封装，多设备配对/回调/重发 |
| **remotePrint** | `remotePrint.hpp` | 基于 ESP-NOW 的远程打印，输出到 mini 开关 |
| **VOFA** | `VOFA.hpp` | 串口动态参数调优，`名称:数值` 实时更新 |
| **HEServo** | `HEServo.hpp` | 幻尔舵机控制（角度/速度/温度/电压） |
| **ESP32PCNT** | `HXCEncoder.hpp` | PCNT 编码器计数，4 倍采样，速度检测 |
| **EMMC42V5** | `EMMC42V5.hpp` | 张大头 V5 步进闭环驱动控制 |
| **DSHOT_ESC** | `DSHOT_ESC.hpp` | DSHOT300 驱动（兼容 IDF 4.x） |
| **HotRC_RC** | `HotRC_RC.hpp` | 遥控 PWM 通道解码（ISR + 归一化） |
| **SBUS/DBUS** | `SBUS.hpp` / `DBUS.hpp` | 遥控器 SBUS/DBUS 协议解码 |
| **SteeringWheelChassis** | `SteeringWheelChassis.hpp` | 通用舵轮底盘运动学逆解算 |
| **MecanumWheelChassis** | `MecanumWheelChassis.hpp` | 麦克纳姆轮底盘运动学解算 |
| **STATUS_LED** | `STATUS_LED.hpp` | 状态指示灯控制 |
| **OPS-9** | `ops9.hpp` | OPS-9 传感器驱动 |

---

## 开发规则

### GPIO 不变规则

⚠️ 以下引脚已经过硬件验证，不要随手更改：

| 功能 | 引脚 |
|------|------|
| CAN TX | GPIO8 |
| CAN RX | GPIO18 |
| UART0 RX | GPIO44 |
| UART0 TX | GPIO43 |

### C620 规则

- 上电先 `listen-only` 模式监听总线
- 控制帧用标准 11-bit ID
- 反馈 ID = `0x200 + motor_id`
- 速度模式是 ESP32 侧软件外环

### N630 规则

- 调试前先接 VESC 上位机确认当前 CAN 波特率
- 主控只发 `CAN_PACKET_SET_CURRENT`
- 不发 `CAN_PACKET_SET_RPM` / `CAN_PACKET_SET_POS`
- 使用扩展帧 EID = `(packet_id << 8) | controller_id`
- 位置反馈需要从 Status 4 的 pid_pos 做多圈展开
- 位置反馈方向必须和电流正方向一致（否则可能跑飞）

### AM32 / DSHOT 规则

- Flash 配置必须匹配硬件（N16R8 配 16MB）
- Arduino-ESP32 v3.x 基于 IDF 4.x，用旧版 RMT API（`driver/rmt.h`）
- 方向指令需要连续发送 ≥10 次才生效
- 切换方向前必须停电机
- 四轮底盘注意左右两侧电机镜像安装方向相反

### 安全规则

- 第一次调试 N630 时，`current_cmd` 限幅 ±0.5A 起步
- 上电默认不输出，先 `arm` 再控制
- 串口活动 watchdog 超时后自动停机
- C620 位置模式超时时进入低电流保持
- 带载测试前先 r 10 / r 30 确认方向和制动
- 如果出现反向跑飞，立即 `s` 停止

---

## 三项目选型对照

| 需求 | 选哪个项目 | 起点 |
|------|-----------|------|
| 只调 C620 | HXC_A_C620 | `HXC_A_C620/.../ESP32_platformio_temple_project` |
| 只调 N630/VESC | HCX_A_N630 | `HCX_A_N630/ESP32_platformio_temple_project` |
| 夹爪/机构/双电机联调 | gripper_debug | 仓库中的 gripper_debug 工程 |
| AM32 替代 C620 | AM32 → DSHOT_ESC | `AM32/BoardA/module/DSHOT_ESC/` |
| 四轮底盘开发 | AM32 → BoardA | `AM32/BoardA/src/main.cpp` |
| 需要模块库 | AM32 → BoardA/module | 按需复制模块到 lib 目录 |