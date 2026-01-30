import os

COLLECTION_NAME = "rag_documents"
EMBEDDING_DIM = 768
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/generate"
OLLAMA_MODEL = "gemma3"

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_NAME = "pdf-documents"

# OCR Configuration
OCR_ENABLED = True
OCR_LANGUAGE = "eng"  # Language for OCR (eng, ara, fra, etc.)
OCR_DPI = 300  # DPI for image rendering (higher = better quality, slower)
OCR_MIN_TEXT_LENGTH = 100  # Minimum text length before triggering full-page OCR
