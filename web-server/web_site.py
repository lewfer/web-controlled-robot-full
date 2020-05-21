# www.thinkcreatelearn.co.uk
#
# Main web site page
# 
# Controls all web page requests and calls other functions to carry out the request
#
# Requires installation of Flask and Paho MQTT.  Install with:
#
#   pip install flask
#   pip install paho-mqtt
#
# For details see:
#   https://pypi.org/project/paho-mqtt/
#   https://pypi.org/project/Flask/


# Includes
# -------------------------------------------------------------------------------------------------

# Flask provides a framework for building web applications in Python
from flask import Flask, render_template, Response, request, url_for, session, redirect

# Paho MQTT provides the ability to send messages from one computer to another using the MQTT protocol
import paho.mqtt.publish as publish

# We keep the video streaming code in a separate python file
# Choose which streaming module you want
from pi_camera_player import VideoPlayer
#from webcam_player import VideoPlayer

# Allow us to pass Python dictionaries to javascript
import json

# Allow us to select random robots
import random

# Allow use to implement pass-through to cameras
import requests

# Allow us to work out time in room
import time


# Constants
# -------------------------------------------------------------------------------------------------

# Get settings from an external modules so they are all in one place
from web_site_settings import *


# Global objects
# -------------------------------------------------------------------------------------------------
# Create our video player object
player = VideoPlayer(resolution=MAIN_CAMERA_RESOLUTION, rotation=MAIN_CAMERA_ROTATION)   

# Create the Flask web application
app = Flask(__name__)

# Set the secret key so session encryption works
app.secret_key = b'A]qr>n@2XB"{B;CN'

# List of users - this will be filled in as users log in
users = {}



# Utility functions
# -------------------------------------------------------------------------------------------------

def robotAvailable():
    """Check if robot available."""
    # Go through all robots and find a list of ones with no user linked
    robotNames = []
    for name, user in robots.items():
        if user is None:
            robotNames.append(name)

    # Return a random robot from this list
    if len(robotNames)==0:
        return None
    else:
        return random.choice(robotNames)


def handleLoginForm(loginForm):
    """Deal with user logins"""
    # Get user name entered
    requestedUsername = request.form['username'] 

    # If requested username matches session name, let them straight in
    if 'username' in session:
        if requestedUsername == session['username']:
            print("Matches session")
            return redirect(url_for('waitingroom'))

    # If requested username already exists, try again !! but what if same user logging in from elsewhere?
    if requestedUsername in users:
        print("Already exists")
        return redirect(url_for(loginForm, error="User name " + requestedUsername + " already taken.  Try again"))

    # New user, so save in session and database
    print("New user")
    session['username'] = request.form['username']              # save username in the session
    users[session['username']] = {"robot":None, "inroom":0}     # save username in the database

    return redirect(url_for('waitingroom'))


def linkRobotAndUser(robotName):
    """Associate the robot with the current user (so no one else can take it)"""
    userName = session['username']
    robots[robotName] = userName                # link user to robot
    users[userName]["robot"] = robotName        # link robot to user


def unlinkRobotAndUser():
    """Free up the robot for another user and remove the user"""
    userName = session['username']              # get current user
    robotName = users[userName]["robot"]        # get their robot name
    robots[robotName] = None                    # unlink the user from the robot
    users[userName]["robot"] = None             # unlink the robot from the user
    users.pop(userName, None)                   # remove the username
    session.clear()                             # clear the user name from the session


def userHasRobot():
    """Check if the current user has a robot"""
    userName = session['username']
    return users[userName]["robot"] is not None   


def userName():
    """Get the current user name for this session"""
    return session['username']


def userRobot():
    """Get the user's robot"""
    userName = session['username']
    return users[userName]["robot"]       


def userLoggedIn():
    """Check if the user has provided a name"""
    return 'username' in session


def stopEverything():
    """Stop robots and unlink user"""
    for name, user in robots.items():
        topic = MQTT_TOPIC + name
        publish.single(topic, "stop", hostname=MQTT_SERVER)
        robots[name] = None

    # Remove all users
    users = {}


def getTimeInSeconds():
    """Get the current system time in seconds"""
    return int(round(time.time()))


def startTimeInRoom():
    """Start the stopwatch"""
    userName = session['username']
    users[userName]["inroom"] = getTimeInSeconds()


def getTimeLeftInRoom():
    """Get time left on stopwatch"""
    userName = session['username']
    return TIME_IN_ROOM - (getTimeInSeconds() - users[userName]["inroom"])


def getRoomCameras():
    """Get Json string of cameras not linked to robot"""

    # Get available robot and camera names
    robotNames = list(robots.keys())
    cameraNames = list(cameras.keys())

    # Allow cameras that are not robot-specific
    allowedCameraNames = [c for c in cameraNames if c not in robotNames] 
    allowedCameras = {c:cameras[c] for c in allowedCameraNames if c in cameras}
    print(json.dumps(allowedCameras))
    return json.dumps(allowedCameras)


def getRobotCameras():
    """Get Json string of cameras for current user robot"""

    # Get available robot and camera names
    robotNames = list(robots.keys())
    cameraNames = list(cameras.keys())

    # Allow cameras that are not robot-specific, plus the current user's robot camera
    allowedCameraNames = [c for c in cameraNames if c not in robotNames] + [userRobot()]
    allowedCameras = {c:cameras[c] for c in allowedCameraNames if c in cameras}
    print(json.dumps(allowedCameras))
    return json.dumps(allowedCameras)


# Web request handlers
# -------------------------------------------------------------------------------------------------

# Viewing room - anyone can enter
@app.route('/', methods = ['GET'])
def viewingroom():
    return render_template('viewingroom.html', cameras=getRoomCameras()) 


