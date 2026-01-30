"""
Milvus Client
=============
Connection utility for Milvus vector database.

WHAT IS MILVUS:
    - Vector database for storing and searching embeddings
    - Specialized for high-dimensional vector similarity search
    - Used to find semantically similar text chunks
    
WHY MILVUS:
    - Fast similarity search across millions of vectors
    - Supports inner product (IP) and other distance metrics
    - Open-source and scalable
    
WHERE USED: Imported by collection.py and main.py for connection
"""

import os
from pymilvus import connections
from app.core.logger import get_logger

logger = get_logger(__name__)


def connect_milvus():
    """
    Establish connection to Milvus vector database.
    
    WHY: Milvus connection needed before any vector operations
    WHERE: Called by collection.py and main.py startup
    HOW: Connects to Milvus server using host and port from config
    
    Configuration:
        MILVUS_HOST: Default "localhost"
        MILVUS_PORT: Default "19530"
        
    Raises:
        Exception: If connection fails
    """
    host = os.getenv("MILVUS_HOST", "localhost")
    port = os.getenv("MILVUS_PORT", "19530")
    
    logger.debug(f"Connecting to Milvus at {host}:{port}")
    connections.connect(
        alias="default",
        host=host,
        port=port
    )
    logger.info("Milvus connection established")
