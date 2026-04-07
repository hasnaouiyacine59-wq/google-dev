#!/bin/bash
set -e

echo "[1/4] Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
  libglib2.0-0 libnss3 libnspr4 libdbus-1-3 \
  libatk1.0-0 libatk-bridge2.0-0 libcups2 \
  libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
  libxfixes3 libxrandr2 libgbm1 xvfb \
  libasound2t64 || sudo apt-get install -y -qq libasound2

echo "[2/4] Installing Python packages..."
pip install -q playwright opencv-python-headless numpy

echo "[3/4] Installing Playwright Chromium..."
export PATH="$HOME/.local/bin:$PATH"
playwright install chromium
playwright install-deps chromium

echo "[4/4] Starting virtual display..."
sudo mkdir -p /tmp/.X11-unix
sudo chmod 1777 /tmp/.X11-unix
Xvfb :99 -screen 0 1366x768x24 &
sleep 1
export DISPLAY=:99

echo "Done! Run with: xvfb-run python visual_automation.py -s 1"
