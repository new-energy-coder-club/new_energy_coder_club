# EMMC42V5 电机驱动库

## 概述

`EMMC42V5` 是一个用于控制 张大头V5 系列电机的 Arduino 库。该库提供了丰富的功能，包括电机使能控制、速度控制、位置控制、回零操作、参数读取与修改等。通过该库，用户可以方便地与 EMMC42V5 电机进行通信，并实现各种复杂的控制任务。

## 使用示例

### 1. 初始化电机驱动

首先，需要包含头文件并初始化 `EMMC42V5` 对象。假设使用 `Serial1` 作为通信端口，电机 ID 为 1。

```cpp
#include "EMMC42_V5.hpp"

EMMC42V5 motor(&Serial1, 1);  // 使用 Serial1 作为通信端口，电机 ID 为 1

void setup() {
    motor.setup(115200);  // 初始化串口通信，波特率为 115200
}
```

### 2. 使能电机

使用 `enable()` 函数使能电机。

```cpp
void loop() {
    motor.enable(true);  // 使能电机
    delay(1000);
    motor.enable(false);  // 禁用电机
    delay(1000);
}
```

### 3. 速度控制

使用 `speed_control()` 函数控制电机速度。

```cpp
void loop() {
    motor.speed_control(1000);  // 设置电机速度为 1000 RPM
    delay(5000);
    motor.stop();  // 停止电机
    delay(1000);
}
```

### 4. 位置控制

使用 `pulse_control()` 函数控制电机位置。

```cpp
void loop() {
    motor.pulse_control(3200, 1000);  // 设置电机转动 3200 个脉冲，速度为 1000 RPM
    delay(5000);
    motor.stop();  // 停止电机
    delay(1000);
}
```

### 5. 回零操作

使用 `re_zero()` 函数触发电机回零操作。

```cpp
void loop() {
    motor.re_zero(0);  // 触发单圈就近回零
    delay(5000);
}
```

### 6. 读取电机状态

使用 `read_motor_status()` 函数读取电机状态。

```cpp
void loop() {
    Motor_status_flag status = motor.read_motor_status();
    if (status.is_enable) {
        Serial.println("电机已使能");
    }
    if (status.is_moving) {
        Serial.println("电机正在运动");
    }
    delay(1000);
}
```

## API 文档

### 构造函数

```cpp
EMMC42V5(HardwareSerial *sl, uint8_t id);
```

- `sl`: 使用的串口对象（如 `Serial1`）。
- `id`: 电机的 ID 地址。

### 初始化函数

```cpp
void setup(int bund_rate);
void setup();
```

- `bund_rate`: 串口通信的波特率。如果不指定，默认使用 115200。

### 电机控制函数

#### 使能控制

```cpp
COMMAND_STATUS enable(bool is_enable, bool needsync = false, bool need_retry = false);
```

- `is_enable`: 是否使能电机（`true` 为使能，`false` 为禁用）。
- `needsync`: 是否需要多机同步。
- `need_retry`: 是否需要重试。

#### 速度控制

```cpp
COMMAND_STATUS speed_control(int speed, uint8_t acce = 0, bool needsync = false, bool need_retry = false);
```

- `speed`: 电机速度（RPM）。
- `acce`: 加速度档位。
- `needsync`: 是否需要多机同步。
- `need_retry`: 是否需要重试。

#### 位置控制

```cpp
COMMAND_STATUS pulse_control(int64_t pulse_num, int16_t speed, int acce = 0, bool absolute_mode = false, bool needsync = false, bool need_retry = false);
```

- `pulse_num`: 脉冲数。
- `speed`: 电机速度（RPM）。
- `acce`: 加速度档位。
- `absolute_mode`: 是否为绝对位置模式。
- `needsync`: 是否需要多机同步。
- `need_retry`: 是否需要重试。

#### 停止电机

```cpp
COMMAND_STATUS stop(bool need_retry = false, bool needsync = false);
```

- `need_retry`: 是否需要重试。
- `needsync`: 是否需要多机同步。

#### 多机同步

