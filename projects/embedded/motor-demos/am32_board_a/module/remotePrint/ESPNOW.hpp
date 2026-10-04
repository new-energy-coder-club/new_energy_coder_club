/*
 * @LastEditors: qingmeijiupiao
 * @Description: 重庆邮电大学HXC战队ESP-NOW二次封装库,指定了发包格式
 * @Author: qingmeijiupiao
 * @LastEditTime: 2025-07-07 23:17:47
 */

#ifndef esp_now_hpp
#define esp_now_hpp
#include <Arduino.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include <esp_now.h>
#include <functional>
#include <map>
#include <list>

//默认数据包密钥
#define DEFAULT_SECRET_KEY 0xFEFE

//发送数据包失败最大重试次数
#define MAX_RETRY 5


/*↓↓↓↓声明↓↓↓↓*/

//数据包结构体
struct HXC_ESPNOW_data_pakage;

//MAC地址结构体
struct MAC_t{
  uint8_t mac[6];
  //默认构造函数
  MAC_t(){memset(this->mac,0xFF,6);}
  //构造函数,从6个字节构造
  MAC_t(uint8_t mac1,uint8_t mac2,uint8_t mac3,uint8_t mac4,uint8_t mac5,uint8_t mac6){ mac[0]=mac1;mac[1]=mac2;mac[2]=mac3;mac[3]=mac4;mac[4]=mac5;mac[5]=mac6; }
  //构造函数,从数组构造
  MAC_t(uint8_t* mac){ memcpy(this->mac,mac,6); }
  //索引运算符
  uint8_t operator[](int i) { return mac[i]; }
  //赋值运算符
  void operator=(uint8_t* mac) { memcpy(this->mac,mac,6); }
  //比较运算符
  bool operator==(MAC_t other) { return memcmp(this->mac,other.mac,6)==0; }
  //类型转换
  operator uint8_t*() { return mac; }
  operator const uint8_t*() const { return mac; }
};

//广播地址
MAC_t broadcastMacAddress(0xFF,0xFF,0xFF,0xFF,0xFF,0xFF);

//回调函数
using callback_func =std::function<void(HXC_ESPNOW_data_pakage)>;


/**
 * @description: ESP-NOW初始化
 * @return {*}
 * @Author: qingmeijiupiao
 * @param {MAC_t} receive_MAC 接收数据的设备MAC 默认广播地址
 * @param {int} wifi_channel 使用的wifi信道 默认0
 */
void esp_now_setup(MAC_t receive_MAC=broadcastMacAddress,int wifi_channel=0);

//添加配对MAC
void add_esp_now_peer_mac(MAC_t mac);

//删除配对MAC
void remove_esp_now_peer_mac(MAC_t mac);

//检查是否是配对MAC
bool is_esp_now_peer(MAC_t mac);


/**
 * @description: 发送经过封装的ESP-NOW数据包
 * @return {esp_err_t} 正确返回ESP_OK
 * @Author: qingmeijiupiao
 * @param {String} name 数据包名称
 * @param {uint8_t*} data 数据
 * @param {int} datalen 数据长度
 * @param {MAC_t} receive_MAC 接收数据的设备MAC 默认广播地址
 */
esp_err_t esp_now_send_package(String name,uint8_t* data,int datalen,MAC_t receive_MAC=broadcastMacAddress);


/**
 * @description: 添加回调函数,回调函数会在接收到数据包时自动运行
 * @return {*}
 * @Author: qingmeijiupiao
 * @param {String} package_name 数据包名称
 * @param {callback_func} func 回调函数,可使用函数指针或者lambda
 */
void add_esp_now_callback(String package_name,callback_func func);

//移除回调函数
void remove_esp_now_callback(String package_name);

//修改数据包密钥
void change_secret_key(uint16_t _secret_key);









/*↓↓↓↓定义↓↓↓↓*/

//数据包密钥
static uint16_t secret_key=DEFAULT_SECRET_KEY;

//数据包格式
struct HXC_ESPNOW_data_pakage {
  uint16_t header_code=secret_key;//数据包头,作为密钥使用
  uint8_t name_len;
  uint8_t data_len;
  String package_name;
  uint8_t data[256];
  //添加名字
  void add_name(String _name){
    package_name=_name;
    name_len=package_name.length();
  }
  //添加数据
  void add_data(uint8_t* _data,int _datalen){
    data_len=_datalen;
    for(int i=0;i<_datalen;i++){
      data[i]=_data[i];
    }
  }
  //获取数据
  void get_data(uint8_t* _data){
    _data[0]=header_code&0xFF;
    _data[1]=header_code>>8;
    _data[2]=package_name.length();
    _data[3]=data_len;
    memcpy(_data+4,package_name.c_str(),package_name.length());
    memcpy(_data+4+package_name.length(),data,data_len);
  }

