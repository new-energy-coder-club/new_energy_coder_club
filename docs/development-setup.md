# HXC 开发环境搭建指南

> 从零开始搭建 HXC ESP A Board 开发环境，适用于新设备 / 新环境。

## 1️⃣ 前置依赖

| 工具 | 版本要求 | 安装方式 |
|------|----------|----------|
| Python | ≥ 3.8 | [python.org](https://www.python.org/) |
| Git | ≥ 2.30 | [git-scm.com](https://git-scm.com/) |
| PlatformIO Core | 最新 | `pip install platformio` |
| VSCode | 推荐 | 安装 PlatformIO IDE 插件 |

### 1.1 Windows 快速安装

```powershell
# 1. 安装 Python（确保勾选 "Add to PATH"）
# 2. 安装 Git
# 3. 安装 PlatformIO
pip install platformio

# 4. 验证
pio --version
git --version
python --version
```

## 2️⃣ 克隆项目

### 2.1 克隆 SKill 分支（核心设备仓库）

```powershell
git clone -b SKill https://gitee.com/darrenpig/new_energy_coder_club.git
cd new_energy_coder_club

# 初始化子模块（拉取上游 ESP32 项目）
git submodule update --init --recursive
```

### 2.2 也可单独拉取上游 ESP32 项目

```powershell
git clone https://github.com/CQUPTHXC/ESP32_platformio_temple_project.git
cd ESP32_platformio_temple_project
```

## 3️⃣ 构建固件

```powershell
cd projects\embedded\ESP32_platformio_temple_project

# 构建
pio run --environment temple_project

# 烧录（自动检测 COM 口）
pio run --target upload --environment temple_project

# 指定端口烧录
pio run --target upload --environment temple_project --upload-port COM<N>
```

### 下载模式烧录（首次 / 串口冲突时）

1. 按住 **BOOT** 按钮
2. 按一下 **RESET** 按钮
3. 松开 **BOOT** 按钮
4. 立即执行以上烧录命令

## 4️⃣ 串口通信

### 自动检测 ESP32-S3 COM 口

```python
python -c "import serial.tools.list_ports as lp; print([p.device for p in lp.comports() if '303A' in (p.hwid or '')])"
```

### 发送指令

```powershell
# 使用内置脚本
python projects\embedded\ESP32_platformio_temple_project\send_cmd.py <命令>

# 示例
python send_cmd.py "c 0.3"   # 电流模式 0.3A
python send_cmd.py "p 90"    # 绝对位置 90°
python send_cmd.py "s"       # 停止
```

## 5️⃣ 硬件接线速查

| 功能 | ESP32-S3 引脚 | 备注 |
|------|--------------|------|
| CAN TX | GPIO8 | 接 CAN 收发器 TX |
| CAN RX | GPIO18 | 接 CAN 收发器 RX |
| UART0 TX | GPIO43 | 外部串口链路 |
| UART0 RX | GPIO44 | 外部串口链路 |
| USB CDC | USB-DM/DP | 烧录 + 调试串口 |

## 6️⃣ 环境验证清单

```powershell
# 检查清单
pio device list          # 应显示 ESP32-S3 COM 口
pio run --environment temple_project  # 应编译通过
# 打开串口监视器
pio device monitor -p COM<N> -b 115200
```

## 7️⃣ 常见问题

| 问题 | 解决方案 |
|------|----------|
| COM 口被占用 | `taskkill /f /im pio.exe & taskkill /f /im python.exe` |
| 烧录失败 "port doesn't exist" | 重新检测 COM 口，ESP32 复位后可能变号 |
| 串口无数据 | 等待 3-5 秒枚举，检查 USB 数据线是否支持数据 |
| CAN 无通信 | 先用 VESC 上位机确认 N630 实际波特率 |

---

*最后更新: 2026-06-08*
