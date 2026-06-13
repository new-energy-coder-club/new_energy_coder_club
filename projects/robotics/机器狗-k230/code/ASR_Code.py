import Hiwonder
import time
import Hiwonder_IIC
from HW_MechDog import MechDog

# 初始化MechDog对象
mechdog = MechDog()
# 创建IIC2对象
i2c2 = Hiwonder_IIC.IIC(2)
# 创建语音识别模块对象
asr = Hiwonder_IIC.asr_module(i2c2)


# 设置MechDog初始姿态
mechdog.set_default_pose()

# 延时函数，参数为延时的时间（单位：秒）
time.sleep(1)


# 主函数
def main():
  backward = 0
  flag_move_action = 1
  
  while True:
    # 获取识别结果，无结果则返回0
    rec = asr.getResult()
    
    if rec == 0:
      time.sleep_ms(100)
      continue
    
    if rec < 10: # move
      if flag_move_action != 1:
        flag_move_action = 1
        backward = 0
        mechdog.set_default_pose()
        time.sleep_ms(1000)
      
      # 识别到前进
      if rec == 1: # forward
        if backward > 0:
          backward = 0
          mechdog.set_pose([0,0,0],[0,0,0],200)
          time.sleep_ms(300)
        print("go")
        mechdog.move(90,0)
      # 识别到后退
      elif rec == 2: # backward
        if backward == 0:
          backward = 1
          mechdog.set_pose([-10,0,-5],[0,0,0],200)
          time.sleep_ms(300)
        print("back")
        mechdog.move(-80,0)
      # 识别到左转
      elif rec == 3: # left
        if backward > 0:
          backward = 0
          mechdog.set_pose([0,0,0],[0,0,0],200)
          time.sleep_ms(300)
        print("left")
        mechdog.move(80,50)
      # 识别到右转
      elif rec == 4: # right
        if backward > 0:
          backward = 0
          mechdog.set_pose([0,0,0],[0,0,0],200)
          time.sleep_ms(300)
        print("right")
        mechdog.move(80,-50)
        
      elif rec == 9:
        if backward > 0:
          mechdog.set_pose([0,0,0],[0,0,0],200)
          time.sleep_ms(300)
        print("stop")
        mechdog.move(0,0)
        
    elif rec >= 10: # action
      if flag_move_action != 2:
        flag_move_action = 2
        mechdog.move(0,0)
        time.sleep_ms(500)
        
      if rec == 10:
        print("stand")
        mechdog.set_default_pose()
        time.sleep_ms(1000)
      elif rec == 11:
        print("go prone")
        mechdog.action_run("go_prone")
        time.sleep(1)
      elif rec == 12:
        print("sit dowm")
        mechdog.action_run("sit_dowm")
    
    time.sleep_ms(100)

# 执行主函数
main()

