#include <Arduino.h>
#include "driver/twai.h"
#include <ctype.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

// ==================== 配置 ====================
#define LOG_PORT Serial

static constexpr gpio_num_t CAN_TX_PIN = GPIO_NUM_8;
static constexpr gpio_num_t CAN_RX_PIN = GPIO_NUM_18;
static constexpr uint8_t VESC_ID = 1;
static constexpr float CURRENT_LIMIT_A = 5.0f;
static constexpr uint32_t CURRENT_SEND_PERIOD_MS = 5;     // 200Hz
static constexpr uint32_t STATUS_PRINT_PERIOD_MS = 500;
static constexpr uint32_t STATUS_TIMEOUT_MS = 1000;
static constexpr float POSITION_WRAP_DEG = 360.0f;
static constexpr float POSITION_KP_A_PER_DEG = 0.015f;
static constexpr float POSITION_KI_A_PER_DEG_S = 0.0015f;
static constexpr float POSITION_KD_A_PER_DEG_S = 0.005f;
static constexpr float POSITION_DEADBAND_DEG = 0.5f;
static constexpr float POSITION_SETTLE_VEL_DEG_S = 8.0f;
static constexpr float POSITION_CURRENT_LIMIT_A = 4.0f;
static constexpr float POSITION_I_LIMIT_A = 0.8f;
static constexpr float POSITION_STATIC_CURRENT_A = 0.65f;
static constexpr float POSITION_STATIC_ENABLE_DEG = 1.0f;
static constexpr float TRAJ_MAX_VEL_DEG_S = 300.0f;
static constexpr float TRAJ_MAX_ACCEL_DEG_S2 = 900.0f;
static constexpr float TRAJ_VEL_GAIN = 5.0f;

// VESC CAN 命令 ID
enum VescCanPacket : uint8_t {
    CAN_PACKET_SET_CURRENT = 1,
    CAN_PACKET_STATUS = 9,
    CAN_PACKET_STATUS_4 = 16,
    CAN_PACKET_STATUS_5 = 27,
};

enum ControlMode : uint8_t {
    MODE_IDLE,
    MODE_CURRENT,
    MODE_POSITION,
};

struct VescFeedback {
    bool has_status_1 = false;
    bool has_status_4 = false;
    bool has_status_5 = false;
    uint32_t last_rx_ms = 0;
    uint32_t last_status_4_ms = 0;

    int32_t erpm = 0;
    float motor_current_a = 0.0f;
    float duty = 0.0f;

    float temp_fet_c = 0.0f;
    float temp_motor_c = 0.0f;
    float input_current_a = 0.0f;
    float pid_pos_deg = 0.0f;

    int32_t tachometer = 0;
    float input_voltage_v = 0.0f;
};

struct PositionTracker {
    bool initialized = false;
    bool has_velocity = false;
    float last_deg = 0.0f;
    int32_t turns = 0;
    float multi_deg = 0.0f;
    float velocity_deg_s = 0.0f;
    uint32_t last_update_ms = 0;
};

struct PositionController {
    bool initialized = false;
    float command_target_deg = 0.0f;
    float ref_pos_deg = 0.0f;
    float ref_vel_deg_s = 0.0f;
    float integral_a = 0.0f;
    uint32_t last_update_ms = 0;
};

static VescFeedback vesc;
static PositionTracker position_tracker;
static PositionController position_controller;
static ControlMode control_mode = MODE_IDLE;
static String input_buf;
static float target_current_a = 0.0f;
static float output_current_a = 0.0f;
static float position_error_deg = 0.0f;
static uint32_t last_current_send_ms = 0;
static uint32_t last_status_print_ms = 0;
static uint32_t last_timeout_print_ms = 0;
static uint32_t can_tx_ok = 0;
static uint32_t can_tx_fail = 0;
static uint32_t can_rx_total = 0;

// ==================== 工具函数 ====================
static float clamp_float(float value, float min_value, float max_value) {
    if (value < min_value) return min_value;
    if (value > max_value) return max_value;
    return value;
}

static int16_t read_i16_be(const uint8_t *data, uint8_t offset) {
    uint16_t raw = ((uint16_t)data[offset] << 8) | data[offset + 1];
    return (int16_t)raw;
}

