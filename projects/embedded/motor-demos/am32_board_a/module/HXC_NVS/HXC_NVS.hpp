/*
 * @LastEditors: qingmeijiupiao
 * @Description: HXC战队nvs储存系统二次封装库，用于储存变量到NVS
 * @Author: qingmeijiupiao
 * @LastEditTime: 2025-05-15 02:36:57
 */
#ifndef HXC_NVS_HPP
#define HXC_NVS_HPP
#include "Arduino.h"
#include "nvs.h"
#include "nvs_flash.h"

//使用HXC命名空间
namespace HXC{

//错误代码对应的错误信息数组
static const char * nvs_errors[] = { "OTHER", "NOT_INITIALIZED", "NOT_FOUND", "TYPE_MISMATCH", "READ_ONLY", "NOT_ENOUGH_SPACE", "INVALID_NAME", "INVALID_HANDLE", "REMOVE_FAILED", "KEY_TOO_LONG", "PAGE_FULL", "INVALID_STATE", "INVALID_LENGTH"};

// 用于将NVS的错误代码转换为对应的错误信息的宏
#define nvs_error(e) (((e)>ESP_ERR_NVS_BASE)?nvs_errors[(e)&~(ESP_ERR_NVS_BASE)]:nvs_errors[0])

//默认使用的NVS page名称
#define NVS_NAME "HXC"


// 基类，用于共享静态变量,解决String模板特化静态变量不同的问题
class NVS_Base {
    protected:
        static bool is_setup; // 共享的静态变量
        static nvs_handle_t _handle; // 共享的 NVS 句柄
};
// 初始化类的静态成员变量
bool NVS_Base::is_setup=false;
nvs_handle_t NVS_Base::_handle=0;

template<typename Value_type>
class NVS_DATA: public NVS_Base {
public:
    // 构造函数，初始化key和默认值
    NVS_DATA(String _key,Value_type default_value){
        static_assert(
            !std::is_pointer<Value_type>::value,
            "NVS_DATA<Value_type>:Cannot use pointer type!"
        );
        if(_key.length()>15){
            log_e("nvs key too long: %s", key.c_str());
            _key=_key.substring(0,15);
        }
        this->key=_key;
        this->value=default_value;
    }
    ~NVS_DATA(){}
    // 保存数据到NVS的方法
    esp_err_t save(){
        if(!is_setup){setup();} // 如果未初始化，则先初始化

        esp_err_t err = nvs_set_blob(NVS_Base::_handle, key.c_str(), (const void*)&value, sizeof(Value_type)); // 将数据写入NVS
        if(err){
            log_e("nvs_set_blob fail: %s %s", key.c_str(), nvs_error(err)); // 如果写入失败，记录错误信息
        }
        err = nvs_commit(NVS_Base::_handle); // 提交写入操作
        if(err){
            log_e("nvs_commit fail: %s %s", key.c_str(), nvs_error(err)); // 如果提交失败，记录错误信息
        }
        return err; // 返回操作结果
    }

    // 从NVS读取数据的方法
    Value_type read(){
        if(!is_setup){setup();} // 如果未初始化，则先初始化
        if(is_read) return value; // 如果已经读取过，则直接返回缓存的值
        size_t datalen = 0;
        esp_err_t err = nvs_get_blob(NVS_Base::_handle, key.c_str(), NULL, &datalen); // 获取数据长度
        if(err!=ESP_OK || datalen!=sizeof(Value_type)){
            log_e("KEY=%s NVS无数据,使用默认值", key.c_str()); // 如果获取长度失败，记录错误信息
            is_read=true;
            return value; // 返回默认值
        }
        err = nvs_get_blob(NVS_Base::_handle, key.c_str(), (void*)&value, &datalen); // 读取数据
        if(err){
            log_e("KEY=%s NVS读取失败,使用默认值", key.c_str()); // 如果读取失败，记录错误信息
            return value; // 返回默认值
        }
        is_read=true; // 标记为已读取
        return value; // 返回读取的值
    }

