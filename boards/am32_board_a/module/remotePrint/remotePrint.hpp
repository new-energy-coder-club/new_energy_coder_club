#ifndef remotePrint_hpp
#define remotePrint_hpp

#include "ESPNOW.hpp"  // 包含ESP-NOW通信库
#include <inttypes.h>  // 标准整数类型头文件
#include "Print.h"     // Arduino打印功能基类

// 远程打印类，继承自Arduino的Print类
class remotePrint_t : public Print {
private:
    // 私有构造函数（单例模式关键）
    remotePrint_t() {} // 禁止外部直接实例化
        
    // 禁用拷贝构造函数（单例模式关键）
    remotePrint_t(const remotePrint_t&) = delete;
    // 禁用赋值运算符（单例模式关键）
    remotePrint_t& operator=(const remotePrint_t&) = delete;
    
    // 静态实例指针（单例模式核心）
    static remotePrint_t* instance;
    
    // 接收端的MAC地址，默认设置为广播地址
    MAC_t receive_MAC = broadcastMacAddress;

public:
    // 析构函数
    ~remotePrint_t() {
        instance = nullptr; // 清除实例指针
    }

    // 获取单例实例的静态方法（单例模式唯一访问点）
    static remotePrint_t& getInstance() {
        if (!instance) {  // 如果实例不存在
            instance = new remotePrint_t(); // 创建新实例
        }
        return *instance; // 返回实例引用
    }
    
    // 初始化设置函数
    // 参数：
    //   _secret_key: 安全密钥，默认使用DEFAULT_SECRET_KEY
    //   _receive_MAC: 目标MAC地址，默认使用广播地址
    void setup(uint16_t _secret_key=DEFAULT_SECRET_KEY, MAC_t _receive_MAC=broadcastMacAddress) {
        change_secret_key(_secret_key);  // 设置通信密钥
        receive_MAC = _receive_MAC;     // 更新目标MAC地址
        esp_now_setup(_receive_MAC);    // 初始化ESP-NOW通信
    }
    
    // 实现Print类的write方法（单字节版本）
    // 参数：
    //   data: 要发送的单个字节
    // 返回值：实际写入的字节数（总是1）
    size_t write(uint8_t data) override {
        esp_now_send_package("remotePrint", &data, 1, receive_MAC);
        return 1;
    };
    
    // 实现Print类的write方法（缓冲区版本）
    // 参数：
    //   buffer: 要发送的数据缓冲区
    //   size: 要发送的数据大小
    // 返回值：实际写入的字节数
    size_t write(const uint8_t *buffer, size_t size) override {
        esp_now_send_package("remotePrint", const_cast<uint8_t*>(buffer), size, receive_MAC);
        return size;
    };
    
    // 销毁单例实例的静态方法
    // 注意：需要时手动调用以释放资源
    static void destroy() {
        if (instance) {   // 如果实例存在
            delete instance; // 删除实例
            instance = nullptr; // 重置指针
        }
    }
};

// 初始化静态成员变量（必须放在类定义外部）
remotePrint_t* remotePrint_t::instance = nullptr;

// 创建全局引用别名，方便使用
// 注意：实际使用时需要先调用setup()进行初始化
remotePrint_t& remotePrinter = remotePrint_t::getInstance();

#endif