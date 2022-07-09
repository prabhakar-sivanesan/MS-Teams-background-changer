#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 23:46:07 2022

@author: prabhakar
"""

# imports
import cv2
import v4l2
import time
import fcntl
import numpy as np
import configparser
import tensorflow as tf
from stream import Video

# parse config file to read configuration data
config = configparser.ConfigParser()
config.read("config.yaml")

try:
    
    model_path = config['model']['path']
    
    # input physical camera configuration
    input_cam_id = int(config['stream']['cameraID'].split("/dev/video")[-1])
    input_fps = int(config['stream']['fps'])
    height = int(config['stream']['height'])
    width  = int(config['stream']['width'])
    channels = int(config['stream']['channel'])
    
    # background configuration data
    enable_blur = config['background'].getboolean('blur')
    background = config['background']['bg_image']
    intensity = int(config['background']['blur_intensity'])
    background = cv2.imread(background)
    background = cv2.resize(background, (width,height))
    
    # virtual camera device ID
    virtual_cam_id = config['V4L2']['virtualDeviceID']
    
except ValueError as e:
    print(e)

# open virtual camera
device = open(virtual_cam_id, "wb")

# =============================================================================
# set configuration for buffered stteaming to virtual camera 
# Recommended not to mess with these values, unless you know what you're doing.
# =============================================================================
format                      = v4l2.v4l2_format()
format.type                 = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT
format.fmt.pix.field        = v4l2.V4L2_FIELD_NONE
format.fmt.pix.pixelformat  = v4l2.V4L2_PIX_FMT_YUV420
format.fmt.pix.width        = width
format.fmt.pix.height       = height
format.fmt.pix.bytesperline = width* channels
format.fmt.pix.sizeimage    = width*height*channels
print ("set format result (0 is good):{}".format(fcntl.ioctl(device, v4l2.VIDIOC_S_FMT, format)))

# load tflite models and get input and output tensor values  
interpreter = tf.lite.Interpreter(model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_index = input_details[0]['index']
output_index = output_details[0]['index']

# start physical camera on parallel thread, refer stream.py
# press ctrl+q to stop the thread.
cap = Video(input_cam_id, width, height, input_fps).start()

while True:
  try:
    ret, frame, count = cap.read_frame()
    if ret:
      start_time = time.time()
      height, width, _ = frame.shape
      image = cv2.resize(frame, (257,257))
      
      image_for_prediction = image.astype(np.float32)
      image_for_prediction = np.expand_dims(image_for_prediction, 0)
      image_for_prediction = image_for_prediction / 127.5 - 1
      interpreter.set_tensor(input_index, image_for_prediction)
      interpreter.invoke()
      
      output_data = interpreter.get_tensor(output_index)
      seg_map = tf.argmax(tf.image.resize(output_data, (height, width)), axis=3)
      seg_map = tf.squeeze(seg_map).numpy().astype(np.int8)
      
      seg_map_3c = np.zeros((np.array(frame).shape[0], np.array(frame).shape[1], 3), dtype=np.int8)
      seg_map_3c[:,:,0] = seg_map
      seg_map_3c[:,:,1] = seg_map
      seg_map_3c[:,:,2] = seg_map
            
      if enable_blur: # blurs the background, does not add background image
          blurred_image = cv2.blur(frame, (intensity,intensity))
          mask_image = np.where(seg_map_3c == np.array([15, 15, 15]) ,frame, blurred_image)
      else: # adds background image, does not blur the background
          mask_image = np.where(seg_map_3c == np.array([15, 15, 15]) ,frame, background)
      
      # essential to convert the image from BGR planar to YUV 4:2:0 planar
      mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2YUV_I420)
      device.write(mask_image)
      
      print("Processing frame: {0} at{1:3d} fps. Press ctrl+c to stop".format(count,int(1/(time.time() - start_time))))
  except KeyboardInterrupt:
    cap.stop()
    #cv2.destroyAllWindows()
    device.close()
    break
