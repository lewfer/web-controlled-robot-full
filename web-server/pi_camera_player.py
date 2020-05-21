# www.thinkcreatelearn.co.uk
#
# Video player class for Raspberry Pi camera
#
# Implements a class that can be used by the web page to stream video images from the Rasbperry Pi camera.
#
#

# Includes
# -------------------------------------------------------------------------------------------------

# Allows use of the Raspberry Pi camera
from picamera import PiCamera

# Library for dealing with stream io
import io

# Threading library, so our code can run multiple things at the same time
import threading

from time import sleep


# Constants
# -------------------------------------------------------------------------------------------------

#RESOLUTION = (320,240)      # camera resolution
RESOLUTION = (640,480)      # camera resolution
ROTATION = 180              # camera rotation
JPEGQUALITY = 90            # 0 to 100, higher is better quality but more data
FPS = 15                    # video frames per second.  Reduce if bandwidth is an issue, increase if quality is an issue


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
        stream = io.BytesIO()

        # Start capturing frames as a stream
        cap = self.camera.capture_continuous(stream, format="jpeg", use_video_port=True, quality=self.jpegQuality)

        # For each frame captured, return it to the calling loop
        for foo in cap:
            # store frame
            stream.seek(0)
            frame = stream.read()

            yield frame

            # reset stream for next frame
            stream.seek(0)
            stream.truncate()       


    def _getFrame(self):     
        """Return the last frame read, if there is one"""
        
        if self.lastFrame is None:
            return None
        else:
            return self.lastFrame 


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
            