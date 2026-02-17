"""
MinIO Client
============
Object storage client for PDF file management.

WHAT IS MINIO:
    - S3-compatible object storage (like AWS S3)
    - Stores PDF files persistently
    - Each PDF gets unique UUID identifier
    
WHY MINIO:
    - Separates file storage from application
    - Scalable and reliable
    - Docker container for easy deployment
    
WHERE USED: Called by RAG routes to store uploaded PDFs

STORAGE FLOW:
    1. User uploads PDF → Temporary file
    2. PDF stored in MinIO with UUID name
    3. Original filename kept in metadata
    4. Temporary file deleted
"""

from minio import Minio
from minio.error import S3Error
from .config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME
from app.core.logger import get_logger
import uuid
import re

logger = get_logger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to only include ASCII characters.
    
    WHY: MinIO metadata only supports ASCII characters
    WHERE: Called before storing filename in MinIO metadata
    HOW: Removes non-ASCII chars, replaces special chars with underscores
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for MinIO
        
    Example:
        "résumé (2024).pdf" → "resume_2024_.pdf"
    """
    # Remove non-ASCII characters
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    # Replace special characters with underscores
    filename = re.sub(r'[^\w\-.]', '_', filename)
    # Remove consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    return filename


def get_minio_client() -> Minio:
    """
    Create and return MinIO client instance.
    
    WHY: Reusable client for all MinIO operations
    WHERE: Called by upload and other MinIO functions
    HOW: Connects using credentials from config
    
    Returns:
        Configured MinIO client
    """
    logger.debug(f"Creating MinIO client for {MINIO_ENDPOINT}")
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False  # Use HTTP (not HTTPS) for local development
    )


def ensure_bucket_exists():
    """
    Create MinIO bucket if it doesn't exist.
    
    WHY: Bucket must exist before uploading files
    WHERE: Called before each upload operation
    HOW: Checks existence, creates if needed
    
    Raises:
        S3Error: If bucket creation fails
    """
    client = get_minio_client()
    try:
        if not client.bucket_exists(MINIO_BUCKET_NAME):
            client.make_bucket(MINIO_BUCKET_NAME)
            logger.info(f"Created MinIO bucket: {MINIO_BUCKET_NAME}")
        else:
            logger.debug(f"MinIO bucket exists: {MINIO_BUCKET_NAME}")
    except S3Error as e:
        logger.error(f"MinIO bucket check failed: {e}")
        raise


def upload_pdf_to_minio(file_path: str, original_filename: str) -> str:
    """
    Upload PDF to MinIO object storage.
    
    WHY: Persistent storage for uploaded PDFs
    WHERE: Called by /rag/upload-pdf endpoint
    HOW:
        1. Generate unique UUID for object name
        2. Sanitize original filename for metadata
        3. Upload file to MinIO bucket
        4. Return UUID for database tracking
    
    Args:
        file_path: Local path to PDF file
        original_filename: User's original filename
    
    Returns:
        UUID object name (e.g., "abc123.pdf")
        
    Raises:
        S3Error: If upload fails
    """
    client = get_minio_client()
    ensure_bucket_exists()
    
    # Generate UUID for unique object name
    object_name = f"{uuid.uuid4()}.pdf"
    
    # Sanitize filename for metadata storage
    sanitized_filename = sanitize_filename(original_filename)
    
    logger.info(f"Uploading PDF to MinIO: {original_filename} → {object_name}")
    
    try:
        client.fput_object(
            MINIO_BUCKET_NAME,
            object_name,
            file_path,
            metadata={"original-filename": sanitized_filename}
        )
        logger.info(f"Successfully uploaded to MinIO: {object_name}")
        return object_name
        
    except S3Error as e:
        logger.error(f"MinIO upload failed: {e}")
        raise


def delete_pdf_from_minio(object_name: str) -> bool:
    """
    Delete PDF from MinIO object storage.
    
    WHY: Remove files when admin deletes documents
    WHERE: Called by /rag/documents/{doc_id} delete endpoint
    HOW: Uses MinIO remove_object to delete file
    
    Args:
        object_name: MinIO object name (UUID.pdf)
    
    Returns:
        True if successful
        
    Raises:
        Exception: If deletion fails
    """
    client = get_minio_client()
    
    logger.info(f"Deleting PDF from MinIO: {object_name}")
    
    try:
        client.remove_object(MINIO_BUCKET_NAME, object_name)
        logger.info(f"Successfully deleted from MinIO: {object_name}")
        return True
        
    except S3Error as e:
        logger.error(f"MinIO deletion failed: {e}")
        raise Exception(f"Failed to delete from MinIO: {str(e)}")


def get_pdf_from_minio(object_name: str):
    """
    Retrieve PDF from MinIO object storage.
    
    WHY: Enable document download functionality
    WHERE: Called by /rag/documents/{doc_id}/download endpoint
    HOW: Returns file stream from MinIO
    
    Args:
        object_name: MinIO object name (UUID.pdf)
    
    Returns:
        File response object
        
    Raises:
        Exception: If retrieval fails
    """
    client = get_minio_client()
    
    logger.info(f"Retrieving PDF from MinIO: {object_name}")
    
    try:
        response = client.get_object(MINIO_BUCKET_NAME, object_name)
        logger.info(f"Successfully retrieved from MinIO: {object_name}")
        return response
        
    except S3Error as e:
        logger.error(f"MinIO retrieval failed: {e}")
        raise Exception(f"Failed to retrieve from MinIO: {str(e)}")