  //解码数组到结构体对象
  void decode(uint8_t* _data,int _datalen){
    header_code=*((uint16_t*)_data);
    name_len=_data[2];
    data_len=_data[3];
    package_name="";
    for(int i=0;i<name_len;i++){
      package_name+=char(_data[4+i]);
    }
    for(int i=0;i<data_len;i++){
      data[i]=_data[4+name_len+i];
    }
  }
  //获取数据包长度
  int get_len(){
    return 4+name_len+data_len;
  }

};


static std::list<MAC_t> peer_mac_list;//配对MAC地址列表

static std::map<String, callback_func> callback_map;//回调函数map

//添加回调函数
void add_esp_now_callback(String package_name,callback_func func){
  callback_map[package_name]=func;
}

//移除回调函数
void remove_esp_now_callback(String package_name){
  callback_map.erase(package_name);
};

static HXC_ESPNOW_data_pakage re_data;//数据包缓存对象

//是否连接的标志
bool is_conect=false;

//接收数据时的回调函数，收到数据时自动运行
void OnESPNOWDataRecv(const uint8_t *mac, const uint8_t *data, int len) {
  //检查是否是数据包
  if(len<4) return;
  if(*(uint16_t*)data!=secret_key) return;
  re_data.decode((uint8_t*)data,len);
    //检查是否是需要运行回调函数的数据包
  if(callback_map.count( re_data.package_name )!=0){
    callback_map[re_data.package_name](re_data);
  }
  is_conect=true;
}

//配对信息对象
static esp_now_peer_info_t peerInfo;

//是否初始化的标志
static bool is_setup=false;

//ESP-NOW初始化
void esp_now_setup(MAC_t receive_MAC,int wifi_channel){
  
  if(is_setup) return;
  is_setup=true;

  if(WiFi.getMode()==WIFI_MODE_NULL){
    WiFi.mode(WIFI_STA);
  }
  
  if (esp_now_init() != ESP_OK) {
      Serial.println("ESP-NOW initialization failed");
      return;
  }
  if(wifi_channel!=0){
    peerInfo.channel = wifi_channel;
  }
  peerInfo.ifidx = WIFI_IF_STA;
  memcpy(peerInfo.peer_addr, receive_MAC, 6);
  peer_mac_list.push_back(receive_MAC);
  esp_now_add_peer(&peerInfo);

  if(receive_MAC!=broadcastMacAddress){
    memcpy(peerInfo.peer_addr, broadcastMacAddress, 6);
    esp_now_add_peer(&peerInfo);
  }
  esp_now_register_recv_cb(OnESPNOWDataRecv);
} 

//添加配对MAC
void add_esp_now_peer_mac(MAC_t mac){
  memcpy(peerInfo.peer_addr, mac, 6);
  peer_mac_list.push_back(mac);
  esp_now_add_peer(&peerInfo);
};

//删除配对MAC
void remove_esp_now_peer_mac(MAC_t mac){
  peer_mac_list.remove(mac);
  esp_now_del_peer(mac);
};

//检查是否是配对MAC
bool is_esp_now_peer(MAC_t mac){

  //检查是否是配对MAC
  auto item=std::find(peer_mac_list.begin(),peer_mac_list.end(),mac);

  //没有找到
  if(item==peer_mac_list.end()) return false;

  //找到了
  return true;
}

//通过espnow发送数据包
esp_err_t esp_now_send_package(String name,uint8_t* data,int datalen,MAC_t receive_MAC){
  HXC_ESPNOW_data_pakage send_data;
  send_data.add_name(name);
  send_data.add_data(data,datalen);
  uint8_t send_data_array[send_data.get_len()];
  send_data.get_data(send_data_array);
  //发送
  for(int i=0;i<MAX_RETRY;i++){
    auto err = esp_now_send(receive_MAC,send_data_array,send_data.get_len());
    if (err == ESP_OK)  return ESP_OK;
    delay(20);
  }
  return ESP_FAIL;
}

//修改数据包密钥
void change_secret_key(uint16_t _secret_key){
  secret_key=_secret_key;
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