#include <Arduino.h>
#include <stdarg.h>
#include "driver/twai.h"

// ==================== 配置 ====================
#define CAN_TX_PIN GPIO_NUM_8
#define CAN_RX_PIN GPIO_NUM_18
#define MOTOR_ID   1

// C620 使用 11 位标准帧，CAN 速率固定为 1 Mbps
constexpr uint32_t C620_CMD_ID_LOW = 0x200;   // 控制 ID 1-4
constexpr uint32_t C620_CMD_ID_HIGH = 0x1FF;  // 控制 ID 5-8
constexpr uint32_t C620_FB_BASE_ID = 0x200;   // 反馈 ID = 0x200 + motor_id

constexpr float C620_MAX_CURRENT_A = 20.0f;
constexpr int16_t C620_MAX_CURRENT_CMD = 16384;
constexpr uint32_t COMMAND_PERIOD_MS = 2;
constexpr uint32_t STATUS_PRINT_PERIOD_MS = 200;
constexpr uint32_t LISTEN_ONLY_PROBE_MS = 15000;
constexpr uint32_t ACTIVE_ID_SCAN_MS = 2000;
constexpr uint32_t ACTIVE_ID_SCAN_TX_PERIOD_MS = 10;
constexpr float SPEED_KP_A_PER_RPM = 0.0060f;
constexpr float DEFAULT_CURRENT_LIMIT_A = 12.0f;
constexpr float STARTUP_BOOST_CURRENT_A = 3.0f;
constexpr int16_t STARTUP_BOOST_SPEED_RPM = 30;

enum class ControlMode {
    Stop,
    Current,
    Speed
};

struct MotorFeedback {
    uint16_t angle_raw = 0;
    int16_t speed_rpm = 0;
    int16_t torque_current_raw = 0;
    uint8_t temperature_c = 0;
    bool online = false;
    uint32_t last_update_ms = 0;
};

static String input_buf;
static ControlMode control_mode = ControlMode::Stop;
static float target_current_a = 0.0f;
static int32_t target_rpm = 0;
static float current_limit_a = DEFAULT_CURRENT_LIMIT_A;
static float last_command_current_a = 0.0f;
static uint32_t last_send_ms = 0;
static uint32_t last_print_ms = 0;
static uint32_t last_can_error_print_ms = 0;
static uint32_t can_rx_total_frames = 0;
static uint32_t can_target_feedback_frames = 0;
static uint32_t can_tx_ok_count = 0;
static uint32_t can_tx_fail_count = 0;
static uint32_t probe_total_frames = 0;
static uint32_t probe_target_feedback_frames = 0;
static uint32_t detected_motor_id_mask = 0;
static bool first_feedback_logged = false;
static bool first_nonzero_command_logged = false;
static MotorFeedback motor_feedback;

static int16_t current_a_to_command(float current_a);
static void parse_feedback(const twai_message_t &msg);
static void active_motor_id_scan(uint32_t duration_ms);

static void log_begin() {
    Serial.begin(115200);
    Serial0.begin(115200, SERIAL_8N1, 44, 43);
}

static void dual_println(const char *message) {
    Serial.println(message);
    Serial0.println(message);
}

static void dual_printf(const char *format, ...) {
    char buffer[192];
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    Serial.print(buffer);
    Serial0.print(buffer);
}

static const char *twai_state_name(twai_state_t state) {
    switch (state) {
        case TWAI_STATE_STOPPED:
            return "STOPPED";
        case TWAI_STATE_RUNNING:
            return "RUNNING";
        case TWAI_STATE_BUS_OFF:
            return "BUS_OFF";
        case TWAI_STATE_RECOVERING:
            return "RECOVERING";
        default:
            return "UNKNOWN";
    }
}

static const char *control_mode_name(ControlMode mode) {
    switch (mode) {
        case ControlMode::Stop:
            return "STOP";
        case ControlMode::Current:
            return "CURRENT";
        case ControlMode::Speed:
            return "SPEED";
        default:
            return "UNKNOWN";
    }
}

static uint32_t expected_feedback_id() {
    return C620_FB_BASE_ID + MOTOR_ID;
}

static uint32_t command_id_for_motor(uint8_t motor_id) {
    return (motor_id <= 4) ? C620_CMD_ID_LOW : C620_CMD_ID_HIGH;
}

