from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import shutil
import os
from .rag_pipeline import ingest_pdf, ask_question
from .minio_client import upload_pdf_to_minio
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatMessage, PDFDocument
import uuid
from .collection import get_collection

router = APIRouter(prefix="/rag")

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    print(f"[UPLOAD] Received file: {file.filename}")
    temp_path = f"temp_{file.filename}"
    minio_object_name = None
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            print(f"[UPLOAD ERROR] Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check if file is empty
        contents = await file.read()
        if len(contents) == 0:
            print("[UPLOAD ERROR] Empty file uploaded")
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        print(f"[UPLOAD] File size: {len(contents)} bytes")
        
        # Reset file pointer and save uploaded file temporarily
        await file.seek(0)
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        print(f"[UPLOAD] Saved temp file: {temp_path}")
        
        # Store PDF in MinIO (persistent storage)
        try:
            minio_object_name = upload_pdf_to_minio(temp_path, file.filename)
            print(f"[UPLOAD] Stored in MinIO: {minio_object_name}")
        except Exception as e:
            print(f"[UPLOAD ERROR] MinIO upload failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"MinIO upload failed: {str(e)}")
        
        # Process PDF through existing RAG pipeline
        try:
            print(f"[UPLOAD] Starting PDF ingestion...")
            chunk_count = ingest_pdf(temp_path, source_file=minio_object_name)
            print(f"[UPLOAD] Ingestion completed successfully: {chunk_count} chunks")
        except Exception as e:
            print(f"[UPLOAD ERROR] PDF processing failed: {type(e).__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
        
        # Save PDF metadata to database
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
            print(f"[UPLOAD] Saved PDF metadata to database")
        except Exception as e:
            print(f"[UPLOAD WARNING] Failed to save PDF metadata: {e}")
            db.rollback()
        finally:
            db.close()
        
        print(f"[UPLOAD] Returning success response")
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
        print(f"[UPLOAD ERROR] Unexpected error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"[UPLOAD] Cleaned up temp file")

@router.post("/ask")
def ask(query: str, session_id: str | None = None, db: Session = Depends(get_db)):
    """Answer a question via RAG and optionally persist the bot reply to chat history.

    If `session_id` is provided, the answer is stored as a bot `ChatMessage` for that session.
    """
    answer = ask_question(query)

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
        except Exception:
            # If storing fails, still return the answer
            pass

    return {"answer": answer}


@router.get("/debug")
def rag_debug():
    """Return basic RAG storage stats to help diagnose empty-search issues."""
    try:
        col = get_collection()
        # count entities
        count = col.num_entities
        sample = []
        try:
            sample = col.query(expr="id >= 0", output_fields=["content"], limit=3)
        except Exception as e:
            sample = [{"error": str(e)}]
        return {"count": count, "sample": sample}
    except Exception as e:
        return {"error": str(e)}


@router.delete("/clear")
def clear_rag():
    """Clear all documents from RAG collection."""
    try:
        col = get_collection()
        col.delete(expr="id >= 0")
        col.flush()
        return {"status": "RAG collection cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    """List all uploaded PDF documents."""
    try:
        documents = db.query(PDFDocument).order_by(PDFDocument.upload_date.desc()).all()
        return [{
            "id": str(doc.id),
            "filename": doc.original_filename,
            "minio_object": doc.minio_object_name,
            "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
            "chunk_count": doc.chunk_count
        } for doc in documents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.delete("/documents/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a specific PDF document and its vectors from the collection."""
    try:
        # Get document from database
        doc = db.query(PDFDocument).filter(PDFDocument.id == uuid.UUID(document_id)).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete vectors from Milvus
        col = get_collection()
        expr = f'source_file == "{doc.minio_object_name}"'
        col.delete(expr)
        col.flush()
        print(f"[DELETE] Removed vectors for {doc.minio_object_name}")
        
        # Delete from database
        db.delete(doc)
        db.commit()
        
        return {
            "status": "Document deleted successfully",
            "filename": doc.original_filename
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")
