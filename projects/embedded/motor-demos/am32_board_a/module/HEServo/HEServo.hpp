#ifndef HESERVO_HPP
#define HESERVO_HPP
#include "HardwareSerial.h"
#include <Arduino.h>
#define HE_SERVO_FRAME_HEADER         0x55
#define HE_SERVO_MOVE_TIME_WRITE      1
#define HE_SERVO_MOVE_TIME_READ       2
#define HE_SERVO_MOVE_TIME_WAIT_WRITE 7
#define HE_SERVO_MOVE_TIME_WAIT_READ  8
#define HE_SERVO_MOVE_START           11
#define HE_SERVO_MOVE_STOP            12
#define HE_SERVO_ID_WRITE             13
#define HE_SERVO_ID_READ              14
#define HE_SERVO_ANGLE_OFFSET_ADJUST  17
#define HE_SERVO_ANGLE_OFFSET_WRITE   18
#define HE_SERVO_ANGLE_OFFSET_READ    19
#define HE_SERVO_ANGLE_LIMIT_WRITE    20
#define HE_SERVO_ANGLE_LIMIT_READ     21
#define HE_SERVO_VIN_LIMIT_WRITE      22
#define HE_SERVO_VIN_LIMIT_READ       23
#define HE_SERVO_TEMP_MAX_LIMIT_WRITE 24
#define HE_SERVO_TEMP_MAX_LIMIT_READ  25
#define HE_SERVO_TEMP_READ            26
#define HE_SERVO_VIN_READ             27
#define HE_SERVO_POS_READ             28
#define HE_SERVO_OR_MOTOR_MODE_WRITE  29
#define HE_SERVO_OR_MOTOR_MODE_READ   30
#define HE_SERVO_LOAD_OR_UNLOAD_WRITE 31
#define HE_SERVO_LOAD_OR_UNLOAD_READ  32
#define HE_SERVO_LED_CTRL_WRITE       33
#define HE_SERVO_LED_CTRL_READ        34
#define HE_SERVO_LED_ERROR_WRITE      35
#define HE_SERVO_LED_ERROR_READ       36
#define MAX_TIME 300 
class HEServo
{
public:
    HEServo(HardwareSerial *sl,uint8_t id){
        this->serial = sl;
        this->id = id;
    };
    // HEServo(uint8_t id){
    //     this->serial = &Serial;
    //     this->id = id;
    // };
    HEServo(){

    };
    ~HEServo(){};
    //angle：角度，范围:0~240度） time:时间，范围：0~30000毫秒
    void SERVO_MOVE_TIME_WRITE(float angle, unsigned short int time=0){
        /*指令名SERVO_MOVE_TIME_WRITE指令值1数据长度7：
        参数1：角度的低八位。
        参数2：角度的高八位。范围0~1000，对应舵机角度的0~240°，即舵机可变化
        的最小角度为0.24度。
        参数3：时间低八位。
        参数4：时间高八位，时间的范围0~30000毫秒。该命令发送给舵机，舵机将
        在参数时间内从当前角度匀速转动到参数角度。该指令到达舵机后，舵机会立
        即转动*/

        angle=fmod(angle,360);

        uint16_t anl=(1000*angle)/240;
 
        uint8_t data[8] = {this->id,7,HE_SERVO_MOVE_TIME_WRITE,anl&0xff,anl>>8,time&0xff,time>>8,0};
        this->add_checksum(data);
        this->send(data);
    }

    void SERVO_MOVE_TIME_READ(uint8_t* rdata,float angle, unsigned short int time=0){
        /*指令名SERVO_MOVE_TIME_READ指令值2数据长度3：
        读取指令名SERVO_MOVE_TIME_WRITE 发送给舵机的角度和时间值*/
        uint16_t anl=1000*angle/240;
        uint8_t data[8] = {this->id,7,HE_SERVO_MOVE_TIME_READ,anl&0xff,anl>>8,time&0xff,time>>8,0};
        this->add_checksum(data);
        this->send(data);

        int rangle=0;
        int rtime=0;
        uint8_t r_data[8]={0,0,0,0,0,0,0};
        this->read(r_data,7);
        if (r_data[0] == this->id && r_data[2] == HE_SERVO_MOVE_TIME_READ){
            for (int i = 0; i < r_data[1]; i++){
                rdata[i] = r_data[i];
            }
        }
    }
    void SERVO_MOVE_TIME_WAIT_WRITE(float angle, int time=0){
        /*该指令跟第 1点中SERVO_MOVE_TIME_WRITE 指令功能相似，不同的是该指令到达舵机后，舵机
        不会立即转动，需要等待指令名SERVO_MOVE_START指令值为11的指令送达
        舵机后，舵机才会转动，将在参数时间内从当前角度匀速转动到参数角度*/
        
        angle=fmod(angle,240);

        uint16_t anl=(1000*angle)/240;
 
        uint8_t data[8] = {this->id,7,HE_SERVO_MOVE_TIME_WAIT_WRITE,anl&0xff,anl>>8,time&0xff,time>>8,0};
        this->add_checksum(data);
        this->send(data);
    }

