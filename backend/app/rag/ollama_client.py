"""
Groq LLM Client
===============
Interfaces with Groq API for fast text generation using retrieved context.

WHAT IS GROQ:
    - Cloud-based LLM API with ultra-fast inference
    - Uses specialized hardware (LPU) for speed
    - Supports Llama, Mixtral, Gemma models
    
WHY GROQ:
    - Speed: Fastest LLM inference available (300+ tokens/sec)
    - Quality: Access to top models like Llama 3.3 70B
    - Cost: Affordable API pricing
    
MODEL USED: llama-3.3-70b-versatile
    - Meta's Llama 3.3 (70B parameters)
    - Excellent for question answering
    - Fast responses on Groq infrastructure
    
WHERE USED: Called by pipeline.py after retrieving context chunks
"""

from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL
from app.core.logger import get_logger

logger = get_logger(__name__)


def count_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 4 characters)"""
    return len(text) // 4


def generate_answer(context: str, query: str) -> str:
    """
    Generate answer using Groq LLM with retrieved context.
    
    WHY: 
        - Context alone is not an answer
        - LLM synthesizes context into natural response
        - Can reformat, summarize, and clarify information
    
    WHERE: Called by ask_question() in pipeline.py
    HOW:
        1. Create prompt with context and query
        2. Send to Groq API
        3. Groq generates natural language answer
        4. Return answer to user
    
    Args:
        context: Retrieved text chunks joined together
        query: User's original question
        
    Returns:
        Natural language answer from LLM
        
    Raises:
        Exception: If Groq API is unavailable or fails
        
    PROMPT STRUCTURE:
        System instructions
        → Context from documents
        → User's question
        → Answer constraints
    """
    # Check if API key is configured
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY not configured in .env file")
        raise Exception("GROQ_API_KEY not configured. Please add it to your .env file.")
    
    # Calculate token counts
    prompt_tokens = count_tokens(context) + count_tokens(query)
    
    logger.info(f"\n🚀 Generating answer with Groq ({GROQ_MODEL})...")
    logger.debug(f"   Input tokens: ~{prompt_tokens}")
    
    try:
        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        # Send request to Groq API with chat completion format
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a factual assistant. Answer ONLY from the provided context. "
                        "Add your context in answer not just copy it from the document. "
                        "Do NOT repeat the context verbatim. Use complete sentences and proper grammar. "
                        "Do NOT use markdown formatting such as bold (**), italics, or bullet points. Write in plain text only. "
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
            temperature=0.7,  # Creativity level
            max_tokens=1024,  # Maximum response length
            top_p=0.9
        )
        
        # Extract answer from response
        answer = chat_completion.choices[0].message.content.strip()
        answer_tokens = count_tokens(answer)
        
        logger.info(f"✓ Answer generated (~{answer_tokens} tokens)\n")
        
        return answer
        
    except Exception as e:
        logger.error(f"Groq API request failed: {str(e)}")
        raise Exception(f"Groq API error: {str(e)}")

