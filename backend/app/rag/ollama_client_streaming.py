"""
Groq LLM Streaming Client
==========================
Streaming version of Groq client for real-time token generation.

DIFFERENCE FROM ollama_client.py:
    - ollama_client.py: Returns complete answer at once (for HTTP endpoints)
    - THIS FILE: Streams tokens one by one (for WebSocket streaming)

WHY STREAMING:
    - Better UX: User sees response as it's generated (like ChatGPT)
    - Lower latency: First token arrives faster
    - Feels more responsive
    
WHERE USED: Called by worker.py when processing jobs

STREAMING FLOW:
    Groq API → Worker → Redis Pub/Sub → WebSocket → Client browser
"""

from groq import Groq
from typing import Generator
from app.rag.config import GROQ_API_KEY, GROQ_MODEL
from app.core.logger import get_logger

logger = get_logger(__name__)


def generate_answer_streaming(context: str, query: str) -> Generator[str, None, None]:
    """
    Generate answer using Groq LLM with streaming (token by token).
    
    WHY: Real-time streaming for better UX
    WHERE: Called by worker when processing RAG jobs
    HOW:
        1. Create streaming request to Groq API
        2. Yield each token as it arrives
        3. Worker publishes each token to Redis Pub/Sub
    
    Args:
        context: Retrieved text chunks joined together
        query: User's original question
        
    Yields:
        str: Individual tokens from LLM response
        
    Raises:
        Exception: If Groq API is unavailable or fails
        
    Example:
        for token in generate_answer_streaming(context, question):
            print(token, end="", flush=True)  # Print in real-time
    """
    # Check if API key is configured
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not configured in .env file")
        raise Exception("GROQ_API_KEY not configured. Please add it to your .env file.")
    
    logger.info(f"🚀 Generating streaming answer with Groq ({GROQ_MODEL})...")
    
    try:
        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        # Create streaming chat completion
        stream = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a factual assistant. Answer ONLY from the provided context. "
                        "Add your context in answer not just copy it from the document. "
                        "Do NOT repeat the context verbatim. Use complete sentences and proper grammar. "
                        "If the question is not related to the context, respond with: "
                        "'The question is not related to the document.'"
                    )
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer (use only information from the context above):"
                }
            ],
            model=GROQ_MODEL,
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9,
            stream=True  # ENABLE STREAMING
        )
        
        # Yield tokens as they arrive
        token_count = 0
        for chunk in stream:
            # Extract token from chunk
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                token_count += 1
                yield token
        
        logger.info(f"✓ Streaming completed ({token_count} tokens)")
        
    except Exception as e:
        logger.error(f"Groq streaming API request failed: {str(e)}")
        raise Exception(f"Groq API error: {str(e)}")
