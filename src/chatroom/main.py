import asyncio

from chatroom.server.server import (
    Chatroom,
    JsonFormatter,
    IdentityMessageHandler,
    BroadcastMessageHandler,
)


def run() -> None:
    """Core application logic."""
    formatter = JsonFormatter()
    message_handlers = [IdentityMessageHandler(), BroadcastMessageHandler()]
    chatroom = Chatroom(formatter, message_handlers)
    asyncio.run(chatroom.start())
