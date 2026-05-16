import asyncio
import logging

from chatroom.server.message import (
    IdentityMessageHandler,
    BroadcastMessageHandler,
    JsonFormatter,
)
from chatroom.server.chatroom import Chatroom
from chatroom.server.connections import WebsocketConnectionHandler


logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    formatter = JsonFormatter()
    message_handlers = [IdentityMessageHandler(), BroadcastMessageHandler()]
    connection_handler = WebsocketConnectionHandler()
    chatroom = Chatroom(formatter, message_handlers, connection_handler)
    asyncio.run(chatroom.start())
