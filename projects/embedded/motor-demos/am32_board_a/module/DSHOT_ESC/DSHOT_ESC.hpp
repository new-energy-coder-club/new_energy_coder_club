/*
 * @Description: DSHOT300 / AM32 电调驱动库（ESP32-S3 RMT, IDF 4.x API）
 * @Platform:    HXC-A (ESP32-S3-WROOM-1-N16R8), Arduino-ESP32 v3.x
 */

#pragma once
#ifndef DSHOT_ESC_HPP
#define DSHOT_ESC_HPP

#include <Arduino.h>
#include "driver/rmt.h"

// ─── RMT 时钟 & DSHOT300 时序参数 ─────────────────────────────────────────
#define DSHOT_RMT_CLK_DIV   1

#define DSHOT300_T1H        200
#define DSHOT300_T1L        66
#define DSHOT300_T0H        100
#define DSHOT300_T0L        166

// ─── 协议常量 ──────────────────────────────────────────────────────────────
#define DSHOT_THROTTLE_MIN      48
#define DSHOT_THROTTLE_MAX      2047
#define DSHOT_ARM_VALUE         0

#define DSHOT_CMD_DIRECTION_NORMAL   20
#define DSHOT_CMD_DIRECTION_REVERSE  21
#define DSHOT_CMD_REPEAT             15

#define DSHOT_FRAME_BITS             16
#define DSHOT_FRAME_ITEMS            17

#define AM32_DIRECTION_CHANGE_STOP_MS  150
#define AM32_DIRECTION_CHANGE_WAIT_MS  100

class DSHOT_ESC {
public:
    explicit DSHOT_ESC(
        gpio_num_t pin,
        rmt_channel_t channel = RMT_CHANNEL_0,
        Print* logger = &Serial
    )
        : _pin(pin), _channel(channel), _logger(logger) {}

    ~DSHOT_ESC() { deinit(); }

    bool begin() {
        if (_initialized) {
            return true;
        }

        rmt_config_t config = {};
        config.rmt_mode = RMT_MODE_TX;
        config.channel = _channel;
        config.gpio_num = _pin;
        config.clk_div = DSHOT_RMT_CLK_DIV;
        config.mem_block_num = 1;
        config.tx_config.loop_en = false;
        config.tx_config.carrier_en = false;
        config.tx_config.idle_output_en = true;
        config.tx_config.idle_level = RMT_IDLE_LEVEL_LOW;

        esp_err_t err = rmt_config(&config);
        if (err != ESP_OK) {
            logf("[DSHOT] GPIO%d ch%d rmt_config failed: %s\n",
                 (int)_pin, (int)_channel, esp_err_to_name(err));
            return false;
        }

        err = rmt_driver_install(_channel, 0, 0);
        if (err != ESP_OK) {
            logf("[DSHOT] GPIO%d ch%d rmt_driver_install failed: %s\n",
                 (int)_pin, (int)_channel, esp_err_to_name(err));
            return false;
        }

        _initialized = true;
        logf("[DSHOT] GPIO%d ch%d init ok\n", (int)_pin, (int)_channel);
        return true;
    }

    void deinit() {
        if (!_initialized) {
            return;
        }
        rmt_driver_uninstall(_channel);
        _initialized = false;
    }

    void sendThrottle(uint16_t throttle, bool telemetry = false) {
        if (throttle > DSHOT_THROTTLE_MAX) {
            throttle = DSHOT_THROTTLE_MAX;
        }
        const uint16_t packet = buildPacket(throttle, telemetry);
        encodeFrame(packet);
        transmit();
    }

    void sendThrottlePercent(float percent) {
        sendThrottle(throttlePercentToValue(percent));
    }

    void stop() {
        sendThrottle(DSHOT_ARM_VALUE);
    }

    void arm(uint32_t ms = 1000) {
        logf("[DSHOT] GPIO%d arm %lums\n", (int)_pin, ms);
        const uint32_t start = millis();
        while (millis() - start < ms) {
            stop();
            delay(1);
        }
    }

    void setDirection(bool reverse, int repeat = DSHOT_CMD_REPEAT) {
        const uint16_t cmd = reverse ? DSHOT_CMD_DIRECTION_REVERSE
                                     : DSHOT_CMD_DIRECTION_NORMAL;
        for (int i = 0; i < repeat; ++i) {
            sendThrottle(cmd);
            delay(1);
        }
        logf("[DSHOT] GPIO%d direction=%s\n", (int)_pin, reverse ? "reverse" : "forward");
    }

    static uint16_t throttlePercentToValue(float percent) {
        if (percent <= 0.0f) {
            return DSHOT_ARM_VALUE;
        }
        if (percent > 100.0f) {
            percent = 100.0f;
        }
        return static_cast<uint16_t>(
            DSHOT_THROTTLE_MIN +
            (percent / 100.0f) * (DSHOT_THROTTLE_MAX - DSHOT_THROTTLE_MIN)
        );
    }

    bool initialized() const { return _initialized; }
    gpio_num_t pin() const { return _pin; }
    rmt_channel_t channel() const { return _channel; }

private:
    uint16_t buildPacket(uint16_t throttle, bool telemetry) const {
        const uint16_t data = (throttle << 1) | (telemetry ? 1 : 0);
        const uint16_t crc = (data ^ (data >> 4) ^ (data >> 8)) & 0x0F;
        return (data << 4) | crc;
    }

