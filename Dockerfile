FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    RESOLUTION=1920x1080x24

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    openbox \
    tint2 \
    xfce4-terminal \
    wget \
    ca-certificates \
    fonts-liberation \
    fonts-dejavu-core \
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
    # Install Google Chrome
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY google_dev_gitcode/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && \
    playwright install chromium --with-deps

RUN chsh -s $(which zsh)

# Openbox right-click menu
RUN mkdir -p /root/.config/openbox && \
    printf '<?xml version="1.0" encoding="UTF-8"?>\n<openbox_menu>\n  <menu id="root-menu" label="Desktop">\n    <item label="Terminal"><action name="Execute"><command>xfce4-terminal</command></action></item>\n    <separator/>\n    <item label="Chrome"><action name="Execute"><command>google-chrome --no-sandbox --disable-dev-shm-usage</command></action></item>\n  </menu>\n</openbox_menu>\n' > /root/.config/openbox/menu.xml

COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]
