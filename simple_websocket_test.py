#!/usr/bin/env python3
"""
Simple test to verify WebSocket routing is working
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import TestCase
from channels.testing import WebsocketCommunicator
from myproject.asgi import application

class WebSocketTest(TestCase):
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        communicator = WebsocketCommunicator(
            application=application,
            path="/ws/doctor-status/"
        )
        
        connected, _ = await communicator.connect()
        
        if connected:
            print("✅ WebSocket connection successful!")
            
            # Send a test message
            await communicator.send_json_to({
                "type": "ping"
            })
            
            # Wait for response
            response = await communicator.receive_json_from()
            print(f"📥 Received response: {response}")
            
            await communicator.disconnect()
        else:
            print("❌ WebSocket connection failed!")

if __name__ == "__main__":
    import asyncio
    
    async def run_test():
        test = WebSocketTest()
        await test.test_websocket_connection()
    
    asyncio.run(run_test()) 