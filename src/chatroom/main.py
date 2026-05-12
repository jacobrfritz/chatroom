import asyncio

from chatroom.server.server import start


def run() -> None:
    """Core application logic."""
    asyncio.run(start())
