"""
Text Chunker - WORD-BASED CHUNKING
===================================
Splits text into chunks based on WORD COUNT, not character count.

STRATEGY:
    - Word-based chunking: Chunks contain exactly N words (default: 800 words)
    - Continuous chunking: No section/paragraph boundaries respected
    - Smart overlap: Overlaps by word count for context preservation
    - Preserves newlines: Maintains text structure within chunks

WHY THIS WORKS:
    - Consistent chunk sizes based on word count
    - Better for semantic embeddings (same amount of content per chunk)
    - Overlap ensures context continuity across chunks
    - Simple and predictable chunking behavior

WHERE USED: Called by pipeline.py during PDF ingestion
"""

from app.core.logger import get_logger
import re

logger = get_logger(__name__)

# Configuration - WORD-BASED (not character-based)
CHUNK_SIZE_WORDS = 300        # Target words per chunk
CHUNK_OVERLAP_WORDS = 75     # Overlap words for context preservation
MIN_CHUNK_SIZE_WORDS = 0     # Minimum words to keep a chunk


def chunk_text(text: str) -> list[str]:
    """
    Word-based chunking: Split text into chunks by word count.
    
    ALGORITHM:
        1. Split text into words (preserving spaces and newlines)
        2. Group words into chunks of CHUNK_SIZE_WORDS
        3. Add CHUNK_OVERLAP_WORDS overlap between consecutive chunks
    
    Args:
        text: Full text string from PDF
        
    Returns:
        List of text chunks (each ~300 words)
    """
    logger.info(f"Starting word-based chunking for {len(text)} characters")
    
    # Step 1: Split into words while preserving whitespace structure
    words = text.split()  # Split by any whitespace (space, newline, tab)
    total_words = len(words)
    
    logger.info(f"Total words in document: {total_words}")
    
    if total_words == 0:
        logger.warning("No words found in text")
        return []
    
    # Step 2: Create chunks with word count
    chunks = []
    start_idx = 0
    
    while start_idx < total_words:
        # Get words for this chunk
        end_idx = min(start_idx + CHUNK_SIZE_WORDS, total_words)
        chunk_words = words[start_idx:end_idx]
        
        # Skip if chunk is too small (unless it's the last chunk)
        if len(chunk_words) < MIN_CHUNK_SIZE_WORDS and end_idx < total_words:
            logger.debug(f"Skipping small chunk with {len(chunk_words)} words")
            start_idx = end_idx
            continue
        
        # Join words back into text
        chunk_text = ' '.join(chunk_words)
        chunks.append(chunk_text)
        
        logger.debug(f"Created chunk {len(chunks)}: {len(chunk_words)} words, {len(chunk_text)} chars")
        
        # Move to next chunk with overlap
        start_idx += CHUNK_SIZE_WORDS - CHUNK_OVERLAP_WORDS
    
    logger.info(f"Created {len(chunks)} chunks (target={CHUNK_SIZE_WORDS} words, overlap={CHUNK_OVERLAP_WORDS} words)")
    
    # Log statistics
    if chunks:
        avg_words = sum(len(c.split()) for c in chunks) / len(chunks)
        logger.info(f"Average words per chunk: {avg_words:.1f}")
    
    return chunks
