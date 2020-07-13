#! /usr/bin/python3

# Think Create Learn
# www.thinkcreatelearn.co.uk
#
# ROSI remote control solution
#
# Use a remote control to control a robot

# ======================================================================================================
# Imports
# ======================================================================================================
import rosi_library as robot
import paho.mqtt.client as mqtt

# ======================================================================================================
# Constants
# ======================================================================================================

# If you need to change the defaults, change them in settings.py:
from settings import *

# ======================================================================================================
# Global variables
# ======================================================================================================


# ======================================================================================================
# Functions
# ======================================================================================================

def map(n, a, b, c, d):
    return (n-a) * (d-c)/(b-a)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC)
 
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    m = msg.payload.decode("utf-8")
    print(msg.topic+" " + m)

    if m=="forward":
        robot.turnMotors(MAXSPEED,MAXSPEED) 
    elif m=="backward":
        robot.turnMotors(-MAXSPEED,-MAXSPEED) 
    elif m=="left":
        robot.turnMotors(-MAXSPEED,MAXSPEED) 
    elif m=="right":
        robot.turnMotors(MAXSPEED,-MAXSPEED) 
    elif m=="stop":
        robot.turnMotors(0,0) 
    elif m.startswith("move"):
        x = int(m[m.find(":")+1:m.find(",")])
        y = int(m[m.find(",")+1:])
        print(x,y)
        leftMotorSpeed = y
        rightMotorSpeed = y

        if y > 0:
            if x > 20:
                leftMotorSpeed = map(x, 20, 100, 0, MAXSPEED)
                rightMotorSpeed = 0
            elif x < -20:
                leftMotorSpeed = 0
                rightMotorSpeed = map(-x, 20, 100, 0, MAXSPEED)
        else:
            if x > 20:
                leftMotorSpeed = map(x, 20, 100, -0, -MAXSPEED)
                rightMotorSpeed = 0
            elif x < -20:
                leftMotorSpeed = 0
                rightMotorSpeed = map(-x, 20, 100, -0, -MAXSPEED)

        '''            
        # Adjust motor speed based on right-left axis
        if x < 0:  
            # Turning left, slow the left motor down
            leftMotorSpeed = leftMotorSpeed - leftMotorSpeed * -x/100  
        elif x > 0:  
            # Turning right, slow the right motor down
            rightMotorSpeed = rightMotorSpeed - rightMotorSpeed * x/100
        '''
        
        # Turn motors
        print(leftMotorSpeed,rightMotorSpeed)
        robot.turnMotors(int(leftMotorSpeed), int(rightMotorSpeed))         
    


# ======================================================================================================
# Main program
# ======================================================================================================

# Create an MQTT client, which will allow the robot to receive messages
client = mqtt.Client()

# Set up the function that will be called when we connect to the broker
client.on_connect = on_connect

# Set up the function that will be called when we receive a message
client.on_message = on_message

# Connect to the broker, so we can receive messages
client.connect(MQTT_BROKER, port=1883, keepalive=60)


robot.start()
 
# Connect to the broker, so we can receive messages
client.loop_forever()


robot.finish()

