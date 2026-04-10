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

# Start XFCE desktop session
startxfce4 &
sleep 3

# Clipboard sync: X selection <-> clipboard (for noVNC copy/paste)
autocutsel -fork
autocutsel -selection PRIMARY -fork

# Start VNC server with clipboard support
x11vnc -display $DISPLAY -nopw -forever -shared -rfbport 5900 \
    -clip xfixed -noxdamage &
sleep 1

# Start noVNC
websockify --web /usr/share/novnc/ 8080 localhost:5900 &

wait
