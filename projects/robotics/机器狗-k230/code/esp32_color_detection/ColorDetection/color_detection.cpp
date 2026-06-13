#include "color_detection.hpp"
#include "esp_log.h"
#include "esp_camera.h"
#include "dl_image.hpp"
#include "fb_gfx.h"
#include "color_detector.hpp"
#include "who_ai_utils.hpp"

using namespace std;
using namespace dl;

static const char *TAG = "color_detection";

static QueueHandle_t xQueueFrameI = NULL;
static QueueHandle_t xQueueEvent = NULL;
static QueueHandle_t xQueueFrameO = NULL;
static QueueHandle_t xQueueResult = NULL;

static bool gReturnFB = true;
static int g_max_color_area = 0;
color_data_t color_data[5];



/* 颜色阈值 用户可在此处调整 */
vector<color_info_t> std_color_info = {
    {{151, 15, 70, 255, 90, 255}, 64, "red"},
    {{23, 34, 70, 255, 90, 255}, 64, "yellow"},
    {{45, 75, 70, 255, 90, 255}, 64, "green"},
    {{97, 117, 70, 255, 90, 255}, 64, "blue"},
    {{130, 155, 70, 255, 90, 255}, 64, "purple"}
};

/* 获取颜色检测的结果 */
static void get_color_detection_result(uint16_t *image_ptr, int image_height, int image_width, vector<color_detect_result_t> &results, uint16_t color)
{
  int g_max_color_column_index = 0;
  /* 寻找同色最大色块 */
  for (int i = 0; i < results.size(); ++i)
  {
    if (results[i].area > g_max_color_area)
    {
      g_max_color_area= results[i].area;
      g_max_color_column_index = i;
    }
    switch (color)
    {
      case COLOR_RED:

        color_data[0].center_x = (uint8_t)results[g_max_color_column_index].center[0];
        color_data[0].center_y = (uint8_t)results[g_max_color_column_index].center[1];
        /* right_down_x - left_up_x  */
        color_data[0].width = (uint8_t)(results[g_max_color_column_index].box[2] - results[g_max_color_column_index].box[0]);
        /* right_down_y - left_up_y  */
        color_data[0].length = (uint8_t)(results[g_max_color_column_index].box[3] - results[g_max_color_column_index].box[1]);
        break;

      case COLOR_YELLOW:

        color_data[1].center_x = (uint8_t)results[g_max_color_column_index].center[0];
        color_data[1].center_y = (uint8_t)results[g_max_color_column_index].center[1];
        /* right_down_x - left_up_x  */
        color_data[1].width = (uint8_t)(results[g_max_color_column_index].box[2] - results[g_max_color_column_index].box[0]);
        /* right_down_y - left_up_y  */
        color_data[1].length = (uint8_t)(results[g_max_color_column_index].box[3] - results[g_max_color_column_index].box[1]);
        break;

      case COLOR_GREEN:

        color_data[2].center_x = (uint8_t)results[g_max_color_column_index].center[0];
        color_data[2].center_y = (uint8_t)results[g_max_color_column_index].center[1];
        /* right_down_x - left_up_x  */
        color_data[2].width = (uint8_t)(results[g_max_color_column_index].box[2] - results[g_max_color_column_index].box[0]);
        /* right_down_y - left_up_y  */
        color_data[2].length = (uint8_t)(results[g_max_color_column_index].box[3] - results[g_max_color_column_index].box[1]);
        break;

      case COLOR_BLUE:

        color_data[3].center_x = (uint8_t)results[g_max_color_column_index].center[0];
        color_data[3].center_y = (uint8_t)results[g_max_color_column_index].center[1];
        /* right_down_x - left_up_x  */
        color_data[3].width = (uint8_t)(results[g_max_color_column_index].box[2] - results[g_max_color_column_index].box[0]);
        /* right_down_y - left_up_y  */
        color_data[3].length = (uint8_t)(results[g_max_color_column_index].box[3] - results[g_max_color_column_index].box[1]);
        break;

      case COLOR_PURPLE:

        color_data[4].center_x = (uint8_t)results[g_max_color_column_index].center[0];
        color_data[4].center_y = (uint8_t)results[g_max_color_column_index].center[1];
        /* right_down_x - left_up_x  */
        color_data[4].width = (uint8_t)(results[g_max_color_column_index].box[2] - results[g_max_color_column_index].box[0]);
        /* right_down_y - left_up_y  */
        color_data[4].length = (uint8_t)(results[g_max_color_column_index].box[3] - results[g_max_color_column_index].box[1]);
        break;

      default:
        break;
    }    
  }
}

static void task_process_handler(void *arg)
{
  camera_fb_t *frame = NULL;
  ColorDetector detector;
  /* 注册颜色信息 */
  for (int i = 0; i < std_color_info.size(); ++i)
  {
    detector.register_color(std_color_info[i].color_thresh, std_color_info[i].area_thresh, std_color_info[i].name);
  }
  vector<uint16_t> draw_colors = {
    COLOR_RED,
    COLOR_YELLOW,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_PURPLE,
  };
  int draw_colors_num = draw_colors.size();
  while (true)
  {
    if (xQueueReceive(xQueueFrameI, &frame, portMAX_DELAY))
    {
      std::vector<std::vector<color_detect_result_t>> &results = detector.detect((uint16_t *)frame->buf, {(int)frame->height, (int)frame->width, 3});
      for(int i = 0; i < COLOR_NUM; ++i)
      {
        if(results[i].size() == 0)
        {
          color_data[i].center_x = 0;
          color_data[i].center_y = 0;
          color_data[i].width = 0;
          color_data[i].length = 0;
        }else{
          printf("Color:[%d] \r\n", i);
        }
      }
      
      for (int i = 0; i < results.size(); ++i)
      {
        get_color_detection_result((uint16_t *)frame->buf, (int)frame->height, (int)frame->width, results[i], draw_colors[i % draw_colors_num]);
      }
    }
    if (xQueueFrameO)
    {
      xQueueSend(xQueueFrameO, &frame, portMAX_DELAY);
    }
    else if (gReturnFB)
    {
      esp_camera_fb_return(frame);
    }
    else
    {
      free(frame);
    }
    if (xQueueResult)
    {
      xQueueSend(xQueueResult, &color_data, portMAX_DELAY);             
    }          
  }
}

static void task_event_handler(void *arg)
{
    while (true)
    {
    }
}

void register_color_detection(const QueueHandle_t frame_i,
                                   const QueueHandle_t event,
                                   const QueueHandle_t result,
                                   const QueueHandle_t frame_o,
                                   const bool camera_fb_return)
{
  xQueueFrameI = frame_i;
  xQueueFrameO = frame_o;
  xQueueEvent = event;
  xQueueResult = result;
  gReturnFB = camera_fb_return;

  xTaskCreatePinnedToCore(task_process_handler, TAG, 4 * 1024, NULL, 5, NULL, 1);
  // xTaskCreatePinnedToCore(task_event_handler, TAG, 4 * 1024, NULL, 5, NULL, 0);
}