    void encodeFrame(uint16_t packet) {
        for (int i = 0; i < DSHOT_FRAME_BITS; ++i) {
            const bool bit = (packet >> (DSHOT_FRAME_BITS - 1 - i)) & 1;
            if (bit) {
                _items[i].duration0 = DSHOT300_T1H;
                _items[i].level0 = 1;
                _items[i].duration1 = DSHOT300_T1L;
                _items[i].level1 = 0;
            } else {
                _items[i].duration0 = DSHOT300_T0H;
                _items[i].level0 = 1;
                _items[i].duration1 = DSHOT300_T0L;
                _items[i].level1 = 0;
            }
        }

        _items[DSHOT_FRAME_BITS].duration0 = 0;
        _items[DSHOT_FRAME_BITS].level0 = 0;
        _items[DSHOT_FRAME_BITS].duration1 = 0;
        _items[DSHOT_FRAME_BITS].level1 = 0;
    }

    void transmit() {
        rmt_write_items(_channel, _items, DSHOT_FRAME_ITEMS, true);
        rmt_wait_tx_done(_channel, pdMS_TO_TICKS(10));
    }

    template <typename... Args>
    void logf(const char* format, Args... args) const {
        if (_logger != nullptr) {
            _logger->printf(format, args...);
        }
    }

    gpio_num_t _pin;
    rmt_channel_t _channel;
    Print* _logger;
    bool _initialized = false;
    rmt_item32_t _items[DSHOT_FRAME_ITEMS] = {};
};

// 方向切换状态机
enum class DirState : uint8_t {
    RUNNING,        // 正常运行
    STOP_WAIT,      // 切换前停车等待
    CMD_WAIT,       // 发送方向指令后等待生效
};

class AM32Motor {
public:
    explicit AM32Motor(
        gpio_num_t pin,
        rmt_channel_t channel = RMT_CHANNEL_0,
        Print* logger = &Serial
    )
        : _driver(pin, channel, logger), _logger(logger) {}

    bool begin() {
        return _driver.begin();
    }

    void arm(uint32_t ms = 1000) {
        _driver.arm(ms);
        _outputEnabled = false;
        _targetThrottlePercent = 0.0f;
        _dirState = DirState::RUNNING;
    }

    void stop() {
        _outputEnabled = false;
        _targetThrottlePercent = 0.0f;
        _driver.stop();
        _dirState = DirState::RUNNING;
    }

    void setOutputEnabled(bool enabled) {
        _outputEnabled = enabled;
        if (!enabled) {
            _driver.stop();
        }
    }

    // 只记录目标，不阻塞；方向切换由 update() 状态机驱动
    void setThrottle(float percent) {
        if (percent > 100.0f) percent = 100.0f;
        else if (percent < -100.0f) percent = -100.0f;

        _pendingReverse = percent < 0.0f;
        _targetThrottlePercent = fabsf(percent);

        // 如果需要切换方向且当前不在切换流程中，启动状态机
        if (_targetThrottlePercent > 0.0f &&
            _pendingReverse != _reverse &&
            _dirState == DirState::RUNNING) {
            _dirState = DirState::STOP_WAIT;
            _dirStateMs = millis();
        }
    }

    void setThrottlePercent(float percent) {
        setThrottle(percent);
    }

    // 非阻塞 update，每次 loop 调用一次
    void update() {
        if (!_outputEnabled) {
            _driver.stop();
            return;
        }

        switch (_dirState) {
            case DirState::STOP_WAIT:
                // 停车等待阶段：持续发 stop，计时到后发方向指令
                _driver.stop();
                if (millis() - _dirStateMs >= AM32_DIRECTION_CHANGE_STOP_MS) {
                    _driver.setDirection(_pendingReverse);
                    _dirState = DirState::CMD_WAIT;
                    _dirStateMs = millis();
                }
                break;

            case DirState::CMD_WAIT:
                // 指令等待阶段：继续发 stop，等待 ESC 响应
                _driver.stop();
                if (millis() - _dirStateMs >= AM32_DIRECTION_CHANGE_WAIT_MS) {
                    _reverse = _pendingReverse;
                    _dirState = DirState::RUNNING;
                }
                break;

            case DirState::RUNNING:
            default:
                if (_targetThrottlePercent <= 0.0f) {
                    _driver.stop();
                } else {
                    _driver.sendThrottlePercent(_targetThrottlePercent);
                }
                break;
        }
    }

    float targetThrottle() const { return _reverse ? -_targetThrottlePercent : _targetThrottlePercent; }
    float targetThrottleAbs() const { return _targetThrottlePercent; }
    bool isReverse() const { return _reverse; }
    bool outputEnabled() const { return _outputEnabled; }
    gpio_num_t pin() const { return _driver.pin(); }
    rmt_channel_t channel() const { return _driver.channel(); }

private:
    DSHOT_ESC _driver;
    Print* _logger = nullptr;
    bool _reverse = false;
    bool _pendingReverse = false;
    bool _outputEnabled = false;
    float _targetThrottlePercent = 0.0f;
    DirState _dirState = DirState::RUNNING;
    uint32_t _dirStateMs = 0;
};

#endif // DSHOT_ESC_HPP
