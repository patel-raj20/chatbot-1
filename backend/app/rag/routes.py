from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import shutil
import os
from .rag_pipeline import ingest_pdf, ask_question
from .minio_client import upload_pdf_to_minio
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatMessage
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
            ingest_pdf(temp_path)
            print(f"[UPLOAD] Ingestion completed successfully")
        except Exception as e:
            print(f"[UPLOAD ERROR] PDF processing failed: {type(e).__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
        
        print(f"[UPLOAD] Returning success response")
        return JSONResponse(
            status_code=200,
            content={
                "status": "PDF indexed successfully",
                "minio_object": minio_object_name,
                "filename": file.filename
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
