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
# Start virtual display
#git clone https://github.com/hasnaouiyacine59-wq/gitlab_new.git

Xvfb $DISPLAY -screen 0 $RESOLUTION &
sleep 1

# Fix NumLock
numlockx on

# Run entire session under a proper dbus session bus
# Use double-quotes so $DISPLAY is expanded correctly
exec dbus-run-session -- bash -c "
    export DISPLAY=$DISPLAY

    # Window manager — must run in background with &, not --daemon
    xfwm4 --replace --sm-client-disable &
    sleep 1

    # Desktop, panel, settings daemon
    xfdesktop --sm-client-disable &
    xfce4-panel --sm-client-disable &
    xfsettingsd --sm-client-disable &
    sleep 2

    # Fix xfce4-power-manager panel plugin: hide it and disable unsafe session actions
    xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/show-tray-icon -s false --create -t bool
    # Action buttons plugin: disable shutdown, reboot, suspend, hibernate — keep only logout
    xfconf-query -c xfce4-panel -p /plugins/plugin-6/appearance -s 0 --create -t int
    xfconf-query -c xfce4-panel -p /plugins/plugin-6/items \
        --create -t string -s "+logout-dialog" \
        -t string -s "-shutdown" \
        -t string -s "-restart" \
        -t string -s "-suspend" \
        -t string -s "-hibernate" \
        -t string -s "-switch-user" \
        -t string -s "-lock-screen" 2>/dev/null || true
    # Also tell xfce4-session to not offer shutdown/reboot
    xfconf-query -c xfce4-session -p /shutdown/ShowHibernate -s false --create -t bool
    xfconf-query -c xfce4-session -p /shutdown/ShowSuspend   -s false --create -t bool
    xfconf-query -c xfce4-session -p /shutdown/ShowHybridSleep -s false --create -t bool

    # Apply Arc-Dark theme
    xfconf-query -c xsettings -p /Net/ThemeName       -s 'Arc-Dark' --create -t string
    xfconf-query -c xsettings -p /Net/IconThemeName   -s 'gnome'    --create -t string
    xfconf-query -c xfwm4     -p /general/theme       -s 'Arc-Dark' --create -t string

    # Solid dark desktop background
    xfconf-query -c xfce4-desktop \
        -p /backdrop/screen0/monitorVNC-0/workspace0/color-style \
        -s 0 --create -t int
    xfconf-query -c xfce4-desktop \
        -p /backdrop/screen0/monitorVNC-0/workspace0/rgba1 \
        --create -t double -t double -t double -t double \
        -s 0.17 -s 0.17 -s 0.17 -s 1.0

    # Clipboard sync (noVNC copy/paste)
    autocutsel -fork
    autocutsel -selection PRIMARY -fork

    # VNC server
    x11vnc -display $DISPLAY -nopw -forever -shared -rfbport 5900 -noxdamage &
    sleep 1

    # noVNC web interface
    websockify --web /usr/share/novnc/ 8080 localhost:5900 &

    wait
"
