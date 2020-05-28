# www.thinkcreatelearn.co.uk
#
# MQTT Controlled Raspberry Pi Robot
#
# Handles the incoming MQTT messages and translates them into robot movements.
#
# How you then respond to those messages depends on your robot hardware and the behaviour you want.
#
# This code assumes you have a simple robot similar to the one described here:
#   https://projects.raspberrypi.org/en/projects/build-a-buggy/2
#
# But there are lots of ways to build robots with a Raspberry Pi, so adjust the code as necessary.
#


# Imports
# -------------------------------------------------------------------------------------------------

from gpiozero import Robot              # controls the robot hardware
import paho.mqtt.client as mqtt         # provides IoT functionality to send messages between computers

# Constants
# -------------------------------------------------------------------------------------------------

# Settings for MQTT communication
MQTT_BROKER = "web-server"              # Change to name of your broker 
MQTT_TOPIC = "robots/clarissa"          # Change to name of your topic

MAXSPEED = 100                                       # Max % speed

# Globals
# -------------------------------------------------------------------------------------------------

# Set the GPIO pins used to connect to the motor controller
robot = Robot(left=(19,26), right=(16,20))


# Functions
# -------------------------------------------------------------------------------------------------

def map(n, a, b, c, d):
    return (n-a) * (d-c)/(b-a)

def on_connect(client, userdata, flags, rc):
    # Called when the client receives connection acknowledgement response from the broker

    print("MQTT Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)

 
def on_message(client, userdata, msg):
    # Called when a PUBLISH message is received from the broker

    # Extract the message
    m = msg.payload.decode("utf-8")
    print(msg.topic+" " + m)

    # Depending on the message received, make the robot respond
    if m=="forward":
        robot.forward(1.0) 
    elif m=="backward":
        robot.backward(1.0) 
    elif m=="left":
        robot.left(1.0) 
    elif m=="right":
        robot.right(1.0) 
    elif m=="stop":
        robot.stop() 
    elif m.startswith("move"):
        x = int(m[m.find(":")+1:m.find(",")])
        y = int(m[m.find(",")+1:])
        print(x,y)

        '''
        if x > 50:
            robot.right(y/100.0)
        elif x < -50:
            robot.left(y/100.0)
        elif y < 0:
            robot.backward(-y/100.0) 
        else:
            robot.forward(y/100.0)     
        ''' 

        if x > 20:
            robot.right(map(x, 20, 100, 0, MAXSPEED*1.0/100))
        elif x < -20:
            robot.left(map(-x, 20, 100, 0, MAXSPEED*1.0/100))
        elif y < 0:
            #robot.backward(-y/100.0) 
            robot.backward(map(-y, 0, 100, 0, MAXSPEED*1.0/100))
        else:
            #robot.forward(y/100.0)     
            robot.forward(map(y, 0, 100, 0, MAXSPEED*1.0/100))

# Main program
# -------------------------------------------------------------------------------------------------

# Create an MQTT client, which will allow the robot to receive messages
client = mqtt.Client()

# Set up the function that will be called when we connect to the broker
client.on_connect = on_connect

# Set up the function that will be called when we receive a message
client.on_message = on_message
 
# Connect to the broker, so we can receive messages
client.connect(MQTT_BROKER)
 
# Now just loop, waiting for messages
client.loop_forever()
