"""
Application Configuration
=========================
Centralized configuration management using environment variables.

WHY: Having all configuration in one place makes it easier to:
     - Understand what can be configured
     - Change settings without modifying code
     - Deploy to different environments (dev, staging, production)

WHERE USED: Imported by other modules that need configuration values
HOW IT WORKS: Reads from environment variables with sensible defaults
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Settings:
    """
    Application settings loaded from environment variables.
    
    All settings have default values for local development.
    Override them by setting environment variables.
    """
    
    # ============= DATABASE CONFIGURATION =============
    # WHY: Database stores conversation nodes, edges, FAQs, and chat history
    # WHERE: Used by database.py to establish SQLAlchemy connection
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).resolve().parent.parent.parent / 'chatbot.db'}"
    )
    
    # ============= CORS CONFIGURATION =============
    # WHY: Frontend runs on different port, CORS allows cross-origin requests
    # WHERE: Used in main.py to configure CORS middleware
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://192.168.3.166:3000"
    ]
    
    # ============= MILVUS CONFIGURATION =============
    # WHY: Milvus stores vector embeddings for semantic search
    # WHERE: Used by rag/milvus_client.py to connect to vector database
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: str = os.getenv("MILVUS_PORT", "19530")
    
    # ============= LOGGING CONFIGURATION =============
    # WHY: Control verbosity of logs for debugging
    # WHERE: Used by core/logger.py to set logging level
    # HOW: Set to DEBUG for detailed logs, INFO for normal operation
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR
    
    # ============= FUZZY MATCHING CONFIGURATION =============
    # WHY: Determines how similar user input must be to trigger a conversation node
    # WHERE: Used in services/chat_service.py for fuzzy matching
    # HOW: 80 means 80% similarity required (0-100 scale)
    FUZZY_MATCH_THRESHOLD: int = int(os.getenv("FUZZY_MATCH_THRESHOLD", "80"))
    
    # ============= REDIS CACHE CONFIGURATION =============
    # WHY: Redis provides fast in-memory caching for frequently asked questions
    # WHERE: Used by cache/redis_client.py and cache/cache_service.py
    # HOW: Connect to Redis and cache Q&A responses with TTL
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    
    # ============= CACHE BEHAVIOR CONFIGURATION =============
    # WHY: Control caching behavior without code changes
    # WHERE: Used by cache service to determine caching strategy
    # HOW: Set CACHE_ENABLED=false to disable caching, adjust TTL for expiration time
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "600"))  # Default 10 minutes (600 seconds)
    CACHE_KEY_PREFIX: str = "chatbot:qa"  # Prefix for all cache keys


# Create global settings instance
# WHY: Single instance used throughout the application
settings = Settings()
