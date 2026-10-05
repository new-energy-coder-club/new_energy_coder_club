/*
 * @Description: 
 * @Author: qingmeijiupiao
 * @Date: 2024-07-15 22:17:54
 */
#include "ESPNOW.hpp"

void test2(HXC_ESPNOW_data_pakage package){
    Serial.println("receive test2 data");
}

void setup() {
    //调试串口初始化
    Serial.begin(115200);

    //ESP-NOW初始化
    esp_now_setup();

    //使用lamda添加回调
    add_esp_now_callback("test",[](HXC_ESPNOW_data_pakage package){
      Serial.println("receive test data");
    })

    //使用函数添加回调
    add_esp_now_callback("test2",test2);
    
}
void loop() {
    uint8_t data[3] = {1,2,3};
    //通过espnow发送名称为test的数据包
    esp_now_send_package("test",data,sizeof(data),broadcastMacAddress);
    delay(100);
}