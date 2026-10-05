# HXC ESP A Board — 开发环境搭建 & 烧录 & 测试 Skill

## 概述

**HXC 战队 ESP32-S3 主控板（Board A）** 的完整开发环境搭建、固件提取、烧录、电机基础旋转测试以及调试继电器控制。封装了从零开始到电机转动和继电器调试的全流程，适用于在新机器 / 新环境快速搭建 HXC N630 位控开发环境。

## 前置条件

- Windows 系统
- Python ≥ 3.8
- ESP32-S3 板通过 USB 连接电脑
- HXC_A_N630.zip 项目压缩包

## 硬件参数

| 参数 | 值 |
|------|-----|
| **MCU** | ESP32-S3 (rev v0.2) |
| **板型** | ESP32-S3-DevKitC-1 (N16R8) |
| **Flash** | 16MB (QIO OPI) |
| **PSRAM** | 8MB |
| **CAN TX** | GPIO8 |
| **CAN RX** | GPIO18 |
| **调试继电器** | GPIO9 |
| **BOOT 按钮** | GPIO0 |
| **串口** | USB CDC (115200, 8N1) |

## 环境搭建

### 1. 创建隔离环境并安装 PlatformIO

```powershell
# 创建虚拟环境
python -m venv C:\Users\<USERNAME>\.venv_hxc

# 安装 PlatformIO 和 pyserial
C:\Users\<USERNAME>\.venv_hxc\Scripts\python.exe -m pip install platformio pyserial

# 验证安装
C:\Users\<USERNAME>\.venv_hxc\Scripts\pio.exe --version
```

### 2. 检测 ESP32-S3 串口

ESP32-S3 的 USB VID 为 `303A`。每次复位或换 USB 口后，COM 端口号可能变化，建议先检测再配置。

```powershell
C:\Users\<USERNAME>\.venv_hxc\Scripts\python.exe -c "import serial.tools.list_ports as lp; print([(p.device, p.hwid) for p in lp.comports() if '303A' in (p.hwid or '')])"
```

预期输出类似：`[('COM5', 'USB VID:PID=303A:1001 SER=10:20:BA:59:30:40')]` 或 `[('COM8', 'USB VID:PID=303A:1001 SER=94:A9:90:E0:FC:48')]`

## 工作流

### 3. 从压缩包提取项目文件

```powershell
# 解压 HCX_A_N630.zip 到开发目录
New-Item -ItemType Directory -Path C:\Users\<USERNAME>\hxc_workspace -Force
Expand-Archive -Path "D:\eg\HCX_A_N630.zip" -DestinationPath C:\Users\<USERNAME>\hxc_workspace -Force

# 实际项目路径
# C:\Users\<USERNAME>\hxc_workspace\HCX_A_N630\ESP32_platformio_temple_project\
```

### 4. 平台配置（platformio.ini）

默认 `esp32-s3-devkitc-1` 板型定义是 **N8 版本**（8MB Flash，无 PSRAM）。为了正确识别 N16R8，需要创建自定义板型定义。

#### 4.1 创建自定义板型 JSON

创建 `boards/esp32-s3-devkitc-1-n16r8.json`：

```json
{
  "build": {
    "arduino": {
      "ldscript": "esp32s3_out.ld",
      "partitions": "default_16MB.csv"
    },
    "core": "esp32",
    "extra_flags": [
      "-DARDUINO_ESP32S3_DEV",
      "-DARDUINO_USB_MODE=1",
      "-DARDUINO_RUNNING_CORE=1",
      "-DARDUINO_EVENT_RUNNING_CORE=1"
    ],
    "f_cpu": "240000000L",
    "f_flash": "80000000L",
    "flash_mode": "qio",
    "hwids": [["0x303A", "0x1001"]],
    "mcu": "esp32s3",
    "variant": "esp32s3"
  },
  "connectivity": ["bluetooth", "wifi"],
  "debug": {
    "default_tool": "esp-builtin",
    "onboard_tools": ["esp-builtin"],
    "openocd_target": "esp32s3.cfg"
  },
  "frameworks": ["arduino", "espidf"],
  "name": "Espressif ESP32-S3-DevKitC-1-N16R8 (16 MB QD, 8 MB OPI PSRAM)",
  "upload": {
    "flash_size": "16MB",
    "maximum_ram_size": 327680,
    "maximum_size": 16777216,
    "require_upload_port": true,
    "speed": 460800
  },
  "url": "https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html",
  "vendor": "Espressif"
}
```

#### 4.2 修改 platformio.ini

将 `<COM_PORT>` 替换为实际检测到的端口（如 `COM5` 或 `COM8`）：

