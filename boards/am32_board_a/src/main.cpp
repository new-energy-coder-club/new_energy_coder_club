/*
 * @Description: AM32 四电机无线串口调参测试程序
 * @Platform:    HXC-A (ESP32-S3-WROOM-1-N16R8)
 *
 * 引脚分配:
 *   M1 -> GPIO9   / RMT ch0
 *   M2 -> GPIO10  / RMT ch1
 *   M3 -> GPIO11  / RMT ch2
 *   M4 -> GPIO12  / RMT ch3
 *   UART0 -> RX44 / TX43
 *
 * 串口命令格式: 命令[空格][数值]，不区分大小写
 *   F / F20 / F 20    前进（无数值默认10）
 *   B / B20           后退
 *   L / L20           左转（原地差速）
 *   R / R20           右转（原地差速）
 *   S                 停止
 *   arm 1             重新解锁所有电调
 *   arm_ms 1500       解锁持续时间 ms
 *   all 10            四路统一设值（调试）
 *   m1~m4 [-]10       单路调试，范围 -100~100
 *   status_ms 500     状态打印周期 ms
 */

#include <Arduino.h>
#include "DSHOT_ESC/DSHOT_ESC.hpp"
#include "vofa/VOFA.hpp"
#include "HotRC_RC/HotRC_RC.hpp"

#define SERIAL_BAUD              115200
#define UART0_RX_PIN             44
#define UART0_TX_PIN             43
#define DEFAULT_ARM_DURATION_MS  1500
#define DSHOT_UPDATE_INTERVAL_MS 2
#define MOTOR_COUNT              4

// ---- 遥控器引脚 ----
#define RC_CH1_PIN               GPIO_NUM_48   // 左右（1000=最左, 2000=最右）
#define RC_CH3_PIN               GPIO_NUM_38   // 前后（1000=最后, 2000=最前）

// ---- 可调常量（集中管理，避免散落的魔法数字）----
static constexpr float    THROTTLE_LIMIT_PERCENT = 100.0f;
static constexpr float    DEFAULT_DRIVE_SPEED    = 10.0f;   // 行驶命令不带数值时的默认速度
static constexpr float    ARM_TRIGGER_THRESHOLD  = 0.5f;    // arm 参数上升沿判定阈值
static constexpr float    MIN_ARM_DURATION_MS    = 100.0f;
static constexpr float    MIN_STATUS_PERIOD_MS   = 100.0f;
static constexpr float    DEFAULT_STATUS_MS      = 500.0f;
static constexpr float    RC_THROTTLE_SCALE      = 80.0f;   // 遥控油门最大幅度（%）
static constexpr float    RC_TURN_SCALE          = 60.0f;   // 遥控转向最大幅度（%）
static constexpr float    DEFAULT_ACCEL_LIMIT    = 50.0f;   // 缓冲模式默认加速度上限（%/s）
static constexpr float    DEFAULT_DECEL_LIMIT    = 200.0f;  // 缓冲模式默认减速度上限（%/s）

enum MotorIndex : uint8_t {
    MOTOR_1 = 0,
    MOTOR_2 = 1,
    MOTOR_3 = 2,
    MOTOR_4 = 3,
};

AM32Motor motors[MOTOR_COUNT] = {
    AM32Motor(GPIO_NUM_9,  RMT_CHANNEL_0, &Serial),
    AM32Motor(GPIO_NUM_10, RMT_CHANNEL_1, &Serial),
    AM32Motor(GPIO_NUM_11, RMT_CHANNEL_2, &Serial),
    AM32Motor(GPIO_NUM_12, RMT_CHANNEL_3, &Serial),
};

