import asyncio

from chatroom.server.server import (
    Chatroom
)
from chatroom.server.message import JsonFormatter, IdentityMessageHandler,BroadcastMessageHandler
from chatroom.server.connections import WebsocketConnectionHandler

def run() -> None:
    """Core application logic."""
    formatter = JsonFormatter()
    message_handlers = [IdentityMessageHandler(), BroadcastMessageHandler()]
    connection_handler = WebsocketConnectionHandler()
    chatroom = Chatroom(formatter, message_handlers, connection_handler)
    asyncio.run(chatroom.start())
