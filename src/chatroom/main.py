import asyncio

from chatroom.server.server import  Chatroom


def run() -> None:
    """Core application logic."""
    chatroom = Chatroom()
    asyncio.run(chatroom.start())
