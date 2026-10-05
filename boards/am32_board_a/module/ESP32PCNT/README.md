# HXC::Encoder

`HXC::Encoder` 类是一个用于 ESP32 的编码器计数器实现，利用 ESP32 的 PCNT（脉冲计数器）外设来实现高效的编码器信号处理。该类默认4倍采样(即在每个脉冲上计数4次)，并且通过任务
轮询 PCNT 单元来实现更高的计数范围。

由于该类仅依赖```pcnt.h```所以Arduino框架和ESP-IDF都可直接使用

[IDF API文档链接](https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32s3/api-reference/peripherals/pcnt.html)
## 目录
- [构造函数](#构造函数)
- [成员函数](#成员函数)
  - [setup](#setup)
  - [set_filter](#set_filter)
  - [get_count](#get_count)
  - [get_speed](#get_speed)
  - [reset_count](#reset_count)
- [保护成员函数](#保护成员函数)
  - [get_count_row](#get_count_row)
- [保护成员变量](#保护成员变量)
- [静态成员变量](#静态成员变量)

## 构造函数

### `Encoder(uint8_t _PINA, uint8_t _PINB)`

- **描述**: 构造函数，初始化编码器对象。
- **参数**:
  - `_PINA`: 编码器 A 相的脉冲信号 GPIO 引脚。
  - `_PINB`: 编码器 B 相的脉冲信号 GPIO 引脚。
- **注意**: 该构造函数会自动分配一个 PCNT 单元。

## 成员函数

### `void setup(int frc = 1000)`

- **描述**: 初始化编码器计数器。
- **参数**:
  - `frc`: 多圈计数器和速度检测的频率，默认值为 1000 Hz。
- **注意**: 该函数会配置 PCNT 单元，并启动一个任务来轮询 PCNT 计数。

### `void set_filter(uint16_t ns)`

- **描述**: 设置脉冲去抖动滤波器的时间常数。
- **参数**:
  - `ns`: 宽度小于该值的脉冲将被忽略，单位为纳秒。

### `int64_t get_count()`

- **描述**: 获取计数器的当前计数。
- **返回值**: 计数器的当前计数值。

### `float get_speed()`

- **描述**: 获取当前的脉冲速度。
- **返回值**: 当前的脉冲速度，单位为 Hz。

### `void reset_count(int64_t _count = 0)`

- **描述**: 将计数器重置为指定的值。
- **参数**:
  - `_count`: 要重置的值，缺省为 0。

## 保护成员函数

### `int16_t get_count_row()`

- **描述**: 直接从 PCNT 单元获取当前计数，未经任何处理。
- **返回值**: 当前计数，作为一个有符号的 16 位整数。
- **注意**: 该函数被循环检测线程用于获取当前计数。

## 保护成员变量

### `uint8_t PINA, PINB`

- **描述**: 编码器 A 相和 B 相的 GPIO 引脚。

### `int64_t count`

- **描述**: 脉冲计数，默认 4 倍计数。

### `uint8_t unit`

- **描述**: PCNT 单元编号。

### `pcnt_config_t pcnt_config`

- **描述**: PCNT 配置结构体。

### `int last_count_row`

- **描述**: 上一次从 PCNT 单元获取的计数值。

### `int LOOPFREQ`

- **描述**: 循环检测任务的频率。

### `int64_t last_time`

- **描述**: 上一次检测的时间。

### `float speed`

- **描述**: 当前的脉冲速度，单位为 Hz。

### `TaskHandle_t counter_loop_handle`

- **描述**: 循环检测任务的句柄。

## 静态成员变量

### `uint8_t used_unit`

- **描述**: 已经使用的 PCNT 单元数量。
- **初始值**: 0

