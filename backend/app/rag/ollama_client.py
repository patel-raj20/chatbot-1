"""
Ollama LLM Client
=================
Interfaces with Ollama for text generation using retrieved context.

WHAT IS OLLAMA:
    - Local LLM runtime (like running ChatGPT on your computer)
    - Supports various models (gemma3, llama2, mistral, etc.)
    - No API keys needed, fully private
    
WHY OLLAMA:
    - Privacy: Data stays on your server
    - No cost: No API fees
    - Control: Choose your own model
    
MODEL USED: gemma3
    - Google's Gemma model (3B parameters)
    - Good balance of speed and quality
    - Requires ~4GB RAM
    
WHERE USED: Called by pipeline.py after retrieving context chunks
"""

import requests
from .config import OLLAMA_URL, OLLAMA_MODEL
from app.core.logger import get_logger

logger = get_logger(__name__)


def count_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 4 characters)"""
    return len(text) // 4


def generate_answer(context: str, query: str) -> str:
    """
    Generate answer using Ollama LLM with retrieved context.
    
    WHY: 
        - Context alone is not an answer
        - LLM synthesizes context into natural response
        - Can reformat, summarize, and clarify information
    
    WHERE: Called by ask_question() in pipeline.py
    HOW:
        1. Create prompt with context and query
        2. Send to Ollama API
        3. Ollama generates natural language answer
        4. Return answer to user
    
    Args:
        context: Retrieved text chunks joined together
        query: User's original question
        
    Returns:
        Natural language answer from LLM
        
    Raises:
        Exception: If Ollama is unavailable or fails
        
    PROMPT STRUCTURE:
        System instructions
        → Context from documents
        → User's question
        → Answer constraints
    """
    # Construct prompt for LLM
    # WHY: Clear instructions help LLM stay focused and accurate
    prompt = f"""You are a factual assistant.

Rules:
- Answer ONLY from the provided context
- Add your context in answer not just copy it from the document
- Do NOT repeat the context
- Use complete sentences
- Maintain proper grammar and punctuation
- If the question is not related to the context, respond with:
  "The question is not related to the document."

Context:
{context}

Question: {query}

Answer (use only information from the context above):"""

    # Calculate token counts
    prompt_tokens = count_tokens(prompt)
    
    logger.info(f"\n🤖 Generating answer with {OLLAMA_MODEL}...")
    logger.debug(f"   Input tokens: ~{prompt_tokens}")
    
    try:
        # Send request to Ollama API
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,  # Get complete response at once
                "options": {
                    "temperature": 0.8,  # Creativity (0.0=deterministic, 1.0=creative)
                    "top_p": 0.9  # Nucleus sampling threshold
                }
            },
            timeout=60  # 60 second timeout
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse response
        response_data = response.json()
        if "response" not in response_data:
            raise Exception(f"Unexpected response format: {response_data}")
        
        answer = response_data["response"].strip()
        answer_tokens = count_tokens(answer)
        
        logger.info(f"✓ Answer generated (~{answer_tokens} tokens)\n")
        
        return answer
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Cannot connect to Ollama at {OLLAMA_URL}")
        raise Exception(
            f"Cannot connect to Ollama at {OLLAMA_URL}. "
            "Is Ollama running? Start it with: ollama serve"
        )
        
    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out after 60 seconds")
        raise Exception(
            "Ollama request timed out. The model might be too slow or not responding."
        )
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"Ollama HTTP error: {e.response.status_code}")
        raise Exception(
            f"Ollama HTTP error: {e.response.status_code} - {e.response.text}"
        )
        
    except Exception as e:
        logger.error(f"Ollama request failed: {str(e)}")
        raise Exception(f"Ollama error: {str(e)}")
