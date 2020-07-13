# www.thinkcreatelearn.co.uk
#
# Video player class for Raspberry Pi camera
#
# Implements a class that can be used by the web page to stream video images from the Rasbperry Pi camera.
#
# Requires installation of OpenCV and numpy
# Installation of OpenCV on the Raspberry Pi can be a bit problematic.
# See my web page for details
#

# Includes
# -------------------------------------------------------------------------------------------------

# picamera.array allows us to get camera output into a numpy array
# This will facilitate manipulation of the image if we want to
from picamera.array import PiRGBArray

# Allows use of the Raspberry Pi camera
from picamera import PiCamera

# Numpy, for holding image data
import numpy as np

# OpenCV for image manipulation
import cv2

# Threading library, so our code can run multiple things at the same time
import threading

from time import sleep


# Settings
# -------------------------------------------------------------------------------------------------

# If you need to change the defaults, change them in settings.py:
from settings import *


# Class definition
# -------------------------------------------------------------------------------------------------

class VideoPlayer(object):

    def __init__(self, resolution=RESOLUTION, rotation=ROTATION):
        # Set up the camera attributes according to your needs
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.hflip = True
        self.camera.vflip = True

        # Set up the video quality
        self.jpegQuality = JPEGQUALITY
        self.fps = FPS

        # We will start the camera on a separate thread.
        # This ensures the camera continues running even if no one is watching
        self.thread = threading.Thread(target=self._runCamera)

        # We will save the last frame read on the thread so when someone watches we can return this frame
        self.lastFrame = None

        # Now start the camera running
        self.thread.start()

        # wait until frames are available
        while self._getFrame() is None:
            sleep(0)

    def _runCamera(self):
        """Function to set the camera off generating frame data"""

        # Start the camera generating frames
        framesIterator = self._generateFrames()

        # Use an iterator to read the frames, one by one
        for frame in framesIterator:
            # Save the frame read in case someone wants to look at it
            self.lastFrame = frame

        self.thread = None

    def _generateFrames(self):
        """This is a generator function that can be used by a loop to get one frame at a time"""

        # Create a buffer to hold the image data
        buffer = PiRGBArray(self.camera, size=self.camera.resolution)

        # Start capturing frames as a stream
        stream = self.camera.capture_continuous(buffer, format="bgr", use_video_port=True)

        # For each frame captured, return it to the calling loop
        for frame in stream:
            yield frame.array
            buffer.truncate(0)            


    def _getFrame(self):     
        """Return the last frame read, if there is one"""

        if self.lastFrame is None:
            return None
        else:
            result, encodedFrame = cv2.imencode('.jpg', self.lastFrame, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpegQuality])
            return encodedFrame.tostring()      


    def genVideo(self):    
        """This is a generator function.  We can call it in a loop and it returns one frame at a time.
           Note how it loops forever (while True).  It never stops returning frames"""

        while True:
            # Limit the frames per second
            sleep(1.0/self.fps)

            # Get the next video frame
            frame = self._getFrame()

            # Return it to the , wrapper in the necessary mime encodings
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')    
            