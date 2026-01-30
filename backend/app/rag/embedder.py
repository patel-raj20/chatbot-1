"""
Text Embedder
=============
Converts text into vector embeddings using Sentence Transformers.

WHAT ARE EMBEDDINGS:
    - Numerical representations of text (vectors)
    - Similar meanings → closer vectors
    - 768-dimensional vectors (bge-base-en-v1.5 model)

WHY EMBEDDINGS:
    - Enable semantic search (meaning-based, not keywords)
    - Robust to paraphrasing and OCR noise
    - Core building block of RAG systems

MODEL: bge-base-en-v1.5
    - Retrieval-optimized embedding model
    - High-quality semantic representations
    - 768-dimensional output

WHERE USED:
    - Called by pipeline.py and retriever.py
"""

from sentence_transformers import SentenceTransformer
from app.core.logger import get_logger
import numpy as np

logger = get_logger(__name__)

# Global model instance (loaded once, reused for all requests)
_model = None


def _normalize(vectors: np.ndarray) -> np.ndarray:
    """
    Normalize vectors for cosine similarity.

    WHY:
        - Prevents vector magnitude from affecting similarity
        - Makes similarity scores stable and comparable
    """
    return vectors / np.linalg.norm(vectors, axis=1, keepdims=True)


def embed(texts: list[str]) -> list[list[float]]:
    """
    Convert text strings into vector embeddings.

    WHY:
        - Transforms text into numerical format for semantic search

    WHERE:
        - During PDF ingestion (embed chunks for storage)
        - During query (embed user question for search)

    HOW:
        1. Load BGE model (once)
        2. Generate embeddings
        3. Normalize vectors for cosine similarity

    Args:
        texts: List of text strings to embed

    Returns:
        List of 768-dimensional normalized embedding vectors

    Example:
        texts = ["hello world", "goodbye world"]
        embeddings = embed(texts)
        # embeddings[0] = [0.012, -0.087, ..., 0.221]  (768 numbers)
    """
    global _model

    # Load model on first use
    if _model is None:
        logger.info("Loading Sentence Transformer model: bge-base-en-v1.5")
        _model = SentenceTransformer("BAAI/bge-base-en-v1.5")
        logger.info("Model loaded successfully")

    logger.debug(f"Generating embeddings for {len(texts)} text(s)")

    embeddings = _model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    embeddings = _normalize(embeddings)

    logger.debug(
        f"Generated {len(embeddings)} embeddings "
        f"of dimension {embeddings.shape[1]}"
    )

    return embeddings.tolist()