```cpp
COMMAND_STATUS sync(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

### 回零操作

#### 设置零点位置

```cpp
COMMAND_STATUS set_zero_position(bool save = false, bool need_retry = false);
```

- `save`: 是否保存零点位置。
- `need_retry`: 是否需要重试。

#### 触发回零

```cpp
COMMAND_STATUS re_zero(int mode = 0, bool needsync = false, bool need_retry = false);
```

- `mode`: 回零模式（0: 单圈就近回零，1: 单圈方向回零，2: 多圈无限位碰撞回零，3: 多圈有限位开关回零）。
- `needsync`: 是否需要多机同步。
- `need_retry`: 是否需要重试。

#### 强制中断回零

```cpp
COMMAND_STATUS exit_rezero(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

### 参数读取与修改

#### 读取回零状态标志位

```cpp
Return_to_zero_status_flag get_return_to_zero_status(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取版本信息

```cpp
version_info get_version_info(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取相电阻和相电感

```cpp
Phase_resistance_inductance get_Phase_resistance_inductance(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取位置环 PID 参数

```cpp
PID_parameter read_PID_parameter(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取总线电压

```cpp
uint16_t read_Bus_voltage(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取相电流

```cpp
uint16_t read_Phase_current(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取编码器值

```cpp
uint16_t read_Encoder(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取输入脉冲数

```cpp
int64_t read_input_pulses(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取电机目标位置

```cpp
int64_t read_target_location(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取电机实时转速

```cpp
int read_current_speed(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取电机实时位置

```cpp
int64_t read_current_location(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取电机位置误差

```cpp
int64_t read_location_error(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取电机状态标志位

```cpp
Motor_status_flag read_motor_status(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 读取驱动配置参数

```cpp
Driver_parameter read_driver_parameter(bool need_retry = false);
```

- `need_retry`: 是否需要重试。

#### 修改细分

```cpp
COMMAND_STATUS change_subdivision(uint8_t subdivision, bool save = true, int need_retry = false);
```

- `subdivision`: 细分值。
- `save`: 是否保存修改。
- `need_retry`: 是否需要重试。

#### 修改 ID 地址

```cpp
COMMAND_STATUS change_ID(uint8_t new_id, bool save = true, int need_retry = false);
```

- `new_id`: 新的 ID 地址。
- `save`: 是否保存修改。
- `need_retry`: 是否需要重试。

#### 切换开环/闭环模式

```cpp
COMMAND_STATUS change_open_or_closed_loop(uint8_t mode, bool save = true, int need_retry = false);
```

- `mode`: 模式（0x01: 开环，0x02: 闭环）。
- `save`: 是否保存修改。
- `need_retry`: 是否需要重试。

#### 修改开环模式的工作电流

```cpp
COMMAND_STATUS change_open_loop_current(uint16_t current, bool save = true, int need_retry = false);
```

- `current`: 开环模式电流。
- `save`: 是否保存修改。
- `need_retry`: 是否需要重试。

#### 修改驱动配置参数

```cpp
COMMAND_STATUS change_driver_configuration_parameters(uint8_t parameters, bool save = true, int need_retry = false);
```

- `parameters`: 驱动配置参数。
- `save`: 是否保存修改。
- `need_retry`: 是否需要重试。

#### 修改位置环 PID 参数

```cpp
COMMAND_STATUS change_PID_parameter(uint8_t PID_parameter, bool save = true, int need_retry = false);
```

- `PID_parameter`: 位置环 PID 参数。
- `save`: 是否保存修改。
- `need_retry`: 是否需要重试。

## 注意事项

1. 在使用该库时，请确保电机的 ID 地址与代码中设置的 ID 地址一致。
2. 在进行回零操作时，请确保电机处于合适的位置，以避免碰撞或其他意外情况。
3. 在修改参数时，请谨慎操作，避免误操作导致电机无法正常工作。

## 结语

通过 `EMMC42V5` 库，用户可以方便地控制张大头V5系列电机，并实现各种复杂的控制任务。希望该库能够帮助您更好地完成项目开发。如果有任何问题或建议，欢迎反馈。****