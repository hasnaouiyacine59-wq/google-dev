# google-dev

A Docker image with noVNC (1920x1080), Google Chrome, Python 3, xterm + zsh, and Playwright — accessible via browser on port 8080.

## Requirements
- Docker
- 6–8 GB RAM recommended (minimum 4 GB)

## Build & Deploy

```bash
# Build
docker build -t chrome-novnc .

# Run
docker run -d --name chrome --shm-size=4g --memory=6g -p 8080:8080 chrome-novnc
```

Open: http://localhost:8080/vnc.html

## Stop & Remove

```bash
docker stop chrome && docker rm chrome
```

## One-liner: Clone & Deploy

```bash
git clone https://github.com/hasnaouiyacine59-wq/google-dev.git && cd google-dev && docker build -t chrome-novnc . && docker run -d --name chrome --shm-size=4g --memory=6g -p 8080:8080 chrome-novnc
```
