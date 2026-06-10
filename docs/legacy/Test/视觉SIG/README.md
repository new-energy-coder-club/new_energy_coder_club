# 视觉 SIG (Visual SIG)

## 一、SIG 定义与目标
**SIG (Special Interest Group)**：即“专题技术小组”，旨在打破传统单一职能边界，围绕“视觉系统交付”这一明确主题，聚合算法、硬件与测试能力。

**核心目标**：
- 不止于“写代码”，而是对 **从设备选型到算法部署再到实机联调** 的端到端视觉系统负责。
- 建立更短的沟通链路、更稳定的协作关系与更清晰的交付责任。

---

## 二、组织架构 (小组负责制)
以 **“视觉系统小组”** 为基本作战单元，实行 **算法+硬件+测试** 一体化运作。

### [1. 上位机与视觉算法](./算法/) (Algorithms & Software)
- **职责**：
  - **识别与推理**：模型训练（YOLO等）、推理加速（TensorRT/ONNX）、传统图像处理（OpenCV）。
  - **应用开发**：上位机交互界面（Qt/WinForms）、通信协议栈（TCP/UDP/Serial）。
  - **策略逻辑**：视觉数据滤波、坐标解算、预测算法。

### [2. 硬件调试与驱动接口](./硬件/) (Hardware & Drivers)
- **职责**：
  - **计算平台**：K230、树莓派 5、Jetson Nano 等嵌入式主板的系统配置与环境搭建。
  - **感知设备**：工业相机/USB摄像头选型、镜头焦距计算、补光方案设计。
  - **通信链路**：驱动稳定性测试、接口协议（MIPI/USB/Eth）调试、线缆选型与抗干扰设计。

### [3. 场务支持与测试环境](./场务/) (Field & Testing)
- **职责**：
  - **数据采集**：搭建标准采集环境（光照/背景）、制作数据集（标注）。
  - **标定流程**：相机内参/外参标定、手眼标定、坐标系转换验证。
  - **实地测试**：复现比赛现场光照条件，进行鲁棒性测试与极限边界测试。

---

## 三、个人进度 (Personal Progress)

| 成员 | 日期 | 进度描述 | 相关链接 |
| :--- | :--- | :--- | :--- |
| **卢永杰** | 260120 | 工业相机 SDK 实操 (C#+Winform+海康) | [B站视频](https://www.bilibili.com/video/BV1VnBTBiE7R) |
| **卢永杰** | 260121 | OpenCV+YOLO 实时目标检测 | [B站视频](https://www.bilibili.com/video/BV1M7oMYXE5h) |
| **卢永杰** | 260125 | 树莓派5 部署 YOLOv8/v11 | [B站视频](https://www.bilibili.com/video/BV1zCWYzvEA7) |
| **郭童童** | 260125 | 中科大电控合集 (1-5.3) | - |
| **郭童童** | 260126 | 树莓派 5 学习 erwp | [Yahboom教程](https://www.yahboom.com/study/raspberry5) |
| **汪奕希** | 260121 | 哈工大竞培营课程 (第一讲) | [B站视频](https://www.bilibili.com/video/BV1iH4jz4EPo) |
| **汪奕希** | 260126 | 哈工大竞培营课程 (第二讲) | [B站视频](https://www.bilibili.com/video/BV1iH4jz4EPo) |
| **杨彩妮** | 260121 | 哈工大竞培营课程 (第一讲) | [B站视频](https://www.bilibili.com/video/BV1iH4jz4EPo) |
| **杨彩妮** | 260125 | 哈工大竞培营课程 (第二讲) | [B站视频](https://www.bilibili.com/video/BV1iH4jz4EPo) |
| **白逸鸣** | 260121 | 哈工大竞培营课程 (第一讲) | [B站视频](https://www.bilibili.com/video/BV1iH4jz4EPo) |
| **白逸鸣** | 260126 | 哈工大竞培营课程 (第二讲) | [B站视频](https://www.bilibili.com/video/BV1iH4jz4EPo) |
| **卞乐凌** | 260131 | 从零开始制作RoboMaster步兵机器人全集 | [B站视频](https://www.bilibili.com/video/BV1g14y1j7Zi) |

*(请保持格式统一：`YYMMDD @姓名 内容 [链接]` 或表格形式)*

---

## 四、建议学习路径
1. **编程语言**：优先 Python 生态（快速验证），掌握 C++（高性能部署）。
2. **基础操作**：OpenCV 核心操作（读取/变换/色彩空间/形态学）。
3. **硬件认知**：熟悉工业相机特性（曝光/增益/触发）及嵌入式平台（Linux基础）。
