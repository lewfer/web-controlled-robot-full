DATE=`date '+%Y-%m-%d %H:%M:%S'`
echo "Myservice service started at ${DATE}" | systemd-cat -p info

python3 /home/pi/web-controlled-robot-full/robot/mqtt_picon_robot.py &
python3 /home/pi/web-controlled-robot-full/web-server/streamvideo.py

