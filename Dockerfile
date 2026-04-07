FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:1 \
    VNC_PASSWORD=password \
    RESOLUTION=1280x800x24

RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    openbox \
    wget \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libnss3 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    tilix \
    zsh \
    python3 \
    python3-pip \
    --no-install-recommends && \
    # Install Google Chrome
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set zsh as default shell
RUN chsh -s $(which zsh)

# Install oh-my-zsh for better zsh experience
RUN sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
RUN chmod +x /start.sh

EXPOSE 8080

CMD ["/start.sh"]
