# 🏭 流体工作站智能监控系统
250319启动
> **关联Issue**: #IBTPAG  
> **项目状态**: 🟢 活跃开发中 | **最后更新**: 2025年8月  
> **主仓库**: [GitHub - 5轴流体工作站](https://github.com/Darrenpig/5-axis-fluid-workstation) | [Gitee镜像](https://gitee.com/darrenpig/5-axis-fluid-workstation)

## 📋 项目概述

流体工作站智能监控系统是一个集工业自动化、数据采集和AI分析于一体的智能监控平台。项目基于树莓派5、Modbus协议和Qt框架，实现对流体系统的实时监控、预测性维护和智能控制。

**📦 完整项目代码请访问主仓库**:  
👉 [https://github.com/Darrenpig/5-axis-fluid-workstation](https://github.com/Darrenpig/5-axis-fluid-workstation)

> 💡 提示：当前目录包含项目文档和配置，完整源代码和硬件设计请访问主仓库。

### 🎯 核心功能
- **实时监控**: 多传感器数据采集与可视化
- **预测维护**: AI算法预测设备故障和寿命
- **智能控制**: 自动化调节和优化控制策略
- **远程管理**: Web界面和移动端监控支持

## 👥 项目团队

| 角色 | 负责人 | 职责范围 | 联系方式 |
|------|--------|----------|----------|
| 项目负责人 | @DarrenPig | 整体规划、元件采购、BSP开发 | darrenpig@outlook.com |
| 硬件工程师 | @杨鑫海 | 传感器选型、硬件布线、电源管理 | - |
| 算法工程师 | @单广志 | Modbus协议、数据采集、算法开发 | - |
| 前端工程师 | @殷统创 | Qt HMI界面、可视化设计、用户体验 | - |
| 开发工程师 | @Leo TianWW | 树莓派开发、电机控制、系统集成 | - |

## 🛠️ 技术栈

### 硬件平台
- **主控板**: Raspberry Pi 5 (树莓派5)
- **通信协议**: Modbus RTU/ASCII, RS485
- **传感器**: 光电限位开关、温度传感器、流量计
- **执行器**: 步进电机、伺服电机、电磁阀

### 软件架构
```python
# 技术栈矩阵
tech_stack = {
    "操作系统": ["Raspberry Pi OS", "Ubuntu Server"],
    "编程语言": ["Python 3.10", "C++", "QML"],
    "框架库": ["PyTorch", "PyModbus", "PyQT", "NumPy", "Pandas"],
    "通信协议": ["Modbus", "RS485", "HTTP/REST", "WebSocket"],
    "可视化": ["Qt Charts", "Matplotlib", "Grafana"],
    "部署": ["Docker", "Systemd", "Git"]
}
```

## 📁 项目结构

```
20250319流体工作站/
├── 📄 README.md                 # 项目说明文档 (当前文件)
├── ⚙️  environment.yml          # Conda环境配置
├── 🗂️  docs/                   # 项目文档
│   ├── architecture.md        # 系统架构设计
│   ├── api.md                # API接口文档
│   └── deployment.md         # 极速部署指南
├── 🐍 src/                     # 源代码
│   ├── modbus_client/        # Modbus客户端
│   ├── motor_control/        # 电机控制模块
│   ├── data_processing/      # 数据处理
│   ├── ai_models/            # AI预测模型
│   ├── qt_interface/         # Qt界面代码
│   └── main.py              # 主程序入口
├── 📊 data/                   # 数据文件
│   ├── raw/                 # 原始传感器数据
│   ├── processed/           # 处理后的数据
│   └── models/              # 训练好的模型
├── 🔧 config/                # 配置文件
│   ├── modbus_config.yaml    # Modbus配置
│   ├── motor_config.yaml     # 电机参数配置
│   └── system_config.yaml    # 系统配置
└── 📋 tests/                 # 测试代码
    ├── unit_tests/          # 单元测试
    └── integration_tests/   # 集成测试
```

## 🔗 相关资源

### 🌐 外部仓库链接
- **[5轴流体工作站主仓库](https://github.com/Darrenpig/5-axis-fluid-workstation)** - 包含完整的源代码、硬件设计和详细文档
- **[Gitee镜像仓库](https://gitee.com/darrenpig/5-axis-fluid-workstation)** - 国内加速访问

### 📚 技术文档
- [Modbus协议官方文档](https://www.modbus.org/specs.php)
- [树莓派5官方文档](https://www.raspberrypi.com/documentation/)
- [PyQt6文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [PyModbus文档](https://pymodbus.readthedocs.io/)

### 🎥 视频教程
- [流体工作站搭建过程](https://youtube.com/playlist?list=PLX0qU极速C5dVzJ5hTc极速q极速7极速q极速8极速X极速w极速)
- [Modbus通信实战](https://youtube.com/playlist?list=PLX0qUC5dVzJ5hTcq7q8Xw)
- [Qt界面开发教程](https://youtube.com/playlist?list=PLX0qUC5d极速VzJ5hTcq7q8Xw)

## 🚀 快速开始

### 环境配置

```bash
# 1. 安装Miniconda (推荐)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh
bash Miniconda3-latest-Linux-aarch64.sh

# 2. 创建环境
conda create -n fluid_workshop python=3.10
conda activate fluid_workshop

# 3. 安装依赖
pip install -r requirements.txt
```

### 硬件连接

#### 光电限位开关接线
![光电限位开关接线](光电限位开关接线.jpg)

#### RS485通信接口
![485接口图](../image/485COM.png)

#### 引脚定义
![引脚定义](../image/JIDINAQI.png)

### 运行系统

```bash
# 启动数据采集服务
python src/modbus_client/data_collector.py

# 启动Qt界面
python src/qt_interface/main_window.py

# 启动AI预测服务
python src/ai_models/predictive_maintenance.py
```

## 🎯 开发里程碑

### 📅 项目时间线
| 阶段 | 时间节点 | 完成状态 | 负责人 |
|------|----------|----------|--------|
| 需求分析 | 2025-03 | ✅ 已完成 | @DarrenPig |
| 硬件选型 | 2025-03 | ✅ 已完成 | @杨鑫海 |
| 原型开发 | 2025-04 | ✅ 已完成 | @单广志 |
| 系统集成 | 2025-05 | 🟡 进行中 | @Leo TianWW |
| HMI界面 | 2025-06 | 🟡 进行中 | @殷统创 |
| 测试验证 | 2025-07 | 🔲 待开始 | 全体成员 |
| 部署上线 | 2025-08 | 🔲 待开始 | 全体成员 |

### 🔄 当前进度

#### 硬件组 (@杨鑫海)
- ✅ 光电传感器选型和采购完成
- ✅ RS485通信模块测试通过
- ✅ 电源系统设计完成
- 🟡 机械结构优化进行中

#### 软件组 (@单广志)
- ✅ Modbus协议栈集成完成
- ✅ 树莓派5环境配置完成
- ✅ 步进电机驱动开发完成
- 🟡 多轴联动算法开发中

#### 界面组 (@殷统创)
- ✅ Qt开发环境搭建完成
- ✅ 基础界面原型设计
- 🟡 HMI界面联调进行中
- 🔲 数据可视化组件开发

#### 系统组 (@DarrenPig)
- ✅ 项目架构设计完成
- ✅ 开发规范制定
- ✅ 持续集成环境配置
- 🟡 文档体系建设中

## 📊 技术文档

### 系统架构图
![系统架构](../image/Snipaste_2025-03-25_21-58-01.png)

### 通信协议
项目采用Modbus RTU协议进行设备通信：
- **波特率**: 9600 bps
- **数据位**: 8 bits
- **停止位**: 1 bit
- **校验位**: None

### 数据格式
```json
{
  "sensor_id": "photoelectric_001",
  "timestamp": "2025-03-19T10:30:00Z",
  "value": 1,
  "unit": "boolean",
  "status": "normal"
}
```

## 🐛 故障排查

### 常见问题

1. **Modbus通信失败**
   ```bash
   # 检查串口权限
   ls -l /dev/ttyUSB*
   sudo chmod 666 /dev/ttyUSB0
   
   # 测试Modbus连接
   python -c "from pymodbus.client import ModbusSerialClient; client = ModbusSerialClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600); print(client.connect())"
   ```

2. **树莓派GPIO权限问题**
   ```bash
   # 将用户加入gpio组
   sudo usermod -a -G gpio $USER
   sudo reboot
   ```

3. **Python依赖冲突**
   ```bash
   # 使用虚拟环境
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## 📝 维护日志

### 2025年4月
- **2025-04-29**: @DarrenPig, @单广志, @吴洛斌 - 完成485线缆整理和热缩管保护
- **2025-04-30**: @卞乐凌, @Leo TianWW - 完成供电系统布线和限位开关安装

### 2025年5月  
- **2025-05-01**: @郑绍恺, @Leo TianWW, @单广志 - 树莓派5 SSH开发环境部署完成
- **2025-05-02**: @DarrenPig - 光电限位紧固件到货，机械安装完成

### 2025年6月
- **2025-06-15**: @单广志 - 完成多电机同步控制算法
- **2025-06-20**: @殷统创 - Qt界面基础框架开发完成

## 🤝 贡献指南

### 开发流程
1. 在Issues中认领任务
2. 创建特性分支: `git checkout -b feature/your-feature`
3. 遵循编码规范开发
4. 编写单元测试
5. 提交Pull Request

### 代码规范
- 使用Black格式化Python代码
- 遵循PEP 8编码规范
- 所有函数添加类型提示和docstring
- 测试覆盖率要求 > 80%

## 📞 技术支持

### 紧急联系
- **技术问题**: @DarrenPig (darrenpig@outlook.com)
- **硬件问题**: @杨鑫海
- **软件问题**: @单广志
- **界面问题**: @殷统创

### 社区支持
- **主仓库**: [5轴流体工作站 GitHub](https://github.com/Darrenpig/5-axis-fluid-workstation)
- **镜像仓库**: [5轴流体工作站 Gitee](https://gitee.com/darrenpig/5-axis-fluid-workstation)
- **技术论坛**: [NEC技术社区](https://gitee.com/darrenpig/new_energy_coder_club/issues)
- **文档中心**: [项目Wiki](../../../README.md)
- **培训材料**: [AI项目组文档](../README.md)

### 📋 问题报告
如果您遇到任何问题，请优先在以下位置提交：
1. **[GitHub Issues](https://github.com/Darrenpig/5-axis-fluid-workstation/issues)** - 主仓库问题跟踪
2. **[Gitee Issues](https://gitee.com/darrenpig/5-axis-fluid-workstation/issues)** - 镜像仓库问题跟踪
3. **邮件支持**: darrenpig@outlook.com (紧急问题)

> ⚡ 提示：完整源代码、硬件设计文件和详细开发文档都在主仓库中！

---

**许可证**: MIT License  
**版本**: v1.0.0  
**最后更新**: 2025年8月25日

> 💡 提示：本项目是 NEC新能源开发者社区 的核心 AI 项目，欢迎各位开发者参与贡献！