VOFA_float param_arm("arm", 0.0f);
VOFA_float param_arm_ms("arm_ms", DEFAULT_ARM_DURATION_MS);
VOFA_float param_forward("f", 0.0f);
VOFA_float param_backward("b", 0.0f);
VOFA_float param_left("l", 0.0f);
VOFA_float param_right("r", 0.0f);
VOFA_float param_stop("s", 0.0f);
VOFA_float param_all("all", 0.0f);
VOFA_float param_m1("m1", 0.0f);
VOFA_float param_m2("m2", 0.0f);
VOFA_float param_m3("m3", 0.0f);
VOFA_float param_m4("m4", 0.0f);
VOFA_float param_status_ms("status_ms", DEFAULT_STATUS_MS);
VOFA_float param_rc_enable("rc_enable", 1.0f);   // 遥控模式开关：>0.5 启用
VOFA_float param_rc_debug("rc_debug", 0.0f);     // 遥控调试打印：>0.5 启用
VOFA_float param_smooth_enable("smooth", 1.0f);  // 缓冲模式开关：>0.5 启用加速度限制
VOFA_float param_accel_limit("accel", DEFAULT_ACCEL_LIMIT);  // 加速度上限 %/s
VOFA_float param_decel_limit("decel", DEFAULT_DECEL_LIMIT);  // 减速度上限 %/s

static bool arm_latched = false;
static uint32_t last_dshot_send_ms = 0;
static uint32_t last_status_ms = 0;
static uint32_t last_rc_debug_ms = 0;
static float motorTargets[MOTOR_COUNT] = {0.0f, 0.0f, 0.0f, 0.0f};          // 期望输出
static float motorTargetsSmoothed[MOTOR_COUNT] = {0.0f, 0.0f, 0.0f, 0.0f};  // 斜率限制后实际输出

HotRC_Channel rc_ch1(RC_CH1_PIN, "CH1");
HotRC_Channel rc_ch3(RC_CH3_PIN, "CH3");

float clampPercent(float value) {
    if (value > THROTTLE_LIMIT_PERCENT) {
        return THROTTLE_LIMIT_PERCENT;
    }
    if (value < -THROTTLE_LIMIT_PERCENT) {
        return -THROTTLE_LIMIT_PERCENT;
    }
    return value;
}

// 内部直接赋值（不再重复 clamp，调用方保证已 clamp）
static inline void assignMotorTargets(float m1, float m2, float m3, float m4) {
    motorTargets[MOTOR_1] = m1;
    motorTargets[MOTOR_2] = m2;
    motorTargets[MOTOR_3] = m3;
    motorTargets[MOTOR_4] = m4;
}

void setMotorTargets(float m1, float m2, float m3, float m4) {
    assignMotorTargets(clampPercent(m1), clampPercent(m2),
                       clampPercent(m3), clampPercent(m4));
}

static float maxAbs4(float a, float b, float c, float d) {
    float result = fabsf(a);
    if (fabsf(b) > result) result = fabsf(b);
    if (fabsf(c) > result) result = fabsf(c);
    if (fabsf(d) > result) result = fabsf(d);
    return result;
}

// 混控专用：当油门+转向超过 100% 时，四路按比例整体缩小，保留转向手感。
void setMixedMotorTargets(float m1, float m2, float m3, float m4) {
    const float max_abs = maxAbs4(m1, m2, m3, m4);
    if (max_abs > THROTTLE_LIMIT_PERCENT) {
        const float scale = THROTTLE_LIMIT_PERCENT / max_abs;
        m1 *= scale;
        m2 *= scale;
        m3 *= scale;
        m4 *= scale;
    }
    setMotorTargets(m1, m2, m3, m4);
}

template <typename... Args>
void printfBoth(const char* format, Args... args) {
    Serial.printf(format, args...);
    Serial0.printf(format, args...);
}

void printlnBoth(const String& text = "") {
    Serial.println(text);
    Serial0.println(text);
}

void setAllMotorTargets(float throttle) {
    const float limited = clampPercent(throttle);
    assignMotorTargets(limited, limited, limited, limited);
}

void commandForward(float speed) {
    const float limited = clampPercent(fabsf(speed));
    assignMotorTargets(-limited, -limited, limited, limited);
}

void commandBackward(float speed) {
    const float limited = clampPercent(fabsf(speed));
    assignMotorTargets(limited, limited, -limited, -limited);
}

void commandLeft(float speed) {
    const float limited = clampPercent(fabsf(speed));
    assignMotorTargets(limited, limited, limited, limited);
}

