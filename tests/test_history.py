import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from chatroom.server.chatroom import Chatroom
from chatroom.server.interfaces import Message

def test_send_all_clients_updates_history():
    async def run_test():
        # Setup mocks
        formatter = MagicMock()
        formatter.format.side_effect = lambda m: f"formatted_{m.value}"
        
        connection_handler = AsyncMock()
        
        chatroom = Chatroom(
            formatter=formatter,
            message_handlers=[],
            connection_handler=connection_handler
        )
        
        # Test MESSAGE
        msg1 = Message(message_type="MESSAGE", value="User: Hello")
        await chatroom.send_all_clients(msg1)
        
        assert len(chatroom.recent_messages) == 1
        assert chatroom.recent_messages[0] == "formatted_User: Hello"
        
        # Test CONNECTED
        msg2 = Message(message_type="CONNECTED", value="User Connected!")
        await chatroom.send_all_clients(msg2)
        
        assert len(chatroom.recent_messages) == 2
        assert chatroom.recent_messages[1] == "formatted_User Connected!"
        
        # Test history limit (20)
        for i in range(25):
            msg = Message(message_type="MESSAGE", value=f"msg_{i}")
            await chatroom.send_all_clients(msg)
            
        assert len(chatroom.recent_messages) == 20
        assert chatroom.recent_messages[-1] == "formatted_msg_24"

    asyncio.run(run_test())
