FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    RESOLUTION=1920x1080x24
ARG VNC_PASSWORD=password

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    xfce4 \
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

# Install oh-my-zsh and set zsh as default shell
RUN sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended && \
    chsh -s $(which zsh)

# Suppress XFCE first-run dialogs
RUN mkdir -p /root/.config/xfce4 && \
    printf '[General]\nFirstRun=false\n' > /root/.config/xfce4/helpers.rc

RUN chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]