```ini
[env:temple_project]
platform = espressif32
board = esp32-s3-devkitc-1-n16r8   ; 自定义 N16R8 板型定义
framework = arduino

; N16R8 模组：16MB Flash + 8MB PSRAM
board_build.arduino.memory_type = qio_opi
board_build.flash_mode = qio

; 启用 USB CDC 模拟串口
build_flags = 
    -DARDUINO_USB_CDC_ON_BOOT=1
    -D CORE_DEBUG_LEVEL=ARDUHAL_LOG_LEVEL_VERBOSE
    -D CONFIG_ARDUHAL_LOG_COLORS=1

; 串口和烧录设置（根据实际检测结果修改）
monitor_speed = 115200
monitor_port = <COM_PORT>
upload_port = <COM_PORT>
monitor_dtr = 0
monitor_rts = 0

upload_protocol = esptool
upload_flags =
    --before=no_reset
    --after=hard_reset
    --connect-attempts=10
    --baud=115200

; 崩溃调试
monitor_filters = esp32_exception_decoder 
build_type = debug 

; 后处理脚本（合并固件）
extra_scripts = post:merge_bins.py
build.mcu = esp32s3
```

> **注意**：`build.mcu` 是 `merge_bins.py` 脚本使用的自定义参数，PlatformIO 会报 "Ignore unknown configuration option `build.mcu`" 警告，这是已知警告，不影响编译和烧录。

### 5. 构建固件

```powershell
cd C:\Users\<USERNAME>\hxc_workspace\HCX_A_N630\ESP32_platformio_temple_project
C:\Users\<USERNAME>\.venv_hxc\Scripts\pio.exe run --environment temple_project
```

预期输出：

```
PLATFORM: Espressif 32 (6.12.0) > Espressif ESP32-S3-DevKitC-1-N16R8 (16 MB QD, 8 MB OPI PSRAM)
HARDWARE: ESP32S3 240MHz, 320KB RAM, 16MB Flash
RAM:   5.8% (used 19020 bytes from 327680 bytes)
Flash: 4.3% (used 282589 bytes from 6553600 bytes)
========================= [SUCCESS] =========================
```

### 6. 烧录固件

**正常烧录**（板子运行中）：

```powershell
C:\Users\<USERNAME>\.venv_hxc\Scripts\pio.exe run --target upload --environment temple_project
```

**下载模式烧录**（推荐第一次烧录或遇到串口冲突时）：

1. 按住 BOOT 按钮
2. 按一下 RESET 按钮
3. 松开 BOOT 按钮
4. 立即执行上面的 upload 命令

### 7. 串口通信测试

将 `<COM_PORT>` 替换为实际端口：

```python
import serial, time

ser = serial.Serial('<COM_PORT>', 115200, timeout=2)
ser.dtr = False
ser.rts = False
time.sleep(3)  # 等待 USB CDC 枚举和 boot 消息

data = ser.read(5000)
print(data.decode('utf-8', 'replace'))
ser.close()
```

预期输出：

```
boot
CAN driver ok
CAN start ok
relay OFF
relay pulse test
relay ON
relay OFF
relay pulse done
ready: p, p deg, r deg, c A, s, d [0/1]
CAN tx=6/0 rx=0 S=--- M=I R=0 | wait VESC | out=0.000A
```

## 串口命令

| 指令 | 说明 | 示例 |
|------|------|------|
| `c <A>` | 电流模式（力矩控制） | `c 0.3` → 0.3A 旋转 |
| `p <deg>` | 绝对位置模式 | `p 90` → 转到 90° |
| `r <deg>` | 相对位置模式 | `r -45` → 逆时针转 45° |
| `p` | 保持当前位置 | `p` |
| `s` | 停止 / IDLE 模式 | `s` |
| `d` | 翻转调试继电器（GPIO9） | `d` |
| `d 0/1` | 设置调试继电器状态 | `d 1` 闭合，`d 0` 断开 |

### 发送指令脚本（send_cmd.py）

```python
import serial, sys, time

ser = serial.Serial('<COM_PORT>', 115200, timeout=2)
ser.dtr = False
ser.rts = False
time.sleep(1)
ser.read(5000)  # 排空缓冲区
time.sleep(0.3)

cmd = sys.argv[1] if len(sys.argv) > 1 else "s"
ser.write((cmd + '\n').encode())

time.sleep(3)
data = ser.read(2000)
print(data.decode('utf-8', 'replace'))

ser.close()
```

## 调试继电器

调试继电器连接在 **GPIO9**，支持三种控制方式：

### 1. 上电自动自检脉冲

上电约 3 秒后，继电器自动闭合 200ms 然后断开，用于验证继电器硬件正常：

```
relay pulse test
relay ON
relay OFF
relay pulse done
```

### 2. BOOT 按钮长按控制

