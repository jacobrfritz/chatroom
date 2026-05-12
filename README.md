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
   Then open `http://localhost:8080` in your browser.

### Development Tasks

- **Run tests:** `make test`
- **Linting:** `make lint`
- **Formatting:** `make format`
- **Type Checking:** `make typecheck`

## 🐳 Docker

To run the entire application (frontend and backend) in a container:

1. **Build the image:**
   ```bash
   docker build -t chatroom .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8080:8080 -p 8765:8765 chatroom
   ```
   Access the app at `http://localhost:8080`.

## 🔌 API & Protocols

### WebSocket (Port 8765)

- **Incoming Messages (JSON):**
  - `{"type": "SET_IDENTITY", "username": "string"}`: Sets the user's display name.
  - `{"type": "MESSAGE", "message": "string"}`: Sends a message to the room.
- **Outgoing Messages (String):**
  - Broadcasts formatted strings: `"{username} connected."` or `"{username} said: {message}"`.
