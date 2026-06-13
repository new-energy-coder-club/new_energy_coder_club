
# Hiwonder MechDog
# MicroPython - APP Bluetooth control

import Hiwonder
import time
import Hiwonder_IIC
from Hiwonder_BLE import BLE
from HW_MechDog import MechDog
import machine

_BLE_REC_DATA = 0
_COMMAND = 0
_SEND_DATA = 0
_DATA = 0
_distance = 0
_SONER_DISTANCE = 0
_self_balancing_flag = 0
_RUN_STEP = 0
_obstacle_avoidance_flag = 0
_Pitch_angle = 0
_Roll_angle = 0
_ACTION_TYPE = 0
_ACTION_NUM = 0
_RUN_DIR = 0
_REC_PARSE_VALUE = []
_High_mm = 0
_ARM_ACTION = 0
ble = None
# default_pose = ((74.00, 46.0, -80), (-60.00, 46.0, -80), (74.00, -46.0, -80), (-60.00, -46.0, -80))
default_pose = ((75.00, 46.0, -80), (-57.00, 46.0, -80), (75.00, -46.0, -80), (-57.00, -46.0, -80))
mac = machine.unique_id()
doghw = MechDog(default_pose)
i2c1 = Hiwonder_IIC.IIC(1)
i2csonar = Hiwonder_IIC.I2CSonar(i2c1)
led = Hiwonder.LED()

time.sleep(1)

def start_main():
  global ble
  global _BLE_REC_DATA
  global _COMMAND
  global _SEND_DATA
  global _DATA
  global _distance
  global _SONER_DISTANCE
  global _self_balancing_flag
  global _RUN_STEP
  global _obstacle_avoidance_flag
  global _Pitch_angle
  global _Roll_angle
  global doghw
  global _ACTION_TYPE
  global _ACTION_NUM
  global _RUN_DIR
  global _REC_PARSE_VALUE
  global _High_mm
  global _ARM_ACTION
  
  dir_flag = 1
  while True:
    if ble.is_connected():
      if ble.contains_data("CMD"):
        _BLE_REC_DATA = ble.read_uart_cmd()
        if not _BLE_REC_DATA:
          continue
        _REC_PARSE_VALUE = ble.parse_uart_cmd(_BLE_REC_DATA)
        _COMMAND = _REC_PARSE_VALUE[0]
        _COMMAND = int(_COMMAND)
        if (_COMMAND==6):
          _SEND_DATA = "CMD|6|{}|$".format(Hiwonder.Battery_power())
          ble.send_data(_SEND_DATA)
          continue
        if (_COMMAND==4):
          _DATA = int(_REC_PARSE_VALUE[1])
          if (_DATA==1):
            _distance = round((_SONER_DISTANCE*10))
            if (_distance>5000):
              _distance = 5000
            _SEND_DATA = "CMD|4|{}|$".format(_distance)
            ble.send_data(_SEND_DATA)
          elif ((_DATA==2) and (_self_balancing_flag==0)):
            if ((int(_REC_PARSE_VALUE[2]))==1):
              doghw.set_default_pose(default_pose)
              _Pitch_angle = 0
              _Roll_angle = 0
              _High_mm = 0
              time.sleep(1)
              _RUN_STEP = 41
            else:
              _RUN_STEP = 40
          elif (_DATA==3):
            i2csonar.setRGB(0,(int(_REC_PARSE_VALUE[2])),(int(_REC_PARSE_VALUE[3])),(int(_REC_PARSE_VALUE[4])))
          continue
        if ((_COMMAND==1) and (_obstacle_avoidance_flag==0)):
          _DATA = int(_REC_PARSE_VALUE[1])
          if (_DATA==3):
            _DATA = int(_REC_PARSE_VALUE[2])
            if (_DATA==1):
              doghw.set_default_pose(default_pose)
              _Pitch_angle = 0
              _Roll_angle = 0
              _High_mm = 0
              time.sleep(1)
              _RUN_STEP = 131
            else:
              _RUN_STEP = 130
          if ((_obstacle_avoidance_flag==0) and (_self_balancing_flag==0)):
            if (_DATA==1):
              _DATA = int(_REC_PARSE_VALUE[2])
              if (_DATA==1):
                if (_Roll_angle<17):
                  _Roll_angle+=1
                  doghw.transform([0, 0, 0], [-1, 0, 0], 80)
              else:
                if (_Roll_angle>-17):
                  _Roll_angle-=1
                  doghw.transform([0, 0, 0], [1, 0, 0], 80)
            if (_DATA==2):
              _DATA = int(_REC_PARSE_VALUE[2])
              if (_DATA==1):
                if (_Pitch_angle<17):
                  _Pitch_angle+=1
                  doghw.transform([0, 0, 0], [0, 1, 0], 80)
              else:
                if (_Pitch_angle>-17):
                  _Pitch_angle-=1
                  doghw.transform([0, 0, 0], [0, -1, 0], 80)
            if (_DATA==4):
              _DATA = int(_REC_PARSE_VALUE[2])
              if (_DATA==1):
                if (_High_mm < 15):
                  _High_mm += 1
                  doghw.transform([0, 0, 1], [0, 0, 0], 80)
              else:
                if _High_mm > -25:
                  _High_mm -= 1
                  doghw.transform([0, 0, -1], [0, 0, 0], 80)
            if (_DATA==5):
              doghw.set_default_pose(default_pose)
              _Pitch_angle = 0
              _Roll_angle = 0
              _High_mm = 0
              time.sleep(1)
            continue
        if (_COMMAND==2) and (_obstacle_avoidance_flag==0) and (_self_balancing_flag==0):
          _RUN_STEP = 2
          _ACTION_TYPE = int(_REC_PARSE_VALUE[1])
          _ACTION_NUM = int(_REC_PARSE_VALUE[2])
        if (_COMMAND==3) and (_obstacle_avoidance_flag==0) and (_self_balancing_flag==0):
          _RUN_STEP = 3
          _RUN_DIR = int(_REC_PARSE_VALUE[1])
          if _RUN_DIR < 6:
            if dir_flag != 1:
              dir_flag = 1
              doghw.transform([10 , 0 , 0] , [0 , 0 , 0] , 100)
          else:
            if dir_flag != -1:
              dir_flag = -1
              doghw.transform([-10 , 0 , 0] , [0 , 0 , 0] , 100)
        if (_COMMAND==7):
          _ARM_ACTION = int(_REC_PARSE_VALUE[1])
      else:
        time.sleep(0.03)

