# google-dev

A Docker image with noVNC, Google Chrome, Python 3, and xterm terminal accessible via browser on port 8080.

## Quick Start

```bash
docker build -t chrome-novnc .
docker run -d --name chrome --shm-size=2g -p 8080:8080 chrome-novnc
```

Open: http://localhost:8080/vnc.html
