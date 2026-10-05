/*
 * @LastEditors: qingmeijiupiao
 * @Description: HXCthread库,基于FreeRTOS实现的类似std::thread线程库 
 * @Author: qingmeijiupiao
 * @LastEditTime: 2025-05-15 02:33:18
 */
#ifndef HXCTHREAD_HPP
#define HXCTHREAD_HPP

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/timers.h"
#include "esp32-hal.h"
#include <functional>

#ifndef DEFAULT_STACK_SIZE// 如果未定义DEFAULT_STACK_SIZE
#define DEFAULT_STACK_SIZE 2048
#endif

#ifndef DEFAULT_PRIORITY// 如果未定义DEFAULT_PRIORITY
#define DEFAULT_PRIORITY 5
#endif

#ifndef DEFAULT_TASK_NAME// 如果未定义DEFAULT_TASK_NAME
#define DEFAULT_TASK_NAME "DEFAULTNAME"
#endif

namespace HXC {
    template <typename ParamType = void>
    class thread {
    public:
        // 构造函数，接收一个函数对象作为参数，该函数对象将被线程执行。
        thread(std::function<void(ParamType)> _func) : func(_func) {}

        /**
         * @description:线程启动
         * @return {*}
         * @Author: qingmeijiupiao
         * @param {ParamType} parameter 线程参数
         * @param {char} *taskname 线程名称
         * @param {int} stack_size 线程堆栈大小
         * @param {UBaseType_t} priority 线程优先级
         * @param {int} core 线程所在核心 0-1 默认运行在任意核心
         */
        void start(ParamType parameter = {},const char *taskname=DEFAULT_TASK_NAME, int stack_size = DEFAULT_STACK_SIZE, UBaseType_t priority = DEFAULT_PRIORITY, int core = tskNO_AFFINITY) {
            if (this->threadHandle == nullptr) { // 如果线程句柄为空，则创建新线程。
                this->funcparam = parameter; // 保存参数
                xTaskCreatePinnedToCore( // 创建一个指定核心的线程
                    TaskWrapper, // 线程的包装函数
                    taskname, // 任务名称
                    stack_size, // 堆栈大小
                    this, // 传递this指针，以便在TaskWrapper中访问成员变量和函数
                    priority, // 线程优先级
                    &this->threadHandle, // 线程句柄的地址
                    core); // 核心亲和性
            }
        }
        void stop(){ // 停止线程
            if (this->threadHandle != nullptr) { // 如果线程句柄不为空，则删除线程。
                vTaskDelete(this->threadHandle); // 删除线程
                this->threadHandle = nullptr; // 清空线程句柄
            }
        }

        // 获取线程句柄。
        xTaskHandle get_Handle() {
            return this->threadHandle;
        }

        // 等待线程结束的函数。
        void join() {
            while(this->threadHandle != nullptr){ // 循环直到线程句柄为空，即线程结束。
                vTaskDelay(1/ portTICK_PERIOD_MS); // 延迟一个tick周期，避免忙等。
            }
        }

        #ifdef INCLUDE_uxTaskGetStackHighWaterMark//获取是否启用该函数
        /**
         * @brief 获取线程的剩余栈大小
         * 
         * @return int 返回线程的剩余栈大小，以字节为单位
         * @note 该函数需要在FreeRTOSConfig.h中定义INCLUDE_uxTaskGetStackHighWaterMark=1
         * @warning 该函数可能会使系统暂时变得不可响应
         */
        int get_remaining_stack_size(){
            if(this->threadHandle == nullptr) return 0;
            return uxTaskGetStackHighWaterMark(this->threadHandle);
        }
        #endif

        #ifdef INCLUDE_eTaskGetState
        /**
         * @brief 获取当前线程的状态。
         * 
         * @return eTaskState 返回当前线程的状态，状态由eTaskState枚举类型编码。
         * 可以是eRunning, eReady, eBlocked, eSuspended, eDeleted等状态之一。
         * @note 该函数需要在FreeRTOSConfig.h中定义INCLUDE_eTaskGetState=1
         */
        eTaskState get_state(){
            if(this->threadHandle == nullptr) return eTaskState::eInvalid;
            return eTaskGetState(this->threadHandle);
        }
        #endif

