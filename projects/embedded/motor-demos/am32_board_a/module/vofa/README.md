# VOFA_float 模块使用说明

`VOFA_float` 是一个用于通过串口通信动态更新浮点数值的 Arduino 模块。它允许你通过串口发送特定格式的字符串来更新模块中定义的浮点数值。这个模块特别适用于需要通过串口实时调整参数的场景，例如调试或参数调优。

## 功能特性

- **动态更新浮点数值**：通过串口发送特定格式的字符串，可以实时更新模块中定义的浮点数值。
- **自动映射**：模块会自动将名称与浮点数值进行映射，方便通过名称查找和更新数值。
- **线程安全**：通过 FreeRTOS 的任务机制，确保串口读取操作的线程安全。

## 使用方法

### 1. 引入头文件

在你的 Arduino 项目中引入 `VOFA.hpp` 头文件：

```cpp
#include "VOFA.hpp"
```

### 2. 创建 VOFA_float 对象

在代码中创建 `VOFA_float` 对象，并指定名称和默认值：

```cpp
VOFA_float my_float("my_float_name", 0.0);
```

- `my_float_name` 是你为这个浮点数值指定的名称，后续通过串口更新时需要用到这个名称。
- `0.0` 是这个浮点数值的默认值。

### 3. 初始化模块

在 `setup()` 函数中调用 `VOFA_float::setup()` 来初始化模块：

```cpp
void setup() {
    VOFA_float::setup();
}
```

### 4. 读取浮点数值

你可以通过以下两种方式读取浮点数值：

- **直接读取**：使用 `read()` 方法读取当前值。

```cpp
float current_value = my_float.read();
```

- **隐式转换**：通过 `float` 类型的隐式转换读取当前值。

```cpp
float current_value = my_float;
```

### 5. 通过串口更新浮点数值

通过串口发送以下格式的字符串来更新浮点数值：

```
<名称>:<数值>
```

例如，如果你想将名为 `my_float_name` 的浮点数值更新为 `3.14`，可以发送：

```
my_float_name:3.14
```
### 6. 回调功能
```cpp
void onParamChange(String name, float value) {
    Serial.printf("参数 %s 已更新为: %.2f\n", name.c_str(), value);
}

void setup() {
    // ...其他初始化...
    VOFA_float::add_on_value_change_callback(onParamChange);
}
```
### 7. 示例代码

```cpp
#include "VOFA.hpp"

VOFA_float my_float("my_float_name", 0.0);

void setup() {
    Serial.begin(115200);
    VOFA_float::setup();
}

void loop() {
    float current_value = my_float;  // 读取当前值
    Serial.println(current_value);  // 打印当前值到串口
    delay(1000);  // 每秒打印一次
}
```

## 注意事项

- **串口波特率**：确保在 `setup()` 函数中设置了正确的串口波特率（例如 `Serial.begin(115200);`）。
- **名称唯一性**：每个 `VOFA_float` 对象的名称应该是唯一的，否则可能会导致数值更新错误。
- **线程安全**：模块使用了 FreeRTOS 的任务机制来确保串口读取操作的线程安全，确保你的 Arduino 环境支持 FreeRTOS。

## 依赖

- **Arduino.h**：标准 Arduino 库。
- **FreeRTOS**：用于创建任务，确保串口读取操作的线程安全。