void commandRight(float speed) {
    const float limited = clampPercent(fabsf(speed));
    assignMotorTargets(-limited, -limited, -limited, -limited);
}

void commandStop() {
    setAllMotorTargets(0.0f);
}

void armAllMotors() {
    const uint32_t arm_ms = (uint32_t)max(param_arm_ms.read(), MIN_ARM_DURATION_MS);
    printfBoth("[ARM] all motors, duration=%lu ms\n", arm_ms);
    for (auto& motor : motors) {
        motor.arm(arm_ms);
    }
}

void printHelp() {
    printlnBoth();
    printlnBoth("四电机调参已就绪，格式: 命令[空格][数值]");
    printlnBoth("  -- 行驶命令 (不输入数值默认速度10) --");
    printlnBoth("  F / F10 / F 10    前进");
    printlnBoth("  B / B10 / B 10    后退");
    printlnBoth("  L / L10 / L 10    左转");
    printlnBoth("  R / R10 / R 10    右转");
    printlnBoth("  S                 停止");
    printlnBoth("  -- 调试命令 --");
    printlnBoth("  arm 1             四个电调全部重新解锁一次");
    printlnBoth("  arm_ms 1500       解锁持续时间，单位 ms");
    printlnBoth("  all 10            四个电机统一设为 10%");
    printlnBoth("  m1 10             电机1目标油门，范围 -100~100");
    printlnBoth("  m2 -10            电机2目标油门，负数自动反转");
    printlnBoth("  m3 0              电机3停止");
    printlnBoth("  m4 0              电机4停止");
    printlnBoth("  status_ms 500     状态打印周期，单位 ms");
    printlnBoth("  rc_enable 1       启用遥控器控制（0 关闭，恢复串口控制）");
    printlnBoth("  rc_debug 1        打印遥控脉宽/混控调试信息");
    printlnBoth("  smooth 1          启用缓冲模式（加速度限制，防止瞬间冲出）");
    printlnBoth("  accel 50          缓冲模式加速度上限，单位 %/s（越小越柔和）");
    printlnBoth("  decel 200         缓冲模式减速度上限，单位 %/s（越大刹车越快）");
    printlnBoth();
}

void printStatus() {
    const bool smooth_on = param_smooth_enable.read() > 0.5f;
    const bool rc_on     = param_rc_enable.read() > 0.5f;
    printfBoth(
        "[STATUS] tgt=[%.1f %.1f %.1f %.1f] out=[%.1f %.1f %.1f %.1f] "
        "| mode=%s%s | accel=%.0f decel=%.0f%%/s arm_ms=%.0f\n",
        motorTargets[MOTOR_1], motorTargets[MOTOR_2],
        motorTargets[MOTOR_3], motorTargets[MOTOR_4],
        motorTargetsSmoothed[MOTOR_1], motorTargetsSmoothed[MOTOR_2],
        motorTargetsSmoothed[MOTOR_3], motorTargetsSmoothed[MOTOR_4],
        rc_on ? "RC" : "SERIAL",
        smooth_on ? "+SMOOTH" : "",
        param_accel_limit.read(), param_decel_limit.read(), param_arm_ms.read()
    );
}

void onParamChange(String name, float value) {
    if (name == "f") {
        commandForward(value == 1.0f ? DEFAULT_DRIVE_SPEED : value);
    } else if (name == "b") {
        commandBackward(value == 1.0f ? DEFAULT_DRIVE_SPEED : value);
    } else if (name == "l") {
        commandLeft(value == 1.0f ? DEFAULT_DRIVE_SPEED : value);
    } else if (name == "r") {
        commandRight(value == 1.0f ? DEFAULT_DRIVE_SPEED : value);
    } else if (name == "s") {
        commandStop();
    } else if (name == "all") {
        setAllMotorTargets(value);
    } else if (name == "m1") {
        motorTargets[MOTOR_1] = clampPercent(value);
    } else if (name == "m2") {
        motorTargets[MOTOR_2] = clampPercent(value);
    } else if (name == "m3") {
        motorTargets[MOTOR_3] = clampPercent(value);
    } else if (name == "m4") {
        motorTargets[MOTOR_4] = clampPercent(value);
    }
    printfBoth("[PARAM] %s = %.3f\n", name.c_str(), value);
}

