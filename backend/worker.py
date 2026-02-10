"""
RAG Worker Service
==================
Background worker that processes RAG jobs from RabbitMQ queue.

RESPONSIBILITIES:
    1. Consume jobs from RabbitMQ
    2. Execute RAG pipeline (retrieve + LLM streaming)
    3. Publish each token to Redis Pub/Sub
    4. ACK RabbitMQ message when done

WHAT THIS WORKER DOES NOT DO:
    - Does NOT know about WebSockets (decoupled)
    - Does NOT store RAG answers in Redis cache (as per requirements)
    - Does NOT talk to HTTP clients directly

ARCHITECTURE:
    RabbitMQ → Worker → Redis Pub/Sub → WebSocket → Client
    
SCALING:
    - Single worker for now
    - Designed to support multiple workers later (RabbitMQ handles load balancing)
    - Each worker processes one job at a time (prefetch_count=1)
    
USAGE:
    python worker.py
    
    Or in Docker:
    docker-compose up worker
"""

import json
import time
import sys
import os
import signal

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.queue.rabbitmq_client import RabbitMQClient
from app.rag.pipeline_streaming import ask_question_streaming
from app.core.logger import get_logger
from app.core.config import settings
from app.database import SessionLocal
from app.models import ChatMessage
import uuid as uuid_module

logger = get_logger(__name__)


