# 通用舵轮底盘运动学控制模块

## 模块概述

本模块为通用舵轮底盘运动学逆解算库，提供从底盘整体运动指令到单个舵轮速度和转向角的转换功能。支持任意数量舵轮的配置，适用于各种全向移动机器人底盘的控制系统开发。

## 功能特性

- 🚗 **多舵轮支持**：模板化设计，支持2个及以上任意数量舵轮配置
- 🔄 **动态旋转中心**：可实时修改旋转中心位置
- ⚡ **高效解算**：基于向量运算的快速运动学解算
- 🛑 **零速处理**：提供零速状态下的特殊处理回调
- 📐 **坐标系灵活**：不限制坐标系原点位置

## 数学原理

基于刚体运动学原理，每个舵轮的速度由两部分组成：

$`
  \underbrace{\vec{v}}_{\text{舵轮速度}} = 
  \underbrace{\mathbf{\vec{v_{xy}}}}_{\text{平移速度}} + 
  \underbrace{\vec{v_{\omega}} }_{\text{旋转速度分量}}
`$

详细公式推导见
[舵轮解算公式推导](./舵轮解算公式推导.md)
其中：
- $\vec{v}$ 为底盘整体平移速度矢量
- $\vec{v_{xy}}$ 为底盘运动的平动速度分量
- $\vec{v_{\omega}}$ 为底盘运动旋转分量在舵轮上的速度分量

## 快速开始

### 1. 引入头文件

```cpp
#include "SteeringWheelChassis.hpp"
```

### 2. 创建底盘实例

```cpp
// 三舵轮底盘初始化
SteeringWheelChassis3 chassis(
    vec3<float>{0,0,0},   // 旋转中心坐标
    vec3<float>{1,0,0},   // 舵轮1位置
    vec3<float>{-0.5,0.866,0},  // 舵轮2位置
    vec3<float>{-0.5,-0.866,0}   // 舵轮3位置
);
```

### 3. 设置底盘速度

```cpp
// 设置速度：x方向1m/s，旋转0.5rad/s
auto wheelStates = chassis.set_speed(vec3<float>{1.0f, 0.0f, 0.5f});

// 或者使用操作符简写
auto wheelStates = chassis << vec3<float>{1.0f, 0.0f, 0.5f};
```

### 4. 获取舵轮状态

```cpp
// 获取1号舵轮位置
vec3<float> pos = chassis.get_wheel_position(1);

// 获取当前旋转中心
vec3<float> center = chassis.get_rotation_center();
```

## 高级功能

### 零速回调设置

```cpp
chassis.set_zero_point_callback(
    [](SteeringWheelChassis3* chassis) {
        // 在零速时保持舵轮最后角度，速度设为0
        auto last = chassis->get_last_wheel_states();
        for(auto& w : last) w.speed = 0;
        return last;
    }
);
```

### 动态修改旋转中心

```cpp
// 将旋转中心改为(0.5, 0, 0)
chassis.change_rotation_center(vec3<float>{0.5f, 0.0f, 0.0f});
```

## 坐标系约定

