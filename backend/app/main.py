"""
Main Application
================
FastAPI application entry point.

This file sets up:
    - FastAPI app with CORS middleware
    - Database initialization
    - Milvus vector database connection
    - API route registration
    
FLOW:
    1. Application starts
    2. Database tables are created (if not exist)
    3. Milvus connection is established
    4. Routes are registered from separate modules
    5. API is ready to accept requests
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.core.logger import get_logger
from app.core.config import settings

# Import route modules
from app.routes.chat import router as chat_router
from app.routes.faqs import router as faq_router
from app.routes.admin import router as admin_router
from app.rag.routes import router as rag_router
from app.auth.routes import router as auth_router  # Authentication routes

# Import cache services
from app.cache.redis_client import RedisClient
from app.cache.cache_service import CacheService

# Initialize logger
logger = get_logger(__name__)

# ============= INITIALIZE REDIS CACHE =============
# WHY: Global cache instance shared across all requests
# WHERE: Used by chat routes to cache Q&A responses
# HOW: Create Redis client and cache service instances
redis_client = RedisClient()
cache_service = CacheService(redis_client)

# Create FastAPI application
app = FastAPI(
    title="Intelligent Chat Bot API",
    description="RAG-powered chatbot with conversation flow management",
    version="1.0.0"
)

# ============= CORS CONFIGURATION =============
# WHY: Frontend runs on different port (3000), needs permission to call API
# WHERE: Applied to all routes automatically
# HOW: Allows specified origins to make cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
)

# ============= DATABASE INITIALIZATION =============
# WHY: Ensures database tables exist before app starts accepting requests
# WHERE: Runs once at application startup
# HOW: SQLAlchemy creates tables based on model definitions
logger.info("Initializing database tables...")
Base.metadata.create_all(bind=engine)
logger.info("Database tables initialized")

# ============= REGISTER API ROUTES =============
# WHY: Organizes endpoints by feature area
# WHERE: Each router handles specific functionality
# HOW: Routers are imported from separate modules and included here
app.include_router(auth_router)   # /auth/* (signup, login)
app.include_router(chat_router)   # /chat/message
app.include_router(faq_router)    # /faqs
app.include_router(admin_router)  # /admin/*
app.include_router(rag_router)    # /rag/*

logger.info("API routes registered")


# ============= STARTUP EVENT =============
@app.on_event("startup")
async def startup_event():
    """
    Connect to external services on application startup.
    
    WHY: Database connections needed for RAG and caching functionality
    WHERE: Runs automatically when FastAPI starts
    HOW: Attempts connections, logs warnings if unavailable
    """
    logger.info("Starting up application...")
    
    # ========== CONNECT TO MILVUS ==========
    try:
        from pymilvus import connections
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT
        )
        logger.info("✓ Connected to Milvus vector database successfully")
    except Exception as e:
        logger.warning(f"✗ Could not connect to Milvus: {e}")
        logger.warning("RAG functionality will be limited without Milvus")
    
    # ========== CONNECT TO REDIS CACHE ==========
    if settings.CACHE_ENABLED:
        try:
            await redis_client.connect()
            if await redis_client.ping():
                logger.info(f"✓ Redis cache connected successfully (TTL: {settings.CACHE_TTL}s)")
            else:
                logger.warning("✗ Redis ping failed - cache will be disabled")
        except Exception as e:
            logger.warning(f"✗ Could not connect to Redis: {e}")
            logger.warning("Cache functionality will be disabled - chatbot will work normally")


# ============= SHUTDOWN EVENT =============
@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on application shutdown.
    
    WHY: Proper cleanup prevents resource leaks
    WHERE: Runs automatically when FastAPI shuts down
    HOW: Closes Redis connection pool
    """
    logger.info("Shutting down application...")
    
    try:
        await redis_client.disconnect()
        logger.info("✓ Redis connection closed")
    except Exception as e:
        logger.error(f"✗ Error closing Redis connection: {e}")


# ============= HEALTH CHECK ENDPOINT =============
@app.get("/")
def root():
    """
    Health check endpoint.
    
    WHY: Verify API is running
    WHERE: Called by monitoring tools or manual testing
    HOW: Returns simple status message
    
    Returns:
        {"status": "Backend running"}
    """
    return {"status": "Backend running"}
