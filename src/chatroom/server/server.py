import asyncio
import logging
import json
from websockets.asyncio.server import serve
from websockets.asyncio.server import ServerConnection
from typing import Protocol
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)


@dataclass
class Message:
    type: str | None
    username: str | None
    value: str | None


class MessageFormatter(Protocol):
    def format(self, message: Message) -> str: ...


class JsonFormatter(MessageFormatter):
    def format(self, message: Message):
        return json.dumps(asdict(message))


class Chatroom:
    def __init__(self, formatter: MessageFormatter):
        self.formatter = formatter
        self.connections = dict()
        self.recent_messages = list()

    async def send_single_client(self, message: Message, client: ServerConnection):
        formatted_message = self.formatter.format(message)
        if message.type in ["MESSAGE", "CONNECTED"]:
            self.recent_messages.append(message)
            self.recent_messages = self.recent_messages[-20:]
        await client.send(formatted_message)

    async def send_all_clients(self, message: Message):
        if self.connections:
            await asyncio.gather(
                *(self.send_single_client(message, client) for client in self.connections.values())
            )

    async def send_recent_messages(self, websocket: ServerConnection):
        if self.recent_messages:
            await asyncio.gather(
                *(self.send_single_client(message, websocket) for message in self.recent_messages)
            )

    def validate_identity(
        self, username: str, websocket: ServerConnection
    ) -> str | None:
        if (
            username
            and username.strip() != ""
            and username not in self.connections.keys()
        ):
            self.connections[username] = websocket
            return username
        else:
            return None

    def parse_message(self, message: str) -> tuple[str | None, str | None]:
        msg = json.loads(message)
        if isinstance(msg, dict):
            message_type = msg.get("type")
            message_value = msg.get("message")
            if message_type and message_value:
                return (message_type, message_value)
        return (None, None)

    async def handler(self, websocket):
        username = None
        try:
            await self.send_recent_messages(websocket)
            async for raw_message in websocket:
                message_type, message_value = self.parse_message(raw_message)
                if message_type and message_value:
                    if message_type == "SET_IDENTITY":
                        valid_username = self.validate_identity(message_value, websocket)
                        if valid_username:
                            username = valid_username
                            msg = Message(
                                username=username, 
                                type="CONNECTED", 
                                value=message_value
                            )
                            await self.send_all_clients(msg)
                        else:
                            msg = Message(
                                username=None, 
                                type="invalid_user", 
                                value=None
                            )
                            await self.send_single_client(msg, websocket)
                            continue
                    elif message_type == "MESSAGE":
                        msg = Message(
                            username=username, 
                            type=message_type, 
                            value=message_value
                        )
                        await self.send_all_clients(msg)
                    else:
                        msg = Message(username="", type="ERROR", value="")
                        await self.send_all_clients(msg)
                        logging.warning(f"Message Type Not Recognized: {message_type}")
        except Exception as e:
            logging.error(f"Error in handler: {e}")
        finally:
            # Unregister when the client disconnects
            if username and username in self.connections:
                del self.connections[username]
                logging.info(f"User {username} disconnected")

    async def start(self):
        async with serve(self.handler, "0.0.0.0", 8765):
            await asyncio.Future()  # run forever


if __name__ == "__main__":
    formatter = JsonFormatter()
    chatroom = Chatroom(formatter)
    asyncio.run(chatroom.start())