- **全局坐标系**：
![image](https://github.com/user-attachments/assets/c3c765dd-2147-4ae9-b4e9-778f5df667f8)

- $+x$:正右方
- $+y$:正前方
- $+z$:正上方，用作旋转轴时符合右手螺旋，正方向为逆时针
- **舵轮角度**：
  - 0弧度：指向X轴正方向
  - 范围：[-π, π]
![舵轮 drawio](https://github.com/user-attachments/assets/874986cf-0994-43d2-8457-1729ccaba8b0)


## 性能考虑

- 解算时间复杂度：O(N)，N为舵轮数量
- 无动态内存分配
- 适合实时控制系统

## 限制与注意事项

- 所有位置参数单位必须一致（建议使用米）
- 零速回调不应包含耗时操作
- 修改旋转中心会影响正在执行的运动

## 示例配置

### 四舵轮底盘
```cpp
#include "SteeringWheelChassis.hpp"
#include <iostream>

int main() {
    // 定义旋转中心（假设为底盘几何中心）
    vec3<float> rotation_center(0.0f, 0.0f, 0.0f);
    
    // 定义四个舵轮的位置（相对于旋转中心）
    // 假设底盘为矩形，长宽各1米，舵轮对称分布
    vec3<float> wheel1_pos(0.5f, 0.5f, 0.0f);   // 右前轮
    vec3<float> wheel2_pos(-0.5f, 0.5f, 0.0f);  // 左前轮
    vec3<float> wheel3_pos(-0.5f, -0.5f, 0.0f); // 左后轮
    vec3<float> wheel4_pos(0.5f, -0.5f, 0.0f);  // 右后轮

    // 创建四舵轮底盘对象
    SteeringWheelChassis<4> chassis(
        rotation_center,
        wheel1_pos,
        wheel2_pos,
        wheel3_pos,
        wheel4_pos
    );

    // 设置零点回调函数（可选）
    chassis.set_zero_point_callback([](SteeringWheelChassis<4>* ch) {
        std::array<WheelModule, 4> modules;
        // 将所有舵轮角度设为0度，速度为0
        for (auto& m : modules) {
            m.speed = 0;
            m.angle = 0;
        }
        return modules;
    });

    // 示例1：向前移动（x方向速度1m/s）
    vec3<float> move_forward(1.0f, 0.0f, 0.0f);
    auto result1 = chassis.set_speed(move_forward);
    std::cout << "Forward movement:" << std::endl;
    for (size_t i = 0; i < 4; ++i) {
        std::cout << "Wheel " << i+1 << ": Speed=" << result1[i].speed 
                  << ", Angle=" << result1[i].angle << " rad" << std::endl;
    }

    // 示例2：原地旋转（z轴角速度1rad/s）
    vec3<float> rotate_in_place(0.0f, 0.0f, 1.0f);
    auto result2 = chassis << rotate_in_place;  // 使用操作符重载
    std::cout << "\nRotation in place:" << std::endl;
    for (size_t i = 0; i < 4; ++i) {
        std::cout << "Wheel " << i+1 << ": Speed=" << result2[i].speed 
                  << ", Angle=" << result2[i].angle << " rad" << std::endl;
    }

    // 示例3：斜向移动加旋转
    vec3<float> complex_move(0.5f, 0.5f, 0.5f);
    auto result3 = chassis.set_speed(complex_move);
    std::cout << "\nComplex movement:" << std::endl;
    for (size_t i = 0; i < 4; ++i) {
        std::cout << "Wheel " << i+1 << ": Speed=" << result3[i].speed 
                  << ", Angle=" << result3[i].angle << " rad" << std::endl;
    }

    // 获取舵轮位置信息
    std::cout << "\nWheel positions:" << std::endl;
    for (size_t i = 1; i <= 4; ++i) {
        auto pos = chassis.get_wheel_position(i);
        std::cout << "Wheel " << i << " at (" 
                  << pos.x << ", " << pos.y << ", " << pos.z << ")" << std::endl;
    }

    return 0;
}
```

### 示例输出说明：
1. **向前移动**时，所有舵轮角度应为0（指向正前方），速度相同
2. **原地旋转**时，舵轮角度应指向切线方向，速度与旋转中心距离成正比
3. **复合运动**时，各舵轮会有不同的速度和角度组合

### 自定义配置提示：
1. 可以修改舵轮位置来适应不同底盘布局
2. 旋转中心可以设置为非几何中心以实现特殊运动模式
3. 零点回调函数可以根据实际需求自定义停止状态

## 依赖项
**不依赖任何特定硬件**
- C++11或更新标准
- `VECTOR3.hpp` 三维向量库，仓库同目录
- STL组件：`<array>`, `<functional>`

## 许可证

