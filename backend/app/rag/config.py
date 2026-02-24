import os

COLLECTION_NAME = "rag_documents"
EMBEDDING_DIM = 768

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast and powerful Groq model

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_NAME = "pdf-documents"

# OCR Configuration
OCR_ENABLED = True
OCR_LANGUAGE = "eng"  # Language for OCR (eng, ara, fra, etc.)
OCR_DPI = 300  # DPI for image rendering (higher = better quality, slower)
OCR_MIN_TEXT_LENGTH = 50  # Minimum text length before triggering full-page OCR

# Chunking Configuration (STRUCTURE-AWARE, TOKEN-BASED)
TARGET_CHUNK_TOKENS = 500    # Target tokens per chunk (approximate)
MAX_CHUNK_TOKENS = 800       # Maximum tokens per chunk
MIN_CHUNK_TOKENS = 30        # Minimum tokens to keep a chunk (reduced to preserve small sections)
ENABLE_TABLE_ATOMIC = True   # Keep tables as single chunks (never split rows)
