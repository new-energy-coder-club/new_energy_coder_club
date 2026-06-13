/*
 * @LastEditors: qingmeijiupiao
 * @Description:HXC线程库示例
 * @Author: qingmeijiupiao
 * @Date: 2024-10-17 22:00:39
 */
#include <Arduino.h>
#include "HXCthread.hpp"
#include <tuple>

void task_func(std::tuple<int,float,const char*> param) {
    int param1 = std::get<0>(param);
    float param2 = std::get<1>(param);
    const char* param3 = std::get<2>(param);
    while (1){
        Serial.println("task_func1");
        Serial.print("param:  ");
        Serial.print(param1);
        Serial.print(",");
        Serial.print(param2);
        Serial.print(",");
        Serial.println(param3);
        delay(1000);
    }
};
 
//线程1
HXC::thread<std::tuple<int,float,const char*>> thread1(task_func);  

//线程2
HXC::thread<void> thread2([](){

    while (1){
        Serial.println("task_func2");
        
        delay(1000);
    }
});

void setup() {

    Serial.begin(115200);

    //启动线程1
    thread1.start(std::make_tuple(1,3.14,"hello"));

    //启动线程2
    thread2.start("task2");

}

void loop() {
    delay(1000);
}


