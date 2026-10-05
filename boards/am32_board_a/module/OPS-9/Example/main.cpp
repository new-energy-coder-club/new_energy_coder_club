/*
 * @Description: 
 * @Author: qingmeijiupiao
 * @Date: 2024-07-15 22:10:36
 */
#include"ops9.hpp"
#include<Arduino.h>

hardwareSerial ops9serial(1);//esp32 dev 和s3有0 1 2三个串口这里指定使用串口1

void setup() {
    ops9 Ops9Sensor(&ops9serial);//指定使用串口
    Ops9Sensor.setup(/*TX=*/2, /*RX=*/3);//指定串口引脚
    Serial.begin(115200);//初始化调试串口

    while(Ops9Sensor.getX()==0){
        Serial.println("等待ops9初始化");
        delay(1000);
    }
}
void loop() {
    Serial.print("X: ");
    Serial.print(Ops9Sensor.getX());
    Serial.print("Y: ");
    Serial.print(Ops9Sensor.getY());
    Serial.print("Yaw: ");
    Serial.print(Ops9Sensor.getYaw());
    Serial.print("pitch: ");
    Serial.print(Ops9Sensor.getPitch());
    Serial.print("roll: ");
    Serial.println(Ops9Sensor.getRoll());
    delay(1000);
}