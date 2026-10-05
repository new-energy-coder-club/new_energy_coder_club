/*
 * @version: no version
 * @LastEditors: QMJ
 * @Description: 用于加速度控制的类定义
 * @author: QMJ
 * @LastEditTime: 2025-09-11 11:48:18
 */
#ifndef ACCELERATION_CONTROL_HPP
#define ACCELERATION_CONTROL_HPP

#include "VECTOR3.hpp"
#include <functional>

class AccelerationControl {
public:
    /**
     * @brief 构造函数，用于初始化加速度控制对象
     * 
     * 该构造函数接收一个三维向量作为参数，用于设置加速度控制对象的最大加速度。
     * 初始化列表将传入的加速度值赋给类的成员变量 acceleration。
     * 
     * @param _acceleration 一个 vec3<float> 类型的三维向量，表示最大加速度
     */
    AccelerationControl(vec3<float> _acceleration) : acceleration(_acceleration){}
    // 成员函数模板特化应该在类外部进行
    /**
     * @brief 根据最大加速度限制计算输出速度
     * 
     * 该函数接收一个期望速度向量，根据最大加速度限制计算并返回实际输出速度向量，
     * 确保速度变化不超过最大加速度限制。
     * 
     * @param speed_vector 期望的速度向量，类型为 vec3<float>
     * @return vec3<float> 经过加速度限制后的实际输出速度向量
     */
    vec3<float> get_speed(vec3<float> speed_vector){
        // 获取当前时间（单位：微秒）
        uint64_t now_time_us = get_now_time_us_func();
        // 计算时间差（单位：秒）
        float delta_time_s = 1e-6*(now_time_us - last_time_us);
        // 更新上一次记录的时间
        last_time_us = now_time_us;
        // 计算在当前时间间隔内允许的最大速度变化量
        vec3<float> max_delata_speed=acceleration*delta_time_s;
        // 计算期望速度与上一次速度的差值
        vec3<float> delta_speed = speed_vector - last_speed;
        // 初始化输出速度为期望速度
        vec3<float> out_speed = speed_vector;

        // 对 x 轴速度变化进行限制
        std::abs(delta_speed.x) > max_delata_speed.x ? 
            out_speed.x = speed_vector.x > 0 ? max_delata_speed.x : -max_delata_speed.x : 
            out_speed.x = speed_vector.x;
        // 对 y 轴速度变化进行限制
        std::abs(delta_speed.y) > max_delata_speed.y ? 
            out_speed.y = speed_vector.y > 0 ? max_delata_speed.y : -max_delata_speed.y : 
            out_speed.y = speed_vector.y;
        // 对 z 轴速度变化进行限制
        std::abs(delta_speed.z) > max_delata_speed.z ? 
            out_speed.z = speed_vector.z > 0 ? max_delata_speed.z : -max_delata_speed.z : 
            out_speed.z = speed_vector.z;

        // 更新上一次的速度记录
        last_speed = out_speed;
        // 返回经过加速度限制后的实际输出速度
        return out_speed;
    };

    /**
     * @brief 重载 << 运算符，用于方便地调用 get_speed 函数
     * 
     * 该运算符重载函数接收一个期望速度向量，调用 get_speed 函数计算并返回实际输出速度向量。
     * 
     * @param speed_vector 期望的速度向量，类型为 vec3<float>
     * @return vec3<float> 经过加速度限制后的实际输出速度向量
     */
    vec3<float> operator<<(vec3<float> speed_vector){
        return get_speed(speed_vector);
    };
    /**
     * @brief 设置获取当前时间的函数
     * 
     * 该函数接收一个函数指针或 lambda 表达式，用于设置获取当前时间的函数。
     * 函数指针或 lambda 表达式的类型为 std::function<uint64_t()>，表示返回 uint64_t 类型的函数。
     * 
     * @param func 一个 std::function<uint64_t()> 类型的函数指针或 lambda 表达式，用于获取当前时间
     */
    void set_get_now_time_us_func(std::function<uint64_t()> func) { 
        get_now_time_us_func = func; 
        last_time_us = get_now_time_us_func(); 
    }
protected:
    /**
     * @brief 获取当前时间的函数
     * 
     * 该函数返回当前时间，单位为微秒。
     * 函数指针或 lambda 表达式的类型为 std::function<uint64_t()>，表示返回 uint64_t 类型的函数。
     * @note 默认函数每次调用加 1e4 微秒
     * @return uint64_t 当前时间，单位为微秒
     */
    std::function<uint64_t()> get_now_time_us_func=[](){
        static uint64_t now_time_us = 0;
        now_time_us+=1e4;
        return now_time_us;
    };
    uint64_t last_time_us = 0;
    vec3<float> last_speed=vec3<float>(0,0,0);
    vec3<float> acceleration=vec3<float>(0,0,0);
    
};


#endif