# ESP-NOW 二次封装库

重庆邮电大学HXC战队ESP-NOW二次封装库，提供了简化的ESP-NOW通信接口。

## 功能特性

- 简化的数据包封装格式
- 支持多设备配对管理
- 支持回调函数机制
- 自动重发机制
- 数据包校验

## 快速开始

### 1. 初始化

```cpp
#include "esp_now.hpp"

void setup() {
  // 初始化ESP-NOW，默认使用广播地址和信道0
  esp_now_setup();
  
  // 或者指定接收设备MAC和信道
  MAC_t targetMac(0x12,0x34,0x56,0x78,0x9A,0xBC);
  esp_now_setup(targetMac, 6); // 使用信道6
}
```

### 2. 发送数据

```cpp
void loop() {
  uint8_t data[] = {1, 2, 3, 4};
  
  // 发送数据包
  esp_err_t result = esp_now_send_package("test", data, 4);
  
  if(result == ESP_OK) {
    Serial.println("发送成功");
  } else {
    Serial.println("发送失败");
  }
  
  delay(1000);
}
```

### 3. 接收数据

```cpp
// 在setup中添加回调函数
void setup() {
  esp_now_setup();
  
  // 添加数据包接收回调
  add_esp_now_callback("test", [](HXC_ESPNOW_data_pakage pkg) {
    Serial.print("收到数据包: ");
    Serial.println(pkg.package_name);
    
    for(int i=0; i<pkg.data_len; i++) {
      Serial.print(pkg.data[i]);
      Serial.print(" ");
    }
    Serial.println();
  });
}
```

## API参考

### 初始化函数

```cpp
void esp_now_setup(MAC_t receive_MAC=broadcastMacAddress, int wifi_channel=0);
```

### 数据发送

```cpp
esp_err_t esp_now_send_package(String name, uint8_t* data, int datalen, MAC_t receive_MAC=broadcastMacAddress);
```

### 配对管理

```cpp
void add_esp_now_peer_mac(MAC_t mac);
void remove_esp_now_peer_mac(MAC_t mac);
bool is_esp_now_peer(MAC_t mac);
```

### 回调管理

```cpp
void add_esp_now_callback(String package_name, callback_func func);
void remove_esp_now_callback(String package_name);
```

### 其他

```cpp
void change_secret_key(uint16_t _secret_key);
```

## 数据包格式

数据包采用以下格式：

| 字段         | 长度         | 说明           |
| ------------ | ------------ | -------------- |
| header_code  | 2字节        | 数据包头(密钥) |
| name_len     | 1字节        | 数据包名称长度 |
| data_len     | 1字节        | 数据长度       |
| package_name | name_len字节 | 数据包名称     |
| data         | data_len字节 | 数据内容       |

## 注意事项

1. 默认使用广播地址(0xFF,0xFF,0xFF,0xFF,0xFF,0xFF)
2. 默认数据包密钥为0xFEFE，可通过`change_secret_key()`修改
3. 发送失败会自动重试，最大重试次数为5次
4. 接收回调函数会在接收到匹配的数据包时自动调用

## 示例代码

更多使用示例请参考项目中的examples目录。
