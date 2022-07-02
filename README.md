# MS Teams background changer

Microsoft Teams on linux operating system does not have background effects like background blur or custom background image. This utility application enables these missing features to blur and add custom background image. It works on other video conference platform like Zoom, Google Meet and Skype. 

We have used AI based Image segmentation model [DeepLab-V3](https://ai.googleblog.com/2018/03/semantic-image-segmentation-with.html) to segment person as foreground and the rest of the objects as a background and apply filters to it.


## Installation

### Install v4l2loopback and create virtual camera

    sudo apt-get install v4l2loopback-dkms v4l-utils

[v4l2loopback](https://github.com/umlaeute/v4l2loopback) module is used to create **virtual video devices**. Therefore, all v4l2 applications will read the newly created virtual video device as a physical video device. This allows us to push modified video stream to the virtual camera and use it as a normal video feed coming from physical camera device.  

### Create Virtual Camera

    sudo modprobe v4l2loopback video_nr=20 card_name="Virtual Camera 1" exclusive_caps=1


This will create a virtual camera with a device 20 (if it's taken, change to different ID. Recommended to give higher number therefore there won't me clash) and name **Virtual Camera 1**

You can verify that by running

    ls -1 /sys/devices/virtual/video4linux
and this should output something like ``` video20 ```.