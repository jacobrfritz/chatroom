import asyncio
import logging
import json
from websockets.asyncio.server import serve
from websockets.asyncio.server import ServerConnection
from typing import Protocol
from dataclasses import dataclass, asdict
import uuid

logging.basicConfig(level=logging.INFO)


@dataclass
class Message:
    message_type: str | None
    value: str | None


@dataclass
class User:
    username: str
    user_id: uuid.UUID
    conn: ServerConnection


class MessageFormatter(Protocol):
    def format(self, message: Message) -> str: ...


class RoomContext(Protocol):
    def add_user(self, username: str, conn: ServerConnection): ...

    def get_username(self, conn: ServerConnection) -> str: ...

    async def send_all_clients(self, message: Message): ...

    async def send_single_client(self, message: Message, conn: ServerConnection): ...


class MessageHandler(Protocol):
    keyword: str

    async def handle(
        self, context: RoomContext, conn: ServerConnection, value: str
    ): ...


class JsonFormatter(MessageFormatter):
    def format(self, message: Message):
        return json.dumps(asdict(message))


class BroadcastMessageHandler(MessageHandler):
    keyword = "MESSAGE"

    async def handle(self, context: RoomContext, conn: ServerConnection, value: str):
        username = context.get_username(conn)
        msg = Message(message_type="MESSAGE", value=f"{username}: {value}")
        await context.send_all_clients(msg)
        context.recent_messages.append(msg)
        context.recent_messages = context.recent_messages[-20:]


class IdentityMessageHandler(MessageHandler):
    keyword = "SET_IDENTITY"

    async def handle(self, context: RoomContext, conn: ServerConnection, value: str):
        username = value
        if username and username.strip() != "":
            context.add_user(username, conn)
            logging.info(f"User {username} identified")
            message = Message(message_type="CONNECTED", value=f"{username} Connected!")
            await context.send_all_clients(message)
        else:
            message = Message(message_type="INVALID_USERNAME", value="Invalid Username")
            await context.send_single_client(message, conn)


class Chatroom(RoomContext):
    def __init__(
        self, formatter: MessageFormatter, message_handlers: list[MessageHandler]
    ):
        self.formatter = formatter
        self.message_handlers = message_handlers
        self.connections:list[User] = list()
        self.recent_messages:list[Message] = list()

    async def send_single_client(self, message: Message, client: ServerConnection):
        formatted_message = self.formatter.format(message)
        await client.send(formatted_message)

    async def send_all_clients(self, message: Message):
        if self.connections:
            await asyncio.gather(
                *(
                    self.send_single_client(message, user.conn)
                    for user in self.connections
                )
            )

    async def send_recent_messages(self, websocket: ServerConnection):
        if self.recent_messages:
            await asyncio.gather(
                *(
                    self.send_single_client(message, websocket)
                    for message in self.recent_messages
                )
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
            user = next(
                (u for u in self.connections if u.conn == websocket), None
            )
            if user:
                msg = f"{user.username} disconnected"
                logging.info(msg)
                out = Message("CONNECTED", msg)
                await self.send_all_clients(out)
            else:
                logging.info("Unidentified user disconnected")

    async def start(self):
        async with serve(self.handler, "0.0.0.0", 8765):
            await asyncio.Future()  # run forever


if __name__ == "__main__":
    formatter = JsonFormatter()
    message_handlers = [IdentityMessageHandler(), BroadcastMessageHandler()]
    chatroom = Chatroom(formatter, message_handlers)
    asyncio.run(chatroom.start())
