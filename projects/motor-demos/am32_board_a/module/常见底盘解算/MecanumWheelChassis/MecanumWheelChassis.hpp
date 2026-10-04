#ifndef MECANUM_WHEEL_CHASSIS_HPP
#define MECANUM_WHEEL_CHASSIS_HPP
#include "VECTOR3.hpp"
#include <array>
class MecanumWheelChassis {
public:
    /**
     * @brief : 构造函数，用于初始化机械轮底盘对象
     * @return  {*}
     * @Author : QMJ
     * @param {float} wheel_radius 轮子半径 单位：米
     * @param {float} wheel_base_length 轮子轴距 单位：米
     * @param {float} wheel_base_width 轮子宽度 单位：米
     */
    MecanumWheelChassis(float wheel_radius, float wheel_base_length, float wheel_base_width)
        : r(wheel_radius), L(wheel_base_length), W(wheel_base_width) {}

    /**
     * @brief : 计算机械轮底盘的轮子速度
     * @param  {const vec3<float>&} chassis_speeds 底盘 速度向量，包含线速度 Vx、Vy 和角速度 Omega 单位：m/s rad/s
     * @return  {std::array<float, 4>} 轮子速度数组，顺序为前左、前右、后左、后右 单位：rad/s
     * @Author : QMJ
     */
    std::array<float, 4> calculate_wheel_speeds(const vec3<float>& chassis_speeds) {
        float Vx = chassis_speeds.x;
        float Vy = chassis_speeds.y;
        float Omega = chassis_speeds.z;
        std::array<float, 4> wheel_speeds;
        wheel_speeds[0] = (1/r) * (Vx - Vy - (L + W) * Omega); //左前
        wheel_speeds[1] = (1/r) * (Vx + Vy + (L + W) * Omega); //右前
        wheel_speeds[2] = (1/r) * (Vx - Vy + (L + W) * Omega); //左后
        wheel_speeds[3] = (1/r) * (Vx + Vy - (L + W) * Omega); //右后
        return wheel_speeds;    
    }
protected:
    float r; // 轮子半径 单位：米
    float L; // 轮子轴距 单位：米
    float W; // 轮子宽度 单位：米
};
#endif