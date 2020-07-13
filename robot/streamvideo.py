# www.thinkcreatelearn.co.uk
#
# Stream video
# 
# Streams video over http
#


# Includes
# -------------------------------------------------------------------------------------------------

# Flask provides a framework for building web applications in Python
from flask import Flask, Response

# We keep the video streaming code in a separate python file
# Choose which streaming module you want
from pi_camera_player import VideoPlayer
#from webcam_player import VideoPlayer

# Settings
# -------------------------------------------------------------------------------------------------

# If you need to change the defaults, change them in settings.py:
from settings import *


# Global objects
# -------------------------------------------------------------------------------------------------
# Create our video player object
player = VideoPlayer()   

# Create the Flask web application
app = Flask(__name__)

# Set the secret key so session encryption works
app.secret_key = b'f5fg674a&3l^N$='


# Web request handlers
# -------------------------------------------------------------------------------------------------

# When a request to the /video url is made, we run this
@app.route('/')
@app.route('/video')
def video_feed():          
    # Pass in the generator function to the response.  Flask will then loop around, calling the generator.
    # We use the multipart mime type.  In this case we have a video made up of multiple frames.
    # I.e. we are saying that our content is made up of multiple parts (the frames).
    return Response(player.genVideo(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Run the web site.  Specifying 0.0.0.0 as the host makes it visible to the rest of the network.
# We runs as a threaded site so we can have multiple clients connect and so the site responds to user interaction when busy streaming
if __name__ == '__main__':
    #print(flask.__version__)
    app.run(threaded=True, host='0.0.0.0', port=VIDEO_STREAM_PORT) #, debug=True)
