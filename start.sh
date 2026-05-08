#!/bin/bash
for f in /root/*.tar.xz; do tar xfv "$f" -C /root/; done

# Sync repos
if [ -d /root/google-dev ]; then git -C /root/google-dev pull; else git clone https://github.com/hasnaouiyacine59-wq/google-dev.git /root/google-dev; fi
if [ -d /root/armi ]; then git -C /root/armi pull; else git clone https://github.com/hasnaouiyacine59-wq/armi.git /root/armi; fi

# Clean stale X lock
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1

Xvfb $DISPLAY -screen 0 $RESOLUTION &
sleep 1

numlockx on

exec dbus-run-session -- bash -c "
    export DISPLAY=$DISPLAY

    xfwm4 --replace --sm-client-disable &
    sleep 1

    xfdesktop --sm-client-disable &
    xfce4-panel --sm-client-disable &
    xfsettingsd --sm-client-disable &
    sleep 2

    # Power manager cleanup
    pkill -f xfce4-power-manager 2>/dev/null || true
    xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/show-tray-icon -s false --create -t bool 2>/dev/null || true

    # Theme
    xfconf-query -c xsettings -p /Net/ThemeName     -s 'Arc-Dark' --create -t string 2>/dev/null || true
    xfconf-query -c xsettings -p /Net/IconThemeName -s 'gnome'    --create -t string 2>/dev/null || true
    xfconf-query -c xfwm4     -p /general/theme     -s 'Arc-Dark' --create -t string 2>/dev/null || true

    # Clipboard
    autocutsel -fork
    autocutsel -selection PRIMARY -fork

    # VNC server (-xkb fixes numpad)
    x11vnc -display \$DISPLAY -nopw -forever -shared -rfbport 5900 -noxdamage -xkb &
    sleep 1

    websockify --web /usr/share/novnc/ 8080 localhost:5900 &

    wait
"
