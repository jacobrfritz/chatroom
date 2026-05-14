import asyncio

from chatroom.server.server import Chatroom, JsonFormatter


def run() -> None:
    """Core application logic."""
    jsonFormatter = JsonFormatter()
    chatroom = Chatroom(jsonFormatter)
    asyncio.run(chatroom.start())
