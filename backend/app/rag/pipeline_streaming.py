"""
Streaming RAG Pipeline
=======================
RAG pipeline with token-by-token streaming support.

DIFFERENCE FROM pipeline.py:
    - pipeline.py: Returns complete answer (for HTTP endpoints)
    - THIS FILE: Streams tokens one by one (for worker)

WHERE USED: Called by worker.py when processing jobs

FLOW:
    1. Retrieve relevant chunks from Milvus
    2. Combine chunks into context
    3. Stream LLM response token by token
    4. Worker publishes each token to Redis Pub/Sub
"""

from typing import Generator
from .retriever import retrieve
from .ollama_client_streaming import generate_answer_streaming
from app.core.logger import get_logger

logger = get_logger(__name__)


def ask_question_streaming(query: str) -> Generator[str, None, None]:
    """
    Answer question using RAG with streaming (token by token).
    
    WHY: Real-time streaming for better user experience
    WHERE: Called by worker when processing jobs from RabbitMQ
    HOW:
        1. Retrieve relevant chunks from Milvus
        2. If no chunks found → yield error message
        3. If chunks found → stream LLM response
    
    Args:
        query: User's question
        
    Yields:
        str: Individual tokens from LLM response
        
    Example:
        for token in ask_question_streaming("What is ML?"):
            # Publish each token to Redis Pub/Sub
            pubsub.publish_token(request_id, token)
    """
    # STEP 1: Retrieve relevant chunks
    logger.info(f"Processing RAG query: {query}")
    chunks = retrieve(query)
    
    if not chunks:
        logger.warning(f"No relevant chunks found for query: '{query}'")
        # Yield error message as single token
        yield "I couldn't find relevant information in the uploaded documents. Please make sure you've uploaded a document first."
        return
    
    # STEP 2: Combine chunks into context
    context = "\n\n".join(chunks)
    logger.info(f"Retrieved {len(chunks)} chunks for context")
    
    # STEP 3: Stream LLM response
    try:
        for token in generate_answer_streaming(context, query):
            yield token
    except Exception as e:
        logger.error(f"Streaming failed: {e}")
        # Yield error message
        yield f"\n\n[Error: {str(e)}]"