def start_main1():
  global ble
  global _SONER_DISTANCE
  global _self_balancing_flag
  global _RUN_STEP
  global _obstacle_avoidance_flag
  global doghw
  global _ACTION_TYPE
  global _ACTION_NUM
  global _RUN_DIR
  global i2csonar
  global _Pitch_angle
  global _Roll_angle
  global _High_mm

  step = 0
  while True:
    if (step==0):
      step = _RUN_STEP
      _RUN_STEP = 0
      time.sleep(0.05)
    else:
      if (step==41):
        _obstacle_avoidance_flag = 1
        forward_flag = 1
        while True:
          if ((_RUN_STEP==40) or (_obstacle_avoidance_flag==0)):
            _obstacle_avoidance_flag = 0
            doghw.move(0,0)
            i2csonar.setRGB(0,0x33,0x33,0xff)
            if forward_flag == 0:
                forward_flag = 1
                doghw.transform([10 , 0 , 0] , [0 , 0 , 0] , 100)
            time.sleep(1)
            break
          if (_SONER_DISTANCE<10):
            i2csonar.setRGB(0,0xff,0x00,0x00)
            if forward_flag == 1:
              forward_flag = 0
              doghw.transform([-10 , 0 , 0] , [0 , 0 , 0] , 100)
            doghw.move(-40,0)
            for count in range(30):
              if (_RUN_STEP==40):
                break
              time.sleep(0.1)
          else:
            if forward_flag == 0:
                forward_flag = 1
                doghw.transform([10 , 0 , 0] , [0 , 0 , 0] , 100)
            if (_SONER_DISTANCE<40):
              i2csonar.setRGB(0,0xff,0xcc,0x00)
              doghw.move(80,-50)  
              for count in range(50):
                if (_RUN_STEP==40):
                  break
                time.sleep(0.1)
            else:
              i2csonar.setRGB(0,0xcc,0x33,0xcc)
              doghw.move(120,0)
          time.sleep(0.02)
      if (step==131):
        _self_balancing_flag = 1
        doghw.homeostasis(True)
        time.sleep(2)
        while True:
          if (_RUN_STEP==130):
            _self_balancing_flag = 0
            doghw.homeostasis(False)
            time.sleep(2)
            doghw.set_default_pose(default_pose, duration = 500)
            break
          if not (doghw.read_homeostasis_status()):
            ble.send_data("CMD|1|3|0|$")
            _self_balancing_flag = 0
            time.sleep(1)
            doghw.set_default_pose(default_pose, duration = 500)
            break
      if (step==2):
        if (_ACTION_TYPE==1):
          doghw.set_default_pose(default_pose, duration = 500)
          _Pitch_angle = 0
          _Roll_angle = 0
          _High_mm = 0
          time.sleep(1)
          dong_zuo_zu_yun_xing(_ACTION_NUM)
        else:
          doghw.set_default_pose(default_pose, duration = 500)
          _Pitch_angle = 0
          _Roll_angle = 0
          _High_mm = 0
          time.sleep(1)
          doghw.action_run(str(_ACTION_NUM))
      if (step==3):
        while True:
          if (_RUN_DIR==0):
            doghw.move(0,0)
            break
          elif (_RUN_DIR==1):
            doghw.move(80,-40)
          elif (_RUN_DIR==2):
            doghw.move(90,-25)
          elif (_RUN_DIR==3):
            doghw.move(120,0)
          elif (_RUN_DIR==4):
            doghw.move(90,25)
          elif (_RUN_DIR==5):
            doghw.move(80,40)
          elif (_RUN_DIR==6):
            doghw.move(-40,-20)
          elif (_RUN_DIR==7):
            doghw.move(-40,0)
          elif (_RUN_DIR==8):
            doghw.move(-40,20)
      step = 0


