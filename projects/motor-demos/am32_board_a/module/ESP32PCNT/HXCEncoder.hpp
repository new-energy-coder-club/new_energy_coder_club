/*
 * @LastEditors: qingmeijiupiao
 * @Description: 使用PCNT外设实现的编码器库
 * @Author: qingmeijiupiao
 * @LastEditTime: 2025-01-30 02:11:07
 */
#ifndef HXCPCNTENCODER_HPP
#define HXCPCNTENCODER_HPP
#include <Arduino.h>
#include "driver/pcnt.h"
namespace HXC{

/**
 * @brief : 使用ESP32的PCNT外设实现的编码器计数器,4倍采样
 * @note  : 相比中断计数cpu资源占用低,由于PCNT最大计数限制32767,内部使用一个任务来轮询PCNT,因此可以实现更高的计数
 * @return  {*}
 * @Author : qingmeijiupiao
 */
class Encoder{
    public:
        /**
         * @brief 构造函数
         * @param _PINA  编码器A相的脉冲信号GPIO
         * @param _PINB  编码器B相的脉冲信号GPIO
         */
        Encoder(uint8_t _PINA,uint8_t _PINB):PINA(_PINA),PINB(_PINB){
            unit=used_unit++;//自动分配PCNT单元
        };
        //禁止复制
        Encoder(Encoder&)=delete;
        //禁止赋值传递
        Encoder& operator=(Encoder&)=delete;
        ~Encoder(){
            vTaskDelete(counter_loop_handle);
        }
        /**
         * @brief 初始化
         * @param frc  多圈计数器和速度检测的频率
         */
        void setup(int frc=1000){
            LOOPFREQ=frc;
            this->pcnt_config= pcnt_config_t{
                        .pulse_gpio_num = static_cast<gpio_num_t>(PINA),  // 编码器A相连接的GPIO
                        .ctrl_gpio_num = static_cast<gpio_num_t>(PINB),   // 编码器B相连接的GPIO
                        .lctrl_mode = PCNT_MODE_REVERSE, // 控制信号低电平时反转计数方向
                        .hctrl_mode = PCNT_MODE_KEEP,    // 控制信号高电平时保持计数模式不变
                        .pos_mode = PCNT_COUNT_DEC,      // 正边沿计数增加
                        .neg_mode = PCNT_COUNT_INC,      // 负边沿计数保持不变
                        .counter_h_lim = 32767,          // 最大计数限制
                        .counter_l_lim = 0,              // 最小计数限制
                        .unit = static_cast<pcnt_unit_t>(unit),             // PCNT单元编号
                        .channel =static_cast<pcnt_channel_t>(unit),       // PCNT通道编号
            };
            
            pcnt_unit_config(&pcnt_config);
            // 重新配置结构体，用于第二个通道
            pcnt_config.pulse_gpio_num = static_cast<gpio_num_t>(PINB);  // 现在脉冲输入是编码器B相
            pcnt_config.ctrl_gpio_num = static_cast<gpio_num_t>(PINA);   // 控制输入是编码器A相
            pcnt_config.pos_mode = PCNT_COUNT_INC;
            pcnt_config.neg_mode = PCNT_COUNT_DEC;
            pcnt_config.channel = PCNT_CHANNEL_1; // 使用通道1
            pcnt_unit_config(&pcnt_config);
            pcnt_counter_clear(pcnt_config.unit);
            if(counter_loop_handle==nullptr){
                xTaskCreate(counter_loop, "counter_loop", 1024, this, 5, &counter_loop_handle);               
            }

        };

        /**
         * @brief 设置脉冲去抖动滤波器的时间常数
         * @param ns  宽度小于该值的脉冲将被忽略，单位为纳秒
         */
        void set_filter(uint16_t ns){
            pcnt_filter_enable(static_cast<pcnt_unit_t>(unit));
            pcnt_set_filter_value(static_cast<pcnt_unit_t>(unit),ns);
        }


        /**
         * @brief 获取计数器的当前计数
         * @return 计数器的当前计数
         */
        int64_t get_count(){
            return count;
        };


        /**
         * @brief   获取当前的脉冲速度，单位 Hz
         * @return  当前的脉冲速度，单位 Hz
         */
        float get_speed(){
            return speed;
        };

        /**
         * @brief 将计数器重置为指定的值。
         * 
         * @param _count 要重置的值，缺省为0。
         */
        void reset_count(int64_t _count=0){
            count=_count;
        };
    protected:
        /**
         * @brief 直接从PCNT单元获取当前计数，未经任何处理。
         * @return 当前计数，作为一个有符号的16位整数。
         * @note 该函数被循环检测线程用于获取当前计数。
         */

        int16_t get_count_row(){
            int16_t count;
            pcnt_get_counter_value(static_cast<pcnt_unit_t>(unit),&count);
            return count;
        }

        //循环计数线程
        static void counter_loop(void* param){
            HXC::Encoder *instance=static_cast<HXC::Encoder*>(param);
            instance->last_time=micros();
            auto time=xTaskGetTickCount();
            while(1){
                int now_count=instance->get_count_row();
                int now_time=micros();
                //计算增量
                int delta=now_count-instance->last_count_row;
                //超过PCNT最大计数限制,计算正反转
                if(abs(delta)>32767/2){
                    if(delta>0){
                        delta-=32767;
                    }else{
                        delta+=32767;
                    }
                }
                //累加
                instance->count+=delta;
                //速度
                instance->speed=float(delta)/((now_time-instance->last_time)/1000000.f);
                //更新
                instance->last_count_row=now_count;
                instance->last_time=now_time;
                //延时
                vTaskDelayUntil(&time,1000/instance->LOOPFREQ);//延时控制频率
            }
        };
        uint8_t PINA,PINB;//AB相引脚
        int64_t count=0;//脉冲计数，默认4倍计数
        uint8_t unit;//PCNT单元好号
        static uint8_t used_unit;//已经使用的单元
        pcnt_config_t pcnt_config;
        int last_count_row=0;
        int LOOPFREQ=1000;//循环检测任务频率
        int64_t last_time=0;//上一次检测的时间
        float speed=0;//脉冲频率，单位Hz
        TaskHandle_t counter_loop_handle=nullptr;//循环检测任务句柄


};
uint8_t Encoder::used_unit=0;//已经使用的单元
}
#endif
