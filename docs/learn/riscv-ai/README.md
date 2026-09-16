# RISC-V × AI 学习路径

> NEC 社区的 RISC-V × 边缘 AI 技术主线学习入口。
> 主线硬件：**嘉楠 K230**（RISC-V 双核 C908 + KPU NPU）与 **海思 WS63**（RISC-V 内核 + 星闪 NearLink）。

## 学习路径总览

```
阶段一：RISC-V 基础          阶段二：端侧 AI 部署           阶段三：系统与生态
├─ RISC-V 架构导论           ├─ K230 开发环境搭建 ────────┐ ├─ openEuler Embedded
│  （PLCT 公开课）           │  → k230-getting-started.md │ ├─ RT-Thread / LiteOS
├─ 嵌入式 Linux 基础         ├─ nncase 模型转换与量化      │ ├─ 星闪 SLE 协议与组网
└─ 交叉编译工具链            ├─ ESP32-S3 视觉子系统       │ └─ ROS 2 机器人栈
                             └─ WS63 星闪开发 ────────────┘      ↑ OSPP 课题方向
                                → ws63-nearlink-guide.md
```

## 本仓教程

| 教程 | 内容 | 前置 |
|---|---|---|
| [k230-getting-started.md](./k230-getting-started.md) | K230 开发环境搭建与 kmodel 部署（以仓库内机器狗视觉工程为实例） | 嵌入式基础 |
| [ws63-nearlink-guide.md](./ws63-nearlink-guide.md) | WS63 星闪开发指南（SDK 获取、烧录、SLE 样例） | C 语言基础 |

## 本仓实战资产

| 资产 | 位置 | 说明 |
|---|---|---|
| K230 kmodel 图像分类（3 类易拉罐识别） | [projects/robotics/机器狗-k230/code/K230_KFS_detection/](../../../projects/robotics/机器狗-k230/code/K230_KFS_detection/) | nncase 2.9.0 工具链，含部署脚本 |
| ESP32 / ESP32-S3 人脸与颜色识别 | [projects/robotics/机器狗-k230/code/](../../../projects/robotics/机器狗-k230/code/) | Arduino 工程 |
| 星闪 SLE 遥控手柄 | [projects/星闪手柄/](../../../projects/星闪手柄/) | OSPP 2024 参与项目 |
| AGL × openEuler 适配结项 | [projects/research-horizontal/AGL-openEuler.md](../../../projects/research-horizontal/AGL-openEuler.md) | OSPP 结项报告范例 |

## 外部资源索引

**RISC-V 与开源社区**
- [PLCT 实验室（中科院软件所）](https://plctlab.org/) — RISC-V 公开课、甲辰计划、实习机会
- [RISC-V 国际基金会](https://riscv.org/) — 指令集规范与生态动态
- [开源之夏官网](https://summer-ospp.ac.cn/) — 学生开源活动

**K230 / 嘉楠**
- [嘉楠开发者社区](https://developer.canaan-creative.com/) — K230 SDK、CanMV、文档与论坛
- [nncase GitHub](https://github.com/kendryte/nncase) — KPU 神经网络编译器（模型转换/量化）

**WS63 / 星闪**
- [fbb_ws63 SDK（HiSpark）](https://gitee.com/HiSpark/fbb_ws63) — WS63/WS63E 官方开源 SDK，含示例与硬件资料
- [小熊派 BearPi](https://www.bearpi.cn/) — BearPi-Pico_H3863 开发板教程
- [openEuler Embedded](https://www.openeuler.org/zh/embedded/) — 嵌入式 Linux 生态

---

> 贡献：发现教程过时或有误？欢迎提 Issue（`area:embedded` 标签）或直接 PR，见 [CONTRIBUTING](../../../CONTRIBUTING.md)。