- **按住 BOOT 按钮** → 继电器闭合（`R=1`）
- **松开 BOOT 按钮** → 继电器断开（`R=0`）

实现代码（在 `loop()` 中）：

```cpp
static constexpr gpio_num_t BOOT_PIN = GPIO_NUM_0;

void loop() {
    // BOOT 按钮长按控制继电器：按住闭合，松开断开
    bool boot_pressed = gpio_get_level(BOOT_PIN) == 0;  // BOOT 按下为低电平
    if (boot_pressed) {
        if (!relay_state) set_relay(true);
    } else {
        if (relay_state) set_relay(false);
    }

    // ... 其他逻辑
}
```

> ⚠️ **注意**：上电启动时不要按住 BOOT，否则 ESP32-S3 会进入下载模式。等串口输出 `ready:` 后再按 BOOT。

### 3. 串口命令控制

- `d`：翻转继电器状态
- `d 1`：闭合继电器
- `d 0`：断开继电器

常用场景：控制 VESC/电机供电、复位外部设备、隔离调试电路。

## 基础旋转测试流程

```
# 1. 停止/清空
send: s

# 2. 检查状态 — 应显示 M=I (IDLE)
#    关注: tx/rx 递增, erpm≈0, vin≈22.9V, temp 正常

# 3. 电流模式旋转测试 (0.3A 低电流)
send: c 0.3
# 观察: M=C, out=0.300A, erpm 变化, 位置递增

# 4. 停止
send: s

# 5. 位置模式测试 (转到 90°)
send: p 90
# 观察: M=P, tgt=90, 位置从当前位置运动到 90° 附近

# 6. 位置归零
send: p 0
# 观察: 回到 0° 附近

# 7. 停止
send: s
```

## 常见问题

### 1. COM 端口访问被拒绝

原因：其他进程已占用串口（如 `pio device monitor`、Python 脚本）

解决：

```powershell
taskkill /f /im pio.exe
taskkill /f /im python.exe
```

### 2. 烧录时 "Could not open COMxx, the port is busy or doesn't exist"

原因：ESP32-S3 复位后 USB 重新枚举，COM 端口号可能变化（例如从 COM5 变为 COM8）

解决：重新检测端口并更新 `platformio.ini` 中的 `monitor_port` / `upload_port`

```powershell
C:\Users\<USERNAME>\.venv_hxc\Scripts\python.exe -c "import serial.tools.list_ports as lp; print([p.device for p in lp.comports() if '303A' in (p.hwid or '')])"
```

### 3. 串口打开成功但无数据

原因：

- USB CDC 枚举较慢（等待 3-5 秒后再读）
- 未设置 `ser.dtr = False; ser.rts = False`，导致 ESP32-S3 被保持在复位状态
- CAN 驱动器初始化失败（检查 CAN 收发器连接）
- 固件崩溃（重新烧录）

### 4. 构建时板型显示为 N8（8MB Flash）

原因：默认 `esp32-s3-devkitc-1` 板型定义是 N8 版本

解决：按本文 4.1 节创建自定义 `esp32-s3-devkitc-1-n16r8` 板型 JSON

### 5. USB 数据线问题

部分 USB 线只支持充电不支持数据。换用高质量 USB 数据线可解决串口不稳定问题。

### 6. platformio.ini 中的 `build.mcu` 警告

```
Warning! Ignore unknown configuration option `build.mcu`
```

这是已知警告，用于 `merge_bins.py` 脚本，不影响编译和烧录。

### 7. 上电时按住 BOOT 导致无法启动

原因：BOOT（GPIO0）是 ESP32-S3 的 strapping 引脚，上电时按住会进入下载模式

解决：上电时松开 BOOT，等串口输出 `ready:` 后再按 BOOT 控制继电器

## 环境验证清单

| 检查项 | 预期结果 |
|--------|---------|
| `pio device list` 显示 ESP32-S3 | COM 端口存在 |
| 构建输出显示 N16R8 | 16MB Flash, 8MB OPI PSRAM |
| 烧录成功 | Hash of data verified |
| 串口输出 `boot` / `CAN driver ok` / `CAN start ok` | 固件运行正常 |
| 上电 3 秒继电器自检 | 听到/看到继电器吸合一次 |
| 长按 BOOT | 继电器闭合，松开后断开 |
| CAN 通信正常 | tx/rx 持续递增 |
| erpm 读数 | 静止时 ≈0，旋转时变化 |
| 输入电压 | 22.9V（锂电池供电） |
| 温度读数 | FET < 40°C，电机 < 40°C |
| 位置反馈 (pid_pos_deg) | 随电机转动变化 |
| 调试继电器 | 发送 `d` 可在 `R=0/1` 间切换 |