# Waiting room - can enter if you have provided your user name
@app.route('/waitingroom', methods = ['GET', 'POST'])
def waitingroom():
    # If we get a POST it means the user entered a login name, so process it
    if request.method == 'POST':
        return handleLoginForm('waitingroom')

    # If we get a GET it means the user browsed to or redirected to the waiting room
    if request.method == 'GET':
        # Need to be logged in to enter waiting room, so return to viewing room if not
        if 'username' not in session:
            return redirect(url_for('viewingroom'))

        # Enter the waiting room
        return render_template('waitingroom.html', username=session['username'], cameras=getRoomCameras())


# Callback to check if there is a robot available
@app.route('/checkavailability')
def checkavailability():
    # Don't allow calls here if user not logged in
    if not userLoggedIn():
        return redirect(url_for('viewingroom')) # go back to viewing room

    # Check if user already has a robot
    # If they have, probably means they tried to jump back into waiting room, so kick them out
    robotName = userRobot()
    if userRobot() is not None:
        print("User already has robot", robotName, ".  Kicking out")
        return redirect(url_for('gameover'))  

    # Check if robot available and handle accordingly
    robotName = robotAvailable()
    if robotName is None:
        # No robot, so just respond
        return Response("")                     
    else:
        # Robot available, so assign the robot to the user and redirect to the room
        linkRobotAndUser(robotName)
        startTimeInRoom()
        return redirect(url_for('room'))        


# Robot room
@app.route('/room', methods = ['GET'])
def room():
    # Don't allow calls here if user not logged in or has no robot
    if not userLoggedIn() or not userHasRobot():
        return redirect(url_for('viewingroom'))

    # Get the time left in the room
    timeLeft = getTimeLeftInRoom() 

    # Show the room
    return render_template('room.html', username=userName(), robotname=userRobot(), cameras=getRobotCameras(), timeinroom=timeLeft, timebeforeexit=TIME_BEFORE_EXIT)


# Player is redirected here when their time is up
@app.route('/gameover')
def gameover():
    print("Game over")
    # Don't allow calls here if user not logged in
    if not userLoggedIn():
        return redirect(url_for('viewingroom'))

    # Free up the robot and return to the viewing room
    unlinkRobotAndUser()
    return redirect(url_for('viewingroom'))   


# When a request to the /video url is made, we run this
@app.route('/video')
def video_feed():          
    # Pass in the generator function to the response.  Flask will then loop around, calling the generator.
    # We use the multipart mime type.  In this case we have a video made up of multiple frames.
    # I.e. we are saying that our content is made up of multiple parts (the frames).
    return Response(player.genVideo(), mimetype='multipart/x-mixed-replace; boundary=frame')


# When a request to view a camera is made, we run this
@app.route('/camera/<camera_name>')
def camera_feed(camera_name):       
    print(camera_name, cameras[camera_name]) 

    # Get the url for the camera
    cameraUrl = cameras[camera_name] 

    # Generate the video feed
    if not DIRECT_CAMERA and cameraUrl.startswith("http"):
        # The camera is running somewhere else, grab the content and pass it through
        r = requests.get(cameraUrl, stream=True)
        return Response(r.iter_content(chunk_size=10*1024), content_type=r.headers['Content-Type'])
    else:
        # The camera is running as part of this app.  Redirect to it
        return redirect(cameraUrl)


# When a control request comes in, we run this
@app.route('/control/<control_name>')
def control(control_name):
    if not userLoggedIn():
        return redirect(url_for('viewingroom'))

    # Get the robot name
    robotName = userRobot()
    print("Control ", userName(), robotName, control_name)

    # If end of session, free up robot, delete user and stop robot
    if control_name=="end":
        unlinkRobotAndUser()
        control_name = "stop"    

    # Create the topic for the message
    topic = MQTT_TOPIC + robotName
    if control_name=="move":
        # For a move command we need to package up the x and y coordinates
        x = request.args.get('x')
        y = request.args.get('y')
        #print(topic, "->", control_name, x, y)
        publish.single(topic, control_name+":"+x+","+y, hostname=MQTT_SERVER)
    else:
        # Other commands are just sent through
        #print(topic, "->", control_name)
        publish.single(topic, control_name, hostname=MQTT_SERVER)
    return Response('queued')


# When a request for the admin screen comes in
@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    print("login", "-"+request.method+"-")
    # If called with GET we show the login form
    if request.method == 'GET':
        return '<form action = "/admin" method = "post"><label>Password:</label><input type = "text" name = "password"/></p></form>'

    # If called with POST, we have received the filled-in login form
    if request.method == 'POST':
        # If they don't know the secret password, don't let them in
        if request.form['password']!='friskyrobot':
            return 'Not allowed'

        # Build list of users as HTML
        userlist = "<ul>"
        for name, info in users.items():
            userlist += "<li>" + name + " ==> " + str(info) + "</li>"
        userlist += "</ul>"

        # Build list of robots as HTML
        robotlist = "<ul>"
        for name, info in robots.items():
            robotlist += "<li>" + name + " assigned to " + str(info) + "</li>"  
        robotlist += "</ul>"   

        # Render the admin page
        return render_template('admin.html', users=userlist, robots=robotlist)    


# When a request for the admin screen comes in
@app.route('/stopeverything', methods = ['GET'])
def stopeverything():
    print("Stop everything")
    stopEverything()
    session.clear() 
    return Response('')


# Run the web site.  Specifying 0.0.0.0 as the host makes it visible to the rest of the network.
# We runs as a threaded site so we can have multiple clients connect and so the site responds to user interaction when busy streaming
if __name__ == '__main__':
    #print(flask.__version__)
    stopEverything() # reset robots if they are crashed
    app.run(threaded=True, host='0.0.0.0', port=WEBSITE_PORT) #, debug=True)

