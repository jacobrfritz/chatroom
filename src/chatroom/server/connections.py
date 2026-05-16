import logging
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed
import asyncio

from chatroom.server.interfaces import ConnectionHandler, RoomContext


class WebsocketConnectionHandler(ConnectionHandler):
    async def send_single_client(self, message: str, websocket: ServerConnection):
        try:
            await websocket.send(message)
        except ConnectionClosed:
            logging.debug("Attempted to send to a closed connection")

    async def send_all_clients(self, context: RoomContext, message: str):
        if context.connections:
            await asyncio.gather(
                *(
                    self.send_single_client(message, user.conn)
                    for user in context.connections
                ),
                return_exceptions=True,
            )

    async def send_recent_messages(
        self, context: RoomContext, websocket: ServerConnection
    ):
        if context.recent_messages:
            await asyncio.gather(
                *(
                    self.send_single_client(message, websocket)
                    for message in context.recent_messages
                ),
                return_exceptions=True,
            )
