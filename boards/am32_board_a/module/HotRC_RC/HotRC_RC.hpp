/*
 * @Description: HotRC 遥控器独立 PWM 通道解码类
 * @Platform:    ESP32 / ESP32-S3 (Arduino framework)
 * @Note:        每个通道占一根信号线，50Hz 周期，1000~2000us 脉宽
 *               解码层复用自 HCX_A_N630 参考实现
 *               ISR 使用纯 C 风格全局函数（避免 ESP32 IRAM l32r 字面量池重定位异常）
 */

#pragma once

#include <Arduino.h>

class HotRC_Channel {
public:
    // 协议常量（宏形式，避免 ISR 内读 constexpr 字面量触发 l32r 问题）
    static constexpr uint16_t PWM_MIN_US        = 1000;
    static constexpr uint16_t PWM_CENTER_US     = 1500;
    static constexpr uint16_t PWM_MAX_US        = 2000;
    static constexpr uint16_t PWM_DEADBAND_US   = 60;
    static constexpr uint32_t TIMEOUT_MS        = 100;
    static constexpr uint8_t  LOCK_COUNT        = 3;

    // ISR 需要访问的共享数据（POD 结构体）
    struct Shared {
        uint8_t           pin;
        volatile uint32_t rise_time_us;
        volatile uint16_t pulse_width_us;
        volatile uint32_t last_update_us;
    };

    HotRC_Channel(uint8_t pin, const char* name)
        : _name(name) {
        _shared.pin = pin;
        _shared.rise_time_us   = 0;
        _shared.pulse_width_us = 0;
        _shared.last_update_us = 0;
    }

    void begin() {
        pinMode(_shared.pin, INPUT_PULLDOWN);
        attachInterruptArg(
            digitalPinToInterrupt(_shared.pin),
            &HotRC_Channel::isr_entry,
            &_shared,
            CHANGE
        );
    }

    bool read(uint16_t& pulse_width_us, uint32_t& last_update_us) const {
        noInterrupts();
        const uint16_t pulse  = _shared.pulse_width_us;
        const uint32_t update = _shared.last_update_us;
        interrupts();

        if (update == 0) return false;
        if (micros() - update > TIMEOUT_MS * 1000UL) return false;

        pulse_width_us = pulse;
        last_update_us = update;
        return true;
    }

    bool updateLock(uint32_t update_us) {
        if (update_us != _last_seen_update_us) {
            _last_seen_update_us = update_us;
            if (_valid_streak < 255) _valid_streak++;
        }
        if (!_locked && _valid_streak >= LOCK_COUNT) {
            _locked = true;
        }
        return _locked;
    }

    bool isLocked() const { return _locked; }
    const char* name() const { return _name; }
    uint8_t pin() const { return _shared.pin; }

    static float toNormalized(uint16_t pulse_us) {
        if (pulse_us > PWM_CENTER_US + PWM_DEADBAND_US) {
            const float ratio = (float)(pulse_us - (PWM_CENTER_US + PWM_DEADBAND_US))
                                / (float)(PWM_MAX_US - PWM_CENTER_US - PWM_DEADBAND_US);
            return constrain(ratio, 0.0f, 1.0f);
        }
        if (pulse_us < PWM_CENTER_US - PWM_DEADBAND_US) {
            const float ratio = (float)(pulse_us - (PWM_CENTER_US - PWM_DEADBAND_US))
                                / (float)(PWM_CENTER_US - PWM_DEADBAND_US - PWM_MIN_US);
            return constrain(ratio, -1.0f, 0.0f);
        }
        return 0.0f;
    }

    bool signal_present = false;

private:
    // ISR 入口：纯 POD 指针接口，字面量池与函数体自然邻近
    static void IRAM_ATTR isr_entry(void* arg);

    Shared            _shared;
    const char* const _name;
    uint32_t          _last_seen_update_us = 0;
    uint8_t           _valid_streak        = 0;
    bool              _locked              = false;
};

// ISR 实现放在类外 inline，让编译器按独立函数处理字面量
inline void IRAM_ATTR HotRC_Channel::isr_entry(void* arg) {
    HotRC_Channel::Shared* s = static_cast<HotRC_Channel::Shared*>(arg);
    if (digitalRead(s->pin)) {
        s->rise_time_us = micros();
        return;
    }
    const uint32_t now_us = micros();
    const uint32_t width  = now_us - s->rise_time_us;
    // 用字面量常量而非 constexpr，避免 IRAM 段字面量池布局问题
    if (width >= 500u && width <= 2500u) {
        s->pulse_width_us = static_cast<uint16_t>(width);
        s->last_update_us = now_us;
    }
}
