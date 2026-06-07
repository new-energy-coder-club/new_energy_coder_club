# 📦 共享资源库

欢迎来到NEC新能源极客俱乐部的共享资源库！这里汇集了所有项目通用的资源文件、工具库和模型文件，实现资源的高效复用和统一管理。

## 📂 目录结构

```
shared_new/
├── assets/                # 多媒体资源文件
│   ├── images/           # 图片资源库
│   │   ├── Image/        # 核心品牌图片
│   │   ├── competition/  # 竞赛相关图片
│   │   ├── project/      # 项目展示图片
│   │   ├── team/         # 团队合照
│   │   └── technical/    # 技术文档图片
│   └── videos/           # 视频资源库
│       ├── tutorials/    # 教学视频
│       ├── demos/        # 项目演示
│       └── presentations/ # 汇报展示
├── models/               # 3D模型文件库
│   ├── mechanical/       # 机械零件模型
│   ├── electronics/      # 电子器件模型
│   └── assemblies/       # 装配体模型
├── libraries/            # 代码库
│   ├── algorithms/       # 通用算法库
│   ├── drivers/          # 硬件驱动库
│   ├── protocols/        # 通信协议库
│   └── utilities/        # 工具函数库
└── tools/                # 开发工具
    ├── scripts/          # 自动化脚本
    ├── configs/          # 配置文件模板
    └── generators/       # 代码生成器
```

## 🖼️ 多媒体资源 (Assets)

### 📸 图片资源库 (Images)

