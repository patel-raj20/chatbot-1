"""
Vector Retriever
================
Retrieves relevant document chunks using similarity search.

HOW SIMILARITY SEARCH WORKS:
    1. Convert user query to embedding (768-dim vector)
    2. Search Milvus for vectors similar to query vector
    3. Return text chunks with highest similarity scores
    
SIMILARITY METRIC: cosine similarity
    - Measures angle between vectors
    - Higher score = more similar
    - Range: 0.0 (unrelated) to 1.0 (identical)
    
WHERE USED: Called by pipeline.py to answer questions
"""

from .embedder import embed
from .collection import get_collection
from app.core.logger import get_logger

logger = get_logger(__name__)


def retrieve(query: str, top_k: int = 5, threshold: float = 0.3) -> list[str]:
    """
    Retrieve relevant document chunks for a query.
    
    WHY: Finds most relevant text chunks to answer user's question
    WHERE: Called by ask_question() in pipeline.py
    HOW:
        1. Convert query to embedding
        2. Search Milvus for similar embeddings
        3. Filter by similarity threshold
        4. Return matching text chunks
    
    Args:
        query: User's question
        top_k: Number of results to retrieve (default: 5)
        threshold: Minimum similarity score (0.0-1.0, default: 0.0)
                  Lower = more lenient, Higher = stricter
        
    Returns:
        List of text chunks (most relevant first)
        
    Example:
        query = "What are business hours?"
        chunks = retrieve(query, top_k=3)
        # Returns top 3 most relevant chunks from all PDFs
        
    THRESHOLD TUNING:
        - 0.0: Return all top_k results (very lenient)
        - 0.3: Good balance for general use
        - 0.5: Only very relevant matches (strict)
        - 0.7+: Extremely strict, may return nothing
    """
    col = get_collection()
    
    # STEP 1: Convert query to embedding
    logger.debug(f"Converting query to embedding: '{query}'")
    q_emb = embed([query])[0]  # Get embedding for single query
    
    # STEP 2: Search Milvus for similar vectors
    logger.debug(f"Searching for top {top_k} similar chunks (threshold={threshold})")
    results = col.search(
        [q_emb],
        "embedding",
        param={
            "metric_type": "COSINE",  # Cosine similarity
            "params": {"nprobe": 10}  # Number of clusters to search
        },
        limit=top_k,
        output_fields=["content"]  # Return text content
    )
    
    # STEP 3: Filter by threshold and extract content
    matches = []
    all_scores = []
    
    logger.info(f"\n{'='*90}")
    logger.info(f"                  🎯 SIMILARITY SCORE ANALYSIS")
    logger.info(f"{'='*90}")
    logger.info(f"Query: {query}")
    logger.info(f"Top K: {top_k} | Threshold: {threshold:.4f}")
    logger.info(f"{'='*90}")
    
    # Collect scores and show each chunk
    for idx, hit in enumerate(results[0], 1):
        score = hit.score
        content = hit.entity.get("content")
        all_scores.append(score)
        
        status = "✓ PASS" if score >= threshold else "✗ FAIL"
        logger.info(f"\n[Chunk {idx}] Score: {score:.4f} {status}")
        logger.info(f"Content: {content}")
        logger.info(f"{'-'*90}")
        
        if score >= threshold:
            matches.append(content)
    
    # Show statistics
    if all_scores:
        logger.info(f"\n📊 STATISTICS:")
        logger.info(f"   Highest: {max(all_scores):.4f} | Lowest: {min(all_scores):.4f} | Avg: {sum(all_scores)/len(all_scores):.4f}")
        logger.info(f"   Accepted: {len(matches)}/{len(all_scores)} chunks")
    
    logger.info(f"{'='*90}\n")
    
    return matches
