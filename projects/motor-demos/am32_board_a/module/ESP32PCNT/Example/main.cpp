#include "HXCEncoder.hpp"

HXC::Encoder encoder(/*PINA=*/2,/*PINB=*/1);

void setup() {
    //调试串口初始化
    Serial.begin(115200);
    encoder.setup();//初始化

    //encoder.set_filter(100);//设置脉冲去抖动滤波器的时间常数,单位纳秒

}
void loop() {
    Serial.print(encoder.get_count());
    Serial.print(",");
    Serial.println(encoder.get_speed());
    delay(300);
}