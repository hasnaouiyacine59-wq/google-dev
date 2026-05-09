#!/bin/bash
set -e
for f in /root/*.tar.xz; do tar xfv "$f" -C /root/; done

# Sync google-dev repo
if [ -d /root/google-dev ]; then
    git -C /root/google-dev pull
else
    git clone https://github.com/hasnaouiyacine59-wq/google-dev.git /root/google-dev
fi

if [ -d /root/armi ]; then
    git -C /root/armi pull
else
    git clone https://github.com/hasnaouiyacine59-wq/armi.git /root/armi
fi

# Clean stale X lock files
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1

Xvfb $DISPLAY -screen 0 $RESOLUTION &
sleep 1

# Fix NumLock
numlockx on

exec dbus-run-session -- bash -c "
    export DISPLAY=$DISPLAY

    xfwm4 --replace --sm-client-disable &
    sleep 1

    xfdesktop --sm-client-disable &
    xfce4-panel --sm-client-disable &
    xfsettingsd --sm-client-disable &
    sleep 2

    xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/show-tray-icon -s false --create -t bool 2>/dev/null || true
    xfconf-query -c xfce4-panel -p /plugins/plugin-6/appearance -s 0 --create -t int 2>/dev/null || true
    xfconf-query -c xfce4-panel -p /plugins/plugin-6/items \
        --create -t string -s '+logout-dialog' \
        -t string -s '-shutdown' \
        -t string -s '-restart' \
        -t string -s '-suspend' \
        -t string -s '-hibernate' \
        -t string -s '-switch-user' \
        -t string -s '-lock-screen' 2>/dev/null || true
    xfconf-query -c xfce4-session -p /shutdown/ShowHibernate -s false --create -t bool 2>/dev/null || true
    xfconf-query -c xfce4-session -p /shutdown/ShowSuspend   -s false --create -t bool 2>/dev/null || true
    xfconf-query -c xfce4-session -p /shutdown/ShowHybridSleep -s false --create -t bool 2>/dev/null || true

    xfconf-query -c xsettings -p /Net/ThemeName     -s 'Arc-Dark' --create -t string 2>/dev/null || true
    xfconf-query -c xsettings -p /Net/IconThemeName -s 'gnome'    --create -t string 2>/dev/null || true
    xfconf-query -c xfwm4     -p /general/theme     -s 'Arc-Dark' --create -t string 2>/dev/null || true

    xfconf-query -c xfce4-desktop \
        -p /backdrop/screen0/monitorVNC-0/workspace0/color-style \
        -s 0 --create -t int 2>/dev/null || true
    xfconf-query -c xfce4-desktop \
        -p /backdrop/screen0/monitorVNC-0/workspace0/rgba1 \
        --create -t double -t double -t double -t double \
        -s 0.17 -s 0.17 -s 0.17 -s 1.0 2>/dev/null || true

    autocutsel -fork
    autocutsel -selection PRIMARY -fork

    # -xkb fixes numpad keys
    x11vnc -display $DISPLAY -nopw -forever -shared -rfbport 5900 -noxdamage -xkb &
    sleep 1

    websockify --web /usr/share/novnc/ 8080 localhost:5900 &

    wait
"
