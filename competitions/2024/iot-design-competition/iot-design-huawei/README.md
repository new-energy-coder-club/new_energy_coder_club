# 🌐 物联网设计竞赛项目

## 📋 项目概览

本目录包含新能源开发者社区参与的物联网相关竞赛项目，主要聚焦于全国大学生物联网设计竞赛等赛事。

## 🏆 竞赛项目

### [2024物联网设计竞赛_Huawei数通](./2024物联网设计竞赛_Huawei数通/)

**竞赛信息**
- **竞赛全称**: 2024年全国大学生物联网设计竞赛
- **命题方向**: 华为数通（数据网关）
- **项目主题**: 基于openEuler的低功耗巡检小车设计
- **技术架构**: "端-边-云"架构计算
- **应用场景**: 智能工厂巡检系统
- **参赛状态**: ✅ 已完成

**项目展示**
- **在线PPT**: [项目展示网站](https://low-power-inspection-veh-95gmidb.gamma.site/)
- **技术架构图**: 完整的系统架构设计
- **Demo演示**: 实际运行效果展示

## 🛠️ 技术架构

### 核心设备

#### 华为AR502H-CN数据网关
- **产品定位**: 工业级边缘计算网关
- **核心功能**: "端-边-云"架构的关键节点
- **应用场景**: 智能工厂数据汇聚和处理
- **技术特点**: 高可靠性、低功耗、强实时性
- **官方文档**: [AR502H-CN技术文档](https://support.huawei.com/enterprise/zh/routers/ar500-pid-21247181)

### 系统架构

#### "端-边-云"三层架构

**端侧设备**
- **巡检小车**: 基于openEuler的移动巡检平台
- **传感器网络**: 温度、湿度、气体等环境传感器
- **执行器**: 电机、舵机等控制设备
- **通信模块**: 支持多种无线通信协议

**边缘计算**
- **AR502H-CN网关**: 数据预处理和本地决策
- **本地存储**: 关键数据本地缓存
- **实时处理**: 低延迟的实时响应
- **协议转换**: 多协议适配和转换

**云端平台**
- **数据分析**: 大数据分析和挖掘
- **AI算法**: 智能预测和优化
- **远程监控**: 全局监控和管理
- **决策支持**: 智能决策辅助系统

### 技术栈

#### 操作系统
- **openEuler**: 主要操作系统平台
- **openEuler Embedded**: 嵌入式版本
- **实时性**: 支持实时任务调度
- **安全性**: 内置安全机制

#### 开发框架
- **物联网协议**: MQTT、CoAP、HTTP/HTTPS
- **通信技术**: Wi-Fi、蓝牙、LoRa、NB-IoT
- **数据格式**: JSON、XML、Protobuf
- **API接口**: RESTful API设计

#### 核心技术
- **边缘计算**: 本地数据处理和分析
- **机器学习**: 设备状态预测和异常检测
- **数据融合**: 多传感器数据融合
- **安全加密**: 端到端数据加密

## 🎯 项目特色

### 💡 创新亮点

#### 低功耗设计
- **硬件优化**: 选用低功耗芯片和模块
- **软件优化**: 智能休眠和唤醒机制
- **能源管理**: 太阳能供电 + 电池备份
- **功耗监控**: 实时功耗监测和优化

#### 智能巡检
- **自主导航**: SLAM建图和路径规划
- **环境感知**: 多传感器环境监测
- **异常检测**: AI算法实现异常自动识别
- **远程控制**: 支持远程监控和控制

#### 工业级可靠性
- **高可用性**: 99.9%系统可用性设计
- **故障自愈**: 自动故障检测和恢复
- **数据安全**: 多层次数据安全保护
- **环境适应**: 工业环境适应性设计

### 🔧 技术实现

#### 硬件平台
```
巡检小车硬件架构:
├── 主控系统
│   ├── ARM处理器 (openEuler)
│   ├── 存储系统 (eMMC + SD)
│   └── 电源管理 (PMU)
├── 传感器模块
│   ├── 环境传感器 (温湿度、气体)
│   ├── 视觉传感器 (摄像头、激光雷达)
│   └── 运动传感器 (IMU、编码器)
├── 通信模块
│   ├── Wi-Fi模块
│   ├── 蓝牙模块
│   └── LoRa模块
└── 执行机构
    ├── 驱动电机
    ├── 转向舵机
    └── 机械臂 (可选)
```

#### 软件架构
```
软件系统架构:
├── 应用层
│   ├── 巡检应用
│   ├── 数据采集
│   └── 远程控制
├── 中间件层
│   ├── 通信中间件
│   ├── 数据处理
│   └── 设备管理
├── 系统层
│   ├── openEuler内核
│   ├── 驱动程序
│   └── 系统服务
└── 硬件抽象层
    ├── 传感器接口
    ├── 通信接口
    └── 执行器接口
```

## 📊 项目成果

### 🏅 竞赛成绩
- **参赛资格**: 成功通过初审，获得决赛资格
- **技术创新**: 在低功耗和边缘计算方面有所创新
- **实用价值**: 具有实际的工业应用价值
- **团队协作**: 展现了优秀的团队协作能力

### 💡 技术积累
- **物联网技术**: 掌握了完整的物联网开发技术栈
- **边缘计算**: 深入理解边缘计算架构和实现
- **工业应用**: 积累了工业级系统开发经验
- **华为生态**: 熟悉华为技术生态和产品

### 📈 应用前景
- **智能制造**: 可应用于各类智能工厂
- **环境监测**: 适用于环境监测和保护
- **安防巡检**: 可用于安防和巡检场景
- **农业物联网**: 可扩展到农业物联网应用

## 📚 学习资源

### 官方资源
- **华为AR502H-CN**: [产品文档](https://support.huawei.com/enterprise/zh/routers/ar500-pid-21247181)
- **华为命题资料**: [竞赛资料包](https://iot.sjtu.edu.cn/ueditor/net/upload/file/20240327/6384717615388308323667272.pdf)
- **openEuler社区**: [官方网站](https://www.openeuler.org/)
- **华为开发者**: [开发者社区](https://developer.huawei.com/)

### 技术文档
- **物联网协议**: MQTT、CoAP、HTTP协议规范
- **边缘计算**: 边缘计算架构和实现
- **openEuler**: 系统安装和配置指南
- **AR502配置**: 网关配置和管理手册

### 开发工具
- **开发环境**: Ubuntu + openEuler开发环境
- **IDE工具**: VSCode、Eclipse等
- **调试工具**: GDB、Wireshark等
- **仿真平台**: 物联网仿真和测试平台

## 🔧 开发指南

### 环境搭建

#### openEuler开发环境
```bash
# 下载openEuler镜像
wget https://repo.openeuler.org/openEuler-22.03-LTS/ISO/

# 安装开发工具
sudo yum install gcc gcc-c++ make cmake
sudo yum install python3 python3-pip

# 安装物联网开发库
pip3 install paho-mqtt requests
```

#### AR502H-CN配置
```bash
# 登录网关
ssh admin@192.168.1.1

# 配置网络接口
interface GigabitEthernet0/0/1
ip address 192.168.1.1 255.255.255.0

# 配置MQTT服务
mqtt-server enable
mqtt-server port 1883
```

### 核心代码示例

#### 数据采集模块
```python
import paho.mqtt.client as mqtt
import json
import time
from sensors import TemperatureSensor, HumiditySensor

class DataCollector:
    def __init__(self, mqtt_broker, mqtt_port):
        self.client = mqtt.Client()
        self.client.connect(mqtt_broker, mqtt_port, 60)
        self.temp_sensor = TemperatureSensor()
        self.humidity_sensor = HumiditySensor()
    
    def collect_and_send(self):
        while True:
            data = {
                'timestamp': time.time(),
                'temperature': self.temp_sensor.read(),
                'humidity': self.humidity_sensor.read()
            }
            
            self.client.publish('sensor/data', json.dumps(data))
            time.sleep(10)
```

#### 边缘计算处理
```python
class EdgeProcessor:
    def __init__(self):
        self.threshold_temp = 30.0
        self.threshold_humidity = 80.0
    
    def process_data(self, data):
        # 本地数据处理和异常检测
        if data['temperature'] > self.threshold_temp:
            self.send_alert('High temperature detected')
        
        if data['humidity'] > self.threshold_humidity:
            self.send_alert('High humidity detected')
        
        # 数据预处理和压缩
        processed_data = self.compress_data(data)
        return processed_data
```

## 🚀 未来发展

### 技术升级
- **5G集成**: 集成5G通信技术
- **AI增强**: 集成更多AI算法
- **数字孪生**: 建立数字孪生系统
- **区块链**: 集成区块链技术保证数据安全

### 应用扩展
- **多场景适配**: 适配更多应用场景
- **标准化**: 建立行业标准和规范
- **产业化**: 推动技术产业化应用
- **国际化**: 参与国际标准制定

## 📞 联系我们

### 👨‍💻 项目团队
- **项目负责人**: DarrenPig
- **技术负责人**: 朱佩韦
- **系统架构师**: 和尚
- **文档维护**: 许子涵涵

### 🤝 合作伙伴
- **华为技术有限公司** - 提供AR502H-CN设备和技术支持
- **openEuler社区** - 提供操作系统和技术支持
- **上海交通大学** - 竞赛组织方

### 🌐 项目链接
- **代码仓库**: [Gitee仓库](https://gitee.com/darrenpig/new_energy_coder_club/tree/master/competitions/2024/iot-design-huawei)
- **项目展示**: [在线PPT](https://low-power-inspection-veh-95gmidb.gamma.site/)
- **技术文档**: [项目Wiki](./2024物联网设计竞赛_Huawei数通/Readme.md)
- **竞赛官网**: [物联网竞赛](https://iot.sjtu.edu.cn/show.aspx?info_lb=34&info_id=3962&flag=2)

---

*最后更新: 2025年1月*

> 💡 **技术交流**: 欢迎对物联网和边缘计算技术感兴趣的同学与我们交流！我们在openEuler、华为生态、边缘计算等方面有丰富的实践经验。