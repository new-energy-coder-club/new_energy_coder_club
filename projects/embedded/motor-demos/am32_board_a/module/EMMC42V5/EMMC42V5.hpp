#ifndef EMM_42_V5_HPP
#define EMM_42_V5_HPP
#include "HardwareSerial.h"
#include <Arduino.h>
#define MAX_RETRY 10 //最大重试次数
#define COMMAND_SUCCESS 1
#define COMMAND_FAIL 0
#define COMMAND_ERROR 2
#define NOT_RESPONSE 3
typedef int COMMAND_STATUS;//命令执行状态

//读取回零状态标志位返回结构体
struct  Return_to_zero_status_flag{
    bool is_valid_data=false;//数据有效
    bool encoder_ready;//编码器就绪
    bool calibration_ready;//校准表就绪
    bool is_zeroing;//正在回零
    bool is_zeroing_fail;//回零失败
};
//读取版本信息返回结构体
struct version_info{
    uint8_t software_version=0;//软件版本
    uint8_t hardware_version=0;//硬件版本
};

//读取相电阻和相电感返回结构体
struct Phase_resistance_inductance{
    uint16_t phase_resistance=0;//相电阻
    uint16_t phase_inductance=0;//相电感
};
//读取位置环PID参数返回结构体
struct PID_parameter{
    int Kp=0;
    int Ki=0;
    int Kd=0;
};
//读取原点回零参数返回结构体
struct REZREO_parameter{
    uint8_t mode=0;//回零模式
    uint8_t direction=0;//回零方向
    uint16_t speed=0;//回零转速
    int timeout=0;//回零超时时间
    uint16_t limit_speed=0;//无限位碰撞回零检测转速
    uint16_t limit_current=0;//无限位碰撞回零检测电流
    uint16_t limit_time=0; //无限位碰撞回零检测时间
    uint8_t auto_rezero=0;//是否使能上电自动触发回零功能
};
//读取电机状态标志位返回结构体
struct Motor_status_flag{
    bool is_enable=0;//电机使能状态标志位
    bool is_moving=0;//电机到位标志位
    bool is_blocked=0;//电机堵转标志位
    bool is_overload=0;//电机堵转保护标志
};
//读取读取驱动配置参数返回结构体
struct Driver_parameter{
    uint8_t motor_type=0;//电机类型 25为1.8°电机,50为0.9°电机
    uint8_t pulse_port_mode=0;//脉冲端口控制模式
    uint8_t comm_port_mode=0;//通讯端口复用模式
    uint8_t en_mode=0; //En 引脚的有效电平
    uint8_t dir_mode=0;//Dir 引脚的有效方向
    uint8_t resolution=0;//细分 = 0x10 = 16（如果返回0x00，则为256细分）
    uint8_t split=0; //细分插补功能
    uint8_t auto_screen=0;//自动熄屏功能
    uint16_t open_current=0;//开环模式工作电流
    uint16_t close_current=0;//闭环模式堵转时的最大电流
    uint16_t max_voltage=0;//闭环模式最大输出电压
    uint8_t baud_rate_mode=0;//串口波特率=0X05=115200（对应屏幕选项顺序：0x00为9600，...）;
    uint8_t CAN_rate_mode=0;//CAN 通讯速率 =0x07=500000（对应屏幕选项顺序：0x00为10000，...）;
    uint8_t ID_address=0;// ID 地址
    uint8_t comm_check_mode=0;    //通讯校验方式
    uint8_t control_command_response=0;//控制命令应答
    uint8_t brake_protection_enable=0;//堵转保护功能
    uint16_t brake_protection_speed=0;//堵转保护转速阈值
    uint16_t brake_protection_current=0;//堵转保护电流阈值
    uint16_t brake_protection_time=0;//堵转保护检测时间阈值 （堵转检测判定条件：电机实际转速 < 设置的堵转检测转速阈值 + 电机实际相电流 >设置的堵转检测相电流阈值 + 持续时间 > 设置的堵转检测时间阈值）
    //位置到达窗口//（表示当目标位置（你发送的位置角度）与传感器实际位置（传感器读取的位置角度）
    //相差小于0.1°时，认为电机已经到达设定的位置，将置位位置到达标志位，如果控制
    //命令应答设置为返回到位命令，则到位后将返回到位命令：地址 + FD + 9F + 6B）
};
//读取系统状态参数返回结构体
struct System_status{
    uint16_t voltage=0;//总线电压
    uint16_t current=0;//总线相电流
    uint16_t encoder=0;//校准后编码器值
    int64_t target_position=0;//电机目标位置
    int speed=0;//电机实时转速
    int64_t real_position=0;//电机实时位置
    int64_t position_error=0;//电机位置误差
    bool is_ready=0;//编码器就绪状态标志位
    bool is_calibrated=0;//校准表就绪状态标志位
    bool is_zeroing=0;//正在回零标志位
    bool is_zeroing_fail=0;//回零失败标志位
    bool is_enable=0;//使能状态标志位
    bool is_moving=0;//电机到位标志位
    bool is_blocked=0;//电机堵转标志位
    bool is_overload=0;//电机堵转保护标志

};
class EMMC42V5
{

public:
    EMMC42V5(HardwareSerial *sl,uint8_t id){
        this->serial = sl;
        this->id = id;
    };

