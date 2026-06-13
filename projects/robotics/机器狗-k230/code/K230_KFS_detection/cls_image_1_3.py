# -*- coding: utf-8 -*-
'''
Script: deploy_cls_image.py
脚本名称：deploy_cls_image.py

Description:
    This script performs image classification on a single image.It loads an image, performs inference using a pre-trained Kmodel,
    and displays the classification result.

    The model configuration is loaded from the Canaan online training platform via a JSON config file. Please prepare the test image yourself.

脚本说明：
    本脚本对单张图像进行分类。它会加载一张图像，使用预训练的 Kmodel 进行推理，并显示分类结果。

    模型配置文件通过 JSON 文件从 Canaan 在线训练平台加载。请自行准备测试图片。

Author: Canaan Developer
作者：Canaan 开发者
'''

import os, gc
from libs.PlatTasks import ClassificationApp
from libs.Utils import *

# Load image in CHW format for inference and RGB888 for display
# The image dimensions are used for setting the input size for the inference model
img_chw, img_rgb888 = read_image("/sdcard/test.jpg")
rgb888p_size = [img_chw.shape[2], img_chw.shape[1]]

# Set root directory path for model and config
root_path = "/sdcard/mp_deployment_source/"

# Load deployment configuration
deploy_conf = read_json(root_path + "/deploy_config.json")
kmodel_path = root_path + deploy_conf["kmodel_path"]              # KModel path
labels = deploy_conf["categories"]                                # Label list
confidence_threshold = deploy_conf["confidence_threshold"]        # Confidence threshold
model_input_size = deploy_conf["img_size"]                        # Model input size
num_classes = deploy_conf["num_classes"]                          # Number of classes

# Inference configuration
inference_mode = "image"                                          # Inference mode: 'image'
debug_mode = 0                                                    # Debug mode flag

# Initialize classification application
cls_app = ClassificationApp(inference_mode,kmodel_path,labels,model_input_size,confidence_threshold,rgb888p_size,rgb888p_size,debug_mode=debug_mode)

# Configure preprocessing for the model
cls_app.config_preprocess()

# Run inference on the loaded image
res = cls_app.run(img_chw)

# Draw classification result on the image
cls_app.draw_result(img_rgb888, res)

# Prepare image for IDE display
img_rgb888.compress_for_ide()

# Cleanup: De-initialize classification app and Run garbage collection to free memory
cls_app.deinit()
gc.collect()

