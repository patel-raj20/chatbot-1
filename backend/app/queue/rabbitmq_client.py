"""
RabbitMQ Client
===============
Handles all RabbitMQ operations for job queueing.

DESIGN PHILOSOPHY:
    - Simple: Single queue with direct exchange (no complex routing)
    - Reliable: Connection pooling, auto-reconnect, ACK confirmation
    - Isolated: RabbitMQ logic stays in this module only

QUEUE STRUCTURE:
    Exchange: 'chat_exchange' (direct)
    Queue: 'chat_queue'
    Routing Key: 'chat.rag'

MESSAGE FORMAT:
    {
        "request_id": "uuid-string",
        "user_id": "uuid-string",
        "question": "user's question text",
        "session_id": "uuid-string"
    }
"""

import pika
import json
from typing import Dict, Any, Optional, Callable
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class RabbitMQClient:
    """
    RabbitMQ client for publishing and consuming messages.
    
    USAGE:
        # Publishing (API side)
        client = RabbitMQClient()
        client.connect()
        client.publish_job({"request_id": "123", "question": "What is RAG?"})
        
        # Consuming (Worker side)
        client = RabbitMQClient()
        client.connect()
        client.consume(callback_function)
    """
    
    # Queue configuration
    EXCHANGE_NAME = "chat_exchange"
    QUEUE_NAME = "chat_queue"
    ROUTING_KEY = "chat.rag"
    
    def __init__(self):
        """Initialize client (connection established via connect())."""
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self._is_connected = False
        self._connection_params = None  # Store connection params for reconnection
    
    def connect(self) -> None:
        """
        Establish connection to RabbitMQ server.
        
        WHY: Connection pooling improves performance
        WHERE: Called once during app startup (API) or worker initialization
        HOW:
            1. Connect to RabbitMQ using credentials from settings
            2. Create channel (like a session)
            3. Declare exchange and queue (idempotent - safe to call multiple times)
            4. Bind queue to exchange with routing key
        
        Raises:
            Exception: If connection fails (check RabbitMQ is running)
        """
        try:
            # Build connection parameters
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASS
            )
            
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,  # Keep connection alive
                blocked_connection_timeout=300
            )
            
            # Store parameters for reconnection
            self._connection_params = parameters
            
            # Establish connection
            logger.info(f"Connecting to RabbitMQ at {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}...")
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange (direct type for simple routing)
            self.channel.exchange_declare(
                exchange=self.EXCHANGE_NAME,
                exchange_type='direct',
                durable=True  # Survive RabbitMQ restarts
            )
            
            # Declare queue
            self.channel.queue_declare(
                queue=self.QUEUE_NAME,
                durable=True  # Survive RabbitMQ restarts
            )
            
            # Bind queue to exchange
            self.channel.queue_bind(
                exchange=self.EXCHANGE_NAME,
                queue=self.QUEUE_NAME,
                routing_key=self.ROUTING_KEY
            )
            
            self._is_connected = True
            logger.info("✓ RabbitMQ connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def is_connection_healthy(self) -> bool:
        """
        Check if the RabbitMQ connection and channel are actually open.
        
        WHY: The connection can become stale after inactivity
        WHERE: Called before publishing to verify connection health
        HOW: Checks both connection and channel states
        
        Returns:
            True if connection and channel are open, False otherwise
        """
        try:
            if not self._is_connected:
                return False
            
            # Check if connection exists and is open
            if not self.connection or not self.connection.is_open:
                logger.warning("RabbitMQ connection is closed")
                self._is_connected = False
                return False
            
            # Check if channel exists and is open
            if not self.channel or not self.channel.is_open:
                logger.warning("RabbitMQ channel is closed")
                self._is_connected = False
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking connection health: {e}")
            self._is_connected = False
            return False
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to RabbitMQ.
        
        WHY: Connection may be closed due to inactivity or network issues
        WHERE: Called by publish_job when connection is unhealthy
        HOW: Closes old connection and creates a new one
        
        Returns:
            True if reconnection successful, False otherwise
        """
        try:
            logger.info("Attempting to reconnect to RabbitMQ...")
            
            # Close old connection if it exists
            try:
                if self.channel:
                    self.channel.close()
            except:
                pass
            
            try:
                if self.connection:
                    self.connection.close()
            except:
                pass
            
            self._is_connected = False
            
            # Reconnect using stored parameters
            if self._connection_params:
                self.connection = pika.BlockingConnection(self._connection_params)
                self.channel = self.connection.channel()
                
                # Re-declare exchange and queue
                self.channel.exchange_declare(
                    exchange=self.EXCHANGE_NAME,
                    exchange_type='direct',
                    durable=True
                )
                
                self.channel.queue_declare(
                    queue=self.QUEUE_NAME,
                    durable=True
                )
                
                self.channel.queue_bind(
                    exchange=self.EXCHANGE_NAME,
                    queue=self.QUEUE_NAME,
                    routing_key=self.ROUTING_KEY
                )
                
                self._is_connected = True
                logger.info("✓ Successfully reconnected to RabbitMQ")
                return True
            else:
                logger.error("Cannot reconnect: connection parameters not stored")
                return False
                
        except Exception as e:
            logger.error(f"Failed to reconnect to RabbitMQ: {e}")
            self._is_connected = False
            return False
    
    def publish_job(self, job_data: Dict[str, Any]) -> bool:
        """
        Publish a job to RabbitMQ queue.
        
        WHY: Offload RAG processing to worker for scalability
        WHERE: Called by HTTP endpoint after generating request_id
        HOW:
            1. Check if connection is healthy (auto-reconnect if not)
            2. Serialize job data to JSON
            3. Publish to exchange with routing key
            4. Message routes to queue, worker picks it up
        
        Args:
            job_data: Dictionary containing request_id, user_id, question, etc.
            
        Returns:
            True if published successfully, False otherwise
            
        Example:
            publish_job({
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "user-uuid",
                "question": "What is machine learning?",
                "session_id": "session-uuid"
            })
        """
        # STEP 1: Check connection health and reconnect if needed
        if not self.is_connection_healthy():
            logger.warning("RabbitMQ connection is unhealthy, attempting to reconnect...")
            if not self.reconnect():
                logger.error("Cannot publish: Failed to reconnect to RabbitMQ")
                return False
        
        try:
            # STEP 2: Serialize to JSON
            message = json.dumps(job_data)
            
            # STEP 3: Publish with persistence
            self.channel.basic_publish(
                exchange=self.EXCHANGE_NAME,
                routing_key=self.ROUTING_KEY,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"✓ Job published to queue: {job_data.get('request_id', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish job: {e}")
            # Mark connection as unhealthy so next call will attempt reconnection
            self._is_connected = False
            return False
    
    def consume(self, callback: Callable) -> None:
        """
        Start consuming messages from queue (blocking).
        
        WHY: Worker needs to continuously process jobs
        WHERE: Called by worker.py on startup
        HOW:
            1. Register callback function to handle each message
            2. Start consuming (blocks indefinitely)
            3. Each message triggers callback with job data
            4. Worker must ACK message when done
        
        Args:
            callback: Function to call for each message
                      Signature: callback(ch, method, properties, body)
        
        BLOCKING: This function runs forever until interrupted
        
        Example:
            def process_job(ch, method, properties, body):
                job = json.loads(body)
                # ... process job ...
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            client.consume(process_job)
        """
        if not self._is_connected:
            logger.error("Cannot consume: Not connected to RabbitMQ")
            return
        
        try:
            # Set QoS: Process one message at a time
            # (important for scaling to multiple workers later)
            self.channel.basic_qos(prefetch_count=1)
            
            # Register callback
            self.channel.basic_consume(
                queue=self.QUEUE_NAME,
                on_message_callback=callback,
                auto_ack=False  # Manual ACK for reliability
            )
            
            logger.info(f"🔄 Worker started consuming from '{self.QUEUE_NAME}'...")
            logger.info("Waiting for messages. Press CTRL+C to exit.")
            
            # Start consuming (blocks here)
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            self.stop_consuming()
        except Exception as e:
            logger.error(f"Error while consuming: {e}")
            raise
    
    def stop_consuming(self) -> None:
        """Stop consuming messages gracefully."""
        if self.channel and self._is_connected:
            self.channel.stop_consuming()
            logger.info("Stopped consuming messages")
    
    def close(self) -> None:
        """
        Close RabbitMQ connection gracefully.
        
        WHERE: Called during app shutdown or worker termination
        """
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
            
            if self.connection and self.connection.is_open:
                self.connection.close()
            
            self._is_connected = False
            logger.info("RabbitMQ connection closed")
            
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")
    
    def get_queue_size(self) -> int:
        """
        Get number of messages waiting in queue.
        
        USAGE: Monitoring, debugging
        Returns:
            Number of messages in queue
        """
        if not self._is_connected:
            return -1
        
        try:
            method = self.channel.queue_declare(
                queue=self.QUEUE_NAME,
                durable=True,
                passive=True  # Don't create if doesn't exist
            )
            return method.method.message_count
        except Exception as e:
            logger.error(f"Failed to get queue size: {e}")
            return -1


# Singleton instance (optional, for convenience)
_rabbitmq_client: Optional[RabbitMQClient] = None


def get_rabbitmq_client() -> RabbitMQClient:
    """
    Get or create singleton RabbitMQ client instance.
    
    USAGE: Dependency injection in FastAPI routes
    
    Example:
        @router.post("/chat")
        def chat(rmq: RabbitMQClient = Depends(get_rabbitmq_client)):
            rmq.publish_job({...})
    """
    global _rabbitmq_client
    
    if _rabbitmq_client is None:
        _rabbitmq_client = RabbitMQClient()
        _rabbitmq_client.connect()
    
    return _rabbitmq_client
