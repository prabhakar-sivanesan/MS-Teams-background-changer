## MS Teams background changer

Microsoft Teams on linux operating system does not have background effects like background blur or custom background image. This utility application enables these missing features to blur and add custom background image.  

Image segmentation is a computer vision technique used to understand objects present in the image at pixel level. This allows us to differentiate the foreground and background in an image easily. We have used [DeepLab-V3](https://ai.googleblog.com/2018/03/semantic-image-segmentation-with.html) image segmentation AI model to segment humans as foreground and the rest of the objects as a background and apply filters to it.

We use [v4l2loopback](https://github.com/umlaeute/v4l2loopback) module to create **virtual video devices**. Therefore, all v4l2 applications will read the newly created virtual video device as a physical video device. This allows us to add some effects to the video feed.