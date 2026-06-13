# 资料https://www.bearpi.cn/core_board/bearpi/bm/h63/
[EB25](https://lierda.feishu.cn/wiki/X360wInOjihWzukypNzc0Df5nHf?from=from_copylink)




# fbb_ws63开发指南



## 介绍

  fbb_ws63代码仓为支持ws63和ws63e解决方案SDK，该SDK包从统一开发平台FBB（Family Big Box，统一开发框架，统一API）构建而来，在该平台上开发的应用很容易被移植到其他星闪解决方案上，有效降低开发者门槛，缩短开发周期，支持开发者快速开发星闪产品。

## 购买渠道

|      序号      | 硬件资料                                                     | 介绍          |
| :------------: | ------------------------------------------------------------ | ------------- |
| 1 | [购买链接](https://www.ickey.cn/detail/1003001013187550/Q353333N1100.html) | ws63解决方案  |
| 2 | [购买链接](https://www.ickey.cn/detail/1003001013187551/Q353333N1100E.html) | ws63E解决方案 |
| 3 | [模组购买链接](https://gitee.com/link?target=https%3A%2F%2Fitem.taobao.com%2Fitem.htm%3Fid%3D821194904380) | 星闪WiFi6模组，邮票孔，无天线 |
| 4 | [模组购买链接](https://gitee.com/link?target=https%3A%2F%2Fitem.taobao.com%2Fitem.htm%3Fid%3D823544936579) | 星闪WiFi6模组，12：板载天线，12E：外置天线 |
| 5 | [模组购买链接](https://gitee.com/link?target=https%3A%2F%2Fitem.taobao.com%2Fitem.htm%3Fid%3D820900594332) | 星闪WiFi6模组，20：板载天线，20E：外置天线 |

## 支持的开发板

|                          开发板名称                          | 硬件资料                                                     | 软件资料         | 购买链接                                                     | 开发板介绍                                                   |
| :----------------------------------------------------------: | ------------------------------------------------------------ | :--------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| HiHope_NearLink_DK3863E_V03 ![输入图片说明](https://gitee.com/wu-luobin/fbb_ws63/raw/master/docs/pic/readme/image-20240809164437807.png)| [扩展板硬件资料](https://gitee.com/HiSpark/fbb_ws63/tree/master/docs/hardware/HiHope_NearLink_DK_WS63E_V03) | 参考示例教程章节 | [开发板购买链接](https://main.m.taobao.com/security-h5-detail/home?id=808369265492&spm=a2141.7631565.tbshopmod-guess_your_like.808369265492&scm=1007.18373.317678.0&pvid=fdb854bd-99a3-4b65-955b-392bdf0c083e&fromNormal=true) | 是一款高度集成的2.4GHz Wi-Fi 6 星闪多模开发板，支持Liteos、OpenHarmony轻量系统 |
| BearPi-Pico_H3863![输入图片说明](https://gitee.com/wu-luobin/fbb_ws63/raw/master/docs/pic/BearPi-Pico_H3863/bearpi_pico_h3863.png) | [扩展板硬件资料](https://gitee.com/HiSpark/fbb_ws63/tree/master/docs/hardware/BearPi-Pico_H3863) | 参考示例教程章节 | [开发板购买链接](https://item.taobao.com/item.htm?id=821386760379) | 是一款高度集成的2.4GHz Wi-Fi 6 星闪多模开发板，具有灵活的数字接口，集成高性能 32bit 微处理器（MCU），硬件安全引擎以及丰富的外设接口，外设接口包括 SPI、UART、I2C、PWM、GPIO，支持 6 路 13bit 分辨率 ADC，内置 SRAM 和合封 Flash，并支持在 Flash 上运行程序支持Liteos、OpenHarmony轻量系统 |
|  ![输入图片说明](https://gitee.com/wu-luobin/fbb_ws63/raw/master/vendor/Hqyj_Ws63/doc/HQYJ_WS63.png)| [扩展板硬件资料](https://gitee.com/HiSpark/fbb_ws63/blob/master/vendor/Hqyj_Ws63/doc/FS-WS63-%E5%8E%9F%E7%90%86%E5%9B%BEV2.pdf) | 参考示例教程章节 | [开发板购买链接](https://item.taobao.com/item.htm?id=892481769813) | 专为学习者设计的WS63鸿蒙星闪开发板，支持OpenHarmony，Liteos，多模通信（WiFi/星闪/蓝牙），丰富的板载资源、项目拓展模块与学习资料，可广泛应用于个人学习、高校教学、学生毕设、创新竞赛等 |

## 目录介绍

| 目录   | 介绍                                                 |
| ------ | ---------------------------------------------------- |
| docs   | 存放资料手册、IO复用关系表、硬件原理图、用户指南手册 |
| src    | SDK源码目录                                          |
| tools  | 开发工具及环境搭建指南                               |
| vendor | 存放对应开发板案例                                   |

## 快速上手

1. 开发环境搭建[参考tools目录README](https://gitee.com/HiSpark/fbb_ws63/tree/master/tools)
2. 资料手册、IO复用关系、用户手册指南表[参考docs/board目录README](https://gitee.com/HiSpark/fbb_ws63/tree/master/docs/board)
3. 硬件原理图[参考docs/hardware](https://gitee.com/HiSpark/fbb_ws63/tree/master/docs/hardware)

## 示例教程

HiHope_NearLink_DK3863E_V03提供了以下Demo供开发参考：

<table  width="990" border="0" cellpadding="0" cellspacing="0" style='border-collapse:collapse;table-layout:fixed;'>
 <tr height="18" style='height:13.50pt;'>
  <td width="140" x:str><strong>一级分类</strong></td>
  <td width="170" x:str><strong>子分类</strong></td>
  <td width="680" colspan="6" align="center" x:str><strong>应用示例</strong></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="5" style='height:27.00pt' x:str>
<strong>基础驱动</strong></td>
  <td x:str><strong>I2C</strong></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/src/application/samples/peripheral/i2c">I2C组件master端案例</a></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/src/application/samples/peripheral/i2c">I2C组件slave端案例</a></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/oled">SSD1306 OLED屏幕显示“Hello World”</a></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/environment">AHT20模块读取当前温湿度并显示在屏幕案例</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>SPI</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/src/application/samples/peripheral/spi">SPI组件master端案例</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/src/application/samples/peripheral/spi">SPI组件slave端案例</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/gyro">LSM6DSM模块读取横滚角、俯仰角、偏航角</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>UART</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/src/application/samples/peripheral/uart">UART轮询案例</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/src/application/samples/peripheral/uart">UART中断读取案例</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/uartdemo">开发板UART自发自收</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>PWM</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/src/application/samples/peripheral/pwm">PWM案例</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/beep">蜂鸣器案例</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>GPIO</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/buttondemo">按键案例</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/led">点亮LED灯案例</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/servo">实现SG92R舵机转动-90°、-45°、0°、45°、90°</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/tricolored">实现SK6812三色灯亮绿、红、蓝三种颜色</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/ultrasonic">超声波测距</a></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/trafficlight">交通灯案例</a></td>
 </tr>
  <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="5" style='height:27.00pt' x:str>
<strong>操作系统</strong></td>
  <td x:str><strong>Thread</strong></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/thread">线程使用案例</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>semaphore</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/semaphore">信号量使用案例</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
  <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>event</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/event">事件使用案例</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
  <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>message</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/message">消息队列使用案例</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
  <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>mutex</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/mutex">互斥锁使用案例</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
  <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>星闪</strong></td>
  <td x:str><strong>SLE</strong></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/sle_distribute_network">SLE配网</a></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/sle_led">通过SLE控制LED灯</a></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/sle_wifi_coexist">WiFi/SLE共存</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
 </tr>
  <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>BLE</strong></td>
  <td x:str><strong>BLE</strong></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
 </tr>
  <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>Wi-Fi</strong></td>
  <td x:str><strong>Wi-Fi</strong></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/wifista">Wi-Fi STA</a></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/wifiap">Wi-Fi AP</a></td>
  <td width="170" x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/wifidemo">Wi-Fi TCP/UDP测速</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>TIMER</strong></td>
  <td x:str><strong>定时器</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/timer">定时器</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>雷达</strong></td>
  <td x:str><strong>运动感知</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/radar_led">运动感知1.0</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>低功耗</strong></td>
  <td x:str><strong>低功耗</strong></td>
  <td width="170" x:str><a href=""></a></td>
  <td x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
  <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>端云协同</strong></td>
  <td x:str><strong>MQTT</strong></td>
  <td x:str><a href="https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/HiHope_NearLink_DK_WS63E_V03/demo/mqtt">华为云与开发板通过MQTT实现订阅、发布</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="4" style='height:27.00pt' x:str>
<strong>行业解决方案</strong></td>
  <td x:str><strong>鼠标</strong></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>键盘</strong></td>
  <td x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>车钥匙</strong></td>
  <td x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>遥控器</strong></td>
  <td x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
  <td ></td>
 </tr>
 </tr>
 <tr>
<![if supportMisalignedColumns]>
   <tr height="18" style="display:none;">
   </tr>
  <![endif]>
</table>
BearPi-Pico H3863提供了以下Demo供开发参考：

<table  width="990" border="0" cellpadding="0" cellspacing="0" style='border-collapse:collapse;table-layout:fixed;'>
 <tr height="18" style='height:13.50pt;'>
  <td width="140" x:str><strong>一级分类</strong></td>
  <td width="170" x:str><strong>子分类</strong></td>
  <td width="680" colspan="6" align="center" x:str><strong>应用示例</strong></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="6" style='height:27.00pt' x:str>
<strong>基础驱动</strong></td>
  <td x:str><strong>I2C</strong></td>
  <td width="170" x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/study/6.I2C%20%E9%A9%B1%E5%8A%A8OLED%E5%B1%8F%E5%B9%95%E6%B5%8B%E8%AF%95.html">I2C驱动OLED屏幕案例</a></td> <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>SPI</strong></td>
  <td x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/study/7.SPI%20%E9%A9%B1%E5%8A%A8OLED%E5%B1%8F%E5%B9%95%E6%B5%8B%E8%AF%95.html">SPI驱动OLED屏幕案例</a></td><td ></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
 </tr>
 <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>UART</strong></td>
  <td x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/study/5.UART%E6%95%B0%E6%8D%AE%E4%BC%A0%E8%BE%93%E6%B5%8B%E8%AF%95.html">开发板UART自发自收</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
  <td ></td>
 </tr> <tr height="18" style='height:13.50pt;'>
  <td x:str><strong>ADC</strong></td>
  <td x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/study/4.ADC%E9%87%87%E6%A0%B7%E6%B5%8B%E8%AF%95.html">ADC案例</a></td>  <td ></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
 </tr><tr height="18" style='height:13.50pt;'>
  <td x:str><strong>PWM</strong></td>
  <td x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/study/3.PWM%E8%BE%93%E5%87%BA%E6%B5%8B%E8%AF%95.html">PWM案例</a></td><td ></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td ></td>
 </tr><tr height="18" style='height:13.50pt;'>
  <td x:str><strong>GPIO</strong></td>
  <td x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/study/1.GPIO%E7%82%B9%E4%BA%AELED%E7%81%AF%E6%B5%8B%E8%AF%95.html">点亮LED灯案例</a></td>
  <td x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/study/2.GPIO%E6%8C%89%E9%94%AE%E4%B8%AD%E6%96%AD%E6%B5%8B%E8%AF%95.html">按键案例</a></td><td ></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
 </tr> <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>星闪</strong></td>
  <td x:str><strong>SLE</strong></td>
  <td width="170" x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/SLE%E4%B8%B2%E5%8F%A3%E9%80%8F%E4%BC%A0%E6%B5%8B%E8%AF%95.html">SLE串口透传</a></td>
  <td width="170" x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/SLE%E7%BD%91%E5%85%B3%E9%80%8F%E4%BC%A0%E6%B5%8B%E8%AF%95.html">SLE网关透传</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td> </tr>
  <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>BLE</strong></td>
  <td x:str><strong>BLE</strong></td>
    <td width="170" x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/BLE%E4%B8%B2%E5%8F%A3%E9%80%8F%E4%BC%A0%E6%B5%8B%E8%AF%95.html">BLE串口透传</a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td></tr>
  <tr height="18" style='height:13.50pt;'>
  <td width="140" align="center" rowspan="1" style='height:27.00pt' x:str>
<strong>Wi-Fi</strong></td>
  <td x:str><strong>Wi-Fi</strong></td>
  <td width="170" x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/Wi-Fi%20STA%20%E8%BF%9E%E6%8E%A5%E6%97%A0%E7%BA%BF%E7%83%AD%E7%82%B9%E6%B5%8B%E8%AF%95.html">Wi-Fi STA</a></td>
  <td width="170" x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/Wi-Fi%20SoftAP%20%E5%BC%80%E5%90%AF%E6%97%A0%E7%BA%BF%E7%83%AD%E7%82%B9%E6%B5%8B%E8%AF%95.html">Wi-Fi AP</a></td>
  <td width="170" x:str><a href="https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/Wi-Fi%20UDP%E5%AE%A2%E6%88%B7%E7%AB%AF%E6%B5%8B%E8%AF%95.html">Wi-Fi UDP客户端</a></td> <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td>
  <td width="170" x:str><a href=""></a></td></tr>
 </tr>
 <tr>
<![if supportMisalignedColumns]>
   <tr height="18" style="display:none;">
   </tr>
  <![endif]>
</table>
华清远见WS63鸿蒙星闪开发板提供了以下Demo供开发参考：

| 一级分类     | 子分类             | 应用示例                                                     |                                                              |                                                              |                                                              |
| :----------- | ------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **基础驱动** | **GPIO**           | [点亮LED灯案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/base_01_ledblink) |                                                              |                                                              |                                                              |
|              | **UART**           | [串口轮询、中断收发案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/base_02_uart) |                                                              |                                                              |                                                              |
|              | **I2C**            | [0.96寸OLED屏幕驱动案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/base_03_ssd1306) | [RGB灯珠驱动案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/base_04_rgb) | [SHT20传感器温湿度读取](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/base_05_sht20) | [AP3216读取光照、红外、人体接近数据](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/base_06_ap3216) |
|              | **SPI**            | [2.8寸LCD屏驱动案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/base_07_spi_lcd) |                                                              |                                                              |                                                              |
| **操作系统** | **Thread**         | [任务调度使用案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/kernel_01_task) |                                                              |                                                              |                                                              |
|              | **Timer**          | [软件定时器使用案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/kernel_02_timer) |                                                              |                                                              |                                                              |
|              | **Event**          | [事件使用案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/kernel_03_event) |                                                              |                                                              |                                                              |
|              | **Mutex**          | [互斥锁使用案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/kernel_04_mutex) |                                                              |                                                              |                                                              |
|              | **MutexSemaphore** | [互斥信号量使用案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/kernel_05_mutex_Semaphore) |                                                              |                                                              |                                                              |
|              | **SyncSemaphore**  | [同步信号量使用案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/kernel_06_sync_Semaphore) |                                                              |                                                              |                                                              |
|              | **CountSemaphore** | [计数型信号量使用案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/kernel_07_count_Semaphore) |                                                              |                                                              |                                                              |
|              | **MessgeQueue**    | [消息队列使用案例](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/kernel_08_message_queque) |                                                              |                                                              |                                                              |
| **WI-FI**    | **WI-FI**          | [WI-FI STA](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/wifi_01_sta) | [WI-FI AP](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/wifi_02_ap) | [WI-FI UDP通信](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/wifi_03_udp) | [Wi-Fi TCP通信](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/wifi_04_tcp) |
| **端云协同** | **MQTT**           | [MQTT本地回环测试](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/wifi_05_mqtt) | [连接华为云实现控制板载资源](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/wifi_06_huawei_iot) |                                                              |                                                              |
| **星闪**     | **SLE**            | [SLE串口透传](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/sle_01_trans_server) |                                                              |                                                              |                                                              |
| **BLE**      | **BLE**            | [BLE串口透传](https://gitee.com/HiSpark/fbb_ws63/tree/master/vendor/Hqyj_Ws63/Farsight/ble_02_trans_server) |                                                              |                                                              |                                                              |

## 参与贡献

- 参考[社区参与贡献指南](https://gitee.com/HiSpark/docs/blob/master/contribute/%E7%A4%BE%E5%8C%BA%E5%8F%82%E4%B8%8E%E8%B4%A1%E7%8C%AE%E6%8C%87%E5%8D%97.md)

| 序号 | 参考仓库                               | 网址                                                                                               |
|----|------------------------------------|--------------------------------------------------------------------------------------------------|
| 1  | eulercar_controller                | https://gitee.com/HiEuler/eulercar_controller                                                    |
| 2  | SolarA2_1.1.0.1                    | https://gitee.com/Solarec/open_solarec#application                                               |
| 3  | Vm-Ubuntu22.04-ROSSDK.md           | https://gitee.com/HiEuler/doc/blob/master/Vm-Ubuntu22.04-ROSSDK.md                               |
| 4  | 基于openEuler Embedded的星闪开源应用案例开发 | https://gitee.com/openeuler/yocto-embedded-tools/tree/hieuler/hi-sle                             |
| 5  | hi-sle/Autodesk_Fusion_360_Designs | https://gitee.com/openeuler/yocto-embedded-tools/tree/hieuler/hi-sle/Autodesk_Fusion_360_Designs |
| 6  | hi-sle/Bill_of_Materials | https://gitee.com/openeuler/yocto-embedded-tools/blob/hieuler/hi-sle/Bill_of_Materials/material_description.txt |
| 7  | ws63_ws73_ros2.c | https://gitee.com/openeuler/yocto-embedded-tools/blob/hieuler/hi-sle/EulerCar_Host_Computer_EulerPi_Source_Code/ws63_ws73_ros2.c |
| 8  | fbb_ws63开发指南 | https://gitee.com/wu-luobin/fbb_ws63#https://gitee.com/link?target=https%3A%2F%2Fitem.taobao.com%2Fitem.htm%3Fid%3D892481769813 |

---
@吴洛斌 25.3.10 测试验证开源之夏文件
---
# 基于openEuler Embedded的星闪开源应用案例开发

本开源项目是一款「基于NearLink_DK_WS63星闪开发板制作的遥控手柄」,无缝互联并操作「集成星闪WS73的智能小车」(小车可兼容Open Euler与Ros2系统)

> 星光熠熠，科技浪潮涌动！"Euler星闪耀·万物智联" —— 星闪+OpenEuler Embedded，一场关于智能交互的盛宴，让未来触手可及！


<div style="font-size:2.0em" >
  <p align="center">
    <img src="https://img.shields.io/badge/梅科尔工作室-blue?style=for-the-badge&logo=&logoColor=white" alt="梅科尔">
  </a>
  <a href="https://gitee.com/AbrillantLee/yocto-embedded-tools/stargazers"><img src="https://img.shields.io/badge/Stars-Click%20me-%23293241?style=flat-square&labelColor=%23293241&color=%23E0FBFC"></a>
  <a href="https://gitee.com/AbrillantLee/yocto-embedded-tools/contributors"><img src="https://img.shields.io/badge/Members-Click%20me-%23293241?style=flat-square&labelColor=%23293241&color=%2398C1D9"></a>
  </p>
</div>

<p align="center">
  <a href="https://gitee.com/AbrillantLee/yocto-embedded-tools/tree/hieuler/hi-sle">
  
  </a>

  <h3 align="center" >「星闪 · 遥控手柄」</h3>
  <p align="center">
    「星闪：短距新赛道」: 不止于控，更在于“速” 
    <br />
    <br />
    <a href="https://github.com/李浩楠/yocto-embedded-tools">查看Demo</a>
    ·
    <a href="https://gitee.com/AbrillantLee/yocto-embedded-tools/tree/hieuler/hi-sleissues">报告Bug</a>
    ·
    <a href="https://gitee.com/AbrillantLee/yocto-embedded-tools/tree/hieuler/hi-sleissues">提出新特性</a>
  </p>
</p>

---

- [基于openEuler Embedded的星闪开源应用案例开发](#基于openeuler-embedded的星闪开源应用案例开发)
  - [项目介绍](#项目介绍)
    - [目录结构](#目录结构)
  - [软件指南](#软件指南)
    - [1. 环境搭建](#1-环境搭建)
    - [2. 编译烧录](#2-编译烧录)
      - [2.1 Ws63主控](#21-ws63主控)
      - [2.2 EulerPi](#22-eulerpi)
      - [2.3 Hi3061M](#23-hi3061m)
    - [ws63代码文件详解](#ws63代码文件详解)
      - [EulerCar控制核心代码](#eulercar控制核心代码)
  - [硬件指南](#硬件指南)
    - [1. 电路设计](#1-电路设计)
    - [2. PCBlayout](#2-pcblayout)
    - [3. 主体建模](#3-主体建模)
    - [4. 物料购买](#4-物料购买)
    - [5. 焊接说明](#5-焊接说明)
    - [6. 测试说明](#6-测试说明)
    - [7. 硬件总装](#7-硬件总装)
    - [8. 软硬件调试](#8-软硬件调试)
      - [ws63主控调试](#ws63主控调试)
      - [遥控器整体调试](#遥控器整体调试)
      - [控制第二辆小车（Hihope Car）](#控制第二辆小车hihope-car)
  - [星闪手柄实操展示](#星闪手柄实操展示)
  - [作者](#作者)
  - [特别鸣谢 「梅科尔工作室」](#特别鸣谢-梅科尔工作室)


## 项目介绍

这是一个完整的星闪手柄开源项目，包含星闪手柄主控源码、星闪手柄结构设计、 星闪手柄电子硬件设计等多个部分，完成了以下内容：

- 使用 Autodesk Fusion 360 完成的星闪手柄模型设计
- 使用 嘉立创EDA完成的星闪手柄PCB设计
- 基于 Hispark Studio完成润和ws63星闪开发板(主控)嵌入式软件设计
- 基于 Ubuntu-vm22.04 完成ws73星闪模组代码编译

整个星闪手柄从一个ieda到真正实现、从前期部分投入到最后全身心投入经历了约三个月的时间，这个经历也让我更明白技术无止境，只有不停地学习、分享、复盘才能进步更快。所以我更希望把对制作星闪手柄过程中的困难和思考分享给大家。
<!-- 为星闪生态贡献自己薄弱的力量。 -->

所以呢，整个开源项目最重要的不是星闪手柄本身(当然落地是非常困难的)，而是，这是一套非常详细的开发教程，甚至可以说是手把手产品开发教程。从一个需求开始，到提取重点、外设选型、原理图设计、PCBlayout、代码编写、调试、烧录、结构设计、安装。如果本项目能对正在观看的你引起对星闪的兴趣和帮助，将是对我极大的鼓励和慰藉。

### 目录结构

如果刚刚开始接触这个项目，那么您可以看看本项目的文件结构，这样您可以更好的理解这个项目。
```
hi-sle 
├── Autodesk_Fusion_360_Designs/                  # Autodesk Fusion 360 模型设计文件夹
├── Bill_of_Materials/                            # 物料清单
├── JLCPCB_Files/                                 # 立创PCB文件夹
│── RemoteController_WS63E_Source_Code/*       # NearLink_DK_WS63源代码
│  ├── /SLE_OSPP_SERVER/ 
│  │  ├── inc/                                      # 头文件
│  │  └── src/                                      # 源文件
├── EulerCar_Host_Computer_EulerPi_Source_Code    # 上位机EulerPi源代码文件夹
├── EulerCar_Slave_Computer_Hi3061_Source_Code    # 下位机Hi3061源代码文件夹
├── Images                                        # 图片文件夹
└── README.md                                     # 项目说明文件

```

## 软件指南

### 1. 环境搭建

工欲善其事，必先利其器。在开始项目之前，我们需要搭建好开发环境。本项目的开发环境主要分为两个部分：**星闪遥控手柄** 开发环境 和 **EulerCar星闪遥控小车** 开发环境。由于官方基本上都有相对应的搭建教程，在本文档中就不再过多赘述。同时当然，如果您在真实开发过程中确实遇到了问题，无论问题简单与否，请大胆询问，摒弃掉学生思维。任何问题也欢迎在issue中提出，或者联系我，我会尽力解答。

1. **星闪遥控手柄**

    星闪遥控手柄的主控是**NearLink_DK_WS63**，海思官方和小熊派团队都提供了开发环境搭建教程。
    - [海思Hispark Gitee组织提供的基于Windows搭建的开发环境教程](https://gitee.com/HiSpark/fbb_ws63/tree/master/tools#windows-%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA)
    - [小熊派团队提供的基于Window环境下开发环境搭建教程](https://www.bearpi.cn/core_board/bearpi/pico/h3863/software/%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BAwindows_IDE.html)

2. **EulerCar星闪遥控小车**

    EulerCar是基于 Eulerpi主控板 和 Hi3061M控制板构建，那么我们需要搭建的环境主要分为两个部分：**EulerPi主控板** 开发环境 和 **Hi3061M控制板** 开发环境。

3. **EulerCar星闪遥控小车-EulerPi主控板**

    易百纳官方提供了[海欧派开发及使用一指禅](https://gitee.com/HiEuler/doc/blob/master/EulerPi%20Compile%20using%20One%20Finger%20Zen.md)，同时也可观看官方文档提供的[海鸥派Euler Pi 快速体验手册.pdf](https://github.com/Abrillant-Lee/Abrillant-Lee.github.io/blob/main/Summer-OSPP2024/EulerPi_Quick%20_Experience.pdf) 进行快速体验。
    >注意事项：
    >1. 固件来源有很多种：官方网盘中给的固件、gitee中下载固件、自己构建的固件，我选择使用wsl构建固件，如果对Linux不熟悉的同学可以直接使用官方提供的VM虚拟机
    >2. PD电源输入端供电不支持电脑USB接口或者5v供电，12v供电最佳。<br>
       1. 电脑USB接口的标准电压为5V，标准电流为500mA。<br>
       2.  否则网口无法正常工作💢😠<br>
    >3. 注意烧录固件大小，4G使用4G的固件，8G使用8G的固件

4. **EulerCar星闪遥控小车-Hi3061M主控板**

    官方教程：[eulercar mcu底盘代码和MCU开发IDE、MCU开发板指导手册](https://gitee.com/HiEuler/eulercar_controller)

### 2. 编译烧录

1. 将本项目clone到本地

    ```bash
    git clone https://gitee.com/AbrillantLee/yocto-embedded-tools.git
    ```

2. 切换到hieuler分支

    ```bash
    git switch hieuler
    ```

#### 2.1 Ws63主控

1. 进入到项目目录下，将`RemoteController_WS63E_Source_Code`目录下`SLE_OSPP_Server`的拷贝到您的hispark studio 开发环境`xxx\src\application\samples\peripheral\`目录下。

    ```bash
    cd hi-sle
    cp -r RemoteController_WS63E_Source_Code xxx\src\application\samples\peripheral\
    ```

2. 在xxx\src\application\samples\peripheral\CMakeLists.txt文件中新增编译案例（如果不知道在哪个地方加的，可以在“set(SOURCES "${SOURCES}" PARENT_SCOPE)”上面一行添加）。

    ```
    if(DEFINED CONFIG_SAMPLE_SUPPORT_SLE_OSPP)
        add_subdirectory_if_exist(sle_ospp)
    endif()
    ```
  
3. 在xxx\src\application\samples\peripheral\Kconfig文件中新增编译案例，具体如下图所示（如果不知道在哪个地方加，可以在最后一行添加）。

    ```
    config SAMPLE_SUPPORT_SLE_OSPP
        bool
        prompt "使能星闪遥控器"
        default n
        depends on ENABLE_PERIPHERAL_SAMPLE
        help
            This option means support SLE_OSPP Sample.
    ```

4. 选择”**系统配置**“，具体选择路径“Application/Enable the Sample of peripheral”，在弹出框中选择“使能星闪遥控器”，点击Save，关闭弹窗。

5. 点击“build”或者“rebuild”编译

6. 编译完成之后，在HiSpark Studio工具中点击“工程配置”按钮，选择“程序加载”，传输方式选择“serial”，端口选择“comxxx”，com口在设备管理器中查看。
  
7. 配置完成后，点击工具“程序加载”按钮烧录。

8. 出现“Connecting, please reset device...”字样时，复位开发板，等待烧录结束。

#### 2.2 EulerPi

- EulerPi官方Gitee仓库提供教程，可以参考[EulerPi Gitee仓库 教程 ](https://gitee.com/HiEuler/doc/blob/master/Vm-Ubuntu22.04-ROSSDK.md)。

- 注意在在`先从gitee网站上，将项目代码下载到到ubuntu环境，普通目录/home/robot下` 这一步时:

- 将`xxx/eulercar/sle_control/src/bs21_ws73_ros2.c`文件替换为本目录下的`EulerCar_Host_Computer_EulerPi_Source_Code\ws63_ws73_ros2.c`文件 

#### 2.3 Hi3061M

- 使用HisparkStudio打开Hi3061M的工程，将User目录下的文件替换为本目录下`EulerCar_Slave_Computer_Hi3061_Source_Code`文件编译烧录即可。

- 还有一种最为简单的方式就是将`Hispark`配置中的`Bin`文案金更换为`EulerCar_Slave_Computer_Hi3061_Source_Code/out/target.bin`文件，然后直接烧录即可。

<p align="center">
</p>

### ws63代码文件详解

```
│  ├── /SLE_OSPP_SERVER/
│  │  ├── inc/
│  │  │  │  ├── button.h               # 按钮模块的头文件
│  │  │  │  ├── shake.h                # 震动传感器模块的头文件
│  │  │  │  ├── eulercar_control.h     # EulerCar控制模块的头文件
│  │  │  │  ├── sle_ospp_server.h 
│  │  └── src/
│  │  │  │  ├── button.c               # 按钮/扭子开关模块的实现文件
│  │  │  │  ├── shake.c                # 震动传感器模块的实现文件
│  │  │  │  ├── eulercar_control.c     # EulerCar控控制模块的实现文件，
│  │  │  │  ├── sle_ospp_server_adv.c  
│  │  │  │  ├── sle_ospp_server.c      # SLE OSPP服务器的主实现文件
│  │  │  ├── CMakeLists.txt            # CMake 构建系统的配置文件
│  │  │  ├── Kconfig                   # Kconfig 配置文件

```
#### EulerCar控制核心代码 

```
// 键盘报告结构体定义
typedef struct
{
    uint8_t kind;        // 键盘报告类型
    uint8_t special_key; // 特殊按键
    uint8_t reserve;     // 保留字段
    uint8_t key[6];      // 按键值数组
} usb_hid_rcu_keyboard_report_t;

// 向上键报告
usb_hid_rcu_keyboard_report_t EulerCarUp = {
    .kind = 1,                                  // 键盘报告类型
    .special_key = 0,                           // 特殊按键
    .reserve = 0,                               // 保留字段
    .key = {0x52, 0x00, 0x00, 0x00, 0x00, 0x00} // 按键值数组
};

// 释放键报告
usb_hid_rcu_keyboard_report_t EulerCarRelease = {
    .kind = 1,                                 // 键盘报告类型
    .special_key = 0,                          // 特殊按键
    .reserve = 0,                              // 保留字段
    .key = {0x0, 0x00, 0x00, 0x00, 0x00, 0x00} // 按键值数组
};

// 辅助函数：发送键盘报告通知
void send_keyboard_report(usb_hid_rcu_keyboard_report_t *report)
{
    ssaps_ntf_ind_t param = {0};                           // 初始化通知参数结构体
    param.handle = g_property_handle;                      // 设置通知的句柄
    param.type = 0;                                        // 设置通知类型为0
    param.value = (uint8_t *)report;                       // 将键盘报告数据转换为 uint8_t 指针
    param.value_len = sizeof(*report);                     // 设置通知数据的长度
    ssaps_notify_indicate(g_server_id, g_conn_id, &param); // 发送通知
}

/**
 * @brief 控制小车前进
 *
 * 该函数通过发送键盘报告通知来控制小车前进。首先发送前进键报告，
 * 然后延时一段时间，再发送释放键报告。最后打印一条日志信息并延时一段时间。
 */
void eulercar_control_forward(void)
{
    send_keyboard_report(&EulerCarUp);         // 发送前进键报告
    (void)osal_msleep(PRESS_RELEASE_INTERVAL); // 延时
    send_keyboard_report(&EulerCarRelease);    // 发送释放键报告
    Vibration_CarControl();
    PRINT("[SLE Server] 星闪小车前进！ \r\n");
    (void)osal_msleep(LONG_PRESS_INTERVAL); // 延时，等待响应
}

...... # 向左、右、后代码查看源代码即可，注释非常详细

```


## 硬件指南
硬件主要由底板，PCB主板和亚克力板组成
<p align="center">
</p>

以下是PCB主板主要功能图示
<p align="center">
</p>
<p align="center">
</p>

### 1. 电路设计

> 本硬件电路主要分为电源管理电路，震动马达驱动电路和控制模块电路构成
<p align="center">
</p>

1. 电源管理电路以IP5306（<a  href="hi-sle\RelevantDetails\IP5306_datasheet_v1.01.pdf" alt="链接">产品资料🔗</a>）为核心。IP5306是一款集成升压转换器、锂电池充电管理、电池电量指示的多功能电源管理 SOC，为移动电源提供完整的电源解决方案。
    - 可同步开关充放电，支持4LED电量显示
    - 自动检测充电器插拔，自适应充电电流调节
    - 按键功能：
      - 短按（持续时间长于 50ms，但小于 2s）会打开电量显示灯和升压输出。
      - 连续两次短按键（ 1s 内），会关闭电量显示和升压输出
<p align="center">
</p>
<p align="center">
</p>

2. 震动马达驱动电路以微型震动马达为核心，在这个电路中，场效应管能够通过控制门极电压来开启或关闭电流，从而控制电机的工作状态。肖特基二极管防止电机在停止时产生的反向电流对电路造成损坏，起到保护作用。

<p align="center">
</p>

3. 控制模块电路以WS63E为核心，用于各个引脚与传感器或执行器之间的通信。

### 2. PCBlayout


以下是<a href="JLCPCB_Files\Gerber_eulercar_2024-09-15.zip" alt="链接">PCB设计🔗</a>
<p align="center">
</p>


为了方便硬件焊接测试与软件调试，我们将各个摇杆等主要功能按键导出为<a href="JLCPCB_Files\Gerber_eulercar_2024-09-15.zip" alt="链接">markdown文件🔗</a>
以供快速参考

### 3. 主体建模
1. 遥控器<a href="hi-sle\Autodesk_Fusion_360_Designs\remote_controller_model.dxf" alt="链接">底板模型🔗</a>总体按照PCB轮廓构建，使用Autodesk Fusion进行建模。
    - 整体参考游戏手柄与遥控手柄设计
    - 底板前端突起为外置天线座，可以搭载外设SLE天线
    - 预留四个M3空位，用于与PCB和顶板的连接固定

<p align="center">
</p>


2. 顶层<a href="hi-sle\Autodesk_Fusion_360_Designs\remote_controller_model.f3d" alt="链接">亚克力板轮廓🔗</a>由底板模型轮廓构建，使用Fusion进行导出
    - 顶板设计需要考虑按键与摇杆等传感器加上键帽配件等的总体高度
    - 预留四个M3空位，用于与PCB和顶板的连接固定
    - 六角铜柱需要的最小高度为：PCB插排高度+WS63E最大高度 = 16mm

<p align="center">
</p>

### 4. 物料购买

PDB电子元器件物料可直接由嘉立创EDA导出
<a href="hi-sle\JLCPCB_Files\BOM_Board1_EulerCar.xlsx" alt="链接">BOM表单🔗</a>，交由专业配件商家购买。

除此之外，完成总体装配还需要<a  href="hi-sle\Bill_of_Materials\material_purchase.xlsx" alt="链接">其他配件或耗材🔗</a>。


1. 摇杆帽：用于摇杆操控（注意底孔是小孔型号哦）
2. 亚克力板：用于遥控器整体面板（<a href="hi-sle\Autodesk_Fusion_360_Designs\remote_controller_model.dxf" alt="链接">dxf亚克力轮廓图🔗</a>）
3. 焊锡膏：用于贴片原件焊料
4. 704硅橡胶：用于PCB电池盒固定
5. 18650电池：用于遥控板供电
6. 六角铜柱：用于整体连接


### 5. 焊接说明

1. 准备好PCB、元器件、电烙铁或热风枪、锡膏或锡丝、镊子。
2. 打开BOM表或EDA，从贴片元器件开始，找到要焊接的元器件型号。

<p align="center">
</p>

3. 按照元器件位置进行分区，使用热风枪时对邻近贴片元器件一起焊接。

<p align="center">
</p>

4. 每个模块焊接完成后，可以对照PCB工程图，用万用表逐个检查是否存在焊错、短路、虚焊、脱焊等情况。
5. 按上述的步骤，完成所有元器件的焊接即可。也可使用洗板水确保焊后的美观。
<p align="center">
</p>

<p align="center">
</p>


### 6. 测试说明

> 焊接完成后，要先目测、用万用表检测下，有没有焊接错的地方。尤其确保没有短路。第一次上电时也要第一时间观察下有没有异常，有异常迅速拔掉电源。

可能遇到的问题：
1. IP5306相关问题
    - [x] 1. 输出电压很低，只有2-3V，没有了升压。<br>
        - 原因
         是芯片底部GND与PCB之间脱焊所致。
        - 解决方案
         IP5306底部的焊盘为GND，在焊接时建议为底盘加锡进行焊接
    - [x] 2. 开机半分钟自动休眠
        - 原因
          - 是电流过低，可以检查是否有元器件虚焊脱焊现象。当一段时间内芯片负载电流持续小于45mA左右时，芯片会自动进入休眠状态。 但在实际应用中，此芯片个体差异很大，有部分芯片负载电流需要达到70mA以上才不会自动休眠
        - 解决方案
          - 检查元器件是否脱焊、虚焊，重新焊接。
    - [x] 不断关机重启
        - 原因
          - 可能是芯片检测到过流或者短路引起的
          - 可能是散热不足触发过温保护导致的
        - 解决方案
          - 检查是否短路，进行重新焊接；
          - 检查是否由过温导致，检查工作温度是否符合要求，增加散热片等散热措施；
    <p align="center">
    </p>

    - [x] 芯片烧毁
       - 原因
          - 电池持续放电或温度过高等原因导致芯片烧毁
       - 解决方案
         - 检查电池质量与焊接质量，进行重新焊接，更换芯片。
2. 其他问题
    - [x] 传感器失灵
      - 原因
        - 传感器元器件与PCB脱焊或虚焊
      - 解决方案
        - 检查元器件是否脱焊、虚焊，重新焊接。

### 7. 硬件总装
注意三个组件从底部往上装配。
1. 从底版底部拧入螺丝，在底版上部放入垫片与螺帽。在确保与PCB孔位对齐的情况下固定好底板与螺丝。
2. 在底板上部侧放入PCB，注意对准螺孔，在上侧放入垫片与六角铜柱拧紧。
3. 在螺柱顶部放入亚克力板，对齐后加上垫片拧入螺丝
4. 您的第一个星闪遥控器大功告成

<p align="center">
</p>

### 8. 软硬件调试



#### ws63主控调试

- 程序：[RemoteController_WS63E_Source_Code_one](RemoteController_WS63E_Source_Code_one)
- 调试现象：ws63遥控小车前进、后退、左转、右转，每个控制指令中间间隔100ms；
- 如需调整控制时间，可在`eulercar_control.h`中修改宏定义`PRESS_RELEASE_INTERVAL`即可
<p align="center">
</p>


#### 遥控器整体调试

- 程序：[RemoteController_WS63E_Source_Code_two](RemoteController_WS63E_Source_Code_two)
- 调试现象：左摇杆x轴控制小车左转、右转，右摇杆y轴控制小车前进、后退;
- usb连接遥控器上的主控ws63, 同时启动EulerCar小车sle和ros节点即可。
<p align="center">
</p>

#### 控制第二辆小车（Hihope Car）
<p align="center">
</p>


## 星闪手柄实操展示

手柄操作方法：
1. 左摇杆：控制EulerCar前进、后退、左转、右转
2. 右摇杆：控制EulerCar夹爪：张开、闭合
3. 左右扭子开关：切换不同EulerCar小车
4. ...持续更新中




# 个人进度
## 杨力滔
#### 4.20正式开始安装相关环境，WSL子系统开发环境搭建，一开始没找到下载的fbb_ws63_wsl，最后将它拖到桌面上，找到了文件路径，在poweshell中要更新wsl子系统不然不能使用
#### 4.26星闪代码下载，将星闪代码导入到VSCode，对星闪代码编译。
#### 4.27进行镜像烧录，Typec线将板端与PC端连接，安装驱动“CH341SER驱动”下载烧录工具进行烧录，发现总是失败。
#### 4.28解决不能烧录问题，有的板子需要插拔后才可以烧录成功，进行虚拟机开发环境部署，下载项目代码和安装SDK，然后进行项目代码编译
#### 4.29进行小车端组网配置和域id配置。
#### 4.30对海鸥派进行开发和使用，进行EulerPi镜像下载，镜像文件包括Uboot、kernel和rootfs，需要拷贝到SD卡给海鸥派升级，过程中遇到了问题，发现可能是拷贝镜像文件到 SD 卡可能未正确创建分区表或文件系统，我们直接使用 dd 写入完整镜像：sudo dd if=image.img of=/dev/sdX bs=4M status=progress。
#### 5.1 下载Uboot二进制包，然后下载海鸥派普通版本镜像![输入图片说明](image/1747832651740.png)
#### 5.2 对海鸥派进行镜像烧录，我们先快速构建出一个openEuler Embedded镜像，需要在构建主机上安装必要的主机包，初始化oebuild构建环境，然后执行命令进行 ARM64 QEMU 镜像的构建，build_arm64 为该镜像的构建目录，在主机上通过命令安装QEMU。
#### 5.3 完成基于SDK的应用开发，进入到镜像构建目录 build_arm64，执行命令构建SDK卡，安装依赖软件包，执行SDK自解压安装脚本，然后设置SDK环境变量，并检查是否安装成功如图所示![输入图片说明](image/1747833318080.png)
#### 5.6了解手柄电路的设计，遥控器底板模型总体按照PCB轮廓构建，使用Autodesk Fusion进行建模，顶层亚克力板轮廓，由底板模型轮廓构建，使用Fusion进行导出。
#### 5.7购买PDB电子元器件物料。
#### 5.8先试着调试1.0星闪手柄。今日无事，早点回去休息。
#### 5.9所有材料到齐，准备进行焊接，从贴片元器件开始，找到要焊接的元器件型号。
#### 5.10用万用表检查有没有焊接错误的地方，遇到问题开机后休眠，检查后发现又虚焊的情况。
#### 5.11将硬件总装，对软硬件进行调试，完成任务。以下是完成的手柄图片。
## 图片：
![输入图片说明](https://gitee.com/ylt123456789/new_energy_coder_club/raw/master/%E7%A7%91%E7%A0%94%E3%80%8C%E6%A8%AA%E5%90%91%E9%A1%B9%E7%9B%AE%E3%80%8D/20250426%E6%98%9F%E9%97%AA%E6%89%8B%E6%9F%84/image/1f93acac9135ea619e2737446bac10f.jpg)
![输入图片说明](image/26a7f4dbece3034dc0a8081bc154da9.jpg)