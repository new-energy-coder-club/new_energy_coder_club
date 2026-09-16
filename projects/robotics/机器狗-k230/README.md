# 轮腿机器狗 K230（MechDog KFS）

> 状态：🟢 活跃 ｜ Maintainer: @DarrenPig ｜ 技术栈：**RISC-V K230 + KPU** / nncase kmodel / ESP32 / ESP32-S3
> 目标：基于 K230 与 KFS 方案的轮腿机器狗，验证传感、控制与机电协同；面向竞赛与教学的模块化工程。

## 硬件 BOM

| 模块 | 型号/说明 |
|---|---|
| 本体 | 幻尔（Hiwonder）MechDog Pro 轮腿机器狗 |
| 视觉计算 | 嘉楠 K230 开发板（RISC-V 双核 C908 + KPU NPU） |
| 视觉子模块 | ESP32 / ESP32-S3 摄像头模组（人脸/颜色识别） |
| 拓展 | 金属机械臂、ASR 语音识别模块 |

## 软件环境

| 组件 | 版本/说明 |
|---|---|
| CanMV IDE + K230 固件 | 见 [K230 上手指南](../../../docs/learn/riscv-ai/k230-getting-started.md) |
| nncase | **2.9.0**（kmodel 编译版本，运行时必须匹配） |
| Arduino IDE + esp32 package | 2.0.11（ESP32/ESP32-S3 子工程） |
| 幻尔 Python 编辑器 | MechDog 主控例程（MicroPython） |

## 代码目录

| 路径 | 说明 |
|---|---|
| `code/K230_KFS_detection/` | **核心**：K230 kmodel 图像分类（3 类易拉罐 R1/R2真/R2假），含部署脚本与配置 |
| `code/esp32_face_detection/FaceDetection/` | ESP32 人脸识别 Arduino 工程（含 IIC 寄存器协议文档） |
| `code/esp32_color_detection/ColorDetection/` | ESP32 颜色识别 Arduino 工程 |
| `code/mechdog_arm_main.py` | 机械臂控制例程主程序 |
| `code/ASR_Code.py` | 语音识别例程（依赖幻尔闭源库，见 [NOTICE.md](./NOTICE.md)） |

## Quickstart

1. **K230 视觉推理**（推荐先跑通，无需整机）：
   将 `code/K230_KFS_detection/` 下 kmodel、deploy_config.json、推理脚本拷入 TF 卡 `/sdcard/`，CanMV IDE 运行。
   详细步骤 → [K230 上手指南](../../../docs/learn/riscv-ai/k230-getting-started.md)
2. **ESP32 视觉子模块**：Arduino IDE 打开 `code/esp32_color_detection/ColorDetection/ColorDetection.ino` 或 `code/esp32_face_detection/FaceDetection/FaceDetection.ino`，编译烧录
3. **机械臂/语音**：用幻尔 Python 编辑器运行 `code/mechdog_arm_main.py` / `code/ASR_Code.py`
4. **联调建议**：按"视觉 → 通信 → 动作"逐步联调，先单模块稳定再跨模块集成

## 已知边界

- 📋 模型训练管线未开源：kmodel 由 Canaan 在线训练平台生成，本仓无训练脚本/数据集。训练→量化→部署全链路开源化已列入 **OSPP 课题 #1**，见 [OSPP 专区](../../../docs/ospp/)
- 📋 IOT 联动例程（`mechdog_iot_main.py`）尚未入库，欢迎贡献

## 产品资料（厂商官方，外部链接）

- MechDog Pro 渠道版资料：https://pan.baidu.com/s/1LahXRI-P0pEQ-tDn42GBPA 提取码：d5p2
- MechDog 2025 版资料：https://pan.baidu.com/s/1oAETxC1i2ORVh3rV5Vza9Q 提取码：d5p2
- 语音识别模块资料：https://pan.baidu.com/s/1R8hlIpHT721zfjP72ydOKw 提取码：tb2d

## 贡献与联系

- 第三方代码出处与许可：见 [NOTICE.md](./NOTICE.md)
- Issues：主仓库 Issues 区（标签 `area:embedded`）
- 上手指引：[RISC-V × AI 学习路径](../../../docs/learn/riscv-ai/)
