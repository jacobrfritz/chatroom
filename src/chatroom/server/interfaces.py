from typing import Protocol
from dataclasses import dataclass
from websockets.asyncio.server import ServerConnection
import uuid


@dataclass
class User:
    username: str
    user_id: uuid.UUID
    conn: ServerConnection
    
@dataclass
class Message:
    message_type: str | None
    value: str | None

class RoomContext(Protocol):
    recent_messages: list[Message] 
    def add_user(self, username: str, conn: ServerConnection): ...
    def get_username(self, conn: ServerConnection) -> str: ...
    async def send_all_clients(self, message: Message): ...
    async def send_single_client(self, message: Message, conn: ServerConnection): ...
    
class MessageFormatter(Protocol): 
    def format(self, message: Message) -> str: ...
 
class MessageHandler(Protocol):
    keyword: str
    async def handle(
        self, context: RoomContext, conn: ServerConnection, value: str
    ): ...



