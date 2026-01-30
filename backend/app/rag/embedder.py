"""
Text Embedder
=============
Converts text into vector embeddings using Sentence Transformers.

WHAT ARE EMBEDDINGS:
    - Numerical representations of text (vectors)
    - Similar text has similar vectors
    - 384-dimensional vectors (all-MiniLM-L6-v2 model)
    
WHY EMBEDDINGS:
    - Enable semantic search (meaning-based, not just keywords)
    - Can find "technical support" even if user asks "help with tech"
    - Foundation of RAG system
    
MODEL: all-MiniLM-L6-v2
    - Fast and lightweight (22MB)
    - Good balance between speed and quality
    - 384-dimensional output
    
WHERE USED: Called by pipeline.py and retriever.py
"""

from sentence_transformers import SentenceTransformer
from app.core.logger import get_logger

logger = get_logger(__name__)

# Global model instance (loaded once, reused for all requests)
# WHY: Loading model is slow, so we do it once and reuse
_model = None


def embed(texts: list[str]) -> list[list[float]]:
    """
    Convert text strings into vector embeddings.
    
    WHY: Transforms text into numerical format for similarity search
    WHERE: 
        - During PDF ingestion (embed chunks for storage)
        - During query (embed user question for search)
    HOW:
        1. Load Sentence Transformer model (once)
        2. Pass text through model
        3. Get 384-dimensional vector for each text
    
    Args:
        texts: List of text strings to embed
        
    Returns:
        List of 384-dimensional embedding vectors
        
    Example:
        texts = ["hello world", "goodbye world"]
        embeddings = embed(texts)
        # embeddings[0] = [0.123, -0.456, 0.789, ..., 0.234]  (384 numbers)
        # embeddings[1] = [0.234, -0.567, 0.890, ..., 0.345]  (384 numbers)
    """
    global _model
    
    # Load model on first use
    if _model is None:
        logger.info("Loading Sentence Transformer model: all-MiniLM-L6-v2")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Model loaded successfully")
    
    logger.debug(f"Generating embeddings for {len(texts)} text(s)")
    embeddings = _model.encode(texts).tolist()
    logger.debug(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}")
    
    return embeddings
