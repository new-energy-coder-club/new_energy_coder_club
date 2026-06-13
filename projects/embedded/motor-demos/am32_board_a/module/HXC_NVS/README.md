# HXC_NVS - ESP32 NVS 存储封装库

## 简介

HXC_NVS 是一个针对 ESP32 平台的 NVS (Non-Volatile Storage) 存储系统的二次封装库，提供了简单易用的接口来存储和读取各种类型的数据到 ESP32 的 NVS 中。

## 特性

- 支持多种数据类型存储（包括自定义结构体）
- 支持 String 类型的特化处理
- 自动初始化 NVS 系统
- 简洁的 API 设计
- 错误日志记录
- 自动处理键名长度限制

## 安装

1. 将 `HXC_NVS.hpp` 文件放入您的 Arduino 项目的库目录中
2. 在代码中包含头文件：`#include "HXC_NVS.hpp"`

## 使用方法

### 基本使用

```cpp
#include "HXC_NVS.hpp"

// 定义一个存储整数的 NVS 变量
HXC::NVS_DATA<int> myInt("my_int_key", 10); // 参数：键名，默认值

// 定义一个存储字符串的 NVS 变量
HXC::NVS_DATA<String> myString("my_str_key", "default");

void setup() {
    // 读取值
    int val = myInt.read();
    String str = myString.read();
    
    // 或者直接使用隐式转换
    int val = myInt;
    String str = myString;
    
    // 修改并保存值
    myInt = 20;
    myString = "new value";
}
```

### 支持的数据类型

- 基本数据类型（int, float, double, bool 等）
- String 类型
- 自定义结构体（需要确保结构体是 POD 类型）

### 自定义结构体示例

```cpp
struct MyStruct {
    int a;
    float b;
    char c[10];
};

// 定义并使用
HXC::NVS_DATA<MyStruct> myStruct("struct_key", {0, 0.0f, ""});

void setup() {
    MyStruct data = myStruct.read();
    data.a = 42;
    myStruct = data; // 保存修改
}
```

## API 文档

### 构造函数

```cpp
NVS_DATA(String key, Value_type default_value)
```
- `key`: 存储在 NVS 中的键名（自动截断到15个字符）
- `default_value`: 当键不存在时使用的默认值

### 方法

#### `esp_err_t save()`
将当前值保存到 NVS 中

#### `Value_type read()`
从 NVS 中读取值，如果不存在则返回默认值

### 运算符重载

#### `operator=(const Value_type& newValue)`
赋值运算符，赋值后自动保存到 NVS

#### `operator Value_type()`
隐式类型转换运算符，等同于调用 read()

## 注意事项

1. 键名长度不能超过15个字符（超出的部分会被自动截断）
2. 存储自定义结构体时，确保结构体是简单的 POD 类型
3. 首次使用时会自动初始化 NVS 系统
4. 所有实例共享同一个 NVS 命名空间（默认为"HXC"）

## 错误处理

库会自动记录错误日志到串口，包括：
- NVS 初始化失败
- 读写操作失败
- 键名过长
- 类型不匹配等

## 示例

完整示例请参考 examples 文件夹。

## 许可证

MIT License