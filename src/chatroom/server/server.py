import asyncio
import logging
import json
from websockets.asyncio.server import serve

logging.basicConfig(level=logging.INFO)


# Maintain a set of all connected clients
CONNECTIONS = dict()

RECENT_MESSAGES = list()

async def send_all_clients(message):
    global CONNECTIONS
    # When a message is received, broadcast it to EVERYONE
    # including the sender (or exclude them if you prefer)
    if CONNECTIONS:
        tasks = [asyncio.create_task(client.send(message)) for client in CONNECTIONS.values()]
        
        if tasks:
            await asyncio.wait(tasks)
        
async def send_recent_messages(websocket):
    if len(RECENT_MESSAGES) != 0:
            tasks = [asyncio.create_task(websocket.send(message)) for message in RECENT_MESSAGES]
                
            if tasks:
                await asyncio.wait(tasks)    
            
async def handler(websocket):   
    global RECENT_MESSAGES 
    global CONNECTIONS
    username = None
    out = None
    
    try:
        await send_recent_messages(websocket)

        async for message in websocket:
            message = json.loads(message)
            message_type = message.get("type")
            if message_type == "SET_IDENTITY":
                username = message.get("username")
                print(username)
                if username and username.strip() != "":
                    CONNECTIONS[username] = websocket
                    out = f"{username} connected."
                    await send_all_clients(out)
                else:
                    continue
            elif message_type == "MESSAGE":
                out = f"{username} said: {message.get("message")}"
                await send_all_clients(out)
            else:
                logging.warning("Message Type Not Recognized")
            
            if out:
                RECENT_MESSAGES.append(out)
                RECENT_MESSAGES = RECENT_MESSAGES[:20]
            
    finally:
        # Unregister when the client disconnects
       del CONNECTIONS[username]

async def start():
    async with serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(start())