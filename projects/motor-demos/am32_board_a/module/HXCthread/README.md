# HXCthread 库 - 基于 FreeRTOS 的轻量级线程库

## 概述

HXCthread 是一个基于 FreeRTOS 实现的 C++ 线程库，提供了类似 std::thread 的接口，简化了在 ESP32 平台上使用 FreeRTOS 创建和管理线程的过程。

## 特性

- 类 std::thread 的简洁接口
- 支持带参数和不带参数的线程函数
- 可指定线程名称、堆栈大小、优先级和核心亲和性
- 线程状态查询功能
- 线程堆栈使用情况监控
- 线程安全停止和等待机制

## 使用方法

### 基本使用

```cpp
#include "HXCthread.hpp"

// 不带参数的线程函数
void myTask() {
    while(1) {
        // 线程工作内容
        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
}

// 带参数的线程函数
void myTaskWithParam(int param) {
    while(1) {
        // 使用参数
        Serial.println(param);
        vTaskDelay(100 / portTICK_PERIOD_MS);
    }
}

void setup() {
    // 创建不带参数的线程
    HXC::thread<> task1(myTask);
    task1.start("MyTask1");
    
    // 创建带参数的线程
    HXC::thread<int> task2(myTaskWithParam);
    task2.start(42, "MyTask2");
}

void loop() {
    // 主循环
}
```

### 线程控制

```cpp
// 获取线程状态
eTaskState state = task1.get_state();

// 获取剩余堆栈
int stackRemaining = task1.get_remaining_stack_size();

// 停止线程
task1.stop();

// 等待线程结束
task1.join();
```

## API 参考

### 模板类

```cpp
template <typename ParamType = void>
class thread;
```

### 构造函数

- `thread(std::function<void(ParamType)> _func)` - 创建带参数的线程
- `thread(std::function<void()> _func)` - 创建不带参数的线程（特化版本）

### 主要方法

- `start()` - 启动线程
  - 参数：
    - `parameter` - 线程参数（仅带参数版本）
    - `taskname` - 线程名称（默认：DEFAULT_TASK_NAME）
    - `stack_size` - 堆栈大小（默认：DEFAULT_STACK_SIZE）
    - `priority` - 优先级（默认：DEFAULT_PRIORITY）
    - `core` - 核心亲和性（默认：tskNO_AFFINITY）

- `stop()` - 停止线程
- `join()` - 等待线程结束
- `get_Handle()` - 获取线程句柄
- `get_remaining_stack_size()` - 获取剩余堆栈大小（需启用INCLUDE_uxTaskGetStackHighWaterMark）
- `get_state()` - 获取线程状态（需启用INCLUDE_eTaskGetState）

## 配置选项

在 FreeRTOSConfig.h 中可配置以下选项：

```c
#define INCLUDE_uxTaskGetStackHighWaterMark 1  // 启用堆栈监控功能
#define INCLUDE_eTaskGetState 1               // 启用线程状态查询功能
```

## 默认值

```cpp
#define DEFAULT_STACK_SIZE 2048    // 默认堆栈大小
#define DEFAULT_PRIORITY 5         // 默认优先级
#define DEFAULT_TASK_NAME "DEFAULTNAME" // 默认任务名称
```

## 注意事项

1. 线程函数应包含适当的延迟或阻塞调用，以避免占用过多CPU资源
2. 调用stop()会立即终止线程，可能导致资源未释放
3. join()会阻塞当前线程直到目标线程结束
4. 确保堆栈大小足够，可通过get_remaining_stack_size()监控

## 示例

更多示例请参考 examples 目录。

