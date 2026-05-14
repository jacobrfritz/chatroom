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
        return asyncio.create_task(client.send(formatted_message))

    async def send_all_clients(self, message: Message):
        if self.connections:
            tasks = [
                asyncio.create_task(self.send_single_client(message, client))
                for client in self.connections.values()
            ]
            if tasks:
                await asyncio.wait(tasks)

    async def send_recent_messages(self, websocket: ServerConnection):
        if len(self.recent_messages) != 0:
            tasks = [
                asyncio.create_task(self.send_single_client(message, websocket))
                for message in self.recent_messages
            ]
            if tasks:
                await asyncio.wait(tasks)

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
        out = None
        try:
            await self.send_recent_messages(websocket)
            async for message in websocket:
                message_type, message_value = self.parse_message(message)
                if message_type and message_value:
                    if message_type == "SET_IDENTITY":
                        username = self.validate_identity(message_value, websocket)
                        if username:
                            message = Message(
                                username=username, type="CONNECTED", value=message_value
                            )
                            await self.send_all_clients(message)
                        else:
                            message = Message(
                                username=username, type="invalid_user", value=None
                            )
                            await self.send_single_client(message, websocket)
                            continue
                    elif message_type == "MESSAGE":
                        message = Message(
                            username=username, type=message_type, value=message_value
                        )
                        await self.send_all_clients(message)
                    else:
                        message = Message(username="", type="ERROR", value="")
                        await self.send_all_clients(message)
                        logging.warning(f"Message Type Not Recognized {out}")

        finally:
            # Unregister when the client disconnects
            del self.connections[username]

    async def start(self):
        async with serve(self.handler, "0.0.0.0", 8765):
            await asyncio.Future()  # run forever


if __name__ == "__main__":
    formatter = JsonFormatter()
    chatroom = Chatroom(formatter)
    asyncio.run(chatroom.start())
