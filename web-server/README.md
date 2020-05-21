# Web Controlled Robots (Full Version)

These are brief notes and are not intended to be a full tutorial.  A simpler version of this code is explained in detail here:

https://www.thinkcreatelearn.co.uk/resources/web-controlled-robot.html


The project contains 2 directories.  

The web-server directory contains the main web application.  Install this on a Raspberry Pi 3 in a directory called web-server.

The robot directory contains the code for the robot.  Install this on each Raspberry Pi robot you want to control in a directory called robot.

## Web server setup

Follow the setup instructions here to install Mosquitto and Paho:

https://www.thinkcreatelearn.co.uk/resources/web-controlled-robot.html


Edit the sessings in web_site_settings.py

Start the web application by running:

> python3 web_site.py


## Additional camera setup

On each computer running additional cameras, run:

> python3 streamvideo.py


Note that you can alter the code to rotate the camera, change the resolution, etc.

## Robot setup

On each robot, edit mqtt_robot.py.  Find these lines:

<pre>
MQTT_BROKER = "web-server"              # Change to name of your broker 
MQTT_TOPIC = "robots/clarissa"          # Change to name of your topic
</pre>

Change the name "web-server" to the name or IP address of your web server.

Change the name "clarissa" to the name of this robot.

Start the robot:

> python3 mqtt_robot.py


## Exposing your server on the internet

The best way to do this is to set up a DMZ or port forwarding on your router.  Otherwise you could use a service like ngrok.


