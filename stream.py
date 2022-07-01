#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 00:48:02 2022

@author: prabhakar
"""


import cv2
import threading

class Video:
    def __init__(self, video_src, width, height, fps):

        self.stream = cv2.VideoCapture(video_src)
        self.stream.set(3, width)
        self.stream.set(4, height)
        self.stream.set(5, fps)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.count = 0
        
    def start(self):
        threading.Thread(target=self.update, args=()).start()
        return self
    
    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return
            (self.grabbed, self.frame) = self.stream.read()
            self.count+=1
            
    def read_frame(self):
        return self.grabbed, self.frame, self.count
    
    def get_shape(self):
        return self.frame.shape
    
    def stop(self):
        self.stopped = True