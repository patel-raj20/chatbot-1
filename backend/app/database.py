"""
Database Configuration
======================
Database connection and session management using SQLAlchemy ORM.

WHY: 
    - SQLAlchemy provides object-relational mapping (ORM) for database operations
    - Abstracts database operations into Python objects
    - Supports multiple database backends (SQLite, PostgreSQL, etc.)
    
WHERE USED: Imported by main.py and route modules
HOW IT WORKS:
    1. Reads DATABASE_URL from environment or uses default SQLite
    2. Creates database engine
    3. Provides session factory for database connections
    4. Each request gets its own database session via get_db()
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env file if present
load_dotenv()

# ============= DATABASE URL CONFIGURATION =============
# WHY: Different environments (dev, prod) may use different databases
# WHERE: Read by create_engine() to establish connection
# HOW: Environment variable takes precedence, fallback to local SQLite file
DATABASE_URL = os.getenv(
    "DATABASE_URL"
) or f"sqlite:///{Path(__file__).resolve().parent.parent / 'chatbot.db'}"

# ============= ENGINE CREATION =============
# WHY: Engine is the core interface to the database
# WHERE: Used by SessionLocal to create connections
# HOW: SQLite needs special config for FastAPI's async nature
engine_kwargs = (
    {"connect_args": {"check_same_thread": False}}
    if DATABASE_URL.startswith("sqlite")
    else {}
)
engine = create_engine(DATABASE_URL, **engine_kwargs)

# ============= SESSION FACTORY =============
# WHY: Sessions handle database transactions and object persistence
# WHERE: Used by get_db() to provide session to routes
# HOW: Each request gets a new session, automatically closed after use
SessionLocal = sessionmaker(
    autocommit=False,  # Manual transaction control
    autoflush=False,   # Don't auto-flush changes to database
    bind=engine
)

# ============= BASE CLASS FOR MODELS =============
# WHY: All database models inherit from this base
# WHERE: Used in models.py to define tables
# HOW: Provides metadata for table creation and query interface
Base = declarative_base()


def get_db():
    """
    Dependency function that provides database session to routes.
    
    WHY: Ensures each request gets a fresh database session
    WHERE: Used with FastAPI's Depends() in route functions
    HOW: Creates session, yields it to route, closes after request completes
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
