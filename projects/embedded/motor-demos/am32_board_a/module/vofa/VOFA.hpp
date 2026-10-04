#ifndef VOFA_HPP
#define VOFA_HPP
#include "Arduino.h"
#include <map>
#include <list>
class VOFA_float{
    public:
    VOFA_float(String _name,float default_value){
        this->name=_name;
        this->value=default_value;
        name_to_value_map[this->name]=this;

    };
    // 支持同时监听两个流（主 + 辅），任一流收到命令都会被解析
    // 例如：setup(Serial0, &Serial)  → UART0 和 USB 都能接收命令
    static void setup(Stream& serial = Serial, Stream* aux = nullptr){
        io_stream=&serial;
        io_stream_aux=aux;
        if(!is_setup){
            is_setup=true;
            xTaskCreate(read_loop,"read_loop",8192,NULL,5,NULL);
        }
    }
    operator float(){
        return value;
    }
    float read(){
        return value;
    }

    static void add_on_value_change_callback(std::function<void(String,float)> callback){
        on_value_change_callback_list.push_back(callback);
    }
    protected:
    float value;
    String name;
    static std::map<String, VOFA_float*>name_to_value_map;
    static std::list<std::function<void(String,float)>>on_value_change_callback_list;
    static bool is_setup;
    static Stream* io_stream;
    static Stream* io_stream_aux;

    // 单行命令解析 + 分派；reply_stream 指定回复目的流（来源流）
    static void process_line(String str, Stream* reply_stream){
        str.trim();
        if(str.length()==0) return;

        // 解析格式: "NAME [VALUE]"
        // 支持: "F10"  "F 10"  "F     10"  "F"（纯命令无值）
        String name;
        float value = 1.0f;

        str.toLowerCase();

        int split_index = -1;
        for (int i = 0; i < (int)str.length(); i++) {
            char c = str.charAt(i);
            if (c == ' ' || c == '-' || (c >= '0' && c <= '9')) {
                split_index = i;
                break;
            }
        }

        if (split_index < 0) {
            name = str;
        } else {
            name = str.substring(0, split_index);
            String val_str = str.substring(split_index);
            val_str.trim();
            if (val_str.length() > 0) {
                value = val_str.toFloat();
            }
        }

        name.trim();
        if(name_to_value_map.find(name)!=name_to_value_map.end()){
            name_to_value_map[name]->value=value;
        }else if(reply_stream != nullptr){
            reply_stream->println("VOFA_float: "+name+" not found");
        }
        if(on_value_change_callback_list.size()!=0){
            for(std::function<void(String,float)> callback:on_value_change_callback_list){
                callback(name,value);
            }
        }
    }

    // 从单个流读取并处理一行（若有可用数据）
    static bool poll_stream(Stream* s){
        if(s==nullptr || s->available()<=0) return false;
        String str = s->readStringUntil('\n');
        process_line(str, s);
        return true;
    }

    static void read_loop(void* p){
        while(1){
            const bool got_main = poll_stream(io_stream);
            const bool got_aux  = poll_stream(io_stream_aux);
            if(!got_main && !got_aux){
                delay(1);
            }
        }
    };

};
bool VOFA_float::is_setup=false;
Stream* VOFA_float::io_stream=nullptr;
Stream* VOFA_float::io_stream_aux=nullptr;
std::map<String, VOFA_float*>VOFA_float::name_to_value_map;
std::list<std::function<void(String,float)>>VOFA_float::on_value_change_callback_list;

#endif
