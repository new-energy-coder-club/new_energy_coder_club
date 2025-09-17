# 🚗 智能车竞赛项目

## 📋 项目概览

本目录包含新能源开发者社区参与的智能车相关竞赛项目，主要聚焦于全国大学生智能汽车竞赛等赛事。

## 🏆 竞赛项目

### [2024智能车室外赛比赛](./2024智能车室外赛比赛/)

**竞赛信息**
- **竞赛全称**: 第十九届全国大学生智能汽车竞赛
- **竞赛类别**: 智能车室外赛
- **参赛时间**: 2024年9月22日开始
- **官方网站**: [www.smartcar.zone](https://www.smartcar.zone)
- **参赛状态**: ✅ 已完成

**团队信息**
- **团队性质**: 跨学院合作队伍（光电学院 + 汽车学院）
- **团队规模**: 5人核心团队
- **实验室**: 汽车院天权2楼C208智能车实验室
- **指导老师**: 顾偲雯、王树磊

**团队分工**
- **电控组** (3人): @Pony17、@单广志、@杨鑫海
- **上位机组** (2人): @DarrenPig、@许子涵涵

**技术栈**
- **硬件平台**: 树莓派5、MicroROS控制板、i5-4200H工控机
- **传感器**: 520编码器减速电机、各类传感器
- **通信技术**: ROS2通信、SSH远程控制
- **开发环境**: Ubuntu、ROS2、JupyterLab
- **仿真平台**: Gazebo、RViz

**项目亮点**
- 🤝 **跨学院合作**: 光电学院提供技术，汽车学院提供场地
- 🔧 **完整开发链**: 从硬件到软件的完整开发体系
- 📱 **远程开发**: 支持SSH远程开发和调试
- 🎯 **模块化设计**: 采用ROS2模块化架构
- 🚀 **快速迭代**: 基于开源硬件快速原型开发

## 🛠️ 技术架构

### 硬件平台

#### 主控系统
- **树莓派5主板**: 主要计算平台
- **MicroROS控制板**: 实时控制系统
- **ROS扩展板**: 传感器接口扩展
- **i5-4200H工控机**: 高性能计算（备选）
- **Atlas200 DK A2**: AI推理加速（备选）

#### 执行机构
- **520编码器减速电机**: 主要驱动电机
- **DDSM210直驱伺服电机**: 精密控制
- **各类传感器**: 环境感知系统

### 软件架构

#### 操作系统
- **Ubuntu 20.04/22.04**: 主要开发环境
- **ROS2 Humble/Foxy**: 机器人操作系统
- **MicroROS**: 微控制器ROS接口

#### 开发工具
- **VSCode**: 主要IDE
- **JupyterLab**: 数据分析和算法开发
- **Git**: 版本控制
- **SSH**: 远程开发

#### 核心功能模块
- **导航系统**: 路径规划和避障
- **感知系统**: 环境感知和目标识别
- **控制系统**: 运动控制和执行
- **通信系统**: 远程监控和调试

## 📚 学习资源

### 官方资源
- **MicroROS Robot**: [官网资料](https://www.yahboom.com/study/MicroROS-ESP32) (提取码：ypom)
- **MicroROS控制板**: [学习资料](https://www.yahboom.com/study/MicroROS-Board) (提取码：dsaf)
- **树莓派5主板**: [官方教程](https://www.yahboom.com/study/raspberry5) (提取码：erwp)
- **ROS扩展板**: [开发文档](https://www.yahboom.com/study/ROS-Driver-Board) (提取码：o8jw)
- **MicroROS-Pi5**: [集成方案](https://www.yahboom.com/study/MicroROS-Pi5) (提取码：sfah)

### 基础教程
- **ROS官方文档**: [http://wiki.ros.org/](http://wiki.ros.org/)
- **JupyterLab教程**: [知乎专栏](https://zhuanlan.zhihu.com/p/154515490)
- **SSH教程**: [阮一峰博客](https://www.ruanyifeng.com/blog/2020/12/ssh-tutorial.html)
- **Git教程**: [廖雪峰教程](https://liaoxuefeng.com/books/git/introduction/index.html)

### 竞赛资源
- **比赛规则**: [官方规则](https://www.smartcar.zone/contents/1132/1109.html)
- **技术论坛**: [智能车竞赛社区](https://www.smartcar.zone)

## 💾 开发资源

### 工控机资源

#### i5-4200H工控机
- **学习资料**: [百度网盘](https://pan.baidu.com/s/1MWCZ9siXVzbo5FwMuML2dw?pwd=po56)
- **系统镜像**: [百度网盘](https://pan.baidu.com/s/1sVVRGg8MxfxSahkiKd_rSw?pwd=4za5)

#### Atlas200 DK A2工控机
- **学习资料**: [百度网盘](https://pan.baidu.com/s/12WCaEZfCkk4PjTPxQnY2ug?pwd=c49d)
- **系统镜像**: [百度网盘](https://pan.baidu.com/s/1r_x2szKCRAl87x26pw_GPA?pwd=u2z6)

### 开发进度追踪

| 阶段 | 内容 | 资源链接 | 状态 |
|------|------|----------|------|
| 1 | 环境搭建 | MicroROS Robot官网资料 | ✅ 完成 |
| 2 | 基础控制 | 键盘控制实现 | ✅ 完成 |
| 3 | 传感器集成 | ROS扩展板集成 | 🔄 进行中 |
| 4 | 导航算法 | 路径规划实现 | 📋 计划中 |
| 5 | 竞赛调试 | 现场调试优化 | 📋 计划中 |

## 📊 项目成果

### 🏅 技术成果
- **完整开发环境**: 建立了从硬件到软件的完整开发链
- **跨平台支持**: 支持多种硬件平台和操作系统
- **模块化架构**: 采用ROS2模块化设计，便于维护和扩展
- **远程开发**: 实现了完整的远程开发和调试流程

### 💡 经验积累
- **团队协作**: 建立了高效的跨学院合作模式
- **技术文档**: 完善的开发文档和学习资源
- **知识传承**: 建立了技术传承和培训体系
- **产学研结合**: 与企业和实验室建立合作关系

## 🔧 开发环境搭建

### 基础环境
```bash
# 安装ROS2
sudo apt update
sudo apt install ros-humble-desktop

# 安装MicroROS
sudo apt install ros-humble-micro-ros-setup

# 配置开发环境
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 硬件连接
1. **树莓派5** - 主控制器
2. **MicroROS控制板** - 实时控制
3. **ROS扩展板** - 传感器接口
4. **电机驱动** - 运动控制

### 远程开发
```bash
# SSH连接
ssh pi@raspberry_ip

# 启动ROS节点
ros2 launch smart_car main.launch.py

# 远程监控
ros2 topic list
ros2 topic echo /cmd_vel
```

## 🚀 未来规划

### 技术升级
- **AI集成**: 集成更多人工智能算法
- **5G通信**: 升级到5G通信技术
- **边缘计算**: 部署边缘计算节点
- **数字孪生**: 建立数字孪生仿真系统

### 竞赛目标
- **2025年竞赛**: 争取获得更好的竞赛成绩
- **技术创新**: 在算法和硬件方面实现创新
- **团队扩建**: 招募更多优秀成员
- **经验传承**: 建立完善的培训体系

## 📞 联系我们

### 👨‍💻 团队成员
- **项目负责人**: DarrenPig
- **电控负责人**: Pony17
- **技术顾问**: 许子涵涵
- **指导老师**: 顾偲雯、王树磊

### 🌐 项目链接
- **代码仓库**: [Gitee仓库](https://gitee.com/darrenpig/new_energy_coder_club/tree/master/competitions/2024/smart-car-outdoor)
- **技术文档**: [项目Wiki](./2024智能车室外赛比赛/README.md)
- **学习资源**: 上述各类官方资源链接

---

*最后更新: 2025年1月*

> 💡 **加入我们**: 欢迎对智能车技术感兴趣的同学加入我们的团队！我们提供完整的技术培训和实战机会，一起探索智能驾驶的未来！