static uint8_t feedback_id_to_motor_id(uint32_t feedback_id) {
    if (feedback_id >= (C620_FB_BASE_ID + 1) && feedback_id <= (C620_FB_BASE_ID + 8)) {
        return static_cast<uint8_t>(feedback_id - C620_FB_BASE_ID);
    }
    return 0;
}

static void print_motor_id_mask(const char *reason, uint32_t mask) {
    dual_printf("[scan] %s detected motor IDs:", reason);
    if (mask == 0) {
        dual_println(" none");
        return;
    }

    for (uint8_t motor_id = 1; motor_id <= 8; ++motor_id) {
        if (mask & (1UL << (motor_id - 1))) {
            dual_printf(" %u", motor_id);
        }
    }
    dual_println("");
}

static void print_diagnostics(const char *reason) {
    twai_status_info_t can_status = {};
    twai_get_status_info(&can_status);

    uint32_t feedback_age_ms = motor_feedback.online ? (millis() - motor_feedback.last_update_ms) : 0xFFFFFFFFUL;
    int16_t raw_command = current_a_to_command(last_command_current_a);

    dual_printf("[diag] reason=%s mode=%s target_rpm=%ld target_current=%.2fA current_limit=%.2fA last_cmd=%.2fA raw_cmd=%d fb_online=%d fb_age_ms=%lu fb_rpm=%d rx_total=%lu fb_frames=%lu tx_ok=%lu tx_fail=%lu can_state=%s tx_err=%lu rx_err=%lu bus_err=%lu\n",
                reason,
                control_mode_name(control_mode),
                target_rpm,
                target_current_a,
                current_limit_a,
                last_command_current_a,
                raw_command,
                motor_feedback.online ? 1 : 0,
                static_cast<unsigned long>(feedback_age_ms),
                motor_feedback.speed_rpm,
                static_cast<unsigned long>(can_rx_total_frames),
                static_cast<unsigned long>(can_target_feedback_frames),
                static_cast<unsigned long>(can_tx_ok_count),
                static_cast<unsigned long>(can_tx_fail_count),
                twai_state_name(can_status.state),
                can_status.tx_error_counter,
                can_status.rx_error_counter,
                can_status.bus_error_count);

    dual_printf("[diag] MOTOR_ID=%d expected_fb_id=0x%03lX command_id=0x%03lX probe_total=%lu probe_target=%lu detected_mask=0x%02lX\n",
                MOTOR_ID,
                static_cast<unsigned long>(expected_feedback_id()),
                static_cast<unsigned long>(command_id_for_motor(MOTOR_ID)),
                static_cast<unsigned long>(probe_total_frames),
                static_cast<unsigned long>(probe_target_feedback_frames),
                static_cast<unsigned long>(detected_motor_id_mask));

    if (control_mode == ControlMode::Stop) {
        dual_println("[diag] Motor is in STOP mode. It will not rotate until you send 'r 3000' or 'i 2'.");
    }

    if (probe_total_frames == 0) {
        dual_println("[diag] No CAN traffic was seen during the listen-only probe. Check C620 power, transceiver power, CANH/CANL wiring, common ground, and 120 ohm termination.");
    } else if (probe_target_feedback_frames == 0) {
        dual_printf("[diag] CAN traffic exists, but no feedback matched expected ID 0x%03lX. Check motor ID and whether the C620 is in CAN mode.\n",
                    static_cast<unsigned long>(expected_feedback_id()));
    }
}

static esp_err_t install_twai_driver(twai_mode_t mode) {
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, mode);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_1MBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    esp_err_t ret = twai_driver_install(&g_config, &t_config, &f_config);
    if (ret != ESP_OK) {
        return ret;
    }

    ret = twai_start();
    if (ret != ESP_OK) {
        twai_driver_uninstall();
        return ret;
    }

    return ESP_OK;
}

static void uninstall_twai_driver() {
    twai_stop();
    twai_driver_uninstall();
}