static int32_t read_i32_be(const uint8_t *data, uint8_t offset) {
    uint32_t raw = ((uint32_t)data[offset] << 24) |
                   ((uint32_t)data[offset + 1] << 16) |
                   ((uint32_t)data[offset + 2] << 8) |
                   data[offset + 3];
    return (int32_t)raw;
}

static void write_i32_be(uint8_t *data, int32_t value) {
    data[0] = (value >> 24) & 0xFF;
    data[1] = (value >> 16) & 0xFF;
    data[2] = (value >> 8) & 0xFF;
    data[3] = value & 0xFF;
}

static void update_position_tracker(float pos_deg) {
    uint32_t now = millis();

    if (!position_tracker.initialized) {
        position_tracker.initialized = true;
        position_tracker.last_deg = pos_deg;
        position_tracker.multi_deg = pos_deg;
        position_tracker.last_update_ms = now;
        return;
    }

    float delta = pos_deg - position_tracker.last_deg;
    if (delta > POSITION_WRAP_DEG * 0.5f) {
        position_tracker.turns--;
    } else if (delta < -POSITION_WRAP_DEG * 0.5f) {
        position_tracker.turns++;
    }

    position_tracker.last_deg = pos_deg;
    float new_multi_deg = position_tracker.turns * POSITION_WRAP_DEG + pos_deg;

    uint32_t dt_ms = now - position_tracker.last_update_ms;
    if (dt_ms > 0 && dt_ms < 500) {
        float raw_velocity = (new_multi_deg - position_tracker.multi_deg) * 1000.0f / dt_ms;
        if (position_tracker.has_velocity) {
            position_tracker.velocity_deg_s = position_tracker.velocity_deg_s * 0.7f + raw_velocity * 0.3f;
        } else {
            position_tracker.velocity_deg_s = raw_velocity;
            position_tracker.has_velocity = true;
        }
    }

    position_tracker.multi_deg = new_multi_deg;
    position_tracker.last_update_ms = now;
}

static char mode_char() {
    switch (control_mode) {
        case MODE_CURRENT:
            return 'C';
        case MODE_POSITION:
            return 'P';
        default:
            return 'I';
    }
}

static bool position_feedback_ready(uint32_t now) {
    return position_tracker.initialized &&
           vesc.has_status_4 &&
           now - vesc.last_status_4_ms <= STATUS_TIMEOUT_MS;
}

static void reset_position_controller(float current_position_deg) {
    position_controller.initialized = true;
    position_controller.command_target_deg = current_position_deg;
    position_controller.ref_pos_deg = current_position_deg;
    position_controller.ref_vel_deg_s = 0.0f;
    position_controller.integral_a = 0.0f;
    position_controller.last_update_ms = millis();
    position_error_deg = 0.0f;
}

static void set_position_command_target(float target_deg) {
    if (!position_controller.initialized) {
        reset_position_controller(position_tracker.multi_deg);
    }
    position_controller.command_target_deg = target_deg;
}

// ==================== VESC CAN 发送 ====================
static bool vesc_send_can(uint8_t command_id, uint8_t vesc_id, const uint8_t *data, uint8_t len) {
    if (len > 8) return false;

    twai_message_t msg = {};
    msg.identifier = (command_id << 8) | vesc_id;
    msg.extd = 1;           // 29位扩展帧
    msg.rtr = 0;
    msg.data_length_code = len;
    memcpy(msg.data, data, len);

    return twai_transmit(&msg, pdMS_TO_TICKS(10)) == ESP_OK;
}

static bool vesc_set_current(float current_a) {
    current_a = clamp_float(current_a, -CURRENT_LIMIT_A, CURRENT_LIMIT_A);
    int32_t current_ma = (int32_t)(current_a * 1000.0f + (current_a >= 0.0f ? 0.5f : -0.5f));
    uint8_t data[4];
    write_i32_be(data, current_ma);
    return vesc_send_can(CAN_PACKET_SET_CURRENT, VESC_ID, data, 4);
}