void serviceArmCommand() {
    // 严格上升沿触发：仅在 "低->高" 跳变时执行一次 arm
    const bool arm_request = param_arm.read() > ARM_TRIGGER_THRESHOLD;
    if (arm_request && !arm_latched) {
        arm_latched = true;
        armAllMotors();
    } else if (!arm_request && arm_latched) {
        arm_latched = false;
    }
}

// 遥控通道读取 + 锁定更新，返回两通道当前脉宽（us），失败返回 false
static bool readRcChannels(uint16_t& ch1_us, uint16_t& ch3_us) {
    uint32_t ch1_update = 0, ch3_update = 0;
    const bool ch1_ok = rc_ch1.read(ch1_us, ch1_update);
    const bool ch3_ok = rc_ch3.read(ch3_us, ch3_update);
    if (ch1_ok) rc_ch1.updateLock(ch1_update);
    if (ch3_ok) rc_ch3.updateLock(ch3_update);
    return ch1_ok && ch3_ok && rc_ch1.isLocked() && rc_ch3.isLocked();
}

// 纯调试输出：与 rc_enable 解耦，只要 rc_debug=1 就打印
static void serviceRcDebugPrint() {
    if (param_rc_debug.read() <= 0.5f) return;
    if (millis() - last_rc_debug_ms < 200) return;
    last_rc_debug_ms = millis();

    uint16_t ch1_us = 0, ch3_us = 0;
    uint32_t ch1_upd = 0, ch3_upd = 0;
    const bool ch1_ok = rc_ch1.read(ch1_us, ch1_upd);
    const bool ch3_ok = rc_ch3.read(ch3_us, ch3_upd);
    if (ch1_ok) rc_ch1.updateLock(ch1_upd);
    if (ch3_ok) rc_ch3.updateLock(ch3_upd);

    const float turn_norm     = ch1_ok ? HotRC_Channel::toNormalized(ch1_us) : 0.0f;
    const float throttle_norm = ch3_ok ? HotRC_Channel::toNormalized(ch3_us) : 0.0f;

    printfBoth(
        "[RC] ch1=%4uus%s  ch3=%4uus%s  | turn=%+.2f thr=%+.2f | lock[%d,%d]\n",
        ch1_ok ? ch1_us : 0, ch1_ok ? "" : "(X)",
        ch3_ok ? ch3_us : 0, ch3_ok ? "" : "(X)",
        turn_norm, throttle_norm,
        rc_ch1.isLocked(), rc_ch3.isLocked()
    );
}

// 遥控模式：读取两通道 → 混控到四电机
void serviceRcControl() {
    if (param_rc_enable.read() <= 0.5f) return;

    uint16_t ch1_us = 0, ch3_us = 0;
    const bool rc_ready = readRcChannels(ch1_us, ch3_us);

    if (!rc_ready) {
        // 失控保护：信号丢失立即停车
        setAllMotorTargets(0.0f);
        return;
    }

    // 归一化到 -1.0~+1.0（含死区），再按幅度缩放
    const float turn     = HotRC_Channel::toNormalized(ch1_us) * RC_TURN_SCALE;
    const float throttle = HotRC_Channel::toNormalized(ch3_us) * RC_THROTTLE_SCALE;

    // 混控（符号模式匹配现有 commandForward/Right）
    const float m1 = -throttle - turn;
    const float m2 = -throttle - turn;
    const float m3 = +throttle - turn;
    const float m4 = +throttle - turn;
    setMixedMotorTargets(m1, m2, m3, m4);
}

// 标量斜率限制：current 向 target 逼近，每秒最大变化 max_delta_per_s
static inline float slewTowards(float current, float target, float max_delta_per_s, float dt_s) {
    const float max_step = max_delta_per_s * dt_s;
    const float diff = target - current;
    if (diff > max_step)  return current + max_step;
    if (diff < -max_step) return current - max_step;
    return target;
}

