import asyncio
import logging

from chatroom.server.message import (
    IdentityMessageHandler,
    BroadcastMessageHandler,
    JsonFormatter,
)
from chatroom.server.chatroom import Chatroom


logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    formatter = JsonFormatter()
    message_handlers = [IdentityMessageHandler(), BroadcastMessageHandler()]
    chatroom = Chatroom(formatter, message_handlers)
    asyncio.run(chatroom.start())
