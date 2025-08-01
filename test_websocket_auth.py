#!/usr/bin/env python3
"""
Test WebSocket authentication with JWT token
"""
import asyncio
import json
import time
try:
    import websockets
except ImportError:
    print("websockets library not found. Installing...")
    import subprocess
    subprocess.check_call(["pip", "install", "websockets"])
    import websockets

async def test_websocket_auth():
    """Test WebSocket connection with authentication"""
    uri = "ws://127.0.0.1:8000/ws/doctor-status/"
    
    # This is a sample JWT token - you'll need to replace with a real one
    # You can get this from the browser's localStorage or from a login response
    sample_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzOTk4NzAxLCJpYXQiOjE3NTM5OTUxMDEsImp0aSI6Ijg1YjUwNmQxYzBjMjRhNzhiMDUyNDgyMjM1YTI2NmQzIiwidXNlcl9pZCI6IlVTUjAwMSJ9.7OppHG1zp0mN2hDRe5EuJPspltRN-iXT0IntAT6iv8A"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send authentication message
            auth_message = {
                "type": "auth",
                "token": sample_token
            }
            await websocket.send(json.dumps(auth_message))
            print("📤 Sent authentication message")
            
            # Wait for authentication response
            response = await websocket.recv()
            print(f"📥 Received: {response}")
            
            # Parse the response
            response_data = json.loads(response)
            if response_data.get('type') == 'auth_success':
                print("✅ Authentication successful!")
                
                # Send a ping message
                ping_message = {
                    "type": "ping"
                }
                await websocket.send(json.dumps(ping_message))
                print("📤 Sent ping message")
                
                # Wait for pong response
                pong_response = await websocket.recv()
                print(f"📥 Received: {pong_response}")
                
            else:
                print(f"❌ Authentication failed: {response_data.get('message', 'Unknown error')}")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ WebSocket connection refused. Make sure the server is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Testing WebSocket authentication...")
    asyncio.run(test_websocket_auth()) 