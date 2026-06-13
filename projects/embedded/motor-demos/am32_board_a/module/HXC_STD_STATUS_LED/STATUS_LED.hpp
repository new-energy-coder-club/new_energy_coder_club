/*
 * @version: no version
 * @LastEditors: qingmeijiupiao
 * @Description: HXC统一状态LED控制器
 * @author: 
 * @LastEditTime: 2025-05-15 15:35:14
 * @relay: HXCthread
 */
#ifndef STATUS_LED_HPP
#define STATUS_LED_HPP

#include <HXCthread.hpp>

class STATUS_LED {
public:
    /**
     * @brief LED状态枚举
     */
    enum class State {
        NORMAL,          // 正常工作情况 - 呼吸灯效果
        CAN_OFFLINE,     // CAN离线 - 一次快闪
        DEVICE_OFFLINE,  // 传感器或者设备异常 - 常亮
        ERROR            // 其他异常 - 二次快闪
    };

    /**
     * @brief 构造函数
     * @param pin LED控制引脚
     * @param pwmChannel PWM通道(默认0)
     * @param pwmFreq PWM频率(默认1000Hz)
     * @param pwmResolution PWM分辨率(默认8位)
     */
    LED(uint8_t pin, 
        uint8_t pwmChannel = 0, 
        uint32_t pwmFreq = 1000, 
        uint8_t pwmResolution = 8)
        : pin_(pin), 
          pwmChannel_(pwmChannel),
          pwmFreq_(pwmFreq),
          pwmResolution_(pwmResolution),
          currentState_(State::NORMAL) {}

    /**
     * @brief 初始化LED控制器
     */
    void begin() {
        // 初始化PWM通道
        ledcSetup(pwmChannel_, pwmFreq_, pwmResolution_);
        ledcAttachPin(pin_, pwmChannel_);
        
        // 初始状态设置为NORMAL
        setState(State::NORMAL);
    }

    /**
     * @brief 设置LED状态
     * @param state 要设置的状态
     */
    void setState(State state) {
        if (state == currentState_) return;

        stopCurrentState();
        currentState_ = state;
        startStateThread(state);
    }

    /**
     * @brief 获取当前LED状态
     * @return 当前状态
     */
    State getState() const {
        return currentState_;
    }

    /**
     * @brief 停止所有LED效果
     */
    void turnOff() {
        stopCurrentState();
        ledcWrite(pwmChannel_, 0);
    }

private:
    // 停止当前状态线程
    void stopCurrentState() {
        if (currentThread_) {
            currentThread_->stop();
            currentThread_ = nullptr;
        }
    }

    // 启动对应状态的线程
    void startStateThread(State state) {
        switch (state) {
            case State::NORMAL:
                currentThread_ = &normalThread_;
                break;
            case State::CAN_OFFLINE:
                currentThread_ = &canOfflineThread_;
                break;
            case State::DEVICE_OFFLINE:
                currentThread_ = &deviceOfflineThread_;
                break;
            case State::ERROR:
                currentThread_ = &errorThread_;
                break;
        }
        currentThread_->start(pin_);
    }

    // PWM参数
    const uint8_t pin_;
    const uint8_t pwmChannel_;
    const uint32_t pwmFreq_;
    const uint8_t pwmResolution_;

    // 当前状态
    State currentState_;
    HXC::thread<uint8_t>* currentThread_ = nullptr;

    // 各种状态线程
    HXC::thread<uint8_t> normalThread_ = HXC::thread<uint8_t>(
        [this](uint8_t pin) {
            while (true) {
                // 呼吸灯效果
                for (uint8_t i = 0; i < 50; i++) {
                    ledcWrite(pwmChannel_, i);
                    delay(10);
                }
                for (uint8_t i = 49; i > 0; i--) {
                    ledcWrite(pwmChannel_, i);
                    delay(10);
                }
            }
        }
    );

    HXC::thread<uint8_t> canOfflineThread_ = HXC::thread<uint8_t>(
        [this](uint8_t pin) {
            while (true) {
                // 一次快闪效果
                ledcWrite(pwmChannel_, 150);
                delay(500);
                ledcWrite(pwmChannel_, 0);
                delay(500);
            }
        }
    );

    HXC::thread<uint8_t> deviceOfflineThread_ = HXC::thread<uint8_t>(
        [this](uint8_t pin) {
            while (true) {
                // 常亮效果
                ledcWrite(pwmChannel_, 150);
                delay(100); // 小延迟防止线程占用过高CPU
            }
        }
    );

    HXC::thread<uint8_t> errorThread_ = HXC::thread<uint8_t>(
        [this](uint8_t pin) {
            while (true) {
                // 二次快闪效果
                for (int i = 0; i < 2; i++) {
                    ledcWrite(pwmChannel_, 150);
                    delay(100);
                    ledcWrite(pwmChannel_, 0);
                    delay(100);
                }
                delay(1000);
            }
        }
    );
};

#endif // STATUS_LED_HPP