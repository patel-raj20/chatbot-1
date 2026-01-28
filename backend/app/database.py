import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load environment variables from .env when present
load_dotenv()

# Prefer DATABASE_URL if provided, otherwise fall back to a local SQLite file
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{Path(__file__).resolve().parent.parent / 'chatbot.db'}"

# SQLite needs check_same_thread=False for use with FastAPI
engine_kwargs = {"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()