static void listen_only_probe(uint32_t duration_ms) {
    probe_total_frames = 0;
    probe_target_feedback_frames = 0;
    dual_printf("[probe] Listen-only for %lu ms. Expecting feedback ID 0x%03lX on TX=%d RX=%d\n",
                duration_ms,
                static_cast<unsigned long>(expected_feedback_id()),
                static_cast<int>(CAN_TX_PIN),
                static_cast<int>(CAN_RX_PIN));
    dual_printf("启动 %lu ms CAN 监听探测...\n", duration_ms);

    uint32_t start_ms = millis();
    uint32_t frame_count = 0;

    while (millis() - start_ms < duration_ms) {
        twai_message_t msg;
        if (twai_receive(&msg, pdMS_TO_TICKS(20)) == ESP_OK) {
            frame_count++;
            probe_total_frames++;
            if (!msg.extd && msg.identifier == expected_feedback_id()) {
                probe_target_feedback_frames++;
            }
            dual_printf("监听到帧 id=0x%03lx ext=%d dlc=%d data=%02X %02X %02X %02X %02X %02X %02X %02X\n",
                        msg.identifier,
                        msg.extd,
                        msg.data_length_code,
                        msg.data[0], msg.data[1], msg.data[2], msg.data[3],
                        msg.data[4], msg.data[5], msg.data[6], msg.data[7]);
        }
    }

    if (frame_count == 0) {
        dual_println("监听阶段未收到任何 CAN 帧");
    } else {
        dual_printf("监听阶段共收到 %lu 帧\n", frame_count);
    }
    dual_printf("[probe] total_frames=%lu matched_expected_feedback=%lu\n",
                static_cast<unsigned long>(probe_total_frames),
                static_cast<unsigned long>(probe_target_feedback_frames));
}

static int16_t clamp_current_command(int32_t value) {
    if (value > C620_MAX_CURRENT_CMD) {
        return C620_MAX_CURRENT_CMD;
    }
    if (value < -C620_MAX_CURRENT_CMD) {
        return -C620_MAX_CURRENT_CMD;
    }
    return static_cast<int16_t>(value);
}

static int16_t current_a_to_command(float current_a) {
    float limited_current = constrain(current_a, -C620_MAX_CURRENT_A, C620_MAX_CURRENT_A);
    int32_t command = static_cast<int32_t>(limited_current * C620_MAX_CURRENT_CMD / C620_MAX_CURRENT_A);
    return clamp_current_command(command);
}

static float command_to_current_a(int16_t command) {
    return static_cast<float>(command) * C620_MAX_CURRENT_A / C620_MAX_CURRENT_CMD;
}

static void c620_send_current_command(uint8_t motor_id, int16_t current_cmd) {
    if (motor_id < 1 || motor_id > 8) {
        return;
    }

    twai_message_t msg = {};
    msg.identifier = (motor_id <= 4) ? C620_CMD_ID_LOW : C620_CMD_ID_HIGH;
    msg.extd = 0;
    msg.rtr = 0;
    msg.data_length_code = 8;
    memset(msg.data, 0, sizeof(msg.data));

    uint8_t offset = static_cast<uint8_t>(((motor_id - 1) % 4) * 2);
    msg.data[offset] = static_cast<uint8_t>((current_cmd >> 8) & 0xFF);
    msg.data[offset + 1] = static_cast<uint8_t>(current_cmd & 0xFF);

    esp_err_t ret = twai_transmit(&msg, pdMS_TO_TICKS(10));
    if (ret == ESP_OK) {
        can_tx_ok_count++;
        if (current_cmd != 0 && !first_nonzero_command_logged) {
            first_nonzero_command_logged = true;
            dual_printf("[cmd] First non-zero command sent: motor=%d can_id=0x%03lX raw=%d current=%.2fA\n",
                        motor_id,
                        static_cast<unsigned long>(msg.identifier),
                        current_cmd,
                        command_to_current_a(current_cmd));
        }
    } else {
        can_tx_fail_count++;
        if (millis() - last_can_error_print_ms >= 200) {
            last_can_error_print_ms = millis();
            twai_status_info_t can_status = {};
            twai_get_status_info(&can_status);
            dual_printf("CAN 发送失败 ret=%d state=%s tx_err=%lu rx_err=%lu tx_fail=%lu bus_err=%lu tx_msg=%lu\n",
                        static_cast<int>(ret),
                        twai_state_name(can_status.state),
                        can_status.tx_error_counter,
                        can_status.rx_error_counter,
                        can_status.tx_failed_count,
                        can_status.bus_error_count,
                        can_status.msgs_to_tx);
        }
    }
}

