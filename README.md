# Chatroom

A lightweight, real-time chat application built with a Python WebSocket backend and a minimalist web frontend.

## 🚀 Features

- **Real-time Messaging:** Instant message delivery using WebSockets.
- **Persistent Session State:** New users receive the 20 most recent messages upon joining.
- **Identity Management:** Simple prompt-based username selection.
- **Containerized Deployment:** Dockerized setup for easy scaling and deployment.
- **Developer-First Tooling:** Powered by `uv` for fast dependency management and a comprehensive `Makefile`.

## 🏗️ Repository Structure

```text
chatroom/
├── src/chatroom/           # Main source code
│   ├── client/             # Frontend assets
│   │   ├── static/         # JavaScript (Websocket logic)
│   │   ├── templates/      # CSS styling
│   │   └── index.html      # Main entry point for the browser
│   ├── server/             # Backend server
│   │   └── server.py       # WebSocket handler logic
│   ├── cli.py              # Command-line interface entry point
│   └── main.py             # Application bootstrap
├── tests/                  # Test suite (Pytest)
├── Dockerfile              # Container definition
├── docker-entrypoint.sh    # Dual-server startup script (Frontend + Backend)
├── Makefile                # Automation for common dev tasks
├── pyproject.toml          # Project configuration and dependencies
└── uv.lock                 # Deterministic dependency lockfile
```

## 🛠️ Tech Stack

- **Backend:** Python 3.12, `websockets`.
- **Frontend:** Vanilla JavaScript, HTML5, CSS3.
- **Package Management:** [uv](https://github.com/astral-sh/uv).
- **Environment:** Docker.

## 🏃 Local Development

### Prerequisites

- [uv](https://github.com/astral-sh/uv) installed on your system.
- Python 3.12+.

### Setup

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Run the backend:**
   ```bash
   make run
   ```

3. **Run the frontend:**
   Navigate to `src/chatroom/client` and serve it with your preferred HTTP server. For example:
   ```bash
   cd src/chatroom/client
   python -m http.server 8080
   ```
   
   **Note:** The application now uses dynamic WebSocket routing and expects a reverse proxy (like Nginx or Caddy) to route requests to `/chat-ws/` to the backend on port 8765. For direct local access without a proxy, you may need to adjust the connection URL in `chatroom.mjs`.

## 🐳 Docker

To run the application in a production-like environment with a reverse proxy:

1. **Build the image:**
   ```bash
   docker build -t chatroom .
   ```

   **Push the Image to dockerhub**
   ```bash
   docker buildx build --platform linux/amd64,linux/arm64 -t hateyoujake/chatroom-app:latest --push .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8080:8080 -p 8765:8765 chatroom
   ```
   
   **Architecture Note:** This container starts both the frontend (8080) and backend (8765). Ensure your deployment environment (e.g., Docker Compose with Nginx) is configured to:
   - Serve static files from port 8080.
   - Proxy WebSocket traffic at `/chat-ws/` to port 8765.

## 🔌 API & Protocols

### WebSocket (Dynamic Path: `/chat-ws/`)

The client automatically detects the protocol (`ws://` or `wss://`) based on the page's connection.

- **Endpoint:** `${window.location.host}/chat-ws/`
- **Incoming Messages (JSON):**
  - `{"type": "SET_IDENTITY", "username": "string"}`: Sets the user's display name.
  - `{"type": "MESSAGE", "message": "string"}`: Sends a message to the room.
- **Outgoing Messages (String):**
  - Broadcasts formatted strings: `"{username} connected."` or `"{username} said: {message}"`.
