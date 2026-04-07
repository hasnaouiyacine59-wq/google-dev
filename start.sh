#!/bin/bash
set -e

# Start virtual display
Xvfb $DISPLAY -screen 0 $RESOLUTION &
sleep 1

# Start window manager + taskbar
openbox &
tint2 &

# Start VNC server
x11vnc -display $DISPLAY -nopw -forever -shared -rfbport 5900 &
sleep 1

# Start noVNC
websockify --web /usr/share/novnc/ 8080 localhost:5900 &
sleep 1

# Launch Chrome
google-chrome \
  --no-sandbox \
  --disable-dev-shm-usage \
  --display=$DISPLAY \
  --start-maximized \
  about:blank &

# Launch terminal
xfce4-terminal &

wait
