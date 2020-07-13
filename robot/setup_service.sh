sudo cp runrobot.sh /usr/bin
sudo cp runrobot.service /etc/systemd/system/
sudo cp runrobot.timer /etc/systemd/system/
sudo systemctl enable runrobot.service
sudo systemctl enable runrobot.timer