    // 重载赋值运算符，用于更新NVS中的数据
    NVS_DATA& operator=(const Value_type& newValue) {
        value = newValue;
        save(); // 保存到NVS
        return *this;
    }

    // 重载隐式类型转换运算符，用于获取NVS中的数据
    operator Value_type() {
        return read(); // 读取NVS中的值
    }

protected:
    // 静态方法，用于初始化NVS
    static void setup(){
        if(is_setup) return; // 如果已经初始化，则直接返回
        auto err= nvs_open(NVS_NAME,NVS_READWRITE, &NVS_Base::_handle); // 打开NVS命名空间
        if(err!=ESP_OK){
            log_e("nvs_open failed: %s", nvs_error(err)); // 如果打开失败，记录错误信息
            return;
        };
        is_setup=true; // 标记为已初始化
    }
    String key; // 存储NVS中的key
    Value_type value; // 存储数据的值
    bool is_read=false;//标记是否已读取
};

//用于存储字符串的NVS类模板特化
template <>
class NVS_DATA<String> : public NVS_Base {
    public:
    // 构造函数，初始化key和默认值
    NVS_DATA(String _key,String default_value){
        if(_key.length()>15){
            log_e("nvs key too long: %s", key.c_str());
            _key=_key.substring(0,15);
        }
        this->key=_key;
        this->value=default_value;
    }
    ~NVS_DATA(){}
    // 保存数据到NVS的方法
    esp_err_t save(){
        if(!is_setup){setup();} // 如果未初始化，则先初始化

        esp_err_t err = nvs_set_blob(NVS_Base::_handle, key.c_str(),value.c_str(),value.length()+1); // 将数据写入NVS,value.length()不包括'\0' 所以需要+1否则会出错
        if(err){
            log_e("nvs_set_blob fail: %s %s", key.c_str(), nvs_error(err)); // 如果写入失败，记录错误信息
        }
        err = nvs_commit(NVS_Base::_handle); // 提交写入操作
        if(err){
            log_e("nvs_commit fail: %s %s", key.c_str(), nvs_error(err)); // 如果提交失败，记录错误信息
        }
        return err; // 返回操作结果
    }

    // 从NVS读取数据的方法
    String read(){
        if(!is_setup){setup();} // 如果未初始化，则先初始化
        if(is_read) return value; // 如果已经读取过，则直接返回缓存的值
        size_t datalen = 0;
        esp_err_t err = nvs_get_blob(NVS_Base::_handle, key.c_str(), NULL, &datalen); // 获取数据长度
        if(err!=ESP_OK){
            log_e("KEY=%s NVS无数据,使用默认值", key.c_str()); // 如果获取长度失败，记录错误信息
            is_read=true;
            return value; // 返回默认值
        }
        const char *arr = new char[datalen];
        err = nvs_get_blob(NVS_Base::_handle, key.c_str(), (void*)arr, &datalen); // 读取数据
        if(err){
            log_e("KEY=%s NVS读取失败,使用默认值", key.c_str()); // 如果读取失败，记录错误信息
            return value; // 返回默认值
        }
        value=arr;
        is_read=true; // 标记为已读取
        return value; // 返回读取的值
    }

    // 重载赋值运算符，用于更新NVS中的数据
    NVS_DATA& operator=(const String& newValue) {
        value = newValue;
        save(); // 保存到NVS
        return *this;
    }

