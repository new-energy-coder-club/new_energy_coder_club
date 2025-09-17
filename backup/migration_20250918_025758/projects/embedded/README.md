# 嵌入式系统项目 (Embedded Projects)

本目录包含新能源编程俱乐部在嵌入式系统领域的各类项目，涵盖物联网设备、智能硬件、通信协议等多个方向。

## 🔌 项目概览

### 星闪技术 (NearLink)
基于华为星闪技术的无线通信项目，探索新一代短距离无线通信解决方案。

#### [20250426星闪手柄](./nearlink/20250426星闪手柄/)
- **项目类型**: 无线通信设备
- **核心芯片**: WS63/WS63E
- **技术栈**: C/C++, FBB SDK, 星闪协议
- **应用场景**: 游戏手柄、遥控器、HID设备
- **状态**: 开发中
- **负责人**: @22自三杨力滔

## 🛠️ 技术栈

### 主控芯片
- **华为海思**: WS63, WS63E (星闪WiFi6多模芯片)
- **乐鑫科技**: ESP32系列 (WiFi + 蓝牙)
- **STM32**: ARM Cortex-M系列微控制器
- **瑞萨电子**: RA系列MCU

### 开发框架
- **FBB SDK**: 华为统一开发框架
- **ESP-IDF**: 乐鑫物联网开发框架
- **STM32CubeIDE**: ST官方开发环境
- **Arduino**: 快速原型开发平台

### 通信协议
- **星闪 (NearLink)**: 新一代短距离无线通信
- **WiFi 6**: 高速无线局域网
- **蓝牙 5.x**: 低功耗蓝牙通信
- **LoRa/LoRaWAN**: 长距离低功耗通信

## 📋 开发规范

### 项目结构
```
project_name/
├── README.md              # 项目说明文档
├── CMakeLists.txt         # 构建配置文件
├── sdkconfig              # SDK配置文件
├── src/                   # 源代码目录
│   ├── main/             # 主程序
│   ├── components/       # 自定义组件
│   └── include/          # 头文件
├── hardware/             # 硬件设计文件
│   ├── schematic/        # 原理图
│   ├── pcb/             # PCB设计
│   └── 3d_models/       # 3D模型
├── docs/                 # 项目文档
├── tests/                # 测试代码
└── tools/                # 开发工具
```

### 编码规范
- 使用C99/C++11标准
- 遵循Google C++编码规范
- 函数和变量命名使用下划线风格
- 添加详细的注释和文档
- 使用静态分析工具检查代码质量

### 硬件设计规范
- 使用标准封装和接口
- 预留调试接口和测试点
- 考虑EMC和热设计
- 提供完整的BOM清单
- 包含装配图和使用说明

## 🚀 快速开始

### 开发环境搭建

#### 星闪开发环境
```bash
# 下载FBB SDK
git clone https://gitee.com/HiSpark/fbb_ws63.git

# 安装开发工具
# 参考: tools/HiSparkStudio工具下载及安装.md
```

#### ESP32开发环境
```bash
# 安装ESP-IDF
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh
. ./export.sh
```

### 支持的开发板

| 开发板 | 芯片 | 特性 | 购买链接 |
|--------|------|------|----------|
| HiHope_NearLink_DK3863E_V03 | WS63E | WiFi6+星闪+蓝牙 | [淘宝链接](https://main.m.taobao.com/security-h5-detail/home?id=808369265492) |
| BearPi-Pico_H3863 | WS63 | 高集成度开发板 | [淘宝链接](https://item.taobao.com/item.htm?id=821386760379) |
| ESP32-DevKitC | ESP32 | WiFi+蓝牙双模 | [官方商店](https://www.espressif.com/zh-hans/products/devkits) |

## 📚 学习资源

### 官方文档
- [星闪技术白皮书](https://www.hisilicon.com/cn/products/connectivity/short-range-wireless)
- [ESP32技术参考手册](https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32/)
- [STM32开发指南](https://www.st.com/zh/development-tools/stm32cubeide.html)

### 开源项目
- [ESP32 Arduino库](https://github.com/espressif/arduino-esp32)
- [STM32 HAL库示例](https://github.com/STMicroelectronics/STM32CubeF4)
- [物联网项目集合](https://github.com/phodal/awesome-iot)

### 在线课程
- [嵌入式系统设计](https://www.coursera.org/specializations/embedded-systems)
- [物联网开发实战](https://www.edx.org/course/introduction-to-the-internet-of-things-iot)

## 🔧 开发工具

### IDE和编辑器
- **HiSpark Studio**: 华为星闪开发专用IDE
- **VS Code**: 轻量级代码编辑器 + 插件
- **CLion**: JetBrains C/C++ IDE
- **Keil MDK**: ARM官方开发环境

### 调试工具
- **J-Link**: SEGGER调试器
- **ST-Link**: ST官方调试器
- **ESP-Prog**: ESP32专用调试器
- **逻辑分析仪**: 协议分析和时序调试

### 测试设备
- **示波器**: 信号波形分析
- **频谱分析仪**: 射频信号测试
- **网络分析仪**: 天线和射频电路测试
- **功耗分析仪**: 低功耗设计验证

## 🤝 项目合作

### 合作机会
- 🏭 **产业合作**: 与企业联合开发实际应用项目
- 🎓 **学术研究**: 参与高校科研项目和论文发表
- 🏆 **竞赛项目**: 参加电子设计竞赛和创新大赛
- 💡 **开源贡献**: 为开源社区贡献代码和文档

### 技术交流
- 定期举办技术分享会
- 组织硬件设计评审
- 参与行业技术论坛
- 建立导师制培养体系

## 📞 联系方式

- **技术支持**: 嵌入式技术交流群
- **项目合作**: 22230635@czu.cn
- **硬件设计**: 硬件设计讨论组SIG
- **问题反馈**: GitHub/Gitee Issues

---

*最后更新: 2025年1月*
*维护者: 嵌入式项目组*