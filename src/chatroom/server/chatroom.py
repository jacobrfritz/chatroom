import logging
from websockets.asyncio.server import serve
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed
import uuid
import asyncio
import json

from chatroom.server.interfaces import (
    Message,
    User,
    MessageFormatter,
    MessageHandler,
    RoomContext,
)


class Chatroom(RoomContext):
    def __init__(
        self, formatter: MessageFormatter, message_handlers: list[MessageHandler]
    ):
        self.formatter = formatter
        self.message_handlers = message_handlers
        self.connections: list[User] = list()
        self.recent_messages: list[Message] = list()

    async def send_single_client(self, message: Message, client: ServerConnection):
        try:
            formatted_message = self.formatter.format(message)
            await client.send(formatted_message)
        except ConnectionClosed:
            logging.debug("Attempted to send to a closed connection")

    async def send_all_clients(self, message: Message):
        if self.connections:
            await asyncio.gather(
                *(
                    self.send_single_client(message, user.conn)
                    for user in self.connections
                ),
                return_exceptions=True,
            )

    async def send_recent_messages(self, websocket: ServerConnection):
        if self.recent_messages:
            await asyncio.gather(
                *(
                    self.send_single_client(message, websocket)
                    for message in self.recent_messages
                ),
                return_exceptions=True,
            )

    def add_user(self, username: str, conn: ServerConnection):
        user_id = uuid.uuid4()
        new_user = User(username=username, conn=conn, user_id=user_id)
        self.connections.append(new_user)

    def get_username(self, conn: ServerConnection) -> str:
        for user in self.connections:
            if user.conn == conn:
                return user.username
        return "Anonymous"

    def parse_message(self, message: str) -> tuple[str | None, str | None]:
        try:
            msg = json.loads(message)
            if isinstance(msg, dict):
                message_type = msg.get("type")
                message_value = msg.get("message")
                if message_type and message_value:
                    return (message_type, message_value)
        except Exception as e:
            logging.error(f"Error parsing message: {e}")
        return (None, None)

    async def handler(self, websocket):
        logging.info("New connection established")
        try:
            await self.send_recent_messages(websocket)
            async for raw_message in websocket:
                logging.info(f"Received raw message: {raw_message}")
                message_type, message_value = self.parse_message(raw_message)
                if message_type and message_value:
                    for message_handler in self.message_handlers:
                        if message_handler.keyword == message_type.upper():
                            await message_handler.handle(self, websocket, message_value)
                            break
                    else:
                        logging.error(
                            f"Don't recognize message type. Message Type: {message_type} Message Value: {message_value}"
                        )

                        msg = Message(
                            message_type="ERROR",
                            value=f"Unknown message type: {message_type}",
                        )
                        await self.send_single_client(msg, websocket)
                else:
                    logging.warning(f"Invalid message format: {raw_message}")
        except Exception as e:
            logging.error(f"Error in handler: {e}")
        finally:
            # Unregister when the client disconnects
            user = next((u for u in self.connections if u.conn == websocket), None)
            if user:
                self.connections.remove(user)
                msg = f"{user.username} disconnected"
                logging.info(msg)
                out = Message("CONNECTED", msg)
                await self.send_all_clients(out)
            else:
                logging.info("Unidentified user disconnected")

    async def start(self):
        async with serve(self.handler, "0.0.0.0", 8765):
            await asyncio.Future()  # run forever