    // 重载隐式类型转换运算符，用于获取NVS中的数据
    operator String() {
        return read(); // 读取NVS中的值
    }

protected:
    // 静态方法，用于初始化NVS
    static void setup(){
        if(is_setup) return; // 如果已经初始化，则直接返回
        auto err= nvs_open(NVS_NAME,NVS_READWRITE, &NVS_Base::_handle); // 打开NVS命名空间
        if(err!=ESP_OK){
            log_e("nvs_open failed: %s", nvs_error(err)); // 如果打开失败，记录错误信息
            return;
        };
        is_setup=true; // 标记为已初始化
    }
    String key; // 存储NVS中的key
    String value; // 存储数据的值
    bool is_read=false;//标记是否已读取
};
}
#endif
/*
                                              .=%@#=.                                               
                                            -*@@@@@@@#=.                                            
                                         .+%@@@@@@@@@@@@#=                                          
                                       -#@@@@@@@* =@@@@@@@@*:                                       
                                     =%@@@@@@@@=   -@@@@@@@@@#-                                     
                                  .+@@@@@@@@@@-     .@@@@@@@@@@%=                                   
                                .+@@@@@@@@@@@@-     +@@@@@@@@@@@@@+.                                
                               +@@@@@@@@@@@@@@@    .@@@@@@@@@@@@@@@@+.                              
                             =@@@@@@@@@@@@@@@%-     =%@@%@@@@@@@@@@@@@=                             
                           -%@@@@@@@@@@@@+..     .       -@@@@@@@@@@@@@%-                           
                         .#@@@@@@@@@@@@@#       -@+       +@@@@@@@@@@@@@@#:                         
                        +@@@@@@@@@@@@@@@@+     +@@@+     =@@@@@@@@@@@@@@@@@+                        
                      :%@@@@@@@@@@@@@@@@@+    *@@@@*     =@@@@@@@@@@@@@@@@@@%-                      
                     +@@@@@@@@@@@@@@#+*+-   .#@@@@+       :+*+*@@@@@@@@@@@@@@@*                     
                   :%@@@@@@@@@@@@@@+       :%@@@@-    .-       -@@@@@@@@@@@@@@@%:                   
                  =@@@@@@@@@@@@@@@@-      -@@@@%:    .%@+      =@@@@@@@@@@@@@@@@@=                  
                 *@@@@@@@@@@@@@@@@@@.    =@@@@#.    -@@@@+    =@@@@@@@@@@@@@@@@@@@#                 
               .%@@@@@@@@@@@@@@@@@@+    +@@@@*     =@@@@%:    .#@@@@@@@@@@@@@@@@@@@%.               
              :@@@@@@@@@@@@@@@%:::.    #@@@@+     +@@@@#        .::.*@@@@@@@@@@@@@@@@-              
             -@@@@@@@@@@@@@@@%       .%@@@@=     *@@@@*     +-       *@@@@@@@@@@@@@@@@=             
            =@@@@@@@@@@@@@@@@@#.    -@@@@@-    :%@@@@=    .#@@+     +@@@@@@@@@@@@@@@@@@=            
           =@@@@@@@@@@@@@@@@@@@:    =====.     -+===:     :====     @@@@@@@@@@@@@@@@@@@@+           
          +@@@@@@@@@@@@@@@#%%#-                                     :*%%#%@@@@@@@@@@@@@@@+          
         =@@@@@@@@@@@@@@%.       ...........................              *@@@@@@@@@@@@@@@=         
        =@@@@@@@@@@@@@@@+      .#@@@@@@@@@@@@@@@@@@@@@@@@@@#     .*:      =@@@@@@@@@@@@@@@@-        
       -@@@@@@@@@@@@@@@@@=    .%@@@@@@@@@@@@@@@@@@@@@@@@@@#     :@@@-    =@@@@@@@@@@@@@@@@@@:       
      :@@@@@@@@@@@@@@@@@%.   -@@@@%+=====================:     -@@@@%    :%@@@@@@@@@@@@@@@@@@.      
      %@@@@@@@@@@@@@=-=:    =@@@@#.                           +@@@@#.      -=--%@@@@@@@@@@@@@%      
     #@@@@@@@@@@@@@:       +@@@@*      ............. .       *@@@@*             %@@@@@@@@@@@@@+     
    =@@@@@@@@@@@@@@#.     #@@@@+     +@@@@@@@@@@@@@@@#.    .#@@@@+     +#.     +@@@@@@@@@@@@@@@:    
   .@@@@@@@@@@@@@@@@-   .%@@@@=     *@@@@@@@@@@@@@@@#     :%@@@@-     *@@%:    @@@@@@@@@@@@@@@@%    
   %@@@@@@@@@@@%%%#=   :@@@@@:    .#@@@@+-----------     -@@@@@:     #@@@@=    :#%%%@@@@@@@@@@@@*   
  =@@@@@@@@@@@=       -@@@@%.    :%@@@@-                =@@@@%.    .%@@@@=          :%@@@@@@@@@@@:  
  @@@@@@@@@@@%.      =@@@@#     -@@@@%:    .:::-:      +@@@@#     :@@@@@:    .       +@@@@@@@@@@@#  
 +@@@@@@@@@@@@@.    *@@@@*     =@@@@#.    -@@@@@:     #@@@@+     =@@@@%.    -@#     +@@@@@@@@@@@@@- 
.@@@@@@@@@@@@@#    *@%@%=     +@@@@*     =@@@@#.    .#@@@%=     +@@@@#     =@@@%.   =@@@@@@@@@@@@@% 
+@@@@@@@@*-==-                .          .           . ..       .....      .....     .=+=+@@@@@@@@@-
%@@@@@@@+                                                                                 -@@@@@@@@#
@@@@@@@-       =#%#=     -#%%#-     -#%%*.     +%%%*.    .*%%#=     :#%%#-     =%%%*.      .#@@@@@@@
@@@@@@=.::::::*@@@@@*:::-@@@@@@-:::=@@@@@%::::*@@@@@#::::%@@@@@+:---@@@@@@=---+@@@@@%------:=@@@@@@@
=@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@+
 *@@@@@@@@@@@@@@@@@@@@@@@@@@@%%##**++===----:::::------===++***##%%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@* 
  -#@@@@@@@@@@@@@@@@%#*+=-:.                                        ..::-=+*##%@@@@@@@@@@@@@@@@@#-  
    :=*%@@@@@%#*=-:                                                             .:-=+*#%%%%##+-.    
                                                                                        
        K####      #####     ###    ###  ######.   ##########     K##    ### ###    ##W    ####W    
       #######    #######    ###    ###  ########  ##########     ###    ### ###   ###   W######    
      W###G####  ###W ####   ###    ###  ######### ##########     ###    ###  ##   ###   ###W####   
      ###   ###  ###   ###   ###    ##  ###    ###    ###         ###    ###  ### t##   ###   ###   
     G##    #   ###    ###   ##     ##  ###    ###    ###         ###    ###  ### ###   ##W         
     ###        ###    ###   ##    ###  ###    ###    ###         ##L    ##   ### ##   ###          
     ###        ###    ###  K##    ###  ###    ###    ###         ##     ##    #####   ###          
     ###       ,##     ###  ###    ###  ###   ###,    ##         G##    ###    ####    ###          
    W##        ###     ###  ###    ###  #########     ##         ##########    ####    ###          
    ###        ###     ###  ###    ###  ########     ###         ##########    ###i   K##           
    ###        ###     ###  ###    ##  #######       ###         ###    ###    ####   ###           
    ###        ###     ###  ##     ##  ###           ###         ###    ###   ##W##   ###           
    ###        ###     ##i  ##    ###  ###           ###         ###    ##    ## ##   ###           
    ###        ###    ###  ,##    ###  ###           ###         ##     ##   ### ##   ###           
    ###    ### ###    ###  K##    ###  ###           ##         t##    ###   ##  ###  ###    ###    
    ###   G##i ###   ###   .##   ###.  ##t           ##         ###    ###  ###  ###  W##,   ###    
     ########  W##W#####    ########   ##           ###         ###    ###  ##    ##   ####W###     
     #######    #######     #######   ###           ###         ###    ### ###    ##.  #######      
      #####      #####       #####    ###           ###         ###    ### ##W    ###   #####       
                   ###                                                                              
                   ###                                                                              
                   #####                                                                            
                    ####                                                                            
                      K                                                                             
*/