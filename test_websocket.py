#!/usr/bin/env python3
"""
Simple WebSocket test script to verify doctor status updates
"""
import asyncio
import websockets
import json
import time

async def test_websocket():
    """Test WebSocket connection and doctor status updates"""
    uri = "ws://127.0.0.1:8000/ws/doctor-status/"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send a ping message
            ping_message = {
                "type": "ping"
            }
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent ping message")
            
            # Wait for response
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            # Send another ping after 5 seconds
            await asyncio.sleep(5)
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent second ping message")
            
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ WebSocket connection refused. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing WebSocket connection...")
    asyncio.run(test_websocket()) 