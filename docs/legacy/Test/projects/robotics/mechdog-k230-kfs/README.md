# Project_MechDog 机器狗 K230 KFS

- 目标：基于 K230 与 KFS 方案的轮腿机器狗，验证传感、控制与机电协同
- 范式：模块化驱动、实时控制、可复用接口，面向竞赛与教学

## 代码目录
- `code/mechdog_iot_main.py` IOT 控制例程主程序1
- `code/mechdog_arm_main.py` 机械臂控制例程主程序11
- `code/esp32s3_face_detection/` ESP32S3 人脸识别完整工程11
- `code/esp32s3_color_detection/` ESP32S3 颜色识别完整工程11
- `code/esp32_face_detection/` ESP32 人脸识别完整工程1
- `code/esp32_color_detection/` ESP32 颜色识别完整工程

## 学习路线
1. 环境准备
   - 安装 Arduino IDE 与依赖：[Arduino环境搭建.pdf](1）IOT拓展课程/2.程序下载/2.1 视觉模块程序下载/2.1.1 Arduino环境搭建.pdf)
   - Arduino 安装包：
     - [ArduinoIDE-2.2.1.exe](1）IOT拓展课程/2.程序下载/2.1 视觉模块程序下载/2.1.3 Arduino安装包/ArduinoIDE-2.2.1.exe)
     - [esp32_package_2.0.11_arduinome.exe](1）IOT拓展课程/2.程序下载/2.1 视觉模块程序下载/2.1.3 Arduino安装包/esp32_package_2.0.11_arduinome.exe)
   - 安装幻尔 Python 编辑器：
     - [Hiwonder.exe](1）IOT拓展课程/2.程序下载/2.2 MechDog程序下载/2.2.3 幻尔Python编辑器安装包/Hiwonder.exe)
     - 编辑器介绍：[幻尔Python编辑器介绍.pdf](2）金属机械臂拓展课程/1.程序下载/1.1 幻尔Python编辑器介绍.pdf)

2. 视觉感知（ESP32/ESP32S3）
   - 人脸识别：
     - ESP32S3 工程：[FaceDetection](1）IOT拓展课程/4.人脸检测预警/4.2 ESP32S3人脸识别程序/FaceDetection/)
     - 汇总代码：`code/esp32s3_face_detection/`
   - 颜色识别：
     - ESP32S3 工程：[ColorDetection](1）IOT拓展课程/7.远程颜色检测/7.2 ESP32S3颜色识别程序/ColorDetection/)
     - 汇总代码：`code/esp32s3_color_detection/`
   - 远程颜色检测说明：[7.1 远程颜色检测说明.pdf](1）IOT拓展课程/7.远程颜色检测/7.1 远程颜色检测说明.pdf)

3. IOT 控制联动
   - MechDog IOT 例程：`code/mechdog_iot_main.py`
   - 程序下载说明：[2.2 MechDog IOT程序下载.pdf](1）IOT拓展课程/2.程序下载/2.2 MechDog程序下载/2.2.2 MechDog IOT程序下载.pdf)
   - APP 安装与使用：
     - [IoT Control-V1.0.2.apk](1）IOT拓展课程/3.APP安装/3.2 APP安装包/IoT Control-V1.0.2.apk)
     - [3.1 APP使用说明.pdf](1）IOT拓展课程/3.APP安装/3.1 APP使用说明.pdf)

4. 机械臂拓展
   - 机械臂例程：`code/mechdog_arm_main.py`
   - 程序下载说明：[1.2 MechDog程序下载.pdf](2）金属机械臂拓展课程/1.程序下载/1.2 MechDog程序下载.pdf)
   - 控制说明：[2.2 机械臂控制说明.pdf](2）金属机械臂拓展课程/2.机械臂控制/2.2 机械臂控制说明.pdf)
   - APP 安装包：[Wonderbot-V2.1.4.apk](2）金属机械臂拓展课程/2.机械臂控制/2.1 APP安装/2.1.2 APP安装包/Wonderbot-V2.1.4.apk)

5. 辅助能力与安全
   - 警示与遥控：
     - [10.1 远程警示说明.pdf](1）IOT拓展课程/10.远程警示/10.1 远程警示说明.pdf)
     - [11.1 远程遥控说明.pdf](1）IOT拓展课程/11.远程遥控/11.1 远程遥控说明.pdf)
   - 测距与开灯：
     - [8.1 远程测距说明.pdf](1）IOT拓展课程/8.远程测距/8.1 远程测距说明.pdf)
     - [9.1 远程开灯说明.pdf](1）IOT拓展课程/9.远程开灯/9.1 远程开灯说明.pdf)

