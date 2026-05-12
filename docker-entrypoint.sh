#!/bin/sh
set -e

# Start the frontend HTTP server in the background
echo "Starting frontend server on port 8080..."
cd src/chatroom/client 
exec python3 -m http.server 8080 &

# Start the backend WebSocket server in the foreground
echo "Starting backend WebSocket server..."
cd /app 
exec uv run chatroom
