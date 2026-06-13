#include "dm_motor_drv.h"

/**
 * @brief  发送电流给 ID 1~4 的四个电机
 *         帧ID = 0x200, 8字节, 每个电机占 2 字节 (高字节在前)
 *         电流映射: -20A ~ +20A  ->  -16384 ~ +16384
 */
void c620_set_current(hcan_t* hcan, float cur1, float cur2, float cur3, float cur4)
{
    uint8_t data[8];

    int16_t c1 = (int16_t)(cur1 * (16384.0f / 20.0f));
    int16_t c2 = (int16_t)(cur2 * (16384.0f / 20.0f));
    int16_t c3 = (int16_t)(cur3 * (16384.0f / 20.0f));
    int16_t c4 = (int16_t)(cur4 * (16384.0f / 20.0f));

    data[0] = (uint8_t)(c1 >> 8);
    data[1] = (uint8_t)(c1);
    data[2] = (uint8_t)(c2 >> 8);
    data[3] = (uint8_t)(c2);
    data[4] = (uint8_t)(c3 >> 8);
    data[5] = (uint8_t)(c3);
    data[6] = (uint8_t)(c4 >> 8);
    data[7] = (uint8_t)(c4);

    fdcanx_send_data(hcan, 0x200, data, 8);
}

/**
 * @brief  解析 C620 电调反馈帧 (8字节)
 *         data[0-1]: 机械角度 0~8191
 *         data[2-3]: 转速 rpm (int16_t)
 *         data[4-5]: 实际转矩电流 (int16_t)
 *         data[6]:   温度 (uint8_t)
 */
void c620_feedback_decode(c620_motor_t *motor, uint8_t *rx_data)
{
    motor->fdb.angle       = (uint16_t)((rx_data[0] << 8) | rx_data[1]);
    motor->fdb.speed_rpm   = (int16_t)((rx_data[2] << 8) | rx_data[3]);
    motor->fdb.current     = (int16_t)((rx_data[4] << 8) | rx_data[5]);
    motor->fdb.temperature = rx_data[6];

    motor->fdb.angle_deg = (float)motor->fdb.angle / 8192.0f * 360.0f;

    /* ---------- 多圈角度累计 ---------- */
    if (!motor->fdb.first_flag)
    {
        motor->fdb.first_flag = 1;
        motor->fdb.last_angle = motor->fdb.angle;
        motor->fdb.round_cnt  = 0;
        motor->fdb.total_angle = motor->fdb.angle_deg;
        return;
    }

    int16_t delta = (int16_t)motor->fdb.angle - (int16_t)motor->fdb.last_angle;

    /* 过零检测: 8192 的一半 = 4096 */
    if (delta > 4096)
        motor->fdb.round_cnt--;
    else if (delta < -4096)
        motor->fdb.round_cnt++;

    motor->fdb.last_angle  = motor->fdb.angle;
    motor->fdb.total_angle = motor->fdb.round_cnt * 360.0f + motor->fdb.angle_deg;
}

/**
 * @brief  直接发送原始电流值, 只给 Motor1, 其余为0
 */
uint8_t c620_set_current_raw(hcan_t* hcan, int16_t raw_cur)
{
    uint8_t data[8] = {0};

    data[0] = (uint8_t)(raw_cur >> 8);
    data[1] = (uint8_t)(raw_cur & 0xFF);
    /* data[2]~data[7] = 0 (Motor2~4 电流为0) */

    return fdcanx_send_data(hcan, 0x200, data, 8);
}