static void print_help() {
    dual_println("C620 控制命令:");
    dual_println("  直接输入数字: 目标转速 RPM，例如 3000");
    dual_println("  r 3000      : 转速模式，目标 3000 RPM");
    dual_println("  i 3.5       : 电流模式，输出 3.5A");
    dual_println("  l 8         : 设置闭环限流 8A");
    dual_println("  s           : 停止输出");
    dual_println("  h           : 显示帮助");
    dual_println("  d / diag    : Print a diagnostic snapshot");
    dual_println("  scan / ids  : Active safe motor ID scan");
}

static void set_stop_mode() {
    control_mode = ControlMode::Stop;
    target_current_a = 0.0f;
    target_rpm = 0;
    dual_println("已停止输出");
}

static void handle_command(String line) {
    line.trim();
    if (line.length() == 0) {
        return;
    }

    if (line.equalsIgnoreCase("h") || line.equalsIgnoreCase("help")) {
        print_help();
        return;
    }

    if (line.equalsIgnoreCase("scan") || line.equalsIgnoreCase("ids")) {
        active_motor_id_scan(ACTIVE_ID_SCAN_MS);
        print_diagnostics("manual_scan");
        return;
    }

    if (line.equalsIgnoreCase("d") || line.equalsIgnoreCase("diag")) {
        print_diagnostics("manual");
        return;
    }

    if (line.equalsIgnoreCase("s") || line == "0") {
        set_stop_mode();
        print_diagnostics("stop_command");
        return;
    }

    if (line.startsWith("i ") || line.startsWith("I ")) {
        float value = line.substring(2).toFloat();
        target_current_a = constrain(value, -current_limit_a, current_limit_a);
        control_mode = ControlMode::Current;
        print_diagnostics("current_command");
        dual_printf("电流模式: 目标 %.2f A (限流 %.2f A)\n", target_current_a, current_limit_a);
        return;
    }

    if (line.startsWith("r ") || line.startsWith("R ")) {
        target_rpm = line.substring(2).toInt();
        control_mode = ControlMode::Speed;
        print_diagnostics("speed_command");
        dual_printf("转速模式: 目标 %ld RPM (限流 %.2f A)\n", target_rpm, current_limit_a);
        return;
    }

    if (line.startsWith("l ") || line.startsWith("L ")) {
        float value = fabsf(line.substring(2).toFloat());
        current_limit_a = constrain(value, 0.5f, C620_MAX_CURRENT_A);
        if (control_mode == ControlMode::Current) {
            target_current_a = constrain(target_current_a, -current_limit_a, current_limit_a);
        }
        print_diagnostics("limit_command");
        dual_printf("闭环限流已设置为 %.2f A\n", current_limit_a);
        return;
    }

    target_rpm = line.toInt();
    control_mode = (target_rpm == 0) ? ControlMode::Stop : ControlMode::Speed;
    print_diagnostics("numeric_speed_command");
    dual_printf("转速模式: 目标 %ld RPM (限流 %.2f A)\n", target_rpm, current_limit_a);
}

static void process_serial_stream(Stream &port, String &buffer) {
    while (port.available()) {
        char c = static_cast<char>(port.read());
        if (c == '\n' || c == '\r') {
            if (buffer.length() > 0) {
                handle_command(buffer);
                buffer = "";
            }
        } else {
            buffer += c;
        }
    }
}

static void read_serial_commands() {
    process_serial_stream(Serial, input_buf);
    process_serial_stream(Serial0, input_buf);
}

