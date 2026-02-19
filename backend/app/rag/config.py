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

# Chunking Configuration (WORD-BASED)
CHUNK_SIZE_WORDS = 800        # Target words per chunk (not characters!)
CHUNK_OVERLAP_WORDS = 100     # Overlap words between chunks
MIN_CHUNK_SIZE_WORDS = 0     # Minimum words to keep a chunk
