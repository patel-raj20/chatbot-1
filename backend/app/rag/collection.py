"""
Milvus Collection Manager
==========================
Manages Milvus collection schema and operations.

WHAT IS A COLLECTION:
    - Like a "table" in Milvus vector database
    - Stores vectors with metadata (content, source file, etc.)
    - Supports vector similarity search
    
COLLECTION SCHEMA:
    - id: Auto-generated unique ID
    - content: Original text chunk
    - embedding: 384-dimensional vector
    - source_file: MinIO object name
    - original_filename: User's original PDF name
    
WHERE USED: By pipeline.py and retriever.py for vector storage/search
"""

from pymilvus import FieldSchema, CollectionSchema, DataType, Collection, utility
from .config import COLLECTION_NAME, EMBEDDING_DIM
from .milvus_client import connect_milvus
from app.core.logger import get_logger

logger = get_logger(__name__)


def get_collection() -> Collection:
    """
    Get or create Milvus collection for RAG documents.
    
    WHY: Centralized collection management
    WHERE: Called by pipeline.py (insert) and retriever.py (search)
    HOW:
        1. Ensure Milvus connection exists
        2. Load existing collection if available
        3. Create new collection if doesn't exist
        4. Create index for fast similarity search
    
    Returns:
        Milvus Collection object ready for operations
        
    COLLECTION STRUCTURE:
        fields = [
            id (INT64, primary, auto): Unique identifier
            content (VARCHAR, max 2048): Text chunk
            embedding (FLOAT_VECTOR, dim 384): Vector representation
            source_file (VARCHAR, max 256): MinIO object name
            original_filename (VARCHAR, max 256): Original PDF name
        ]
    """
    # Ensure Milvus connection is established
    try:
        connect_milvus()
    except Exception as e:
        logger.warning(f"Milvus connection attempt failed: {e}")
    
    # Check if collection already exists
    if utility.has_collection(COLLECTION_NAME):
        logger.debug(f"Loading existing collection: {COLLECTION_NAME}")
        col = Collection(COLLECTION_NAME)
        try:
            col.load()
            logger.info(f"Collection loaded: {COLLECTION_NAME}")
        except Exception as e:
            logger.warning(f"Failed to load collection {COLLECTION_NAME}: {e}")
        return col
    
    # Create new collection
    logger.info(f"Creating new collection: {COLLECTION_NAME}")
    
    # Define collection fields (schema)
    fields = [
        FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema("content", DataType.VARCHAR, max_length=2048),
        FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        FieldSchema("source_file", DataType.VARCHAR, max_length=256),
        FieldSchema("original_filename", DataType.VARCHAR, max_length=256),
    ]
    
    schema = CollectionSchema(fields, description="RAG document collection")
    col = Collection(COLLECTION_NAME, schema)
    
    # Create index for fast similarity search
    # WHY: Without index, search would be slow (brute force)
    # IVF_FLAT: Inverted File with Flat compression
    # metric_type=IP: Inner Product (cosine similarity)
    logger.info("Creating index for fast vector search...")
    col.create_index(
        "embedding",
        {
            "index_type": "IVF_FLAT",
            "metric_type": "IP",  # Inner Product (for normalized vectors)
            "params": {"nlist": 128}  # Number of clusters
        }
    )
    
    # Load collection into memory for searching
    col.load()
    logger.info(f"Collection created and loaded: {COLLECTION_NAME}")
    
    return col
