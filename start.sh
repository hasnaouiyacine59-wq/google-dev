#!/bin/bash
set -e

# Start D-Bus
eval $(dbus-launch --sh-syntax)
export DBUS_SESSION_BUS_ADDRESS

# Start virtual display
Xvfb $DISPLAY -screen 0 $RESOLUTION &
sleep 1

# Fix NumLock on
numlockx on

# Start XFCE components individually (more reliable in headless containers)
xfwm4 --daemon --sm-client-disable
xfdesktop --sm-client-disable &
xfce4-panel --sm-client-disable &
xfsettingsd --sm-client-disable &
sleep 2

# Apply Arc theme + icons
xfconf-query -c xsettings -p /Net/ThemeName -s "Arc-Dark" --create -t string
xfconf-query -c xsettings -p /Net/IconThemeName -s "Adwaita" --create -t string
xfconf-query -c xfwm4 -p /general/theme -s "Arc-Dark" --create -t string

# Set desktop background to solid dark color (no black void)
xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitorVNC-0/workspace0/color-style -s 0 --create -t int
xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitorVNC-0/workspace0/rgba1 \
    --create -t double -t double -t double -t double -s 0.17 -s 0.17 -s 0.17 -s 1.0

# Clipboard sync for noVNC copy/paste
autocutsel -fork
autocutsel -selection PRIMARY -fork

# Start VNC server
x11vnc -display $DISPLAY -nopw -forever -shared -rfbport 5900 -noxdamage &
sleep 1

# Start noVNC
websockify --web /usr/share/novnc/ 8080 localhost:5900 &

wait