6. 综合联调建议
   - 将视觉识别结果（人脸/颜色）通过串口/网络透传至 IOT 控制层，驱动 MechDog 动作与机械臂协同
- 建议按“视觉→IOT→动作”逐步联调，先单模块稳定再做跨模块集成

## IOT拓展课程 文件结构
```
1）IOT拓展课程/
├── 1.传感器安装及接线/
│   ├── 01 组装.png
│   └── 02 接线.png
├── 2.程序下载/
│   ├── 2.1 视觉模块程序下载/
│   │   ├── 2.1.1 Arduino环境搭建.pdf
│   │   ├── 2.1.2 视觉模块程序下载.pdf
│   │   └── 2.1.3 Arduino安装包/
│   │       ├── ArduinoIDE-2.2.1.exe
│   │       ├── arduino-ide_2.3.2_macOS_arm64.dmg
│   │       ├── esp32_package_2.0.11_arduinome.exe
│   │       └── Mac版安装教程.txt
│   └── 2.1.4 视觉模块程序/
│       ├── 01 人脸识别程序/FaceDetection/
│       └── 02 颜色识别程序/ColorDetection/
├── 3.APP安装/
│   ├── 3.1 APP使用说明.pdf
│   └── 3.2 APP安装包/IoT Control-V1.0.2.apk
├── 4.人脸检测预警/
│   └── 4.1 人脸检测预警说明.pdf
├── 5.不明物体预警/
│   └── 5.1 不明物体预警说明.pdf
├── 6.不明物品撞击预警/
│   └── 6.1 不明物品撞击预警说明.pdf
├── 7.远程颜色检测/
│   ├── 7.1 远程颜色检测说明.pdf
│   └── 7.2 ESP32S3颜色识别程序/ColorDetection/
├── 8.远程测距/8.1 远程测距说明.pdf
├── 9.远程开灯/9.1 远程开灯说明.pdf
├── 10.远程警示/10.1 远程警示说明.pdf
└── 11.远程遥控/11.1 远程遥控说明.pdf
```

## 金属机械臂拓展课程 文件结构
```
2）金属机械臂拓展课程/
├── 1.程序下载/
│   ├── 1.1 幻尔Python编辑器介绍.pdf
│   ├── 1.2 MechDog程序下载.pdf
│   ├── 1.3 幻尔Python编辑器.exe
│   └── 1.4 MechDog机械臂例程/main.py
└── 2.机械臂控制/
    ├── 2.1 APP安装/
    │   ├── 2.1.1 APP使用说明.pdf
    │   └── 2.1.2 APP安装包/Wonderbot-V2.1.4.apk
    └── 2.2 机械臂控制说明.pdf
```

## 快速上手
- 安装工具
  - 安装 Arduino IDE 与 ESP32 包：`1）IOT拓展课程/2.程序下载/2.1 视觉模块程序下载/2.1.1 Arduino环境搭建.pdf`、`2.1.3 Arduino安装包/`
  - 安装幻尔 Python 编辑器：`2）金属机械臂拓展课程/1.程序下载/1.3 幻尔Python编辑器.exe`
- 编译与烧录
  - 颜色识别：打开 `code/esp32_color_detection/ColorDetection/ColorDetection.ino` 编译烧录
  - 人脸识别：打开 `code/esp32_face_detection/FaceDetection/FaceDetection.ino` 编译烧录
- IOT 联动
  - 运行 `code/mechdog_iot_main.py`，按 `1）IOT拓展课程/2.程序下载/2.2 MechDog程序下载/2.2.2 MechDog IOT程序下载.pdf` 设置连接
  - 安装并使用 `IoT Control-V1.0.2.apk` 控制：`1）IOT拓展课程/3.APP安装/`
- 机械臂控制
  - 运行 `code/mechdog_arm_main.py` 并参考 `2）金属机械臂拓展课程/2.机械臂控制/2.2 机械臂控制说明.pdf`
- 联调建议
  - 先验证视觉数据输出，再接入 IOT 控制，最后联动机械臂与底盘动作
## 项目简介
- 轮腿运动控制与姿态稳定
- 关节电机驱动与步态规划
- 传感融合与环境感知

## 产品资料
- MechDog Pro 渠道版资料：https://pan.baidu.com/s/1LahXRI-P0pEQ-tDn42GBPA  提取码：d5p2
- MechDog产品2025版2025版本资料: https://pan.baidu.com/s/1oAETxC1i2ORVh3rV5Vza9Q 提取码: d5p2 
- 语音识别模块资料链接：https://pan.baidu.com/s/1R8hlIpHT721zfjP72ydOKw 提取码：tb2d

## 联系方式
- Maintainer: @DarrenPig
- Issues: 在主仓库提交或顶部 README 的 Issues 区
