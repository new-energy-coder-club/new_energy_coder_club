### 节能减排大赛
![星闪节能 标志图](https://github.com/Darrenpig/new_energy_coder_club/assets/121377489/39f1b1dd-eff7-4b8f-b446-59a44588dd71)

[![节能减排大赛](https://img.shields.io/badge/节能减排大赛-仓库-blue)](https://gitee.com/darrenpig/new_energy_coder_club/tree/master/%E8%8A%82%E8%83%BD%E5%87%8F%E6%8E%92%E5%A4%A7%E8%B5%9B%EF%BC%88Nearlink%E5%B0%8F%E8%BD%A6%E8%AE%A1%E5%88%92%EF%BC%89)         [![物联网设计竞赛-meta_freescale](https://img.shields.io/badge/物联网设计竞赛-仓库-brightgreen)](https://gitee.com/darrenpig/new_energy_coder_club/tree/master/2024%E7%89%A9%E8%81%94%E7%BD%91%E8%AE%BE%E8%AE%A1%E7%AB%9E%E8%B5%9B%EF%BC%88Huawei%E6%95%B0%E9%80%9A%EF%BC%89)



[![lisence.md-meta_freescale](https://img.shields.io/badge/lisence.md-Markdown-violet
)](https://gitee.com/darrenpig/new_energy_coder_club/blob/master/LICENSE.md)
[![Readme.md meta-imx](https://img.shields.io/badge/Readme.md-Markdown-8A2BE2
)](https://gitee.com/darrenpig/new_energy_coder_club/blob/master/README.md)


#### 项目介绍
- **标题**：源头治理-智慧化工
- **简短描述**：低成本、节能的工厂巡检方案
- **长描述及官网地址**：全国大学生节能减排竞赛（能动类）官网

#### 建仓目标
- **主要方向**：化工设计（节能减排绿色工厂设计）
- **特色**：加入四轮工厂巡检小车（光伏、节能运维向）

#### 时间节点
- **5.8**：硬件收工
- **5.10**：两份word初审
- **5.15**：Demo视频拍摄剪辑
- **5.18**：上传文档（注意校团委的章可能需要提前）
- **6.26**: 得知国赛结果--我们在校赛12的基础上，结束啦！
#### 成员分工与进度
- **硬件待办**
  - 负责人：朱佩韦
    - 4.28 电机就位
    - 其他任务...


#### 项目整体思路
1. 造车：上电机（520编码电机）
2. 通讯模块：EB25
3. 供电电源：12V电池盒+稳压模块+太阳能板

#### 额外部分项目进度
- 列出从2.24到5.24期间的具体任务及完成人

#### 项目成员分工
- @和尚：ROS，PWM
- @DarrenPig：上位机
- @郝磊：文档、调研、沟通项管【队长】

#### 资料共享与文档区
- 提供ROS开发板链接、资料共享说明等
---
### 3.1.1  感知层

数据采集： openMV\openCV视觉识别技术用于实时捕获巡检场地信息和人员位置

板载机器人的视觉识别传统机械 压力阀

### 3.1.2  传输层

5G移动基站通信技术  通信模块： 巡检小车配备5G通信模块，与数据网关建立高速、低延迟的数据传输通道 搭建Nearlink抗干扰网络，使用开发板EB25进行BLE透传 使用esp32搭建微型MQTT服务，多链路传输  数据传输： 将采集到的视频、图像、位置信息以及环境数据通过5G网络发送到数据网关 USB串口连接上位机imx8-NXP,将部分数据封装后集成向AR502H-CN传输

### 3.1.3  控制层

综合管理系统  部署环境： 数据网关AR502H-CN容器部署的综合管理系统   功能实现： 接收来自巡检小车的实时数据 数据处理与分析（如人员位置跟踪、环境数据监测等） 巡检任务管理（如设置巡检路线、巡检质量要求、发布临时巡检任务等） 与其他系统（如ERP、MES等）集成，实现数据共享
---
整体开发流程如上，截止2024.6.2提交，已完成Yocto环境编译小车上位机系统openEuler_embedded，下位机ROS开发版RasPi5的控制，RA8视觉开发板的openMV固件烧录，目前小组全体在封装API接口和写入模块，将尽早完成AR502H-CN的网关容器环境开发配置。

# 最近一次的活动
# 我们的2024节能减排大赛收工，我们

# 将在6月29日下午5:50-6:30组会结束后正式赛程。

# 感谢大家接近一年以来的激情与支持，在我最艰难的时候感谢大家的精神支持与物质援助。

# 我们的项目挺到了国赛前的最后一刻，我们的最后是校赛 12（前15） 获得国赛资格，然后学校15的队伍，只有

# 除去我们的三支队伍入选。此时我想说，拜拜节能减排^

现实往往焦灼，环境的无力感，常常充斥着我们的故事。

## 我们这场会议将会决定我们暑假何去何从，是否意志坚定因而留下，或者正常的随着赛程落幕而安心收工。
