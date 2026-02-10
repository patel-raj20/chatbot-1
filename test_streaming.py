"""
Test Streaming RAG Endpoint
============================
Simple script to test the complete streaming flow:
1. Send question via HTTP
2. Connect to WebSocket
3. Receive streaming tokens
4. Display complete answer

Usage:
    python test_streaming.py
"""

import requests
import asyncio
import websockets
import json
import sys


async def test_streaming(question="Who is B S Mehta?"):
    """Test the streaming RAG endpoint."""
    
    print(f"\n{'='*60}")
    print(f"Testing Streaming RAG")
    print(f"{'='*60}\n")
    
    # Step 1: Send question via HTTP
    print(f"📤 Sending question: {question}")
    
    response = requests.post('http://localhost:8000/rag/ask-stream', json={
        "question": question,
        "user_id": "test-user",
        "session_id": "test-session"
    })
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return
    
    data = response.json()
    request_id = data['request_id']
    websocket_url = data['websocket_url']
    
    print(f"✓ Request queued successfully")
    print(f"  Request ID: {request_id}")
    print(f"  WebSocket URL: {websocket_url}\n")
    
    # Step 2: Connect to WebSocket
    print(f"🔌 Connecting to WebSocket...\n")
    
    ws_uri = f"ws://localhost:8000{websocket_url}"
    
    try:
        async with websockets.connect(ws_uri) as websocket:
            print(f"✓ WebSocket connected!")
            print(f"\n{'='*60}")
            print(f"📝 Streaming Answer:")
            print(f"{'='*60}\n")
            
            full_answer = ""
            token_count = 0
            
            # Step 3: Receive streaming tokens
            while True:
                try:
                    message = await websocket.recv()
                    msg_data = json.loads(message)
                    
                    if msg_data['type'] == 'token':
                        token = msg_data['content']
                        print(token, end='', flush=True)
                        full_answer += token
                        token_count += 1
                        
                    elif msg_data['type'] == 'done':
                        print(f"\n\n{'='*60}")
                        print(f"✓ Stream completed!")
                        print(f"  Total tokens received: {token_count}")
                        print(f"{'='*60}\n")
                        break
                        
                    elif msg_data['type'] == 'error':
                        print(f"\n\n❌ Error: {msg_data['message']}\n")
                        break
                        
                except websockets.exceptions.ConnectionClosed:
                    print("\n\n⚠️  WebSocket connection closed\n")
                    break
                except Exception as e:
                    print(f"\n\n❌ Error receiving message: {e}\n")
                    break
            
            # Step 4: Display summary
            if full_answer:
                print(f"\n{'='*60}")
                print(f"Complete Answer:")
                print(f"{'='*60}")
                print(full_answer)
                print(f"{'='*60}\n")
    
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}\n")
        print(f"   Make sure the backend and worker are running!")
        print(f"   Run: docker-compose up -d\n")


if __name__ == "__main__":
    # Get question from command line or use default
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Who is B S Mehta?"
    
    # Run the async test
    asyncio.run(test_streaming(question))
