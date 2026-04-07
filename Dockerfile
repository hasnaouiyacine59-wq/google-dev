FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    VNC_PASSWORD=password \
    RESOLUTION=1920x1080x24

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    openbox \
    obconf \
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
    xterm \
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

# Set zsh as default shell
RUN chsh -s $(which zsh)

# Install oh-my-zsh for better zsh experience
RUN sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended

# xterm config: dark bg, good font, zsh
RUN echo '*.background: #1e1e1e\n*.foreground: #d4d4d4\n*.font: DejaVu Sans Mono:size=12\n*.scrollBar: true\n*.scrollTtyOutput: false\n*.saveLines: 5000\nXTerm*faceName: DejaVu Sans Mono\nXTerm*faceSize: 12' > /root/.Xresources

# Openbox right-click menu with terminal shortcut
RUN mkdir -p /root/.config/openbox && \
    printf '<?xml version="1.0" encoding="UTF-8"?>\n<openbox_menu>\n  <menu id="root-menu" label="Desktop">\n    <item label="Terminal"><action name="Execute"><command>xterm -e zsh</command></action></item>\n    <separator/>\n    <item label="Chrome"><action name="Execute"><command>google-chrome --no-sandbox --disable-dev-shm-usage</command></action></item>\n  </menu>\n</openbox_menu>\n' > /root/.config/openbox/menu.xml && \
    printf '<openbox_config>\n  <menu><file>menu.xml</file><showIcons>no</showIcons></menu>\n</openbox_config>\n' > /root/.config/openbox/rc.xml

RUN chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]
