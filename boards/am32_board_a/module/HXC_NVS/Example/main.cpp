/*
 * @LastEditors: qingmeijiupiao
 * @Description:HXC线程库示例
 * @Author: qingmeijiupiao
 * @Date: 2024-10-17 22:00:39
 */
#include <Arduino.h>
#include "HXC_NVS.hpp"

//注意key长度不能超过15字节，并且不能重复

HXC::NVS_DATA<int> int_value(/*key=*/"test",/*default_value=*/0);

HXC::NVS_DATA<double> double_value(/*key=*/"test1",/*default_value=*/0.0);

//字符串只能使用String类型
HXC::NVS_DATA<String> string_value(/*key=*/"test2",/*default_value=*/"hello");
void setup() {

    Serial.begin(115200);

    // 赋值时变量会自动保存到NVS储存
    int_value=10;

    //double_value=9.6;

    //string_value="world";

}

void loop() {
    // 读取时变量会自动从NVS储存读取

    Serial.println(int_value);

    Serial.println(double_value);

    Serial.println(string_value);
    delay(1000);
}


