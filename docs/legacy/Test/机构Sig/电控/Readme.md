# NEC 电控

## 一、定位与目标
- 电控组负责机器人电气与控制系统的设计、开发与联调
- 今年的电控组，我们将继续保持之前的合作模式，即每个成员负责一个子模块的开发。
- 与往年不同，今年我们希望所有的电控与机械成员合作起来，共同承担机器人项目中的所有任务。
- 不需要有明确的责任边界，做一种文化，做成一个高凝聚力的组织。

## 二、协作与反馈
- 需求与问题跟踪：https://gitee.com/darrenpig/new_energy_coder_club/issues/ICGYAY
- 重要变更用文字记录，保证可追溯与可交接

## 三、学习资料
- 中科大 RM 电控合集
- 入门与实战课程：https://www.bilibili.com/video/BV1XHi7BZEU1?vd_source=c7437912ce16dd349e9bcfd59699e4c4&spm_id_from=333.788.videopod.sections

## 四、个人进度
| 成员 | 日期 | 进度描述 | 相关链接 |
| :--- | :--- | :--- | :--- |
| **魏卫** | 260121 |中科大RM电控合集 观看了clion环境配置教程，结合claude code辅助，完成了STM32H723项目的CLion+OpenOCD调试环境配置 | [B站视频](https://www.bilibili.com/video/BV1Rx4y1C7d4) |
| **魏卫** | 260124 |中科大RM电控合集 观看了达妙板篇，配置了点灯程序并成功编译烧录，但是没有5v供电，没有看到效果；后烧录官方IMU例程，通过keil的debug初步观察pitch俯仰角和roll横滚角；| [B站视频](https://www.bilibili.com/video/BV1XHi7BZEU1) |
| **魏卫** | 260127 |中科大RM电控合集 学习了CAN总线的理论知识；收到了24V电源转换器，烧录运行了点灯与彩灯等例程；购入XT30母对母转接线用于后续的DM3519调试；| [B站视频](https://www.bilibili.com/video/BV1HY411D7Ar) |
| **魏卫** | 260130 | 中科大RM电控合集 一开始在 [kit/电机控制例程 - Gitee.com](https://gitee.com/kit-miao/motor-control-routine/tree/master/stm32例程/dm_ctrl(DM3519 一拖四))的基础上编译烧录，调试失败，后来多次寻找官方文档，找到后用AI辅助修改底层协议，最终用MIT模式成功实现电机控制 | [DM-S3519-1EC 使用说明书 V1.1 (PDF)](https://gitee.com/kit-miao/DM-S3519-1EC/blob/master/DM-S3519-1EC%E5%87%8F%E9%80%9F%E7%94%B5%E6%9C%BA%EF%BC%88%E5%90%ABDM3520-1EC%E9%A9%B1%E5%8A%A8%E5%99%A8%EF%BC%89%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E%E4%B9%A6V1.1.pdf) |
| **王欣怡** | 260121 | 中科大RM电控合集 观看了Git基础操作教学和1.1的电控简介对其资料的位置以及整体流程有了初步了解 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **王欣怡** | 260123 | 中科大RM电控合集 观看了2.1的环境配置并且已经完成环境调试，正在学习2.2的基础知识| [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **王欣怡** | 260123 | 中科大RM电控合集 CubeMX今天使用的时候报错了，部分信息没办法及时更新全删掉重新进行了安装并在网上购买了与视频教程一样型号的STM32板子还没到继续学习2.2的基础知识| [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **王欣怡** | 260129 | 中科大RM电控合集的 今天把2.2的GPIO学完了，并且代码准备明天把板子拿到手就直接烧代码点灯，并且通过查找资料对自己的负责部分有了初步理解| [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **王欣怡** | 260130 | 中科大RM电控合集 学完了2.3和2.4的定时器中断和外部中断，代码实际应用时发现课程所教使用的cpp11对我而言不适用会出现报错要用c99| [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **王欣怡** | 260201 | 中科大RM电控合集 学习2.5内容| [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **孙诗睿** | 260121 | 中科大RM电控合集 观看了1.1的电控简介，对其有了初步的认识，并学习了2.1中一部分的STM32单片机环境配置 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V)| 
| **孙诗睿** | 260123 | 中科大RM电控合集 完成2.1内容，学习了2.2GPIO输出电压。 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **孙诗睿** | 260124 | 中科大RM电控合集 学习了2.3EXTI外部中断。 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **孙诗睿** | 260126 | 中科大RM电控合集 学习了2.4TIM定时器中断。 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **孙诗睿** | 260130 | 中科大RM电控合集 学习了2.5UART通信。 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **梁新雷** | 260121 | 中科大RM电控合集 观看了1.1和2.1对电控理论和stm32单片机环境配置和基础知识有了一定了解 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **文钰婷** | 260122 | 中科大RM电控合集 观看了1.1电控简介有了简单的认识 复习了stm32基础知识 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **文钰婷** | 260125 | 中科大RM电控合集 观看了2.1STM32单片机环境配置|[B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **文钰婷** | 260129 | 中科大RM电控合集，观看了2.3EXTI外部中断|[B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **孟洁** | 260121 |中科大RM电控合集 观看了1.1的电控简介，对其有了简单的认识 复习了stm32基础知识 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **岳添俊** | 260121 |中科大RM电控合集 观看了1.1，并对电控简介有了了解，学习了2.2中stm32的基础知识 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **岳添俊** | 260123 |中科大RM电控合集 观看了2.2进一步学习STM32CubeMX-GPIO输出电压的相关知识 | [B站视频](https://www.bilibili.com/video/BV1hQ4y167ri?vd_source=5fd636356f1b9e917e7df1c877f5b503) |
| **李畅畅** | 260121 |中科大RM电控合集 观看了2.1配置环境，2.4TIM定时器中断，3.12大疆电机，学习代码和了解产品 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **李畅畅** | 260123 |中科大RM电控合集 观看了2.6PWM呼吸灯理论 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **李畅畅** | 260126 |中科大RM电控合集 观看了2.5STM32CubeMX UART通信 | [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **李畅畅** | 260130 |中科大RM电控合集 观看了2.6PWM呼吸灯实操测试，CAN通信开头部分| [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **孟洁** | 260124 |中科大RM电控合集 观看了2.1STM32单片机环境配置，2.3EXTI外部中断| [B站视频](https://www.bilibili.com/video/BV1z14y1G77V) |
| **吴梦婷** | 260127 | 中科大RM电控合集 观看了2.3STM32CubeMX-EXTI外部中断 | [B站视频](https://www.bilibili.com/video/BV14T4y1Z7XF?vd_source=b4605d95465c67d41069f2d4bd865c02)|
| **田旺旺** | 260131 | B站最新Trae全套实战保姆级教程，一周从入门到精通全集 | [B站视频](https://www.bilibili.com/video/BV1hdsjzjEhZ)|
*(请保持格式统一：`YYMMDD @姓名 内容 [链接]` 或表格形式)*
<<<<<<< HEAD
=======