# RemotePrint 远程打印模块

## 概述

这是一个专为ESP32系列开发板设计的远程打印工具模块，允许将其他ESP32设备上的打印输出通过网络传输到指定的mini开关上显示。基于ESP-NOW协议实现高效、低延迟的无线通信。


## 硬件要求

- 主控设备：任意ESP32系列开发板
- 接收设备：mini开关（需开启RemotePrint功能）

## 安装方法

1. PlatformIO：将remotePrint文件夹复制到您的项目`lib`目录下,或者将remotePrint文件夹中的`remotePrint.hpp ，ESPNOW.hpp`文件复制到您的项目`include`目录下
2. Arduino IDE：将remotePrint文件夹复制到您的项目`libraries`目录下,或者将remotePrint文件夹中的`remotePrint.hpp ，ESPNOW.hpp`文件复制到您的项目`src`目录下

## 使用方法

### 发送端设备（任意ESP32）

```cpp
#include <Arduino.h>
#include "remotePrint.hpp"

void setup() {
  // 初始化远程打印（使用默认密钥和广播地址）
  remotePrinter.setup(); 
  
  // 或者自定义设置（推荐）：
  // remotePrinter.setup(0xFFFF, {0xAA,0xBB,0xCC,0xDD,0xEE,0xFF});
  
  Serial.begin(115200);
}

void loop() {
  // 像使用Serial一样使用远程打印
  remotePrinter.println("Hello from ESP32!");
  delay(1000);
  
  // 支持所有Print类方法
  remotePrinter.printf("Sensor value: %.2f\n", 25.6f);
}
```

### 接收端设备（mini开关）

通过串口Shell启用远程打印功能：
   ```bash
   > remoteprint 1
   > set_esp_now_secret_key 0xFFFF # 必须与发送端密钥一致
   ```




