from minio import Minio
from minio.error import S3Error
from .config import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME
import uuid
import re


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to only include ASCII characters and safe characters"""
    # Remove or replace non-ASCII characters
    filename = filename.encode('ascii', 'ignore').decode('ascii')
    # Replace spaces and special characters with underscores
    filename = re.sub(r'[^\w\-.]', '_', filename)
    # Remove consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    return filename


def get_minio_client():
    """Create and return MinIO client instance"""
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )


def ensure_bucket_exists():
    """Create bucket if it doesn't exist"""
    client = get_minio_client()
    try:
        if not client.bucket_exists(MINIO_BUCKET_NAME):
            client.make_bucket(MINIO_BUCKET_NAME)
            print(f"[OK] Created MinIO bucket: {MINIO_BUCKET_NAME}")
    except S3Error as e:
        print(f"[WARNING] MinIO bucket check failed: {e}")
        raise


def upload_pdf_to_minio(file_path: str, original_filename: str) -> str:
    """
    Upload PDF to MinIO and return the object name (UUID)
    
    Args:
        file_path: Local path to the PDF file
        original_filename: Original filename for metadata
    
    Returns:
        str: UUID object name used in MinIO
    """
    client = get_minio_client()
    ensure_bucket_exists()
    
    # Generate UUID for object name
    object_name = f"{uuid.uuid4()}.pdf"
    
    # Sanitize filename for metadata (MinIO only supports ASCII)
    sanitized_filename = sanitize_filename(original_filename)
    
    try:
        client.fput_object(
            MINIO_BUCKET_NAME,
            object_name,
            file_path,
            metadata={"original-filename": sanitized_filename}
        )
        print(f"[OK] Uploaded to MinIO: {object_name} (original: {sanitized_filename})")
        return object_name
    except S3Error as e:
        print(f"[ERROR] MinIO upload failed: {e}")
        raise