action_list = { 1:"left_foot_kick" ,  2:"right_foot_kick_2" ,   3:"stand_four_legs",
                4:"sit_dowm" ,        5:"go_prone" ,          6:"stand_two_legs" ,
                7:"handshake" ,       8:"scrape_a_bow" ,      9:"nodding_motion" ,
                10:"boxing" ,         11:"stretch_oneself" ,  12:"pee" ,
                13:"press_up" ,       14:"rotation_pitch" ,   15:"rotation_roll" }

def dong_zuo_zu_yun_xing(dong_zuo):
  global doghw
  if (dong_zuo <= 15):
    doghw.action_run(action_list[dong_zuo])
    time.sleep(2)

def start_main2():
  global _SONER_DISTANCE
  global i2csonar
  global _ARM_ACTION
  sonar_tick = 0
  arm_tick = 0
  arm_step = 0
  time.sleep(2)
  while True:
    if time.ticks_ms() > sonar_tick:
      sonar_tick = time.ticks_ms() + 80
      _SONER_DISTANCE = i2csonar.getDistance()
    if time.ticks_ms() > arm_tick:
      if arm_step == 0:
        if _ARM_ACTION == 0:
          arm_tick = time.ticks_ms() + 100
        elif _ARM_ACTION == 6: # capture
          arm_step = 1
        elif _ARM_ACTION == 7: # lay down
          arm_step = 4
      elif arm_step == 1:  # capture step
        doghw.set_servo(11,1000,500)
        doghw.set_servo(10,1500,1000)
        doghw.set_servo(9,2300,1000)
        arm_tick = time.ticks_ms() + 1200
        arm_step = 2
      elif arm_step == 2:
        doghw.set_servo(11,1350,500)
        arm_tick = time.ticks_ms() + 600
        arm_step = 3
      elif arm_step == 3:
        doghw.set_servo(10,500,1000)
        doghw.set_servo(9,500,1000)
        arm_tick = time.ticks_ms() + 1500
        arm_step = 0
        _ARM_ACTION = 0
      elif arm_step == 4:  # lay down step
        doghw.set_servo(10,1500,1000)
        doghw.set_servo(9,2300,1000)
        arm_tick = time.ticks_ms() + 1200
        arm_step = 5
      elif arm_step == 5:
        doghw.set_servo(11,1200,500)
        arm_tick = time.ticks_ms() + 600
        arm_step = 6
      elif arm_step == 6:
        doghw.set_servo(11,1500,1500)
        doghw.set_servo(10,500,1000)
        doghw.set_servo(9,500,1000)
        arm_tick = time.ticks_ms() + 1200
        arm_step = 0
        _ARM_ACTION = 0
    time.sleep(0.08)


led.off()
ble = BLE(BLE.MODE_BLE_SLAVE,"MechDog_{:02X}".format(mac[5]))
Hiwonder.startMain(start_main)
Hiwonder.startMain(start_main1)
Hiwonder.startMain(start_main2)



