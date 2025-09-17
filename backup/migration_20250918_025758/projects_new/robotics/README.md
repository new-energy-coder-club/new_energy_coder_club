# 机器人技术项目 (Robotics Projects)

本目录包含NEC在机器人技术领域的各类项目，涵盖人形机器人、无人机、移动机器人等多个研究方向。

## 🤖 项目概览

### 人形机器人 (Humanoid Robot)
专注于双关节行走、人机交互和智能控制的人形机器人研发项目。

#### [人形机器人主线](./humanoid-robot/人形机器人主线/)
- **项目类型**: 双足人形机器人
- **技术栈**: ROS2, Python/C++, 运动控制算法
- **核心功能**: 步态规划、平衡控制、视觉导航
- **状态**: 核心开发阶段
- **负责人**: 待更新

### 飞行控制系统
基于开源飞控的电控开发和多电机协同控制优化。

#### [250510飞控通讯](./250510飞控通讯/)
- **项目类型**: 无人机飞控系统
- **技术栈**: PX4, MAVLink, C/C++
- **核心功能**: 双下位机通讯、单手柄控制
- **交付日期**: 2025年6月30日
- **团队成员**: @DarrenPig, @yansonkun, @仇俊彤
- **状态**: 进行中

## 🛠️ 技术栈

### 机器人操作系统
- **ROS2 (Robot Operating System)**: 分布式机器人软件框架
- **Gazebo**: 3D机器人仿真环境
- **RViz**: 机器人可视化工具
- **MoveIt**: 运动规划框架

### 控制算法
- **PID控制**: 经典反馈控制算法
- **模型预测控制 (MPC)**: 先进控制策略
- **强化学习**: 智能控制算法
- **卡尔曼滤波**: 状态估计算法

### 硬件平台
- **单板计算机**: Raspberry Pi, NVIDIA Jetson
- **微控制器**: STM32, ESP32, Arduino
- **传感器**: IMU, 激光雷达, 摄像头, 超声波
- **执行器**: 舵机, 步进电机, 直流电机

### 飞控系统
- **PX4**: 开源飞控固件
- **ArduPilot**: 多平台飞控系统
- **MAVLink**: 无人机通信协议
- **QGroundControl**: 地面控制站软件

## 📋 开发规范

### 项目结构
```
robot_project/
├── README.md              # 项目说明文档
├── package.xml            # ROS包配置文件
├── CMakeLists.txt         # 构建配置文件
├── launch/                # 启动文件
├── src/                   # 源代码
│   ├── nodes/            # ROS节点
│   ├── libs/             # 库文件
│   └── utils/            # 工具函数
├── config/                # 配置文件
├── urdf/                  # 机器人模型文件
├── meshes/                # 3D网格文件
├── worlds/                # 仿真世界文件
├── scripts/               # 脚本文件
├── tests/                 # 测试代码
└── docs/                  # 项目文档
```

### 编码规范
- 遵循ROS2编码规范
- 使用Python 3.8+ 或 C++14+
- 采用面向对象设计模式
- 添加完整的代码注释
- 提供单元测试和集成测试

### 文档要求
每个机器人项目应包含：
- **系统架构**: 整体设计和模块划分
- **硬件清单**: BOM表和接线图
- **软件依赖**: 环境配置和安装说明
- **使用指南**: 启动步骤和操作说明
- **调试指南**: 常见问题和解决方案

## 🚀 快速开始

### ROS2环境搭建
```bash
# Ubuntu 22.04 安装ROS2 Humble
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo sh -c 'echo "deb http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'
sudo apt update
sudo apt install ros-humble-desktop python3-argcomplete

# 环境配置
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 仿真环境
```bash
# 安装Gazebo
sudo apt install ros-humble-gazebo-*

# 安装MoveIt
sudo apt install ros-humble-moveit

# 创建工作空间
mkdir -p ~/robot_ws/src
cd ~/robot_ws
colcon build
source install/setup.bash
```

### PX4飞控开发
```bash
# 克隆PX4源码
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot

# 安装依赖
bash ./Tools/setup/ubuntu.sh

# 编译和仿真
make px4_sitl gazebo
```

## 🎯 应用场景

### 服务机器人
- 🏠 **家庭服务**: 清洁、陪伴、安防
- 🏥 **医疗辅助**: 康复训练、药物配送
- 🏢 **商业应用**: 迎宾、导览、配送

### 工业机器人
- 🏭 **制造业**: 装配、焊接、搬运
- 🚛 **物流**: 分拣、包装、仓储
- 🔧 **维护**: 巡检、维修、清洁

### 特种机器人
- 🚁 **无人机**: 航拍、巡检、救援
- 🌊 **水下机器人**: 探测、维护、科研
- 🔥 **救援机器人**: 消防、搜救、排爆

## 📚 学习资源

### 官方文档
- [ROS2官方教程](https://docs.ros.org/en/humble/)
- [PX4开发指南](https://dev.px4.io/)
- [Gazebo仿真教程](http://gazebosim.org/tutorials)
- [MoveIt运动规划](https://moveit.ros.org/)

### 开源项目
- [TurtleBot3](https://github.com/ROBOTIS-GIT/turtlebot3)
- [Universal Robots](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver)
- [Boston Dynamics Spot](https://github.com/boston-dynamics/spot-sdk)

### 在线课程
- [机器人学导论](https://www.coursera.org/learn/robotics-introduction)
- [现代机器人学](https://www.coursera.org/specializations/modernrobotics)
- [无人机系统](https://www.edx.org/course/autonomous-navigation-for-flying-robots)

## 🔧 开发工具

### 仿真软件
- **Gazebo**: 物理仿真环境
- **CoppeliaSim**: 机器人仿真平台
- **Webots**: 专业机器人仿真
- **AirSim**: 无人机仿真环境

### 设计工具
- **SolidWorks**: 3D机械设计
- **Fusion 360**: 集成设计平台
- **KiCad**: 电路设计工具
- **Blender**: 3D建模和动画

### 调试工具
- **RQT**: ROS图形化调试工具
- **PlotJuggler**: 数据可视化工具
- **Wireshark**: 网络协议分析
- **GDB**: 程序调试器

## 🏆 竞赛项目

### 国际竞赛
- **RoboCup**: 机器人世界杯
- **DARPA Robotics Challenge**: 美国国防部机器人挑战赛
- **Amazon Robotics Challenge**: 亚马逊机器人挑战赛

### 国内竞赛
- **全国大学生机器人大赛**: RoboMaster、RoboCon
- **中国机器人大赛**: 各类机器人竞技项目
- **全国智能车竞赛**: 智能车技术挑战

## 🤝 合作交流

### 学术合作
- 与高校实验室联合研究
- 参与国际学术会议
- 发表高质量论文
- 申请科研项目资助

### 产业合作
- 与机器人公司技术合作
- 参与产品原型开发
- 提供技术咨询服务
- 开展人才培养项目

## 📞 联系方式

- **技术讨论**: 机器人技术交流群
- **项目合作**: 22230635@czu.cn
- **学术交流**: 机器人学术研讨组
- **竞赛组队**: 机器人竞赛团队群

---

*最后更新: 2025年1月*
*维护者: 机器人技术项目组*