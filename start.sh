#!/bin/bash
exec > /proc/1/fd/1 2>/proc/1/fd/2
set -x

# Unpack archives
for f in /root/*.tar.xz; do tar xf "$f" -C /root/ 2>/dev/null || true; done

# Sync repos
if [ -d /root/google-dev ]; then git -C /root/google-dev pull; else git clone https://github.com/hasnaouiyacine59-wq/google-dev.git /root/google-dev; fi
if [ -d /root/armi ]; then git -C /root/armi pull; else git clone https://github.com/hasnaouiyacine59-wq/armi.git /root/armi; fi

# Clean stale X lock
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1

# Virtual display
Xvfb :1 -screen 0 1920x1080x24 &
sleep 2

export DISPLAY=:1
numlockx on

# Start dbus session
eval $(dbus-launch --sh-syntax)
export DBUS_SESSION_BUS_ADDRESS

# Window manager & desktop
xfwm4 --replace --sm-client-disable &
sleep 1
xfdesktop --sm-client-disable &
xfce4-panel --sm-client-disable &
xfsettingsd --sm-client-disable &
sleep 2

# Theme
xfconf-query -c xsettings -p /Net/ThemeName     -s 'Arc-Dark' --create -t string 2>/dev/null || true
xfconf-query -c xsettings -p /Net/IconThemeName -s 'gnome'    --create -t string 2>/dev/null || true
xfconf-query -c xfwm4     -p /general/theme     -s 'Arc-Dark' --create -t string 2>/dev/null || true

# Clipboard
autocutsel -fork
autocutsel -selection PRIMARY -fork

# VNC
x11vnc -display :1 -nopw -forever -shared -rfbport 5900 -noxdamage -xkb &
sleep 1

# noVNC — foreground, keeps container alive
exec websockify --web /usr/share/novnc/ 8080 localhost:5900
