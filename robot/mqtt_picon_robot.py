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

MQTT_SERVER = "web-server"                           # Change to name of your broker 
MQTT_TOPIC = "robots/edwina"                         # Change to name of your topic
MAXSPEED = 100                                       # Max % speed

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

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(MQTT_SERVER, 1883, 60)


robot.start()
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()


robot.finish()

'''

try:

    # Variable to indicate if we are still running
    running = True

    robot.start()

    with ControllerResource() as joystick:
        print ("Found joystick")
        while running and joystick.connected:

            presses = joystick.check_presses()
            
            if joystick.presses.start:
                # We want to exit the program                
                running = False
               
            if joystick.presses.cross:
                # We want to stop the robot
                robot.turnMotors(0, 0) 
                
            if joystick.presses.dleft:
                # We want to spin the robot left
                robot.turnMotors(-100, 100)

            if joystick.presses.dright:
                # We want to spin the robot left
                robot.turnMotors(100, -100)                
                
            if joystick.ly or joystick.rx:
                y = joystick.ly
                x = joystick.rx
                # We want to move the robot according to the joystick positions

                # y is 1.0 for full forward, -1.0 for full backward and 0.0 for stop.  
                # x is 1.0 for full right, -1.0 for full left and 0.0 for straight.        

                # Work out motor speed based on forward-backward axis
                leftMotorSpeed = y * 100
                rightMotorSpeed = y * 100

                # Adjust motor speed based on right-left axis
                if x < 0:  
                    # Turning left, slow the left motor down
                    leftMotorSpeed = leftMotorSpeed - leftMotorSpeed * -x  
                elif x > 0:  
                    # Turning right, slow the right motor down
                    rightMotorSpeed = rightMotorSpeed - rightMotorSpeed * x
                
                # Turn motors
                robot.turnMotors(int(leftMotorSpeed), int(rightMotorSpeed))      
               
            # Give the computer a bit of time to rest
            robot.wait(0.1)

    robot.finish()

except IOError:
    print("Unable to find any joystick")
except robot.RosiException as e:
    print(e.value)
except KeyboardInterrupt:
    robot.finish()    
'''
