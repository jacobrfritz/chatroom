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
    type:str
    value:str
    
    
class MessageFormatter(Protocol):
    def format(self, message:Message)->str: ...
    

class JsonFormatter(MessageFormatter):
    def format(self, message:Message):
        return json.dumps(asdict(message))
    
    
class Chatroom:
    def __init__(self):
        self.connections = dict()
        self.recent_messages = list()
        
        
    async def send_all_clients(self, message:str):
        if self.connections:
            tasks = [asyncio.create_task(client.send(message)) for client in self.connections.values()]
            
            if tasks:
                await asyncio.wait(tasks)
            
            
    async def send_recent_messages(self, websocket:ServerConnection):
        if len(self.recent_messages) != 0:
                tasks = [asyncio.create_task(websocket.send(message)) for message in self.recent_messages]
                    
                if tasks:
                    await asyncio.wait(tasks)    
    
    
    def validate_identity(self, message:dict, websocket:ServerConnection)->str|None:
        username = message.get("username")
        if username and username.strip() != "":
            self.connections[username] = websocket
            return username
        else:
            return None
    
                
    async def handler(self, websocket):   
        out = None
        try:
            await self.send_recent_messages(websocket)
            async for message in websocket:
                message = json.loads(message)
                message_type = message.get("type")
                if message_type == "SET_IDENTITY":
                    username = self.validate_identity(message,websocket)
                    if username and username not in self.connections.keys():
                        out = f"{username} connected."
                        await self.send_all_clients(out)
                    else:
                        #await websocket.send("invalid username")
                        continue
                elif message_type == "MESSAGE":
                    out = f"{username} said: {message.get("message")}"
                    await self.send_all_clients(out)
                else:
                    logging.warning("Message Type Not Recognized")
                
                if out:
                    self.recent_messages.append(out)
                    self.recent_messages = self.recent_messages[-20:]
        finally:
            # Unregister when the client disconnects
            del self.connections[username]

    async def start(self):
        async with serve(self.handler, "0.0.0.0", 8765):
            await asyncio.Future()  # run forever

if __name__ == "__main__":
    chatroom = Chatroom()
    asyncio.run(chatroom.start())