#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 25 23:46:07 2022

@author: prabhakar
"""

# Imports
import cv2
import v4l2
import time
import fcntl
import numpy as np
import tensorflow as tf
from stream import Video

#from vidgear.gears import WriteGear


model_path = "models/lite-model_deeplabv3_1_metadata_2.tflite"

interpreter = tf.lite.Interpreter(model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_index = input_details[0]['index']
output_index = output_details[0]['index']

background = cv2.imread("sample.jpeg")
background = cv2.resize(background, (640,480))


print(input_details)
print(output_details)

#cv2.namedWindow("Display", cv2.WINDOW_NORMAL)
#cv2.namedWindow("Processed", cv2.WINDOW_NORMAL)
device = open(r"/dev/video10", "wb")
enable_bg = False


format                      = v4l2.v4l2_format()
format.type                 = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT
format.fmt.pix.field        = v4l2.V4L2_FIELD_NONE
format.fmt.pix.pixelformat  = v4l2.V4L2_PIX_FMT_YUV420
format.fmt.pix.width        = 640
format.fmt.pix.height       = 480
format.fmt.pix.bytesperline = 640 * 3
format.fmt.pix.sizeimage    = 640 * 480 * 3

print ("set format result (0 is good):{}".format(fcntl.ioctl(device, v4l2.VIDIOC_S_FMT, format)))

cap = Video(2).start()

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
      
      #image_expanded = np.asarray(np.expand_dims(image, axis=0), dtype=np.float32)
      
      interpreter.set_tensor(input_index, image_for_prediction)
      interpreter.invoke()
      
      output_data = interpreter.get_tensor(output_index)
      
      seg_map = tf.argmax(tf.image.resize(output_data, (480, 640)), axis=3)
      seg_map = tf.squeeze(seg_map).numpy().astype(np.int8)
      
      img2 = np.zeros((np.array(frame).shape[0], np.array(frame).shape[1], 3), dtype=np.int8)
      img2[:,:,0] = seg_map # same value in each channel
      img2[:,:,1] = seg_map
      img2[:,:,2] = seg_map
            
      if enable_bg:
          blurred_image = cv2.blur(frame, (9,9))
          mask_image = np.where(img2 == np.array([15, 15, 15]) ,frame, blurred_image)
      else:
          mask_image = np.where(img2 == np.array([15, 15, 15]) ,frame, background)
      
      mask_image = cv2.cvtColor(mask_image, cv2.COLOR_BGR2YUV_I420)
      #mask_image = cv2.resize(mask_image, (1920,1080))
      device.write(mask_image)
      print((time.time() - start_time)*1000)
      print("Count: ", count)
      #cv2.imshow("Processed", mask_image)
      #cv2.waitKey(1)
  except KeyboardInterrupt:
    cap.stop()
    cv2.destroyAllWindows()
    device.close()
    break
