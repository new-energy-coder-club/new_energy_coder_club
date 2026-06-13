# HEServo 舵机控制库

`HEServo` 是一个用于控制幻尔舵机的 Arduino 库，支持多种舵机操作，包括角度控制、速度控制、温度读取、电压读取等。该库通过串口与舵机通信，提供了丰富的 API 接口，方便用户进行舵机的控制和状态读取。

## 目录
- [HEServo 舵机控制库](#heservo-舵机控制库)
  - [目录](#目录)
  - [安装](#安装)
  - [使用示例](#使用示例)
  - [API 文档](#api-文档)
    - [构造函数](#构造函数)
    - [方法](#方法)
  - [注意事项](#注意事项)

## 安装

1. 将 `HEServo.hpp` 文件放入你的 Arduino 项目目录中。
2. 在你的 Arduino 代码中包含该头文件：
   ```cpp
   #include "HEServo.hpp"
   ```

## 使用示例

以下是一个简单的示例，展示了如何使用 `HEServo` 库控制舵机。

```cpp
#include <Arduino.h>
#include "HEServo.hpp"

// 创建一个 HEServo 对象，使用 Serial1 作为通信串口，舵机 ID 为 1
HEServo myServo(&Serial1, 1);

void setup() {
  // 初始化串口
  Serial1.begin(115200);

  // 设置舵机角度为 90 度，转动时间为 1000 毫秒
  myServo.SERVO_MOVE_TIME_WRITE(90, 1000);

  // 读取舵机当前角度
  float currentAngle = myServo.SERVO_ANGLE_READ();
  Serial.print("Current Angle: ");
  Serial.println(currentAngle);

  // 读取舵机内部温度
  int temperature = myServo.SERVO_TEMP_READ();
  Serial.print("Temperature: ");
  Serial.println(temperature);

  // 读取舵机内部电压
  int voltage = myServo.SERVO_VIN_READ();
  Serial.print("Voltage: ");
  Serial.println(voltage);
}

void loop() {
  // 主循环中可以添加其他代码
}
```

## API 文档

### 构造函数

- `HEServo(HardwareSerial *sl, uint8_t id)`
  - 初始化一个 `HEServo` 对象。
  - 参数：
    - `sl`: 使用的串口对象（如 `Serial1`, `Serial2` 等）。
    - `id`: 舵机的 ID。

### 方法

- `void SERVO_MOVE_TIME_WRITE(float angle, unsigned short int time = 0)`
  - 控制舵机转动到指定角度。
  - 参数：
    - `angle`: 目标角度，范围 0~240 度。
    - `time`: 转动时间，范围 0~30000 毫秒。

- `void SERVO_MOVE_TIME_READ(uint8_t* rdata, float angle, unsigned short int time = 0)`
  - 读取舵机的目标角度和时间。
  - 参数：
    - `rdata`: 用于存储读取数据的数组。
    - `angle`: 目标角度。
    - `time`: 转动时间。

- `void SERVO_MOVE_TIME_WAIT_WRITE(float angle, int time = 0)`
  - 设置舵机目标角度和时间，但不立即转动，等待 `SERVO_MOVE_START` 指令。
  - 参数：
    - `angle`: 目标角度。
    - `time`: 转动时间。

- `void SERVO_MOVE_START()`
  - 启动舵机转动。

- `void SERVO_MOVE_STOP()`
  - 停止舵机转动。

- `void SERVO_ID_WRITE(uint8_t id)`
  - 设置舵机的 ID。
  - 参数：
    - `id`: 新的舵机 ID。

- `uint8_t SERVO_ID_READ()`
  - 读取舵机的 ID。
  - 返回值：舵机的 ID。

- `int SERVO_TEMP_READ()`
  - 读取舵机内部温度。
  - 返回值：舵机温度。

- `int SERVO_VIN_READ()`
  - 读取舵机内部电压。
  - 返回值：舵机电压。

- `int16_t SERVO_POS_READ()`
  - 读取舵机当前位置。
  - 返回值：舵机当前位置。

- `float SERVO_ANGLE_READ()`
  - 读取舵机当前角度。
  - 返回值：舵机当前角度。

- `void SERVO_OR_MOTOR_MODE_WRITE(bool motor_mode = false, int16_t motor_speed = 0)`
  - 设置舵机或电机模式。
  - 参数：
    - `motor_mode`: 是否为电机模式。
    - `motor_speed`: 电机速度。

- `void SERVO_LOAD_OR_UNLOAD_WRITE(bool load)`
  - 设置舵机电机是否卸载掉电。
  - 参数：
    - `load`: 是否装载电机。

- `bool SERVO_LOAD_OR_UNLOAD_READ()`
  - 读取舵机电机的状态。
  - 返回值：电机是否装载。

## 注意事项

1. **串口通信**：确保使用的串口与舵机连接的串口一致，并且波特率设置正确。
2. **舵机 ID**：每个舵机都有一个唯一的 ID，确保在初始化 `HEServo` 对象时使用正确的 ID。
3. **角度范围**：舵机的角度范围为 0~240 度，超出范围的值会被自动调整。
4. **时间范围**：转动时间的范围为 0~30000 毫秒，超出范围的值会被自动调整。
