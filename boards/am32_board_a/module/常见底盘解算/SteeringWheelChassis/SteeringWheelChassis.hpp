/*
 * @version: no version
 * @LastEditors: qingmeijiupiao
 * @Description: 通用舵轮运动学逆解算封装库声明（支持2轮及以上）
 * @author: qingmeijiupiao
 * @LastEditTime: 2025-07-26 00:16:04
 */
#ifndef STEERING_WHEEL_CHASSIS_HPP
#define STEERING_WHEEL_CHASSIS_HPP

#include "VECTOR3.hpp"
#include <functional>
#include <array>
#include <utility>

// 单个舵轮运动学参数
struct WheelModule {
    float speed; // 舵轮转速 单位：m/s
    float angle; // 舵轮转角 单位：弧度 朝向X轴(底盘右侧)为0
};
/**
 * @class SteeringWheelChassis
 * @tparam N 舵轮数量，必须≥2
 * @brief 通用舵轮底盘运动学控制器
 * @note 坐标系约定:
 *       车正前方是Y正，右侧是X正，正上方是Z正
 *          Z
 *          |
 *          |    Y
 *          |   /
 *    ______|  /
 *   /     /| /
 *  /_____/ |/
 *  |     | O--------> X
 *  |_____|/
 */
template <size_t N>
class SteeringWheelChassis {
public:
    /**
     * @brief 构造函数（可变参数模板版本）
     * 
     * @param rotation_center 底盘旋转中心坐标，单位：米(m)
     * @param [std::array<vec3<float>, N>] args N个vec3<float>类型的舵轮位置参数，单位：米(m)
     */

    SteeringWheelChassis(vec2<float> _rotation_center, const std::array<vec2<float>, N>& _wheel_positions):
        rotation_center_vector(_rotation_center), wheel_positions(_wheel_positions) {
        for (auto& w : wheel_module_speed_angle) {
            w.speed = 0;
            w.angle = 0;
        }
    };

    /**
     * @brief 设置零点速度回调函数
     * 
     * @param callback 回调函数，当输入速度为0时调用
     * 
     * @details 当底盘速度矢量为0时，系统将：
     * 1. 如果有设置回调，调用回调函数获取舵轮状态
     * 2. 否则保持各舵轮角度不变，速度设为0
     * 
     * 回调函数应返回包含N个WheelModule的数组，指定各舵轮在零速时的状态。
     * 典型应用场景：
     * - 保持舵轮最后有效角度
     * - 执行特殊归位动作
     */
    void set_zero_point_callback(
        std::function<std::array<WheelModule, N>(SteeringWheelChassis<N>*)> callback
    ){
        zero_point_callback = callback;
    };
    
    /**
     * @brief 设置底盘运动速度
     * 
     * @param speed_vector 速度矢量(x,y,ω)：
     *   - x: 横向速度(m/s)
     *   - y: 前进速度(m/s)
     *   - z: 旋转角速度(rad/s)
     * @return std::array<WheelModule, N> 各舵轮的状态
     * 
     * @note 坐标系约定：
     * - x轴正向为底盘右侧
     * - y轴正向为底盘前方
     * - ω逆时针方向为正
     */
    std::array<WheelModule, N> set_speed(vec3<float> speed_vector) {
    /* 
    * 数学原理：
    * 各舵轮速度 = 平移速度分量 + 旋转速度分量
    * 旋转分量由 (ω × r) 计算得出，其中：
    *   ω - 底盘旋转角速度矢量
    *   r - 舵轮到旋转中心的矢量
    */
        //处理速度为零的情况
        if (speed_vector.is_zero()) {
            if (zero_point_callback) {//调用回调函数
                return zero_point_callback(this);
            } else {//保持舵轮状态不变
                auto last = wheel_module_speed_angle;
                for (auto& w : last) w.speed = 0;
                return last;
            }
        }

        // 计算各舵轮速度和角度
        for (size_t i = 0; i < N; ++i) {
            // 计算舵轮相对于旋转中心的向量
            vec3<float> wheel_vec = wheel_positions[i] - rotation_center_vector;
            // 计算舵轮垂直旋转轴的单位向量
            vec3<float> wheel_rot = wheel_vec.cross(vec3<float>(0, 0, 1)).normalized();
            // 计算旋转速度分量
            wheel_rot = wheel_rot * (speed_vector.z * wheel_vec.length());
            // 计算平移速度分量
            vec3<float> speed(speed_vector.x, speed_vector.y, 0);
            // 合速度 = 平移速度 + 旋转速度
            vec3<float> total_speed = speed + wheel_rot;
            wheel_module_speed_angle[i] = {
                total_speed.length(),// 舵轮速度
                atan2(total_speed.y, total_speed.x)//舵轮角度
            };
        }

        return wheel_module_speed_angle;
    };
    
    /**
     * @brief 速度设置操作符重载
     * @see set_speed()
     */
    std::array<WheelModule, N> operator<<(vec3<float> speed_vector){
        return set_speed(speed_vector);
    };
    /**
     * @brief 获取指定舵轮的位置坐标
     * 
     * @param wheel_number 舵轮编号(1~N)
     * @return vec3<float> 舵轮位置坐标
     * @throws 无异常，但输入无效编号时返回(0,0,0)
     */
    vec2<float> get_wheel_position(size_t wheel_number) const{
        if (wheel_number > 0 && wheel_number <= N) {
            return wheel_positions[wheel_number - 1];
        }
        return vec2<float>(0, 0);
    };
    
    /**
     * @brief 获取当前旋转中心坐标
     */
    vec2<float> get_rotation_center() const{
        return rotation_center_vector;
    };
    
    /**
     * @brief 修改旋转中心坐标
     * 
     * @param rotation_center 新的旋转中心坐标
     * 
     * @note 修改后立即生效，会影响后续所有速度计算
     */
    void change_rotation_center(vec2<float> rotation_center){
        rotation_center_vector = rotation_center;
    };

protected:
    std::array<vec2<float>, N> wheel_positions; ///< 各舵轮位置坐标数组
    vec2<float> rotation_center_vector;         ///< 当前旋转中心坐标
    
    /// 零点速度回调函数（默认为nullptr）
    std::function<std::array<WheelModule, N>(SteeringWheelChassis<N>*)> zero_point_callback = nullptr;
    
    /// 各舵轮当前状态（速度+角度）
    std::array<WheelModule, N> wheel_module_speed_angle;
};

// 3轮舵轮底盘
class SteeringWheelChassis3 : public SteeringWheelChassis<3> {
public:
    SteeringWheelChassis3(vec2<float> rotation_center, 
                         vec2<float> wheel1, 
                         vec2<float> wheel2, 
                         vec2<float> wheel3):SteeringWheelChassis<3>(rotation_center,{wheel1,wheel2,wheel3}){};
};

// 4轮舵轮底盘
class SteeringWheelChassis4 : public SteeringWheelChassis<4> {
public:
    SteeringWheelChassis4(vec2<float> rotation_center, 
                         vec2<float> wheel1, 
                         vec2<float> wheel2, 
                         vec2<float> wheel3,
                         vec2<float> wheel4):SteeringWheelChassis<4>(rotation_center,{wheel1,wheel2,wheel3,wheel4}){};
};

#endif // STEERING_WHEEL_CHASSIS_HPP