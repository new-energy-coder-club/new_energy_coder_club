#include <Arduino.h>
#include "driver/twai.h"

// ==================== 配置 ====================
#define CAN_TX_PIN GPIO_NUM_8
#define CAN_RX_PIN GPIO_NUM_18
#define VESC_ID    1

// VESC CAN 命令 ID
#define CAN_PACKET_SET_RPM    3
#define CAN_PACKET_STATUS     9

// ==================== VESC CAN 发送 ====================
void vesc_send_can(uint8_t command_id, uint8_t vesc_id, uint8_t *data, uint8_t len) {
    twai_message_t msg;
    msg.identifier = (command_id << 8) | vesc_id;
    msg.extd = 1;           // 29位扩展帧
    msg.rtr = 0;
    msg.data_length_code = len;
    memcpy(msg.data, data, len);
    twai_transmit(&msg, pdMS_TO_TICKS(10));
}

void vesc_set_rpm(int32_t rpm) {
    uint8_t data[4];
    data[0] = (rpm >> 24) & 0xFF;
    data[1] = (rpm >> 16) & 0xFF;
    data[2] = (rpm >> 8) & 0xFF;
    data[3] = rpm & 0xFF;
    vesc_send_can(CAN_PACKET_SET_RPM, VESC_ID, data, 4);
}

// ==================== VESC 状态接收 ====================
static unsigned long last_print = 0;

void vesc_parse_status(twai_message_t *msg) {
    if (msg->data_length_code < 8) return;
    if (millis() - last_print < 1000) return; // 1秒打印一次
    last_print = millis();

    int32_t erpm = (msg->data[0] << 24) | (msg->data[1] << 16) |
                   (msg->data[2] << 8) | msg->data[3];
    float current = (int16_t)((msg->data[4] << 8) | msg->data[5]) / 10.0f;
    float duty = (int16_t)((msg->data[6] << 8) | msg->data[7]) / 1000.0f;

    Serial0.printf("ERPM: %ld  电流: %.1fA  占空比: %.1f%%\n", erpm, current, duty * 100);
}

// ==================== 初始化 ====================
void setup() {
    // 使用 UART0 (GPIO43/44)，与无线烧录器通信
    Serial0.begin(115200, SERIAL_8N1, 44, 43); // RX=44, TX=43
    delay(500);

    // TWAI (CAN) 配置：500Kbps
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, TWAI_MODE_NORMAL);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
        Serial0.println("TWAI 驱动安装成功");
    } else {
        Serial0.println("TWAI 驱动安装失败");
        return;
    }

    if (twai_start() == ESP_OK) {
        Serial0.println("TWAI 启动成功");
    } else {
        Serial0.println("TWAI 启动失败");
        return;
    }

    Serial0.println("输入 RPM 值控制电机（如 3000），输入 0 停止");
}

// ==================== 主循环 ====================
static String input_buf;
static unsigned long last_send = 0;
static int32_t target_rpm = 0; 

void loop() {
    // 串口读取 RPM 指令
    while (Serial0.available()) {
        char c = Serial0.read();
        if (c == '\n' || c == '\r') {
            if (input_buf.length() > 0) {
                target_rpm = input_buf.toInt();
                Serial0.printf("设置目标 RPM: %ld\n", target_rpm);
                input_buf = "";
            }
        } else {
            input_buf += c;
        }
    }

    // 50Hz 持续发送 RPM 命令（VESC 要求持续发送，否则超时停转）
    if (millis() - last_send >= 20) {
        last_send = millis();
        vesc_set_rpm(target_rpm);
    }

    // 接收 VESC 状态消息
    twai_message_t rx_msg;
    if (twai_receive(&rx_msg, 0) == ESP_OK) {
        uint8_t cmd_id = (rx_msg.identifier >> 8) & 0xFF;
        if (cmd_id == CAN_PACKET_STATUS) {
            vesc_parse_status(&rx_msg);
        }
    }
}
