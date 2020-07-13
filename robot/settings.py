# Robot settings

# Settings for robot MQTT communication
MQTT_BROKER = "web-server"              # Change to name of your broker 
MQTT_TOPIC = "robots/clarissa"          # Change to name of your topic

MAXSPEED = 100                          # Max % speed

# Pi camera player

RESOLUTION = (160,120)      # camera resolution
ROTATION = 180              # camera rotation
JPEGQUALITY = 10            # 0 to 100, higher is better quality but more data
FPS = 5                     # video frames per second.  Reduce if bandwidth is an issue, increase if quality is an issue

# Stream video
VIDEO_STREAM_PORT = 5001