    void SERVO_MOVE_START(){
        /*配合指令SERVO_MOVE_TIME_WAIT_WRITE使用*/
        uint8_t data[4] = {this->id,3,HE_SERVO_MOVE_START,0};
        this->add_checksum(data);
        this->send(data);
    }
    void SERVO_MOVE_STOP(){
        /*该指令到达舵机，如果舵机正在转动，就会立即停止转动。停在当前角度位置。*/
        uint8_t data[4] = {this->id,3,HE_SERVO_MOVE_STOP,0};
        this->add_checksum(data);
        this->send(data);
    }
    void SERVO_ID_WRITE(uint8_t id){
        /*该指令可以改变舵机的ID号*/
        if(id>=253)
            return ;
        uint8_t data[5] = {this->id,4,HE_SERVO_ID_WRITE,id,0};
        this->add_checksum(data);
        this->send(data);
    }
    uint8_t SERVO_ID_READ(){
        //读取舵机的ID值
        uint8_t data[4] = {254,3,HE_SERVO_ID_READ,0};
        this->add_checksum(data);
        this->send(data);
        uint8_t r_data[5]={0,0,0,0,0};
        this->read(r_data,5);
        return r_data[3];
    }
    int SERVO_TEMP_READ(){
        //读取舵机内部实时温度
        uint8_t data[4] = {this->id,3,HE_SERVO_TEMP_READ,0};
        this->add_checksum(data);
        this->send(data);
        uint8_t r_data[5]={0,0,0,0,0};
        this->read(r_data,5);
        return r_data[3];
    }
    int SERVO_VIN_READ(){
        //读取舵机内部电压
        uint8_t data[4] = {this->id,3,HE_SERVO_VIN_READ,0};
        this->add_checksum(data);
        this->send(data);
        uint8_t r_data[6]={0,0,0,0,0,0};
        this->read(r_data,6);
        return r_data[4]<<8 | r_data[3];
    }
    int16_t SERVO_POS_READ(){
        //读取舵机当前角度
        uint8_t data[4] = {this->id,3,HE_SERVO_POS_READ,0};
        this->add_checksum(data);
        this->send(data);
        uint8_t r_data[6]={0,0,0,0,0,0};
        this->read(r_data,6);
        return (r_data[4]<<8)+r_data[3];
    }
    float SERVO_ANGLE_READ(){
        //读取舵机当前角度
        return 360.0*SERVO_POS_READ()/1500;
    }
    void SERVO_OR_MOTOR_MODE_WRITE(bool motor_mode=false,int16_t motor_speed=0){
        if(abs(motor_speed)>1000){
            motor_speed=1000*motor_speed/abs(motor_speed);
        }

        //设置舵机或者减速电机模式
        uint8_t data[8] = {this->id,3,HE_SERVO_OR_MOTOR_MODE_WRITE,motor_mode,0,motor_speed&0xff,motor_speed>>8,0};
        this->add_checksum(data);
        this->send(data);
    }
    void SERVO_LOAD_OR_UNLOAD_WRITE(bool load){
        /*舵机内部电机是否卸载掉电，范围0或1，0代表卸载掉电，此时舵机
        无力矩输出。1代表装载电机，此时舵机有力矩输出，默认值0。*/
        uint8_t data[5] = {this->id,4,HE_SERVO_LOAD_OR_UNLOAD_WRITE,load,0};
        this->add_checksum(data);
        this->send(data);
    }
    bool SERVO_LOAD_OR_UNLOAD_READ(){
        //读取舵机内部电机的状态
        uint8_t data[4] = {this->id,3,HE_SERVO_LOAD_OR_UNLOAD_READ,0};
        this->add_checksum(data);
        this->send(data);
        uint8_t r_data[5]={0,0,0,0,0};
        this->read(r_data,5);
        return r_data[3];
    }
protected:

    //发送数据
    virtual void send(uint8_t *data){
        //写入固定包头
        this->serial->write(0x55);
        this->serial->write(0x55);
        //写入数据
        for (int i = 0; i < data[1]+1; i++){
            this->serial->write(data[i]);
        }
        delay(1);
    };
    //读取数据
    virtual void read(uint8_t *data,uint8_t len){
        delay(1);   
        for (int i = 0; i < MAX_TIME; i++){
            if (this->serial->available()){
                data[0]=this->serial->read();
                if (data[0] == this->id){
                    for (int j = 1; j < len; j++){
                        data[j]=this->serial->read();
                    }
                    break;
                }
            }
        }
    }
    //计算校验码
    void add_checksum(uint8_t *data){
        uint8_t len=data[1];
        uint8_t checksum = 0;
        for (uint8_t i = 0; i < len; i++)
        {
            checksum += data[i];
        }

        data[len] = ~checksum;
    };
    //求余
    float fmod(double a,double b){
        return a-b*floor(a/b);
    };
    uint8_t id;
    HardwareSerial *serial;
};
#endif