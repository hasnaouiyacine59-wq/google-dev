FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    RESOLUTION=1920x1080x24 \
    XDG_SESSION_TYPE=x11 \
    XDG_CURRENT_DESKTOP=XFCE \
    DBUS_SESSION_BUS_ADDRESS=autolaunch:

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    xfce4 \
    xfce4-terminal \
    xfce4-taskmanager \
    xfce4-notifyd \
    arc-theme \
    greybird-gtk-theme \
    adwaita-icon-theme \
    dbus-x11 \
    autocutsel \
    numlockx \
    wget \
    ca-certificates \
    fonts-liberation \
    fonts-dejavu-core \
    fonts-ubuntu \
    fonts-cantarell \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    zsh \
    python3 \
    python3-pip \
    --no-install-recommends && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY google_dev_gitcode/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    playwright install chromium --with-deps

COPY google_dev_gitcode/ /root/google_dev_gitcode/
COPY kali_google_dev_gitcode/ /root/kali_google_dev_gitcode/

RUN chsh -s $(which zsh)

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]
