from typing import Protocol
import json
from dataclasses import asdict
import logging

from websockets.asyncio.server import ServerConnection
from better_profanity import profanity

profanity.load_censor_words()

from chatroom.server.interfaces import (
    Message,
    MessageHandler,
    MessageFormatter,
    RoomContext,
)


class JsonFormatter(MessageFormatter):
    def format(self, message: Message):
        return json.dumps(asdict(message))


class BroadcastMessageHandler(MessageHandler):
    keyword = "MESSAGE"

    async def handle(self, context: RoomContext, conn: ServerConnection, value: str):
        username = context.get_username(conn)
        masked_value = profanity.censor(value)
        msg = Message(message_type="MESSAGE", value=f"{username}: {masked_value}")
        formatted_message = context.formatter.format(msg)
        await context.send_all_clients(msg)
        context.recent_messages.append(formatted_message)
        context.recent_messages = context.recent_messages[-20:]


class IdentityMessageHandler(MessageHandler):
    keyword = "SET_IDENTITY"

    async def handle(self, context: RoomContext, conn: ServerConnection, value: str):
        username = value
        if not username or username.strip() == "":
            message = Message(message_type="INVALID_USERNAME", value="Invalid Username")
            await context.send_single_client(message, conn)
            return

        if profanity.contains_profanity(username):
            message = Message(
                message_type="INVALID_USERNAME", value="Username contains profanity"
            )
            await context.send_single_client(message, conn)
            return

        context.add_user(username, conn)
        logging.info(f"User {username} identified")
        message = Message(message_type="CONNECTED", value=f"{username} Connected!")
        await context.send_all_clients(message)
