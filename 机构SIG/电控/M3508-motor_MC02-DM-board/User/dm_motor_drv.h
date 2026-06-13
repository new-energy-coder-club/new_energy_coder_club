#ifndef __C620_MOTOR_DRV_H__
#define __C620_MOTOR_DRV_H__
#include "main.h"
#include "fdcan.h"
#include "bsp_fdcan.h"

/*=============================================================
 *  RoboMaster C620 + M3508 CAN Protocol
 *
 *  发送:
 *    帧ID 0x200 -> 控制 电机ID 1~4  (每个电机 16bit 电流值)
 *    帧ID 0x1FF -> 控制 电机ID 5~8
 *    电流范围: -16384 ~ +16384  对应 -20A ~ +20A
 *
 *  接收:
 *    帧ID 0x201~0x204 -> 电机ID 1~4 反馈
 *    帧ID 0x205~0x208 -> 电机ID 5~8 反馈
 *    data[0-1]: 机械角度  0~8191 (对应 0~360 度)
 *    data[2-3]: 转速 rpm  (int16_t)
 *    data[4-5]: 实际转矩电流 (int16_t), 范围 -16384~16384
 *    data[6]:   电机温度 (uint8_t, 单位 C)
 *=============================================================*/

/* 电机编号枚举 */
typedef enum
{
    Motor1 = 0,
    Motor2,
    Motor3,
    Motor4,
    MOTOR_NUM
} motor_num_e;

/* 电机反馈数据 */
typedef struct
{
    uint16_t angle;         // 机械角度 0~8191
    float    angle_deg;     // 角度(度) 0~360
    int16_t  speed_rpm;     // 转速 rpm
    int16_t  current;       // 实际转矩电流 -16384~16384
    uint8_t  temperature;   // 温度 C

    float    total_angle;   // 累计角度(度), 用于多圈计数
    int32_t  round_cnt;     // 圈数计数
    uint16_t last_angle;    // 上一次机械角度, 用于圈数计算
    uint8_t  first_flag;    // 首次接收标志
} motor_feedback_t;

/* 电机结构体 */
typedef struct
{
    uint8_t          id;        // 电机ID 1~4
    motor_feedback_t fdb;       // 反馈数据
    float            set_cur;   // 设定电流 (A), 范围 -20 ~ +20
} c620_motor_t;

/*--- 函数声明 ---*/

/**
 * @brief  发送电流给 ID 1~4 的四个电机 (帧ID = 0x200)
 * @param  hcan   FDCAN 句柄
 * @param  cur1~cur4  每个电机的目标电流(A), -20~+20
 */
void c620_set_current(hcan_t* hcan, float cur1, float cur2, float cur3, float cur4);

/**
 * @brief  解析 C620 反馈数据
 * @param  motor   电机结构体指针
 * @param  rx_data 接收到的 8 字节 CAN 数据
 */
void c620_feedback_decode(c620_motor_t *motor, uint8_t *rx_data);

/**
 * @brief  直接发送原始电流值给 Motor1 (用于诊断)
 * @param  hcan   FDCAN 句柄
 * @param  raw_cur  原始电流值 -16384~16384
 * @return 0=成功, 1=失败
 */
uint8_t c620_set_current_raw(hcan_t* hcan, int16_t raw_cur);

#endif /* __C620_MOTOR_DRV_H__ */