#### 🎨 核心品牌图片 (Image/)
- **Logo.png**: NEC俱乐部官方Logo
- **Roadmap.png**: 技术发展路线图
- **Banner.png**: 项目横幅图片
- **Icons/**: 各类图标资源

**使用示例**:
```markdown
![NEC Logo](../shared_new/assets/images/Image/Logo.png)
```

#### 🏆 竞赛相关图片 (competition/)
- 竞赛现场照片
- 获奖证书扫描件
- 作品展示图片
- 技术方案图解

#### 🔬 项目展示图片 (project/)
- 项目架构图
- 系统流程图
- 界面截图
- 效果对比图

#### 👥 团队合照 (team/)
- 团队成员合影
- 活动现场照片
- 工作场景记录
- 里程碑庆祝

#### 📚 技术文档图片 (technical/)
- 电路原理图
- 系统架构图
- 算法流程图
- 数据可视化图表

### 🎥 视频资源库 (Videos)

#### 📖 教学视频 (tutorials/)
- 技术入门教程
- 开发环境配置
- 工具使用指南
- 最佳实践分享

#### 🎬 项目演示 (demos/)
- 机器人动作演示
- 系统功能展示
- 算法效果对比
- 实时测试录像

#### 📊 汇报展示 (presentations/)
- 竞赛答辩视频
- 技术分享录像
- 项目进展汇报
- 成果展示视频

## 🎯 3D模型文件库 (Models)

### ⚙️ 机械零件模型 (mechanical/)
- **标准件库**: 螺栓、螺母、轴承等
- **传动件**: 齿轮、皮带轮、联轴器
- **结构件**: 支架、外壳、连接件
- **运动件**: 关节、滑块、导轨

**文件格式**: STEP, STL, OBJ
**软件兼容**: SolidWorks, Fusion 360, Blender

### 🔌 电子器件模型 (electronics/)
- **芯片封装**: MCU、传感器、功率器件
- **连接器**: 端子、插座、线缆
- **PCB模型**: 标准尺寸电路板
- **外壳**: 电子产品外壳设计

### 🔧 装配体模型 (assemblies/)
- **机器人整机**: 完整的机器人装配模型
- **子系统**: 驱动系统、控制系统装配
- **测试平台**: 实验台架、治具装配
- **产品原型**: 完整产品装配方案

## 💻 代码库 (Libraries)

### 🧮 通用算法库 (algorithms/)
```
algorithms/
├── control/              # 控制算法
│   ├── pid_controller.py # PID控制器
│   ├── kalman_filter.py  # 卡尔曼滤波
│   └── fuzzy_logic.py    # 模糊控制
├── vision/               # 视觉算法
│   ├── object_detection.py # 目标检测
│   ├── image_processing.py # 图像处理
│   └── feature_matching.py # 特征匹配
├── ml/                   # 机器学习
│   ├── neural_networks.py  # 神经网络
│   ├── clustering.py       # 聚类算法
│   └── optimization.py     # 优化算法
└── math/                 # 数学工具
    ├── matrix_operations.py # 矩阵运算
    ├── signal_processing.py # 信号处理
    └── statistics.py        # 统计分析
```

### 🔌 硬件驱动库 (drivers/)
```
drivers/
├── sensors/              # 传感器驱动
│   ├── imu_driver.py     # IMU传感器
│   ├── camera_driver.py  # 摄像头驱动
│   └── lidar_driver.py   # 激光雷达
├── actuators/            # 执行器驱动
│   ├── servo_driver.py   # 舵机驱动
│   ├── motor_driver.py   # 电机驱动
│   └── valve_driver.py   # 电磁阀驱动
├── communication/         # 通信驱动
│   ├── uart_driver.py    # 串口通信
│   ├── i2c_driver.py     # I2C通信
│   └── can_driver.py     # CAN总线
└── display/              # 显示驱动
    ├── lcd_driver.py     # LCD显示
    ├── oled_driver.py    # OLED显示
    └── led_driver.py     # LED控制
```

### 📡 通信协议库 (protocols/)
```
protocols/
├── modbus/               # Modbus协议
├── mqtt/                 # MQTT协议
├── http_api/             # HTTP API
├── websocket/            # WebSocket
├── nearlink/             # 星闪协议
└── custom/               # 自定义协议
```

### 🛠️ 工具函数库 (utilities/)
```
utilities/
├── data_processing/      # 数据处理
├── file_operations/      # 文件操作
├── logging/              # 日志系统
├── configuration/        # 配置管理
├── testing/              # 测试工具
└── debugging/            # 调试工具
```

## 🔧 开发工具 (Tools)

### 📜 自动化脚本 (scripts/)
- **build_scripts/**: 编译构建脚本
- **deploy_scripts/**: 部署自动化脚本
- **test_scripts/**: 自动化测试脚本
- **maintenance_scripts/**: 维护工具脚本

### ⚙️ 配置文件模板 (configs/)
- **project_templates/**: 项目配置模板
- **environment_configs/**: 环境配置文件
- **ci_cd_configs/**: CI/CD配置模板
- **docker_configs/**: Docker配置文件

### 🏭 代码生成器 (generators/)
- **project_generator/**: 项目脚手架生成器
- **api_generator/**: API代码生成器
- **doc_generator/**: 文档生成器
- **test_generator/**: 测试代码生成器

## 📊 资源统计

| 资源类型 | 文件数量 | 总大小 | 最近更新 |
|----------|----------|--------|----------|
| 🖼️ 图片资源 | 67个 | 54.39 MB | 2025-01 |
| 🎥 视频资源 | 0个 | 0 MB | - |
| 🎯 3D模型 | 9个 | 48.37 MB | 2024-12 |
| 💻 代码库 | 0个 | 0 MB | - |
| 🔧 工具 | 0个 | 0 MB | - |

## 🎯 使用指南

### 📸 图片资源使用
```markdown
<!-- 在README中引用图片 -->
![项目Logo](../shared_new/assets/images/Image/Logo.png)

<!-- 在文档中引用技术图片 -->
![系统架构](../shared_new/assets/images/technical/architecture.png)
```

### 🎯 3D模型使用
```python
# 在Python中加载STEP文件
import FreeCAD
doc = FreeCAD.newDocument()
part = doc.addObject("Part::Feature", "MyPart")
part.Shape = Part.Shape()
part.Shape.read("../shared_new/models/mechanical/bearing.step")
```

### 💻 代码库使用
```python
# 导入通用算法库
from shared_new.libraries.algorithms.control import PIDController
from shared_new.libraries.drivers.sensors import IMUDriver

# 使用PID控制器
pid = PIDController(kp=1.0, ki=0.1, kd=0.01)
output = pid.update(setpoint=100, current_value=95)
```

## 🔄 资源管理

### 📥 添加新资源
1. **确定资源类型和存放位置**
2. **遵循命名规范**
3. **添加资源描述文档**
4. **更新相关索引文件**
5. **提交PR并等待审核**

### 🔄 更新现有资源
1. **保持向后兼容性**
2. **更新版本号**
3. **记录变更日志**
4. **通知相关项目负责人**

### 🗑️ 删除过时资源
1. **检查依赖关系**
2. **通知所有使用者**
3. **提供替代方案**
4. **设置废弃期限**
5. **清理相关引用**

## 📋 命名规范

### 📁 目录命名
- 使用小写字母和连字符
- 语义化命名，便于理解
- 避免使用特殊字符

### 📄 文件命名
- **图片**: `项目名_功能_版本.扩展名`
- **模型**: `零件名_规格_版本.step`
- **代码**: `模块名_功能.py`
- **文档**: `主题_类型_版本.md`

### 🏷️ 版本管理
- 使用语义化版本号 (v1.0.0)
- 重大更新递增主版本号
- 功能更新递增次版本号
- 问题修复递增修订号

## 🤝 贡献指南

### 🎯 资源贡献流程
1. **Fork项目仓库**
2. **创建资源分支**
3. **添加或修改资源**
4. **编写说明文档**
5. **提交Pull Request**
6. **等待代码审核**
7. **合并到主分支**

### ✅ 质量标准
- **图片**: 清晰度高，格式统一
- **模型**: 精度合适，文件完整
- **代码**: 注释完整，测试通过
- **文档**: 内容准确，格式规范

## 🔗 相关链接

- [📁 竞赛项目](../competitions_new/README.md)
- [🔬 技术项目](../projects_new/README.md)
- [📚 文档库](../docs_new/README.md)
- [🛠️ 开发工具](../scripts/README.md)

---

> 💡 **理念**: 通过资源共享，避免重复造轮子，提升整体开发效率！

**维护团队**: 资源管理小组 | **联系方式**: [GitHub Issues](https://github.com/Darrenpig/new_energy_coder_club/issues)