static void parse_feedback(const twai_message_t &msg) {
    if (msg.extd || msg.data_length_code < 7) {
        return;
    }

    if (msg.identifier != C620_FB_BASE_ID + MOTOR_ID) {
        return;
    }

    motor_feedback.angle_raw = static_cast<uint16_t>((msg.data[0] << 8) | msg.data[1]);
    motor_feedback.speed_rpm = static_cast<int16_t>((msg.data[2] << 8) | msg.data[3]);
    motor_feedback.torque_current_raw = static_cast<int16_t>((msg.data[4] << 8) | msg.data[5]);
    motor_feedback.temperature_c = msg.data[6];
    motor_feedback.online = true;
    motor_feedback.last_update_ms = millis();
    detected_motor_id_mask |= (1UL << (MOTOR_ID - 1));
    can_target_feedback_frames++;

    if (!first_feedback_logged) {
        first_feedback_logged = true;
        dual_printf("[fb] First target feedback: id=0x%03lX rpm=%d angle=%u current_raw=%d temp=%uC\n",
                    static_cast<unsigned long>(msg.identifier),
                    motor_feedback.speed_rpm,
                    motor_feedback.angle_raw,
                    motor_feedback.torque_current_raw,
                    motor_feedback.temperature_c);
    }
}

static void receive_can_feedback() {
    twai_message_t msg;
    while (twai_receive(&msg, 0) == ESP_OK) {
        can_rx_total_frames++;
        parse_feedback(msg);
    }
}

static void send_zero_scan_frame(uint32_t command_id) {
    twai_message_t msg = {};
    msg.identifier = command_id;
    msg.extd = 0;
    msg.rtr = 0;
    msg.data_length_code = 8;
    memset(msg.data, 0, sizeof(msg.data));

    esp_err_t ret = twai_transmit(&msg, pdMS_TO_TICKS(10));
    if (ret == ESP_OK) {
        can_tx_ok_count++;
    } else {
        can_tx_fail_count++;
    }
}

static void active_motor_id_scan(uint32_t duration_ms) {
    dual_printf("[scan] Active ID scan for %lu ms. Sending zero-current frames to 0x%03lX and 0x%03lX.\n",
                duration_ms,
                static_cast<unsigned long>(C620_CMD_ID_LOW),
                static_cast<unsigned long>(C620_CMD_ID_HIGH));

    uint32_t scan_mask = 0;
    uint32_t start_ms = millis();
    uint32_t last_tx_ms = 0;

    while (millis() - start_ms < duration_ms) {
        uint32_t now_ms = millis();
        if (now_ms - last_tx_ms >= ACTIVE_ID_SCAN_TX_PERIOD_MS) {
            last_tx_ms = now_ms;
            send_zero_scan_frame(C620_CMD_ID_LOW);
            send_zero_scan_frame(C620_CMD_ID_HIGH);
        }

        twai_message_t msg;
        if (twai_receive(&msg, pdMS_TO_TICKS(5)) == ESP_OK) {
            can_rx_total_frames++;

            uint8_t detected_id = feedback_id_to_motor_id(msg.identifier);
            if (!msg.extd && msg.data_length_code >= 7 && detected_id >= 1 && detected_id <= 8) {
                uint32_t id_bit = 1UL << (detected_id - 1);
                if ((scan_mask & id_bit) == 0) {
                    dual_printf("[scan] Found motor ID %u from feedback 0x%03lX\n",
                                detected_id,
                                static_cast<unsigned long>(msg.identifier));
                }
                scan_mask |= id_bit;
            }

            parse_feedback(msg);
        }
    }

    detected_motor_id_mask |= scan_mask;
    print_motor_id_mask("Active scan", scan_mask);
}

static float compute_target_current_a() {
    if (control_mode == ControlMode::Current) {
        return target_current_a;
    }

    if (control_mode == ControlMode::Speed) {
        int32_t speed_error = target_rpm - motor_feedback.speed_rpm;
        float current_cmd = speed_error * SPEED_KP_A_PER_RPM;
        if (target_rpm != 0 && abs(motor_feedback.speed_rpm) < STARTUP_BOOST_SPEED_RPM) {
            float boost = (target_rpm > 0) ? STARTUP_BOOST_CURRENT_A : -STARTUP_BOOST_CURRENT_A;
            if (fabsf(current_cmd) < fabsf(boost)) {
                current_cmd = boost;
            }
        }
        return constrain(current_cmd, -current_limit_a, current_limit_a);
    }

    return 0.0f;
}

