# 颜色识别IIC寄存器

## 设备地址：0x52



- ### 颜色识别

  | 寄存器地址 |                   数据格式(unsigned char)                    |
  | :--------: | :----------------------------------------------------------: |
  |    0x00    | data[0]:红色中心X轴坐标<br/>data[1]:红色中心Y轴坐标<br/>data[2]:红色检测框宽度<br/>data[3]:红色检测框长度<br/> |
  |    0x01    | data[0]:蓝色中心X轴坐标<br/>data[1]:蓝色中心Y轴坐标<br/>data[2]:蓝色检测框宽度<br/>data[3]:蓝色检测框长度<br/> |
  

## 文件目录
- `ColorDetection.ino` 主程序入口
- `color_detection.cpp` 颜色识别算法逻辑
- `color_detection.hpp` 颜色识别算法声明
- `iic_data_send.cpp` IIC 数据打包与发送
- `iic_data_send.hpp` IIC 发送声明

```
ColorDetection/
├── ColorDetection.ino
├── color_detection.cpp
├── color_detection.hpp
├── iic_data_send.cpp
└── iic_data_send.hpp
```

## 原始文档位置
- 远程颜色检测说明：`1）IOT拓展课程/7.远程颜色检测/7.1 远程颜色检测说明.pdf`
- ESP32S3 颜色识别工程：`1）IOT拓展课程/7.远程颜色检测/7.2 ESP32S3颜色识别程序/ColorDetection/`
- Arduino 环境配置与安装包：`1）IOT拓展课程/2.程序下载/2.1 视觉模块程序下载/`

```
1）IOT拓展课程/
└── 7.远程颜色检测/
    ├── 7.1 远程颜色检测说明.pdf
    └── 7.2 ESP32S3颜色识别程序/
        └── ColorDetection/
            ├── ColorDetection.ino
            ├── color_detection.cpp
            ├── color_detection.hpp
            ├── iic_data_send.cpp
            └── iic_data_send.hpp
```

## 源码要点摘录
- `ColorDetection.ino`
  - 创建图像与IIC数据队列：`xQueueAIFrame`、`xQueueIICData`
  - 注册任务：`register_camera(...)`、`register_color_detection(...)`、`register_iic_data_send(...)`
- `color_detection.cpp`
  - 颜色阈值定义 `std_color_info`：红/黄/绿/蓝/紫，支持阈值与最小面积配置
  - 从检测结果写入 `color_data[]`（中心坐标、宽度、长度），并通过队列输出
- `iic_data_send.cpp`
  - I2C 从机地址 `0x52`，`onReceive` 读取寄存器号，`onRequest` 返回对应颜色的4字节数据
  - 颜色寄存器映射：`0x00` 红、`0x01` 绿、`0x02` 蓝（与说明文档可能存在差异，集成时请统一约定）

## 快速说明
- 编译平台：Arduino IDE（建议安装 ESP32 包）
- 串口波特率：115200（参考工程默认）
- IIC 数据格式：见表格（寄存器 0x00 红色，0x01 蓝色）
