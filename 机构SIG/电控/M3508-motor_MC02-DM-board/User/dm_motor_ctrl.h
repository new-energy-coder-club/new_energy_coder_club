#ifndef __DM_MOTOR_CTRL_H__
#define __DM_MOTOR_CTRL_H__
#include "main.h"
#include "dm_motor_drv.h"
#include "pid.h"

/* 4 个电机实例 */
extern c620_motor_t motor[MOTOR_NUM];

/* 速度环 PID */
extern pid_para_t speed_pid[MOTOR_NUM];

/**
 * @brief  初始化电机结构体和 PID
 */
void motor_init(void);

/**
 * @brief  1ms 定时器控制任务 (在 TIM3 中断中调用)
 *         速度环 PID -> 输出电流 -> 发送 CAN
 */
void motor_control_task(void);

#endif /* __DM_MOTOR_CTRL_H__ */
