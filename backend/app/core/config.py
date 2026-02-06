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
    
    # ============= JWT AUTHENTICATION CONFIGURATION =============
    # WHY: Secure user authentication and authorization
    # WHERE: Used by core/security.py and core/auth.py for JWT tokens
    # HOW: SECRET_KEY signs tokens, ALGORITHM specifies encryption method
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-min-32-chars")
    ALGORITHM: str = "HS256"  # HMAC with SHA-256
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # ============= HASURA CONFIGURATION =============
    # WHY: Integration with Hasura GraphQL for authorization
    # WHERE: Used by core/hasura.py to generate JWT with Hasura claims
    # HOW: Hasura validates JWT using this secret key
    HASURA_GRAPHQL_URL: str = os.getenv("HASURA_GRAPHQL_URL", "http://localhost:8080/v1/graphql")
    HASURA_GRAPHQL_ADMIN_SECRET: str = os.getenv("HASURA_GRAPHQL_ADMIN_SECRET", "")
    HASURA_JWT_SECRET_KEY: str = os.getenv("HASURA_JWT_SECRET_KEY", SECRET_KEY)
    HASURA_JWT_ALGORITHM: str = os.getenv("HASURA_JWT_ALGORITHM", "HS256")


# Create global settings instance
# WHY: Single instance used throughout the application
settings = Settings()
