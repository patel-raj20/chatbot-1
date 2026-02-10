"""
WebSocket Routes
================
WebSocket endpoint for real-time streaming responses.

ENDPOINTS:
    WS /ws/chat/{request_id} - Stream RAG response tokens to client

ARCHITECTURE:
    Client WebSocket ← FastAPI WS Endpoint ← Redis Pub/Sub ← Worker
    
RESPONSIBILITIES:
    - Accept WebSocket connections from clients
    - Subscribe to Redis Pub/Sub channel for request_id
    - Forward tokens to client in real-time
    - Close connection when done
    
WHAT THIS DOES NOT DO:
    - Does NOT perform RAG (worker's job)
    - Does NOT talk to RabbitMQ (worker's job)
    - Does NOT cache answers (as per requirements)
    
FLOW:
    1. Client connects with request_id
    2. Server subscribes to Redis Pub/Sub for that request_id
    3. Worker publishes tokens → Redis Pub/Sub → This endpoint → Client
    4. When "done" received, close connection

USAGE:
    // JavaScript client example
    const ws = new WebSocket(`ws://localhost:8000/ws/chat/${requestId}`);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'token') {
            console.log(data.content);
        } else if (data.type === 'done') {
            ws.close();
        }
    };
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.queue.pubsub_service import RedisPubSubService
from app.core.logger import get_logger
import json

logger = get_logger(__name__)
router = APIRouter(tags=["websocket"])


@router.websocket("/ws/chat/{request_id}")
async def websocket_chat_stream(websocket: WebSocket, request_id: str):
    """
    WebSocket endpoint for streaming chat responses.
    
    WHY: Real-time streaming provides better UX than polling
    WHERE: Client connects after receiving request_id from HTTP endpoint
    HOW:
        1. Accept WebSocket connection
        2. Subscribe to Redis Pub/Sub channel
        3. Forward each token to client
        4. Close when done/error
    
    Args:
        websocket: WebSocket connection object
        request_id: Unique identifier for this request
        
    Message Format (sent to client):
        {"type": "token", "content": "Hello"}
        {"type": "done"}
        {"type": "error", "message": "Error details"}
    
    Example Client Code:
        ```javascript
        const ws = new WebSocket(`ws://localhost:8000/ws/chat/${requestId}`);
        
        ws.onopen = () => console.log('Connected');
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'token') {
                displayToken(data.content);
            } else if (data.type === 'done') {
                console.log('Stream complete');
                ws.close();
            } else if (data.type === 'error') {
                console.error(data.message);
                ws.close();
            }
        };
        
        ws.onerror = (error) => console.error('WebSocket error:', error);
        ws.onclose = () => console.log('Connection closed');
        ```
    """
    # STEP 1: Accept WebSocket connection
    await websocket.accept()
    logger.info(f"✓ WebSocket connected for request: {request_id}")
    
    # Initialize Pub/Sub service
    pubsub = RedisPubSubService()
    
    try:
        # STEP 2: Connect to Redis Pub/Sub
        await pubsub.connect()
        
        # STEP 3: Subscribe to token stream
        logger.info(f"🔄 Subscribing to stream: {request_id}")
        
        async for message in pubsub.subscribe_stream(request_id):
            # STEP 4: Forward message to client
            try:
                await websocket.send_json(message)
                
                # Log token type (but not content to reduce noise)
                msg_type = message.get("type")
                if msg_type == "done":
                    logger.info(f"✓ Stream completed for request: {request_id}")
                    break
                elif msg_type == "error":
                    logger.error(f"Stream error for request {request_id}: {message.get('message')}")
                    break
                    
            except WebSocketDisconnect:
                logger.info(f"Client disconnected: {request_id}")
                break
            except Exception as send_error:
                logger.error(f"Failed to send message: {send_error}")
                break
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {request_id}")
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            # Try to send error to client
            await websocket.send_json({
                "type": "error",
                "message": f"Server error: {str(e)}"
            })
        except:
            pass  # Client already disconnected
    
    finally:
        # STEP 5: Cleanup
        await pubsub.close()
        try:
            await websocket.close()
        except:
            pass  # Already closed
        logger.info(f"WebSocket connection closed: {request_id}")
