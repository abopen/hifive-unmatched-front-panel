#!/usr/bin/bash

apt update

apt install -y lm-sensors python3-dev python3-pip libfreetype6-dev libjpeg8-dev libsdl1.2-dev 

pip3 install luma.oled psutil

cp -R fp /opt

cp *.service /etc/systemd/system

#systemctl enable oled-splash
systemctl enable oled-info
systemctl start oled-info
