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

# Initialize logger
logger = get_logger(__name__)

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
    Connect to Milvus vector database on application startup.
    
    WHY: Milvus connection needed for RAG functionality
    WHERE: Runs automatically when FastAPI starts
    HOW: Attempts connection to Milvus, logs warning if unavailable
    """
    logger.info("Starting up application...")
    
    try:
        from pymilvus import connections
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT
        )
        logger.info("Connected to Milvus vector database successfully")
    except Exception as e:
        logger.warning(f"Could not connect to Milvus: {e}")
        logger.warning("RAG functionality will be limited without Milvus")


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
