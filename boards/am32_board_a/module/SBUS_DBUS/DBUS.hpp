#ifndef DBUS_HPP
#define DBUS_HPP
#include <Arduino.h>

enum DBUS_CHANNEL {
  LEFT_X = 0,
  LEFT_Y = 1,
  RIGHT_X = 2,
  RIGHT_Y = 3,
  s1=4,
  s2=5,
  MOUSE_X=6,
  MOUSE_Y=7,
  MOUSE_Z=8,
  MOUSE_LEFT_BUTTON=9,
  MOUSE_RIGHT_BUTTON=10,
  BUTTON_W=11,
  BUTTON_S=12,
  BUTTON_A=13,
  BUTTON_D=14,
  BUTTON_Q=15,
  BUTTON_E=16,
  BUTTON_SHIFT=17,
  BUTTON_CTRL=18
};

class DBUS {
  public:
  DBUS(const DBUS &obj) = delete;
  DBUS &operator=(const DBUS &obj) = delete;
	DBUS(uint8_t pin, HardwareSerial *serial) {
		_pin = pin;
		_serial = serial;
	};
	DBUS(uint8_t pin) {
		_pin = pin;
		_serial = &Serial2;
	};
	DBUS() {
		_serial = &Serial2;
		_pin = 6;
	};

	void setup() {
		pinMode(_pin, INPUT);
		_serial->begin(100000, SERIAL_8E2, _pin, 38);
        _serial->setRxBufferSize(18*20);
		memset(raw_data, 0, sizeof(raw_data));
		memset(channel_data, 0, sizeof(channel_data));
		xTaskCreate(loop_task, "loop_task", 4096, this, 2, NULL);
	};
	uint16_t get_left_y(){
    return channel_data[3];
  }

  uint16_t get_right_y(){
    return channel_data[1];
  }

  uint16_t get_left_x(){
    return channel_data[2];
  }

  uint16_t get_right_x(){
    return channel_data[0];
  }
  float get_channel_data(DBUS_CHANNEL channel){
    switch (channel)
    {
    case LEFT_X:
      return float(channel_data[2]-1024)/1320.f;
    case LEFT_Y:
      return float(channel_data[3]-1024)/1320.f;
    case RIGHT_X:
      return float(channel_data[0]-1024)/1320.f;
    case RIGHT_Y:
      return float(channel_data[1]-1024)/1320.f;
    case s1:
      return this->S1;
    case s2:
      return this->S2;
    case MOUSE_X:
      return this->mouse_x/32767.f;
    case MOUSE_Y:
      return this->mouse_y/32767.f;
    case MOUSE_Z:
      return this->mouse_z/32767.f;
    case MOUSE_LEFT_BUTTON:
      return this->mouse_left_button;
    case MOUSE_RIGHT_BUTTON:
      return this->mouse_right_button;
    case BUTTON_W:
      return this->button_W;
    case BUTTON_S: 
      return this->button_S;
    case BUTTON_A:
      return this->button_A;
    case BUTTON_D:
      return this->button_D;
    case BUTTON_Q:
      return this->button_Q;
    case BUTTON_E:
      return this->button_E;
    case BUTTON_SHIFT:
      return this->button_Shift;
    case BUTTON_CTRL:
      return this->button_Ctrl;
    default:
      break;
    }
  }
  protected:
  static void loop_task(void *p) {
    DBUS *obj = (DBUS *)p;
    auto check_S1_data=[](uint8_t s1byte){
        int value=((s1byte >> 4) & 0x000C) >> 2;
        return value<4&&value>0;
    };
    auto check_S2_data=[](uint8_t s2byte){
        int value=(s2byte >> 4) & 0x0003;
        return value<4&&value>0;
    };


    //检查S1和S2的值来对齐字节流
    auto data_check =[&](){
        if (obj->_serial->available() < 36) {
            delay(1);
        }
        while(!check_S1_data(obj->_serial->read())){
            if(check_S2_data(obj->_serial->peek())){
                for(int i=0;i<13;i++){
                    obj->_serial->read();
                }
                break;
            }
            obj->_serial->read();
        }
    };
        
		data_check();
		while (true) {
      if (obj->_serial->available() < 18) {
				delay(1);
				continue;
			}
      obj->_serial->readBytes(obj->raw_data, 18);
      obj->channel_data[0]=((int16_t)obj->raw_data[0] | ((int16_t)obj->raw_data[1] << 8)) & 0x07FF;
      obj->channel_data[1]=(((int16_t)obj->raw_data[1] >> 3) | ((int16_t)obj->raw_data[2] << 5)) & 0x07FF;

      obj->channel_data[2]= (((int16_t)obj->raw_data[2] >> 6) | ((int16_t)obj->raw_data[3] << 2) |((int16_t)obj->raw_data[4] << 10)) & 0x07FF;
      obj->channel_data[3]= (((int16_t)obj->raw_data[4] >> 1) | ((int16_t)obj->raw_data[5]<<7)) & 0x07FF;

      obj->mouse_x=*((int16_t*)(obj->raw_data+6));
      obj->mouse_y=*((int16_t*)(obj->raw_data+8));
      obj->mouse_z=*((int16_t*)(obj->raw_data+10));
      obj->mouse_left_button=*(bool*)(obj->raw_data+12);
      obj->mouse_right_button=*(bool*)(obj->raw_data+13);
      uint8_t button_byte= obj->raw_data[14];
      obj->button_W=button_byte & 0x01;
      obj->button_S=button_byte & 0x02;
      obj->button_A=button_byte & 0x04;
      obj->button_D=button_byte & 0x08;
      obj->button_Q=button_byte & 0x10;
      obj->button_E=button_byte & 0x20;
      obj->button_Shift=button_byte & 0x40;
      obj->button_Ctrl=button_byte & 0x80;
    }
	}
	bool is_first = true;
	uint8_t _pin;
	HardwareSerial *_serial;
	uint8_t raw_data[18];
	uint16_t channel_data[4];
  uint8_t S1=0;
  uint8_t S2=0;
  int16_t mouse_x=0;
  int16_t mouse_y=0;
  int16_t mouse_z=0;
  bool mouse_left_button=0;
  bool mouse_right_button=0;
  bool button_W=0;
  bool button_S=0;
  bool button_A=0;
  bool button_D=0;
  bool button_Q=0;
  bool button_E=0;
  bool button_Shift=0;
  bool button_Ctrl=0;
	uint8_t flag;
};

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