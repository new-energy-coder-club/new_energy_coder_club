# HXC ESP A Board — 开发环境搭建 & 烧录 & 测试 Skill

## 概述
**HXC 战队 ESP32-S3 主控板（Board A）** 的完整开发环境搭建、固件提取、烧录和电机基础旋转测试。封装了从零开始到电机转动的全流程，适用于在新机器 / 新环境快速搭建 HXC N630 位控开发环境。

## 前置条件
- Windows 系统
- PlatformIO Core 已安装（`pip install platformio`）
- Python ≥ 3.8
- ESP32-S3 板通过 USB 连接电脑

## 硬件参数

| 参数 | 值 |
|------|-----|
| **MCU** | ESP32-S3 (rev v0.2) |
| **板型** | ESP32-S3-DevKitC-1 (N16R8) |
| **Flash** | 16MB (QIO OPI) |
| **PSRAM** | 8MB |
| **CAN TX** | GPIO8 |
| **CAN RX** | GPIO18 |
| **串口** | USB CDC (115200, 8N1) |

## 工作流

### 1. 从压缩包提取项目文件
```powershell
# 解压 HCX_A_N630.zip 到开发目录
mkdir <target_dir> -Force
tar -xf <path/to/HCX_A_N630.zip> -C <target_dir>
# 实际项目路径为: <target_dir>/HCX_A_N630/ESP32_platformio_temple_project/
```

### 2. 平台配置（platformio.ini 关键参数）
板型: `esp32-s3-devkitc-1`
Flash 大小: `16MB`
分区表: `default_16MB.csv`
内存类型: `qio_opi`
上传协议: `esptool`（UART 串口）或 `esp-builtin`（USB-JTAG）
USB CDC: `-DARDUINO_USB_CDC_ON_BOOT=1`（启用 USB 模拟串口）
CAN (TWAI): 1Mbps, GPIO8(TX) / GPIO18(RX)

### 3. 构建固件
```powershell
cd <project_dir>
pio run --environment temple_project
```

### 4. 烧录固件
**正常烧录**（板子运行中）：
```powershell
pio run --target upload --environment temple_project --upload-port <COM_PORT>
```

**下载模式烧录**（推荐第一次烧录或遇到串口冲突时）：
1. 按住 BOOT 按钮
2. 按一下 RESET 按钮
3. 松开 BOOT 按钮
4. 立即执行：
```powershell
pio run --target upload --environment temple_project --upload-port <COM_PORT>
```

**主机串口变化**：ESP32-S3 使用内置 USB CDC，烧录后复位会重新枚举 COM 口（可能变化），用以下命令检测：
```python
import serial.tools.list_ports as lp
ports = [(p.device, p.hwid) for p in lp.comports() if '303A' in (p.hwid or '')]
```

### 5. 串口通信测试
```python
import serial, time

ser = serial.Serial('<COM_PORT>', 115200, timeout=2)
time.sleep(3)  # 等待 USB CDC 枚举和 boot 消息

# 读取状态
data = ser.read(5000)
print(data.decode('utf-8', 'replace'))
```

### 6. 电机控制指令

| 指令 | 说明 | 示例 |
|------|------|------|
| `c <A>` | 电流模式（力矩控制） | `c 0.3` → 0.3A 旋转 |
| `p <deg>` | 绝对位置模式 | `p 90` → 转到 90° |
| `r <deg>` | 相对位置模式 | `r -45` → 逆时针转 45° |
| `p` | 保持当前位置 | `p` |
| `s` | 停止 / IDLE 模式 | `s` |

**发送指令脚本**（`send_cmd.py`）：
```python
import serial, sys, time

ser = serial.Serial('<COM_PORT>', 115200, timeout=2)
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

### 7. 基础旋转测试流程

```python
# 1. 停止/清空
send: s

# 2. 检查状态 — 应显示 M=I (IDLE)，CAN 通信正常
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
原因：其他进程已占用串口（如 pio device monitor）
解决：`taskkill /f /im pio.exe & taskkill /f /im python.exe`

### 2. 烧录时 "Could not open COMxx, the port doesn't exist"
原因：ESP32-S3 复位后 USB 重新枚举，COM 端口号变化
解决：用 `pio device list` 或 `python -c "import serial.tools.list_ports as lp; print([p.device for p in lp.comports() if '303A' in (p.hwid or '')])"` 重新检测

### 3. 串口打开成功但无数据
原因：
- USB CDC 枚举较慢（等待 3-5 秒后再读）
- CAN 驱动器初始化失败（检查 CAN 收发器连接）
- 固件崩溃（重新烧录）

### 4. USB 数据线问题
部分 USB 线只支持充电不支持数据。换用高质量 USB 数据线可解决串口不稳定问题。

### 5. platformio.ini 中的 `build.mcu` 警告
这是已知警告，不影响编译和烧录。

## 环境验证清单

| 检查项 | 预期结果 |
|--------|---------|
| `pio device list` 显示 ESP32-S3 | COM 端口存在 |
| CAN 通信正常 | tx/rx 持续递增 |
| erpm 读数 | 静止时 ≈0，旋转时变化 |
| 输入电压 | 22.9V（锂电池供电） |
| 温度读数 | FET < 40°C，电机 < 40°C |
| 位置反馈 (pid_pos_deg) | 随电机转动变化 |
