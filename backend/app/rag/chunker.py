"""
Text Chunker
============
Splits long text into smaller overlapping chunks.

WHY CHUNKING:
    - Embeddings work better on smaller text pieces
    - Retrieval is more precise with focused chunks
    - Overlap ensures context isn't lost at boundaries
    
HOW IT WORKS:
    - Takes text and splits into 200-character chunks
    - 50-character overlap between chunks
    - Example: "ABCDEFGHIJ" (chunk_size=5, overlap=2)
      → ["ABCDE", "CDEFG", "EFGHI", "GHIJ"]
      
WHERE USED: Called by pipeline.py during PDF ingestion
"""

from app.core.logger import get_logger

logger = get_logger(__name__)


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.
    
    WHY: 
        - Sentence Transformer models have token limits
        - Smaller chunks give more precise search results
        - Overlap preserves context across chunk boundaries
    
    WHERE: Called during PDF ingestion
    HOW:
        1. Start at position 0
        2. Extract chunk_size characters
        3. Move forward by (chunk_size - overlap)
        4. Repeat until end of text
    
    Args:
        text: Full text to chunk
        chunk_size: Number of characters per chunk (default: 200)
        overlap: Number of overlapping characters (default: 50)
        
    Returns:
        List of text chunks
        
    Example:
        text = "Hello world! This is a test message for chunking."
        chunk_size = 20, overlap = 5
        → ["Hello world! This is", "is is a test message", " message for chunkin", "chunking."]
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # Move forward with overlap
    
    logger.debug(f"Split {len(text)} characters into {len(chunks)} chunks "
                f"(size={chunk_size}, overlap={overlap})")
    return chunks