        // 析构函数，如果线程句柄不为空，则删除线程。
        ~thread() {
            if (this->threadHandle != nullptr) {
                vTaskDelete(this->threadHandle);
            }
        }

    private:
        // 线程包装函数，用于FreeRTOS创建线程时调用。
        static void TaskWrapper(void *parameter) {
            thread *instance = static_cast<thread *>(parameter); // 将void指针转换为thread指针
            instance->func(instance->funcparam); // 调用成员函数并传递参数
            instance->threadHandle = nullptr; // 线程结束后，将句柄置空
            vTaskDelete(NULL); // 删除线程
        }

        // 线程句柄
        xTaskHandle threadHandle = nullptr; 
        // 线程要执行的函数对象
        std::function<void(ParamType)> func; 
        // 线程参数
        ParamType funcparam;
    };

    // ParamType为void的模板特化
    template <>
    class thread<void> {
    public:

        // 构造函数，接收一个无参数的函数对象。
        thread(std::function<void()> _func) : func(_func) {}

        /**
         * @description:线程启动
         * @return {*}
         * @Author: qingmeijiupiao
         * @param {char} *taskname 线程名称
         * @param {int} stack_size 线程堆栈大小
         * @param {UBaseType_t} priority 线程优先级
         * @param {int} core 线程所在核心 0-1 默认运行在任意核心
         */
        void start(const char *taskname=DEFAULT_TASK_NAME, int stack_size = DEFAULT_STACK_SIZE, UBaseType_t priority = DEFAULT_PRIORITY, int core = tskNO_AFFINITY) {
            if (this->threadHandle == nullptr) {
                xTaskCreatePinnedToCore(
                    TaskWrapper,
                    taskname,
                    stack_size,
                    this, // 传递this指针
                    priority,
                    &this->threadHandle,
                    core == tskNO_AFFINITY ? tskNO_AFFINITY : core);
            }
        }

        // 获取线程句柄。
        xTaskHandle get_Handle() {
            return this->threadHandle;
        }

        // 等待线程结束。
        void join() {
            while(this->threadHandle != nullptr){ // 循环直到线程句柄为空，即线程结束。
                vTaskDelay(1/ portTICK_PERIOD_MS); // 延迟一个tick周期，避免忙等。
            }
        }
        void stop(){ // 停止线程
            if (this->threadHandle != nullptr) { // 如果线程句柄不为空，则删除线程。
                vTaskDelete(this->threadHandle); // 删除线程
                this->threadHandle = nullptr; // 清空线程句柄
            }
        }
        #ifdef INCLUDE_uxTaskGetStackHighWaterMark//获取是否启用该函数s
        /**
         * @brief 获取线程的剩余栈大小
         * 
         * @return int 返回线程的剩余栈大小，以字节为单位
         * @note 该函数需要在FreeRTOSConfig.h中定义INCLUDE_uxTaskGetStackHighWaterMark=1
         * @warning 该函数可能会使系统暂时变得不可响应
         */
        int get_remaining_stack_size(){
            if(this->threadHandle == nullptr) return 0;
            return uxTaskGetStackHighWaterMark(this->threadHandle);
        }
        #endif

        #ifdef INCLUDE_eTaskGetState
        /**
         * @brief 获取当前线程的状态。
         * 
         * @return eTaskState 返回当前线程的状态，状态由eTaskState枚举类型编码。
         * 可以是eRunning, eReady, eBlocked, eSuspended, eDeleted等状态之一。
         * * @note 该函数需要在FreeRTOSConfig.h中定义INCLUDE_eTaskGetState=1
         */
        eTaskState get_state(){
            if(this->threadHandle == nullptr) return eTaskState::eInvalid;
            return eTaskGetState(this->threadHandle);
        }
        #endif
        // 析构函数，如果线程句柄不为空，则删除线程。
        ~thread() {
            if (this->threadHandle != nullptr) {
                vTaskDelete(this->threadHandle);
            }
        }


    private:
        // 线程包装函数
        static void TaskWrapper(void *parameter) {
            thread *instance = static_cast<thread *>(parameter);
            instance->func(); // 调用无参数的成员函数
            instance->threadHandle = nullptr;
            vTaskDelete(NULL);
        }
        // 线程句柄
        xTaskHandle threadHandle = nullptr;
        // 线程要执行的函数对象
        std::function<void()> func;
    };

} // namespace HXC

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