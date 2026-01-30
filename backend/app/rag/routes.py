"""
RAG Routes
==========
API endpoints for RAG (Retrieval-Augmented Generation) functionality.

ENDPOINTS:
    POST /rag/upload-pdf    - Upload and process PDF
    POST /rag/ask           - Ask question from documents
    GET  /rag/debug         - Get RAG system statistics
    DELETE /rag/clear       - Clear all documents
    GET  /rag/documents     - List all uploaded PDFs
    DELETE /rag/documents/{doc_id} - Delete specific PDF
    
RAG FLOW:
    1. UPLOAD: PDF → MinIO storage → Text extraction → Chunking → 
       Embeddings → Milvus vector DB
    2. QUERY: Question → Embedding → Vector search → Context retrieval → 
       LLM → Answer
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import shutil
import os
from .pipeline import ingest_pdf, ask_question
from .minio_client import upload_pdf_to_minio
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatMessage, PDFDocument
from app.core.logger import get_logger
import uuid
from .collection import get_collection

logger = get_logger(__name__)
router = APIRouter(prefix="/rag", tags=["rag"])

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process PDF for RAG system.
    
    WHY: Add documents to chatbot's knowledge base
    WHERE: Called from frontend when user uploads PDF
    HOW:
        1. Validate PDF file
        2. Store in MinIO (persistent storage)
        3. Process through RAG pipeline (extract, chunk, embed, store)
        4. Save metadata to database
        5. Clean up temporary files
    
    Returns:
        Success message with chunk count
        
    Raises:
        HTTPException: If validation fails or processing errors
    """
    logger.info(f"Received PDF upload: {file.filename}")
    temp_path = f"temp_{file.filename}"
    minio_object_name = None
    
    try:
        # STEP 1: Validate file type
        if not file.filename.lower().endswith('.pdf'):
            logger.warning(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # STEP 2: Check if file is empty
        contents = await file.read()
        if len(contents) == 0:
            logger.warning("Empty file uploaded")
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        logger.info(f"File size: {len(contents)} bytes")
        
        # STEP 3: Save temporarily
        await file.seek(0)
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.debug(f"Saved temp file: {temp_path}")
        
        # STEP 4: Store in MinIO
        try:
            minio_object_name = upload_pdf_to_minio(temp_path, file.filename)
            logger.info(f"Stored in MinIO: {minio_object_name}")
        except Exception as e:
            logger.error(f"MinIO upload failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"MinIO upload failed: {str(e)}")
        
        # STEP 5: Process through RAG pipeline
        try:
            logger.info("Starting PDF ingestion...")
            chunk_count = ingest_pdf(temp_path, source_file=minio_object_name, original_filename=file.filename)
            logger.info(f"Ingestion completed: {chunk_count} chunks")
        except Exception as e:
            logger.error(f"PDF processing failed: {type(e).__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
        
        # STEP 6: Save metadata to database
        pdf_doc = PDFDocument(
            id=uuid.uuid4(),
            original_filename=file.filename,
            minio_object_name=minio_object_name,
            chunk_count=str(chunk_count)
        )
        db = next(get_db())
        try:
            db.add(pdf_doc)
            db.commit()
            logger.info("Saved PDF metadata to database")
        except Exception as e:
            logger.warning(f"Failed to save PDF metadata: {e}")
            db.rollback()
        finally:
            db.close()
        
        logger.info(f"PDF upload successful: {file.filename}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "PDF indexed successfully",
                "minio_object": minio_object_name,
                "filename": file.filename,
                "chunks": chunk_count
            },
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.debug("Cleaned up temp file")

@router.post("/ask")
def ask(query: str, session_id: str | None = None, db: Session = Depends(get_db)):
    """
    Answer question using RAG system.
    
    WHY: Provide answers from uploaded documents
    WHERE: Called from frontend when user asks question
    HOW:
        1. Query RAG pipeline (retrieves and generates answer)
        2. Optionally save answer to chat history
    
    Args:
        query: User's question
        session_id: Optional chat session ID for history tracking
        
    Returns:
        {"answer": "Generated answer text"}
    """
    logger.info(f"RAG query received: '{query}'")
    answer = ask_question(query)
    
    # Save to chat history if session_id provided
    if session_id:
        try:
            session_uuid = uuid.UUID(session_id)
            db.add(ChatMessage(
                id=uuid.uuid4(),
                session_id=session_uuid,
                sender="bot",
                message_text=answer,
                node_id=None
            ))
            db.commit()
            logger.debug(f"Saved RAG answer to session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to save RAG answer to history: {e}")
    
    logger.info("RAG answer generated successfully")
    return {"answer": answer}


@router.get("/debug")
def rag_debug():
    """
    Get RAG system statistics for debugging.
    
    WHY: Helps diagnose issues with vector search
    WHERE: Called by admins to check system state
    HOW: Returns count of vectors and sample content
    
    Returns:
        {"count": int, "sample": [sample vectors]}
    """
    logger.debug("RAG debug info requested")
    try:
        col = get_collection()
        count = col.num_entities
        sample = []
        try:
            sample = col.query(expr="id >= 0", output_fields=["content"], limit=3)
            logger.debug(f"RAG debug: {count} vectors, {len(sample)} sample(s)")
        except Exception as e:
            logger.warning(f"Failed to get sample vectors: {e}")
            sample = [{"error": str(e)}]
        return {"count": count, "sample": sample}
    except Exception as e:
        logger.error(f"RAG debug failed: {e}")
        return {"error": str(e)}


@router.delete("/clear")
def clear_rag():
    """
    Clear all documents from RAG collection.
    
    WHY: Remove all uploaded documents (admin operation)
    WHERE: Called by admin to reset system
    HOW: Deletes all vectors from Milvus collection
    
    WARNING: This is irreversible!
    """
    logger.warning("RAG collection clear requested")
    try:
        col = get_collection()
        col.delete(expr="id >= 0")
        col.flush()
        logger.info("RAG collection cleared successfully")
        return {"status": "RAG collection cleared"}
    except Exception as e:
        logger.error(f"Failed to clear RAG collection: {e}")
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    """
    List all uploaded PDF documents.
    
    WHY: View what documents are in the system
    WHERE: Called by admin panel
    HOW: Queries PDFDocument table
    
    Returns:
        List of document metadata
    """
    logger.debug("Document list requested")
    try:
        documents = db.query(PDFDocument).order_by(PDFDocument.upload_date.desc()).all()
        logger.info(f"Found {len(documents)} documents")
        return [{
            "id": str(doc.id),
            "filename": doc.original_filename,
            "minio_object": doc.minio_object_name,
            "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
            "chunk_count": doc.chunk_count
        } for doc in documents]
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """
    Delete a specific PDF document and its vectors.
    
    WHY: Remove unwanted documents from system
    WHERE: Called by admin panel
    HOW:
        1. Remove vectors from Milvus (by source_file filter)
        2. Delete metadata from database
    
    Args:
        document_id: UUID of document to delete
        
    Returns:
        Success message
    """
    logger.info(f"Document deletion requested: {document_id}")
    try:
        # Get document from database
        doc = db.query(PDFDocument).filter(PDFDocument.id == uuid.UUID(document_id)).first()
        if not doc:
            logger.warning(f"Document not found: {document_id}")
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete vectors from Milvus
        col = get_collection()
        expr = f'source_file == "{doc.minio_object_name}"'
        col.delete(expr)
        col.flush()
        logger.info(f"Removed vectors for {doc.minio_object_name}")
        
        # Delete from database
        db.delete(doc)
        db.commit()
        logger.info(f"Document deleted successfully: {doc.original_filename}")
        
        return {
            "status": "Document deleted successfully",
            "filename": doc.original_filename
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