// ==================== VESC 状态接收 ====================
static void parse_vesc_status(const twai_message_t &msg) {
    if (!msg.extd) return;

    uint8_t controller_id = msg.identifier & 0xFF;
    uint8_t packet_id = (msg.identifier >> 8) & 0xFF;
    if (controller_id != VESC_ID) return;

    can_rx_total++;
    vesc.last_rx_ms = millis();

    switch (packet_id) {
        case CAN_PACKET_STATUS:
            if (msg.data_length_code < 8) return;
            vesc.has_status_1 = true;
            vesc.erpm = read_i32_be(msg.data, 0);
            vesc.motor_current_a = read_i16_be(msg.data, 4) / 10.0f;
            vesc.duty = read_i16_be(msg.data, 6) / 1000.0f;
            break;

        case CAN_PACKET_STATUS_4:
            if (msg.data_length_code < 8) return;
            vesc.has_status_4 = true;
            vesc.last_status_4_ms = millis();
            vesc.temp_fet_c = read_i16_be(msg.data, 0) / 10.0f;
            vesc.temp_motor_c = read_i16_be(msg.data, 2) / 10.0f;
            vesc.input_current_a = read_i16_be(msg.data, 4) / 10.0f;
            vesc.pid_pos_deg = read_i16_be(msg.data, 6) / 50.0f;
            update_position_tracker(vesc.pid_pos_deg);
            break;

        case CAN_PACKET_STATUS_5:
            if (msg.data_length_code < 6) return;
            vesc.has_status_5 = true;
            vesc.tachometer = read_i32_be(msg.data, 0);
            vesc.input_voltage_v = read_i16_be(msg.data, 4) / 10.0f;
            break;

        default:
            break;
    }
}

static float compute_control_current(uint32_t now) {
    if (control_mode == MODE_CURRENT) {
        return target_current_a;
    }

    if (control_mode == MODE_POSITION) {
        if (!position_feedback_ready(now)) {
            position_controller.ref_vel_deg_s = 0.0f;
            position_controller.integral_a = 0.0f;
            return 0.0f;
        }

        if (!position_controller.initialized) {
            reset_position_controller(position_tracker.multi_deg);
        }

        float dt_s = (now - position_controller.last_update_ms) * 0.001f;
        if (dt_s <= 0.0f || dt_s > 0.1f) {
            dt_s = CURRENT_SEND_PERIOD_MS * 0.001f;
            position_controller.ref_vel_deg_s = 0.0f;
        }
        position_controller.last_update_ms = now;

        float target_delta = position_controller.command_target_deg - position_controller.ref_pos_deg;
        float desired_vel = clamp_float(target_delta * TRAJ_VEL_GAIN,
                                        -TRAJ_MAX_VEL_DEG_S,
                                        TRAJ_MAX_VEL_DEG_S);
        float max_vel_step = TRAJ_MAX_ACCEL_DEG_S2 * dt_s;
        float vel_delta = clamp_float(desired_vel - position_controller.ref_vel_deg_s,
                                      -max_vel_step, max_vel_step);
        position_controller.ref_vel_deg_s += vel_delta;

        float pos_step = position_controller.ref_vel_deg_s * dt_s;
        if (fabsf(pos_step) > fabsf(target_delta)) {
            position_controller.ref_pos_deg = position_controller.command_target_deg;
            position_controller.ref_vel_deg_s = 0.0f;
        } else {
            position_controller.ref_pos_deg += pos_step;
        }

        position_error_deg = position_controller.ref_pos_deg - position_tracker.multi_deg;
        if (fabsf(position_error_deg) <= POSITION_DEADBAND_DEG &&
            fabsf(position_tracker.velocity_deg_s) <= POSITION_SETTLE_VEL_DEG_S) {
            position_controller.integral_a = 0.0f;
            return 0.0f;
        }

        position_controller.integral_a += position_error_deg * POSITION_KI_A_PER_DEG_S * dt_s;
        position_controller.integral_a = clamp_float(position_controller.integral_a,
                                                     -POSITION_I_LIMIT_A,
                                                     POSITION_I_LIMIT_A);

        float current_a = position_error_deg * POSITION_KP_A_PER_DEG +
                          position_controller.integral_a -
                          position_tracker.velocity_deg_s * POSITION_KD_A_PER_DEG_S;

        if (fabsf(position_error_deg) >= POSITION_STATIC_ENABLE_DEG) {
            current_a += (position_error_deg > 0.0f) ? POSITION_STATIC_CURRENT_A : -POSITION_STATIC_CURRENT_A;
        }

        return clamp_float(current_a, -POSITION_CURRENT_LIMIT_A, POSITION_CURRENT_LIMIT_A);
    }

    position_error_deg = 0.0f;
    position_controller.ref_vel_deg_s = 0.0f;
    position_controller.integral_a = 0.0f;
    return 0.0f;
}

