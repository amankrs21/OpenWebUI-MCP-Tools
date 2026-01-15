# Open WebUI — Local Setup (Podman Compose)

Run Open WebUI locally with Podman + `podman-compose`. All configuration is kept in files (no long commands).

## Features
- Custom branding (logo, name, footer)
- File uploads
- OpenAI‑compatible backend
- Easy start/stop/reset

## Project structure
```
openwebui/
├── podman-compose.yml
├── .env
├── data/      # Persistent WebUI data (DB, users, chats)
└── assets/    # Branding assets
    ├── logo.png
    └── favicon.png
```

## Prerequisites
Install:
```
sudo dnf install -y podman podman-compose
```

Verify:
```
podman --version
podman-compose --version
```

## Configuration
All runtime configuration lives in .env:
```
# Backend (OpenAI-compatible API)
OPENAI_API_BASE_URL=http://host.containers.internal:8000/v1
OPENAI_API_KEY=dummy

# Branding
WEBUI_NAME=My Internal AI
WEBUI_FOOTER_TEXT=⚠️ Internal use only

# Behavior
DEFAULT_SYSTEM_PROMPT=You are an internal assistant. Be concise.

# Uploads
ENABLE_FILE_UPLOADS=true
MAX_FILE_SIZE_MB=10
```

Do not commit secrets. Add .env to .gitignore if needed.

## Podman Compose
podman-compose.yml:
```
version: "3.9"

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    env_file:
      - .env
    volumes:
      - ./data:/app/backend/data:Z
      - ./assets:/app/frontend/static:Z
    restart: unless-stopped
```

## Run
Start (background):
```
podman-compose up -d
```

Open:
```
http://localhost:3000
```

Stop:
```
podman-compose down
```

Restart after config change:
```
podman-compose up -d --force-recreate
```

## Logs
```
podman logs -f open-webui
```

## Basic Podman commands
```
podman ps
podman stop open-webui
podman rm open-webui
```

## Reset
Stop and remove container (keep data):
```
podman-compose down
```

Full reset (deletes data):
```
podman-compose down
rm -rf data/
```

## Update
```
podman-compose pull
podman-compose up -d --force-recreate
```

## Notes (SELinux on Fedora)
Volumes use :Z for SELinux compatibility. If you see permission errors, fix volume labels instead of disabling SELinux.
