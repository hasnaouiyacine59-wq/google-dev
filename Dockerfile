FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    RESOLUTION=1920x1080x24 \
    XDG_CURRENT_DESKTOP=XFCE

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    xfce4 \
    xfce4-goodies \
    xfce4-terminal \
    xfce4-taskmanager \
    xfce4-notifyd \
    xfce4-power-manager \
    xfce4-screenshooter \
    xfce4-whiskermenu-plugin \
    thunar \
    thunar-volman \
    arc-theme \
    greybird-gtk-theme \
    adwaita-icon-theme \
    adwaita-icon-theme-full \
    gnome-icon-theme \
    humanity-icon-theme \
    hicolor-icon-theme \
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
    nano \
    git \
    xz-utils \
    bash \
    && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    playwright install chromium --with-deps


COPY *.tar.xz /root/

RUN chsh -s $(which zsh)

# Fix bash prompt (PS1) for root
RUN echo 'export PS1="\[\e[1;31m\]\u\[\e[0m\]@\[\e[1;34m\]\h\[\e[0m\]:\[\e[1;32m\]\w\[\e[0m\]# "' >> /root/.bashrc

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]