static void receive_vesc_messages() {
    twai_message_t rx_msg;
    while (twai_receive(&rx_msg, 0) == ESP_OK) {
        parse_vesc_status(rx_msg);
    }
}

static void print_status_periodic() {
    uint32_t now = millis();
    if (now - last_status_print_ms < STATUS_PRINT_PERIOD_MS) return;
    last_status_print_ms = now;

    if (vesc.last_rx_ms == 0) {
        LOG_PORT.printf("CAN tx=%lu/%lu rx=0 S=--- M=%c | wait VESC | out=%.3fA\n",
                        can_tx_ok, can_tx_fail, mode_char(), output_current_a);
        return;
    }

    LOG_PORT.printf("CAN tx=%lu/%lu rx=%lu age=%lums S=%c%c%c M=%c | out=%.3fA",
                    can_tx_ok, can_tx_fail, can_rx_total,
                    now - vesc.last_rx_ms,
                    vesc.has_status_1 ? '1' : '-',
                    vesc.has_status_4 ? '4' : '-',
                    vesc.has_status_5 ? '5' : '-',
                    mode_char(), output_current_a);

    if (control_mode == MODE_CURRENT) {
        LOG_PORT.printf(" cur=%.3f", target_current_a);
    } else if (control_mode == MODE_POSITION) {
        LOG_PORT.printf(" tgt=%.1f ref=%.1f err=%.1f vel=%.1f i=%.2f",
                        position_controller.command_target_deg,
                        position_controller.ref_pos_deg,
                        position_error_deg,
                        position_tracker.velocity_deg_s,
                        position_controller.integral_a);
    }

    if (vesc.has_status_1) {
        LOG_PORT.printf(" | erpm=%ld motor=%.1fA duty=%.1f%%",
                        vesc.erpm, vesc.motor_current_a, vesc.duty * 100.0f);
    }

    if (vesc.has_status_4) {
        LOG_PORT.printf(" | temp=%.1f/%.1fC in=%.1fA pos=%.1f mt=%.1f",
                        vesc.temp_fet_c, vesc.temp_motor_c,
                        vesc.input_current_a, vesc.pid_pos_deg,
                        position_tracker.multi_deg);
    }

    if (vesc.has_status_5) {
        LOG_PORT.printf(" | tacho=%ld vin=%.1fV",
                        vesc.tachometer, vesc.input_voltage_v);
    }

    LOG_PORT.println();
}

static void print_timeout_periodic() {
    uint32_t now = millis();
    if (vesc.last_rx_ms == 0 || now - vesc.last_rx_ms <= STATUS_TIMEOUT_MS) return;
    if (now - last_timeout_print_ms < STATUS_TIMEOUT_MS) return;
    last_timeout_print_ms = now;
    LOG_PORT.println("WARN: VESC status timeout");
}

// ==================== 串口命令 ====================
static bool parse_float_line(const String &line, float *out_value) {
    char buf[24];
    line.toCharArray(buf, sizeof(buf));

    char *end_ptr = nullptr;
    float value = strtof(buf, &end_ptr);
    while (end_ptr != nullptr && isspace((unsigned char)*end_ptr)) {
        end_ptr++;
    }

    if (end_ptr == buf || *end_ptr != '\0') return false;
    *out_value = value;
    return true;
}

static void apply_current_command(float current_a) {
    target_current_a = clamp_float(current_a, -CURRENT_LIMIT_A, CURRENT_LIMIT_A);
    control_mode = fabsf(target_current_a) > 0.0001f ? MODE_CURRENT : MODE_IDLE;
    if (control_mode != MODE_POSITION) {
        position_controller.ref_vel_deg_s = 0.0f;
        position_controller.integral_a = 0.0f;
    }
    LOG_PORT.printf("cur=%.3fA\n", target_current_a);
}

