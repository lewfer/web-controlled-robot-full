# www.thinkcreatelearn.co.uk
#
# Video player class for webcams
#
# Implements a class that can be used by the web page to stream video images from a webcam
#
# Requires installation of OpenCV and numpy
# Installation of OpenCV on the Raspberry Pi can be a bit problematic.
# See my web page for details
#

from time import sleep
import threading

import numpy as np
import cv2 

# Settings
# -------------------------------------------------------------------------------------------------

# If you need to change the defaults, change them in settings.py:
from settings import *


class VideoPlayer(object):
    def __init__(self, resolution=RESOLUTION, rotation=ROTATION, fps=FPS, filename=0):
        # Remember the filename.  If no filename is given the web cam will be streamed
        self.filename = filename

        self.resolution = resolution
        self.rotation = rotation
        self.fps = fps     

        # We will start the camera on a separate thread.
        # This ensures the camera continues running even if no one is watching
        self.thread = threading.Thread(target=self._runCamera)

        # We will save the last frame read on the thread so when someone watches we can return this frame
        self.lastFrame = None

        # Now start the camera running
        self.thread.start()

        # wait until frames are available
        while self.getFrame() is None:
            sleep(0)

    def _runCamera(self):
        """Start the camera generating frames"""

        framesIterator = self.generateFrames()

        # Use an iterator to read the frames, one by one
        for frame in framesIterator:
            # Save the frame read in case someone wants to look at it
            self.lastFrame = frame

        self.thread = None

    def generateFrames(self):
        """This is a generator function that can be used by a loop to get one frame at a time"""

        # Start the webcam
        camera = cv2.VideoCapture(self.filename)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        camera.set(cv2.CAP_PROP_FRAME_WIDTH,self.resolution[0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT,self.resolution[1])
        camera.set(cv2.CAP_PROP_FPS,self.fps)

        # Keep reading frames forever
        finished = False
        while not finished:
            # Read current frame
            _, img = camera.read()
            if img is None:
                finished = True
        
            # Encode as a jpeg image and return it
            if not finished:
                yield cv2.imencode('.jpg', img)[1].tobytes()       


    def getFrame(self):     
        """Return the last frame read"""
        return self.lastFrame        


    def genVideo(self):
        """This is a generator function.  We can call it in a loop and it returns one frame at a time.
           Note how it loops forever (while True).  It never stops returning frames"""
           
        while True:
            # Get the next video frame
            frame = self.getFrame()

            # Return it to the , wrapper in the necessary mime encodings
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')    
            