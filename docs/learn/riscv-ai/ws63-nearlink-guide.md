# WS63 星闪（NearLink）开发指南

> 适用对象：想基于海思 WS63/WS63E（RISC-V 内核，Wi-Fi 6 + 星闪 SLE 多模）做无线应用的同学。
> 本指南配套仓库项目 [projects/星闪手柄/](../../../projects/星闪手柄/)（OSPP 2024 参与项目）。
> ⚠️ 实机验证环境：常州工学院 A416 实验室。

## 1. WS63 是什么

WS63/WS63E 是海思推出的高集成 2.4GHz 多模 SoC：

- **内核**：RISC-V 高性能 32bit 处理器
- **无线**：Wi-Fi 6 + 星闪 SLE（NearLink）+ 蓝牙
- **系统**：支持 LiteOS / OpenHarmony 轻量系统
- **外设**：SPI、UART、I2C、PWM、GPIO，6 路 13bit ADC，合封 Flash 直接运行程序

## 2. 开发板选型（本社区已用）

| 开发板 | 特点 | 硬件资料 |
|---|---|---|
| BearPi-Pico_H3863（小熊派） | 入门友好、教程丰富 | [fbb_ws63/docs/hardware/BearPi-Pico_H3863](https://gitee.com/HiSpark/fbb_ws63/tree/master/docs/hardware/BearPi-Pico_H3863) |
| HiHope NearLink_DK_WS63E | 官方评估板，接口全 | [fbb_ws63/docs/hardware/HiHope_NearLink_DK_WS63E_V03](https://gitee.com/HiSpark/fbb_ws63/tree/master/docs/hardware/HiHope_NearLink_DK_WS63E_V03) |

## 3. 开发环境搭建

SDK **不入本仓**（避免海思闭源组件再分发问题），一律从上游获取：

1. **获取 SDK**：`git clone https://gitee.com/HiSpark/fbb_ws63.git`
2. **环境搭建**：按上游 [tools 目录 README](https://gitee.com/HiSpark/fbb_ws63/tree/master/tools) 配置编译环境（Windows/Linux 均有指引）
3. **板级资料**：IO 复用关系、用户手册见上游 [docs/board](https://gitee.com/HiSpark/fbb_ws63/tree/master/docs/board)
4. **本仓补充资料**：[星闪手柄/相关资料/](../../../projects/星闪手柄/) 内有《开发WB63编译环境搭建.pdf》、小熊派官方文档、原理图

## 4. 上手示例（上游 samples）

fbb_ws63 SDK 自带外设示例（`src/application/samples/peripheral/`）：I2C / SPI / UART / PWM 等主从案例；`vendor/` 下有 OLED、AHT20 温湿度、陀螺仪等板级 demo。建议按 **UART → GPIO/PWM → 星闪 SLE 配对通信** 的顺序上手。

## 5. 本社区的星闪实践

- **星闪 SLE 遥控手柄 + WS73 小车**：手柄经星闪 SLE 控制小车，核心样例 `sle_ospp_server.c` 位于 OSPP 上游仓库（`AbrillantLee/yocto-embedded-tools` 的 `hi-sle` 分支），本仓 [星闪手柄 readme](../../../projects/星闪手柄/readme.md) 有结构化摘要与引用
- **OSPP 2024**：基于 openEuler Embedded 的星闪开源应用案例开发（已测试验证）
- **自制硬件**：本仓 `相关资料/` 含自研遥控器 PCB 的 Gerber、原理图与 Keil5 工程

## 6. 进阶方向（OSPP 课题候选）

- 基于 WS63 的星闪传感器组网 Demo × openEuler Embedded（OSPP 课题 #3）
- 星闪手柄固件开源化与协议文档补齐

## 参考链接

- [fbb_ws63 SDK（HiSpark 官方）](https://gitee.com/HiSpark/fbb_ws63)
- [小熊派官网](https://www.bearpi.cn/)
- [openEuler Embedded](https://www.openeuler.org/zh/embedded/)