static inline bool isOppositeDirection(float current, float target) {
    return (current > 0.0f && target < 0.0f) || (current < 0.0f && target > 0.0f);
}

// 加速和减速分离：反向时先减到 0，再按加速斜率进入反方向。
static inline float slewTowardsWithAccelDecel(
    float current,
    float target,
    float accel_per_s,
    float decel_per_s,
    float dt_s
) {
    if (isOppositeDirection(current, target)) {
        return slewTowards(current, 0.0f, decel_per_s, dt_s);
    }

    const bool speeding_up = fabsf(target) > fabsf(current);
    return slewTowards(current, target, speeding_up ? accel_per_s : decel_per_s, dt_s);
}

// 根据当前模式更新 motorTargetsSmoothed[]
//   - smooth 关：直接跟随 motorTargets（瞬时响应）
//   - smooth 开：按 accel 限制每秒变化率，平滑逼近 motorTargets
static void updateSmoothedTargets(uint32_t dt_ms) {
    const bool smooth_on = param_smooth_enable.read() > 0.5f;
    if (!smooth_on) {
        for (uint8_t i = 0; i < MOTOR_COUNT; ++i) {
            motorTargetsSmoothed[i] = motorTargets[i];
        }
        return;
    }
    const float accel = max(param_accel_limit.read(), 1.0f);   // 防 0
    const float decel = max(param_decel_limit.read(), 1.0f);   // 防 0
    const float dt_s  = (float)dt_ms * 0.001f;
    for (uint8_t i = 0; i < MOTOR_COUNT; ++i) {
        motorTargetsSmoothed[i] = slewTowardsWithAccelDecel(
            motorTargetsSmoothed[i], motorTargets[i], accel, decel, dt_s);
    }
}

void serviceMotorOutputs() {
    const uint32_t now = millis();
    const uint32_t dt_ms = now - last_dshot_send_ms;
    if (dt_ms < DSHOT_UPDATE_INTERVAL_MS) {
        return;
    }
    last_dshot_send_ms = now;

    updateSmoothedTargets(dt_ms);

    for (uint8_t i = 0; i < MOTOR_COUNT; ++i) {
        motors[i].setOutputEnabled(true);
        motors[i].setThrottle(motorTargetsSmoothed[i]);
        motors[i].update();
    }
}

void servicePeriodicStatus() {
    const uint32_t period_ms = (uint32_t)max(param_status_ms.read(), MIN_STATUS_PERIOD_MS);
    if (millis() - last_status_ms < period_ms) {
        return;
    }
    last_status_ms = millis();
    printStatus();
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    Serial0.begin(SERIAL_BAUD, SERIAL_8N1, UART0_RX_PIN, UART0_TX_PIN);
    delay(500);

    printlnBoth();
    printlnBoth("╔════════════════════════════════════════╗");
    printlnBoth("║     AM32 四电机调参测试程序           ║");
    printlnBoth("╚════════════════════════════════════════╝");
    printlnBoth("M1=GPIO9  M2=GPIO10  M3=GPIO11  M4=GPIO12");

    VOFA_float::add_on_value_change_callback(onParamChange);
    VOFA_float::setup(Serial0, &Serial);   // 主流=UART0（无线串口），辅流=USB CDC

    // 遥控器通道初始化
    rc_ch1.begin();
    rc_ch3.begin();
    printfBoth("[RC] CH1(left/right)=GPIO%d  CH3(fwd/back)=GPIO%d  (rc_enable 1 启用)\n",
               RC_CH1_PIN, RC_CH3_PIN);

    for (uint8_t i = 0; i < MOTOR_COUNT; ++i) {
        if (!motors[i].begin()) {
            printfBoth("[FATAL] motor %u init failed\n", i + 1);
            while (true) {
                delay(1000);
            }
        }
    }

    armAllMotors();
    setAllMotorTargets(0.0f);
    printHelp();
    printStatus();
}

void loop() {
    serviceArmCommand();
    serviceRcControl();
    serviceRcDebugPrint();
    serviceMotorOutputs();
    servicePeriodicStatus();
}
