# K230 开发环境搭建与 kmodel 部署指南

> 适用对象：想在嘉楠 K230（RISC-V 双核 C908 + KPU NPU）上跑通端侧 AI 推理的同学。
> 本指南以仓库内已验证的工程 [机器狗-k230/code/K230_KFS_detection/](../../../projects/robotics/机器狗-k230/code/K230_KFS_detection/) 为实例。
> ⚠️ 实机验证环境：常州工学院 A416 实验室。无硬件的同学可先读通流程，再到实验室上机。

## 1. K230 是什么

K230 是嘉楠科技（Canaan）推出的端侧 AI SoC：

- **CPU**：RISC-V 双核 C908（1.6GHz + 800MHz）
- **NPU**：自研 KPU，支持 INT8/INT16 量化推理
- **开发生态**：CanMV（MicroPython 快速原型）+ C/C++ SDK；模型通过 **nncase** 编译为 `.kmodel`

## 2. 开发环境准备

| 组件 | 说明 | 获取方式 |
|---|---|---|
| K230 开发板（CanMV-K230 或等效） | 运行推理的硬件 | 实验室 A416 借用 / 官方渠道 |
| CanMV IDE | MicroPython 开发、烧录与串口调试 | [嘉楠开发者社区](https://developer.canaan-creative.com/) |
| K230 固件 | 烧录到开发板 TF 卡 | 同上，按开发板型号下载 |
| nncase 2.9.0 | 模型编译工具链（训练框架模型 → kmodel） | [github.com/kendryte/nncase](https://github.com/kendryte/nncase) |

> 版本注意：本仓 kmodel 由 **nncase 2.9.0** 编译（见 `deploy_config.json` 的 `nncase_version` 字段）。运行时与编译工具链版本必须匹配，否则推理会报错。

## 3. 仓库实例：3 类易拉罐图像分类

`K230_KFS_detection/` 目录内容：

| 文件 | 作用 |
|---|---|
| `can2_10.0l_20251128175909.kmodel` | 编译好的推理模型（输入 224×224，3 分类：R1 / R2假 / R2真） |
| `deploy_config.json` | 部署配置：输入尺寸、ImageNet mean/std、置信度阈值 0.5、类别表 |
| `cls_image_1_3.py` | 单张图片推理脚本（MicroPython，基于 K230 SDK `libs.PlatTasks.ClassificationApp`） |
| `cls_video_1_3.py` | 摄像头实时视频流推理脚本 |

### 部署步骤（已验证路径）

1. 将 `kmodel`、`deploy_config.json`、`cls_image_1_3.py`（或 `cls_video_1_3.py`）拷贝到开发板 TF 卡 `/sdcard/`
2. 准备测试图片 `test.jpg` 放入 `/sdcard/`（图片推理脚本默认读取该路径）
3. 用 CanMV IDE 连接开发板，打开脚本运行
4. 观察 IDE 帧缓冲/串口输出的分类结果与置信度

## 4. 已知边界（如实说明）

- **模型训练管线未开源**：本仓 kmodel 由 Canaan 在线训练平台生成，仓库内**没有**训练脚本、数据集与训练配置——只能"部署"，不能"复现训练"。
- 这正是 OSPP 课题 #1 的内容：**K230 KPU 端侧 YOLO 检测部署管线开源化**（训练 → 量化 → nncase 编译 → 部署全链路可复现），见 [OSPP 专区](../../ospp/)。
- 推理脚本改写自嘉楠官方示例（署名 "Canaan Developer"），出处见项目 [NOTICE.md](../../../projects/robotics/机器狗-k230/NOTICE.md)。

## 5. 进阶路线

1. 用 nncase 自带示例把 ONNX/TFLite 模型转为 kmodel，理解量化校准（PTQ）流程
2. 将分类模型替换为 YOLOv8n 检测模型，打通"训练→转换→部署"全链路（OSPP 课题 #1 的核心）
3. 推理结果经 UART/串口透传给主控（如 STM32/ESP32），接入机器人动作闭环（参考机器狗项目的 ESP32 子工程）

## 参考链接

- [嘉楠开发者社区 — K230 文档](https://developer.canaan-creative.com/)
- [nncase 仓库与 Release](https://github.com/kendryte/nncase)
- [K230 KFS_detection 实例目录](../../../projects/robotics/机器狗-k230/code/K230_KFS_detection/)
