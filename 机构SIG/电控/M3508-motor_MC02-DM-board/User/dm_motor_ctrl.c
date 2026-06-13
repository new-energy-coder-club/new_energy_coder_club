#include "dm_motor_ctrl.h"
#include "string.h"

c620_motor_t motor[MOTOR_NUM];
pid_para_t   speed_pid[MOTOR_NUM];

/* 目标速度 (rpm), 在 main 或其他地方设置 */
float target_speed[MOTOR_NUM] = {0};

/**
 * @brief  初始化电机结构体 + 速度环 PID
 */
void motor_init(void)
{
    memset(motor, 0, sizeof(motor));

    motor[Motor1].id = 1;
    motor[Motor2].id = 2;
    motor[Motor3].id = 3;
    motor[Motor4].id = 4;

    /* 初始化速度环 PID (4个电机共用一套参数, 可按需分别调整) */
    for (int i = 0; i < MOTOR_NUM; i++)
    {
        pid_para_init(&speed_pid[i]);
        /* ---- 速度环 PID 参数 (先给一组保守值, 后续可调) ---- */
        pid_reset(&speed_pid[i], 10.0f, 0.5f, 0.0f);
        /* 积分限幅, 输出限幅 (-20A ~ +20A 对应 C620 最大电流) */
        pid_limit_init(&speed_pid[i], 10000.0f, -10000.0f, 16000.0f, -16000.0f);
    }
}

/**
 * @brief  1ms 控制任务
 *         速度环: target_speed(rpm) -> PID -> 电流给定 -> CAN发送
 */
void motor_control_task(void)
{
    float cur[MOTOR_NUM];

    for (int i = 0; i < MOTOR_NUM; i++)
    {
        /* PID 输出单位是 电流原始值 (-16384~16384) */
        float pid_out = parallel_pid_ctrl(&speed_pid[i],
                                          target_speed[i],
                                          (float)motor[i].fdb.speed_rpm);
        /* 将 PID 输出 (原始值) 转换为安培 */
        cur[i] = pid_out / (16384.0f / 20.0f);
    }

    c620_set_current(&hfdcan1, cur[0], cur[1], cur[2], cur[3]);
}

/**
 * @brief  CAN1 接收回调 (覆盖 bsp_fdcan.c 中的 weak 定义)
 */
void fdcan1_rx_callback(void)
{
    uint16_t rec_id;
    uint8_t rx_data[8] = {0};
    fdcanx_receive(&hfdcan1, &rec_id, rx_data);

    /* C620 反馈帧 ID: 0x201~0x204 对应 Motor1~Motor4 */
    if (rec_id >= 0x201 && rec_id <= 0x204)
    {
        uint8_t idx = rec_id - 0x201;
        c620_feedback_decode(&motor[idx], rx_data);
    }
}
