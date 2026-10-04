/*
 * @Description: 
 * @Author: qingmeijiupiao
 * @Date: 2024-07-15 22:17:54
 */
#include "SBUS.hpp"
#include <Arduino.h>
SBUS YourReceiver(6, &Serial2);//指定引脚和串口
void setup() {
    YourReceiver.setup();
    Serial.begin(115200);//调试串口初始化
}
void loop() {
    if (YourReceiver.get_flag()) {
        for (int i = 1; i <= 16; i++) {
            Serial.print("Channel %d :", i);
            Serial.print(YourReceiver[i]);//打印通道数据，[]运算符重载过
            Serial.print(",");
        }
        Serial.println();
    }
    delay(500);
}