static void print_status() {
    if (millis() - last_print_ms < STATUS_PRINT_PERIOD_MS) {
        return;
    }
    last_print_ms = millis();

    twai_status_info_t can_status = {};
    twai_get_status_info(&can_status);

    if (!motor_feedback.online || millis() - motor_feedback.last_update_ms > 500) {
        const char *hint = "Send a command and check wiring.";
        if (control_mode == ControlMode::Stop) {
            hint = "STOP mode. Send 'r 3000' or 'i 2' after boot.";
        } else if (probe_total_frames == 0) {
            hint = "No CAN traffic in probe. Check transceiver, wiring, power, and termination.";
        } else if (probe_target_feedback_frames == 0) {
            hint = "CAN is alive but expected feedback ID was not seen. Check MOTOR_ID and C620 CAN mode.";
        }

        dual_printf("[status] waiting_feedback mode=%s target_rpm=%ld last_cmd=%.2fA tx_ok=%lu tx_fail=%lu rx_total=%lu fb_frames=%lu CAN=%s tx_err=%lu rx_err=%lu tx_fail_hw=%lu bus_err=%lu hint=%s\n",
                    control_mode_name(control_mode),
                    target_rpm,
                    last_command_current_a,
                    static_cast<unsigned long>(can_tx_ok_count),
                    static_cast<unsigned long>(can_tx_fail_count),
                    static_cast<unsigned long>(can_rx_total_frames),
                    static_cast<unsigned long>(can_target_feedback_frames),
                    twai_state_name(can_status.state),
                    can_status.tx_error_counter,
                    can_status.rx_error_counter,
                    can_status.tx_failed_count,
                    can_status.bus_error_count,
                    hint);
        dual_printf("等待 C620 反馈... CAN=%s  tx_err=%lu  rx_err=%lu  tx_fail=%lu  bus_err=%lu\n",
                    twai_state_name(can_status.state),
                    can_status.tx_error_counter,
                    can_status.rx_error_counter,
                    can_status.tx_failed_count,
                    can_status.bus_error_count);
        return;
    }

    float measured_current_a = command_to_current_a(motor_feedback.torque_current_raw);
    dual_printf("反馈 RPM: %d  角度: %u  指令电流: %.2fA  实际电流: %.2fA  温度: %uC  CAN=%s  tx_err=%lu  rx_err=%lu\n",
                motor_feedback.speed_rpm,
                motor_feedback.angle_raw,
                last_command_current_a,
                measured_current_a,
                motor_feedback.temperature_c,
                twai_state_name(can_status.state),
                can_status.tx_error_counter,
                can_status.rx_error_counter);
}

// ==================== 初始化 ====================
void setup() {
    // 同时输出到 USB CDC(Serial) 和 UART0(Serial0)
    log_begin();
    delay(500);

    if (install_twai_driver(TWAI_MODE_LISTEN_ONLY) != ESP_OK) {
        dual_println("TWAI 监听模式启动失败");
        return;
    }
    listen_only_probe(LISTEN_ONLY_PROBE_MS);
    uninstall_twai_driver();

    if (install_twai_driver(TWAI_MODE_NORMAL) != ESP_OK) {
        dual_println("TWAI 正常模式启动失败");
        return;
    }

    dual_printf("C620 控制已启动, MOTOR_ID=%d, CAN=1Mbps\n", MOTOR_ID);
    dual_println("注意: C620 手册要求电机 ID 正确，且电调模式已切到 CAN。");
    dual_printf("[boot] Motor will stay stopped after power-on until a serial command is received. There is also a %lu ms listen-only probe before normal control starts.\n",
                LISTEN_ONLY_PROBE_MS);
    dual_printf("[boot] MOTOR_ID=%d expected_feedback=0x%03lX command_id=0x%03lX CAN=1Mbps\n",
                MOTOR_ID,
                static_cast<unsigned long>(expected_feedback_id()),
                static_cast<unsigned long>(command_id_for_motor(MOTOR_ID)));
    active_motor_id_scan(ACTIVE_ID_SCAN_MS);
    print_help();
    print_diagnostics("boot_complete");
}

// ==================== 主循环 ====================
void loop() {
    read_serial_commands();
    receive_can_feedback();

    if (millis() - last_send_ms >= COMMAND_PERIOD_MS) {
        last_send_ms = millis();
        last_command_current_a = compute_target_current_a();
        int16_t current_cmd = current_a_to_command(last_command_current_a);
        c620_send_current_command(MOTOR_ID, current_cmd);
    }

    print_status();
}
