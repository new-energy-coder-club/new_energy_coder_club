#include "iic_data_send.hpp"
#include "Wire.h"

#define I2C_SLAVE_ADDRESS 0x52

static QueueHandle_t xQueueResultI = NULL;
static QueueHandle_t xQueueResultO = NULL;

static const char *TAG = "iic_data_send";
static const int sdaPin = 47;
static const int sclPin = 48;
static const uint32_t i2cFrequency = 100000;

static iic_send_data_t send_data;

static uint8_t rec;
static uint8_t data[4] = {0};

static void iic_receive(int len)
{
  while(Wire.available())
  {
    rec = Wire.read();
  }  
}

static void iic_request()
{
  if(rec == 0x01)
  {
    data[0] = send_data.center_x;
    data[1] = send_data.center_y;
    data[2] = send_data.detection_width;
    data[3] = send_data.detection_length;
    Wire.slaveWrite(data, sizeof(data));
  }else if(rec == 0x02)
  {
    data[0] = 255;
    data[1] = 255;
    data[2] = 255;
    data[3] = 255;
    Wire.slaveWrite(data, sizeof(data));
  }else if(rec == 0x03)
  {
    data[0] = 255;
    data[1] = 255;
    data[2] = 255;
    data[3] = 255;
    Wire.slaveWrite(data, sizeof(data));
  }
}

static void task_process_handler(void *arg)
{
  /* IIC初始化 */
  Wire.begin((uint8_t)I2C_SLAVE_ADDRESS, sdaPin, sclPin, i2cFrequency);
  /* 注册接收数据的回调函数 */
  Wire.onReceive(iic_receive);
  /* 注册请求数据的回调函数 */
  Wire.onRequest(iic_request);

  while (true)
  {
    if (xQueueReceive(xQueueResultI, &send_data, portMAX_DELAY))
    {

    }
  }

}

void register_iic_data_send(const QueueHandle_t result_i,
                            const QueueHandle_t result_o)
{
  xQueueResultI = result_i;
  xQueueResultO = result_o;

  xTaskCreatePinnedToCore(task_process_handler, TAG, 4 * 1024, NULL, 5, NULL, 1);
}