static void stop_output() {
    control_mode = MODE_IDLE;
    target_current_a = 0.0f;
    output_current_a = 0.0f;
    position_error_deg = 0.0f;
    position_controller.ref_vel_deg_s = 0.0f;
    position_controller.integral_a = 0.0f;
    LOG_PORT.println("idle");
}

static void hold_position() {
    uint32_t now = millis();
    if (!position_feedback_ready(now)) {
        LOG_PORT.println("pos wait");
        return;
    }

    reset_position_controller(position_tracker.multi_deg);
    control_mode = MODE_POSITION;
    LOG_PORT.printf("hold %.1f\n", position_controller.command_target_deg);
}

static void set_position_target(float target_deg) {
    uint32_t now = millis();
    if (!position_feedback_ready(now)) {
        LOG_PORT.println("pos wait");
        return;
    }

    if (!position_controller.initialized || control_mode != MODE_POSITION) {
        reset_position_controller(position_tracker.multi_deg);
    }

    set_position_command_target(target_deg);
    control_mode = MODE_POSITION;
    LOG_PORT.printf("pos %.1f\n", position_controller.command_target_deg);
}

static void move_relative(float delta_deg) {
    uint32_t now = millis();
    if (!position_feedback_ready(now)) {
        LOG_PORT.println("pos wait");
        return;
    }

    float base_deg = (control_mode == MODE_POSITION && position_controller.initialized)
                         ? position_controller.command_target_deg
                         : position_tracker.multi_deg;
    set_position_target(base_deg + delta_deg);
}

static void handle_command_line(String line) {
    line.trim();
    if (line.length() == 0) return;

    if (line.equalsIgnoreCase("s") || line.equalsIgnoreCase("stop")) {
        stop_output();
        return;
    }

    if (line.equalsIgnoreCase("p")) {
        hold_position();
        return;
    }

    char prefix = (char)tolower((unsigned char)line[0]);
    if (prefix == 'c' || prefix == 'p' || prefix == 'r') {
        String arg = line.substring(1);
        arg.trim();

        float value = 0.0f;
        if (!parse_float_line(arg, &value)) {
            LOG_PORT.println("cmd: p [deg], r deg, c A, s");
            return;
        }

        if (prefix == 'c') {
            apply_current_command(value);
        } else if (prefix == 'p') {
            set_position_target(value);
        } else {
            move_relative(value);
        }
        return;
    }

    float requested_current = 0.0f;
    if (parse_float_line(line, &requested_current)) {
        apply_current_command(requested_current);
        return;
    }

    LOG_PORT.println("cmd: p [deg], r deg, c A, s");
}

static void read_serial_commands() {
    while (LOG_PORT.available()) {
        char c = LOG_PORT.read();
        if (c == '\n' || c == '\r') {
            handle_command_line(input_buf);
            input_buf = "";
        } else if (input_buf.length() < 23) {
            input_buf += c;
        }
    }
}

// ==================== 初始化 ====================
void setup() {
    LOG_PORT.begin(115200);
    delay(1500);
    LOG_PORT.println("boot");

    // TWAI (CAN) 配置：1Mbps
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, TWAI_MODE_NORMAL);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_1MBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
        LOG_PORT.println("CAN driver ok");
    } else {
        LOG_PORT.println("CAN driver fail");
        return;
    }

    if (twai_start() == ESP_OK) {
        LOG_PORT.println("CAN start ok");
    } else {
        LOG_PORT.println("CAN start fail");
        return;
    }

    LOG_PORT.println("ready: p, p deg, r deg, c A, s");
}

// ==================== 主循环 ====================
void loop() {
    read_serial_commands();
    receive_vesc_messages();

    uint32_t now = millis();
    if (now - last_current_send_ms >= CURRENT_SEND_PERIOD_MS) {
        last_current_send_ms = now;
        output_current_a = compute_control_current(now);
        if (vesc_set_current(output_current_a)) {
            can_tx_ok++;
        } else {
            can_tx_fail++;
        }
    }

    print_status_periodic();
    print_timeout_periodic();
}