class RAGWorker:
    """
    Worker that processes RAG jobs from queue.
    
    WORKFLOW:
        1. Pull job from RabbitMQ
        2. Extract request_id and question
        3. Execute RAG pipeline (streaming)
        4. Publish each token to Redis Pub/Sub
        5. Publish "done" signal
        6. ACK RabbitMQ message
    """
    
    def __init__(self):
        """Initialize worker components."""
        self.rabbitmq: RabbitMQClient = None
        self.should_stop = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.should_stop = True
        if self.rabbitmq:
            self.rabbitmq.stop_consuming()
    
    def connect(self) -> None:
        """
        Establish connections to RabbitMQ.
        
        WHERE: Called once on worker startup
        """
        try:
            # Connect to RabbitMQ
            logger.info("Connecting to RabbitMQ...")
            self.rabbitmq = RabbitMQClient()
            self.rabbitmq.connect()
            
            logger.info("✓ Worker connections established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect worker: {e}")
            raise
    
    def process_job(self, ch, method, properties, body):
        """
        Process a single job from RabbitMQ (callback function).
        
        WHY: RabbitMQ calls this for each message in queue
        WHERE: Registered as callback in start_consuming()
        HOW:
            1. Parse job data
            2. Validate required fields
            3. Execute RAG streaming
            4. Publish tokens to Redis Pub/Sub
            5. ACK message when complete
        
        Args:
            ch: RabbitMQ channel
            method: Delivery method (contains delivery_tag for ACK)
            properties: Message properties
            body: JSON message body
        """
        request_id = None
        try:
            # STEP 1: Parse job data
            job = json.loads(body)
            request_id = job.get("request_id")
            user_id = job.get("user_id")
            question = job.get("question")
            session_id = job.get("session_id")
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📥 Job received: {request_id}")
            logger.info(f"   User: {user_id}")
            logger.info(f"   Session: {session_id}")
            logger.info(f"   Question: {question}")
            logger.info(f"{'='*60}\n")
            
            # STEP 2: Validate required fields
            if not request_id or not question:
                logger.error("Invalid job: missing request_id or question")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # STEP 3: Execute RAG pipeline with streaming
            start_time = time.time()
            token_count = 0
            
            logger.info("🔄 Starting RAG processing...")
            
            # Use sync Redis client for Pub/Sub in callback
            import redis
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
            
            try:
                # Accumulate tokens to save complete answer later
                full_answer = ""
                
                # Stream tokens from RAG pipeline
                for token in ask_question_streaming(question):
                    # STEP 4: Publish each token to Redis Pub/Sub (sync)
                    message = json.dumps({"type": "token", "content": token})
                    channel = f"chat_stream:{request_id}"
                    redis_client.publish(channel, message)
                    token_count += 1
                    
                    # Accumulate token for database storage
                    full_answer += token
                    
                    # Log progress every 50 tokens
                    if token_count % 50 == 0:
                        logger.debug(f"   Streamed {token_count} tokens...")
                
                # STEP 5: Publish completion signal
                done_message = json.dumps({"type": "done"})
                redis_client.publish(f"chat_stream:{request_id}", done_message)
                
                elapsed = time.time() - start_time
                logger.info(f"\n✓ Job completed: {request_id}")
                logger.info(f"   Tokens streamed: {token_count}")
                logger.info(f"   Time: {elapsed:.2f}s\n")
                
                # STEP 6: Save complete RAG answer to database (chat history)
                if session_id and full_answer:
                    try:
                        db = SessionLocal()
                        try:
                            # Save the bot's RAG answer to chat history
                            chat_message = ChatMessage(
                                id=uuid_module.uuid4(),
                                session_id=uuid_module.UUID(session_id),
                                sender="bot",
                                message_text=full_answer,
                                node_id=None
                            )
                            db.add(chat_message)
                            db.commit()
                            logger.info(f"✓ Saved RAG answer to chat history (session: {session_id})")
                        except Exception as db_error:
                            logger.warning(f"Failed to save RAG answer to database: {db_error}")
                            db.rollback()
                        finally:
                            db.close()
                    except Exception as session_error:
                        logger.warning(f"Failed to create database session: {session_error}")
                
            except Exception as stream_error:
                logger.error(f"RAG processing failed: {stream_error}")
                # Publish error to client
                error_message = json.dumps({"type": "error", "message": str(stream_error)})
                redis_client.publish(f"chat_stream:{request_id}", error_message)
            finally:
                redis_client.close()
            
            # STEP 7: ACK message (mark as processed)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"✓ Message ACKed: {request_id}")
            
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in message: {body}")
            # ACK to remove bad message from queue
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Job processing failed: {e}")
            # Publish error if we have request_id
            if request_id:
                try:
                    import redis
                    redis_client = redis.Redis(
                        host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        decode_responses=True
                    )
                    error_message = json.dumps({"type": "error", "message": f"Worker error: {str(e)}"})
                    redis_client.publish(f"chat_stream:{request_id}", error_message)
                    redis_client.close()
                except:
                    pass
            # ACK to prevent infinite retries
            ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def start(self) -> None:
        """
        Start worker (blocking - runs until stopped).
        
        WHERE: Called by main() after connections established
        HOW: Registers callback and starts consuming from RabbitMQ
        
        BLOCKING: This runs forever until SIGINT/SIGTERM received
        """
        try:
            logger.info("\n" + "="*60)
            logger.info("🚀 RAG Worker started successfully!")
            logger.info("="*60)
            logger.info(f"Queue: {self.rabbitmq.QUEUE_NAME}")
            logger.info(f"Model: {settings.GROQ_MODEL if hasattr(settings, 'GROQ_MODEL') else 'default'}")
            logger.info("="*60 + "\n")
            
            # Start consuming (blocks here)
            self.rabbitmq.consume(self.process_job)
            
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
        except Exception as e:
            logger.error(f"Worker error: {e}")
            raise
    
    def shutdown(self) -> None:
        """
        Cleanup connections gracefully.
        
        WHERE: Called during shutdown
        """
        logger.info("Shutting down worker...")
        
        if self.rabbitmq:
            self.rabbitmq.close()
        
        logger.info("Worker shutdown complete")


def main():
    """
    Main entry point for worker.
    
    FLOW:
        1. Initialize worker
        2. Connect to services
        3. Start consuming jobs
        4. Cleanup on shutdown
    """
    worker = RAGWorker()
    
    try:
        # Connect to services
        worker.connect()
        
        # Start processing jobs (blocks here)
        worker.start()
        
    except Exception as e:
        logger.error(f"Worker failed to start: {e}")
        sys.exit(1)
    
    finally:
        # Cleanup
        worker.shutdown()


if __name__ == "__main__":
    """
    Run worker directly:
        python worker.py
        
    Or with Docker:
        docker-compose up worker
    """
    logger.info("Starting RAG Worker...")
    
    # Check required environment variables
    if not hasattr(settings, 'RABBITMQ_HOST'):
        logger.error("RABBITMQ_HOST not configured in settings")
        sys.exit(1)
    
    if not hasattr(settings, 'REDIS_HOST'):
        logger.error("REDIS_HOST not configured in settings")
        sys.exit(1)
    
    # Run worker
    main()
