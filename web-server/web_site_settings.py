# www.thinkcreatelearn.co.uk
#
# Main web site settings page
# 

# Port number that website runs on
WEBSITE_PORT = 5000

# Identify the name of the computer that will act as the MQTT broker
# If it is the same as the computer that is running this web site, you can use localhost
MQTT_SERVER = "localhost"               # Change to name of your MQTT broker 

# Identify the name of the topic that your robot will be listening on
MQTT_TOPIC = "robots/"                  # Change to name of your topic

# Constant to indicate if we go direct to an external camera, or pass the content through this web site
# Direct means the user will need access to the external camera url
# Pass through means the user just needs access to this web site
# Use pass through (i.e. set to False) if you are hosting the web site in a DMZ and just want to expose the main web site
DIRECT_CAMERA = False

# Settings for main camera (the one attached to the web server)
MAIN_CAMERA_RESOLUTION = (640,480)
MAIN_CAMERA_ROTATION = 0

# Dictionary of robots and who is controlling them (initially None)
robots = {"clarissa":None, "petra":None, "betty":None}

# Dictionary of cameras, name and URL
# First one (Main) should be left unchanged
# Additional ones can be added.
# If additional ones are named with the robot name they are dedicated for the robot
cameras = {"Main":"/video"}
#cameras = {"Main":"/video", "Rear":"http://other:5001/video", "petra":"http://petra:5001/video"}

# Time user is allowed in room
TIME_IN_ROOM = 20;        # seconds allowed controlling robot in room
TIME_BEFORE_EXIT = 10;    # seconds to stay in room after control finished