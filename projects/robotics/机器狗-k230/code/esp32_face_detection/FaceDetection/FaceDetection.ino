#include "camera_setting.h"
#include "face_detection.hpp"
#include "iic_data_send.hpp"

static QueueHandle_t xQueueAIFrame = NULL;
static QueueHandle_t xQueueIICData = NULL;

void setup() 
{
  /* 创建图像传输队列 */
  xQueueAIFrame = xQueueCreate(2, sizeof(camera_fb_t *)); 
  /* 创建IIC数据传输队列 */
  xQueueIICData = xQueueCreate(2, sizeof(iic_send_data_t *));

  /* 注册摄像头处理任务 */
  register_camera(PIXFORMAT_RGB565, FRAMESIZE_240X240, 4, xQueueAIFrame);
  /* 注册人脸检测任务 */
  register_human_face_detection(xQueueAIFrame, NULL, xQueueIICData, NULL, true);
  /* 注册IIC数据传输任务 */
  register_iic_data_send(xQueueIICData, NULL);
}


void loop()
{
  
}