    void setup(int bund_rate){
        this->serial->begin(bund_rate);

    };
    void setup(){
        this->serial->begin(115200);
    };
    //使能控制
    COMMAND_STATUS enable(bool is_enable,bool needsync=false,bool need_retry=false){
        // 命令功能：电机使能控制
        // 命令格式：地址 + 0xF3 + 0xAB + 使能状态 + 多机同步标志 + 校验字节
        // 命令返回：地址 + 0xF3 + 命令状态 + 校验字节
        // 命令示例：发送01 F3 AB 01 00 6B，正确返回01 F3 02 6B，条件不满足返回01 F3
        uint8_t data[6] = {this->id, 0xF3, 0xAB, is_enable, needsync, this->checksum};
        send(data,6);
        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE://错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return enable(is_enable,needsync,true);
                }
                return NOT_RESPONSE;
                break;
        };
    };
    //速度模式控制
    COMMAND_STATUS speed_control(int speed,uint8_t acce=0,bool needsync=false,bool need_retry=false){
        // 命令格式：地址 + 0xF6 + 方向 + 速度 + 加速度 + 多机同步标志 + 校验字节
        // 命令返回：地址 + 0xF6 + 命令状态 + 校验字节
        // 命令示例：发送01 F6 01 05 DC 0A 00 6B，命令正确返回01 F6 02 6B，条件不满
        // 足返回01 F6 E2 6B，错误命令返回01 00 EE 6B
        // （条件不满足情况：触发了堵转保护、电机没使能）
        // 数据解析：01表示旋转方向为CCW（00表示CW），05 DC表示速度为0x05DC =
        // 1500(RPM)，0A 表示加速度档位为0x0A=10，00表示不启用多机同步（01表示启用），
        // 如果需要多个电机同步开始运动，请参考“多机通讯及同步控制”章节；
        // 注意：加速度档位为0表示不使用曲线加减速，直接按照设定的速度运行。曲线加
        // 减速时间计算公式：t2- t1 = (256- acc) * 50(us)，Vt2 = Vt1 + 1(RPM)；
        // （注：acc为加速度档位，Vt1为t1时刻的转速，，Vt2为t2时刻的转速）
        bool direction = speed < 0;
        if(dir){
            direction=!direction;
        }
        u_int32_t s = abs(speed);
        uint8_t data[8] = {this->id, 0xF6, direction, (s>>8)&0xFF, s&0xFF,acce, needsync, this->checksum};
        send(data,8);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE://错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return speed_control(s,acce,needsync,true);
                }
                return NOT_RESPONSE;
                break;
        };
    };
    COMMAND_STATUS pulse_control(int64_t pulse_num,int16_t speed,int acce=0,bool absolute_mode=false  ,bool needsync=false,bool need_retry=false){
        /*命令功能：位置模式控制
        命令格式：地址 +0xFD+ 方向 + 速度+ 加速度 + 脉冲数 + 相对/绝对模式标志 +
        多机同步标志 + 校验字节
        命令返回：地址 + 0xFD + 命令状态 + 校验字节
        命令示例：发送01 FD 01 05 DC 00 00 00 7D 00 00 00 6B，正确返回01 FD 02 6B，
        条件不满足返回01 FD E2 6B，错误命令返回01 00 EE 6B
        （条件不满足情况：触发了堵转保护、电机没使能）
        数据解析：01表示旋转方向为CCW（00表示CW），05 DC表示速度为0x05DC =
        1500(RPM)，00 表示加速度档位为0x00 = 0，00 00 7D 00表示脉冲数为0x00007D00 =
        32000 个，00表示相对位置模式（01表示绝对位置模式），00表示不启用多机同步（01
        表示启用），如果需要多个电机同步开始运动，请参考“多机通讯及同步控制”章节；
        （16细分下发送3200个脉冲电机旋转一圈，32000个脉冲表示转10圈）
        注意：加速度档位为0表示不使用曲线加减速，直接按照设定的速度运行。曲线加
        减速时间计算公式：t2- t1 = (256- acc) * 50(us)，Vt2 = Vt1 + 1(RPM)；
        （注：acc为加速度档位，Vt1为t1时刻的转速，，Vt2为t2时刻的转速）*/
        bool direction = pulse_num < 0;
        if(dir){
            direction=!direction;
        }
        uint64_t p = abs(pulse_num);
        uint8_t data[13] = {this->id, 0xFD, direction, speed>>8, speed&0xFF,acce,p>>24, p>>16, p>>8, p,absolute_mode, needsync, this->checksum};
        send(data,13);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE://错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return pulse_control(pulse_num,speed,acce,absolute_mode,needsync,true);
                }
                return NOT_RESPONSE;
                break;
        };
    };
    COMMAND_STATUS stop(bool need_retry=false,bool needsync=false){
        // 命令功能：立即停止
        // 命令格式：地址 + 0xFE + 0x98 + 多机同步标志 + 校验字节
        // 命令返回：地址 + 0xFE + 命令状态 + 校验字节
        // 命令示例：发送01 FE 98 00 6B，正确返回01 FE 02 6B，条件不满足返回01 FE E2
        // 6B，错误命令返回01 00 EE 6B
        uint8_t data[5] = {this->id, 0xFE, 0x98, needsync, this->checksum};
        send(data,5);


        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE://错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return stop(true,needsync);
                }
                return NOT_RESPONSE;
                break;
        };
    };
    //控制多个电机只需要任意调用一次同步
    COMMAND_STATUS sync(bool need_retry=false){
        // 命令功能：多机同步运动
        // 命令格式：地址 + 0xFF + 0x66 + 校验字节
        // 命令返回：地址 + 0xFF + 命令状态 + 校验字节
        // 命令示例：发送01FF666B，正确返回01FF026B，条件不满足返回01FFE26B，
        // 错误命令返回01 00 EE 6B
        uint8_t data[4] = {0x00, 0xFF, 0x66, this->checksum};
        send(data,4);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return sync(true);
                }
                return NOT_RESPONSE;
                break;
        };
    };
    
    //让电机转到想要的位置，然后发送该命令设置单圈回零的零点位置
    COMMAND_STATUS set_zero_position(bool save=false,bool need_retry=false){
        // 命令功能：设置单圈回零的零点位置
        // 命令格式：地址 + 0x93 + 0x88 + 是否存储标志 + 校验字节
        // 命令返回：地址 + 0x93 + 命令状态 + 校验字节
        // 命令示例：发送01 93 88 01 6B，正确返回01 93 02 6B，错误命令返回01 00 EE 6B
        uint8_t data[5] = {this->id, 0x93, 0x88, save, this->checksum};
        send(data,5);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE://错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return set_zero_position(true,save);
                }
                return NOT_RESPONSE;
                break;
        };
    };
   
   //设置完原点回零参数后，可以发送该命令触发原点回零功能。
    COMMAND_STATUS re_zero(int mode=0,bool needsync=false,bool need_retry=false){
    // 命令功能：触发回零
    // 命令格式：地址 + 0x9A + 回零模式 + 多机同步标志 + 校验字节
    // 命令返回：地址 + 0x9A + 命令状态 + 校验字节
    // 命令示例：发送01 9A 00 00 6B，正确返回01 9A 02 6B，条件不满足返回01 9A E2 6B，错误命令返回01 00 EE 6B
    //数据解析：设置完原点回零参数后，可以发送该命令触发原点回零功能。其中，00表示触发单圈就近回零，01表示触发单圈方向回零，02表示触发多圈无限位碰撞回零，03 表示触发多圈有限位开关回零
        uint8_t data[5] = {this->id, 0x9A, mode, needsync ,this->checksum};
        send(data,5);
        
        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE://错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试w
                    return re_zero(true,mode,needsync);
                }
                return NOT_RESPONSE;
                break;
        };
    };

    //正在回零的过程中，可以使用该命令强制中断并退出回零操作。
    COMMAND_STATUS exit_rezero(bool need_retry=false){
    // 命令功能：强制中断并退出回零操作
    // 命令格式：地址 + 0x9C + 0x48 + 校验字节
    // 命令返回：地址 + 0x9C + 命令状态 + 校验字节
    // 命令示例：发送019C 0x48 6B，正 确返回01 9C 02 6B，条件不满足返回01 9C E2 6B，错误命令返回01 00 EE 6B
        uint8_t data[4] = {this->id, 0x9C, 0x48, this->checksum};
        send(data,4);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return exit_rezero(true);
                }
                return NOT_RESPONSE;
                break;
        };
    };

    REZREO_parameter read_parameter(bool need_retry=false){
    // 命令功能：读取原点回零参数
    // 命令格式：地址 + 0x22 + 校验字节
    // 命令返回：地址 + 0x22 + 原点回零参数 + 校验字节
    // 命令示例：发送01 22 6B，正确返回01 22 00 00 00 1E 00 00 27 10 0F A0 03 20 00 3C 00 6B ，错误命令返回01 00 EE 6B
    // 数据解析：返回的原点回零参数，它将按照下面的数据格式进行排列和数据的转换：
    // 回零模式 = 0x00 = Nearest = 单圈就近回零模式
    // 回零方向 = 0x00 = CW
    // 回零转速 = 0x001E = 30(RPM)
    // 回零超时时间 = 0x00002710 = 10000(ms)
    // 无限位碰撞回零检测转速 = 0x012C = 300(RPM)
    // 无限位碰撞回零检测电流 = 0x0320 = 800(Ma)
    // 无限位碰撞回零检测时间 = 0x003C = 60(ms)
    // 是否使能上电自动触发回零功能 = 0x00 = 不使能
    // （无限位碰撞回零检测判定条件：电机转速 < 碰撞回零检测转速 + 电机相电流 >
    // 碰撞回零检测电流 + 持续时间 > 碰撞回零检测时间）
        uint8_t data[4] = {this->id, 0x9C, 0x48, this->checksum};
        send(data,4);
        uint8_t r_data[18] = {0, 0, 0xFF, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        read(r_data, 4);
        // switch (r_data[2]){
        //     case 0xFF : //未响应
        //         REZREO_parameter null_p;
        //         return null_p;
        //         break;
                
        //     case 0x00 : //错误
        //         if(need_retry){
        //             return read_parameter(true);
        //         }
        //         break;
        //     default:
        //         for(int i=4;i<18;i++){
        //             while(serial->available()==0){
        //                 delay(1);
        //             }
        //             r_data[i]=serial->read();
        //         }
        //         REZREO_parameter p;
        //         p.mode = r_data[4];
        //         p.direction = r_data[5];
        //         p.speed = (r_data[6] << 8) | r_data[7];
        //         p.timeout = (r_data[8] << 8) | r_data[9];
        //         p.limit_speed = (r_data[10] << 8) | r_data[11];
        //         p.limit_current = (r_data[12] << 8) | r_data[13];
        //         p.limit_time = (r_data[14] << 8) | r_data[15];
        //         p.auto_rezero = r_data[16];
        //         return p;
        //         break;
        // };
    };
    
    COMMAND_STATUS change_parameter(bool need_retry,bool save,REZREO_parameter p){
    // 命令功能：修改原点回零参数
    // 命令格式：地址 + 0x4C + 0xAE + 是否存储标志 + 原点回零参数 + 校验字节
    // 命令返回：地址 + 0x4C + 命令状态 + 校验字节
    // 命令示例：发送01 4C AE 01 原点回零参数 6B，正确返回01 4C 02 6B，
    // 错误命令返回01 00 EE 6B
    // 数据解析：修改原点回零参数需要按照下面的数据格式进行排列和数据的转换：
    // 比如，发送如下数据对原点回零参数进行修改：
    // 01 4C AE 0000 00 1E 00 00 27 10 01 2C 03 20 00 3C 00 6B
    // 0x01 = 保存本次修改的配置参数；
    // 0x00 = 回零模式为Nearest（单圈就近回零模式）；
    // 0x00 = 回零方向为CW；
    // 0x001E = 回零速度为30(RPM)；
    // 0x00002710 = 回零超时时间为10000(ms)；
    // 0x012C = 无限位碰撞回零检测转速为300(RPM)；
    // 0x0320 = 无限位碰撞回零检测电流为800(Ma)；
    // 0x003C = 无限位碰撞回零检测时间为60(ms)；
    // 0x00 = 不使能上电自动触发回零功能；
        
        
        uint8_t data[20]={
            this->id,
            0x4C,
            0xAE,
            save ? 0x01 : 0x00,
            p.mode,
            p.direction,
            (p.speed >> 8) & 0xFF,
            p.speed & 0xFF,
            (p.timeout >> 24) & 0xFF,
            (p.timeout >> 16) & 0xFF,
            (p.timeout >> 8) & 0xFF,
            p.timeout & 0xFF,
            (p.limit_speed >> 8) & 0xFF,
            p.limit_speed & 0xFF,
            (p.limit_current >> 8) & 0xFF,
            p.limit_current & 0xFF,
            (p.limit_time >> 8) & 0xFF,
            p.limit_time & 0xFF,
            p.auto_rezero,
            this->checksum
        };
        send(data,20);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0x02 : //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误
                return COMMAND_FAIL;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return change_parameter(true,save,p);
                }
                return NOT_RESPONSE;
                break;
        };
    };
    
    //读取回零状态标志位,返回结构体
    Return_to_zero_status_flag get_return_to_zero_status(bool need_retry=false){
        /*命令功能：读取回零状态标志位
        命令格式：地址 + 0x3B + 校验字节
        命令返回：地址 + 0x3B + 回零状态标志+ 校验字节
        命令示例：发送01 3B 6B，正确返回01 3B 回零状态标志字节 6B，错误命令返回
        01 00 EE 6B
        数据解析：返回的回零状态标志字节的每一位都代表一种状态，比如返回的回零状
        态标志字节为0x03，它将按照下面的数据格式进行排列和数据的转换：
        编码器就绪状态标志位
        校准表就绪状态标志位
        正在回零标志位
        回零失败标志位
        = 0x03 & 0x01 = 0x01
        = 0x03 & 0x02 = 0x01
        = 0x03 & 0x04 = 0x00
        = 0x03 & 0x08 = 0x00*/
        uint8_t data[4] = {this->id, 0x3B, this->checksum};
        send(data,4);
        uint8_t r_data[4] = {0, 0, 0xff, 0};
        read(r_data, 4);
        Return_to_zero_status_flag flag;
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                if(need_retry){
                    return get_return_to_zero_status(true);
                }
                break;
            case 0xff:
                if(need_retry){
                    return get_return_to_zero_status(true);
                }
                break;
            default: //成功
                flag.is_valid_data = true;
                flag.encoder_ready = r_data[2] & 0x01;
                flag.calibration_ready = r_data[2] & 0x02;
                flag.is_zeroing = r_data[2] & 0x04;
                flag.is_zeroing_fail = r_data[2] & 0x08;
                return flag;
        }; 
    };
    
    //读取固件版本和对应的硬件版本
    version_info get_version_info(bool need_retry=false){
        /*命令功能：读取固件版本和对应的硬件版本
        命令格式：地址 + 0x1F + 校验字节
        命令返回：地址 + 0x1F + 固件版本号 + 对应的硬件版本号 + 校验字节
        命令示例：发送01 1F 6B，正确返回01 1F 7D 6F 6B，错误命令返回01 00 EE 6B
        数据解析：固件版本 = 0xF4 = Emm42_V5.0.0，对应的硬件版本 = 0x78 = 120 =
        ZDT_X42_V1.2 版本*/
        uint8_t data[4] = {this->id, 0x1F, this->checksum};
        send(data,4);
        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
        version_info info;
        switch (r_data[2]){
            case 0xE2 : //条件不满足
                if(need_retry){
                    return get_version_info(true);
                }
                break;
            default: //成功
                info.software_version = r_data[2];
                info.hardware_version = r_data[3];
                if(this->serial->available()){//只读取了4个字节，成功的数据还有一个字节在缓冲区
                    this->serial->read();//清除缓冲区
                }
                return info;
        };

    };

    COMMAND_STATUS coder_calibration(bool need_retry=false){
    // 命令功能：触发编码器校准
    // 命令格式：地址 + 0x06 + 0x45 + 校验字节
    // 命令返回：地址 + 0x06 + 状态码 + 校验字节
    // 命令示例：发送0106456B，正确返回0106026B，条件不满足返回0106E26B，
    // 错误命令返回01 00 EE 6B
    // （条件不满足的情况有：当前是开环模式、触发了堵转保护）
    // 数据解析：触发编码器校准，对应屏幕上的“Cal” 菜单
        uint8_t data[4] = {this->id, 0x06, 0x45, this->checksum};
        send(data,4);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
         switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return coder_calibration(true);
                }
                return NOT_RESPONSE;
                break;
        };
    };

    COMMAND_STATUS angle_reset(bool need_retry=false){
        // 命令功能：将当前的位置角度清零
        // 命令格式：地址 + 0x0A + 0x6D + 校验字节
        // 命令返回：地址 + 0x0A + 状态码 + 校验字节
        // 命令示例：发送01 0A 6D 6B，正确返回01 0A 02 6B，错误命令返回01 00 EE 6B
        // 数据解析：将当前位置角度、位置误差、脉冲数等全部清零。
        uint8_t data[4] = {this->id, 0x0A, 0x6D, this->checksum};
        send(data,4);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
         switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return angle_reset(true);
                }
                return NOT_RESPONSE;
                break;
        };
    };

    COMMAND_STATUS cancel_lock_protection(int need_retry=false){
    // 命令功能：解除堵转保护
    // 命令格式：地址 + 0x0E + 0x52 + 校验字节
    // 命令返回：地址 + 0x0E + 状态码 + 校验字节
    // 命令示例：发送010E526B，正确返回010E026B，条件不满足返回010EE26B，
    // 错误命令返回01 00 EE 6B
        uint8_t data[4] = {this->id, 0x0E, 0x52, this->checksum};
        send(data,4);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
         switch (r_data[2]){
            case 0xE2 : //条件不满足
                return COMMAND_FAIL;
                break;
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return cancel_lock_protection(true);
                }
                return NOT_RESPONSE;
                break;
        };
    };

    COMMAND_STATUS restore_factory_settings(int need_retry=false){
    // 命令功能：恢复出厂设置
    // 命令格式：地址 + 0x0F + 0x5F + 校验字节
    // 命令返回：地址 + 0x0F + 状态码 + 校验字节
    // 命令示例：发送01 0F 5F 6B，正确返回01 0F 02 6B，错误命令返回01 00 EE 6B，
    // 触发恢复出厂设置后，蓝灯亮起，需要断电重新上电校准编码器。
    // 数据解析：发送该命令可以恢复出厂设置，恢复出厂设置后需要重新上电，重新空
    // 载校准编码器 。
        uint8_t data[4] = {this->id, 0x0F, 0x5F, this->checksum};
        send(data,4);

        uint8_t r_data[4] = {0, 0, 0, 0};
        read(r_data, 4);
         switch (r_data[2]){
            case 0x02: //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误命令
                return COMMAND_ERROR;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return restore_factory_settings(true);
                }
                return NOT_RESPONSE;
                break;
        };
    };
    
    Phase_resistance_inductance get_Phase_resistance_inductance(bool need_retry=false){
    // 命令功能：读取相电阻和相电感
    // 命令格式：地址 + 0x20 + 校验字节
    // 命令返回：地址 + 0x20 + 相电阻 + 相电感 + 校验字节
    // 命令示例：发送01 20 6B，正确返回01 20 04 7A 0D 28 6B，错误命令返回01 00 EE 6B
    // 数据解析：相电阻 = 0x047A = 1146mΩ，相电感 = 0x0D28 = 3368uH（注意单位）
        uint8_t data[3] = {this->id, 0x20, this->checksum};
        send(data,3);
        uint8_t r_data[7] = {0, 0, 0xFF, 0, 0, 0, 0};
        read(r_data, 4);//不能直接读取7个字节，因为失败的时候只有4个字节
        Phase_resistance_inductance get;
        switch (r_data[2]){
            case 0xEE : //错误
                if(need_retry){
                    return get_Phase_resistance_inductance(true);
                }
                break;
            case 0xFF: //未响应
                break;
            default: //成功
                for (int i = 4; i <7; i++){
                    while(serial->available()==0){//等待数据
                        delay(1);
                    };
                    r_data[i]=serial->read();
                }

                
                get.phase_resistance=r_data[2]<<8|r_data[3];
                get.phase_inductance=r_data[4]<<8|r_data[5];
                
                return get;
        };
    };

    PID_parameter read_PID_parameter(bool need_retry=false){
    // 命令功能：读取位置环PID参数
    // 命令格式：地址 + 0x21 + 校验字节
    // 命令返回：地址 + 0x21 + 位置环PID参数 + 校验字节
    // 命令示例：发送01 21 6B，正确返回01 21 00 00 F2 30 00 00 00 64 00 00 F2 30
    // 6B ，错误命令返回01 00 EE 6B
    // 数据解析：
    // Kp = 0x0000F230 = 62000，Ki = 0x00000064 = 100，Kd = 0x0000F230 = 62000；
        uint8_t data[3] = {this->id, 0x21, this->checksum};
        send(data,3);
        uint8_t r_data[15] = {0, 0, 0xFF, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        read(r_data, 4);
        PID_parameter rdata;
        return rdata;
        // switch (r_data[2]){
        //     case 0xEE : //错误
        //         if(need_retry){
        //             return read_PID_parameter(true);
        //         }
        //         break;
        //     case 0xFF: //未响应
        //         PID_parameter null_data;
        //         return null_data;
        //         break;
        //     default: //成功
        //         for (int i = 4; i <15; i++){
        //             while(serial->available()==0){//等待数据
        //                 delay(1);
        //             };
        //             r_data[i]=serial->read();
        //         }
        //         rdata.Kp=r_data[2]<<24|r_data[3]<<16|r_data[4]<<8|r_data[5];
        //         rdata.Ki=r_data[6]<<24|r_data[7]<<16|r_data[8]<<8|r_data[9];
        //         rdata.Kd=r_data[10]<<24|r_data[11]<<16|r_data[12]<<8|r_data[13];
        //         return rdata;
        // };
    };

    uint16_t read_Bus_voltage(bool need_retry=false){
    // 命令功能：读取总线电压
    // 命令格式：地址 + 0x24 + 校验字节
    // 命令返回：地址 + 0x24 + 总线电压 + 校验字节
    // 命令示例：发送01 24 6B，正确返回01 24 5C 6A 6B，错误命令返回01 00 EE 6B
    // 数据解析：总线电压 = 0x5C6A = 23658mV（输入电压经过反接二极管后会有压降）
        uint8_t data[3] = {this->id, 0x24, this->checksum};
        send(data,3);
        uint8_t r_data[5] = {0, 0, 0xFF, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0xEE : //错误
                if(need_retry){
                    return read_Bus_voltage(true);
                }
                break;
            case 0xFF: //未响应
                return 0;
                break;
            default: //成功
                while(serial->available()==0){
                    delay(1);
                }//等待数据
                r_data[4]=serial->read();
                int16_t rdata = r_data[2]<<8|r_data[3];
                return rdata;
        };
    };
    uint16_t read_Phase_current(bool need_retry=false){
    // 命令功能：读取相电流
    // 命令格式：地址 + 0x27 + 校验字节
    // 命令返回：地址 + 0x27 + 总线相电流 + 校验字节
    // 命令示例：发送01 27 6B，正确返回01 27 02 73 6B，错误命令返回01 00 EE 6B
    // 数据解析：相电流 = 0x0273 = 627Ma
        uint8_t data[3] = {this->id, 0x27, this->checksum};
        send(data,3);
        uint8_t r_data[5] = {0, 0, 0xFF, 0, 0};
        read(r_data, 4);

        switch (r_data[1]){
            case 0x00 : //错误
                if(need_retry){
                    return read_Phase_current(true);
                }
                break;
            case 0xFF: //未响应
                return 0;
                break;
            default: //成功
                while(serial->available()==0){
                    delay(1);
                }
                r_data[4]=serial->read();
                int16_t rdata = r_data[2]<<8|r_data[3];
                return rdata;
        };
    };
    uint16_t read_Encoder(bool need_retry=false){
    // 命令功能：读取经过线性化校准后的编码器值
    // 命令格式：地址 + 0x31 + 校验字节
    // 命令返回：地址 + 0x31 + 读取经过线性化校准后的编码器值 + 校验字节
    // 命令示例：发送01 31 6B，正确返回01 31 8D 9E 6B，错误返回01 00 EE 6B
    // 数据解析：经过线性化校准后的编码器值 = 0x8D9E = 36254
    // （注意：经过线性化校准后，内部对编码器值进行了4倍频，一圈的数值是0-65535）
        uint8_t data[3] = {this->id, 0x31, this->checksum};
        send(data,3);
        uint8_t r_data[5] = {0, 0, 0xFF, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0x00 : //错误
                if(need_retry){
                    return read_Encoder(true);
                }
                break;
            case 0xFF: //未响应
                return 0;
                break;
            default: //成功
                while(serial->available()==0){
                    delay(1);
                }
                r_data[4]=serial->read();
                int16_t rdata = r_data[2]<<8|r_data[3];
                return rdata;
        };
    };
    //读取输入脉冲数
    int64_t read_input_pulses(bool need_retry=false){
    //因为是1位符号+32位数，所以最大值为超出int32_t范围,所以返回值为int64_t
    // 命令功能：读取输入脉冲数
    // 命令格式：地址 + 0x32 + 校验字节
    // 命令返回：地址 + 0x32 + 符号 + 输入脉冲数 + 校验字节
    // 命令示例：发送01 32 6B，正确返回01 32 01 00 00 0C 80 6B，错误命令返回01
    // 00 EE 6B
    // 数据解析：01表示负数(00表示正数)，00 00 0C 80表示输入脉冲数
    // 输入脉冲数 =-0x0C80 =-3200个
        uint8_t data[3] = {this->id, 0x32, this->checksum};
        send(data,3);
        uint8_t r_data[8] = {0, 0, 0xFF, 0, 0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[1]){
            case 0x00 : //错误
                if(need_retry){
                    return read_input_pulses(true);
                }
                break;
            case 0xFF: //未响应
                return 0;
            default: //成功
                for (int i = 4; i < 8; i++){
                    while(serial->available()==0){//等待数据
                        delay(1);
                    };
                    r_data[i]=serial->read();
                }        
                int64_t rdata = r_data[3]<<24|r_data[4]<<16|r_data[5]<<8|r_data[6];
                if(r_data[2] == 0x01){
                    rdata = -rdata;
                }
                return rdata;
        };
    };
    int64_t read_target_location(bool need_retry=false){
    // 命令功能：读取电机目标位置
    // 命令格式：地址 + 0x33 + 校验字节
    // 命令返回：地址 + 0x33 + 符号 + 电机目标位置 + 校验字节
    // 命令示例：发送01 33 6B，正确返回01 33 01 00 01 00 00 6B，错误命令返回01
    // 00 EE 6B
    // 数据解析：01表示负数(00表示正数)，00010000表示电机目标位置值（0-65535
    // 表示一圈），如果要转换成角度，可以这样计算：
    // 电机目标位置角度 =-0x00010000 = (-65536 * 360) / 65536 =-360.0°
        uint8_t data[3] = {this->id, 0x33, this->checksum};
        send(data,3);
        uint8_t r_data[8] = {0, 0xFF, 0, 0, 0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[1]){
            // case 0x00 : //错误
            //     if(need_retry){
            //         return read_target_location(true);
            //     }
            //     return 0;
            //     break;
            case 0xFF: //未响应
                return 0;
                break;
            default: //成功
                for (int i = 4; i < 8; i++){
                    r_data[i]=serial->read();
                }
                int64_t rdata = r_data[3]<<24|r_data[4]<<16|r_data[5]<<8|r_data[6];
                if(r_data[2] == 0x01){
                    rdata = -rdata;
                }
                return rdata;
        };
    };
    int read_current_speed(bool need_retry=false){
        // 命令功能：读取电机实时转速
        // 命令格式：地址 + 0x35 + 校验字节
        // 命令返回：地址 + 0x35 + 符号 + 电机实时转速 + 校验字节
        // 命令示例：发送01 35 6B，正确返回01 35 01 05 DC 6B，错误命令返回01 00 EE
        // 6B
        // 数据解析：01表示负数(00表示正数)，05 DC表示电机实时转速
        // 电机实时转速 =-0x05DC =-1500RPM（转/每分钟）
        uint8_t data[3] = {this->id, 0x35, this->checksum};
        send(data,3);
        uint8_t r_data[6] = {0, 0, 0xFF, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            case 0x00 : //错误
                if(need_retry){
                    return read_target_location(true);
                }
                break;
            case 0xFF: //未响应
                return 0;
                break;
            default: //成功
                for (int i = 4; i < 6; i++){
                    while(serial->available()==0){//等待数据
                        delay(1);
                    }
                    r_data[i]=serial->read();
                }
                int rdata = r_data[3]<<8|r_data[4];
                if(r_data[2] == 0x01){
                    rdata = -rdata;
                }
                return rdata;
        };
    };
    int64_t read_current_location(bool need_retry=false){
        // 命令功能：读取电机实时位置
        // 命令格式：地址 + 0x36 + 校验字节
        // 命令返回：地址 + 0x36 + 符号 + 电机实时位置 + 校验字节
        // 命令示例：发送01 36 6B，正确返回01 36 01 00 01 00 00 6B，错误命令返回01
        // 46
        // 00 EE 6B
        // 数据解析：01表示负数(00表示正数)，00010000表示电机实时位置值（0-65535
        // 表示一圈），如果要转换成角度，可以这样计算：
        // 电机实时位置角度 =-0x00010000 = (-65536 * 360) / 65536 =-360.0°
        uint8_t data[3] = {this->id, 0x36, this->checksum};
        send(data,3);
        uint8_t r_data[8] = {0, 0, 0xFF, 0, 0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
            // case 0x00 : //错误
            //     if(need_retry){
            //         return read_target_location(true);
            //     }
            //     break;
            case 0xFF: //未响应
                return 0;
                break;
            default: //成功
                for (int i = 4; i < 8; i++){
                    while(serial->available()==0){//等待数据
                        delay(1);
                    }
                    r_data[i]=serial->read();
                }
                int64_t rdata = r_data[3]<<24|r_data[4]<<16|r_data[5]<<8|r_data[6];
                if(r_data[2] == 0x01){
                    rdata = -rdata;
                }
                return rdata;
        };
    };
    int64_t read_location_error(bool need_retry=false){
        // 命令功能：读取电机位置误差
        // 命令格式：地址 + 0x37 + 校验字节
        // 命令返回：地址 + 0x37 + 符号 + 电机位置误差 + 校验字节
        // 命令示例：发送01 37 6B，正确返回01 37 01 00 00 00 08 6B，错误命令返回01
        // 00 EE 6B
        // 数据解析：01表示负数(00表示正数)，00000008表示电机位置误差值（0-65535
        // 表示一圈），如果要转换成角度，可以这样计算：
        // 电机实时位置角度 =-0x00000008 = (-8 * 360) / 65536 =-0.0439453125°
        uint8_t data[3] = {this->id, 0x37, this->checksum};
        send(data,3);
        uint8_t r_data[8] = {0, 0, 0xFF, 0, 0, 0, 0, 0};
        read(r_data, 4);
        switch (r_data[2]){
        // case 0x00 : //错误
        //         if(need_retry){
        //             return read_target_location(true);
        //         }
        //         break;
            case 0xFF: //未响应
                return 0;
                break;
            default: //成功
                for (int i = 4; i < 8; i++){
                    while(serial->available()==0){//等待数据
                        delay(1);
                    }
                    r_data[i]=serial->read();
                }
                int64_t rdata = r_data[3]<<24|r_data[4]<<16|r_data[5]<<8|r_data[6];
                if(r_data[2] == 0x01){
                    rdata = -rdata;
                }
                return rdata;            
        };
    };
    Motor_status_flag read_motor_status(bool need_retry=false){
        // 命令格式：地址 + 0x3A + 校验字节
        // 命令返回：地址 + 0x3A + 状态标志+ 校验字节
        // 命令示例：发送01 3A 6B，正确返回01 3A 电机状态标志字节 6B，错误命令返回
        // 01 00 EE 6B
        // 数据解析：比如返回01 3A 03 6B，可以这样进行电机状态的判断：
        // 电机使能状态标志位 = 0x03 & 0x01 = 0x01 = true
        // 47
        // 电机到位标志位 =0x03 & 0x02 = 0x01 = true
        // 电机堵转标志位 =0x03 & 0x04 = 0x00 = false
        // 电机堵转保护标志 = 0x03 & 0x08 = 0x00 = false
        uint8_t data[3] = {this->id, 0x3A, this->checksum};
        send(data,3);
        uint8_t r_data[4] = {0, 0, 0xff, 0};
        read(r_data, 4);
        // switch (r_data[2]){
        //     case 0x00 : //错误
        //         need_retry ? read_motor_status(true) : break;
        //     case 0xFF: //未响应
        //         Motor_status_flag null_data;
        //         return null_data;
        //         break;
        //     default: //成功
        //         Motor_status_flag rdata;
        //         rdata.is_enable = r_data[2] & 0x01;
        //         rdata.is_moving = r_data[2] & 0x02;
        //         rdata.is_blocked = r_data[2] & 0x04;
        //         rdata.is_overload = r_data[2] & 0x08;
        //         return rdata;
        // };
    };
    Driver_parameter read_driver_parameter(bool need_retry=false){
        // 命令功能：读取系统状态参数
        // 命令格式：地址 + 0x43 + 0x7A + 校验字节
        // 命令返回：地址 + 0x43 + 系统状态参数 + 校验字节
        // 命令示例：发送01 43 7A 6B，正确返回01 43 系统状态参数 6B，错误命令返回
        // 01 00 EE 6B
        // 数据解析：命令正确返回01 43后面的字节就是系统的状态参数，它将按照下面的
        // 数据格式进行排列和数据的转换：
        // 比如，发送读取系统状态参数01 43 7A 6B命令后，返回如下数据：
        // 01 43 5C 67 00 03 43 EB 01 00 01 00 00 00 00 00 01 00 01 00 00 01 00
        // 00 00 08 03 03 6B
        uint8_t data[4] = {this->id, 0x43, 0x7A, this->checksum};
        send(data,4);
        uint8_t r_data[31];
        for(int i=0;i<31;i++){
            r_data[i]=0;
        };
        r_data[2]=0xff;
        read(r_data, 4);
        // switch (r_data[2]){
        //     case 0x00 : //错误
        //         return need_retry ? read_driver_parameter(true) : break;
        //         break;
        //     case 0xFF: //未响应
        //         Driver_parameter null_data;
        //         return null_data;
        //         break;
        //     default: //成功
        //         Driver_parameter rdata;
        //         for (int i = 4; i < 31; i++){
        //             while(serial->available()==0){
        //                 delay(1);
        //             }
        //             r_data[i]=serial->read();
        //         }
        //         memcpy(&rdata, r_data+4, sizeof(Driver_parameter));
        //         return rdata;
        // }
    }
    // System_status read_system_status(bool need_retry=false){
    //     // 命令功能：读取系统状态
    //     // 命令格式：地址 + 0x43 + 0x7A + 校验字节
    //     // 命令返回：地址 + 0x43 + 系统状态参数 + 校验字节
    //     // 命令示例：发送01 43 7A 6B，正确返回01 43 系统状态参数 6B，错误命令返回
    //     // 01 00 EE 6B
    //     // 数据解析：命令正确返回01 43后面的字节就是系统的状态参数，它将按照下面的
    //     // 数据格式进行排列和数据的转换：
    //     // 比如，发送读取系统状态参数01 43 7A 6B命令后，返回如下数据：
    //     // 01 43 5C6700 03 43 EB 01 00 01 00 00 00 00 00 01 00 01 00 00 01 00
    //     // 00 00 08 03 03 6B
    //     uint8_t data[4] = {this->id, 0x43, 0x7A, this->checksum};
    //     send(data,4);
    //     uint8_t r_data[31];
    //     for(int i=0;i<31;i++){
    //         r_data[i]=0;
    //     };
    //     r_data[2]=0xff;
    //     read(r_data, 4);
    //     switch (r_data[2]){
    //         case 0x00 : //错误
    //             if(need_retry){
    //                 return read_system_status(true);
    //             }
    //             break;
    //         case 0xFF: //未响应
    //             System_status null_data;
    //             return null_data;
    //             break;
    //         default: //成功
    //             for(int i = 4; i < 31; i++){
    //                 while(serial->available()==0){
    //                     delay(1);
    //                 }
    //                 r_data[i]=serial->read();
    //             }
    //             System_status rdata;
    //             rdata.voltage=r_data[4]<<8|r_data[5];
    //             rdata.current=r_data[6]<<8|r_data[7];
    //             rdata.encoder=r_data[8]<<8|r_data[9];
    //             rdata.target_position=(!r_data[10]*-1)*(r_data[11]<<24|r_data[12]<<16|r_data[13]<<8|r_data[14]);
    //             rdata.speed=(!r_data[15]*-1)*(r_data[16]<<8|r_data[17]);
    //             rdata.real_position=(!r_data[18]*-1)*(r_data[19]<<24|r_data[20]<<16|r_data[21]<<8|r_data[22]);
    //             rdata.position_error(!r_data[23]*-1)*(r_data[24]<<24|r_data[25]<<16|r_data[26]<<8|r_data[27]);
    //             rdata.is_ready=r_data[28]|0x1;//编码器就绪状态标志位
    //             rdata.is_calibrated=r_data[28]|0x2;//校准表就绪状态标志位
    //             rdata.is_zeroing=r_data[28]|0x4;//正在回零标志位
    //             rdata.is_zeroing_fail=r_data[28]|0x8;//回零失败标志位
    //             rdata.is_enable=r_data[29]|0x1;//使能状态标志位
    //             rdata.is_moving=r_data[29]|0x2;//电机到位标志位
    //             rdata.is_blocked=r_data[29]|0x4;//电机堵转标志位
    //             rdata.is_overload=r_data[29]|0x8;//电机堵转保护标志
    //             return rdata;
    //     };
    // };
    COMMAND_STATUS change_subdivision(uint8_t subdivision,bool save=true,int need_retry=false){
        // 命令功能：修改任意细分
        // 命令格式：地址 + 0x84 + 0x8A + 是否存储标志 + 细分值 + 校验字节
        // 命令返回：地址 + 0x84 + 命令状态 + 校验字节
        // 命令示例：发送01 84 8A 01 07 6B，正确返回01 84 02 6B，错误命令返回01 00
        // EE 6B
        // 数据解析：修改细分为0x07 = 7细分，并存储到芯片上；
        uint8_t data[6] = {this->id, 0x84, 0x8A,save,subdivision, this->checksum};
        send(data,6);
        uint8_t r_data[4];
        read(r_data, 4);
        switch (r_data[2]){
            case 0x02 : //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误
                return COMMAND_FAIL;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return change_subdivision(subdivision,save,need_retry);
                }
                return NOT_RESPONSE;
                break;
        };
    };
    COMMAND_STATUS change_ID(uint8_t new_id,bool save=true,int need_retry=false){
        // 命令功能：修改任意ID地址
        // 命令格式：地址 + 0xAE + 0x4B + 是否存储标志 + ID地址 + 校验字节
        // 命令返回：地址 + 0xAE + 命令状态 + 校验字节
        // 命令示例：发送01 AE 4B 01 10 6B，正确返回01 AE 02 6B，错误命令返回01 00
        // 51
        // EE 6B
        // 数据解析：修改ID地址为0x10 = 16，并存储到芯片上；
        uint8_t data[6] = {this->id, 0xAE, 0x4B,save,new_id, this->checksum};
        send(data,6);
        uint8_t r_data[4];
        read(r_data, 4);
        switch (r_data[2]){
            case 0x02 : //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误
                return COMMAND_FAIL;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return change_ID(new_id,save,need_retry);
                }
                return NOT_RESPONSE;
                break;
        };
    };
    
    COMMAND_STATUS change_open_or_closed_loop(uint8_t mode,bool save=true,int need_retry=false){
        // 命令功能：切换开环/闭环模式（P_Pul菜单选项）
        // 命令格式：地址 + 0x46 + 0x69 + 是否存储标志 + 开环/闭环模式 + 校验字节
        // 命令返回：地址 + 0x46 + 命令状态 + 校验字节
        // 命令示例：发送01 46 69 01 01 6B，正确返回01 46 02 6B，错误命令返回01 00
        // EE 6B
        // 数据解析：发送01 46 69 01 01 6B修改为开环模式，发送01 46 69 01 02 6B修
        // 改为闭环模式
        if (mode != 0x01 && mode != 0x02){
            return COMMAND_ERROR;
        }
        uint8_t data[6] = {this->id, 0x46, 0x69,save, mode , this->checksum};
        send(data,6);
        uint8_t r_data[4];
        read(r_data, 4);
        switch (r_data[2]){
            case 0x02 : //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误
                return COMMAND_FAIL;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return change_open_or_closed_loop(mode,save,need_retry);
                }
                return NOT_RESPONSE;
                break;
        };
    }

    COMMAND_STATUS change_open_loop_current(uint16_t current,bool save=true,int need_retry=false){
        // 命令功能：修改开环模式的工作电流
        // 命令格式：地址 + 0x44 + 0x33 + 是否存储标志 + 开环模式电流 + 校验字节
        // 命令返回：地址 + 0x44 + 命令状态 + 校验字节
        // 命令示例：发送01 44 33 00 03 E8 6B，正确返回01 44 02 6B，错误命令返回01
        // 00 EE 6B
        // 数据解析：修改开环模式电流为0x03E8 = 1000(Ma)，不存储（断电丢失）；
        uint8_t data[7] = {this->id, 0x44, 0x33,save, current>>8, current&0xFF, this->checksum};
        send(data,7);
        uint8_t r_data[4];
        read(r_data, 4);
        switch (r_data[2]){
            case 0x02 : //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误
                return COMMAND_FAIL;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return change_open_loop_current(current,save,need_retry);
                }
                return NOT_RESPONSE;
                break;
        };
    }

    COMMAND_STATUS change_driver_configuration_parameters(uint8_t parameters,bool save=true,int need_retry=false){
        // 命令功能：修改驱动配置参数
        // 命令格式：地址 + 0x48 + 0xD1 + 是否存储标志 + 驱动配置参数 + 校验字节
        // 命令返回：地址 + 0x48 + 命令状态 + 校验字节
        // 52
        // 命令示例：发送01 48 D1 01 驱动参数 6B，正确返回01 48 02 6B，错误命令返回
        // 01 00 EE 6B
        uint8_t data[6] = {this->id, 0x48, 0xD1,save, parameters , this->checksum};
        send(data,6);
        uint8_t r_data[4];
        read(r_data, 4);
        switch (r_data[2]){
            case 0x02 : //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误
                return COMMAND_FAIL;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return change_driver_configuration_parameters(parameters,save,need_retry);
                }
                return NOT_RESPONSE;
                break;
        };
    }

    COMMAND_STATUS change_PID_parameter(uint8_t PID_parameter,bool save=true,int need_retry=false){
        // 命令功能：修改位置环PID参数
        // 命令格式：地址 + 0x4A + 0xC3 + 是否存储标志 + 位置环PID参数 + 校验字节
        // 命令返回：地址 + 0x4A + 命令状态 + 校验字节
        // 命令示例：发送01 4A C3 01 位置环PID参数 6B，正确返回01 4A 02 6B，
        // 错误命令返回01 00 EE 6B
        // 数据解析：修改位置环PID参数需要按照下面的数据格式进行排列和数据的转换：
        // 比如，发送如下数据对位置环的PID参数进行修改：
        // 01 4A C3 0000 F2 30 00 00 00 64 00 00 F2 30 6B
        // =不保存本次修改的配置参数；
        // 0x0000F230 = 修改Kp = 62000;
        // 0x00000064 = 修改Ki = 100;
        // 0x0000F230 = 修改Kd = 62000;的有效电平可在菜单En中选择，选H为高电平启动，低电平停止）
        uint8_t data[6] = {this->id, 0x48, 0xD1,save, PID_parameter , this->checksum};
        send(data,6);
        uint8_t r_data[4];
        read(r_data, 4);
        switch (r_data[2]){
            case 0x02 : //成功
                return COMMAND_SUCCESS;
                break;
            case 0xEE: //错误
                return COMMAND_FAIL;
                break;
            default: //未响应
                if(need_retry){//需要重试
                    return change_PID_parameter(PID_parameter,save,need_retry);
                }
                return NOT_RESPONSE;
                break;
        };
    }


    ~EMMC42V5(){};
private:
    uint8_t id=1;
    int64_t location = 0;
    int64_t set_speed = 0;
    int64_t current_speed = 0;
    uint8_t checksum = 0x6B;
    HardwareSerial *serial;
    bool dir=0;


    void send(uint8_t *data,int len){
        if(this->serial->available()){
          serial->flush();
        }
        //写入数据
        for (int i = 0; i < len; i++){
            this->serial->write(data[i]);
        }
        delay(1);
    };
    void read(uint8_t *data,uint8_t len,bool need_delay = true){
        if(need_delay)
            delay(1);
        for (int i = 0; i < MAX_RETRY; i++){
            if (this->serial->available()){
                data[0]=this->serial->read();
                if (data[0] == this->id){
                    for (int j = 1; j < len; j++){
                        data[j]=this->serial->read();
                        
                    }
                    return ;
                }
            }
            delay(1);
        }
    }
};

#endif