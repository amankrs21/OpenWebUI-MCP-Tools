# OpenWebUI MCP Tools — Monorepo

Single entry-point README for all projects in this workspace.

## Project layout
- [llm-server](llm-server/)
- [mcp-server](mcp-server/)
- [openwebui](openwebui/)

## Prerequisites
- Python >= 3.13
- uv package manager
- Podman + podman-compose (for Open WebUI)

Install uv (Linux):
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install Podman + podman-compose (Fedora example):
```
sudo dnf install -y podman podman-compose
```

Verify:
```
uv --version
podman --version
podman-compose --version
```

## Quick start (all services)
Run each service in its own terminal.

1) LLM server (OpenAI-compatible API)
2) MCP server (tools)
3) Open WebUI (frontend)

---

## LLM server setup (llm-server)
Provides an OpenAI-compatible `/v1/chat/completions` endpoint backed by Mistral.

### Install dependencies
```
cd llm-server
uv sync
```

### Configure
Set the Mistral API key:
```
export MISTRAL_API_KEY=your_key_here
```

### Run
```
uvicorn main:app --host 0.0.0.0 --port 8000
```

Health check:
```
curl http://localhost:8000/v1/models
```

---

## MCP server setup (mcp-server)
Exposes tools for weather, time, Wikipedia, and web scraping.

### Install dependencies
```
cd mcp-server
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

### Playwright browsers (required for robust scraping)
```
playwright install
```

### Configure
Edit defaults in [mcp-server/src/config.py](mcp-server/src/config.py) if needed (for example, `weather_api_key`).

### Run
```
python main.py
```

The server listens on `0.0.0.0:8765` by default.

---

## Open WebUI setup (openwebui)
Runs the UI with Podman + podman-compose. All configuration is file-based.

### Features
- Custom branding (logo, name, footer)
- File uploads
- OpenAI‑compatible backend
- Easy start/stop/reset

### Project structure
```
openwebui/
├── podman-compose.yml
├── .env
├── data/      # Persistent WebUI data (DB, users, chats)
└── assets/    # Branding assets
		├── logo.png
		└── favicon.png
```

### Configuration
Create or update [openwebui/.env](openwebui/.env) in the [openwebui](openwebui/) directory:
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

Do not commit secrets. Add [openwebui/.env](openwebui/.env) to [.gitignore](.gitignore) if needed.

### Podman Compose
[openwebui/podman-compose.yml](openwebui/podman-compose.yml):
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

### Run
Start (background):
```
cd openwebui
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

### Logs
```
podman logs -f open-webui
```

### Basic Podman commands
```
podman ps
podman stop open-webui
podman rm open-webui
```

### Reset
Stop and remove container (keep data):
```
podman-compose down
```

Full reset (deletes data):
```
podman-compose down
rm -rf data/
```

### Update
```
podman-compose pull
podman-compose up -d --force-recreate
```

### Notes (SELinux on Fedora)
Volumes use `:Z` for SELinux compatibility. If you see permission errors, fix volume labels instead of disabling SELinux.

---

## Optional references
- Original container-only notes: [openwebui/README.md](openwebui/README.md)
