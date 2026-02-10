"""
Redis Pub/Sub Service
=====================
Handles Redis Pub/Sub for real-time streaming communication between Worker and WebSocket.

WHY PUB/SUB:
    - Workers and WebSocket servers are decoupled
    - Worker publishes tokens without knowing about clients
    - WebSocket subscribes and forwards to client
    - Scales horizontally (multiple workers, multiple WS servers)

CHANNEL FORMAT:
    chat_stream:{request_id}
    
    Example: chat_stream:123e4567-e89b-12d3-a456-426614174000

MESSAGE TYPES:
    1. Token message: {"type": "token", "content": "Hello"}
    2. Done message: {"type": "done"}
    3. Error message: {"type": "error", "message": "Error details"}

FLOW:
    Worker → Redis Pub/Sub → WebSocket → Client
    
IMPORTANT:
    - This is NOT Redis Cache (that's in cache/redis_client.py)
    - This is for LIVE streaming only
    - Messages are ephemeral (not stored)
"""

import redis.asyncio as redis
import json
from typing import Optional, AsyncGenerator
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class RedisPubSubService:
    """
    Redis Pub/Sub service for streaming communication.
    
    RESPONSIBILITIES:
        - Publisher: Worker publishes tokens/completion messages
        - Subscriber: WebSocket subscribes to token stream
    """
    
    def __init__(self):
        """Initialize service (connection established via connect())."""
        self._redis: Optional[redis.Redis] = None
        self._is_connected = False
    
    async def connect(self) -> None:
        """
        Establish connection to Redis.
        
        WHERE: Called during app startup or worker initialization
        """
        try:
            # Create Redis connection (separate from cache)
            self._redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,  # Automatic UTF-8 decoding
                health_check_interval=30
            )
            
            # Test connection
            await self._redis.ping()
            self._is_connected = True
            logger.info("✓ Redis Pub/Sub connection established")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis Pub/Sub: {e}")
            raise
    
    async def publish_token(self, request_id: str, token: str) -> bool:
        """
        Publish a single token to Redis channel.
        
        WHY: Worker streams Groq tokens one by one
        WHERE: Called by worker for each token from Groq API
        HOW: Publishes to channel 'chat_stream:{request_id}'
        
        Args:
            request_id: Unique request identifier
            token: Single token from LLM (could be word, punctuation, etc.)
            
        Returns:
            True if published successfully
        """
        if not self._is_connected:
            logger.error("Cannot publish: Not connected to Redis")
            return False
        
        try:
            channel = f"chat_stream:{request_id}"
            message = json.dumps({"type": "token", "content": token})
            
            # Publish to channel (returns number of subscribers)
            subscribers = await self._redis.publish(channel, message)
            
            # Log only if no subscribers (potential issue)
            if subscribers == 0:
                logger.warning(f"No subscribers listening to {channel}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish token: {e}")
            return False
    
    async def publish_done(self, request_id: str) -> bool:
        """
        Publish completion signal to Redis channel.
        
        WHY: WebSocket needs to know when streaming is complete
        WHERE: Called by worker after all tokens are sent
        HOW: Sends special "done" message
        
        Args:
            request_id: Unique request identifier
            
        Returns:
            True if published successfully
        """
        if not self._is_connected:
            logger.error("Cannot publish: Not connected to Redis")
            return False
        
        try:
            channel = f"chat_stream:{request_id}"
            message = json.dumps({"type": "done"})
            
            await self._redis.publish(channel, message)
            logger.info(f"✓ Published DONE signal for request {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish done signal: {e}")
            return False
    
    async def publish_error(self, request_id: str, error_message: str) -> bool:
        """
        Publish error message to Redis channel.
        
        WHY: Worker needs to notify client of failures
        WHERE: Called by worker if RAG/Groq processing fails
        
        Args:
            request_id: Unique request identifier
            error_message: Error description
            
        Returns:
            True if published successfully
        """
        if not self._is_connected:
            logger.error("Cannot publish: Not connected to Redis")
            return False
        
        try:
            channel = f"chat_stream:{request_id}"
            message = json.dumps({"type": "error", "message": error_message})
            
            await self._redis.publish(channel, message)
            logger.info(f"✓ Published ERROR for request {request_id}: {error_message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish error: {e}")
            return False
    
    async def subscribe_stream(self, request_id: str) -> AsyncGenerator[dict, None]:
        """
        Subscribe to token stream for a specific request.
        
        WHY: WebSocket needs to receive tokens from worker in real-time
        WHERE: Called by WebSocket endpoint when client connects
        HOW:
            1. Subscribe to Redis channel
            2. Yield each message as it arrives
            3. Stop when 'done' message received
        
        Args:
            request_id: Unique request identifier
            
        Yields:
            Dictionary: {"type": "token", "content": "..."} or {"type": "done"}
            
        IMPORTANT: This is an async generator - use with 'async for'
        
        Example:
            async for msg in pubsub.subscribe_stream(request_id):
                if msg["type"] == "token":
                    await websocket.send_text(msg["content"])
                elif msg["type"] == "done":
                    break
        """
        if not self._is_connected:
            logger.error("Cannot subscribe: Not connected to Redis")
            return
        
        channel = f"chat_stream:{request_id}"
        pubsub = self._redis.pubsub()
        
        try:
            # Subscribe to channel
            await pubsub.subscribe(channel)
            logger.info(f"✓ Subscribed to {channel}")
            
            # Listen for messages
            async for message in pubsub.listen():
                # Skip subscription confirmation messages
                if message["type"] != "message":
                    continue
                
                try:
                    # Parse message data
                    data = json.loads(message["data"])
                    yield data
                    
                    # Stop if done message received
                    if data.get("type") == "done":
                        logger.info(f"Stream completed for request {request_id}")
                        break
                    
                    # Stop if error message received
                    if data.get("type") == "error":
                        logger.error(f"Stream error for request {request_id}: {data.get('message')}")
                        break
                        
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode message: {message['data']}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in subscribe_stream: {e}")
            raise
        
        finally:
            # Clean up subscription
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            logger.info(f"Unsubscribed from {channel}")
    
    async def close(self) -> None:
        """
        Close Redis connection gracefully.
        
        WHERE: Called during app shutdown
        """
        try:
            if self._redis:
                await self._redis.close()
                self._is_connected = False
                logger.info("Redis Pub/Sub connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis Pub/Sub connection: {e}")


# Singleton instance
_pubsub_service: Optional[RedisPubSubService] = None


async def get_pubsub_service() -> RedisPubSubService:
    """
    Get or create singleton Pub/Sub service instance.
    
    USAGE: Dependency injection in FastAPI routes
    
    Example:
        @router.websocket("/ws/chat/{request_id}")
        async def websocket_endpoint(
            request_id: str,
            pubsub: RedisPubSubService = Depends(get_pubsub_service)
        ):
            async for msg in pubsub.subscribe_stream(request_id):
                ...
    """
    global _pubsub_service
    
    if _pubsub_service is None:
        _pubsub_service = RedisPubSubService()
        await _pubsub_service.connect()
    
    return _pubsub_service
